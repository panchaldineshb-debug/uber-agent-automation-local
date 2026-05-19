from unittest.mock import patch
from skills.uber_eta.handler import UberETASkill


FAKE_RESULTS = [{"type": "UberX", "eta_minutes": 5, "price_range": "$12-15"}]


def test_get_eta_returns_results():
    with patch("skills.uber_eta.handler.asyncio.run", return_value=FAKE_RESULTS):
        skill = UberETASkill()
        result = skill.get_eta("855 Grove Ave, Edison NJ", "39 Henry St, Edison NJ")
    assert result == FAKE_RESULTS


def test_get_eta_returns_empty_on_exception():
    with patch("skills.uber_eta.handler.asyncio.run", side_effect=Exception("timeout")):
        skill = UberETASkill()
        result = skill.get_eta("pickup", "dropoff")
    assert result == []


def test_get_eta_returns_empty_when_none_returned():
    with patch("skills.uber_eta.handler.asyncio.run", return_value=None):
        skill = UberETASkill()
        result = skill.get_eta("pickup", "dropoff")
    assert result == []
