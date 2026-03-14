# routers/review.py
from fastapi import APIRouter
from services.naver_crawler import get_reviews
from services.scoring_service import extract_points

router = APIRouter(prefix="/api")


@router.get("/reviews/{hospital_name}")
async def reviews_api(hospital_name: str):
    """병원명으로 네이버 리뷰 수집 + 감성 분석 결과 반환."""
    reviews = await get_reviews(hospital_name)
    result = extract_points(reviews)
    return {
        "hospital_name": hospital_name,
        "review_count": result["total"],
        "score": result["score"],
        "reliable": result["reliable"],
        "positive_count": result["positive_count"],
        "negative_count": result["negative_count"],
        "top_positive": result["top_positive"],
        "top_negative": result["top_negative"],
        "summary": result["summary"],
    }
