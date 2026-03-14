# routers/hospital.py
from fastapi import APIRouter, Query
from services.kakao_hospital_service import search_hospitals
from services.hospital_service import enrich_hospitals

router = APIRouter(prefix="/api")


@router.get("/hospitals")
async def hospitals_api(
    lat: float = Query(..., description="위도"),
    lng: float = Query(..., description="경도"),
    radius: int = Query(500, description="반경 (미터)"),
    department: str = Query("", description="진료과 (예: 내과)"),
    sort: str = Query("score", description="정렬 기준: score | distance"),
):
    raw = await search_hospitals(lat, lng, radius, department)
    enriched = enrich_hospitals(raw)

    if sort == "distance":
        enriched.sort(key=lambda x: x.get("distance", 0))

    return {"hospitals": enriched, "total": len(enriched)}


@router.get("/hospitals/{hospital_id}")
async def hospital_detail_api(hospital_id: str):
    """
    카카오 로컬 API는 ID로 단건 조회를 지원하지 않음.
    병원 목록 조회 시 저장된 데이터를 프론트에서 전달하거나,
    카카오 Place ID로 place_url을 반환하는 방식으로 처리.
    """
    return {"error": "상세 조회는 병원 목록에서 직접 데이터를 사용합니다.", "id": hospital_id}
