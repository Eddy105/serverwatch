import sys

import pytest

import serverwatch
from serverwatch import __version__, main


def test_version_is_exposed(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--version"])

    assert main() == 0
    assert capsys.readouterr().out == f"serverwatch {__version__}\n"


def test_health_score_cli_prints_score(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 60.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 30.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 40.0)
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--health-score"])

    assert main() == 0
    assert capsys.readouterr().out == "Health score: 100/100\n"


def test_health_score_cli_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 80.0)
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--health-score", "--json"])

    assert main() == 0
    assert capsys.readouterr().out == '{"health_score": 67}\n'


def test_health_score_cli_json_preserves_fail_under_result(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 80.0)
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--health-score", "--json", "--fail-under", "70"],
    )

    assert main() == serverwatch.EXIT_CRITICAL
    assert capsys.readouterr().out == '{"health_score": 67}\n'


def test_health_score_cli_fail_under_returns_critical(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 80.0)
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--health-score", "--fail-under", "70"],
    )

    assert main() == serverwatch.EXIT_CRITICAL
    assert capsys.readouterr().out == "Health score: 67/100\n"


def test_health_score_cli_fail_under_accepts_exact_score(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 80.0)
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--health-score", "--fail-under", "67"],
    )

    assert main() == 0
    assert capsys.readouterr().out == "Health score: 67/100\n"


def test_health_score_cli_rejects_invalid_thresholds(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "serverwatch",
            "--health-score",
            "--warning",
            "90",
            "--critical",
            "80",
        ],
    )

    with pytest.raises(ValueError, match="warning threshold must be lower"):
        main()


def test_health_score_cli_rejects_invalid_fail_under(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--health-score", "--fail-under", "101"],
    )

    with pytest.raises(ValueError, match="fail-under must be between 0 and 100"):
        main()
