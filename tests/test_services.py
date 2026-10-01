import subprocess

import pytest

from serverwatch.collectors import ServiceObservationError, get_systemd_services


def test_get_systemd_services_parses_fixed_systemctl_output(monkeypatch):
    completed = subprocess.CompletedProcess(
        args=[],
        returncode=0,
        stdout="ssh.service loaded active running OpenSSH server\n"
        "cron.service loaded inactive dead Regular background program processing daemon\n",
        stderr="",
    )
    calls = {}

    def fake_run(command, **kwargs):
        calls["command"] = command
        calls["kwargs"] = kwargs
        return completed

    monkeypatch.setattr(subprocess, "run", fake_run)

    services = get_systemd_services(timeout=3.0)

    assert services == [
        {
            "unit": "ssh.service",
            "load": "loaded",
            "active": "active",
            "sub": "running",
            "description": "OpenSSH server",
        },
        {
            "unit": "cron.service",
            "load": "loaded",
            "active": "inactive",
            "sub": "dead",
            "description": "Regular background program processing daemon",
        },
    ]
    assert calls["command"] == [
        "systemctl",
        "list-units",
        "--type=service",
        "--all",
        "--no-legend",
        "--no-pager",
        "--plain",
    ]
    assert calls["kwargs"]["shell"] is False
    assert calls["kwargs"]["timeout"] == 3.0


def test_get_systemd_services_rejects_non_positive_timeout():
    with pytest.raises(ValueError, match="timeout must be greater than 0"):
        get_systemd_services(timeout=0)


def test_get_systemd_services_reports_command_failure(monkeypatch):
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: subprocess.CompletedProcess(
            args=args[0], returncode=1, stdout="", stderr="systemd unavailable"
        ),
    )

    with pytest.raises(ServiceObservationError, match="systemd unavailable"):
        get_systemd_services()
