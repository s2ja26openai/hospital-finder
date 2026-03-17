# services/claude_service.py
import json
import logging
import os
import httpx
from anthropic import AsyncAnthropic

logger = logging.getLogger(__name__)

_USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
_OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")
_USE_GROQ = os.getenv("USE_GROQ", "false").lower() == "true"
_GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
_GROQ_MODEL = os.getenv("GROQ_MODEL", "gemma2-9b-it")
_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

SYSTEM_PROMPT = """You are a Korean medical assistant. Recommend medical departments based on user symptoms.
Respond ONLY in this exact JSON format, no other text:
{"departments": [{"name": "내과", "reason": "소화 문제에 적합한 과입니다"}, {"name": "가정의학과", "reason": "일반 증상 초기 진료에 적합"}], "message": "증상을 분석했습니다. 아래 진료과를 추천드려요."}

IMPORTANT:
- Use ONLY Korean characters (한국어만 사용, NO Chinese characters, NO English in reason/message)
- Recommend 2-3 departments from: 내과, 외과, 정형외과, 산부인과, 소아청소년과, 안과, 이비인후과, 피부과, 비뇨의학과, 재활의학과, 가정의학과, 신경과, 정신건강의학과, 응급의학과, 치과
- reason: Korean only, max 20 characters
- message: Korean only
- Output JSON only"""


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
    async with httpx.AsyncClient(timeout=60) as client:
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
