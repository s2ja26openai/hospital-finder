# Sprint 1 — 프론트엔드 프로토타입 구현 계획

## ✅ 완료 기록 (2026-03-13)

| 항목 | 상태 | 비고 |
|------|------|------|
| FastAPI 프로젝트 구조 생성 | ✅ 완료 | main.py, routers/, templates/, static/, .env.example |
| Jinja2 base.html 레이아웃 | ✅ 완료 | 공통 헤더/푸터, CSS 변수 시스템 |
| 반응형 CSS 기본 구조 | ✅ 완료 | 375px/768px/1440px 미디어 쿼리 |
| 메인 페이지 진입 UI | ✅ 완료 | 증상 입력창 + 진료과 선택 버튼 |
| 챗봇 UI (Mock) | ✅ 완료 | 사용자/봇 말풍선, 진료과 추천 카드 |
| 위치 설정 UI | ✅ 완료 | GPS 위치 획득 + 주소 입력 fallback |
| 병원 목록 UI (Mock) | ✅ 완료 | 카드 컴포넌트, 반경/정렬 필터 |
| 카카오맵 SDK 연동 | ✅ 완료 | 지도 + 병원 핀 마커 표시 |
| 병원 상세 UI | ✅ 완료 | 전화번호, 주소, 운영시간 표시 |
| 반응형 최종 검증 | ✅ 완료 | 3개 뷰포트 레이아웃 정상 확인 |

**완료 커밋:** `9c3571a`, `3ef90c7`, `0df77a7`

---

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** FastAPI 프로젝트를 초기 설정하고, Mock 데이터 기반으로 전체 UI 플로우(메인/챗봇/위치설정/병원목록/지도+상세)를 완성하여 사용자 검토를 받는다.

**Architecture:** FastAPI 단일 서버에 Jinja2 템플릿을 사용하는 서버사이드 렌더링 방식. 백엔드 API 연동 없이 JavaScript 인라인 Mock 데이터만 사용한다. 반응형 CSS는 외부 프레임워크 없이 자체 작성한다.

**Tech Stack:** Python 3.11+, FastAPI, Uvicorn, Jinja2, python-dotenv, Vanilla JS, 카카오맵 JavaScript SDK

---

## 스프린트 개요

| 항목 | 내용 |
|------|------|
| **스프린트 번호** | Sprint 1 |
| **기간** | 2026-03-13 ~ 2026-03-27 (2주) |
| **마일스톤** | M1: 프론트엔드 프로토타입 완성 |
| **목표** | Mock 데이터로 전체 UI 플로우 동작 + 사용자 검토 피드백 수집 |
| **원칙** | 프론트엔드 먼저 완성 → 사용자 검토 → 백엔드 개발 착수 |

---

## 1. 스프린트 목표

**측정 가능한 목표:**

1. `uvicorn main:app --reload` 실행 시 `http://localhost:8000` 접속 200 OK 응답
2. 전체 5개 화면(메인/챗봇/위치설정/병원목록/병원상세)이 Mock 데이터로 동작
3. Playwright 검증 시나리오 10개 전체 통과
4. 375px / 768px / 1440px 3개 뷰포트에서 레이아웃 깨짐 없음
5. 사용자 검토 세션 완료 → Phase 2 진입 승인

---

## 2. 구현 범위

### 포함 (In Scope)

| 기능 ID | 설명 |
|---------|------|
| 프로젝트 초기 설정 | FastAPI 구조, Jinja2 설정, base.html, 반응형 CSS 기초, requirements.txt |
| F-01 | 메인 페이지: 증상으로 찾기(입력창) + 진료과로 찾기(드롭다운) 2가지 진입 방식 |
| F-02 (Mock) | 챗봇 UI: 대화 버블, Mock 봇 응답, 진료과 추천 카드 |
| F-03 | 위치 설정 UI: GPS Geolocation API + 주소 입력 fallback 모달 |
| F-04 (Mock) | 병원 목록 UI: 카드, 운영상태 3종, 반경 선택, 정렬 토글 |
| F-06 (Mock) | 카카오맵 연동, 병원 핀 마커, 상세 정보 패널, 길 안내 버튼 |
| 반응형 검증 | 375px / 768px / 1440px 전 화면 |

### 제외 (Out of Scope)

- 백엔드 API 실데이터 연동 (Phase 2)
- Claude API 실연동 (Phase 3)
- 건강보험심사평가원 API 연동 (Phase 2)
- 네이버 리뷰 크롤링 (Phase 4)
- 도보 경로 실계산 (Phase 3)
- 사용자 인증/즐겨찾기 (MVP 이후 Backlog)

---

## 3. 가정 (Assumptions) — Think Before Coding

- 카카오맵 JavaScript SDK 키가 `.env`의 `KAKAO_JS_API_KEY`에 이미 등록되어 있다
- 디자인 시안 없이 기능 중심 UI로 진행한다 (디자인 개선은 이후 피드백 반영)
- Mock 데이터만으로 충분히 사용자 피드백을 받을 수 있다
- 브라우저 Geolocation API로 GPS 위치를 획득할 수 있다
- **불확실:** 카카오맵 SDK 무료 할당량으로 개발 기간 중 충분한지 확인 필요

---

## 4. Task Breakdown

### Task 1: FastAPI 프로젝트 초기 구조 생성

**Files:**
- Create: `main.py`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `routers/__init__.py`
- Create: `templates/` (디렉토리)
- Create: `static/css/`, `static/js/`, `static/images/` (디렉토리)

**Step 1: requirements.txt 작성**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
jinja2==3.1.4
python-dotenv==1.0.1
httpx==0.27.0
```

**Step 2: .env.example 작성**

```
KAKAO_JS_API_KEY=your_kakao_js_api_key_here
CLAUDE_API_KEY=your_claude_api_key_here
KAKAO_MAP_API_KEY=your_kakao_rest_api_key_here
HIRA_API_KEY=your_hira_api_key_here
```

**Step 3: main.py 작성**

```python
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="내 주변 병원 찾기")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

KAKAO_JS_API_KEY = os.getenv("KAKAO_JS_API_KEY", "")

@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "kakao_js_api_key": KAKAO_JS_API_KEY}
    )

@app.get("/chatbot")
async def chatbot(request: Request, department: str = ""):
    return templates.TemplateResponse(
        "chatbot.html",
        {"request": request, "kakao_js_api_key": KAKAO_JS_API_KEY, "department": department}
    )

