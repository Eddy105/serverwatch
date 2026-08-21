import pytest

import serverwatch


def test_health_score_is_perfect_below_warning():
    assert serverwatch.get_health_score(20, 30, 40) == 100


def test_health_score_decreases_linearly_between_thresholds():
    assert serverwatch.get_health_score(82.5, 30, 40) == 75


def test_health_score_reaches_zero_at_critical():
    assert serverwatch.get_health_score(90, 20, 30) == 67


def test_health_score_rejects_invalid_threshold_order():
    with pytest.raises(ValueError, match="warning threshold"):
        serverwatch.get_health_score(20, 30, 40, warning_threshold=90, critical_threshold=80)
