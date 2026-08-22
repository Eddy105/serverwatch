import sys

from serverwatch import __version__, main


def test_version_is_exposed(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["serverwatch", "--version"])

    assert main() == 0
    assert capsys.readouterr().out == f"serverwatch {__version__}\n"
