from serverwatch.health_trend import get_health_trend


def test_health_trend_improving():
    assert get_health_trend(90, 75)["delta"] == 15
    assert get_health_trend(90, 75)["direction"] == "improving"


def test_health_trend_degrading():
    assert get_health_trend(60, 80)["delta"] == -20
    assert get_health_trend(60, 80)["direction"] == "degrading"


def test_health_trend_stable():
    assert get_health_trend(80, 80)["delta"] == 0
    assert get_health_trend(80, 80)["direction"] == "stable"
