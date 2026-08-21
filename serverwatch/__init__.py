from . import cli as _cli
from . import collectors
from .collectors import (
    DiskIoUnavailableError,
    NetworkInterfaceError,
    TemperatureUnavailableError,
    get_cpu_usage,
    get_disk_io,
    get_disk_usage,
    get_filesystems,
    get_inode_usage,
    get_load_average,
    get_memory_usage,
    get_network_io,
    get_network_status,
    get_process_count,
    get_processes,
    get_swap_usage,
    get_system_info,
    get_temperatures,
    get_uptime_seconds,
)
from .health import (
    EXIT_CRITICAL,
    EXIT_HEALTHY,
    EXIT_WARNING,
    get_exit_code,
    get_health_score,
    get_status,
)

__all__ = (
    "DiskIoUnavailableError",
    "NetworkInterfaceError",
    "TemperatureUnavailableError",
    "EXIT_CRITICAL",
    "EXIT_HEALTHY",
    "EXIT_WARNING",
    "collect_metrics",
    "format_uptime",
    "get_cpu_usage",
    "get_disk_io",
    "get_disk_usage",
    "get_exit_code",
    "get_filesystems",
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


def main():
    # Keep the historical top-level API patchable for integrations and tests.
    original_parse_arguments = _cli.parse_arguments
    original_cli_collect_metrics = _cli.collect_metrics
    function_names = (
        "validate_thresholds",
        "validate_interval",
        "collect_metrics",
        "get_cpu_usage",
        "get_memory_usage",
        "get_swap_usage",
        "get_disk_usage",
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
        "get_exit_code",
        "get_selected_metric",
        "print_metric",
        "format_uptime",
        "print_selected_metric",
        "print_human_readable",
        "run_watch",
    )
    original_functions = {name: getattr(_cli, name) for name in function_names}

    patched_collect_metrics = globals()["collect_metrics"]

    def collect_metrics_compat(*args, **kwargs):
        metrics = patched_collect_metrics(*args, **kwargs)
        if "health_score" in metrics:
            return metrics
        if not all(key in metrics for key in ("cpu", "memory", "disk")):
            return metrics

        warning_threshold = kwargs.get(
            "warning_threshold", args[0] if len(args) > 0 else 75.0
        )
        critical_threshold = kwargs.get(
            "critical_threshold", args[1] if len(args) > 1 else 90.0
        )
        metrics = dict(metrics)
        metrics["health_score"] = get_health_score(
            metrics["cpu"],
            metrics["memory"],
            metrics["disk"],
            warning_threshold,
            critical_threshold,
        )
        return metrics

    patched_functions = {
        name: globals().get(name, original_functions[name]) for name in function_names
    }
    patched_functions["collect_metrics"] = collect_metrics_compat

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
        return args

    try:
        for name, function in patched_functions.items():
            setattr(_cli, name, function)
        _cli.parse_arguments = parse_arguments_compat
        return _cli.main()
    finally:
        _cli.parse_arguments = original_parse_arguments
        _cli.collect_metrics = original_cli_collect_metrics
        for name, function in original_functions.items():
            setattr(_cli, name, function)


print_metric = _cli.print_metric
format_uptime = _cli.format_uptime
get_selected_metric = _cli.get_selected_metric
print_selected_metric = _cli.print_selected_metric
print_human_readable = _cli.print_human_readable
run_watch = _cli.run_watch
