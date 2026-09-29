import sys

import pytest

import serverwatch
from serverwatch import __version__, main
from serverwatch.diagnostics import diagnose


def test_version_is_exposed(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--version"])

    assert main() == 0
    assert capsys.readouterr().out == f"serverwatch {__version__}\n"


def test_health_score_cli_prints_score(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 60.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 30.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 80.0)
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--health-score"])

    assert main() == 0
    assert capsys.readouterr().out == "Health score: 89/100\n"


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


def test_health_score_cli_fail_under_accepts_zero_and_hundred(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 80.0)

    for threshold in ("0", "100"):
        monkeypatch.setattr(
            sys,
            "argv",
            ["serverwatch", "--health-score", "--fail-under", threshold],
        )
        expected = 0 if threshold == "0" else serverwatch.EXIT_CRITICAL
        assert main() == expected
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


def test_health_score_cli_rejects_negative_fail_under(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--health-score", "--fail-under", "-1"],
    )

    with pytest.raises(ValueError, match="fail-under must be between 0 and 100"):
        main()


def test_diagnose_cli_reports_warning_findings(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 80.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 30.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 40.0)
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--diagnose"])

    assert main() == 0
    output = capsys.readouterr().out
    assert "[WARNING] CPU_HIGH" in output
    assert "Inspect top CPU-consuming processes." in output


def test_diagnose_cli_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 95.0)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 40.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 91.0)
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--diagnose", "--json"])

    assert main() == 0
    output = capsys.readouterr().out
    assert '"code": "CPU_HIGH"' in output
    assert '"severity": "CRITICAL"' in output
    assert '"code": "DISK_HIGH"' in output


def test_diagnose_returns_empty_for_healthy_metrics():
    assert diagnose(10.0, 20.0, 30.0) == []


def test_diagnose_reports_multiple_findings_with_evidence():
    findings = diagnose(95.0, 95.0, 91.0, disk_path="/var")

    assert [finding.code for finding in findings] == [
        "CPU_HIGH",
        "MEMORY_HIGH",
        "DISK_HIGH",
    ]
    assert all(finding.severity == "CRITICAL" for finding in findings)
    assert findings[-1].resource == "/var"
    assert findings[-1].to_dict()["evidence"]["usage_percent"] == 91.0


def test_diagnose_rejects_invalid_threshold_order():
    with pytest.raises(ValueError, match="warning threshold must be lower"):
        diagnose(1.0, 1.0, 1.0, warning_threshold=90, critical_threshold=80)


def test_diagnose_rejects_thresholds_outside_percent_range():
    with pytest.raises(ValueError, match="warning threshold must be between"):
        diagnose(1.0, 1.0, 1.0, warning_threshold=-1)
    with pytest.raises(ValueError, match="critical threshold must be between"):
        diagnose(1.0, 1.0, 1.0, critical_threshold=101)
