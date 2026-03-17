# routers/chatbot.py
import json
import logging
import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from services.claude_service import recommend_departments

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api")

# 서버 메모리 세션 (개발용 — 프로세스 재시작 시 초기화)
_sessions: dict[str, list[dict]] = {}


class ChatRequest(BaseModel):
    session_id: str = ""
    message: str


@router.post("/chat")
async def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())

    history = _sessions.get(session_id, [])
    history.append({"role": "user", "content": body.message})

    try:
        result = await recommend_departments(history)
    except Exception as e:
        logger.error("recommend_departments failed: %s", e, exc_info=True)
        return {
            "session_id": session_id,
            "departments": [],
            "message": "분석 중 오류가 발생했습니다. 다시 시도해 주세요.",
        }

    history.append({
        "role": "assistant",
        "content": json.dumps(result, ensure_ascii=False),
    })
    _sessions[session_id] = history[-10:]  # 최근 10개 메시지만 유지

    return {
        "session_id": session_id,
        "departments": result.get("departments", []),
        "message": "증상을 분석했습니다. 아래 진료과를 추천드려요:",
    }
