import json

import pytest

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
        "health_score": False,
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
        "fail_under": None,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()


def _patch_score_collectors(monkeypatch, score=82):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 20.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 30.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 40.0)
    monkeypatch.setattr(
        serverwatch,
        "get_health_score",
        lambda cpu, memory, disk, warning, critical: score,
    )


def test_health_score_selector_prints_score(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch, "parse_arguments", lambda: _args(health_score=True)
    )
    _patch_score_collectors(monkeypatch)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert capsys.readouterr().out == "Health score: 82/100\n"


def test_health_score_selector_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(health_score=True, json=True),
    )
    _patch_score_collectors(monkeypatch, score=91)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert json.loads(capsys.readouterr().out) == {"health_score": 91}


def test_health_score_selector_uses_thresholds_and_disk_path(monkeypatch, capsys):
    seen = {}

    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(
            health_score=True,
            warning=60.0,
            critical=90.0,
            disk_path="/var",
        ),
    )
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 20.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 30.0)

    def get_disk_usage(path):
        seen["path"] = path
        return 40.0

    def get_health_score(cpu, memory, disk, warning, critical):
        seen["inputs"] = (cpu, memory, disk, warning, critical)
        return 82

    monkeypatch.setattr(serverwatch, "get_disk_usage", get_disk_usage)
    monkeypatch.setattr(serverwatch, "get_health_score", get_health_score)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert seen == {"path": "/var", "inputs": (20.0, 30.0, 40.0, 60.0, 90.0)}
    assert "Health score: 82/100" in capsys.readouterr().out


@pytest.mark.parametrize("score,expected", [(82, serverwatch.EXIT_HEALTHY), (79, serverwatch.EXIT_CRITICAL)])
def test_fail_under_controls_exit_code(monkeypatch, capsys, score, expected):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(health_score=True, fail_under=80),
    )
    _patch_score_collectors(monkeypatch, score=score)

    assert serverwatch.main() == expected
    assert f"Health score: {score}/100" in capsys.readouterr().out


def test_fail_under_requires_health_score(monkeypatch):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(fail_under=80),
    )

    with pytest.raises(SystemExit, match="--fail-under requires --health-score"):
        serverwatch.main()


@pytest.mark.parametrize("value", [-1, 101])
def test_fail_under_rejects_out_of_range_values(monkeypatch, value):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(health_score=True, fail_under=value),
    )

    with pytest.raises(SystemExit, match="fail-under must be between 0 and 100"):
        serverwatch.main()
