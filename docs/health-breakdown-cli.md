# Health breakdown CLI

ServerWatch can show the individual CPU, memory, and disk components of the health score without requiring callers to calculate them themselves.

Human-readable output:

```bash
serverwatch --health-breakdown
```

Example:

```text
CPU health:    50.0/100
Memory health: 100.0/100
Disk health:   100.0/100
```

For automation, use JSON:

```bash
serverwatch --health-breakdown --json
```

Custom thresholds and disk paths are supported:

```bash
serverwatch --health-breakdown --warning 70 --critical 90
serverwatch --health-breakdown --disk-path /var
```

The selector is informational and always returns the healthy exit code when the metrics can be collected. Existing overall status and exit-code behavior is unchanged.
