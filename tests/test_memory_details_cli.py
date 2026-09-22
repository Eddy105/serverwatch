import sys
from types import SimpleNamespace

import serverwatch
from serverwatch import main


def test_memory_details_cli_prints_memory_values(monkeypatch, capsys):
    memory = SimpleNamespace(
        total=16_000,
        used=6_000,
        available=10_000,
        free=4_000,
        percent=37.5,
    )
    monkeypatch.setattr(serverwatch.psutil, "virtual_memory", lambda: memory)
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--memory-details"])

    assert main() == 0
    output = capsys.readouterr().out
    assert "Memory usage: 37.5 %" in output
    assert "Memory used:  6000 bytes" in output
    assert "Memory available: 10000 bytes" in output
    assert "Memory free:  4000 bytes" in output
    assert "Memory total: 16000 bytes" in output


def test_memory_details_cli_supports_json(monkeypatch, capsys):
    memory = SimpleNamespace(
        total=16_000,
        used=6_000,
        available=10_000,
        free=4_000,
        percent=37.5,
    )
    monkeypatch.setattr(serverwatch.psutil, "virtual_memory", lambda: memory)
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--memory-details", "--json"],
    )

    assert main() == 0
    assert capsys.readouterr().out == (
        '{\n'
        '  "memory_details": {\n'
        '    "total": 16000,\n'
        '    "used": 6000,\n'
        '    "available": 10000,\n'
        '    "free": 4000,\n'
        '    "percent": 37.5\n'
        "  }\n"
        "}\n"
    )
