import json

import pytest

import serverwatch


def _metrics(status="HEALTHY", cpu=10.0, disk_path="/"):
    return {
        "system": {
            "hostname": "test-host",
            "system": "Linux",
            "kernel": "6.0-test",
            "architecture": "x86_64",
            "cpu_count": 8,
        },
        "cpu": cpu,
        "memory": 20.0,
        "swap": {"total": 1000, "used": 250, "free": 750, "percent": 25.0},
        "disk": 30.0,
        "disk_path": disk_path,
        "processes": 42,
        "uptime_seconds": 90061,
        "load_average": {"1m": 1.0, "5m": 0.5, "15m": 0.25},
        "network": {
            "bytes_sent": 100,
            "bytes_received": 200,
            "packets_sent": 10,
            "packets_received": 20,
        },
        "status": status,
        "health_score": 100,
    }


def test_main_returns_healthy_exit_code(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args())
    monkeypatch.setattr(
        serverwatch,
        "collect_metrics",
        lambda warning, critical, disk_path: _metrics(disk_path=disk_path),
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "Host:         test-host" in output
    assert "Uptime:       1d 1h 1m" in output
    assert "Processes:    42" in output
    assert "Swap usage  : 25.0 %" in output
    assert "Disk usage (/): 30.0 %" in output
    assert "Load average: 1.00 0.50 0.25" in output
    assert "Network RX:   200 bytes" in output
    assert "Status: HEALTHY" in output


def test_json_output_is_machine_readable(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(json=True))
    monkeypatch.setattr(
        serverwatch,
        "collect_metrics",
        lambda warning, critical, disk_path: _metrics(
            status="WARNING", cpu=80.0, disk_path=disk_path
        ),
    )

    assert serverwatch.main() == serverwatch.EXIT_WARNING
    payload = json.loads(capsys.readouterr().out)
    assert payload["status"] == "WARNING"
    assert payload["cpu"] == 80.0
    assert payload["swap"]["percent"] == 25.0
    assert payload["disk_path"] == "/"
    assert payload["processes"] == 42
    assert payload["system"]["hostname"] == "test-host"
    assert payload["network"]["bytes_received"] == 200


@pytest.mark.parametrize(
    "metric,getter,label",
    [
        ("cpu", "get_cpu_usage", "CPU usage"),
        ("memory", "get_memory_usage", "Memory usage"),
    ],
)
def test_percentage_metric_output(monkeypatch, capsys, metric, getter, label):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(**{metric: True}))
    monkeypatch.setattr(serverwatch, getter, lambda: 42.5)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert f"{label}: 42.5 %" in capsys.readouterr().out


def test_swap_metric_output(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(swap=True))
    monkeypatch.setattr(
        serverwatch,
        "get_swap_usage",
        lambda: {"total": 1000, "used": 250, "free": 750, "percent": 25.0},
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "Swap usage: 25.0 %" in output
    assert "Swap used: 250 bytes" in output
    assert "Swap total: 1000 bytes" in output


def test_swap_metric_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(swap=True, json=True),
    )
    monkeypatch.setattr(
        serverwatch,
        "get_swap_usage",
        lambda: {"total": 1000, "used": 250, "free": 750, "percent": 25.0},
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    payload = json.loads(capsys.readouterr().out)
    assert payload["swap"]["percent"] == 25.0
    assert payload["swap"]["used"] == 250


def test_process_metric_output(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(processes=True))
    monkeypatch.setattr(serverwatch, "get_process_count", lambda: 42)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert "Processes: 42" in capsys.readouterr().out


def test_process_metric_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(processes=True, json=True),
    )
    monkeypatch.setattr(serverwatch, "get_process_count", lambda: 42)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert json.loads(capsys.readouterr().out) == {"processes": 42}


def test_disk_metric_uses_selected_path(monkeypatch, capsys):
    seen_paths = []
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(disk=True, disk_path="/var"),
    )

    def disk_usage(path):
        seen_paths.append(path)
        return 42.5

    monkeypatch.setattr(serverwatch, "get_disk_usage", disk_usage)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert seen_paths == ["/var"]
    assert "Disk usage (/var): 42.5 %" in capsys.readouterr().out


def test_disk_metric_json_includes_path(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(disk=True, disk_path="/srv", json=True),
    )
    monkeypatch.setattr(serverwatch, "get_disk_usage", lambda path: 33.0)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    payload = json.loads(capsys.readouterr().out)
    assert payload == {"disk": 33.0, "disk_path": "/srv"}


