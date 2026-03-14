# Sprint 2 — 병원 데이터 & 위치 백엔드 구현 계획

## ✅ 완료 기록 (2026-03-13)

| 항목 | 상태 | 비고 |
|------|------|------|
| 카카오 REST API 키 발급 | ✅ 완료 | KAKAO_MAP_API_KEY 환경 변수 설정 |
| 카카오 로컬 API 연동 | ✅ 완료 | kakao_hospital_service.py (HP8 카테고리 검색) |
| Geocoding 서비스 구현 | ✅ 완료 | kakao_service.py — 주소/키워드 → 좌표 |
| 반경 기반 병원 필터링 | ✅ 완료 | Haversine 공식 적용, 500m~10km |
| 운영 상태 판별 로직 | ✅ 완료 | hospital_service.py — open/upcoming/closed/unknown |
| 진료과 필터링 | ✅ 완료 | 카카오 카테고리명 파싱으로 진료과 추출 |
| 프론트엔드 API 연동 | ✅ 완료 | Mock 데이터 → 실제 API 응답으로 교체 |
| 병원 목록 API 엔드포인트 | ✅ 완료 | GET /api/hospitals |
| 위치 설정 API 엔드포인트 | ✅ 완료 | POST /api/geocode |

**주요 결정:** HIRA API → 카카오 로컬 API로 전환 (좌표 기반 반경 검색 직접 지원)
**완료 커밋:** `a32fc39`, `0aa1730`, `5a2cd92`

---

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 실제 공공 API 데이터(건강보험심사평가원 + 카카오맵)로 병원 목록을 조회하고, 위치(GPS/주소) + 진료과 + 반경 필터링이 동작하는 상태를 만든다.

**Architecture:** FastAPI 백엔드에 두 개의 서비스 레이어(kakao_service, hira_service)와 두 개의 라우터(location, hospital)를 추가한다. 프론트엔드의 Mock 데이터를 API 호출로 교체한다.

**Tech Stack:** FastAPI, httpx(비동기 HTTP), 건강보험심사평가원 API, 카카오맵 REST API(주소 검색 + 좌표→행정구역), Haversine 공식

---

## 스프린트 개요

| 항목 | 내용 |
|------|------|
| **스프린트 번호** | Sprint 2 |
| **브랜치** | `sprint2` |
| **기간** | 2026-03-27 ~ 2026-04-10 (2주) |
| **마일스톤** | M2: 병원 검색 실데이터 |
| **목표** | 실데이터로 병원 목록 조회 + 위치/진료과/반경 필터링 동작 |

---

## 사전 확인: .env 키 목록

Sprint 2에서 사용할 환경 변수:

```
KAKAO_JS_API_KEY   → 기존 Jinja2 템플릿에 전달 (카카오맵 JS SDK)
KAKAO_MAP_API_KEY  → 백엔드 Kakao REST API 호출용 (Authorization: KakaoAK <key>)
HIRA_API_KEY       → 건강보험심사평가원 API 서비스키 (URL 인코딩된 값)
```

> ⚠️ `.env` 파일에 `KAKO_JS_API_KEY`로 오타가 있을 수 있음. `main.py`의 변수명과 일치하는지 확인 필요.

---

## API 참고

### 카카오 주소 검색 API
```
GET https://dapi.kakao.com/v2/local/search/address.json?query={주소}
Header: Authorization: KakaoAK {REST_API_KEY}
응답: documents[0].x (경도), documents[0].y (위도)
```

### 카카오 좌표→행정구역 API
```
GET https://dapi.kakao.com/v2/local/geo/coord2regioncode.json?x={lng}&y={lat}
Header: Authorization: KakaoAK {REST_API_KEY}
응답: documents[1].region_2depth_name (시군구), documents[1].region_3depth_name (동)
```

### 건강보험심사평가원 요양기관 기본정보 조회 v2
```
GET http://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList
Params:
  ServiceKey={URL인코딩된 키}
  sidoCd={시도코드}        → ex) 11=서울
  sgguCd={시군구코드}      → ex) 11680=강남구
  dgsbjtCd={진료과목코드}  → ex) 01=내과, 13=이비인후과
  pageNo=1
  numOfRows=100
  _type=json
응답: response.body.items.item[] → yadmNm, addr, telno, XPos(경도), YPos(위도), clCdNm, dgsbjtCdNm
```