@app.get("/hospitals")
async def hospitals(request: Request, department: str = ""):
    return templates.TemplateResponse(
        "hospital_list.html",
        {"request": request, "kakao_js_api_key": KAKAO_JS_API_KEY, "department": department}
    )

@app.get("/hospitals/{hospital_id}")
async def hospital_detail(request: Request, hospital_id: str):
    return templates.TemplateResponse(
        "hospital_detail.html",
        {"request": request, "kakao_js_api_key": KAKAO_JS_API_KEY, "hospital_id": hospital_id}
    )
```

**Step 4: 빈 디렉토리 초기화 파일 생성**

```bash
mkdir -p routers templates/components static/css static/js static/images
touch routers/__init__.py
```

**Step 5: 의존성 설치 및 서버 기동 확인**

Run: `pip install -r requirements.txt && uvicorn main:app --reload`
Expected: `INFO: Application startup complete.` 출력, `http://localhost:8000` 접속 시 500 (템플릿 없음) 또는 200 응답

**Step 6: Commit**

```bash
git add main.py requirements.txt .env.example routers/
git commit -m "feat: FastAPI 프로젝트 초기 구조 생성"
```

---

### Task 2: base.html 레이아웃 및 반응형 CSS 기초

**Files:**
- Create: `templates/base.html`
- Create: `static/css/base.css`

**Step 1: base.css 작성 (CSS 변수 + 반응형 기초)**

```css
/* static/css/base.css */
:root {
  --color-primary: #3182f6;
  --color-primary-dark: #1b64da;
  --color-bg: #f8f9fa;
  --color-surface: #ffffff;
  --color-text: #191f28;
  --color-text-sub: #6b7684;
  --color-border: #e5e8eb;
  --color-open: #00b050;
  --color-closed: #f04452;
  --color-upcoming: #f7931e;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.08);
  --shadow-md: 0 4px 16px rgba(0,0,0,0.12);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Noto Sans KR', sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  font-size: 16px;
  line-height: 1.5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

/* 모바일 375px */
@media (max-width: 480px) {
  body { font-size: 14px; }
  .container { padding: 0 12px; }
}

/* 태블릿 768px */
@media (min-width: 481px) and (max-width: 1024px) {
  .container { padding: 0 24px; }
}

/* PC 1440px+ */
@media (min-width: 1025px) {
  .container { padding: 0 32px; }
}

/* 공통 버튼 */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 20px;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s;
}

.btn-primary {
  background: var(--color-primary);
  color: #fff;
}

.btn-primary:hover { background: var(--color-primary-dark); }
.btn-primary:active { transform: scale(0.98); }

.btn-outline {
  background: transparent;
  color: var(--color-primary);
  border: 1.5px solid var(--color-primary);
}

/* 공통 헤더 */
.header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  padding: 12px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-logo {
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
  text-decoration: none;
}
```

**Step 2: base.html 작성**

```html
<!-- templates/base.html -->
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}내 주변 병원 찾기{% endblock %}</title>
  <link rel="stylesheet" href="/static/css/base.css">
  {% block extra_css %}{% endblock %}
</head>
<body>
  <header class="header">
    <div class="container header-inner">
      <a href="/" class="header-logo">내 주변 병원 찾기</a>
      <nav>
        <a href="/" class="btn btn-outline" style="padding:6px 14px;font-size:13px;">홈</a>
      </nav>
    </div>
  </header>

  <main>
    {% block content %}{% endblock %}
  </main>

  {% block scripts %}{% endblock %}
</body>
</html>
```

**Step 3: 서버 재기동 후 base 레이아웃 렌더링 확인**

Run: `uvicorn main:app --reload`
Expected: `/` 접속 시 base 레이아웃이 적용된 HTML 반환 (헤더 포함)

**Step 4: Commit**

```bash
git add templates/base.html static/css/base.css
git commit -m "feat: base.html 레이아웃 및 반응형 CSS 기초 작성"
```

---

### Task 3: F-01 메인 페이지 — 2가지 탐색 진입 방식

**Files:**
- Create: `templates/index.html`
- Create: `static/css/index.css`
- Create: `static/js/index.js`

**Step 1: index.css 작성**

```css
/* static/css/index.css */
.hero {
  padding: 60px 0 40px;
  text-align: center;
}

.hero-title {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 12px;
  color: var(--color-text);
}

.hero-subtitle {
  font-size: 16px;
  color: var(--color-text-sub);
  margin-bottom: 40px;
}

.entry-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  max-width: 720px;
  margin: 0 auto;
}

.entry-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 32px 24px;
  box-shadow: var(--shadow-sm);
  border: 1.5px solid var(--color-border);
  cursor: pointer;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.entry-card:hover {
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary);
}

.entry-card-icon {
  font-size: 36px;
  margin-bottom: 12px;
}

.entry-card-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 6px;
}

.entry-card-desc {
  font-size: 13px;
  color: var(--color-text-sub);
}

/* 증상 입력창 */
.symptom-section {
  max-width: 560px;
  margin: 0 auto 12px;
}

.symptom-input-wrap {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

.symptom-input {
  flex: 1;
  padding: 12px 16px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 15px;
  outline: none;
  transition: border-color 0.15s;
}

.symptom-input:focus { border-color: var(--color-primary); }

/* 진료과 드롭다운 */
.dept-section {
  max-width: 560px;
  margin: 32px auto 0;
}

.dept-section-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}

.dept-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.dept-btn {
  padding: 8px 16px;
  border: 1.5px solid var(--color-border);
  border-radius: 20px;
  background: var(--color-surface);
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s;
}

.dept-btn:hover {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

@media (max-width: 600px) {
  .entry-cards { grid-template-columns: 1fr; }
  .hero-title { font-size: 24px; }
}
```

**Step 2: index.html 작성**

```html
<!-- templates/index.html -->
{% extends "base.html" %}
{% block title %}내 주변 병원 찾기{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="/static/css/index.css">
{% endblock %}

{% block content %}
<div class="container">
  <section class="hero">
    <h1 class="hero-title">내 주변 병원 찾기</h1>
    <p class="hero-subtitle">증상을 입력하거나 진료과를 선택해 주변 병원을 찾아보세요</p>

    <!-- 증상으로 찾기 -->
    <div class="symptom-section">
      <div class="symptom-input-wrap">
        <input
          type="text"
          id="symptomInput"
          class="symptom-input"
          placeholder="증상을 입력하세요 (예: 머리가 아파요)"
          aria-label="증상 입력"
        >
        <button class="btn btn-primary" onclick="goToChatbot()">증상으로 찾기</button>
      </div>
    </div>

    <!-- 진료과로 찾기 -->
    <div class="dept-section">
      <div class="dept-section-title">또는 진료과를 직접 선택하세요</div>
      <div class="dept-grid" id="deptGrid"></div>
    </div>
  </section>
</div>
{% endblock %}

{% block scripts %}
<script src="/static/js/index.js"></script>
{% endblock %}
```

