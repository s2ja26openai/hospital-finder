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
