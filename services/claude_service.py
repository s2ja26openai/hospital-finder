# services/claude_service.py
import json
import logging
import os
import sys
import httpx
from anthropic import AsyncAnthropic

_SSL_VERIFY = sys.platform != "win32"

logger = logging.getLogger(__name__)

_USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
_USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
_GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

SYSTEM_PROMPT = """You are a Korean medical triage assistant. Recommend the most clinically appropriate medical departments based on the user's specific symptoms.

Respond ONLY in this exact JSON format, no other text:
{"departments": [{"name": "내과", "reason": "소화불량과 복통 증상에 적합"}, {"name": "가정의학과", "reason": "초기 진료 및 전반적 건강 평가"}], "message": "증상을 분석했습니다. 아래 진료과를 추천드려요."}

RULES:
1. Output JSON only — no explanation, no markdown, no extra text.
2. Recommend exactly 2-3 departments.
3. Choose ONLY from: 내과, 외과, 정형외과, 산부인과, 소아청소년과, 안과, 이비인후과, 피부과, 비뇨의학과, 재활의학과, 가정의학과, 신경과, 정신건강의학과, 응급의학과, 치과
4. "reason" must be symptom-specific (NOT generic like "일반 증상에"). Max 20 Korean characters. Korean only.
5. "message" field: Korean only.
6. NEVER recommend 응급의학과 unless the symptom is clearly life-threatening (e.g., 의식불명, 심한 흉통, 호흡곤란).
7. Match the department precisely to the symptom:
   - 두통/어지러움 → 신경과, 내과
   - 눈 증상 → 안과
   - 귀/코/목 → 이비인후과
   - 피부 발진/가려움 → 피부과
   - 관절/근육통 → 정형외과, 재활의학과
   - 복통/소화불량 → 내과
   - 정신건강/불안/우울 → 정신건강의학과
   - 치통 → 치과
   - 비뇨기 증상 → 비뇨의학과
8. Use ONLY Korean characters (NO Chinese characters, NO English in reason/message)."""


def _extract_json(text: str) -> dict:
    # qwen3 thinking 태그 제거
    if "</think>" in text:
        text = text[text.index("</think>") + len("</think>"):].strip()
    # 마크다운 코드블록 제거
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                text = part
                break
    # { 시작 위치부터 파싱
    start = text.find("{")
    if start != -1:
        text = text[start:]
    return json.loads(text)


async def _recommend_via_ollama(messages: list[dict]) -> dict:
    ollama_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    async with httpx.AsyncClient(timeout=60) as client:
        res = await client.post(
            f"{_OLLAMA_URL}/v1/chat/completions",
            json={"model": _OLLAMA_MODEL, "messages": ollama_messages, "stream": False, "response_format": {"type": "json_object"}},
        )
        res.raise_for_status()
    text = res.json()["choices"][0]["message"]["content"].strip()
    print(f"[DEBUG] Ollama raw response: {text[:500]}", flush=True)
    return _extract_json(text)


async def _recommend_via_groq(messages: list[dict]) -> dict:
    groq_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    async with httpx.AsyncClient(timeout=60, verify=_SSL_VERIFY) as client:
        res = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {_GROQ_API_KEY}"},
            json={"model": _GROQ_MODEL, "messages": groq_messages, "stream": False, "response_format": {"type": "json_object"}},
        )
        res.raise_for_status()
    text = res.json()["choices"][0]["message"]["content"].strip()
    print(f"[DEBUG] Groq raw response: {text[:500]}", flush=True)
    return _extract_json(text)


async def _recommend_via_anthropic(messages: list[dict]) -> dict:
    response = await _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    text = response.content[0].text.strip()
    return _extract_json(text)


async def recommend_departments(messages: list[dict]) -> dict:
    """
    대화 히스토리를 받아 진료과 추천 반환.
    messages: [{"role": "user"|"assistant", "content": "..."}, ...]
    반환: {"departments": [...], "message": "..."}
    USE_OLLAMA=true 시 Ollama 사용, USE_GROQ=true 시 Groq 사용, 아니면 Anthropic Claude 사용.
    """
    print(f"[DEBUG] USE_OLLAMA={_USE_OLLAMA} USE_GROQ={_USE_GROQ} OLLAMA_MODEL={_OLLAMA_MODEL} GROQ_MODEL={_GROQ_MODEL}", flush=True)
    if _USE_OLLAMA:
        return await _recommend_via_ollama(messages)
    if _USE_GROQ:
        return await _recommend_via_groq(messages)
    return await _recommend_via_anthropic(messages)
