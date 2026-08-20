import json

import serverwatch


def _args(**overrides):
    defaults = {
        "cpu": False,
        "memory": False,
        "swap": False,
        "disk": False,
        "processes": False,
        "system": False,
        "uptime": False,
        "load": False,
        "network": False,
        "status": True,
        "json": False,
        "disk_path": "/",
        "warning": 75.0,
        "critical": 90.0,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()


def _metrics(status):
    return {"status": status}


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