**Step 3: index.js 작성**

```javascript
// static/js/index.js
const DEPARTMENTS = [
  '내과', '외과', '정형외과', '이비인후과', '피부과',
  '안과', '치과', '산부인과', '비뇨기과', '소아청소년과',
  '신경과', '정신건강의학과', '흉부외과', '성형외과', '재활의학과'
];

function renderDepts() {
  const grid = document.getElementById('deptGrid');
  DEPARTMENTS.forEach(dept => {
    const btn = document.createElement('button');
    btn.className = 'dept-btn';
    btn.textContent = dept;
    btn.onclick = () => goToHospitals(dept);
    grid.appendChild(btn);
  });
}

function goToChatbot() {
  const symptom = document.getElementById('symptomInput').value.trim();
  if (!symptom) {
    alert('증상을 입력해 주세요.');
    return;
  }
  const params = new URLSearchParams({ symptom });
  window.location.href = `/chatbot?${params}`;
}

function goToHospitals(dept) {
  const params = new URLSearchParams({ department: dept });
  window.location.href = `/hospitals?${params}`;
}

// Enter 키 지원
document.addEventListener('DOMContentLoaded', () => {
  renderDepts();
  const input = document.getElementById('symptomInput');
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') goToChatbot();
  });
});
```

**Step 4: 브라우저에서 메인 페이지 확인**

Run: `uvicorn main:app --reload`
Expected: `http://localhost:8000` 접속 시 증상 입력창 + 15개 진료과 버튼 표시. 진료과 클릭 시 `/hospitals?department=내과` 로 이동.

**Step 5: Commit**

```bash
git add templates/index.html static/css/index.css static/js/index.js
git commit -m "feat: F-01 메인 페이지 2가지 탐색 진입 방식 구현"
```

---

### Task 4: F-02 챗봇 UI (Mock 데이터)

**Files:**
- Create: `templates/chatbot.html`
- Create: `static/css/chatbot.css`
- Create: `static/js/chatbot.js`

**Step 1: chatbot.css 작성**

```css
/* static/css/chatbot.css */
.chat-layout {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 60px);
  max-width: 640px;
  margin: 0 auto;
  padding: 0 16px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.bubble {
  max-width: 80%;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  font-size: 14px;
  line-height: 1.6;
}

.bubble-bot {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}

.bubble-user {
  background: var(--color-primary);
  color: #fff;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

.bubble-typing {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 14px 16px;
}

.typing-dot {
  width: 8px;
  height: 8px;
  background: var(--color-text-sub);
  border-radius: 50%;
  animation: typing 1s infinite;
}

.typing-dot:nth-child(2) { animation-delay: 0.2s; }
.typing-dot:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30% { transform: translateY(-6px); opacity: 1; }
}

/* 진료과 추천 카드 */
.dept-recommendation {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dept-card {
  background: var(--color-surface);
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 14px 16px;
  cursor: pointer;
  transition: border-color 0.15s, box-shadow 0.15s;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dept-card:hover {
  border-color: var(--color-primary);
  box-shadow: var(--shadow-sm);
}

.dept-card-name {
  font-weight: 700;
  font-size: 15px;
}

.dept-card-reason {
  font-size: 13px;
  color: var(--color-text-sub);
  margin-top: 2px;
}

.dept-card-arrow { font-size: 18px; color: var(--color-primary); }

/* 입력창 */
.chat-input-area {
  padding: 12px 0 20px;
  display: flex;
  gap: 8px;
}

.chat-input {
  flex: 1;
  padding: 12px 16px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 15px;
  outline: none;
  transition: border-color 0.15s;
}

.chat-input:focus { border-color: var(--color-primary); }
```

**Step 2: chatbot.html 작성**

```html
<!-- templates/chatbot.html -->
{% extends "base.html" %}
{% block title %}증상 챗봇 — 내 주변 병원 찾기{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="/static/css/chatbot.css">
{% endblock %}

{% block content %}
<div class="container">
  <div class="chat-layout">
    <div class="chat-messages" id="chatMessages">
      <div class="bubble bubble-bot">
        안녕하세요! 증상을 알려주시면 적합한 진료과를 추천해 드릴게요.
      </div>
    </div>
    <div class="chat-input-area">
      <input
        type="text"
        id="chatInput"
        class="chat-input"
        placeholder="증상을 입력하세요..."
        aria-label="증상 입력"
      >
      <button class="btn btn-primary" onclick="sendMessage()">전송</button>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
  const INITIAL_SYMPTOM = "{{ department or '' }}";
</script>
<script src="/static/js/chatbot.js"></script>
{% endblock %}
```

**Step 3: chatbot.js 작성 (Mock 데이터 기반)**

```javascript
// static/js/chatbot.js
const MOCK_RESPONSES = {
  default: [
    { name: '내과', reason: '감기, 편두통, 소화기 증상 가능성' },
    { name: '신경과', reason: '두통 관련 신경계 질환 가능성' },
    { name: '이비인후과', reason: '귀, 코, 목 관련 증상 가능성' }
  ],
  열: [
    { name: '내과', reason: '발열, 감기, 독감 가능성' },
    { name: '소아청소년과', reason: '소아 발열의 경우' },
    { name: '감염내과', reason: '고열 지속 시 감염 질환 가능성' }
  ],
  배: [
    { name: '내과', reason: '소화기 질환, 위염, 장염 가능성' },
    { name: '외과', reason: '급성 복통, 맹장염 가능성' },
    { name: '산부인과', reason: '여성의 경우 자궁/난소 관련 가능성' }
  ],
  피부: [
    { name: '피부과', reason: '피부 질환, 습진, 알레르기 가능성' },
    { name: '내과', reason: '전신 질환에 의한 피부 증상 가능성' },
    { name: '성형외과', reason: '상처 관련 치료 필요 시' }
  ]
};

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

function getMockDepts(symptom) {
  for (const [key, depts] of Object.entries(MOCK_RESPONSES)) {
    if (key !== 'default' && symptom.includes(key)) return depts;
  }
  return MOCK_RESPONSES.default;
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

function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input.value.trim();
  if (!text) return;

  input.value = '';
  addBubble(text, 'user');
  addTypingIndicator();

  setTimeout(() => {
    removeTypingIndicator();
    addBubble('입력하신 증상을 분석했습니다. 아래 진료과를 추천드려요:', 'bot');
    addDeptCards(getMockDepts(text));
  }, 1200);
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('chatInput');
  input.addEventListener('keydown', e => {
    if (e.key === 'Enter') sendMessage();
  });

  // URL에서 초기 증상값 처리
  const urlParams = new URLSearchParams(window.location.search);
  const symptom = urlParams.get('symptom');
  if (symptom) {
    input.value = symptom;
    setTimeout(() => sendMessage(), 300);
  }
});
```

