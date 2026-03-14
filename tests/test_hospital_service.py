"""services/hospital_service.py 단위 테스트"""
import pytest
from unittest.mock import patch
from datetime import datetime
from services.hospital_service import get_status, enrich_hospitals, _PY_TO_DAY


def _today_key():
    return _PY_TO_DAY[datetime.now().weekday()]


class TestGetStatus:
    def test_no_hours_returns_unknown(self):
        status, text = get_status({})
        assert status == "unknown"

    def test_no_hours_text(self):
        _, text = get_status({})
        assert text == "운영시간 정보 없음"

    def test_closed_today(self):
        hours = {_today_key(): "휴무"}
        status, text = get_status(hours)
        assert status == "closed"
        assert text == "오늘 휴무"

    def test_open_24h_status(self):
        hours = {_today_key(): "00:00-23:59"}
        status, text = get_status(hours)
        assert status == "open"

    def test_open_24h_text_contains_마감(self):
        hours = {_today_key(): "00:00-23:59"}
        _, text = get_status(hours)
        assert "마감" in text

    def test_invalid_hours_format(self):
        hours = {_today_key(): "잘못된형식"}
        status, text = get_status(hours)
        assert status == "closed"

    def test_today_key_not_in_hours_treated_as_closed(self):
        # 오늘 키가 없으면 기본값 '휴무'로 처리
        hours = {"not_a_day": "09:00-18:00"}
        status, _ = get_status(hours)
        assert status == "closed"

    def test_get_status_returns_tuple(self):
        result = get_status({})
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_open_text_contains_end_time(self):
        hours = {_today_key(): "00:00-23:59"}
        _, text = get_status(hours)
        assert "23:59" in text

    def test_closed_text_is_오늘휴무(self):
        hours = {_today_key(): "휴무"}
        _, text = get_status(hours)
        assert text == "오늘 휴무"

    def test_status_text_not_empty(self):
        status, text = get_status({_today_key(): "00:00-23:59"})
        assert text != ""

    def test_invalid_format_returns_closed_text(self):
        hours = {_today_key(): "INVALID"}
        status, text = get_status(hours)
        assert status == "closed"
        assert text == "오늘 휴무"


class TestEnrichHospitals:
    def _make_hospital(self, hid, name, hours, distance=100):
        return {
            "id": hid, "name": name, "address": "", "phone": "",
            "lat": 37.5, "lng": 127.0,
            "departments": [], "distance": distance, "hours": hours,
        }

    def test_adds_status_field(self):
        hospitals = [self._make_hospital("1", "테스트병원", {})]
        result = enrich_hospitals(hospitals)
        assert "status" in result[0]

    def test_adds_status_text_field(self):
        hospitals = [self._make_hospital("1", "테스트병원", {})]
        result = enrich_hospitals(hospitals)
        assert "statusText" in result[0]

    def test_adds_score_field(self):
        hospitals = [self._make_hospital("1", "테스트병원", {})]
        result = enrich_hospitals(hospitals)
        assert "score" in result[0]

    def test_adds_review_summary_field(self):
        hospitals = [self._make_hospital("1", "테스트병원", {})]
        result = enrich_hospitals(hospitals)
        assert "reviewSummary" in result[0]

    def test_empty_list(self):
        assert enrich_hospitals([]) == []

    def test_sorting_open_first(self):
        today = _today_key()
        hospitals = [
            self._make_hospital("1", "휴무병원", {today: "휴무"}, 100),
            self._make_hospital("2", "운영중병원", {today: "00:00-23:59"}, 300),
        ]
        result = enrich_hospitals(hospitals)
        assert result[0]["name"] == "운영중병원"

    def test_sorting_closed_last(self):
        today = _today_key()
        hospitals = [
            self._make_hospital("1", "휴무병원", {today: "휴무"}, 100),
            self._make_hospital("2", "알수없음병원", {}, 200),
            self._make_hospital("3", "운영중병원", {today: "00:00-23:59"}, 300),
        ]
        result = enrich_hospitals(hospitals)
        # _STATUS_ORDER: open=0, upcoming=1, closed=2, unknown=3
        # 정렬: 운영중(open) → 휴무(closed) → 알수없음(unknown)
        assert result[0]["name"] == "운영중병원"
        assert result[-1]["name"] == "알수없음병원"

    def test_score_initialized_to_zero(self):
        hospitals = [self._make_hospital("1", "병원", {})]
        result = enrich_hospitals(hospitals)
        assert result[0]["score"] == 0

    def test_review_summary_initialized_empty(self):
        hospitals = [self._make_hospital("1", "병원", {})]
        result = enrich_hospitals(hospitals)
        assert result[0]["reviewSummary"] == ""

    def test_original_fields_preserved(self):
        hospitals = [self._make_hospital("1", "테스트병원", {}, distance=250)]
        result = enrich_hospitals(hospitals)
        assert result[0]["name"] == "테스트병원"
        assert result[0]["distance"] == 250

    def test_distance_sort_within_same_status(self):
        hospitals = [
            self._make_hospital("1", "먼병원", {}, distance=500),
            self._make_hospital("2", "가까운병원", {}, distance=100),
        ]
        result = enrich_hospitals(hospitals)
        assert result[0]["name"] == "가까운병원"

    def test_multiple_hospitals_count(self):
        hospitals = [self._make_hospital(str(i), f"병원{i}", {}) for i in range(5)]
        result = enrich_hospitals(hospitals)
        assert len(result) == 5
