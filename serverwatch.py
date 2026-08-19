import argparse
import json
import os
import platform
import socket
import time

import psutil

EXIT_HEALTHY = 0
EXIT_WARNING = 1
EXIT_CRITICAL = 2


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    return psutil.virtual_memory().percent


def get_disk_usage():
    return psutil.disk_usage("/").percent


def get_system_info():
    return {
        "hostname": socket.gethostname(),
        "system": platform.system(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "cpu_count": psutil.cpu_count(),
    }


def get_uptime_seconds():
    return max(0, int(time.time() - psutil.boot_time()))


def get_load_average():
    one, five, fifteen = os.getloadavg()
    return {"1m": one, "5m": five, "15m": fifteen}


def get_network_io():
    counters = psutil.net_io_counters()
    return {
        "bytes_sent": counters.bytes_sent,
        "bytes_received": counters.bytes_recv,
        "packets_sent": counters.packets_sent,
        "packets_received": counters.packets_recv,
    }


def get_status(cpu, memory, disk, warning_threshold=75.0, critical_threshold=90.0):
    highest_usage = max(cpu, memory, disk)

    if highest_usage >= critical_threshold:
        return "CRITICAL"
    if highest_usage >= warning_threshold:
        return "WARNING"
    return "HEALTHY"


def get_exit_code(status):
    return {
        "HEALTHY": EXIT_HEALTHY,
        "WARNING": EXIT_WARNING,
        "CRITICAL": EXIT_CRITICAL,
    }[status]


def collect_metrics(warning_threshold=75.0, critical_threshold=90.0):
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()

    return {
        "system": get_system_info(),
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
        "uptime_seconds": get_uptime_seconds(),
        "load_average": get_load_average(),
        "network": get_network_io(),
        "status": get_status(
            cpu,
            memory,
            disk,
            warning_threshold,
            critical_threshold,
        ),
    }


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Lightweight Linux system monitoring tool."
    )
    metric_group = parser.add_mutually_exclusive_group()
    metric_group.add_argument("--cpu", action="store_true", help="Show CPU usage only.")
    metric_group.add_argument(
        "--memory", action="store_true", help="Show memory usage only."
    )
    metric_group.add_argument(
        "--disk", action="store_true", help="Show disk usage only."
    )
    parser.add_argument(
        "--json", action="store_true", help="Output all metrics as JSON."
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
    return parser.parse_args()


def validate_thresholds(warning_threshold, critical_threshold):
    if not 0 <= warning_threshold <= 100:
        raise ValueError("warning threshold must be between 0 and 100")
    if not 0 <= critical_threshold <= 100:
        raise ValueError("critical threshold must be between 0 and 100")
    if warning_threshold >= critical_threshold:
        raise ValueError("warning threshold must be lower than critical threshold")


def print_metric(label, value):
    print(f"{label}: {value:.1f} %")


def format_uptime(seconds):
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{days}d {hours}h {minutes}m"


def print_human_readable(metrics):
    system = metrics["system"]
    load = metrics["load_average"]
    network = metrics["network"]

    print("SERVERWATCH")
    print("-" * 28)
    print(f"Host:         {system['hostname']}")
    print(f"Kernel:       {system['kernel']}")
    print(f"Uptime:       {format_uptime(metrics['uptime_seconds'])}")
    print()
    print_metric("CPU usage   ", metrics["cpu"])
    print_metric("Memory usage", metrics["memory"])
    print_metric("Disk usage  ", metrics["disk"])
    print(f"Load average: {load['1m']:.2f} {load['5m']:.2f} {load['15m']:.2f}")
    print(f"Network RX:   {network['bytes_received']} bytes")
    print(f"Network TX:   {network['bytes_sent']} bytes")
    print()
    print(f"Status: {metrics['status']}")


def main():
    args = parse_arguments()

    try:
        validate_thresholds(args.warning, args.critical)
    except ValueError as error:
        raise SystemExit(f"serverwatch: error: {error}") from error

    if args.cpu:
        print_metric("CPU usage", get_cpu_usage())
        return EXIT_HEALTHY
    if args.memory:
        print_metric("Memory usage", get_memory_usage())
        return EXIT_HEALTHY
    if args.disk:
        print_metric("Disk usage", get_disk_usage())
        return EXIT_HEALTHY

    metrics = collect_metrics(args.warning, args.critical)

    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        print_human_readable(metrics)

    return get_exit_code(metrics["status"])


if __name__ == "__main__":
    raise SystemExit(main())
