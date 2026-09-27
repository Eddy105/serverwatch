import json

import pytest

import serverwatch


def _args(**overrides):
    defaults = {
        "cpu": False, "memory": False, "swap": False, "swap_details": False,
        "disk": False, "disk_details": False, "filesystems": False,
        "inodes": False, "disk_io": False, "temperatures": False,
        "processes": False, "system": False, "uptime": False, "load": False,
        "load_details": False, "network": False, "network_status": False,
        "health_breakdown": False, "health_score": False, "status": False,
        "json": False, "watch": False, "interval": 5.0, "top": 10, "sort": None,
        "disk_path": "/", "network_interface": None, "warning": 75.0,
        "critical": 90.0, "fail_under": None,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()


def test_health_score_selector_returns_score(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(health_score=True))
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 20.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 30.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 40.0)
    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert capsys.readouterr().out == "Health score: 100/100
"


def test_health_score_selector_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(health_score=True, json=True))
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 20.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 20.0)
    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert json.loads(capsys.readouterr().out) == {"health_score": 67}


def test_fail_under_returns_critical_when_score_is_too_low(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(health_score=True, fail_under=80))
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 90.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 20.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 20.0)
    assert serverwatch.main() == serverwatch.EXIT_CRITICAL
    assert "Health score: 33/100" in capsys.readouterr().out


def test_fail_under_accepts_score_at_threshold(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(health_score=True, fail_under=80))
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 20.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 20.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 20.0)
    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert "Health score: 100/100" in capsys.readouterr().out


@pytest.mark.parametrize("value", [-1, 101])
def test_fail_under_rejects_out_of_range(value, monkeypatch):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(health_score=True, fail_under=value))
    with pytest.raises(SystemExit, match="fail-under must be between 0 and 100"):
        serverwatch.main()


def test_fail_under_requires_health_score(monkeypatch):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(fail_under=80))
    with pytest.raises(SystemExit, match="--fail-under requires --health-score"):
        serverwatch.main()
