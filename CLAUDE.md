# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

"내 주변 병원 찾기" (Nearby Hospital Finder) — a location-based hospital recommendation web service built with Python/FastAPI. Users input symptoms via chatbot (Claude API) or select a medical department directly, then find nearby hospitals filtered by distance, operating hours, and review ratings.

- **Language**: Korean (UI, docs, comments)
- **Stack**: FastAPI + Jinja2 Templates + Vanilla JS + Kakao Maps SDK
- **Deployment**: Render (single-server monolith)

## Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run dev server (port 8000)
uvicorn main:app --reload

# E2E tests (Playwright)
# Tests located in tests/e2e/
```

## Architecture

```
Browser (Jinja2 + Vanilla JS + Kakao Maps SDK)
    ↓ HTTP
FastAPI Server
    ├── routers/chatbot.py    → services/claude_service.py   → Claude API (symptom→department)
    ├── routers/hospital.py   → services/hira_service.py     → 건강보험심사평가원 API (hospital data)
    │                         → services/kakao_service.py    → Kakao Maps API (geocoding)
    ├── routers/review.py     → services/naver_crawler.py    → Naver Maps (Playwright crawling for reviews)
    │                         → services/claude_service.py   → Claude API (review summarization)
    └── routers/location.py   → services/kakao_service.py    → Kakao Maps Geocoding
```

- `services/scoring_service.py` — Review scoring: positive points - negative points
- `templates/` — Jinja2 HTML (base layout + page templates + reusable components/)
- `static/` — CSS, JS, images

## Key Design Decisions

- **Jinja2 + Vanilla JS over SPA**: PRD requires single-server deployment; no build pipeline needed
- **Kakao Maps over Naver Maps**: Kakao provides geocoding and map SDK; reviews are separately crawled from Naver
- **Frontend-first approach**: Build UI with mock data first → user review → then backend integration
- **Responsive**: Mobile (375px) / Tablet (768px) / PC (1440px)

## External APIs & Environment Variables

Managed via `.env` file (see `.env.example`):
- `CLAUDE_API_KEY` — Symptom analysis + review summarization
- `KAKAO_MAP_API_KEY` — Geocoding + hospital search
- `HIRA_API_KEY` — 건강보험심사평가원 (public hospital data)

## Development Methodology

- Agile/Scrum, 2-week sprints (5 phases over 10 weeks)
- **Karpathy Guidelines**: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution
- All tasks follow `[task] → verify: [verification method]` format
- Playwright MCP verification scenarios per phase
- See `docs/PRD.md` for requirements and `docs/ROADMAP.md` for detailed phase plans

## Sprint Workflow Agents

This project uses Claude Code agents in `.claude/agents/`:
- `sprint-planner` — Creates sprint plans from ROADMAP.md
- `sprint-close` — Sprint completion (ROADMAP update, PR, code review, verification report)
- `code-reviewer` — Reviews completed work against plans
- `prd-to-roadmap` — Converts PRD to actionable roadmap
