import argparse
import json
import sys
from importlib.metadata import PackageNotFoundError, version

from . import cli as _cli
from . import collectors
from .collectors import (
    DiskIoUnavailableError,
    NetworkInterfaceError,
    TemperatureUnavailableError,
    get_cpu_usage,
    get_disk_io,
    get_disk_usage,
    get_disk_usage_details,
    get_filesystems,
    get_inode_usage,
    get_load_average,
    get_memory_usage,
    get_network_io,
    get_network_status,
    get_process_count,
    get_processes,
    get_swap_usage,
    get_swap_usage_details,
    get_system_info,
    get_temperatures,
    get_uptime_seconds,
)
from .health import (
    EXIT_CRITICAL,
    EXIT_HEALTHY,
    EXIT_WARNING,
    get_exit_code,
    get_health_breakdown,
    get_health_score,
    get_status,
)

try:
    __version__ = version("serverwatch")
except PackageNotFoundError:
    __version__ = "0.2.0"

__all__ = (
    "DiskIoUnavailableError",
    "NetworkInterfaceError",
    "TemperatureUnavailableError",
    "EXIT_CRITICAL",
    "EXIT_HEALTHY",
    "EXIT_WARNING",
    "__version__",
    "collect_metrics",
    "format_uptime",
    "get_cpu_usage",
    "get_disk_io",
    "get_disk_usage",
    "get_disk_usage_details",
    "get_exit_code",
    "get_filesystems",
    "get_health_breakdown",
    "get_health_score",
    "get_inode_usage",
    "get_load_average",
    "get_memory_usage",
    "get_network_io",
    "get_network_status",
    "get_process_count",
    "get_processes",
    "get_selected_metric",
    "get_status",
    "get_swap_usage",
    "get_swap_usage_details",
    "get_system_info",
    "get_temperatures",
    "get_uptime_seconds",
    "main",
    "parse_arguments",
    "print_human_readable",
    "print_metric",
    "print_selected_metric",
    "run_watch",
    "validate_interval",
    "validate_thresholds",
)

# Preserve the historical module attributes used by integrations and tests.
os = collectors.os
platform = collectors.platform
socket = collectors.socket
psutil = collectors.psutil
time = collectors.time

parse_arguments = _cli.parse_arguments
validate_thresholds = _cli.validate_thresholds
validate_interval = _cli.validate_interval


def collect_metrics(warning_threshold=75.0, critical_threshold=90.0, disk_path="/"):
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage(disk_path)
    return {
        "system": get_system_info(),
        "cpu": cpu,
        "memory": memory,
        "swap": get_swap_usage(),
        "disk": disk,
        "disk_path": disk_path,
        "processes": get_process_count(),
        "uptime_seconds": get_uptime_seconds(),
        "load_average": get_load_average(),
        "network": get_network_io(),
        "network_status": get_network_status(),
        "status": get_status(cpu, memory, disk, warning_threshold, critical_threshold),
        "health_score": get_health_score(
            cpu, memory, disk, warning_threshold, critical_threshold
        ),
    }


def _memory_details_cli(argv):
    parser = argparse.ArgumentParser(
        prog="serverwatch --memory-details",
        description="Show detailed memory usage.",
    )
    parser.add_argument("--memory-details", action="store_true")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    args = parser.parse_args(argv)
    memory = psutil.virtual_memory()
    details = {
        "total": memory.total,
        "used": memory.used,
        "available": memory.available,
        "free": memory.free,
        "percent": memory.percent,
    }
    if args.json:
        print(json.dumps({"memory_details": details}, indent=2))
    else:
        print(f"Memory usage: {details['percent']:.1f} %")
        print(f"Memory used:  {details['used']} bytes")
        print(f"Memory available: {details['available']} bytes")
        print(f"Memory free:  {details['free']} bytes")
        print(f"Memory total: {details['total']} bytes")
    return EXIT_HEALTHY


def _health_score_cli(argv):
    parser = argparse.ArgumentParser(
        prog="serverwatch --health-score",
        description="Show the current 0-100 health score.",
    )
    parser.add_argument("--health-score", action="store_true")
    parser.add_argument("--json", action="store_true", help="Output JSON.")
    parser.add_argument(
        "--disk-path",
        default="/",
        metavar="PATH",
        help="Filesystem path used for the disk component (default: /).",
    )
    parser.add_argument(
        "--warning",
        type=float,
        default=75.0,
        metavar="PERCENT",
        help="Warning threshold in percent (default: 75).",
    )
    parser.add_argument(
        "--critical",
        type=float,
        default=90.0,
        metavar="PERCENT",
        help="Critical threshold in percent (default: 90).",
    )
    parser.add_argument(
        "--fail-under",
        type=int,
        metavar="SCORE",
        help="Return exit code 2 when the score is below SCORE.",
    )
    args = parser.parse_args(argv)
    validate_thresholds(args.warning, args.critical)
    if args.fail_under is not None and not 0 <= args.fail_under <= 100:
        raise ValueError("fail-under must be between 0 and 100")

    score = get_health_score(
        get_cpu_usage(),
        get_memory_usage(),
        get_disk_usage(args.disk_path),
        args.warning,
        args.critical,
    )
    if args.json:
        print(f'{{"health_score": {score}}}')
    else:
        print(f"Health score: {score}/100")
    if args.fail_under is not None and score < args.fail_under:
        return EXIT_CRITICAL
    return EXIT_HEALTHY


def main():
    if "--version" in sys.argv[1:]:
        print(f"serverwatch {__version__}")
        return 0
    if "--memory-details" in sys.argv[1:]:
        return _memory_details_cli(sys.argv[1:])
    if "--health-score" in sys.argv[1:]:
        return _health_score_cli(sys.argv[1:])

    # Keep the historical top-level API patchable for integrations and tests.
    original_parse_arguments = _cli.parse_arguments
    original_functions = {
        name: getattr(_cli, name)
        for name in (
            "validate_thresholds",
            "validate_interval",
            "collect_metrics",
            "get_cpu_usage",
            "get_memory_usage",
            "get_swap_usage",
            "get_swap_usage_details",
            "get_disk_usage",
            "get_disk_usage_details",
            "get_filesystems",
            "get_inode_usage",
            "get_disk_io",
            "get_temperatures",
            "get_process_count",
            "get_processes",
            "get_system_info",
            "get_uptime_seconds",
            "get_load_average",
            "get_network_io",
            "get_network_status",
            "get_status",
            "get_health_score",
            "get_exit_code",
            "get_selected_metric",
            "print_metric",
            "format_uptime",
            "print_selected_metric",
            "print_human_readable",
            "run_watch",
        )
    }

    def parse_arguments_compat():
        args = parse_arguments()
        if not hasattr(args, "interval"):
            args.interval = 5.0
        if not hasattr(args, "watch"):
            args.watch = False
        if not hasattr(args, "network_status"):
            args.network_status = False
        if not hasattr(args, "sort"):
            args.sort = None
        if not hasattr(args, "top"):
            args.top = 10
        if not hasattr(args, "health_breakdown"):
            args.health_breakdown = False
        return args

    try:
        for name in original_functions:
            setattr(_cli, name, globals()[name])
        _cli.parse_arguments = parse_arguments_compat
        return _cli.main()
    finally:
        _cli.parse_arguments = original_parse_arguments
        for name, function in original_functions.items():
            setattr(_cli, name, function)


print_metric = _cli.print_metric
format_uptime = _cli.format_uptime
get_selected_metric = _cli.get_selected_metric
print_selected_metric = _cli.print_selected_metric
print_human_readable = _cli.print_human_readable
run_watch = _cli.run_watch
