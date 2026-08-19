import json

import serverwatch


def test_main_returns_healthy_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args())
    monkeypatch.setattr(
        serverwatch,
        "collect_metrics",
        lambda warning, critical: {
            "cpu": 10.0,
            "memory": 20.0,
            "disk": 30.0,
            "status": "HEALTHY",
        },
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert "Status: HEALTHY" in capsys.readouterr().out


def test_json_output_is_machine_readable(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(json=True))
    monkeypatch.setattr(
        serverwatch,
        "collect_metrics",
        lambda warning, critical: {
            "cpu": 80.0,
            "memory": 20.0,
            "disk": 30.0,
            "status": "WARNING",
        },
    )

    assert serverwatch.main() == serverwatch.EXIT_WARNING
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "WARNING"
    assert payload["cpu"] == 80.0


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
