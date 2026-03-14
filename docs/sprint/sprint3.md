# Sprint 3 — 챗봇 구현 계획

## ✅ 완료 기록 (2026-03-13)

| 항목 | 상태 | 비고 |
|------|------|------|
| Claude API 서비스 구현 | ✅ 완료 | claude_service.py — 증상→진료과 추론 |
| 챗봇 API 엔드포인트 | ✅ 완료 | POST /api/chat |
| 멀티턴 세션 관리 | ✅ 완료 | 서버 메모리 dict 기반 대화 히스토리 |
| 진료과 추천 프롬프트 | ✅ 완료 | 진료과명 + 추천 근거(질병 가능성) 반환 |
| 챗봇 프론트엔드 연동 | ✅ 완료 | Mock 응답 제거, 실제 /api/chat 연동 |
| 로딩 인디케이터 | ✅ 완료 | typing dots 애니메이션 |
| 길 안내 기능 제거 | ✅ 완료 | PRD 범위 외 기능으로 제외 결정 |

**완료 커밋:** `736b424`

---

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Claude API 기반 증상→진료과 추천 챗봇을 완성한다.

**Architecture:** Claude API는 서버에서 직접 호출(키 노출 방지). 챗봇 세션은 서버 메모리(dict)로 관리.

**Tech Stack:** Anthropic Python SDK, FastAPI, SSE(선택)

---

## 사전 확인

- `ANTHROPIC_API_KEY` — .env에 존재 확인됨
- `KAKAO_MAP_API_KEY` — 카카오 REST API 키

---

## Task 1: Claude 챗봇 서비스 구현

**Files:**
- Create: `services/claude_service.py`
- Create: `routers/chatbot.py`
- Modify: `main.py`

### Claude API 프롬프트 설계

```
시스템: 당신은 한국의 의료 안내 도우미입니다. 사용자의 증상을 듣고 방문해야 할 진료과를 추천합니다.
반드시 JSON 형식으로 응답하세요:
{"departments": [{"name": "진료과명", "reason": "추천 이유 (1문장)"}, ...], "message": "사용자에게 보낼 안내 메시지"}
추천 진료과는 2~3개, 이유는 30자 이내로 작성하세요.
가능한 진료과: 내과, 외과, 정형외과, 산부인과, 소아청소년과, 안과, 이비인후과, 피부과, 비뇨의학과, 재활의학과, 가정의학과, 신경과, 정신건강의학과, 신경외과, 응급의학과, 치과
```

**Step 1: requirements.txt에 anthropic 추가**

Run: `grep anthropic requirements.txt`
If not found, add: `anthropic>=0.25.0`

```bash
echo "anthropic>=0.25.0" >> requirements.txt
pip install anthropic
```

**Step 2: services/claude_service.py 작성**

```python
# services/claude_service.py
import json
import os
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))

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
    response = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    text = response.content[0].text.strip()
    # JSON 파싱 (마크다운 코드블록 제거)
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)
```

**Step 3: routers/chatbot.py 작성**

```python
# routers/chatbot.py
import uuid
from fastapi import APIRouter
from pydantic import BaseModel
from services.claude_service import recommend_departments

router = APIRouter(prefix="/api")

# 서버 메모리 세션 (프로세스 재시작 시 초기화 — 개발용)
_sessions: dict[str, list[dict]] = {}


class ChatRequest(BaseModel):
    session_id: str = ""
    message: str


@router.post("/chat")
async def chat(body: ChatRequest):
    session_id = body.session_id or str(uuid.uuid4())

    # 세션 히스토리 로드
    history = _sessions.get(session_id, [])
    history.append({"role": "user", "content": body.message})

    result = await recommend_departments(history)

    # assistant 응답을 히스토리에 추가
    import json as _json
    history.append({"role": "assistant", "content": _json.dumps(result, ensure_ascii=False)})
    _sessions[session_id] = history[-10:]  # 최근 10개 메시지만 유지

    return {
        "session_id": session_id,
        "departments": result.get("departments", []),
        "message": result.get("message", "증상을 분석했습니다."),
    }
```

**Step 4: main.py에 chatbot 라우터 등록**

```python
from routers import location, hospital, chatbot
app.include_router(chatbot.router)
```

