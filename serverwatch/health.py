EXIT_HEALTHY = 0
EXIT_WARNING = 1
EXIT_CRITICAL = 2


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
