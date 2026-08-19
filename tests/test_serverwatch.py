import pytest

from serverwatch import (
    EXIT_CRITICAL,
    EXIT_HEALTHY,
    EXIT_WARNING,
    get_exit_code,
    get_status,
    validate_thresholds,
)


def test_status_is_healthy_below_warning_threshold():
    assert get_status(20, 30, 40) == "HEALTHY"


def test_status_is_warning_at_warning_threshold():
    assert get_status(75, 30, 40) == "WARNING"


def test_status_is_critical_at_critical_threshold():
    assert get_status(20, 90, 40) == "CRITICAL"


def test_custom_thresholds():
    assert get_status(61, 20, 30, warning_threshold=60, critical_threshold=80) == "WARNING"


def test_warning_threshold_must_be_lower_than_critical():
    with pytest.raises(ValueError):
        validate_thresholds(90, 80)


@pytest.mark.parametrize("warning,critical", [(-1, 90), (75, 101)])
def test_thresholds_must_be_percentages(warning, critical):
    with pytest.raises(ValueError):
        validate_thresholds(warning, critical)


@pytest.mark.parametrize(
    "status,expected",
    [
        ("HEALTHY", EXIT_HEALTHY),
        ("WARNING", EXIT_WARNING),
        ("CRITICAL", EXIT_CRITICAL),
    ],
)
def test_exit_codes(status, expected):
    assert get_exit_code(status) == expected
