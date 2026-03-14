# services/naver_crawler.py
"""네이버 Place 리뷰 크롤러 — httpx 기반 (Playwright 불필요)."""
import httpx
import time

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Referer": "https://map.naver.com/",
}

# 서버 메모리 캐시 — {hospital_name: {"reviews": [...], "ts": float}}
_cache: dict[str, dict] = {}
_CACHE_TTL = 3600  # 1시간


async def search_place_id(hospital_name: str) -> str | None:
    """네이버 Place에서 병원 이름으로 검색하여 Place ID 반환."""
    url = "https://map.naver.com/p/api/search/allSearch"
    params = {"query": hospital_name, "type": "place", "searchCoord": "", "boundary": ""}
    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            resp = await client.get(url, params=params, headers=_HEADERS)
            resp.raise_for_status()
            data = resp.json()
            places = data.get("result", {}).get("place", {}).get("list", [])
            if places:
                return places[0].get("id")
    except Exception:
        pass
    return None


async def fetch_reviews(place_id: str, max_count: int = 50) -> list[str]:
    """네이버 Place ID로 리뷰 텍스트 목록 수집 (최신순, 최대 max_count개)."""
    reviews = []
    page = 1
    size = 50
    url = f"https://m.place.naver.com/rest/place/{place_id}/review/ugc"
    try:
        async with httpx.AsyncClient(verify=False, timeout=10) as client:
            while len(reviews) < max_count:
                params = {"page": page, "size": size, "sort": "recent"}
                resp = await client.get(url, params=params, headers=_HEADERS)
                if resp.status_code != 200:
                    break
                data = resp.json()
                items = data.get("reviews", [])
                if not items:
                    break
                for item in items:
                    text = item.get("body", "").strip()
                    if text:
                        reviews.append(text)
                    if len(reviews) >= max_count:
                        break
                if data.get("isLastPage", True):
                    break
                page += 1
    except Exception:
        pass
    return reviews


async def get_reviews(hospital_name: str) -> list[str]:
    """병원명으로 리뷰 수집 (캐시 적용)."""
    now = time.time()
    cached = _cache.get(hospital_name)
    if cached and now - cached["ts"] < _CACHE_TTL:
        return cached["reviews"]

    place_id = await search_place_id(hospital_name)
    if not place_id:
        return []

    reviews = await fetch_reviews(place_id)
    _cache[hospital_name] = {"reviews": reviews, "ts": now}
    return reviews
