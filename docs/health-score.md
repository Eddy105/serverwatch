# Health score

ServerWatch exposes a deterministic health score from 0 to 100 in the full system output and JSON output.

The score combines CPU, memory, and disk usage with equal weighting. Each metric contributes:

- `100` points when usage is at or below the warning threshold
- `0` points when usage is at or above the critical threshold
- a linear value between those thresholds

The three metric scores are averaged and rounded to the nearest integer.

For example, with the default thresholds of 75% warning and 90% critical, CPU at 82.5%, memory at 30%, and disk at 40% produces a score of `83/100`.

The health score is informational. Existing `HEALTHY`, `WARNING`, and `CRITICAL` status values and exit codes remain authoritative for automation.
