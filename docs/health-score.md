# Health score

ServerWatch reports a transparent health score from 0 to 100 in the default overview and in JSON output.

The score uses CPU, memory, and disk usage with equal weighting. Each metric contributes:

- `100` points while usage is below the warning threshold
- `0` points at or above the critical threshold
- a linear score between those thresholds

The final score is the rounded arithmetic mean of the three metric scores.

For example, with warning `75` and critical `90`:

```text
CPU     82.5 %
Memory  30 %
Disk    40 %

Health score: 83/100
```

The score does not replace the existing `HEALTHY`, `WARNING`, and `CRITICAL` states or their exit codes. Those states continue to use the highest CPU, memory, or disk usage against the configured thresholds.

The score is also included in `serverwatch --status --json` for automation.
