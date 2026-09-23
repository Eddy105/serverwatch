import serverwatch


def test_load_average_includes_normalized_values(monkeypatch):
    monkeypatch.setattr(serverwatch.os, "getloadavg", lambda: (4.0, 2.0, 1.0))
    monkeypatch.setattr(serverwatch.psutil, "cpu_count", lambda: 4)

    assert serverwatch.get_load_average() == {
        "1m": 4.0,
        "5m": 2.0,
        "15m": 1.0,
        "cpu_count": 4,
        "per_cpu_1m": 1.0,
        "per_cpu_5m": 0.5,
        "per_cpu_15m": 0.25,
    }


def test_load_average_uses_one_cpu_when_cpu_count_is_unavailable(monkeypatch):
    monkeypatch.setattr(serverwatch.os, "getloadavg", lambda: (2.0, 1.0, 0.5))
    monkeypatch.setattr(serverwatch.psutil, "cpu_count", lambda: None)

    assert serverwatch.get_load_average()["cpu_count"] == 1
    assert serverwatch.get_load_average()["per_cpu_1m"] == 2.0
