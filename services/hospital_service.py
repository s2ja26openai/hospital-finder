# services/hospital_service.py
from datetime import datetime

_PY_TO_DAY = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}
_STATUS_ORDER = {"open": 0, "upcoming": 1, "closed": 2, "unknown": 3}


def get_status(hours: dict) -> tuple[str, str]:
    """
    운영시간 dict → (status, statusText)
    status: "open" | "upcoming" | "closed"
    statusText: "진료 중 · 21:00 마감" | "09:00 진료시작" | "오늘 휴무"
    """
    now = datetime.now()
    today_key = _PY_TO_DAY[now.weekday()]
    today_hours = hours.get(today_key, "휴무")

    if not hours:
        return "unknown", "운영시간 정보 없음"
    if not today_hours or today_hours == "휴무":
        return "closed", "오늘 휴무"

    try:
        start_str, end_str = today_hours.split("-")
        sh, sm = map(int, start_str.strip().split(":"))
        eh, em = map(int, end_str.strip().split(":"))
    except (ValueError, AttributeError):
        return "closed", "오늘 휴무"

    current = now.hour * 60 + now.minute
    start = sh * 60 + sm
    end = eh * 60 + em

    if start <= current < end:
        return "open", f"진료 중 · {end_str.strip()} 마감"
    elif current < start:
        return "upcoming", f"{start_str.strip()} 진료시작"
    else:
        return "closed", "오늘 휴무"


def enrich_hospitals(hospitals: list[dict]) -> list[dict]:
    """병원 목록에 운영 상태 추가 후 정렬 (open > upcoming > closed > unknown, 거리순)."""
    result = []
    for h in hospitals:
        status, status_text = get_status(h.get("hours", {}))
        result.append({
            **h,
            "status": status,
            "statusText": status_text,
            "score": 0,
            "reviewSummary": "",
        })
    result.sort(key=lambda x: (_STATUS_ORDER[x["status"]], x.get("distance", 0)))
    return result
