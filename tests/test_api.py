"""FastAPI 통합 테스트 — httpx.AsyncClient 사용"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from main import app


@pytest.fixture
def mock_hospitals():
    return [
        {
            "id": "1", "name": "강남내과의원", "address": "서울 강남구 역삼동 1-1",
            "phone": "02-1234-5678", "lat": 37.5005, "lng": 127.0365,
            "departments": ["내과"], "distance": 250, "hours": {},
            "status": "unknown", "statusText": "운영시간 정보 없음",
            "score": 0, "reviewSummary": "", "reviewCount": 0, "reliable": False,
        }
    ]


@pytest.mark.asyncio
async def test_index_page():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_hospitals_page():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/hospitals")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_chatbot_page():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/chatbot")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_hospitals_api_requires_lat_lng():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/hospitals")
    assert resp.status_code == 422  # 필수 파라미터 누락


@pytest.mark.asyncio
async def test_hospitals_api_returns_list(mock_hospitals):
    with patch("routers.hospital.search_hospitals", new_callable=AsyncMock) as mock_search, \
         patch("routers.hospital.get_reviews", new_callable=AsyncMock) as mock_reviews:
        mock_search.return_value = mock_hospitals
        mock_reviews.return_value = []

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/hospitals?lat=37.5&lng=127.0&radius=500")

    assert resp.status_code == 200
    data = resp.json()
    assert "hospitals" in data
    assert "total" in data
    assert isinstance(data["hospitals"], list)


@pytest.mark.asyncio
async def test_geocode_api_missing_address():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post("/api/geocode", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_geocode_api_with_address():
    with patch("routers.location.address_to_coords", new_callable=AsyncMock) as mock_geo:
        mock_geo.return_value = {"lat": 37.498, "lng": 127.028}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/geocode", json={"address": "강남역"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["lat"] == 37.498
    assert data["lng"] == 127.028
