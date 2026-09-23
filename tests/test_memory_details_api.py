from types import SimpleNamespace

from serverwatch import get_memory_details


def test_get_memory_details_returns_capacity_and_usage(monkeypatch):
    memory = SimpleNamespace(
        total=16_000,
        used=8_000,
        available=7_000,
        free=6_000,
        percent=50.0,
    )
    monkeypatch.setattr(
        "serverwatch.memory_details.psutil.virtual_memory",
        lambda: memory,
    )

    assert get_memory_details() == {
        "total": 16_000,
        "used": 8_000,
        "available": 7_000,
        "free": 6_000,
        "percent": 50.0,
    }
