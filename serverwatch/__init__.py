from . import collectors
from .cli import *

# Compatibility exports for existing integrations and tests that patch the
# collector dependencies through the top-level `serverwatch` module.
os = collectors.os
platform = collectors.platform
psutil = collectors.psutil
socket = collectors.socket
time = collectors.time


def collect_metrics(warning_threshold=75.0, critical_threshold=90.0, disk_path="/"):
    """Collect the complete metric snapshot using top-level dependencies."""
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