### 주요 진료과목 코드 (dgsbjtCd)
| 코드 | 진료과목 |
|------|----------|
| 01 | 내과 |
| 04 | 외과 |
| 05 | 정형외과 |
| 10 | 산부인과 |
| 11 | 소아청소년과 |
| 12 | 안과 |
| 13 | 이비인후과 |
| 14 | 피부과 |
| 15 | 비뇨의학과 |
| 16 | 재활의학과 |
| 17 | 가정의학과 |

### 시도 코드 (sidoCd)
| 코드 | 시도 |
|------|------|
| 11 | 서울 |
| 21 | 부산 |
| 22 | 대구 |
| 23 | 인천 |
| 24 | 광주 |
| 25 | 대전 |
| 26 | 울산 |
| 29 | 세종 |
| 31 | 경기 |
| 32 | 강원 |
| 33 | 충북 |
| 34 | 충남 |
| 35 | 전북 |
| 36 | 전남 |
| 37 | 경북 |
| 38 | 경남 |
| 39 | 제주 |

---

## Task 1: 환경 설정 정비

**Files:**
- Modify: `main.py`
- Modify: `.env.example`

**Step 1: main.py에 새 API 키 변수 추가**

현재 main.py의 `KAKAO_JS_API_KEY = os.getenv(...)` 아래에 추가:

```python
KAKAO_MAP_API_KEY = os.getenv("KAKAO_MAP_API_KEY", "")
HIRA_API_KEY = os.getenv("HIRA_API_KEY", "")
```

**Step 2: requirements.txt에 httpx 이미 있는지 확인**

Run: `grep httpx requirements.txt`
Expected: `httpx==0.27.0` (이미 포함됨 → 추가 불필요)

**Step 3: .env.example 업데이트**

```
KAKAO_JS_API_KEY=your_kakao_javascript_key
KAKAO_MAP_API_KEY=your_kakao_rest_api_key
HIRA_API_KEY=your_hira_service_key_url_encoded
```

**Step 4: 서버 재시작 확인**

Run: `uvicorn main:app --reload`
Expected: `Application startup complete.` (오류 없음)

**Step 5: Commit**

```bash
git add main.py .env.example
git commit -m "chore: Sprint 2 API 키 환경 변수 추가 (Kakao REST, HIRA)"
```

---

## Task 2: Kakao Geocoding 서비스

**Files:**
- Create: `services/kakao_service.py`
- Create: `routers/location.py`
- Modify: `main.py` (라우터 등록)

### Haversine 공식 (거리 계산)

두 좌표 간 직선 거리(미터):

```python
import math

def haversine(lat1, lng1, lat2, lng2) -> float:
    R = 6371000  # 지구 반지름 (미터)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
```

**Step 1: services/kakao_service.py 작성**

```python
# services/kakao_service.py
import httpx
import math
import os

KAKAO_MAP_API_KEY = os.getenv("KAKAO_MAP_API_KEY", "")
_HEADERS = {"Authorization": f"KakaoAK {KAKAO_MAP_API_KEY}"}


async def address_to_coords(address: str) -> dict | None:
    """주소 문자열 → {"lat": float, "lng": float} 또는 None"""
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=_HEADERS, params={"query": address})
        r.raise_for_status()
        docs = r.json().get("documents", [])
        if not docs:
            # 주소 검색 실패 시 키워드 검색 fallback
            return await keyword_to_coords(address)
        d = docs[0]
        return {"lat": float(d["y"]), "lng": float(d["x"])}


async def keyword_to_coords(keyword: str) -> dict | None:
    """키워드 검색 → 좌표 (주소 검색 fallback)"""
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=_HEADERS, params={"query": keyword})
        r.raise_for_status()
        docs = r.json().get("documents", [])
        if not docs:
            return None
        d = docs[0]
        return {"lat": float(d["y"]), "lng": float(d["x"])}


async def coords_to_region(lat: float, lng: float) -> dict:
    """좌표 → {"sido_cd": str, "sggu_cd": str, "sido_name": str, "sggu_name": str}"""
    url = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json"
    async with httpx.AsyncClient() as client:
        r = await client.get(url, headers=_HEADERS, params={"x": lng, "y": lat})
        r.raise_for_status()
        docs = r.json().get("documents", [])
        # documents[0] = 법정동, documents[1] = 행정동 (없을 수 있음)
        region = docs[0] if docs else {}
        sido_name = region.get("region_1depth_name", "")
        sggu_name = region.get("region_2depth_name", "")
        return {
            "sido_cd": _sido_name_to_code(sido_name),
            "sggu_cd": "",   # Sprint 2에서는 sido만 사용
            "sido_name": sido_name,
            "sggu_name": sggu_name,
        }


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """두 좌표 간 직선 거리 (미터)"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# 시도명 → 코드 매핑
_SIDO_MAP = {
    "서울": "11", "부산": "21", "대구": "22", "인천": "23",
    "광주": "24", "대전": "25", "울산": "26", "세종": "29",
    "경기": "31", "강원": "32", "충북": "33", "충남": "34",
    "전북": "35", "전남": "36", "경북": "37", "경남": "38", "제주": "39",
}

def _sido_name_to_code(name: str) -> str:
    for key, code in _SIDO_MAP.items():
        if key in name:
            return code
    return "11"  # 기본값: 서울
```

