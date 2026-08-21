import argparse
import json
import time
from functools import partial

from . import collectors
from .health import EXIT_HEALTHY, get_exit_code, get_health_score, get_status

DiskIoUnavailableError = collectors.DiskIoUnavailableError
NetworkInterfaceError = collectors.NetworkInterfaceError
TemperatureUnavailableError = collectors.TemperatureUnavailableError

get_cpu_usage = collectors.get_cpu_usage
get_memory_usage = collectors.get_memory_usage
get_swap_usage = collectors.get_swap_usage
get_disk_usage = collectors.get_disk_usage
get_filesystems = collectors.get_filesystems
get_inode_usage = collectors.get_inode_usage
get_disk_io = collectors.get_disk_io
get_temperatures = collectors.get_temperatures
get_process_count = collectors.get_process_count
get_processes = collectors.get_processes
get_system_info = collectors.get_system_info
get_uptime_seconds = collectors.get_uptime_seconds
get_load_average = collectors.get_load_average
get_network_io = collectors.get_network_io
get_network_status = collectors.get_network_status


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


def get_health_score_for_metrics(
    metrics, warning_threshold=75.0, critical_threshold=90.0
):
    score = metrics.get("health_score")
    if score is not None:
        return score
    if not all(key in metrics for key in ("cpu", "memory", "disk")):
        return None
    return get_health_score(
        metrics["cpu"],
        metrics["memory"],
        metrics["disk"],
        warning_threshold,
        critical_threshold,
    )


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Lightweight Linux system monitoring tool."
    )
    metric_group = parser.add_mutually_exclusive_group()
    metric_options = (
        ("--cpu", "Show CPU usage only."),
        ("--memory", "Show memory usage only."),
        ("--swap", "Show swap usage only."),
        ("--disk", "Show disk usage only."),
        ("--filesystems", "Show mounted filesystem usage only."),
        ("--inodes", "Show inode usage for --disk-path only."),
        ("--disk-io", "Show aggregate disk I/O counters only."),
        ("--temperatures", "Show hardware temperatures only."),
        ("--processes", "Show process count or process details."),
        ("--system", "Show host and system information only."),
        ("--uptime", "Show system uptime only."),
        ("--load", "Show load averages only."),
        ("--network", "Show network I/O counters only."),
        ("--network-status", "Show network interface link status only."),
        ("--status", "Show health status only."),
    )
    for option, help_text in metric_options:
        metric_group.add_argument(option, action="store_true", help=help_text)
    parser.add_argument("--json", action="store_true", help="Output metrics as JSON.")
    parser.add_argument(
        "--watch", action="store_true", help="Continuously refresh the selected view."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=5.0,
        metavar="SECONDS",
        help="Watch refresh interval in seconds (default: 5).",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        metavar="N",
        help="Number of processes shown with --processes --sort (default: 10).",
    )
    parser.add_argument(
        "--sort",
        choices=("cpu", "memory"),
        help="Sort process details by CPU or memory usage.",
    )
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


def validate_interval(interval):
    if interval <= 0:
        raise ValueError("interval must be greater than 0")


def validate_process_options(args):
    if getattr(args, "top", 10) <= 0:
        raise ValueError("process limit must be greater than 0")
    if getattr(args, "sort", None) and not getattr(args, "processes", False):
        raise ValueError("--sort requires --processes")
    if getattr(args, "top", 10) != 10 and not getattr(args, "processes", False):
        raise ValueError("--top requires --processes")


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

    process_details = getattr(args, "sort", None) is not None
    process_getter = partial(
        get_processes,
        getattr(args, "top", 10),
        getattr(args, "sort", None) or "cpu",
    )
    selectors = (
        ("cpu", getattr(args, "cpu", False), get_cpu_usage),
        ("memory", getattr(args, "memory", False), get_memory_usage),
        ("swap", getattr(args, "swap", False), get_swap_usage),
        (
            "disk",
            getattr(args, "disk", False),
            lambda: get_disk_usage(args.disk_path),
        ),
        ("filesystems", getattr(args, "filesystems", False), get_filesystems),
        (
            "inodes",
            getattr(args, "inodes", False),
            partial(get_inode_usage, args.disk_path),
        ),
        ("disk_io", getattr(args, "disk_io", False), get_disk_io),
        ("temperatures", getattr(args, "temperatures", False), get_temperatures),
        (
            "processes",
            getattr(args, "processes", False) and process_details,
            process_getter,
        ),
        ("processes", getattr(args, "processes", False), get_process_count),
        ("system", getattr(args, "system", False), get_system_info),
        ("uptime_seconds", getattr(args, "uptime", False), get_uptime_seconds),
        ("load_average", getattr(args, "load", False), get_load_average),
        ("network", getattr(args, "network", False), network_getter),
        (
            "network_status",
            getattr(args, "network_status", False),
            get_network_status,
        ),
    )
    for name, enabled, getter in selectors:
        if enabled:
            return name, getter()
    return None


