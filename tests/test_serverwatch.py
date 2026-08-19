import sys

import pytest

import serverwatch
from serverwatch import (
    EXIT_CRITICAL,
    EXIT_HEALTHY,
    EXIT_WARNING,
    collect_metrics,
    get_cpu_usage,
    get_disk_usage,
    get_exit_code,
    get_memory_usage,
    get_status,
    parse_arguments,
    validate_thresholds,
)


def test_status_is_healthy_below_warning_threshold():
    assert get_status(20, 30, 40) == "HEALTHY"


def test_status_is_warning_at_warning_threshold():
    assert get_status(75, 30, 40) == "WARNING"


def test_status_is_critical_at_critical_threshold():
    assert get_status(20, 90, 40) == "CRITICAL"


def test_custom_thresholds():
    status = get_status(
        61,
        20,
        30,
        warning_threshold=60,
        critical_threshold=80,
    )
    assert status == "WARNING"


def test_warning_threshold_must_be_lower_than_critical():
    with pytest.raises(ValueError):
        validate_thresholds(90, 80)


@pytest.mark.parametrize(
    "warning,critical",
    [(-1, 90), (101, 102), (75, -1), (75, 101)],
)
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


def test_metric_helpers_use_psutil(monkeypatch):
    monkeypatch.setattr(serverwatch.psutil, "cpu_percent", lambda interval: 12.5)
    monkeypatch.setattr(
        serverwatch.psutil,
        "virtual_memory",
        lambda: type("Memory", (), {"percent": 34.5})(),
    )
    monkeypatch.setattr(
        serverwatch.psutil,
        "disk_usage",
        lambda path: type("Disk", (), {"percent": 56.5})(),
    )

    assert get_cpu_usage() == 12.5
    assert get_memory_usage() == 34.5
    assert get_disk_usage() == 56.5


def test_collect_metrics(monkeypatch):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 10.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda: 20.0)

    assert collect_metrics(75.0, 90.0) == {
        "cpu": 10.0,
        "memory": 80.0,
        "disk": 20.0,
        "status": "WARNING",
    }


def test_parse_arguments_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["serverwatch"])
    args = parse_arguments()

    assert args.warning == 75.0
    assert args.critical == 90.0
    assert not args.cpu
    assert not args.memory
    assert not args.disk
    assert not args.json


def test_parse_arguments_options(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--cpu", "--warning", "60", "--critical", "85"],
    )
    args = parse_arguments()

    assert args.cpu
    assert args.warning == 60.0
    assert args.critical == 85.0
