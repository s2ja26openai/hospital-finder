# 내 주변 병원 찾기

[![CI](https://github.com/s2ja26openai/hospital-finder/actions/workflows/ci.yml/badge.svg)](https://github.com/s2ja26openai/hospital-finder/actions/workflows/ci.yml)

증상 또는 진료과 기준으로 현재 위치 기반 최적 병원을 추천하는 웹 서비스.

---

## 주요 기능

| 기능 | 설명 |
|------|------|
| 증상 기반 챗봇 | 자연어 증상 입력 → 진료과 추천 (Claude API) |
| 진료과 직접 선택 | 드롭다운으로 진료과 선택 후 병원 탐색 |
| 위치 기반 병원 검색 | GPS 또는 주소 입력 → 반경 500m~10km 내 병원 조회 (Kakao API) |
| 운영 상태 실시간 표시 | 진료 중 / 진료시작 예정 / 오늘 휴무 구분 |
| 리뷰 기반 평점 정렬 | 네이버 리뷰 수집 + 키워드 감성 분석으로 평점 산출 |

---

## 기술 스택

| 영역 | 기술 |
|------|------|
| Backend | Python 3.11 + FastAPI + Jinja2 |
| Frontend | Vanilla JS + Kakao Maps SDK |
| AI | Claude API (Anthropic) |
| 병원 데이터 | Kakao Local API (카테고리 HP8) |
| 리뷰 데이터 | Naver Place 크롤링 (httpx) |
| 배포 | Render |

---

## 빠른 시작

```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 개발 서버 실행
uvicorn main:app --reload
# → http://localhost:8000
```

---

## 테스트

```bash
# 테스트 의존성 설치
pip install -r requirements-dev.txt

# 전체 테스트 실행
pytest -v

# 커버리지 포함
pytest --cov=services --cov=routers --cov-report=term-missing
```

**테스트 구성:**

| 파일 | 대상 | 테스트 수 |
|------|------|-----------|
| `tests/test_scoring_service.py` | 감성 분석, 평점 산출 | 22개 |
| `tests/test_hospital_service.py` | 운영 상태 판별, 병원 정렬 | 22개 |
| `tests/test_api.py` | FastAPI 엔드포인트 통합 테스트 | 17개 |

---

## 환경 변수

| 변수명 | 설명 |
|--------|------|
| `KAKAO_JS_API_KEY` | 카카오맵 JavaScript SDK 키 |
| `KAKAO_MAP_API_KEY` | 카카오 REST API 키 (Geocoding, 병원 검색) |
| `ANTHROPIC_API_KEY` | Claude API 키 (증상 분석) |

---

## 프로젝트 문서

- [PRD (요구사항 정의서)](docs/PRD.md)
- [ROADMAP (개발 로드맵)](docs/ROADMAP.md)
- [CLAUDE.md (AI 컨텍스트)](CLAUDE.md)

---

## 배포

Render 배포 설정은 `render.yaml` 참조.

```bash
# Render 자동 배포 (main 브랜치 push 시)
git push origin main
```
