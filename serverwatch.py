import argparse
import json
import os
import platform
import socket
import time
from functools import partial

import psutil

EXIT_HEALTHY = 0
EXIT_WARNING = 1
EXIT_CRITICAL = 2


class NetworkInterfaceError(ValueError):
    pass


class DiskIoUnavailableError(ValueError):
    pass


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    return psutil.virtual_memory().percent


def get_swap_usage():
    swap = psutil.swap_memory()
    return {
        "total": swap.total,
        "used": swap.used,
        "free": swap.free,
        "percent": swap.percent,
    }


def get_disk_usage(path="/"):
    return psutil.disk_usage(path).percent


def get_inode_usage(path="/"):
    stats = os.statvfs(path)
    total = stats.f_files
    free = stats.f_ffree
    used = max(0, total - free)
    percent = 0.0 if total == 0 else used / total * 100

    return {
        "total": total,
        "used": used,
        "free": free,
        "percent": percent,
    }


def get_disk_io():
    counters = psutil.disk_io_counters()
    if counters is None:
        raise DiskIoUnavailableError("disk I/O counters are not available")

    return {
        "read_count": counters.read_count,
        "write_count": counters.write_count,
        "read_bytes": counters.read_bytes,
        "write_bytes": counters.write_bytes,
    }


def get_process_count():
    return len(psutil.pids())


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


def get_network_io(interface=None):
    if interface is None:
        counters = psutil.net_io_counters()
    else:
        interfaces = psutil.net_io_counters(pernic=True)
        try:
            counters = interfaces[interface]
        except KeyError as error:
            raise NetworkInterfaceError(
                f"network interface {interface!r} was not found"
            ) from error

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