**Step 2: routers/location.py 작성**

```python
# routers/location.py
from fastapi import APIRouter
from pydantic import BaseModel
from services.kakao_service import address_to_coords

router = APIRouter(prefix="/api")


class GeocodeRequest(BaseModel):
    address: str


@router.post("/geocode")
async def geocode(body: GeocodeRequest):
    result = await address_to_coords(body.address)
    if not result:
        return {"error": "주소를 찾을 수 없습니다."}
    return result
```

**Step 3: main.py에 라우터 등록**

```python
from routers import location
app.include_router(location.router)
```

**Step 4: 수동 테스트**

```bash
curl -X POST http://localhost:8000/api/geocode \
  -H "Content-Type: application/json" \
  -d '{"address": "서울 강남구 역삼동"}'
```
Expected: `{"lat": 37.5..., "lng": 127.0...}`

**Step 5: Commit**

```bash
git add services/kakao_service.py routers/location.py main.py
git commit -m "feat: F-03 Kakao Geocoding 서비스 + /api/geocode 엔드포인트"
```

---

## Task 3: HIRA 병원 데이터 서비스

**Files:**
- Create: `services/hira_service.py`

**Step 1: services/hira_service.py 작성**

```python
# services/hira_service.py
import httpx
import os
from datetime import datetime

HIRA_API_KEY = os.getenv("HIRA_API_KEY", "")
BASE_URL = "http://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList"

# 진료과 이름 → dgsbjtCd 매핑
DEPT_CODE_MAP = {
    "내과": "01", "외과": "04", "정형외과": "05", "산부인과": "10",
    "소아청소년과": "11", "안과": "12", "이비인후과": "13", "피부과": "14",
    "비뇨의학과": "15", "재활의학과": "16", "가정의학과": "17",
    "신경과": "02", "정신건강의학과": "03", "신경외과": "06",
    "응급의학과": "18", "치과": "49",
}


async def get_hospitals(sido_cd: str, dept_name: str = "", page: int = 1, rows: int = 100) -> list[dict]:
    """
    심평원 API로 병원 목록 조회.
    반환: [{"id", "name", "address", "phone", "lat", "lng", "departments", "hours", ...}, ...]
    """
    params = {
        "ServiceKey": HIRA_API_KEY,
        "sidoCd": sido_cd,
        "pageNo": page,
        "numOfRows": rows,
        "_type": "json",
    }
    if dept_name and dept_name in DEPT_CODE_MAP:
        params["dgsbjtCd"] = DEPT_CODE_MAP[dept_name]

    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(BASE_URL, params=params)
        r.raise_for_status()

    body = r.json().get("response", {}).get("body", {})
    items = body.get("items", {})
    if not items:
        return []

    raw = items.get("item", [])
    if isinstance(raw, dict):   # 결과가 1건일 때 dict로 옴
        raw = [raw]

    return [_parse_item(item) for item in raw if item.get("XPos") and item.get("YPos")]


def _parse_item(item: dict) -> dict:
    """HIRA API 응답 1건 → 표준 병원 dict"""
    # 진료과목 파싱 (dgsbjtCdNm: "내과,외과" 또는 단일)
    depts_raw = item.get("dgsbjtCdNm", "") or ""
    departments = [d.strip() for d in depts_raw.split(",") if d.strip()] or ["일반의"]

    # 운영시간: 심평원 API는 요일별 시간을 별도 필드로 제공하지 않음
    # Sprint 2에서는 빈 dict 반환 → Sprint 3에서 보완
    hours = _parse_hours(item)

    return {
        "id": item.get("ykiho", ""),          # 요양기관기호
        "name": item.get("yadmNm", ""),
        "address": item.get("addr", ""),
        "phone": item.get("telno", ""),
        "lat": float(item.get("YPos", 0)),     # YPos = 위도
        "lng": float(item.get("XPos", 0)),     # XPos = 경도
        "departments": departments,
        "hours": hours,
        "clCdNm": item.get("clCdNm", ""),      # 종별명 (의원, 병원 등)
    }


def _parse_hours(item: dict) -> dict:
    """
    심평원 API의 요일별 운영시간 필드 파싱.
    필드명: trmtMonStart/End, trmtTueStart/End, ..., trmtSunStart/End
    형식: "0900" → "09:00"
    """
    day_map = {
        "mon": ("trmtMonStart", "trmtMonEnd"),
        "tue": ("trmtTueStart", "trmtTueEnd"),
        "wed": ("trmtWedStart", "trmtWedEnd"),
        "thu": ("trmtThuStart", "trmtThuEnd"),
        "fri": ("trmtFriStart", "trmtFriEnd"),
        "sat": ("trmtSatStart", "trmtSatEnd"),
        "sun": ("trmtSunStart", "trmtSunEnd"),
    }
    hours = {}
    for day, (start_key, end_key) in day_map.items():
        start = item.get(start_key, "")
        end = item.get(end_key, "")
        if start and end and start != "0000":
            hours[day] = f"{_fmt_time(start)}-{_fmt_time(end)}"
        else:
            hours[day] = "휴무"
    return hours


def _fmt_time(t: str) -> str:
    """'0900' → '09:00'"""
    t = str(t).zfill(4)
    return f"{t[:2]}:{t[2:]}"
```

