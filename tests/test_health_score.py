import json

import pytest

import serverwatch
from serverwatch import cli


def test_health_score_is_100_below_warning():
    assert serverwatch.get_health_score(10, 20, 30) == 100


def test_health_score_is_0_at_critical():
    assert serverwatch.get_health_score(90, 20, 30) == 67
    assert serverwatch.get_health_score(90, 90, 90) == 0


def test_health_score_uses_equal_weighting():
    assert serverwatch.get_health_score(82.5, 30, 40) == 83


def test_health_score_respects_custom_thresholds():
    assert (
        serverwatch.get_health_score(
            75, 50, 25, warning_threshold=50, critical_threshold=100
        )
        == 83
    )


def test_health_score_validates_threshold_order():
    with pytest.raises(ValueError, match="warning threshold"):
        serverwatch.get_health_score(10, 20, 30, 90, 80)


def test_collect_metrics_includes_health_score(monkeypatch):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 10.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 20.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 30.0)
    monkeypatch.setattr(serverwatch, "get_swap_usage", lambda: {})
    monkeypatch.setattr(serverwatch, "get_process_count", lambda: 1)
    monkeypatch.setattr(serverwatch, "get_uptime_seconds", lambda: 1)
    monkeypatch.setattr(serverwatch, "get_load_average", lambda: {})
    monkeypatch.setattr(serverwatch, "get_network_io", lambda: {})
    monkeypatch.setattr(serverwatch, "get_network_status", lambda: [])
    monkeypatch.setattr(serverwatch, "get_system_info", lambda: {})

    metrics = serverwatch.collect_metrics()

    assert metrics["health_score"] == 100


def test_status_json_contains_health_score(monkeypatch, capsys):
    monkeypatch.setattr(
        cli,
        "parse_arguments",
        lambda: type(
            "Args",
            (),
            {
                "warning": 75.0,
                "critical": 90.0,
                "disk_path": "/",
                "status": True,
                "json": True,
                "watch": False,
                "interval": 5.0,
                "top": 10,
                "sort": None,
                "network": False,
                "network_interface": None,
            },
        )(),
    )
    monkeypatch.setattr(
        cli,
        "collect_metrics",
        lambda *args: {"status": "HEALTHY", "health_score": 100},
    )

    assert cli.main() == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"status": "HEALTHY", "health_score": 100}
