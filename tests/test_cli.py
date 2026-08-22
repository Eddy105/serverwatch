import json

import pytest

import serverwatch


def _metrics(status="HEALTHY", cpu=10.0, disk_path="/"):
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
        "swap": {"total": 1000, "used": 250, "free": 750, "percent": 25.0},
        "disk": 30.0,
        "disk_path": disk_path,
        "processes": 42,
        "uptime_seconds": 90061,
        "load_average": {"1m": 1.0, "5m": 0.5, "15m": 0.25},
        "network": {
            "bytes_sent": 100,
            "bytes_received": 200,
            "packets_sent": 10,
            "packets_received": 20,
        },
        "status": status,
        "health_score": 100,
    }


def test_main_returns_healthy_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args())
    monkeypatch.setattr(
        serverwatch,
        "collect_metrics",
        lambda warning, critical, disk_path: _metrics(disk_path=disk_path),
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "Host:         test-host" in output
    assert "Uptime:       1d 1h 1m" in output
    assert "Processes:    42" in output
    assert "Swap usage  : 25.0 %" in output
    assert "Disk usage (/): 30.0 %" in output
    assert "Load average: 1.00 0.50 0.25" in output
    assert "Network RX:   200 bytes" in output
    assert "Status: HEALTHY" in output


def test_json_output_is_machine_readable(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(json=True))
    monkeypatch.setattr(
        serverwatch,
        "collect_metrics",
        lambda warning, critical, disk_path: _metrics(
            status="WARNING", cpu=80.0, disk_path=disk_path
        ),
    )

    assert serverwatch.main() == serverwatch.EXIT_WARNING
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "WARNING"
    assert payload["cpu"] == 80.0
    assert payload["swap"]["percent"] == 25.0
    assert payload["disk_path"] == "/"
