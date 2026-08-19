import argparse
import json

import psutil


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    return psutil.virtual_memory().percent


def get_disk_usage():
    return psutil.disk_usage("/").percent


def get_status(cpu, memory, disk, warning_threshold=75.0, critical_threshold=90.0):
    highest_usage = max(cpu, memory, disk)

    if highest_usage >= critical_threshold:
        return "CRITICAL"
    if highest_usage >= warning_threshold:
        return "WARNING"
    return "HEALTHY"


def collect_metrics(warning_threshold=75.0, critical_threshold=90.0):
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()

    return {
        "cpu": cpu,
        "memory": memory,
        "disk": disk,
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
    metric_group.add_argument(
        "--cpu",
        action="store_true",
        help="Show CPU usage only.",
    )
    metric_group.add_argument(
        "--memory",
        action="store_true",
        help="Show memory usage only.",
    )
    metric_group.add_argument(
        "--disk",
        action="store_true",
        help="Show disk usage only.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output all metrics as JSON.",
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


def print_human_readable(metrics):
    print("SERVERWATCH")
    print("-" * 28)
    print()
    print_metric("CPU usage   ", metrics["cpu"])
    print_metric("Memory usage", metrics["memory"])
    print_metric("Disk usage  ", metrics["disk"])
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
        return
    if args.memory:
        print_metric("Memory usage", get_memory_usage())
        return
    if args.disk:
        print_metric("Disk usage", get_disk_usage())
        return

    metrics = collect_metrics(args.warning, args.critical)

    if args.json:
        print(json.dumps(metrics, indent=2))
        return

    print_human_readable(metrics)


if __name__ == "__main__":
    main()
