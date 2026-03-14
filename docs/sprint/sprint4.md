# Sprint 4 — 리뷰 분석 & 평점 정렬 구현 계획

**Goal:** 네이버 리뷰 수집, 키워드 기반 감성 분석, 평점 산출 기반 정렬을 완성한다.

**Architecture:** 네이버 Place 내부 API로 리뷰 수집 → 키워드 기반 감성 분석(Claude API 불필요) → 긍정-부정 점수 산출 → 캐싱

**Tech Stack:** httpx (네이버 크롤링), 키워드 감성 분석, 서버 메모리 캐시

---

## Task 1: 네이버 리뷰 크롤러 구현

**Files:** Create `services/naver_crawler.py`

- 네이버 Place 검색 API로 병원 Place ID 획득
- Place ID로 리뷰 최신순 최대 50개 수집
- httpx 기반 (Playwright 불필요)

## Task 2: 감성 분석 + 평점 산출

**Files:** Create `services/scoring_service.py`

- 한국어 긍정/부정 키워드 사전 기반 감성 분석
- 점수 = 긍정 리뷰 수 - 부정 리뷰 수
- 리뷰 10개 미만: 신뢰도 낮음 표시

## Task 3: 리뷰 API + 병원 서비스 연동

**Files:** Create `routers/review.py`, Modify `services/hospital_service.py`, `routers/hospital.py`

- GET /api/reviews/{hospital_name} — 리뷰 + 점수 반환
- 병원 목록 API에서 리뷰 점수 포함하여 평점순 정렬

## Task 4: 프론트엔드 연동

**Files:** Modify `static/js/hospital_list.js`, `static/css/hospital_list.css`

- 병원 카드에 리뷰 요약 표시 (긍정/부정 포인트)
- 신뢰도 낮음 뱃지
- 평점순 정렬 실제 동작

## ✅ Sprint 4 완료 기준

- [ ] 네이버 리뷰 크롤링 (최대 50개/병원)
- [ ] 키워드 기반 감성 분석 및 평점 산출
- [ ] 평점순 정렬 동작
- [ ] 리뷰 10개 미만 신뢰도 낮음 표시
- [ ] 리뷰 캐싱 동작
