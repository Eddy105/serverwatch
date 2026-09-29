from dataclasses import dataclass

SEVERITY_INFO = "info"
SEVERITY_WARNING = "warning"
SEVERITY_CRITICAL = "critical"

@dataclass(frozen=True)
class DiagnosticFinding:
    code: str
    severity: str
    message: str
    recommendation: str
    evidence: dict
    def to_dict(self):
        return {"code": self.code, "severity": self.severity, "message": self.message, "recommendation": self.recommendation, "evidence": self.evidence}

def _severity_for_usage(usage, warning, critical):
    if usage >= critical:
        return SEVERITY_CRITICAL
    if usage >= warning:
        return SEVERITY_WARNING
    return None

def diagnose_metrics(metrics, warning_threshold=75.0, critical_threshold=90.0):
    if warning_threshold >= critical_threshold:
        raise ValueError("warning threshold must be lower than critical threshold")
    if not 0 <= warning_threshold <= 100:
        raise ValueError("warning threshold must be between 0 and 100")
    if not 0 <= critical_threshold <= 100:
        raise ValueError("critical threshold must be between 0 and 100")
    findings = []
    checks = (("CPU_USAGE_HIGH", "cpu", "CPU usage is elevated.", "Inspect top CPU-consuming processes and workload changes."), ("MEMORY_USAGE_HIGH", "memory", "Memory usage is elevated.", "Inspect memory-heavy processes and available memory pressure."), ("DISK_USAGE_HIGH", "disk", "Filesystem usage is elevated.", "Inspect large files, logs, and container storage on the affected filesystem."))
    for code, metric, message, recommendation in checks:
        usage = float(metrics[metric])
        severity = _severity_for_usage(usage, warning_threshold, critical_threshold)
        if severity is None:
            continue
        evidence = {"metric": metric, "usage_percent": usage, "warning_threshold": warning_threshold, "critical_threshold": critical_threshold}
        if metric == "disk":
            evidence["path"] = metrics.get("disk_path", "/")
        findings.append(DiagnosticFinding(code, severity, message, recommendation, evidence))
    return findings

def findings_to_dict(findings):
    return [finding.to_dict() for finding in findings]

# Diagnosis remains deterministic and read-only.