**Step 4: 챗봇 UI 동작 확인**

Run: `uvicorn main:app --reload`
Expected: `http://localhost:8000/chatbot` 접속 → "머리가 아파요" 입력 → 타이핑 인디케이터 1.2초 표시 → 진료과 카드 3개 표시 → 카드 클릭 시 `/hospitals?department=내과` 이동

**Step 5: Commit**

```bash
git add templates/chatbot.html static/css/chatbot.css static/js/chatbot.js
git commit -m "feat: F-02 챗봇 UI Mock 데이터 구현 (타이핑 인디케이터, 진료과 추천 카드)"
```

---

### Task 5: F-03 위치 설정 UI (GPS + 주소 fallback)

**Files:**
- Create: `static/js/location.js`
- Modify: `static/css/base.css` (모달 스타일 추가)

**Step 1: 모달 스타일을 base.css에 추가**

```css
/* base.css 하단에 추가 */
/* 모달 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-overlay.hidden { display: none; }

.modal {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 28px 24px;
  width: 100%;
  max-width: 420px;
  box-shadow: var(--shadow-md);
}

.modal-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
}

.modal-desc {
  font-size: 14px;
  color: var(--color-text-sub);
  margin-bottom: 20px;
}

.modal-input {
  width: 100%;
  padding: 12px 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 15px;
  margin-bottom: 12px;
  outline: none;
}

.modal-input:focus { border-color: var(--color-primary); }

.modal-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 위치 표시 바 */
.location-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 14px;
  cursor: pointer;
}

.location-bar-icon { color: var(--color-primary); }
.location-bar-text { flex: 1; }
.location-bar-change { font-size: 13px; color: var(--color-primary); }
```

**Step 2: location.js 작성**

```javascript
// static/js/location.js
// 위치 상태를 전역으로 관리 (다른 페이지 JS에서 사용)
window.LocationState = {
  lat: 37.5665,   // 기본값: 서울 시청 (Mock)
  lng: 126.9780,
  label: '현재 위치',
  isSet: false
};

function showLocationModal() {
  document.getElementById('locationModal').classList.remove('hidden');
  document.getElementById('addressInput').focus();
}

function hideLocationModal() {
  document.getElementById('locationModal').classList.add('hidden');
}

function requestGPS() {
  if (!navigator.geolocation) {
    showLocationModal();
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      window.LocationState.lat = pos.coords.latitude;
      window.LocationState.lng = pos.coords.longitude;
      window.LocationState.label = '현재 위치 (GPS)';
      window.LocationState.isSet = true;
      updateLocationBar();
      hideLocationModal();
      if (typeof onLocationSet === 'function') onLocationSet();
    },
    () => {
      // GPS 권한 거부 시 주소 입력 fallback
      showLocationModal();
    },
    { timeout: 8000 }
  );
}

function confirmAddress() {
  const val = document.getElementById('addressInput').value.trim();
  if (!val) return;
  // Phase 1: Mock 좌표 사용 (Phase 2에서 Geocoding API로 교체)
  window.LocationState.lat = 37.5665;
  window.LocationState.lng = 126.9780;
  window.LocationState.label = val;
  window.LocationState.isSet = true;
  updateLocationBar();
  hideLocationModal();
  if (typeof onLocationSet === 'function') onLocationSet();
}

function updateLocationBar() {
  const el = document.getElementById('locationBarText');
  if (el) el.textContent = window.LocationState.label;
}

// 모달 HTML을 동적으로 삽입
function injectLocationModal() {
  const html = `
    <div id="locationModal" class="modal-overlay hidden">
      <div class="modal">
        <div class="modal-title">위치 설정</div>
        <div class="modal-desc">주소 또는 지명을 입력하거나 GPS로 현재 위치를 확인하세요.</div>
        <input id="addressInput" class="modal-input" type="text"
               placeholder="예: 서울 강남구 역삼동"
               onkeydown="if(event.key==='Enter') confirmAddress()">
        <div class="modal-actions">
          <button class="btn btn-outline" onclick="requestGPS()">GPS 사용</button>
          <button class="btn btn-primary" onclick="confirmAddress()">확인</button>
        </div>
      </div>
    </div>
  `;
  document.body.insertAdjacentHTML('beforeend', html);
}

document.addEventListener('DOMContentLoaded', () => {
  injectLocationModal();
  // 페이지 최초 로딩 시 GPS 자동 요청
  requestGPS();
});
```

**Step 3: 위치 설정 동작 확인 항목**

Run: 브라우저 DevTools → Application → Geolocation 거부 설정 후 `/hospitals` 접속
Expected: GPS 거부 시 주소 입력 모달 자동 표시. 주소 입력 후 확인 클릭 시 모달 닫힘.

**Step 4: Commit**

```bash
git add static/js/location.js static/css/base.css
git commit -m "feat: F-03 위치 설정 UI 구현 (GPS Geolocation + 주소 fallback 모달)"
```

---

### Task 6: F-04 병원 목록 UI (Mock 데이터)

**Files:**
- Create: `templates/hospital_list.html`
- Create: `templates/components/hospital_card.html`
- Create: `templates/components/filter_bar.html`
- Create: `static/css/hospital_list.css`
- Create: `static/js/hospital_list.js`
- Create: `static/js/mock_data.js`

**Step 1: mock_data.js 작성 (운영상태 3종 포함)**