**Step 2: 단독 테스트 (Python REPL)**

```bash
cd /경로/git
python -c "
import asyncio, os
from dotenv import load_dotenv
load_dotenv()
from services.hira_service import get_hospitals
hospitals = asyncio.run(get_hospitals('11', '내과'))
print(len(hospitals), 'hospitals')
if hospitals: print(hospitals[0])
"
```
Expected: 병원 수 > 0, 첫 번째 병원 dict 출력

**Step 3: Commit**

```bash
git add services/hira_service.py
git commit -m "feat: F-04 심평원 HIRA API 연동 서비스 (병원 목록 + 운영시간 파싱)"
```

---

## Task 4: 운영 상태 판별 서비스

**Files:**
- Create: `services/hospital_service.py`

**Step 1: services/hospital_service.py 작성**

```python
# services/hospital_service.py
from datetime import datetime
from services.kakao_service import haversine

DAY_KEYS = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"]


def get_status(hours: dict) -> tuple[str, str]:
    """
    운영시간 dict → (status, statusText)
    status: "open" | "upcoming" | "closed"
    statusText: "진료 중 · 21:00 마감" | "09:00 진료시작" | "오늘 휴무"
    """
    now = datetime.now()
    today_key = DAY_KEYS[now.weekday() + 1 if now.weekday() < 6 else 0]
    # Python weekday(): 0=Mon ... 6=Sun → 변환
    py_to_day = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}
    today_key = py_to_day[now.weekday()]

    today_hours = hours.get(today_key, "휴무")

    if today_hours == "휴무" or not today_hours:
        return "closed", "오늘 휴무"

    try:
        start_str, end_str = today_hours.split("-")
        start = _parse_time(start_str, now)
        end = _parse_time(end_str, now)
    except (ValueError, AttributeError):
        return "closed", "오늘 휴무"

    current_minutes = now.hour * 60 + now.minute
    start_minutes = start.hour * 60 + start.minute
    end_minutes = end.hour * 60 + end.minute

    if start_minutes <= current_minutes < end_minutes:
        return "open", f"진료 중 · {end_str} 마감"
    elif current_minutes < start_minutes:
        return "upcoming", f"{start_str} 진료시작"
    else:
        return "closed", "오늘 휴무"


def _parse_time(time_str: str, ref: datetime) -> datetime:
    h, m = map(int, time_str.strip().split(":"))
    return ref.replace(hour=h, minute=m, second=0, microsecond=0)


def enrich_hospitals(hospitals: list[dict], user_lat: float, user_lng: float, radius: int) -> list[dict]:
    """
    병원 목록에 거리 + 운영 상태 추가, 반경 필터링 후 정렬.
    정렬: open > upcoming > closed, 동순위는 거리순
    """
    STATUS_ORDER = {"open": 0, "upcoming": 1, "closed": 2}
    result = []
    for h in hospitals:
        dist = haversine(user_lat, user_lng, h["lat"], h["lng"])
        if dist > radius:
            continue
        status, status_text = get_status(h["hours"])
        result.append({
            **h,
            "distance": round(dist),
            "status": status,
            "statusText": status_text,
            "score": 0,          # Sprint 4에서 리뷰 점수로 교체
            "reviewSummary": "", # Sprint 4에서 채움
        })

    result.sort(key=lambda x: (STATUS_ORDER[x["status"]], x["distance"]))
    return result
```