def print_selected_metric(
    name, value, json_output=False, disk_path="/", network_interface=None
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
    elif name == "filesystems":
        for filesystem in value:
            device = filesystem["device"] or "-"
            fstype = filesystem["fstype"] or "unknown"
            print(
                f"{filesystem['mountpoint']}: {filesystem['percent']:.1f} % "
                f"({device}, {fstype}, "
                f"{filesystem['used']}/{filesystem['total']} bytes)"
            )
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
    elif name == "temperatures":
        for sensor in value:
            limits = []
            if sensor["high"] is not None:
                limits.append(f"high {sensor['high']:.1f} °C")
            if sensor["critical"] is not None:
                limits.append(f"critical {sensor['critical']:.1f} °C")
            suffix = f" ({', '.join(limits)})" if limits else ""
            print(
                f"{sensor['chip']}/{sensor['label']}: "
                f"{sensor['current']:.1f} °C{suffix}"
            )
    elif name == "processes":
        if isinstance(value, int):
            print(f"Processes: {value}")
            return
        for process in value:
            print(
                f"{process['pid']:>6} {process['user']:<16} "
                f"CPU {process['cpu_percent']:>5.1f}% "
                f"MEM {process['memory_percent']:>5.1f}% "
                f"{process['name']}"
            )
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
    elif name == "network_status":
        for interface in value:
            speed = interface["speed_mbps"]
            speed_text = f"{speed} Mbps" if speed is not None else "unknown speed"
            state = "UP" if interface["is_up"] else "DOWN"
            print(
                f"{interface['interface']}: {state} {speed_text}, "
                f"MTU {interface['mtu']}"
            )


def render_selected(args, selected_metric):
    name, value = selected_metric
    print_selected_metric(
        name,
        value,
        getattr(args, "json", False),
        getattr(args, "disk_path", "/"),
        getattr(args, "network_interface", None),
    )


def collect_for_args(args):
    """Collect and render one CLI iteration for watch mode."""
    selected_metric = get_selected_metric(args)
    if selected_metric is not None:
        render_selected(args, selected_metric)
        return EXIT_HEALTHY

    metrics = collect_metrics(args.warning, args.critical, args.disk_path)
    print_human_readable(metrics)
    return get_exit_code(metrics["status"])


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
    print(
        f"Load average: {load['1m']:.2f} "
        f"{load['5m']:.2f} {load['15m']:.2f}"
    )
    print(f"Network RX:   {network['bytes_received']} bytes")
    print(f"Network TX:   {network['bytes_sent']} bytes")
    print()
    print(f"Health score: {metrics['health_score']}/100")
    print(f"Status: {metrics['status']}")


def run_watch(args):
    interval = getattr(args, "interval", 5.0)
    validate_interval(interval)
    if getattr(args, "json", False):
        raise ValueError("--watch cannot be combined with --json")

    while True:
        status = collect_for_args(args)
        try:
            time.sleep(interval)
        except KeyboardInterrupt:
            print("Watch stopped.")
            return status


def main():
    args = parse_arguments()
    try:
        validate_thresholds(args.warning, args.critical)
        validate_interval(getattr(args, "interval", 5.0))
        validate_process_options(args)
    except ValueError as error:
        raise SystemExit(f"serverwatch: error: {error}") from error

    if getattr(args, "network_interface", None) and not getattr(
        args, "network", False
    ):
        raise SystemExit("serverwatch: error: --network-interface requires --network")

    try:
        if getattr(args, "watch", False):
            return run_watch(args)

        if getattr(args, "status", False):
            metrics = collect_metrics(args.warning, args.critical, args.disk_path)
            if args.json:
                payload = {"status": metrics["status"]}
                score = get_health_score_for_metrics(
                    metrics, args.warning, args.critical
                )
                if score is not None:
                    payload["health_score"] = score
                print(json.dumps(payload, indent=2))
            else:
                print(metrics["status"])
            return get_exit_code(metrics["status"])

        selected_metric = get_selected_metric(args)
        if selected_metric is not None:
            render_selected(args, selected_metric)
            return EXIT_HEALTHY

        metrics = collect_metrics(args.warning, args.critical, args.disk_path)
    except (
        DiskIoUnavailableError,
        TemperatureUnavailableError,
        NetworkInterfaceError,
    ) as error:
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