```javascript
// static/js/mock_data.js
window.MOCK_HOSPITALS = [
  {
    id: 'h001',
    name: '강남연세내과의원',
    departments: ['내과', '가정의학과'],
    address: '서울 강남구 역삼동 123-45',
    phone: '02-1234-5678',
    distance: 320,
    lat: 37.5010,
    lng: 127.0260,
    status: 'open',         // 진료 중
    statusText: '진료 중 · 21:00 마감',
    hours: { mon:'09:00-21:00', tue:'09:00-21:00', wed:'09:00-18:00',
             thu:'09:00-21:00', fri:'09:00-18:00', sat:'09:00-13:00', sun:'휴무' },
    reviewSummary: '친절한 진료, 대기 짧음 / 주차 불편',
    score: 3
  },
  {
    id: 'h002',
    name: '역삼정형외과',
    departments: ['정형외과', '재활의학과'],
    address: '서울 강남구 역삼동 234-56',
    phone: '02-2345-6789',
    distance: 480,
    lat: 37.5005,
    lng: 127.0280,
    status: 'upcoming',     // 진료 예정
    statusText: '09:00 진료시작',
    hours: { mon:'09:00-18:00', tue:'09:00-18:00', wed:'09:00-18:00',
             thu:'09:00-18:00', fri:'09:00-18:00', sat:'09:00-13:00', sun:'휴무' },
    reviewSummary: '전문의 상담 꼼꼼 / 예약 필수',
    score: 4
  },
  {
    id: 'h003',
    name: '강남이비인후과',
    departments: ['이비인후과'],
    address: '서울 강남구 삼성동 345-67',
    phone: '02-3456-7890',
    distance: 750,
    lat: 37.5087,
    lng: 127.0330,
    status: 'closed',       // 오늘 휴무
    statusText: '오늘 휴무',
    hours: { mon:'09:00-18:00', tue:'09:00-18:00', wed:'09:00-18:00',
             thu:'09:00-18:00', fri:'09:00-18:00', sat:'09:00-13:00', sun:'휴무' },
    reviewSummary: '시설 깔끔 / 주차 어려움',
    score: 2
  },
  {
    id: 'h004',
    name: '삼성피부과의원',
    departments: ['피부과'],
    address: '서울 강남구 삼성동 456-78',
    phone: '02-4567-8901',
    distance: 920,
    lat: 37.5092,
    lng: 127.0350,
    status: 'open',
    statusText: '진료 중 · 20:00 마감',
    hours: { mon:'10:00-20:00', tue:'10:00-20:00', wed:'10:00-20:00',
             thu:'10:00-20:00', fri:'10:00-20:00', sat:'10:00-14:00', sun:'휴무' },
    reviewSummary: '원장 친절, 빠른 처방 / 대기 김',
    score: 3
  },
  {
    id: 'h005',
    name: '강남안과의원',
    departments: ['안과'],
    address: '서울 강남구 논현동 567-89',
    phone: '02-5678-9012',
    distance: 1100,
    lat: 37.5115,
    lng: 127.0220,
    status: 'open',
    statusText: '진료 중 · 19:00 마감',
    hours: { mon:'09:00-19:00', tue:'09:00-19:00', wed:'09:00-14:00',
             thu:'09:00-19:00', fri:'09:00-19:00', sat:'09:00-13:00', sun:'휴무' },
    reviewSummary: '검사 꼼꼼, 장비 최신 / 비용 비쌈',
    score: 5
  }
];
```

**Step 2: hospital_list.css 작성**

```css
/* static/css/hospital_list.css */
.list-layout {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 0;
  height: calc(100vh - 60px);
}

.list-panel {
  overflow-y: auto;
  border-right: 1px solid var(--color-border);
}

.list-header {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  background: var(--color-bg);
  z-index: 10;
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}

.filter-label { font-size: 13px; color: var(--color-text-sub); }

.radius-btn {
  padding: 5px 12px;
  border: 1.5px solid var(--color-border);
  border-radius: 16px;
  background: var(--color-surface);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.radius-btn.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.sort-toggle {
  margin-left: auto;
  display: flex;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.sort-btn {
  padding: 5px 12px;
  border: none;
  background: var(--color-surface);
  font-size: 13px;
  cursor: pointer;
  transition: all 0.15s;
}

.sort-btn.active {
  background: var(--color-primary);
  color: #fff;
}

/* 병원 카드 */
.hospital-card {
  padding: 16px;
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background 0.1s;
}

.hospital-card:hover { background: #f0f4ff; }
.hospital-card.selected { background: #e8f0fe; border-left: 3px solid var(--color-primary); }

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 4px;
}

.card-name { font-size: 16px; font-weight: 700; }
.card-distance { font-size: 13px; color: var(--color-text-sub); }
.card-depts { font-size: 13px; color: var(--color-text-sub); margin-bottom: 6px; }

.card-status {
  display: inline-block;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 6px;
}

.status-open { background: #e6f7ee; color: var(--color-open); }
.status-upcoming { background: #fff3e0; color: var(--color-upcoming); }
.status-closed { background: #ffeef0; color: var(--color-closed); }

.card-review { font-size: 12px; color: var(--color-text-sub); }

/* 지도 패널 */
.map-panel { position: relative; }
#kakaoMap { width: 100%; height: 100%; }

/* 모바일: 지도 숨기고 목록만 */
@media (max-width: 768px) {
  .list-layout { grid-template-columns: 1fr; }
  .map-panel { display: none; }
}
```

**Step 3: hospital_list.html 작성**

```html
<!-- templates/hospital_list.html -->
{% extends "base.html" %}
{% block title %}병원 목록 — 내 주변 병원 찾기{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="/static/css/hospital_list.css">
{% endblock %}

{% block content %}
<div class="list-layout">
  <!-- 목록 패널 -->
  <div class="list-panel">
    <div class="list-header">
      <!-- 위치 바 -->
      <div class="location-bar" onclick="showLocationModal()" style="margin-bottom:10px;">
        <span class="location-bar-icon">📍</span>
        <span class="location-bar-text" id="locationBarText">위치 설정 중...</span>
        <span class="location-bar-change">변경</span>
      </div>

      <!-- 반경 필터 -->
      <div class="filter-row">
        <span class="filter-label">반경</span>
        <button class="radius-btn active" data-radius="500" onclick="setRadius(this)">500m</button>
        <button class="radius-btn" data-radius="1000" onclick="setRadius(this)">1km</button>
        <button class="radius-btn" data-radius="5000" onclick="setRadius(this)">5km</button>
        <button class="radius-btn" data-radius="10000" onclick="setRadius(this)">10km</button>

        <!-- 정렬 -->
        <div class="sort-toggle">
          <button class="sort-btn active" data-sort="score" onclick="setSort(this)">평점순</button>
          <button class="sort-btn" data-sort="distance" onclick="setSort(this)">거리순</button>
        </div>
      </div>

      <div id="listSummary" style="font-size:13px;color:var(--color-text-sub);"></div>
    </div>

    <div id="hospitalList"></div>
  </div>

  <!-- 지도 패널 -->
  <div class="map-panel">
    <div id="kakaoMap"></div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
  const SELECTED_DEPARTMENT = "{{ department or '' }}";
  const KAKAO_JS_API_KEY = "{{ kakao_js_api_key }}";
</script>
<script src="/static/js/mock_data.js"></script>
<script src="/static/js/location.js"></script>
<script src="/static/js/hospital_list.js"></script>
<script src="//dapi.kakao.com/v2/maps/sdk.js?appkey={{ kakao_js_api_key }}&autoload=false"></script>
{% endblock %}
```