**Step 2: 단독 테스트**

```bash
python -c "
from services.hospital_service import get_status
# 현재 시간에 따라 결과 달라짐
print(get_status({'mon':'09:00-18:00','tue':'09:00-18:00','wed':'09:00-18:00','thu':'09:00-18:00','fri':'09:00-18:00','sat':'09:00-13:00','sun':'휴무'}))
"
```
Expected: 현재 요일/시간에 따라 ('open', '진료 중 · 18:00 마감') 또는 ('upcoming', '09:00 진료시작') 또는 ('closed', '오늘 휴무')

**Step 3: Commit**

```bash
git add services/hospital_service.py
git commit -m "feat: 운영 상태 판별 + Haversine 반경 필터 + 정렬 로직"
```

---

## Task 5: 병원 목록 API 엔드포인트

**Files:**
- Create: `routers/hospital.py`
- Modify: `main.py`

**Step 1: routers/hospital.py 작성**

```python
# routers/hospital.py
from fastapi import APIRouter, Query
from services.kakao_service import coords_to_region
from services.hira_service import get_hospitals
from services.hospital_service import enrich_hospitals

router = APIRouter(prefix="/api")


@router.get("/hospitals")
async def hospitals(
    lat: float = Query(..., description="위도"),
    lng: float = Query(..., description="경도"),
    radius: int = Query(500, description="반경 (미터)"),
    department: str = Query("", description="진료과 (예: 내과)"),
    sort: str = Query("score", description="정렬 기준: score | distance"),
):
    # 1. 좌표 → 시도코드
    region = await coords_to_region(lat, lng)
    sido_cd = region["sido_cd"]

    # 2. 심평원 API 조회
    raw_hospitals = await get_hospitals(sido_cd, dept_name=department)

    # 3. 반경 필터 + 운영 상태 추가 + 기본 정렬 (open>upcoming>closed, 거리순)
    enriched = enrich_hospitals(raw_hospitals, lat, lng, radius)

    # 4. 추가 정렬 (score 요청 시 — Sprint 4 전까지는 distance와 동일)
    if sort == "distance":
        enriched.sort(key=lambda x: x["distance"])

    return {"hospitals": enriched, "total": len(enriched)}
```

**Step 2: main.py에 hospital 라우터 등록**

`from routers import location` 아래에:

```python
from routers import location, hospital
app.include_router(location.router)
app.include_router(hospital.router)
```

**Step 3: 수동 테스트 (서버 실행 후)**

```bash
curl "http://localhost:8000/api/hospitals?lat=37.5665&lng=126.9780&radius=1000&department=내과"
```
Expected: `{"hospitals": [...], "total": N}` (N ≥ 0)

**Step 4: Commit**

