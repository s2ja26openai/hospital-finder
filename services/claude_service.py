# services/claude_service.py
import json
import os
from anthropic import AsyncAnthropic

_client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

SYSTEM_PROMPT = """당신은 한국의 의료 안내 도우미입니다. 사용자의 증상을 듣고 방문해야 할 진료과를 추천합니다.
반드시 아래 JSON 형식으로만 응답하세요 (다른 텍스트 없이):
{"departments": [{"name": "진료과명", "reason": "추천 이유 1문장"}], "message": "사용자에게 보낼 안내 메시지"}
추천 진료과는 2~3개, 이유는 30자 이내.
가능한 진료과: 내과, 외과, 정형외과, 산부인과, 소아청소년과, 안과, 이비인후과, 피부과, 비뇨의학과, 재활의학과, 가정의학과, 신경과, 정신건강의학과, 응급의학과, 치과"""


async def recommend_departments(messages: list[dict]) -> dict:
    """
    대화 히스토리를 받아 진료과 추천 반환.
    messages: [{"role": "user"|"assistant", "content": "..."}, ...]
    반환: {"departments": [...], "message": "..."}
    """
    response = await _client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    text = response.content[0].text.strip()

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

    return json.loads(text)