def collect_metrics(
    warning_threshold=75.0,
    critical_threshold=90.0,
    disk_path="/",
):
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
        "--swap", action="store_true", help="Show swap usage only."
    )
    metric_group.add_argument(
        "--disk", action="store_true", help="Show disk usage only."
    )
    metric_group.add_argument(
        "--inodes", action="store_true", help="Show inode usage for --disk-path only."
    )
    metric_group.add_argument(
        "--disk-io", action="store_true", help="Show aggregate disk I/O counters only."
    )
    metric_group.add_argument(
        "--processes", action="store_true", help="Show process count only."
    )
    metric_group.add_argument(
        "--system", action="store_true", help="Show host and system information only."
    )
    metric_group.add_argument(
        "--uptime", action="store_true", help="Show system uptime only."
    )
    metric_group.add_argument(
        "--load", action="store_true", help="Show load averages only."
    )
    metric_group.add_argument(
        "--network", action="store_true", help="Show network I/O counters only."
    )
    metric_group.add_argument(
        "--status", action="store_true", help="Show health status only."
    )
    parser.add_argument("--json", action="store_true", help="Output metrics as JSON.")
    parser.add_argument(
        "--disk-path",
        default="/",
        metavar="PATH",
        help="Filesystem path used for disk usage checks (default: /).",
    )
    parser.add_argument(
        "--network-interface",
        metavar="INTERFACE",
        help="Network interface used with --network (for example: eth0).",
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


def get_selected_metric(args):
    network_getter = get_network_io
    if getattr(args, "network_interface", None):
        network_getter = partial(get_network_io, args.network_interface)

    selectors = (
        ("cpu", args.cpu, get_cpu_usage),
        ("memory", args.memory, get_memory_usage),
        ("swap", args.swap, get_swap_usage),
        ("disk", args.disk, lambda: get_disk_usage(args.disk_path)),
        (
            "inodes",
            getattr(args, "inodes", False),
            partial(get_inode_usage, args.disk_path),
        ),
        ("disk_io", getattr(args, "disk_io", False), get_disk_io),
        ("processes", args.processes, get_process_count),
        ("system", args.system, get_system_info),
        ("uptime_seconds", args.uptime, get_uptime_seconds),
        ("load_average", args.load, get_load_average),
        ("network", args.network, network_getter),
    )

    for name, enabled, getter in selectors:
        if enabled:
            return name, getter()
    return None


def print_selected_metric(
    name,
    value,
    json_output=False,
    disk_path="/",
    network_interface=None,
):
    if json_output:
        payload = {name: value}
        if name in {"disk", "inodes"}:
            payload["disk_path"] = disk_path
        if name == "network" and network_interface:
            payload["network_interface"] = network_interface
        print(json.dumps(payload, indent=2))
        return

    if name == "cpu":
        print_metric("CPU usage", value)
    elif name == "memory":
        print_metric("Memory usage", value)
    elif name == "swap":
        print_metric("Swap usage", value["percent"])
        print(f"Swap used: {value['used']} bytes")
        print(f"Swap total: {value['total']} bytes")
    elif name == "disk":
        print_metric(f"Disk usage ({disk_path})", value)
    elif name == "inodes":
        print_metric(f"Inode usage ({disk_path})", value["percent"])
        print(f"Inodes used:  {value['used']}")
        print(f"Inodes free:  {value['free']}")
        print(f"Inodes total: {value['total']}")
    elif name == "disk_io":
        print(f"Disk read:   {value['read_bytes']} bytes")
        print(f"Disk write:  {value['write_bytes']} bytes")
        print(f"Read ops:    {value['read_count']}")
        print(f"Write ops:   {value['write_count']}")
    elif name == "processes":
        print(f"Processes: {value}")
    elif name == "system":
        print(f"Hostname:     {value['hostname']}")
        print(f"System:       {value['system']}")
        print(f"Kernel:       {value['kernel']}")
        print(f"Architecture: {value['architecture']}")
        print(f"CPU count:    {value['cpu_count']}")
    elif name == "uptime_seconds":
        print(f"Uptime: {format_uptime(value)}")
    elif name == "load_average":
        print(f"Load average: {value['1m']:.2f} {value['5m']:.2f} {value['15m']:.2f}")
    elif name == "network":
        suffix = f" ({network_interface})" if network_interface else ""
        print(f"Network RX{suffix}: {value['bytes_received']} bytes")
        print(f"Network TX{suffix}: {value['bytes_sent']} bytes")
        print(f"Packets RX{suffix}: {value['packets_received']}")
        print(f"Packets TX{suffix}: {value['packets_sent']}")


def print_human_readable(metrics):
    system = metrics["system"]
    swap = metrics["swap"]
    load = metrics["load_average"]
    network = metrics["network"]

    print("SERVERWATCH")
    print("-" * 28)
    print(f"Host:         {system['hostname']}")
    print(f"Kernel:       {system['kernel']}")
    print(f"Uptime:       {format_uptime(metrics['uptime_seconds'])}")
    print(f"Processes:    {metrics['processes']}")
    print()
    print_metric("CPU usage   ", metrics["cpu"])
    print_metric("Memory usage", metrics["memory"])
    print_metric("Swap usage  ", swap["percent"])
    print_metric(f"Disk usage ({metrics['disk_path']})", metrics["disk"])
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

    if getattr(args, "network_interface", None) and not args.network:
        raise SystemExit("serverwatch: error: --network-interface requires --network")

    try:
        if getattr(args, "status", False):
            metrics = collect_metrics(args.warning, args.critical, args.disk_path)
            if args.json:
                print(json.dumps({"status": metrics["status"]}, indent=2))
            else:
                print(metrics["status"])
            return get_exit_code(metrics["status"])

        selected_metric = get_selected_metric(args)
        if selected_metric is not None:
            name, value = selected_metric
            print_selected_metric(
                name,
                value,
                args.json,
                args.disk_path,
                getattr(args, "network_interface", None),
            )
            return EXIT_HEALTHY

        metrics = collect_metrics(args.warning, args.critical, args.disk_path)
    except DiskIoUnavailableError as error:
        raise SystemExit(f"serverwatch: error: {error}") from error
    except NetworkInterfaceError as error:
        raise SystemExit(f"serverwatch: error: {error}") from error
    except OSError as error:
        raise SystemExit(
            f"serverwatch: error: cannot read disk path {args.disk_path!r}: {error}"
        ) from error

    if args.json:
        print(json.dumps(metrics, indent=2))
    else:
        print_human_readable(metrics)

    return get_exit_code(metrics["status"])


if __name__ == "__main__":
    raise SystemExit(main())
