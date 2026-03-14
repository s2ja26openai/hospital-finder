# services/scoring_service.py
"""키워드 기반 한국어 리뷰 감성 분석 및 평점 산출."""

# 병원 리뷰에 자주 등장하는 긍정/부정 키워드
_POSITIVE = [
    "친절", "좋았", "좋아요", "좋은", "깨끗", "깔끔", "만족", "추천",
    "빠르", "신속", "꼼꼼", "자세히", "설명", "편안", "안심", "전문",
    "정확", "감사", "최고", "훌륭", "믿을", "세심", "배려", "따뜻",
    "쾌적", "넓은", "잘 봐", "잘 해", "잘해", "잘 치", "잘치",
    "다시 가", "다시 방문", "또 가", "또 방문", "단골",
]

_NEGATIVE = [
    "불친절", "나쁘", "나빴", "더럽", "지저분", "비싸", "비쌈",
    "오래 기다", "대기 시간", "기다림", "불만", "불쾌", "짜증",
    "불편", "별로", "후회", "안 가", "다신", "실망", "최악",
    "무성의", "무시", "차가운", "퉁명", "진상", "엉터리",
    "과잉 진료", "과잉진료", "돈만", "장사",
]


def analyze_sentiment(review: str) -> str:
    """리뷰 한 건의 감성 판별 → 'positive' | 'negative' | 'neutral'."""
    pos = sum(1 for kw in _POSITIVE if kw in review)
    neg = sum(1 for kw in _NEGATIVE if kw in review)
    if pos > neg:
        return "positive"
    elif neg > pos:
        return "negative"
    return "neutral"


def extract_points(reviews: list[str]) -> dict:
    """
    리뷰 목록에서 긍정/부정 포인트를 추출하고 점수를 산출.
    반환: {
        "score": int,
        "positive_count": int,
        "negative_count": int,
        "total": int,
        "reliable": bool,        # 리뷰 10개 이상이면 True
        "top_positive": [...],    # 자주 등장한 긍정 키워드 상위 3개
        "top_negative": [...],    # 자주 등장한 부정 키워드 상위 3개
        "summary": str,           # 요약 문자열
    }
    """
    if not reviews:
        return {
            "score": 0, "positive_count": 0, "negative_count": 0,
            "total": 0, "reliable": False,
            "top_positive": [], "top_negative": [], "summary": "",
        }

    pos_count = 0
    neg_count = 0

    # 키워드 빈도 집계
    pos_freq: dict[str, int] = {}
    neg_freq: dict[str, int] = {}

    for review in reviews:
        sentiment = analyze_sentiment(review)
        if sentiment == "positive":
            pos_count += 1
        elif sentiment == "negative":
            neg_count += 1

        for kw in _POSITIVE:
            if kw in review:
                pos_freq[kw] = pos_freq.get(kw, 0) + 1
        for kw in _NEGATIVE:
            if kw in review:
                neg_freq[kw] = neg_freq.get(kw, 0) + 1

    top_pos = sorted(pos_freq.items(), key=lambda x: -x[1])[:3]
    top_neg = sorted(neg_freq.items(), key=lambda x: -x[1])[:3]

    score = pos_count - neg_count
    total = len(reviews)
    reliable = total >= 10

    # 요약 문자열 생성
    parts = []
    if top_pos:
        parts.append("👍 " + ", ".join(kw for kw, _ in top_pos))
    if top_neg:
        parts.append("👎 " + ", ".join(kw for kw, _ in top_neg))
    summary = " / ".join(parts) if parts else ""

    return {
        "score": score,
        "positive_count": pos_count,
        "negative_count": neg_count,
        "total": total,
        "reliable": reliable,
        "top_positive": [kw for kw, _ in top_pos],
        "top_negative": [kw for kw, _ in top_neg],
        "summary": summary,
    }
