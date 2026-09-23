import sys
from types import SimpleNamespace

import serverwatch
from serverwatch import main


def test_cpu_details_cli_prints_cpu_values(monkeypatch, capsys):
    frequency = SimpleNamespace(current=3200.0, min=800.0, max=4200.0)
    monkeypatch.setattr(
        serverwatch.psutil, "cpu_percent", lambda interval=1: 37.5
    )
    monkeypatch.setattr(
        serverwatch.psutil,
        "cpu_count",
        lambda logical=True: 8 if logical else 4,
    )
    monkeypatch.setattr(serverwatch.psutil, "cpu_freq", lambda: frequency)
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--cpu-details"])

    assert main() == 0
    output = capsys.readouterr().out
    assert "CPU usage:     37.5 %" in output
    assert "Logical CPUs:  8" in output
    assert "Physical CPUs: 4" in output
    assert "CPU current:   3200.0 MHz" in output
    assert "CPU minimum:   800.0 MHz" in output
    assert "CPU maximum:   4200.0 MHz" in output


def test_cpu_details_cli_supports_json(monkeypatch, capsys):
    frequency = SimpleNamespace(current=3200.0, min=800.0, max=4200.0)
    monkeypatch.setattr(
        serverwatch.psutil, "cpu_percent", lambda interval=1: 37.5
    )
    monkeypatch.setattr(
        serverwatch.psutil,
        "cpu_count",
        lambda logical=True: 8 if logical else 4,
    )
    monkeypatch.setattr(serverwatch.psutil, "cpu_freq", lambda: frequency)
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--cpu-details", "--json"],
    )

    assert main() == 0
    assert capsys.readouterr().out == (
        "{\n"
        '  "cpu_details": {\n'
        '    "percent": 37.5,\n'
        '    "logical_cpus": 8,\n'
        '    "physical_cpus": 4,\n'
        '    "frequency_mhz": {\n'
        '      "current": 3200.0,\n'
        '      "min": 800.0,\n'
        '      "max": 4200.0\n'
        "    }\n"
        "  }\n"
        "}\n"
    )


def test_cpu_details_cli_handles_unavailable_frequency(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch.psutil, "cpu_percent", lambda interval=1: 12.0
    )
    monkeypatch.setattr(
        serverwatch.psutil,
        "cpu_count",
        lambda logical=True: 2 if logical else 1,
    )
    monkeypatch.setattr(serverwatch.psutil, "cpu_freq", lambda: None)
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--cpu-details"])

    assert main() == 0
    assert "CPU frequency: unavailable" in capsys.readouterr().out
