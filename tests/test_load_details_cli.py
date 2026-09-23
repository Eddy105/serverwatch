import json

import serverwatch


def _args(**overrides):
    defaults = {
        "cpu": False,
        "memory": False,
        "swap": False,
        "swap_details": False,
        "disk": False,
        "disk_details": False,
        "filesystems": False,
        "inodes": False,
        "disk_io": False,
        "temperatures": False,
        "processes": False,
        "system": False,
        "uptime": False,
        "load": False,
        "load_details": False,
        "network": False,
        "network_status": False,
        "health_breakdown": False,
        "status": False,
        "json": False,
        "watch": False,
        "interval": 5.0,
        "top": 10,
        "sort": None,
        "disk_path": "/",
        "network_interface": None,
        "warning": 75.0,
        "critical": 90.0,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()


def test_load_details_cli_output(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch, "parse_arguments", lambda: _args(load_details=True)
    )
    monkeypatch.setattr(
        serverwatch,
        "get_load_average",
        lambda: {
            "1m": 4.0,
            "5m": 2.0,
            "15m": 1.0,
            "cpu_count": 4,
            "per_cpu_1m": 1.0,
            "per_cpu_5m": 0.5,
            "per_cpu_15m": 0.25,
        },
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "Load average: 4.00 2.00 1.00" in output
    assert "CPU count:    4" in output
    assert "Per-CPU load: 1.00 0.50 0.25" in output


def test_load_details_cli_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(load_details=True, json=True),
    )
    expected = {
        "1m": 4.0,
        "5m": 2.0,
        "15m": 1.0,
        "cpu_count": 4,
        "per_cpu_1m": 1.0,
        "per_cpu_5m": 0.5,
        "per_cpu_15m": 0.25,
    }
    monkeypatch.setattr(serverwatch, "get_load_average", lambda: expected)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert json.loads(capsys.readouterr().out) == {"load_details": expected}
