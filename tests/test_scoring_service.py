"""services/scoring_service.py 단위 테스트"""
import pytest
from services.scoring_service import analyze_sentiment, extract_points


class TestAnalyzeSentiment:
    def test_positive_review(self):
        assert analyze_sentiment("의사 선생님이 너무 친절하고 깨끗한 병원이에요") == "positive"

    def test_negative_review(self):
        assert analyze_sentiment("불친절하고 대기 시간이 너무 길어요") == "negative"

    def test_neutral_review(self):
        assert analyze_sentiment("병원에 다녀왔습니다") == "neutral"

    def test_positive_keywords(self):
        assert analyze_sentiment("만족스러운 진료 추천합니다") == "positive"

    def test_negative_keywords(self):
        assert analyze_sentiment("비싸고 별로였어요 다신 안 가") == "negative"


class TestExtractPoints:
    def test_empty_reviews(self):
        result = extract_points([])
        assert result["score"] == 0
        assert result["total"] == 0
        assert result["reliable"] is False
        assert result["summary"] == ""

    def test_score_calculation(self):
        reviews = [
            "친절하고 좋았어요",
            "만족합니다 추천해요",
            "불친절해요 별로",
        ]
        result = extract_points(reviews)
        # pos=2, neg=1 → score=1
        assert result["score"] == 1
        assert result["positive_count"] == 2
        assert result["negative_count"] == 1

    def test_reliability_below_10(self):
        reviews = ["친절해요"] * 9
        result = extract_points(reviews)
        assert result["reliable"] is False

    def test_reliability_10_or_more(self):
        reviews = ["친절해요"] * 10
        result = extract_points(reviews)
        assert result["reliable"] is True

    def test_summary_contains_keywords(self):
        reviews = ["친절하고 깨끗해요", "만족합니다", "불친절해요"]
        result = extract_points(reviews)
        assert "👍" in result["summary"] or "👎" in result["summary"]

    def test_all_positive(self):
        reviews = ["친절해요 만족"] * 5
        result = extract_points(reviews)
        assert result["score"] > 0
        assert result["negative_count"] == 0

    def test_all_negative(self):
        reviews = ["불친절해요 별로"] * 5
        result = extract_points(reviews)
        assert result["score"] < 0
        assert result["positive_count"] == 0
