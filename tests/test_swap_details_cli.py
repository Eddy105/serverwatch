import sys
from types import SimpleNamespace

import serverwatch
from serverwatch import main


def test_swap_details_cli_prints_swap_values(monkeypatch, capsys):
    swap = SimpleNamespace(
        total=16_000,
        used=6_000,
        free=10_000,
        percent=37.5,
        sin=123_000,
        sout=456_000,
    )
    monkeypatch.setattr(serverwatch.psutil, "swap_memory", lambda: swap)
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--swap-details"])

    assert main() == 0
    output = capsys.readouterr().out
    assert "Swap usage: 37.5 %" in output
    assert "Swap used:  6000 bytes" in output
    assert "Swap free:  10000 bytes" in output
    assert "Swap total: 16000 bytes" in output
    assert "Swap in:    123000 bytes" in output
    assert "Swap out:   456000 bytes" in output


def test_swap_details_cli_supports_json(monkeypatch, capsys):
    swap = SimpleNamespace(
        total=16_000,
        used=6_000,
        free=10_000,
        percent=37.5,
        sin=123_000,
        sout=456_000,
    )
    monkeypatch.setattr(serverwatch.psutil, "swap_memory", lambda: swap)
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--swap-details", "--json"],
    )

    assert main() == 0
    assert capsys.readouterr().out == (
        "{\n"
        '  "swap_details": {\n'
        '    "total": 16000,\n'
        '    "used": 6000,\n'
        '    "free": 10000,\n'
        '    "percent": 37.5,\n'
        '    "sin": 123000,\n'
        '    "sout": 456000\n'
        "  }\n"
        "}\n"
    )