def test_disk_io_metric_output(monkeypatch, capsys):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(disk_io=True))
    monkeypatch.setattr(
        serverwatch,
        "get_disk_io",
        lambda: {
            "read_count": 10,
            "write_count": 20,
            "read_bytes": 1000,
            "write_bytes": 2000,
        },
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "Disk read:   1000 bytes" in output
    assert "Disk write:  2000 bytes" in output
    assert "Read ops:    10" in output
    assert "Write ops:   20" in output


def test_disk_io_metric_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(disk_io=True, json=True),
    )
    monkeypatch.setattr(
        serverwatch,
        "get_disk_io",
        lambda: {
            "read_count": 10,
            "write_count": 20,
            "read_bytes": 1000,
            "write_bytes": 2000,
        },
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    payload = json.loads(capsys.readouterr().out)
    assert payload["disk_io"]["read_bytes"] == 1000
    assert payload["disk_io"]["write_count"] == 20


def test_temperature_metric_output(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(temperatures=True),
    )
    monkeypatch.setattr(
        serverwatch,
        "get_temperatures",
        lambda: [
            {
                "chip": "coretemp",
                "label": "Package id 0",
                "current": 54.5,
                "high": 80.0,
                "critical": 100.0,
            }
        ],
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    output = capsys.readouterr().out
    assert "coretemp/Package id 0: 54.5 °C" in output
    assert "high 80.0 °C" in output
    assert "critical 100.0 °C" in output


def test_temperature_metric_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(temperatures=True, json=True),
    )
    monkeypatch.setattr(
        serverwatch,
        "get_temperatures",
        lambda: [
            {
                "chip": "acpitz",
                "label": "temp1",
                "current": 42.0,
                "high": None,
                "critical": None,
            }
        ],
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    payload = json.loads(capsys.readouterr().out)
    assert payload["temperatures"][0]["current"] == 42.0
    assert payload["temperatures"][0]["chip"] == "acpitz"


def test_temperature_unavailable_exits_with_error(monkeypatch):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(temperatures=True),
    )

    def unavailable():
        raise serverwatch.TemperatureUnavailableError(
            "temperature sensors are not available"
        )

    monkeypatch.setattr(serverwatch, "get_temperatures", unavailable)

    with pytest.raises(SystemExit, match="temperature sensors are not available"):
        serverwatch.main()


@pytest.mark.parametrize(
    "metric,getter,value,expected",
    [
        (
            "system",
            "get_system_info",
            {
                "hostname": "test-host",
                "system": "Linux",
                "kernel": "6.0-test",
                "architecture": "x86_64",
                "cpu_count": 8,
            },
            "Hostname:     test-host",
        ),
        ("uptime", "get_uptime_seconds", 90061, "Uptime: 1d 1h 1m"),
        (
            "load",
            "get_load_average",
            {"1m": 1.0, "5m": 0.5, "15m": 0.25},
            "Load average: 1.00 0.50 0.25",
        ),
        (
            "network",
            "get_network_io",
            {
                "bytes_sent": 100,
                "bytes_received": 200,
                "packets_sent": 10,
                "packets_received": 20,
            },
            "Network RX: 200 bytes",
        ),
    ],
)
def test_extended_metric_output(
    monkeypatch,
    capsys,
    metric,
    getter,
    value,
    expected,
):
    monkeypatch.setattr(serverwatch, "parse_arguments", lambda: _args(**{metric: True}))
    monkeypatch.setattr(serverwatch, getter, lambda: value)

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    assert expected in capsys.readouterr().out


def test_selected_metric_supports_json(monkeypatch, capsys):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(network=True, json=True),
    )
    monkeypatch.setattr(
        serverwatch,
        "get_network_io",
        lambda: {
            "bytes_sent": 100,
            "bytes_received": 200,
            "packets_sent": 10,
            "packets_received": 20,
        },
    )

    assert serverwatch.main() == serverwatch.EXIT_HEALTHY
    payload = json.loads(capsys.readouterr().out)
    assert payload["network"]["bytes_received"] == 200


def test_invalid_thresholds_exit_with_error(monkeypatch):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(warning=90.0, critical=80.0),
    )

    with pytest.raises(SystemExit, match="warning threshold must be lower"):
        serverwatch.main()


def test_unreadable_disk_path_exits_with_error(monkeypatch):
    monkeypatch.setattr(
        serverwatch,
        "parse_arguments",
        lambda: _args(disk=True, disk_path="/missing"),
    )

    def disk_usage(path):
        raise FileNotFoundError(path)

    monkeypatch.setattr(serverwatch, "get_disk_usage", disk_usage)

    with pytest.raises(SystemExit, match="cannot read disk path '/missing'"):
        serverwatch.main()


def _args(**overrides):
    defaults = {
        "cpu": False,
        "memory": False,
        "swap": False,
        "disk": False,
        "disk_io": False,
        "temperatures": False,
        "processes": False,
        "system": False,
        "uptime": False,
        "load": False,
        "network": False,
        "status": False,
        "json": False,
        "disk_path": "/",
        "network_interface": None,
        "warning": 75.0,
        "critical": 90.0,
    }
    defaults.update(overrides)
    return type("Args", (), defaults)()