```bash
git add routers/hospital.py main.py
git commit -m "feat: GET /api/hospitals 엔드포인트 (좌표+반경+진료과 필터)"
```

---

## Task 6: 프론트엔드 → 백엔드 API 연동

**Files:**
- Modify: `static/js/hospital_list.js`
- Modify: `static/js/location.js`

> 목표: Mock 데이터 의존을 제거하고, 실제 `/api/hospitals` 와 `/api/geocode` 를 호출한다.

**Step 1: static/js/location.js의 confirmAddress() 함수 수정**

기존 (Mock 좌표 반환):
```js
// Phase 1 Mock: 서울 시청 좌표 반환
function confirmAddress() { ... window.LocationState.lat = 37.5665 ... }
```

변경 후:
```js
async function confirmAddress() {
  const address = document.getElementById('addressInput').value.trim();
  if (!address) return;

  try {
    const res = await fetch('/api/geocode', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ address }),
    });
    const data = await res.json();
    if (data.error || !data.lat) {
      alert('주소를 찾을 수 없습니다. 다시 입력해 주세요.');
      return;
    }
    window.LocationState.lat = data.lat;
    window.LocationState.lng = data.lng;
    window.LocationState.label = address;
    document.getElementById('locationBarText').textContent = address;
    closeLocationModal();
    if (typeof window.onLocationSet === 'function') window.onLocationSet();
  } catch (e) {
    alert('위치 설정 중 오류가 발생했습니다.');
  }
}
```

**Step 2: static/js/hospital_list.js의 loadHospitals() 함수 수정**

기존 (MOCK_HOSPITALS 사용):
```js
function loadHospitals() {
  let list = window.MOCK_HOSPITALS.filter(...);
  ...
}
```

변경 후:
```js
async function loadHospitals() {
  const { lat, lng } = window.LocationState;
  if (!lat || !lng) return;

  const params = new URLSearchParams({
    lat, lng,
    radius: currentRadius,
    department: SELECTED_DEPARTMENT,
    sort: currentSort,
  });

  try {
    const res = await fetch(`/api/hospitals?${params}`);
    const data = await res.json();
    renderHospitalList(data.hospitals);
    updateMap(data.hospitals);
    document.getElementById('listSummary').textContent =
      `${data.total}개 병원`;
  } catch (e) {
    document.getElementById('hospitalList').innerHTML =
      '<div style="padding:16px;color:var(--color-text-sub);">병원 정보를 불러오는 중 오류가 발생했습니다.</div>';
  }
}
```

> `renderHospitalList`와 `updateMap`은 현재 hospital_list.js의 기존 렌더링 함수를 재사용.
> 데이터 구조가 Mock과 동일(name, address, status, statusText, distance, departments, score, reviewSummary)하므로 렌더링 코드 수정 불필요.

**Step 3: 반경/정렬 변경 이벤트가 loadHospitals() 재호출하는지 확인**

현재 hospital_list.js의 `setRadius()`, `setSort()` 함수가 `loadHospitals()`를 호출하는지 확인.
아직 안 한다면 각 함수 끝에 `loadHospitals();` 추가.

**Step 4: 브라우저 테스트**

1. `http://localhost:8000/hospitals` 접속
2. GPS 허용 또는 주소 입력 ("서울 강남구 역삼동")
3. 병원 목록 카드가 실데이터로 표시되는지 확인
4. 반경 변경 시 목록 갱신 확인

**Step 5: Commit**

```bash
git add static/js/location.js static/js/hospital_list.js
git commit -m "feat: 프론트엔드 Mock 데이터 → 실API 연동 (geocode + hospitals)"
```

---

## Task 7: 병원 상세 페이지 실데이터 연동

**Files:**
- Create: `routers/hospital.py` (상세 엔드포인트 추가)
- Modify: `static/js/hospital_detail.js`

**Step 1: GET /api/hospitals/{hospital_id} 엔드포인트 추가**

`routers/hospital.py`의 기존 내용 아래에 추가:

```python
from services.hira_service import get_hospital_detail

@router.get("/hospitals/{hospital_id}")
async def hospital_detail(hospital_id: str):
    detail = await get_hospital_detail(hospital_id)
    if not detail:
        return {"error": "병원 정보를 찾을 수 없습니다."}
    return detail
```

