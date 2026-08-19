import json

import pytest

import serverwatch


def _metrics(status="HEALTHY", cpu=10.0):
    return {
        "system": {
            "hostname": "test-host",
            "system": "Linux",
            "kernel": "6.0-test",
            "architecture": "x86_64",
            "cpu_count": 8,
        },
        "cpu": cpu,
        "memory": 20.0,
        "disk": 30.0,
        "uptime_seconds": 90061,
        "load_average": {"1m": 1.0, "5m": 0.5, "15m": 0.25},
        "network": {
            "bytes_sent": 100,
            "bytes_received": 200,
            "packets_sent": 10,
            "packets_received": 20,
        },
        "status": status,
    }


def test_main_returns_healthy_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args())
    monkeypatch.setattr(
        serverwatch,
        "collect_metrics",
        lambda warning, critical: _metrics(),
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "Host:         test-host" in output
    assert "Uptime:       1d 1h 1m" in output
    assert "Load average: 1.00 0.50 0.25" in output
    assert "Network RX:   200 bytes" in output
    assert "Status: HEALTHY" in output


def test_json_output_is_machine_readable(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(json=True))
    monkeypatch.setattr(
        serverwatch,
        "collect_metrics",
        lambda warning, critical: _metrics(status="WARNING", cpu=80.0),
    )

    assert serverwatch.main() == serverwatch.EXIT_WARNING
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "WARNING"
    assert payload["cpu"] == 80.0
    assert payload["system"]["hostname"] == "test-host"
    assert payload["network"]["bytes_received"] == 200


@pytest.mark.parametrize(
    "metric,getter,label",
    [
        ("cpu", "get_cpu_usage", "CPU usage"),
        ("memory", "get_memory_usage", "Memory usage"),
        ("disk", "get_disk_usage", "Disk usage"),
    ],
)
def test_single_metric_output(monkeypatch, capsys, metric, getter, label):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(**{metric: True}))
    monkeypatch.setattr(serverwatch, getter, lambda: 42.5)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert f"{label}: 42.5 %" in capsys.readouterr().out


def test_invalid_thresholds_exit_with_error(monkeypatch):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(warning=90.0, critical=80.0),
    )

    with pytest.raises(SystemExit, match="warning threshold must be lower"):
        serverwatch.main()


def _args(**overrides):
    defaults = {
        "cpu": False,
        "memory": False,
        "disk": False,
        "json": False,
        "warning": 75.0,
        "critical": 90.0,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()
