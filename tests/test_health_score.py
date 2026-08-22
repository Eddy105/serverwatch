import pytest

from serverwatch.health import get_health_breakdown, get_health_score


def test_health_score_is_100_below_warning_threshold():
    assert get_health_score(20, 50, 75) == 100


def test_health_score_is_0_at_critical_threshold():
    assert get_health_score(90, 90, 90) == 0


def test_health_score_uses_equal_linear_weighting():
    assert get_health_score(82.5, 30, 40) == 83


def test_health_score_supports_custom_thresholds():
    assert get_health_score(75, 75, 75, 60, 90) == 50


def test_health_breakdown_exposes_each_component():
    breakdown = get_health_breakdown(82.5, 30, 40)
    assert breakdown == {"cpu": 50.0, "memory": 100.0, "disk": 100.0}


def test_health_score_matches_breakdown_average():
    breakdown = get_health_breakdown(80, 70, 85)
    assert get_health_score(80, 70, 85) == round(sum(breakdown.values()) / 3)


@pytest.mark.parametrize(
    "warning, critical",
    [(90, 90), (100, 90), (-1, 90), (75, 101)],
)
def test_health_score_rejects_invalid_thresholds(warning, critical):
    with pytest.raises(ValueError):
        get_health_score(20, 30, 40, warning, critical)
