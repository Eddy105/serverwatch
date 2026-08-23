import pytest

from serverwatch.health import get_health_score


def test_health_score_fail_under_thresholds():
    score = get_health_score(80.0, 80.0, 80.0)
    assert score == 67
    assert score < 80
    assert score >= 0


def test_health_score_fail_under_boundaries():
    score = get_health_score(80.0, 80.0, 80.0)
    assert score < 100
    assert score >= 0


def test_health_score_fail_under_rejects_invalid_thresholds():
    with pytest.raises(ValueError):
        from serverwatch.cli import validate_fail_under

        validate_fail_under(-1)

    with pytest.raises(ValueError):
        from serverwatch.cli import validate_fail_under

        validate_fail_under(101)
