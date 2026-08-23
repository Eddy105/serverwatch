# Health score fail-under threshold

Use `--fail-under` with `--health-score` when automation should fail if the numeric health score is below a required minimum.

```bash
serverwatch --health-score --fail-under 80
serverwatch --health-score --json --fail-under 80
```

The score is still printed. A score below the threshold returns exit code `2`; a score equal to or above it returns `0`.

The threshold must be between 0 and 100. This option does not change the normal health-status calculation or the exit codes of the full system check.