**Step 4: hospital_list.js 작성**

```javascript
// static/js/hospital_list.js
let currentRadius = 500;
let currentSort = 'score';
let kakaoMap = null;
let markers = [];

function setRadius(btn) {
  document.querySelectorAll('.radius-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentRadius = parseInt(btn.dataset.radius);
  renderList();
}

function setSort(btn) {
  document.querySelectorAll('.sort-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  currentSort = btn.dataset.sort;
  renderList();
}

function filterAndSort(hospitals) {
  // 반경 필터 (Mock: distance 필드 기준)
  let filtered = hospitals.filter(h => h.distance <= currentRadius);
  // 진료과 필터
  if (SELECTED_DEPARTMENT) {
    filtered = filtered.filter(h => h.departments.includes(SELECTED_DEPARTMENT));
  }
  // 정렬
  if (currentSort === 'score') {
    filtered.sort((a, b) => {
      // 진료 중 > 진료 예정 > 휴무, 동점 시 점수 내림차순
      const statusOrder = { open: 0, upcoming: 1, closed: 2 };
      if (statusOrder[a.status] !== statusOrder[b.status]) {
        return statusOrder[a.status] - statusOrder[b.status];
      }
      return b.score - a.score;
    });
  } else {
    filtered.sort((a, b) => a.distance - b.distance);
  }
  return filtered;
}

function statusClass(status) {
  return { open: 'status-open', upcoming: 'status-upcoming', closed: 'status-closed' }[status];
}

function renderList() {
  const list = document.getElementById('hospitalList');
  const summary = document.getElementById('listSummary');
  const filtered = filterAndSort(window.MOCK_HOSPITALS);

  summary.textContent = `${filtered.length}개 병원`;
  list.innerHTML = '';

  if (filtered.length === 0) {
    list.innerHTML = '<div style="padding:40px;text-align:center;color:var(--color-text-sub);">해당 반경 내 병원이 없습니다.</div>';
    return;
  }

  filtered.forEach(h => {
    const card = document.createElement('div');
    card.className = 'hospital-card';
    card.dataset.id = h.id;
    card.innerHTML = `
      <div class="card-header">
        <span class="card-name">${h.name}</span>
        <span class="card-distance">${h.distance >= 1000 ? (h.distance/1000).toFixed(1)+'km' : h.distance+'m'}</span>
      </div>
      <div class="card-depts">${h.departments.join(' · ')}</div>
      <span class="card-status ${statusClass(h.status)}">${h.statusText}</span>
      <div class="card-review">${h.reviewSummary}</div>
    `;
    card.onclick = () => openDetail(h);
    list.appendChild(card);
  });

  updateMapMarkers(filtered);
}

function openDetail(hospital) {
  // 선택 상태 표시
  document.querySelectorAll('.hospital-card').forEach(c => c.classList.remove('selected'));
  const card = document.querySelector(`.hospital-card[data-id="${hospital.id}"]`);
  if (card) card.classList.add('selected');

  // 카카오맵 중심 이동
  if (kakaoMap) {
    const pos = new kakao.maps.LatLng(hospital.lat, hospital.lng);
    kakaoMap.setCenter(pos);
  }

  // 상세 패널 (간이 alert → Task 7에서 슬라이드 패널로 교체)
  window.location.href = `/hospitals/${hospital.id}`;
}

// 카카오맵 초기화
function initMap() {
  kakao.maps.load(() => {
    const container = document.getElementById('kakaoMap');
    const lat = window.LocationState ? window.LocationState.lat : 37.5665;
    const lng = window.LocationState ? window.LocationState.lng : 126.9780;
    kakaoMap = new kakao.maps.Map(container, {
      center: new kakao.maps.LatLng(lat, lng),
      level: 4
    });
    renderList();
  });
}

function updateMapMarkers(hospitals) {
  // 기존 마커 제거
  markers.forEach(m => m.setMap(null));
  markers = [];
  if (!kakaoMap) return;

  hospitals.forEach(h => {
    const marker = new kakao.maps.Marker({
      map: kakaoMap,
      position: new kakao.maps.LatLng(h.lat, h.lng),
      title: h.name
    });
    markers.push(marker);
  });
}

// 위치 설정 후 콜백
window.onLocationSet = () => renderList();

document.addEventListener('DOMContentLoaded', () => {
  if (KAKAO_JS_API_KEY && KAKAO_JS_API_KEY !== '') {
    initMap();
  } else {
    // API 키 없을 때 목록만 렌더링
    renderList();
  }
});
```

**Step 5: 병원 목록 UI 확인**

Run: `http://localhost:8000/hospitals?department=내과`
Expected: 내과 포함 병원만 필터링되어 카드 표시, 운영 상태 3종 뱃지(진료 중/진료시작/오늘 휴무) 정상 표시, 반경/정렬 버튼 동작

**Step 6: Commit**

```bash
git add templates/hospital_list.html static/css/hospital_list.css static/js/hospital_list.js static/js/mock_data.js
git commit -m "feat: F-04 병원 목록 UI 구현 (Mock 데이터, 반경 필터, 정렬 토글)"
```

---

### Task 7: F-06 카카오맵 연동 및 병원 상세 정보 UI

**Files:**
- Create: `templates/hospital_detail.html`
- Create: `static/css/hospital_detail.css`
- Create: `static/js/hospital_detail.js`
- Modify: `templates/hospital_list.html` (상세 슬라이드 패널로 교체)

**Step 1: hospital_detail.css 작성**

