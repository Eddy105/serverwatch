import json

import pytest

import serverwatch


def _counters(received=200, sent=100):
    return type(
        "Network",
        (),
        {
            "bytes_sent": sent,
            "bytes_recv": received,
            "packets_sent": 10,
            "packets_recv": 20,
        },
    )()


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
        "status": False,
        "json": False,
        "disk_path": "/",
        "network_interface": None,
        "warning": 75.0,
        "critical": 90.0,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()


def test_get_network_io_for_interface(monkeypatch):
    interfaces = {"eth0": _counters(received=4096, sent=2048)}
    monkeypatch.setattr(
        serverwatch.psutil,
        "net_io_counters",
        lambda pernic=False: interfaces if pernic else _counters(),
    )

    assert serverwatch.get_network_io("eth0") == {
        "bytes_sent": 2048,
        "bytes_received": 4096,
        "packets_sent": 10,
        "packets_received": 20,
    }


def test_unknown_network_interface_is_rejected(monkeypatch):
    monkeypatch.setattr(
        serverwatch.psutil,
        "net_io_counters",
        lambda pernic=False: {} if pernic else _counters(),
    )

    with pytest.raises(
        serverwatch.NetworkInterfaceError,
        match="network interface 'missing0' was not found",
    ):
        serverwatch.get_network_io("missing0")


def test_network_interface_json_output(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(network=True, network_interface="eth0", json=True),
    )
    monkeypatch.setattr(
        serverwatch,
        "get_network_io",
        lambda interface=None: {
            "bytes_sent": 2048,
            "bytes_received": 4096,
            "packets_sent": 10,
            "packets_received": 20,
        },
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    payload = json.loads(capsys.readouterr().out)
    assert payload["network_interface"] == "eth0"
    assert payload["network"]["bytes_received"] == 4096


def test_network_interface_requires_network_selector(monkeypatch):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(network_interface="eth0"),
    )

    with pytest.raises(SystemExit, match="--network-interface requires --network"):
        serverwatch.main()


def test_unknown_network_interface_exits_cleanly(monkeypatch):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(network=True, network_interface="missing0"),
    )

    def fail(interface=None):
        raise serverwatch.NetworkInterfaceError(
            f"network interface {interface!r} was not found"
        )

    monkeypatch.setattr(serverwatch, "get_network_io", fail)

    with pytest.raises(SystemExit, match="network interface 'missing0' was not found"):
        serverwatch.main()
