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
    get_process_count,
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
    "get_inode_usage",
    "get_load_average",
    "get_memory_usage",
    "get_network_io",
    "get_process_count",
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
        "status": get_status(
            cpu, memory, disk, warning_threshold, critical_threshold
        ),
    }


def main():
    # Keep the historical top-level API patchable for integrations and tests.
    names = (
        "parse_arguments",
        "validate_thresholds",
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
        "get_system_info",
        "get_uptime_seconds",
        "get_load_average",
        "get_network_io",
        "get_status",
        "get_exit_code",
        "get_selected_metric",
        "print_metric",
        "format_uptime",
        "print_selected_metric",
        "print_human_readable",
    )
    for name in names:
        setattr(_cli, name, globals()[name])
    return _cli.main()


print_metric = _cli.print_metric
format_uptime = _cli.format_uptime
get_selected_metric = _cli.get_selected_metric
print_selected_metric = _cli.print_selected_metric
print_human_readable = _cli.print_human_readable
