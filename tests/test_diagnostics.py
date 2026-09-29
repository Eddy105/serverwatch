import pytest
from serverwatch.diagnostics import DiagnosticFinding, diagnose_metrics, findings_to_dict

def metrics(cpu=10.0, memory=20.0, disk=30.0, disk_path="/"):
    return {"cpu": cpu, "memory": memory, "disk": disk, "disk_path": disk_path}

def test_healthy_snapshot_has_no_findings():
    assert diagnose_metrics(metrics()) == []

def test_cpu_warning_contains_evidence():
    finding = diagnose_metrics(metrics(cpu=80.0))[0]
    assert isinstance(finding, DiagnosticFinding)
    assert finding.code == "CPU_USAGE_HIGH"
    assert finding.severity == "warning"
    assert finding.evidence["usage_percent"] == 80.0

def test_critical_disk_contains_path():
    finding = diagnose_metrics(metrics(disk=95.0, disk_path="/var"))[0]
    assert finding.code == "DISK_USAGE_HIGH"
    assert finding.severity == "critical"
    assert finding.evidence["path"] == "/var"

def test_multiple_findings_are_deterministically_ordered():
    findings = diagnose_metrics(metrics(cpu=80.0, memory=91.0, disk=92.0))
    assert [finding.code for finding in findings] == ["CPU_USAGE_HIGH", "MEMORY_USAGE_HIGH", "DISK_USAGE_HIGH"]
    assert [finding.severity for finding in findings] == ["warning", "critical", "critical"]

def test_findings_have_stable_json_shape():
    result = findings_to_dict(diagnose_metrics(metrics(cpu=95.0)))
    assert set(result[0]) == {"code", "severity", "message", "recommendation", "evidence"}

def test_invalid_thresholds_are_rejected():
    with pytest.raises(ValueError, match="warning threshold must be lower"):
        diagnose_metrics(metrics(), 90.0, 80.0)