**Step 5: 수동 테스트**

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "머리가 아프고 열이 나요"}'
```
Expected: `{"session_id": "...", "departments": [{"name": "내과", "reason": "..."}, ...], "message": "..."}`

**Step 6: Commit**

```bash
git add services/claude_service.py routers/chatbot.py main.py requirements.txt
git commit -m "feat: F-02 Claude API 챗봇 서비스 + POST /api/chat"
```

---

## Task 2: 챗봇 프론트엔드 → 실제 API 연동

**Files:**
- Modify: `static/js/chatbot.js`

**Step 1: chatbot.js 수정 — Mock 제거, API 호출로 교체**

변경 포인트:
- `MOCK_RESPONSES`, `getMockDepts()` 제거
- `sendMessage()` 를 async로 변경, `/api/chat` 호출
- `sessionId` 전역 변수로 멀티턴 관리
- 타이핑 인디케이터는 그대로 유지 (API 응답 대기 중 표시)

```js
// static/js/chatbot.js
let sessionId = '';

function getMessagesContainer() {
  return document.getElementById('chatMessages');
}

function addBubble(text, type) {
  const container = getMessagesContainer();
  const div = document.createElement('div');
  div.className = `bubble bubble-${type}`;
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

function addTypingIndicator() {
  const container = getMessagesContainer();
  const div = document.createElement('div');
  div.className = 'bubble bubble-bot bubble-typing';
  div.id = 'typingIndicator';
  div.innerHTML = `
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
    <div class="typing-dot"></div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
  const el = document.getElementById('typingIndicator');
  if (el) el.remove();
}

function addDeptCards(depts) {
  const container = getMessagesContainer();
  const wrapper = document.createElement('div');
  wrapper.className = 'dept-recommendation';

  depts.forEach(dept => {
    const card = document.createElement('div');
    card.className = 'dept-card';
    card.innerHTML = `
      <div>
        <div class="dept-card-name">${dept.name}</div>
        <div class="dept-card-reason">${dept.reason}</div>
      </div>
      <span class="dept-card-arrow">→</span>
    `;
    card.onclick = () => {
      window.location.href = `/hospitals?department=${encodeURIComponent(dept.name)}`;
    };
    wrapper.appendChild(card);
  });

  container.appendChild(wrapper);
  container.scrollTop = container.scrollHeight;
}

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  input.disabled = true;
  addBubble(text, 'user');
  addTypingIndicator();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sessionId, message: text }),
    });
    const data = await res.json();
    sessionId = data.session_id || sessionId;

    removeTypingIndicator();
    addBubble(data.message || '증상을 분석했습니다. 아래 진료과를 추천드려요:', 'bot');
    if (data.departments && data.departments.length > 0) {
      addDeptCards(data.departments);
    }
  } catch (e) {
    removeTypingIndicator();
    addBubble('일시적인 오류가 발생했습니다. 다시 시도해 주세요.', 'bot');
  } finally {
    input.disabled = false;
    input.focus();
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chatInput');
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMessage();
  });

  const urlParams = new URLSearchParams(window.location.search);
  const symptom = urlParams.get('symptom');
  if (symptom) {
    input.value = symptom;
    setTimeout(() => sendMessage(), 300);
  }
});
```

**Step 2: 브라우저 테스트**

1. `http://localhost:8000/chatbot` 접속
2. "머리가 아프고 열이 나요" 입력 → 타이핑 인디케이터 → 실제 Claude 추천 카드 표시
3. 추가 증상 입력 → 이전 대화 컨텍스트 유지 확인

**Step 3: Commit**

```bash
git add static/js/chatbot.js
git commit -m "feat: 챗봇 프론트엔드 Claude API 연동 (Mock 응답 제거)"
```

---

## Task 3: Sprint 3 최종 점검 및 push

**Step 1: 전체 플로우 테스트**

```
1. http://localhost:8000 → 메인 → "증상으로 찾기" → 챗봇 화면
2. "목이 아프고 기침이 나요" 입력 → Claude 추천 카드 표시 확인
3. 추천 카드 클릭 → 병원 목록 표시 확인
4. 추가 증상 입력 → 멀티턴 대화 확인
```

**Step 2: Push**

```bash
git push origin sprint3
```

---

## ✅ Sprint 3 완료 기준

- [ ] Claude API 기반 증상→진료과 추천 동작 (2~3개 + 근거)
- [ ] 멀티턴 대화 지원
- [ ] 타이핑 인디케이터 표시 (API 응답 대기 중)
- [ ] `git push origin sprint3` 완료
