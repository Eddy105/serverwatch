import json
import sys

import pytest

import serverwatch
from serverwatch import cli


class FakeProcess:
    def __init__(self, pid, name, memory, cpu, username="user"):
        self.info = {
            "pid": pid,
            "username": username,
            "name": name,
            "memory_percent": memory,
            "cmdline": [name, "--test"],
        }
        self._cpu = cpu

    def cpu_percent(self, interval=None):
        return self._cpu


def test_get_processes_sorts_by_cpu(monkeypatch):
    processes = [
        FakeProcess(1, "low", 2.0, 4.0),
        FakeProcess(2, "high", 8.0, 42.0),
        FakeProcess(3, "mid", 5.0, 18.0),
    ]
    monkeypatch.setattr(serverwatch.psutil, "process_iter", lambda attrs: processes)
    monkeypatch.setattr(serverwatch.time, "sleep", lambda interval: None)

    result = serverwatch.get_processes(limit=2, sort_by="cpu")

    assert [process["pid"] for process in result] == [2, 3]
    assert result[0]["cpu_percent"] == 42.0
    assert result[0]["command"] == "high --test"


def test_get_processes_sorts_by_memory(monkeypatch):
    processes = [
        FakeProcess(1, "low", 2.0, 4.0),
        FakeProcess(2, "high", 8.0, 42.0),
        FakeProcess(3, "mid", 5.0, 18.0),
    ]
    monkeypatch.setattr(serverwatch.psutil, "process_iter", lambda attrs: processes)
    monkeypatch.setattr(serverwatch.time, "sleep", lambda interval: None)

    result = serverwatch.get_processes(limit=2, sort_by="memory")

    assert [process["pid"] for process in result] == [2, 3]
    assert result[0]["memory_percent"] == 8.0


def test_get_processes_validates_arguments():
    with pytest.raises(ValueError, match="process limit"):
        serverwatch.get_processes(limit=0)
    with pytest.raises(ValueError, match="process sort"):
        serverwatch.get_processes(sort_by="disk")


def test_process_selector_parses_sort_and_top(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--processes", "--sort", "memory", "--top", "5"],
    )

    args = cli.parse_arguments()

    assert args.processes
    assert args.sort == "memory"
    assert args.top == 5


def test_process_selector_returns_details(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--processes", "--sort", "cpu", "--top", "1"],
    )
    monkeypatch.setattr(
        cli,
        "get_processes",
        lambda limit, sort_by: [
            {
                "pid": 10,
                "user": "root",
                "name": "worker",
                "cpu_percent": 50.0,
                "memory_percent": 2.0,
                "command": "worker --test",
            }
        ],
    )

    args = cli.parse_arguments()
    name, value = cli.get_selected_metric(args)

    assert name == "processes"
    assert value[0]["pid"] == 10


def test_process_json_output(capsys):
    value = [
        {
            "pid": 10,
            "user": "root",
            "name": "worker",
            "cpu_percent": 50.0,
            "memory_percent": 2.0,
            "command": "worker --test",
        }
    ]

    cli.print_selected_metric("processes", value, json_output=True)

    payload = json.loads(capsys.readouterr().out)
    assert payload["processes"][0]["pid"] == 10


def test_process_human_output(capsys):
    cli.print_selected_metric(
        "processes",
        [
            {
                "pid": 10,
                "user": "root",
                "name": "worker",
                "cpu_percent": 50.0,
                "memory_percent": 2.0,
                "command": "worker --test",
            }
        ],
    )

    output = capsys.readouterr().out
    assert "worker" in output
    assert "CPU  50.0%" in output
    assert "MEM   2.0%" in output
