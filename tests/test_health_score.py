import pytest

from serverwatch.health import get_health_score


def test_health_score_is_100_below_warning_threshold():
    assert get_health_score(20, 50, 75) == 100


def test_health_score_is_0_at_critical_threshold():
    assert get_health_score(90, 90, 90) == 0


def test_health_score_uses_equal_linear_weighting():
    assert get_health_score(82.5, 30, 40) == 83


def test_health_score_supports_custom_thresholds():
    assert get_health_score(75, 75, 75, 60, 90) == 50


@pytest.mark.parametrize(
    "warning, critical",
    [(90, 90), (100, 90), (-1, 90), (75, 101)],
)
def test_health_score_rejects_invalid_thresholds(warning, critical):
    with pytest.raises(ValueError):
        get_health_score(20, 30, 40, warning, critical)
