# services/kakao_service.py
import httpx
import math
import os

KAKAO_MAP_API_KEY = os.getenv("KAKAO_MAP_API_KEY", "")


def _headers() -> dict:
    return {"Authorization": f"KakaoAK {KAKAO_MAP_API_KEY}"}


async def address_to_coords(address: str) -> dict | None:
    """주소 문자열 → {"lat": float, "lng": float} 또는 None"""
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.get(url, headers=_headers(), params={"query": address})
        r.raise_for_status()
        docs = r.json().get("documents", [])
        if not docs:
            return await keyword_to_coords(address)
        d = docs[0]
        return {"lat": float(d["y"]), "lng": float(d["x"])}


async def keyword_to_coords(keyword: str) -> dict | None:
    """키워드 검색 → 좌표 (주소 검색 fallback)"""
    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.get(url, headers=_headers(), params={"query": keyword})
        r.raise_for_status()
        docs = r.json().get("documents", [])
        if not docs:
            return None
        d = docs[0]
        return {"lat": float(d["y"]), "lng": float(d["x"])}


async def coords_to_region(lat: float, lng: float) -> dict:
    """좌표 → {"sido_cd": str, "sido_name": str, "sggu_name": str}"""
    url = "https://dapi.kakao.com/v2/local/geo/coord2regioncode.json"
    async with httpx.AsyncClient(verify=False) as client:
        r = await client.get(url, headers=_headers(), params={"x": lng, "y": lat})
        r.raise_for_status()
        docs = r.json().get("documents", [])
        region = docs[0] if docs else {}
        sido_name = region.get("region_1depth_name", "")
        sggu_name = region.get("region_2depth_name", "")
        return {
            "sido_cd": _sido_name_to_code(sido_name),
            "sido_name": sido_name,
            "sggu_name": sggu_name,
        }


def haversine(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """두 좌표 간 직선 거리 (미터)"""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


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