```css
/* static/css/hospital_detail.css */
.detail-layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 0;
  height: calc(100vh - 60px);
}

.detail-map { position: relative; }
#detailMap { width: 100%; height: 100%; }

.detail-panel {
  overflow-y: auto;
  padding: 24px 20px;
  border-left: 1px solid var(--color-border);
}

.detail-back {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 14px;
  color: var(--color-primary);
  text-decoration: none;
  margin-bottom: 16px;
}

.detail-name {
  font-size: 22px;
  font-weight: 800;
  margin-bottom: 4px;
}

.detail-depts {
  font-size: 14px;
  color: var(--color-text-sub);
  margin-bottom: 12px;
}

.detail-status {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 16px;
}

.detail-info-row {
  display: flex;
  gap: 8px;
  align-items: flex-start;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border);
  font-size: 14px;
}

.detail-info-label {
  width: 64px;
  color: var(--color-text-sub);
  flex-shrink: 0;
}

/* 운영시간 표 */
.hours-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-top: 12px;
}

.hours-table td { padding: 5px 0; }
.hours-table td:first-child { color: var(--color-text-sub); width: 40px; }
.hours-table tr.today td { font-weight: 700; color: var(--color-primary); }

/* 길 안내 버튼 영역 */
.nav-buttons {
  margin-top: 20px;
  display: flex;
  gap: 8px;
}

@media (max-width: 768px) {
  .detail-layout { grid-template-columns: 1fr; }
  .detail-map { height: 220px; }
  .detail-panel { border-left: none; border-top: 1px solid var(--color-border); }
}
```

**Step 2: hospital_detail.html 작성**

```html
<!-- templates/hospital_detail.html -->
{% extends "base.html" %}
{% block title %}병원 상세 — 내 주변 병원 찾기{% endblock %}
{% block extra_css %}
<link rel="stylesheet" href="/static/css/hospital_list.css">
<link rel="stylesheet" href="/static/css/hospital_detail.css">
{% endblock %}

{% block content %}
<div class="detail-layout">
  <!-- 지도 -->
  <div class="detail-map">
    <div id="detailMap"></div>
  </div>

  <!-- 상세 패널 -->
  <div class="detail-panel" id="detailPanel">
    <a href="/hospitals" class="detail-back">← 목록으로</a>
    <div id="detailContent">
      <div style="color:var(--color-text-sub);font-size:14px;">로딩 중...</div>
    </div>
  </div>
</div>
{% endblock %}

{% block scripts %}
<script>
  const HOSPITAL_ID = "{{ hospital_id }}";
  const KAKAO_JS_API_KEY = "{{ kakao_js_api_key }}";
</script>
<script src="/static/js/mock_data.js"></script>
<script src="/static/js/hospital_detail.js"></script>
<script src="//dapi.kakao.com/v2/maps/sdk.js?appkey={{ kakao_js_api_key }}&autoload=false"></script>
{% endblock %}
```

**Step 3: hospital_detail.js 작성**

```javascript
// static/js/hospital_detail.js
const DAY_NAMES = { mon:'월', tue:'화', wed:'수', thu:'목', fri:'금', sat:'토', sun:'일' };
const TODAY_KEY = ['sun','mon','tue','wed','thu','fri','sat'][new Date().getDay()];

function statusClass(status) {
  return { open: 'status-open', upcoming: 'status-upcoming', closed: 'status-closed' }[status];
}

function buildHoursTable(hours) {
  return `
    <table class="hours-table">
      ${Object.entries(hours).map(([key, val]) => `
        <tr class="${key === TODAY_KEY ? 'today' : ''}">
          <td>${DAY_NAMES[key]}</td>
          <td>${val}</td>
        </tr>
      `).join('')}
    </table>
  `;
}

function buildNavUrl(platform, lat, lng, name) {
  if (platform === 'kakao') {
    return `kakaomap://route?ep=${lat},${lng}&by=FOOT`;
  }
  return `nmap://route/walk?dlat=${lat}&dlng=${lng}&dname=${encodeURIComponent(name)}&appname=hospital-finder`;
}

function renderDetail(h) {
  const content = document.getElementById('detailContent');
  content.innerHTML = `
    <div class="detail-name">${h.name}</div>
    <div class="detail-depts">${h.departments.join(' · ')}</div>
    <span class="detail-status ${statusClass(h.status)}">${h.statusText}</span>

    <div class="detail-info-row">
      <span class="detail-info-label">주소</span>
      <span>${h.address}</span>
    </div>
    <div class="detail-info-row">
      <span class="detail-info-label">전화</span>
      <a href="tel:${h.phone}">${h.phone}</a>
    </div>
    <div class="detail-info-row" style="flex-direction:column;">
      <span class="detail-info-label" style="margin-bottom:4px;">운영시간</span>
      ${buildHoursTable(h.hours)}
    </div>

    <div class="nav-buttons">
      <a href="${buildNavUrl('kakao', h.lat, h.lng, h.name)}"
         class="btn btn-primary" target="_blank">카카오맵 길 안내</a>
      <a href="${buildNavUrl('naver', h.lat, h.lng, h.name)}"
         class="btn btn-outline" target="_blank">네이버 지도</a>
    </div>
  `;
}