**Step 2: hira_service.py에 get_hospital_detail() 추가**

```python
async def get_hospital_detail(ykiho: str) -> dict | None:
    """요양기관기호로 단일 병원 상세 조회"""
    params = {
        "ServiceKey": HIRA_API_KEY,
        "ykiho": ykiho,
        "_type": "json",
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(BASE_URL, params=params)
        r.raise_for_status()
    body = r.json().get("response", {}).get("body", {})
    items = body.get("items", {})
    if not items:
        return None
    raw = items.get("item", {})
    if isinstance(raw, list):
        raw = raw[0]
    return _parse_item(raw)
```

**Step 3: hospital_detail.js 수정**

`DOMContentLoaded` 이벤트 핸들러에서 MOCK_HOSPITALS 대신 API 호출:

```js
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const res = await fetch(`/api/hospitals/${HOSPITAL_ID}`);
    const hospital = await res.json();
    if (hospital.error) {
      document.getElementById('detailContent').innerHTML =
        '<div style="color:var(--color-closed);">병원 정보를 찾을 수 없습니다.</div>';
      return;
    }
    // status 추가 (API에서 미포함 시 기본값)
    if (!hospital.status) {
      hospital.status = 'closed';
      hospital.statusText = '운영시간 정보 없음';
    }
    renderDetail(hospital);
    if (KAKAO_JS_API_KEY) initDetailMap(hospital);
  } catch (e) {
    document.getElementById('detailContent').innerHTML =
      '<div style="color:var(--color-closed);">정보를 불러오는 중 오류가 발생했습니다.</div>';
  }
});
```

> Note: 병원 목록에서 상세로 이동 시 URL은 `/hospitals/{ykiho}` (요양기관기호). hospital_list.js의 카드 클릭 URL을 `h.id`로 생성하도록 확인.

**Step 4: Commit**

```bash
git add routers/hospital.py services/hira_service.py static/js/hospital_detail.js
git commit -m "feat: 병원 상세 실API 연동 (GET /api/hospitals/{id})"
```

---

## Task 8: Sprint 2 최종 점검 및 push

**Step 1: 전체 플로우 브라우저 테스트**

```
1. http://localhost:8000 → 메인 페이지 정상
2. "진료과로 찾기" → 내과 선택 → 병원 목록 표시 확인 (실데이터)
3. 주소 "서울 강남구 역삼동" 입력 → 위치 설정 후 병원 목록 갱신 확인
4. 반경 500m → 1km → 10km 변경 시 결과 수 변화 확인
5. 병원 카드 클릭 → 상세 페이지 실데이터 표시 확인
6. 운영 상태 3종 (진료 중/진료시작/오늘 휴무) 중 현재 시간에 맞는 상태 표시 확인
```

**Step 2: 에러 케이스 확인**

```
1. HIRA API 응답 없는 지역 → 빈 목록 표시 (앱 크래시 없음)
2. Kakao Geocoding 실패 → "주소를 찾을 수 없습니다." 알림
```

**Step 3: git push**

```bash
git push origin sprint2
```

**Step 4: Playwright 검증 시나리오 (ROADMAP Phase 2)**

```
1. 접속 → GPS 허용 → 현재 위치 주변 병원 실데이터 표시
2. 진료과 "내과" 선택 → 내과 병원만 표시
3. 반경 500m → 10km 변경 → 결과 수 증가
4. 주소 "서울 강남구 역삼동" 입력 → 해당 위치 병원 표시
5. 운영 상태 텍스트 3종 형식 확인
6. 병원 카드 클릭 → 상세 정보 실데이터 표시
7. 지도 위 병원 핀 마커 위치 확인
```

---

## ✅ Sprint 2 완료 기준

- [ ] `GET /api/hospitals` — 실데이터 병원 목록 반환
- [ ] `POST /api/geocode` — 주소 → 좌표 변환
- [ ] `GET /api/hospitals/{id}` — 병원 상세 실데이터
- [ ] 위치(GPS/주소) + 진료과 + 반경 필터링 정상 동작
- [ ] 운영 상태 (open/upcoming/closed) 현재 시간 기준 정확히 표시
- [ ] 프론트엔드 Mock 데이터 의존 제거
- [ ] `git push origin sprint2` 완료
