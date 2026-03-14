# services/kakao_hospital_service.py
# 카카오 로컬 API 기반 병원 검색 (HIRA 대체)
import httpx
import os
import sys

KAKAO_MAP_API_KEY = os.getenv("KAKAO_MAP_API_KEY", "")
CATEGORY_URL = "https://dapi.kakao.com/v2/local/search/category.json"

_SSL_VERIFY = sys.platform != "win32"
KEYWORD_URL  = "https://dapi.kakao.com/v2/local/search/keyword.json"


def _headers() -> dict:
    return {"Authorization": f"KakaoAK {KAKAO_MAP_API_KEY}"}


async def search_hospitals(lat: float, lng: float, radius: int, department: str = "") -> list[dict]:
    """
    카카오 로컬 API로 근처 병원 검색.
    - department 없음: 카테고리 검색 (HP8=병원)
    - department 있음: 키워드 검색 "{department} 병원"
    반환: [{"id", "name", "address", "phone", "lat", "lng", "departments", "distance", "hours"}, ...]
    """
    if department:
        return await _keyword_search(lat, lng, radius, department)
    return await _category_search(lat, lng, radius)


async def _category_search(lat: float, lng: float, radius: int) -> list[dict]:
    """카테고리 HP8(병원) 반경 검색 — 최대 45개 × 3페이지"""
    results = []
    async with httpx.AsyncClient(verify=_SSL_VERIFY) as client:
        for page in range(1, 4):
            params = {
                "category_group_code": "HP8",
                "x": lng,
                "y": lat,
                "radius": min(radius, 20000),
                "page": page,
                "size": 15,
                "sort": "distance",
            }
            r = await client.get(CATEGORY_URL, headers=_headers(), params=params)
            r.raise_for_status()
            data = r.json()
            docs = data.get("documents", [])
            results.extend([_parse_doc(d) for d in docs])
            if data.get("meta", {}).get("is_end", True):
                break
    return results


async def _keyword_search(lat: float, lng: float, radius: int, department: str) -> list[dict]:
    """키워드 "{진료과}" 반경 검색"""
    results = []
    async with httpx.AsyncClient(verify=_SSL_VERIFY) as client:
        for page in range(1, 4):
            params = {
                "query": department,
                "category_group_code": "HP8",
                "x": lng,
                "y": lat,
                "radius": min(radius, 20000),
                "page": page,
                "size": 15,
                "sort": "distance",
            }
            r = await client.get(KEYWORD_URL, headers=_headers(), params=params)
            r.raise_for_status()
            data = r.json()
            docs = data.get("documents", [])
            results.extend([_parse_doc(d) for d in docs])
            if data.get("meta", {}).get("is_end", True):
                break
    return results


def _parse_doc(doc: dict) -> dict:
    """카카오 로컬 응답 1건 → 표준 병원 dict"""
    # category_name 예: "의료,건강 > 병원 > 내과의원"
    category = doc.get("category_name", "")
    dept = _parse_dept(category)
    dist = int(doc.get("distance", 0) or 0)

    return {
        "id":          doc.get("id", ""),
        "name":        doc.get("place_name", ""),
        "address":     doc.get("road_address_name") or doc.get("address_name", ""),
        "phone":       doc.get("phone", ""),
        "lat":         float(doc.get("y", 0)),
        "lng":         float(doc.get("x", 0)),
        "departments": dept,
        "distance":    dist,
        "hours":       {},   # 카카오 로컬 API는 운영시간 미제공 → Sprint 3에서 보완
    }


def _parse_dept(category_name: str) -> list[str]:
    """
    "의료,건강 > 병원 > 내과의원" → ["내과"]
    "의료,건강 > 병원"           → ["일반의"]
    """
    if not category_name:
        return ["일반의"]
    parts = [p.strip() for p in category_name.split(">")]
    if len(parts) >= 3:
        leaf = parts[-1]
        # "내과의원" → "내과", "이비인후과의원" → "이비인후과" 등
        leaf = leaf.replace("의원", "").replace("병원", "").strip()
        if leaf:
            return [leaf]
    return ["일반의"]
