import argparse
import sys

import pytest

import serverwatch
from serverwatch import cli


def test_validate_watch_interval():
    cli.validate_interval(0.1)

    with pytest.raises(ValueError):
        cli.validate_interval(0)


def test_watch_arguments(monkeypatch):
    monkeypatch.setattr(
        sys,
        "argv",
        ["serverwatch", "--watch", "--interval", "2.5"],
    )

    args = cli.parse_arguments()

    assert args.watch
    assert args.interval == 2.5


def test_watch_repeats_until_keyboard_interrupt(monkeypatch, capsys):
    args = argparse.Namespace(
        json=False,
        interval=0.5,
        disk_path="/",
        network_interface=None,
        warning=75.0,
        critical=90.0,
        watch=True,
    )
    calls = []

    def collect(_args):
        calls.append(1)
        return serverwatch.EXIT_WARNING

    def stop(_interval):
        raise KeyboardInterrupt

    monkeypatch.setattr(cli, "collect_for_args", collect)
    monkeypatch.setattr(cli.time, "sleep", stop)

    assert cli.run_watch(args) == serverwatch.EXIT_WARNING
    assert len(calls) == 1
    assert "Watch stopped." in capsys.readouterr().out


def test_watch_rejects_json():
    args = argparse.Namespace(json=True, interval=1.0)

    with pytest.raises(ValueError, match="--watch cannot be combined with --json"):
        cli.run_watch(args)
