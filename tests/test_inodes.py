import json

import pytest

import serverwatch


def _args(**overrides):
    defaults = {
        "cpu": False,
        "memory": False,
        "swap": False,
        "disk": False,
        "inodes": False,
        "disk_io": False,
        "processes": False,
        "system": False,
        "uptime": False,
        "load": False,
        "network": False,
        "status": False,
        "json": False,
        "disk_path": "/",
        "network_interface": None,
        "warning": 75.0,
        "critical": 90.0,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()


def test_get_inode_usage(monkeypatch):
    stats = type("StatVfs", (), {"f_files": 1000, "f_ffree": 250})()
    monkeypatch.setattr(serverwatch.os, "statvfs", lambda path: stats)

    assert serverwatch.get_inode_usage("/var") == {
        "total": 1000,
        "used": 750,
        "free": 250,
        "percent": 75.0,
    }


def test_get_inode_usage_handles_zero_total(monkeypatch):
    stats = type("StatVfs", (), {"f_files": 0, "f_ffree": 0})()
    monkeypatch.setattr(serverwatch.os, "statvfs", lambda path: stats)

    assert serverwatch.get_inode_usage("/proc")["percent"] == 0.0


def test_inode_metric_uses_selected_path(monkeypatch, capsys):
    seen_paths = []
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(inodes=True, disk_path="/var"),
    )

    def inode_usage(path):
        seen_paths.append(path)
        return {"total": 1000, "used": 750, "free": 250, "percent": 75.0}

    monkeypatch.setattr(serverwatch, "get_inode_usage", inode_usage)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert seen_paths == ["/var"]
    output = capsys.readouterr().out
    assert "Inode usage (/var): 75.0 %" in output
    assert "Inodes used:  750" in output
    assert "Inodes free:  250" in output


def test_inode_metric_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(inodes=True, disk_path="/srv", json=True),
    )
    monkeypatch.setattr(
        serverwatch,
        "get_inode_usage",
        lambda path: {"total": 100, "used": 40, "free": 60, "percent": 40.0},
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "inodes": {"total": 100, "used": 40, "free": 60, "percent": 40.0},
        "disk_path": "/srv",
    }


def test_unreadable_inode_path_exits_with_error(monkeypatch):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(inodes=True, disk_path="/missing"),
    )

    def inode_usage(path):
        raise FileNotFoundError(path)

    monkeypatch.setattr(serverwatch, "get_inode_usage", inode_usage)

    with pytest.raises(SystemExit, match="cannot read disk path '/missing'"):
        serverwatch.main()
