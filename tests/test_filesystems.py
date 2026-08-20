import json
import sys

import serverwatch


def test_get_filesystems_collects_mount_usage(monkeypatch):
    partitions = [
        type(
            "Partition",
            (),
            {"device": "/dev/sda1", "mountpoint": "/", "fstype": "ext4"},
        )(),
        type(
            "Partition",
            (),
            {"device": "/dev/sdb1", "mountpoint": "/srv", "fstype": "xfs"},
        )(),
    ]
    monkeypatch.setattr(
        serverwatch.psutil,
        "disk_partitions",
        lambda all=False: partitions,
    )

    def disk_usage(path):
        values = {
            "/": (1000, 400, 600, 40.0),
            "/srv": (2000, 500, 1500, 25.0),
        }[path]
        return type(
            "Usage",
            (),
            {
                "total": values[0],
                "used": values[1],
                "free": values[2],
                "percent": values[3],
            },
        )()

    monkeypatch.setattr(serverwatch.psutil, "disk_usage", disk_usage)

    assert serverwatch.get_filesystems() == [
        {
            "device": "/dev/sda1",
            "mountpoint": "/",
            "fstype": "ext4",
            "total": 1000,
            "used": 400,
            "free": 600,
            "percent": 40.0,
        },
        {
            "device": "/dev/sdb1",
            "mountpoint": "/srv",
            "fstype": "xfs",
            "total": 2000,
            "used": 500,
            "free": 1500,
            "percent": 25.0,
        },
    ]


def test_get_filesystems_skips_unreadable_mount(monkeypatch):
    partitions = [
        type(
            "Partition",
            (),
            {"device": "/dev/sda1", "mountpoint": "/", "fstype": "ext4"},
        )(),
        type(
            "Partition",
            (),
            {"device": "/dev/sdb1", "mountpoint": "/secret", "fstype": "ext4"},
        )(),
    ]
    monkeypatch.setattr(
        serverwatch.psutil,
        "disk_partitions",
        lambda all=False: partitions,
    )

    def disk_usage(path):
        if path == "/secret":
            raise PermissionError("denied")
        return type(
            "Usage",
            (),
            {"total": 1000, "used": 400, "free": 600, "percent": 40.0},
        )()

    monkeypatch.setattr(serverwatch.psutil, "disk_usage", disk_usage)

    filesystems = serverwatch.get_filesystems()
    assert len(filesystems) == 1
    assert filesystems[0]["mountpoint"] == "/"


def test_filesystem_human_output(capsys):
    value = [
        {
            "device": "/dev/sda1",
            "mountpoint": "/",
            "fstype": "ext4",
            "total": 1000,
            "used": 400,
            "free": 600,
            "percent": 40.0,
        }
    ]

    serverwatch.print_selected_metric("filesystems", value)

    output = capsys.readouterr().out
    assert "/: 40.0 %" in output
    assert "/dev/sda1" in output
    assert "ext4" in output


def test_filesystem_json_output(capsys):
    value = [
        {
            "device": "/dev/sda1",
            "mountpoint": "/",
            "fstype": "ext4",
            "total": 1000,
            "used": 400,
            "free": 600,
            "percent": 40.0,
        }
    ]

    serverwatch.print_selected_metric("filesystems", value, json_output=True)

    payload = json.loads(capsys.readouterr().out)
    assert payload["filesystems"][0]["mountpoint"] == "/"
    assert payload["filesystems"][0]["percent"] == 40.0


def test_parse_filesystems_selector(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--filesystems", "--json"])

    args = serverwatch.parse_arguments()

    assert args.filesystems
    assert args.json
