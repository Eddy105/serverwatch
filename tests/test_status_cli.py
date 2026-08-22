import json

import serverwatch


def _args(**overrides):
    defaults = {
        "cpu": False,
        "memory": False,
        "swap": False,
        "disk": False,
        "filesystems": False,
        "inodes": False,
        "disk_io": False,
        "temperatures": False,
        "processes": False,
        "system": False,
        "uptime": False,
        "load": False,
        "network": False,
        "network_status": False,
        "health_breakdown": False,
        "status": True,
        "json": False,
        "watch": False,
        "interval": 5.0,
        "sort": None,
        "top": 10,
        "disk_path": "/",
        "network_interface": None,
        "warning": 75.0,
        "critical": 90.0,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()


def _metrics(status):
    return {"status": status, "health_score": 100}


def test_status_selector_prints_status_and_returns_monitoring_exit_code(
    monkeypatch, capsys
):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args())
    monkeypatch.setattr(
        serverwatch,
        "collect_metrics",
        lambda warning, critical, disk_path: _metrics("WARNING"),
    )

    assert serverwatch.main() == serverwatch.EXIT_WARNING
    assert capsys.readouterr().out == "WARNING\n"


def test_status_selector_supports_json_and_custom_settings(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(
            json=True,
            disk_path="/var",
            warning=60.0,
            critical=85.0,
        ),
    )

    def collect_metrics(warning, critical, disk_path):
        calls.append((warning, critical, disk_path))
        return _metrics("CRITICAL")

    monkeypatch.setattr(serverwatch, "collect_metrics", collect_metrics)

    assert serverwatch.main() == serverwatch.EXIT_CRITICAL
    assert calls == [(60.0, 85.0, "/var")]
    assert json.loads(capsys.readouterr().out) == {"status": "CRITICAL"}


def test_health_breakdown_selector_uses_current_metrics(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(
            health_breakdown=True,
            status=False,
            warning=60.0,
            critical=90.0,
            disk_path="/var",
        ),
    )
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 75.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 30.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 90.0)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert capsys.readouterr().out == (
        "CPU health:    50.0/100\n"
        "Memory health: 100.0/100\n"
        "Disk health:   0.0/100\n"
    )


def test_health_breakdown_selector_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(health_breakdown=True, status=False, json=True),
    )
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 82.5)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 30.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 40.0)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert json.loads(capsys.readouterr().out) == {
        "health_breakdown": {
            "cpu": 50.0,
            "memory": 100.0,
            "disk": 100.0,
        }
    }
