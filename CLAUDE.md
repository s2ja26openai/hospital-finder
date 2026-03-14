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

# Run tests
pip install -r requirements-dev.txt
pytest -v

# Run tests with coverage
pytest --cov=services --cov=routers --cov-report=term-missing
```

## Architecture

```
Browser (Jinja2 + Vanilla JS + Kakao Maps SDK)
    ↓ HTTP
FastAPI Server
    ├── routers/chatbot.py    → services/claude_service.py        → Anthropic Claude API (symptom→department)
    ├── routers/hospital.py   → services/kakao_hospital_service.py → Kakao Local API HP8 (hospital search)
    │                          → services/kakao_service.py         → Kakao Maps API (geocoding)
    ├── routers/review.py     → services/naver_crawler.py          → Naver Place (httpx crawling for reviews)
    │                          → services/scoring_service.py       → keyword-based sentiment scoring
    └── routers/location.py   → services/kakao_service.py          → Kakao Maps Geocoding
```

- `services/hospital_service.py` — Operating status logic (open/upcoming/closed/unknown) + sorting
- `services/scoring_service.py` — Review scoring: positive keywords - negative keywords
- `templates/` — Jinja2 HTML (base layout + page templates)
- `static/` — CSS, JS

## Key Design Decisions

- **Jinja2 + Vanilla JS over SPA**: PRD requires single-server deployment; no build pipeline needed
- **Kakao Local API over HIRA**: 건강보험심사평가원 API switched to Kakao Local API (HP8 category) for better coordinate-based search
- **httpx over Playwright for crawling**: Naver Place reviews crawled via httpx (no headless browser needed on Render)
- **Keyword-based sentiment over Claude API**: Review scoring uses Korean keyword lists to avoid API costs; no credits required
- **SSL verify flag**: `_SSL_VERIFY = sys.platform != "win32"` — disables SSL only on Windows dev, enables on Linux (Render)
- **Frontend-first approach**: Build UI with mock data first → user review → then backend integration
- **Responsive**: Mobile (375px) / Tablet (768px) / PC (1440px)

## External APIs & Environment Variables

Managed via `.env` file (see `.env.example`):
- `ANTHROPIC_API_KEY` — Claude API for symptom→department chatbot
- `KAKAO_JS_API_KEY` — Kakao Maps JavaScript SDK (frontend map rendering)
- `KAKAO_MAP_API_KEY` — Kakao REST API (geocoding + hospital search)

## Testing

```bash
pytest -v                                          # 70 tests
pytest --cov=services --cov=routers --cov-report=term-missing  # with coverage
```

- `tests/test_scoring_service.py` — sentiment analysis, score calculation (22 cases)
- `tests/test_hospital_service.py` — operating status, sorting logic (22 cases)
- `tests/test_api.py` — FastAPI endpoint integration tests (17 cases + 3 page routes)

## Development Methodology

- Agile/Scrum, 5 sprints completed
- **Karpathy Guidelines**: Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution
- See `docs/PRD.md` for requirements and `docs/ROADMAP.md` for detailed phase plans

## Sprint Workflow Agents

This project uses Claude Code agents in `.claude/agents/`:
- `sprint-planner` — Creates sprint plans from ROADMAP.md
- `sprint-close` — Sprint completion (ROADMAP update, PR, code review, verification report)
- `code-reviewer` — Reviews completed work against plans
- `prd-to-roadmap` — Converts PRD to actionable roadmap
