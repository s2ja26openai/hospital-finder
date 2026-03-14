# services/hira_service.py
import httpx
import os

HIRA_API_KEY = os.getenv("HIRA_API_KEY", "")
BASE_URL = "http://apis.data.go.kr/B551182/hospInfoServicev2/getHospBasisList"

DEPT_CODE_MAP = {
    "내과": "01", "신경과": "02", "정신건강의학과": "03", "외과": "04",
    "정형외과": "05", "신경외과": "06", "흉부외과": "07", "성형외과": "08",
    "산부인과": "10", "소아청소년과": "11", "안과": "12", "이비인후과": "13",
    "피부과": "14", "비뇨의학과": "15", "재활의학과": "16", "가정의학과": "17",
    "응급의학과": "18", "치과": "49",
}


async def get_hospitals(sido_cd: str, dept_name: str = "", page: int = 1, rows: int = 100) -> list[dict]:
    """심평원 API로 병원 목록 조회."""
    params = {
        "ServiceKey": HIRA_API_KEY,
        "sidoCd": sido_cd,
        "pageNo": page,
        "numOfRows": rows,
        "_type": "json",
    }
    if dept_name and dept_name in DEPT_CODE_MAP:
        params["dgsbjtCd"] = DEPT_CODE_MAP[dept_name]

    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
        r = await client.get(BASE_URL, params=params)
        r.raise_for_status()

    body = r.json().get("response", {}).get("body", {})
    items = body.get("items", {})
    if not items:
        return []

    raw = items.get("item", [])
    if isinstance(raw, dict):
        raw = [raw]

    return [_parse_item(item) for item in raw if item.get("XPos") and item.get("YPos")]


async def get_hospital_detail(ykiho: str) -> dict | None:
    """요양기관기호로 단일 병원 상세 조회"""
    params = {
        "ServiceKey": HIRA_API_KEY,
        "ykiho": ykiho,
        "_type": "json",
    }
    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
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


def _parse_item(item: dict) -> dict:
    depts_raw = item.get("dgsbjtCdNm", "") or ""
    departments = [d.strip() for d in depts_raw.split(",") if d.strip()] or ["일반의"]
    hours = _parse_hours(item)
    return {
        "id": item.get("ykiho", ""),
        "name": item.get("yadmNm", ""),
        "address": item.get("addr", ""),
        "phone": item.get("telno", ""),
        "lat": float(item.get("YPos", 0)),
        "lng": float(item.get("XPos", 0)),
        "departments": departments,
        "hours": hours,
        "clCdNm": item.get("clCdNm", ""),
    }


def _parse_hours(item: dict) -> dict:
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
        if start and end and str(start) != "0000":
            hours[day] = f"{_fmt_time(start)}-{_fmt_time(end)}"
        else:
            hours[day] = "휴무"
    return hours


def _fmt_time(t) -> str:
    t = str(t).zfill(4)
    return f"{t[:2]}:{t[2:]}"
