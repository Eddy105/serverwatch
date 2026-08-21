import os
import platform
import socket
import time

import psutil


class NetworkInterfaceError(ValueError):
    """Raised when a requested network interface does not exist."""


class DiskIoUnavailableError(ValueError):
    """Raised when disk I/O counters are not available."""


class TemperatureUnavailableError(ValueError):
    """Raised when hardware temperature sensors are unavailable."""


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


def get_filesystems():
    filesystems = []
    for partition in psutil.disk_partitions(all=False):
        try:
            usage = psutil.disk_usage(partition.mountpoint)
        except OSError:
            continue
        filesystems.append(
            {
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "percent": usage.percent,
            }
        )
    return filesystems


def get_inode_usage(path="/"):
    stats = os.statvfs(path)
    total = stats.f_files
    free = stats.f_ffree
    used = max(0, total - free)
    percent = 0.0 if total == 0 else used / total * 100
    return {"total": total, "used": used, "free": free, "percent": percent}


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


def get_temperatures():
    sensor_getter = getattr(psutil, "sensors_temperatures", None)
    if sensor_getter is None:
        raise TemperatureUnavailableError("temperature sensors are not supported")
    sensor_groups = sensor_getter()
    readings = []
    for chip, sensors in sensor_groups.items():
        for sensor in sensors:
            readings.append(
                {
                    "chip": chip,
                    "label": sensor.label or chip,
                    "current": sensor.current,
                    "high": sensor.high,
                    "critical": sensor.critical,
                }
            )
    if not readings:
        raise TemperatureUnavailableError("temperature sensors are not available")
    return readings


def get_process_count():
    return len(psutil.pids())


def get_processes(limit=10, sort_by="cpu"):
    """Return a bounded process snapshot sorted by CPU or memory usage."""
    if limit <= 0:
        raise ValueError("process limit must be greater than 0")
    if sort_by not in {"cpu", "memory"}:
        raise ValueError("process sort must be 'cpu' or 'memory'")

    processes = []
    candidates = list(psutil.process_iter(["pid", "username", "name", "memory_percent", "cmdline"]))
    for process in candidates:
        try:
            process.cpu_percent(interval=None)
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue

    time.sleep(0.1)
    for process in candidates:
        try:
            info = process.info
            command = info.get("cmdline") or []
            processes.append(
                {
                    "pid": info["pid"],
                    "user": info.get("username") or "-",
                    "name": info.get("name") or "-",
                    "cpu_percent": process.cpu_percent(interval=None),
                    "memory_percent": info.get("memory_percent") or 0.0,
                    "command": " ".join(command),
                }
            )
        except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
            continue

    key = "cpu_percent" if sort_by == "cpu" else "memory_percent"
    processes.sort(key=lambda process: process[key], reverse=True)
    return processes[:limit]


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


def get_network_status():
    """Return operational state and link information for network interfaces."""
    stats = psutil.net_if_stats()
    return [
        {
            "interface": interface,
            "is_up": info.isup,
            "speed_mbps": info.speed,
            "duplex": str(info.duplex),
            "mtu": info.mtu,
        }
        for interface, info in sorted(stats.items())
    ]
