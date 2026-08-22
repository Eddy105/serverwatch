import json

import pytest

import serverwatch


@pytest.fixture
def health_breakdown_metrics(monkeypatch):
    monkeypatch.setattr(serverwatch, "get_cpu_usage", lambda: 82.5)
    monkeypatch.setattr(serverwatch, "get_memory_usage", lambda: 30.0)
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 40.0)


def test_health_breakdown_cli_output(monkeypatch, capsys, health_breakdown_metrics):
    monkeypatch.setattr(
        "sys.argv",
        ["serverwatch", "--health-breakdown"],
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "CPU health:    50.0/100" in output
    assert "Memory health: 100.0/100" in output
    assert "Disk health:   100.0/100" in output


def test_health_breakdown_cli_json(monkeypatch, capsys, health_breakdown_metrics):
    monkeypatch.setattr(
        "sys.argv",
        ["serverwatch", "--health-breakdown", "--json"],
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert json.loads(capsys.readouterr().out) == {
        "cpu": 50.0,
        "memory": 100.0,
        "disk": 100.0,
    }


def test_health_breakdown_cli_uses_custom_thresholds(
    monkeypatch, capsys, health_breakdown_metrics
):
    monkeypatch.setattr(
        "sys.argv",
        [
            "serverwatch",
            "--health-breakdown",
            "--warning",
            "60",
            "--critical",
            "90",
        ],
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "CPU health:    25.0/100" in output
    assert "Memory health: 100.0/100" in output
    assert "Disk health:   100.0/100" in output


def test_health_breakdown_cli_uses_disk_path(
    monkeypatch, capsys, health_breakdown_metrics
):
    seen_paths = []

    def disk_usage(path):
        seen_paths.append(path)
        return 40.0

    monkeypatch.setattr(serverwatch, "get_disk_usage", disk_usage)
    monkeypatch.setattr(
        "sys.argv",
        ["serverwatch", "--health-breakdown", "--disk-path", "/var"],
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert seen_paths == ["/var"]
    assert "Disk health:   100.0/100" in capsys.readouterr().out


def test_health_breakdown_cli_rejects_invalid_thresholds(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "serverwatch",
            "--health-breakdown",
            "--warning",
            "90",
            "--critical",
            "90",
        ],
    )

    with pytest.raises(ValueError, match="warning threshold"):
        serverwatch.main()
