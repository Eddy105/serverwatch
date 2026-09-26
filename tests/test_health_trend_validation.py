import pytest

from serverwatch.health_trend import get_health_trend


@pytest.mark.parametrize("score", [-1, 101])
def test_health_trend_rejects_invalid_current_score(score):
    with pytest.raises(ValueError, match="score must be between 0 and 100"):
        get_health_trend(score, 80)