function initDetailMap(hospital) {
  kakao.maps.load(() => {
    const container = document.getElementById('detailMap');
    const pos = new kakao.maps.LatLng(hospital.lat, hospital.lng);
    const map = new kakao.maps.Map(container, { center: pos, level: 3 });
    new kakao.maps.Marker({ map, position: pos, title: hospital.name });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  const hospital = window.MOCK_HOSPITALS.find(h => h.id === HOSPITAL_ID);
  if (!hospital) {
    document.getElementById('detailContent').innerHTML =
      '<div style="color:var(--color-closed);">병원 정보를 찾을 수 없습니다.</div>';
    return;
  }
  renderDetail(hospital);

  if (KAKAO_JS_API_KEY) {
    initDetailMap(hospital);
  }
});
```

**Step 4: 병원 상세 페이지 동작 확인**

Run: `http://localhost:8000/hospitals/h001`
Expected: 지도에 병원 위치 마커 표시, 상세 패널에 이름/주소/전화/운영시간 표 표시, 길 안내 버튼 2개 표시

**Step 5: Commit**

```bash
git add templates/hospital_detail.html static/css/hospital_detail.css static/js/hospital_detail.js
git commit -m "feat: F-06 병원 상세 정보 UI 및 카카오맵 연동 (Mock 좌표, 길 안내 버튼)"
```

---

### Task 8: 반응형 최종 검증

**Files:**
- Modify: `static/css/hospital_list.css` (모바일 지도 toggle)
- Modify: `static/css/chatbot.css` (모바일 입력창 고정)

**Step 1: 모바일 375px 검증 항목**

```
브라우저 DevTools → 375px 뷰포트:
- [ ] 메인 페이지: 진료과 버튼 격자 → 2열 이하로 wrapping
- [ ] 챗봇: 입력창이 뷰포트 하단에 고정되어 키보드 가림 없음
- [ ] 병원 목록: 지도 패널 숨김, 카드 목록 전체 너비 표시
- [ ] 병원 상세: 지도 220px 높이 → 상세 패널 스크롤
```

**Step 2: 태블릿 768px 검증**

```
브라우저 DevTools → 768px 뷰포트:
- [ ] 병원 목록: 1열 레이아웃(지도 숨김) 또는 좁은 2열 레이아웃
- [ ] 메인 페이지: entry-cards 2열 유지
```

**Step 3: PC 1440px 검증**

```
브라우저 DevTools → 1440px 뷰포트:
- [ ] 병원 목록: 목록 패널 + 지도 패널 2열 레이아웃 정상
- [ ] 병원 상세: 지도 + 패널 2열 레이아웃 정상
```

**Step 4: 챗봇 모바일 입력창 고정 CSS 추가**

```css
/* chatbot.css 추가 */
@media (max-width: 480px) {
  .chat-layout {
    height: calc(100vh - 60px);
  }
  .chat-input-area {
    position: sticky;
    bottom: 0;
    background: var(--color-bg);
    padding-bottom: env(safe-area-inset-bottom, 12px);
  }
}
```

**Step 5: 반응형 검증 완료 후 Commit**

```bash
git add static/css/chatbot.css static/css/hospital_list.css static/css/hospital_detail.css
git commit -m "fix: 모바일/태블릿 반응형 레이아웃 최종 보정"
```

---

## 5. Playwright 검증 시나리오 (http://localhost:8000)

```
1. http://localhost:8000 접속 → 메인 페이지 로딩, 2가지 진입 방식 표시 확인
2. "증상으로 찾기" 입력창에 "머리가 아파요" 입력 → 엔터 → 챗봇 화면 전환 확인
3. 챗봇에서 1.2초 후 타이핑 인디케이터 → 진료과 추천 카드 3개 표시 확인
4. 진료과 카드 클릭 → 병원 목록 화면으로 전환, URL에 department 파라미터 확인
5. "진료과로 찾기"에서 "내과" 버튼 클릭 → 병원 목록 화면 전환 확인
6. 병원 카드 5개 이상 표시, 운영 상태 3종 뱃지 텍스트 확인 (진료 중/진료시작/오늘 휴무)
7. 반경 버튼 "1km" 클릭 → active 상태 하이라이트 변경 확인
8. 정렬 "거리순" 클릭 → 목록 카드 순서 변경 확인
9. 병원 카드 클릭 → 상세 페이지 이동, 전화번호/주소/운영시간 표 표시 확인
10. 모바일 뷰포트(375px)에서 전체 UI 레이아웃 깨짐 없음 확인
```

---

## 6. 의존성 및 리스크

### 태스크 간 의존 관계

| 선행 | 후행 | 이유 |
|------|------|------|
| Task 1 (프로젝트 구조) | Task 2~8 전체 | FastAPI 서버 및 디렉토리 구조 필요 |
| Task 2 (base.html, base.css) | Task 3~8 전체 | 공통 레이아웃 및 CSS 변수 필요 |
| Task 6 (mock_data.js) | Task 7 (상세 페이지) | Mock 데이터 조회 필요 |
| Task 5 (location.js) | Task 6 (병원 목록) | 위치 상태 전역 변수 필요 |

### 병렬 가능 작업

- Task 3 (메인 페이지) + Task 4 (챗봇 UI): 독립적 화면
- Task 5 (위치 설정) + Task 4 (챗봇 UI): CSS만 공유, JS는 독립

### 리스크

| # | 리스크 | 완화 전략 |
|---|--------|-----------|
| R1 | 카카오맵 API 키 미설정 시 지도 영역 빈 화면 | API 키 없을 때 목록 렌더링은 정상 진행, 지도는 placeholder 표시 |
| R2 | 브라우저 Geolocation 미지원 | `navigator.geolocation` 존재 확인 후 fallback 모달 즉시 표시 |
| R3 | Mock 데이터가 사용자 피드백에 불충분한 경우 | Mock 데이터 다양성 보강 (병원 수 10개 이상으로 확대) |
| R4 | Jinja2 템플릿 캐싱으로 수정사항 미반영 | `uvicorn main:app --reload` 사용으로 자동 반영 |

---

## 7. 완료 기준 (Definition of Done)

ROADMAP Phase 1 완료 기준을 그대로 반영합니다.

- [ ] 모든 화면이 Mock 데이터로 동작 (메인, 챗봇, 병원 목록, 병원 상세, 지도)
- [ ] 모바일(375px) / 태블릿(768px) / PC(1440px) 반응형 레이아웃 깨짐 없음
- [ ] Playwright 검증 시나리오 10개 전체 통과
- [ ] 사용자 검토 피드백 수집 완료 → Phase 2 시작 조건 충족

---

## 8. 예상 산출물

| 산출물 | 경로 |
|--------|------|
| FastAPI 앱 진입점 | `main.py` |
| 의존성 목록 | `requirements.txt` |
| 환경변수 예시 | `.env.example` |
| 공통 레이아웃 | `templates/base.html` |
| 메인 페이지 | `templates/index.html` |
| 챗봇 페이지 | `templates/chatbot.html` |
| 병원 목록 페이지 | `templates/hospital_list.html` |
| 병원 상세 페이지 | `templates/hospital_detail.html` |
| 공통 CSS | `static/css/base.css` |
| 페이지별 CSS | `static/css/index.css`, `chatbot.css`, `hospital_list.css`, `hospital_detail.css` |
| Mock 데이터 | `static/js/mock_data.js` |
| 위치 설정 JS | `static/js/location.js` |
| 페이지별 JS | `static/js/index.js`, `chatbot.js`, `hospital_list.js`, `hospital_detail.js` |

---

## 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경변수 설정 (.env 파일 생성)
cp .env.example .env
# .env에서 KAKAO_JS_API_KEY 설정

# 3. 개발 서버 실행
uvicorn main:app --reload

# 4. 브라우저에서 확인
# http://localhost:8000
```

---

> 이 계획은 ROADMAP.md Phase 1 (2026-03-13 ~ 2026-03-27) 기준으로 작성되었습니다.
> 각 Task는 writing-plans 스킬의 bite-sized task 형식(2~5분 단위)으로 분해되었습니다.
> Phase 1 완료 후 사용자 검토 게이트를 통과해야 Phase 2 착수가 가능합니다.
