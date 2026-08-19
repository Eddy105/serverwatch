import psutil


def get_cpu_usage():
    return psutil.cpu_percent(interval=1)


def get_memory_usage():
    memory = psutil.virtual_memory()
    return memory.percent


def get_disk_usage():
    disk = psutil.disk_usage("/")
    return disk.percent


def get_status(cpu, memory, disk):
    if cpu >= 90 or memory >= 90 or disk >= 90:
        return "CRITICAL"
    elif cpu >= 75 or memory >= 75 or disk >= 75:
        return "WARNING"
    else:
        return "HEALTHY"


def main():
    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()

    status = get_status(cpu, memory, disk)

    print("SERVERWATCH")
    print()
    print("CPU usage:   ", cpu, "%")
    print("Memory usage:", memory, "%")
    print("Disk usage:  ", disk, "%")
    print()
    print("Status:", status)


if __name__ == "__main__":
    main()
