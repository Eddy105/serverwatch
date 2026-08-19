import argparse

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


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Lightweight Linux system monitoring tool."
    )
    parser.add_argument(
        "--cpu",
        action="store_true",
        help="Show CPU usage only.",
    )
    parser.add_argument(
        "--memory",
        action="store_true",
        help="Show memory usage only.",
    )
    parser.add_argument(
        "--disk",
        action="store_true",
        help="Show disk usage only.",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()

    if args.cpu:
        print(f"CPU usage: {get_cpu_usage()} %")
        return

    if args.memory:
        print(f"Memory usage: {get_memory_usage()} %")
        return

    if args.disk:
        print(f"Disk usage: {get_disk_usage()} %")
        return

    cpu = get_cpu_usage()
    memory = get_memory_usage()
    disk = get_disk_usage()

    status = get_status(cpu, memory, disk)

    print("SERVERWATCH")
    print("-" * 28)
    print()
    print(f"CPU usage:    {cpu} %")
    print(f"Memory usage: {memory} %")
    print(f"Disk usage:   {disk} %")
    print()
    print(f"Status: {status}")


if __name__ == "__main__":
    main()
