# Health score

ServerWatch reports a 0-100 health score in the default system overview and JSON output.

The score is calculated from CPU, memory, and disk usage using the configured warning and critical thresholds.

For each metric:

- below the warning threshold: 100 points
- at or above the critical threshold: 0 points
- between the thresholds: a linear score between 100 and 0

The final score is the rounded arithmetic mean of the three metric scores.

This calculation is deterministic and does not change the existing `HEALTHY`, `WARNING`, or `CRITICAL` status or exit codes.

Example:

```text
Health score: 92/100
Status: HEALTHY
```

JSON includes the same value:

```json
{
  "status": "HEALTHY",
  "health_score": 92
}
```
