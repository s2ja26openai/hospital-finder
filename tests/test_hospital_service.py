"""services/hospital_service.py 단위 테스트"""
import pytest
from unittest.mock import patch
from services.hospital_service import get_status, enrich_hospitals


class TestGetStatus:
    def test_no_hours_returns_unknown(self):
        status, text = get_status({})
        assert status == "unknown"

    def test_closed_today(self):
        # 오늘 키를 휴무로 설정
        from datetime import datetime
        from services.hospital_service import _PY_TO_DAY
        today_key = _PY_TO_DAY[datetime.now().weekday()]
        hours = {today_key: "휴무"}
        status, text = get_status(hours)
        assert status == "closed"
        assert text == "오늘 휴무"

    def test_open_hours_format(self):
        """운영 중일 때 statusText에 마감 시간 포함 확인"""
        from datetime import datetime
        from services.hospital_service import _PY_TO_DAY
        today_key = _PY_TO_DAY[datetime.now().weekday()]
        # 24시간 운영으로 테스트
        hours = {today_key: "00:00-23:59"}
        status, text = get_status(hours)
        assert status == "open"
        assert "마감" in text

    def test_invalid_hours_format(self):
        from datetime import datetime
        from services.hospital_service import _PY_TO_DAY
        today_key = _PY_TO_DAY[datetime.now().weekday()]
        hours = {today_key: "잘못된형식"}
        status, text = get_status(hours)
        assert status == "closed"


class TestEnrichHospitals:
    def test_adds_required_fields(self):
        hospitals = [{
            "id": "1", "name": "테스트병원", "address": "서울",
            "phone": "02-1234-5678", "lat": 37.5, "lng": 127.0,
            "departments": ["내과"], "distance": 300, "hours": {},
        }]
        result = enrich_hospitals(hospitals)
        assert len(result) == 1
        assert "status" in result[0]
        assert "statusText" in result[0]
        assert "score" in result[0]
        assert "reviewSummary" in result[0]

    def test_sorting_by_status_order(self):
        from datetime import datetime
        from services.hospital_service import _PY_TO_DAY
        today_key = _PY_TO_DAY[datetime.now().weekday()]

        hospitals = [
            {"id": "1", "name": "휴무병원", "address": "", "phone": "", "lat": 37.5,
             "lng": 127.0, "departments": [], "distance": 100, "hours": {today_key: "휴무"}},
            {"id": "2", "name": "알수없음병원", "address": "", "phone": "", "lat": 37.5,
             "lng": 127.0, "departments": [], "distance": 200, "hours": {}},
            {"id": "3", "name": "운영중병원", "address": "", "phone": "", "lat": 37.5,
             "lng": 127.0, "departments": [], "distance": 300, "hours": {today_key: "00:00-23:59"}},
        ]
        result = enrich_hospitals(hospitals)
        # 운영 중(open) → unknown → closed 순
        assert result[0]["name"] == "운영중병원"
        assert result[-1]["name"] == "휴무병원"

    def test_empty_list(self):
        assert enrich_hospitals([]) == []
