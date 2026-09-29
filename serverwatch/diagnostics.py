from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class DiagnosticFinding:
    code: str
    severity: str
    resource: str
    message: str
    evidence: dict[str, Any]
    recommendation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def diagnose(
    cpu: float,
    memory: float,
    disk: float,
    warning_threshold: float = 75.0,
    critical_threshold: float = 90.0,
    disk_path: str = "/",
) -> list[DiagnosticFinding]:
    if warning_threshold >= critical_threshold:
        raise ValueError("warning threshold must be lower than critical threshold")
    if not 0 <= warning_threshold <= 100:
        raise ValueError("warning threshold must be between 0 and 100")
    if not 0 <= critical_threshold <= 100:
        raise ValueError("critical threshold must be between 0 and 100")

    checks = (
        (
            "CPU_HIGH",
            "CPU",
            cpu,
            "CPU utilization is elevated.",
            "Inspect top CPU-consuming processes.",
        ),
        (
            "MEMORY_HIGH",
            "memory",
            memory,
            "Memory utilization is elevated.",
            "Inspect memory-heavy processes.",
        ),
        (
            "DISK_HIGH",
            disk_path,
            disk,
            "Filesystem usage is elevated.",
            "Inspect large files, logs, caches, and container storage.",
        ),
    )
    findings = []
    for code, resource, value, message, recommendation in checks:
        severity = (
            "CRITICAL"
            if value >= critical_threshold
            else "WARNING"
            if value >= warning_threshold
            else None
        )
        if severity:
            findings.append(
                DiagnosticFinding(
                    code,
                    severity,
                    resource,
                    message,
                    {
                        "usage_percent": value,
                        "warning_threshold": warning_threshold,
                        "critical_threshold": critical_threshold,
                    },
                    recommendation,
                )
            )
    return findings
