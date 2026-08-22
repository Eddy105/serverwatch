import json
import sys

import pytest

from serverwatch import NetworkInterfaceError, cli


def test_network_status_cli_filters_interface(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--network-status", "--network-interface", "eth0"],
    )
    monkeypatch.setattr(
        cli,
        "get_network_status",
        lambda interface=None: [
            {
                "interface": interface or "eth0",
                "is_up": True,
                "speed_mbps": 1000,
                "duplex": "2",
                "mtu": 1500,
            }
        ],
    )

    args = cli.parse_arguments()
    name, value = cli.get_selected_metric(args)
    cli.print_selected_metric(
        name,
        value,
        json_output=False,
        network_interface=args.network_interface,
    )

    output = capsys.readouterr().out
    assert "eth0: UP 1000 Mbps" in output


def test_network_status_cli_filter_json(monkeypatch, capsys):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "serverwatch",
            "--network-status",
            "--network-interface",
            "eth0",
            "--json",
        ],
    )
    monkeypatch.setattr(
        cli,
        "get_network_status",
        lambda interface=None: [
            {
                "interface": interface or "eth0",
                "is_up": False,
                "speed_mbps": 100,
                "duplex": "2",
                "mtu": 1500,
            }
        ],
    )

    args = cli.parse_arguments()
    name, value = cli.get_selected_metric(args)
    cli.print_selected_metric(
        name,
        value,
        json_output=True,
        network_interface=args.network_interface,
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["network_interface"] == "eth0"
    assert payload["network_status"][0]["is_up"] is False


def test_network_interface_requires_network_selector(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--network-interface", "eth0"],
    )

    with pytest.raises(SystemExit, match="requires --network or --network-status"):
        cli.main()


def test_network_status_filter_unknown_interface(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--network-status", "--network-interface", "eth9"],
    )
    monkeypatch.setattr(
        cli,
        "get_network_status",
        lambda interface=None: (_ for _ in ()).throw(
            NetworkInterfaceError(f"unknown network interface: {interface}")
        ),
    )

    with pytest.raises(SystemExit, match="eth9"):
        cli.main()
