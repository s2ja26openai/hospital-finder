"""services/scoring_service.py 단위 테스트"""
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

    def test_positive_wins_over_negative(self):
        # 긍정 2개 > 부정 1개
        assert analyze_sentiment("친절하고 깨끗한데 비싸요") == "positive"

    def test_negative_wins_over_positive(self):
        # 부정 2개 > 긍정 1개
        assert analyze_sentiment("친절하지만 불친절하고 별로에요") == "negative"

    def test_empty_string_is_neutral(self):
        assert analyze_sentiment("") == "neutral"

    def test_positive_keyword_단골(self):
        assert analyze_sentiment("단골이 될 것 같아요") == "positive"

    def test_negative_keyword_최악(self):
        assert analyze_sentiment("최악의 병원이었어요") == "negative"

    def test_positive_keyword_전문(self):
        assert analyze_sentiment("전문적인 진료를 받았어요") == "positive"

    def test_negative_keyword_실망(self):
        assert analyze_sentiment("너무 실망스러웠어요") == "negative"

    def test_positive_keyword_추천(self):
        assert analyze_sentiment("강력히 추천합니다") == "positive"

    def test_negative_keyword_과잉진료(self):
        assert analyze_sentiment("과잉진료가 심한 것 같아요") == "negative"

    def test_positive_keyword_꼼꼼(self):
        assert analyze_sentiment("꼼꼼하게 설명해 주셨어요") == "positive"


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

    def test_total_count_matches(self):
        reviews = ["좋아요"] * 7
        result = extract_points(reviews)
        assert result["total"] == 7

    def test_top_positive_list_type(self):
        reviews = ["친절하고 깨끗해요"] * 5
        result = extract_points(reviews)
        assert isinstance(result["top_positive"], list)

    def test_top_negative_list_type(self):
        reviews = ["불친절하고 별로에요"] * 5
        result = extract_points(reviews)
        assert isinstance(result["top_negative"], list)

    def test_top_positive_max_3(self):
        reviews = ["친절 깨끗 만족 추천 빠르 신속"] * 5
        result = extract_points(reviews)
        assert len(result["top_positive"]) <= 3

    def test_top_negative_max_3(self):
        reviews = ["불친절 별로 비싸 불만 짜증 실망"] * 5
        result = extract_points(reviews)
        assert len(result["top_negative"]) <= 3

    def test_score_zero_when_equal(self):
        # "최악이에요" → negative, "추천합니다" → positive → score=0
        reviews = ["최악이에요", "추천합니다"]
        result = extract_points(reviews)
        assert result["score"] == 0

    def test_reliability_exactly_10(self):
        reviews = ["병원에 다녀왔어요"] * 10  # 중립 10개
        result = extract_points(reviews)
        assert result["total"] == 10
        assert result["reliable"] is True

    def test_summary_empty_when_no_keywords(self):
        reviews = ["병원에 다녀왔습니다"] * 3  # 중립
        result = extract_points(reviews)
        assert result["summary"] == ""
