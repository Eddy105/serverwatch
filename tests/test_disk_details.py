import json
import sys

import serverwatch
from serverwatch import get_disk_usage_details, parse_arguments


def test_disk_usage_details_uses_psutil(monkeypatch):
    seen_paths = []

    def disk_usage(path):
        seen_paths.append(path)
        return type(
            "Disk",
            (),
            {"total": 1000, "used": 400, "free": 600, "percent": 40.0},
        )()

    monkeypatch.setattr(serverwatch.psutil, "disk_usage", disk_usage)

    assert get_disk_usage_details("/var") == {
        "total": 1000,
        "used": 400,
        "free": 600,
        "percent": 40.0,
    }
    assert seen_paths == ["/var"]


def test_disk_details_selector_output(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: type(
            "Args",
            (),
            {
                "disk_details": True,
                "disk_path": "/srv",
                "json": False,
                "network_interface": None,
            },
        )(),
    )
    monkeypatch.setattr(
        serverwatch,
        "get_disk_usage_details",
        lambda path: {"total": 1000, "used": 400, "free": 600, "percent": 40.0},
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "Disk usage (/srv): 40.0 %" in output
    assert "Disk used:  400 bytes" in output
    assert "Disk free:  600 bytes" in output
    assert "Disk total: 1000 bytes" in output


def test_disk_details_selector_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: type(
            "Args",
            (),
            {
                "disk_details": True,
                "disk_path": "/home",
                "json": True,
                "network_interface": None,
            },
        )(),
    )
    monkeypatch.setattr(
        serverwatch,
        "get_disk_usage_details",
        lambda path: {"total": 1000, "used": 400, "free": 600, "percent": 40.0},
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "disk_details": {
            "total": 1000,
            "used": 400,
            "free": 600,
            "percent": 40.0,
        },
        "disk_path": "/home",
    }


def test_disk_details_is_available_in_argument_parser(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--disk-details", "--disk-path", "/var"],
    )

    args = parse_arguments()

    assert args.disk_details
    assert args.disk_path == "/var"
