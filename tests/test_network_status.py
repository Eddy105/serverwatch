import json
import sys

import serverwatch
from serverwatch import cli


def test_network_status_collects_interface_state(monkeypatch):
    stats = {
        "eth0": type(
            "Stats",
            (),
            {"isup": True, "speed": 1000, "duplex": 2, "mtu": 1500},
        )(),
        "lo": type(
            "Stats",
            (),
            {"isup": True, "speed": 0, "duplex": 0, "mtu": 65536},
        )(),
    }
    monkeypatch.setattr(serverwatch.psutil, "net_if_stats", lambda: stats)

    assert serverwatch.get_network_status() == [
        {
            "interface": "eth0",
            "is_up": True,
            "speed_mbps": 1000,
            "duplex": "2",
            "mtu": 1500,
        },
        {
            "interface": "lo",
            "is_up": True,
            "speed_mbps": 0,
            "duplex": "0",
            "mtu": 65536,
        },
    ]


def test_network_status_selector_json(monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv", ["serverwatch", "--network-status", "--json"]
    )
    monkeypatch.setattr(
        cli,
        "get_network_status",
        lambda: [
            {
                "interface": "eth0",
                "is_up": False,
                "speed_mbps": 100,
                "duplex": "2",
                "mtu": 1500,
            }
        ],
    )

    args = cli.parse_arguments()
    name, value = cli.get_selected_metric(args)
    cli.print_selected_metric(name, value, json_output=True)

    payload = json.loads(capsys.readouterr().out)
    assert payload["network_status"][0]["interface"] == "eth0"
    assert payload["network_status"][0]["is_up"] is False


def test_network_status_human_output(capsys):
    cli.print_selected_metric(
        "network_status",
        [
            {
                "interface": "eth0",
                "is_up": True,
                "speed_mbps": 1000,
                "duplex": "2",
                "mtu": 1500,
            }
        ],
    )

    output = capsys.readouterr().out
    assert "eth0: UP 1000 Mbps" in output
    assert "MTU 1500" in output
