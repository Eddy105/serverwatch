import sys

import pytest

import serverwatch
from serverwatch import (
    EXIT_CRITICAL,
    EXIT_HEALTHY,
    EXIT_WARNING,
    collect_metrics,
    format_uptime,
    get_cpu_usage,
    get_disk_io,
    get_disk_usage,
    get_exit_code,
    get_health_score,
    get_load_average,
    get_memory_usage,
    get_network_io,
    get_process_count,
    get_status,
    get_swap_usage,
    get_system_info,
    get_temperatures,
    get_uptime_seconds,
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
    status = get_status(61, 20, 30, warning_threshold=60, critical_threshold=80)
    assert status == "WARNING"


def test_warning_threshold_must_be_lower_than_critical():
    with pytest.raises(ValueError):
        validate_thresholds(90, 80)


@pytest.mark.parametrize(
    "warning,critical", [(-1, 90), (101, 102), (75, -1), (75, 101)]
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


def test_health_score_is_exposed_from_public_api():
    assert get_health_score(20, 30, 40) == 100


def test_metric_helpers_use_psutil(monkeypatch):
    monkeypatch.setattr(serverwatch.psutil, "cpu_percent", lambda interval: 12.5)
    monkeypatch.setattr(
        serverwatch.psutil,
        "virtual_memory",
        lambda: type("Memory", (), {"percent": 34.5})(),
    )
    monkeypatch.setattr(
        serverwatch.psutil,
        "swap_memory",
        lambda: type(
            "Swap",
            (),
            {"total": 1000, "used": 250, "free": 750, "percent": 25.0},
        )(),
    )
    monkeypatch.setattr(serverwatch.psutil, "pids", lambda: [1, 2, 3, 4])
    disk_paths = []

    def disk_usage(path):
        disk_paths.append(path)
        return type("Disk", (), {"percent": 56.5})()

    monkeypatch.setattr(serverwatch.psutil, "disk_usage", disk_usage)
    monkeypatch.setattr(
        serverwatch.psutil,
        "disk_io_counters",
        lambda: type(
            "DiskIo",
            (),
            {
                "read_count": 10,
                "write_count": 20,
                "read_bytes": 1000,
                "write_bytes": 2000,
            },
        )(),
    )

    assert get_cpu_usage() == 12.5
    assert get_memory_usage() == 34.5
    assert get_swap_usage() == {
        "total": 1000,
        "used": 250,
        "free": 750,
        "percent": 25.0,
    }
    assert get_process_count() == 4
    assert get_disk_usage("/var") == 56.5
    assert disk_paths == ["/var"]
    assert get_disk_io() == {
        "read_count": 10,
        "write_count": 20,
        "read_bytes": 1000,
        "write_bytes": 2000,
    }


def test_disk_io_unavailable(monkeypatch):
    monkeypatch.setattr(serverwatch.psutil, "disk_io_counters", lambda: None)

    with pytest.raises(serverwatch.DiskIoUnavailableError):
        get_disk_io()


def test_temperature_collection(monkeypatch):
    sensor = type(
        "Temperature",
        (),
        {"label": "Package id 0", "current": 54.5, "high": 80.0, "critical": 100.0},
    )()
    monkeypatch.setattr(
        serverwatch.psutil,
        "sensors_temperatures",
        lambda: {"coretemp": [sensor]},
    )

    assert get_temperatures() == [
        {
            "chip": "coretemp",
            "label": "Package id 0",
            "current": 54.5,
            "high": 80.0,
            "critical": 100.0,
        }
    ]


def test_temperature_collection_uses_chip_when_label_is_empty(monkeypatch):
    sensor = type(
        "Temperature",
        (),
        {"label": "", "current": 42.0, "high": None, "critical": None},
    )()
    monkeypatch.setattr(
        serverwatch.psutil,
        "sensors_temperatures",
        lambda: {"acpitz": [sensor]},
    )

    assert get_temperatures()[0]["label"] == "acpitz"


def test_temperature_unavailable_when_no_readings(monkeypatch):
    monkeypatch.setattr(serverwatch.psutil, "sensors_temperatures", lambda: {})

    with pytest.raises(serverwatch.TemperatureUnavailableError):
        get_temperatures()


def test_extended_metric_helpers(monkeypatch):
    monkeypatch.setattr(serverwatch.socket, "gethostname", lambda: "test-host")
    monkeypatch.setattr(serverwatch.platform, "system", lambda: "Linux")
    monkeypatch.setattr(serverwatch.platform, "release", lambda: "6.0-test")
    monkeypatch.setattr(serverwatch.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(serverwatch.psutil, "cpu_count", lambda: 8)
    monkeypatch.setattr(serverwatch.time, "time", lambda: 1000)
    monkeypatch.setattr(serverwatch.psutil, "boot_time", lambda: 100)
    monkeypatch.setattr(serverwatch.os, "getloadavg", lambda: (1.0, 0.5, 0.25))
    counters = type(
        "Network",
        (),
        {
            "bytes_sent": 100,
            "bytes_recv": 200,
            "packets_sent": 10,
            "packets_recv": 20,
        },
    )()
    monkeypatch.setattr(serverwatch.psutil, "net_io_counters", lambda: counters)

    assert get_system_info()["hostname"] == "test-host"
    assert get_system_info()["cpu_count"] == 8
    assert get_uptime_seconds() == 900
    assert get_load_average() == {"1m": 1.0, "5m": 0.5, "15m": 0.25}
    assert get_network_io()["bytes_received"] == 200
    assert format_uptime(90061) == "1d 1h 1m"


def test_collect_metrics(monkeypatch):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 10.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 80.0)
    monkeypatch.setattr(
        serverwatch,
        "get_swap_usage",
        lambda: {"total": 1000, "used": 100, "free": 900, "percent": 10.0},
    )
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 20.0)
    monkeypatch.setattr(serverwatch, "get_process_count", lambda: 42)
    monkeypatch.setattr(serverwatch, "get_system_info", lambda: {"hostname": "host"})
    monkeypatch.setattr(serverwatch, "get_uptime_seconds", lambda: 3600)
    monkeypatch.setattr(
        serverwatch,
        "get_load_average",
        lambda: {"1m": 1.0, "5m": 0.5, "15m": 0.25},
    )
    monkeypatch.setattr(
        serverwatch,
        "get_network_io",
        lambda: {
            "bytes_sent": 100,
            "bytes_received": 200,
            "packets_sent": 10,
            "packets_received": 20,
        },
    )

    metrics = collect_metrics(75.0, 90.0, "/srv")
    assert metrics["cpu"] == 10.0
    assert metrics["memory"] == 80.0
    assert metrics["swap"]["percent"] == 10.0
    assert metrics["disk"] == 20.0
    assert metrics["disk_path"] == "/srv"
    assert metrics["processes"] == 42
    assert metrics["system"]["hostname"] == "host"
    assert metrics["uptime_seconds"] == 3600
    assert metrics["status"] == "WARNING"
    assert metrics["health_score"] == 89


def test_parse_arguments_defaults(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["serverwatch"])
    args = parse_arguments()

    assert args.warning == 75.0
    assert args.critical == 90.0
    assert args.disk_path == "/"
    assert not args.cpu
    assert not args.memory
    assert not args.swap
    assert not args.disk
    assert not args.disk_io
    assert not args.temperatures
    assert not args.processes
    assert not args.json


def test_parse_arguments_options(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "serverwatch",
            "--disk",
            "--disk-path",
            "/var",
            "--warning",
            "60",
            "--critical",
            "85",
        ],
    )
    args = parse_arguments()

    assert args.disk
    assert args.disk_path == "/var"
    assert args.warning == 60.0
    assert args.critical == 85.0
