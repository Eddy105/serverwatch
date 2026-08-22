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


def get_health_breakdown(
    cpu, memory, disk, warning_threshold=75.0, critical_threshold=90.0
):
    """Return the individual 0-100 component scores for CPU, memory, and disk."""
    if warning_threshold >= critical_threshold:
        raise ValueError("warning threshold must be lower than critical threshold")
    if not 0 <= warning_threshold <= 100:
        raise ValueError("warning threshold must be between 0 and 100")
    if not 0 <= critical_threshold <= 100:
        raise ValueError("critical threshold must be between 0 and 100")

    def score_usage(usage):
        if usage <= warning_threshold:
            return 100.0
        if usage >= critical_threshold:
            return 0.0
        return (
            100.0
            * (critical_threshold - usage)
            / (critical_threshold - warning_threshold)
        )

    return {
        "cpu": score_usage(cpu),
        "memory": score_usage(memory),
        "disk": score_usage(disk),
    }


def get_health_score(
    cpu, memory, disk, warning_threshold=75.0, critical_threshold=90.0
):
    """Return a transparent 0-100 score derived from CPU, memory, and disk."""
    breakdown = get_health_breakdown(
        cpu, memory, disk, warning_threshold, critical_threshold
    )
    return round(sum(breakdown.values()) / len(breakdown))


def get_exit_code(status):
    return {
        "HEALTHY": EXIT_HEALTHY,
        "WARNING": EXIT_WARNING,
        "CRITICAL": EXIT_CRITICAL,
    }[status]
