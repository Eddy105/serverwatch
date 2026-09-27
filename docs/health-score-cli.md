# Health score CLI

Use `--health-score` for a machine-friendly numeric health value.

```bash
serverwatch --health-score
serverwatch --health-score --json
```

Use `--fail-under` as a monitoring gate. The score is still printed; exit code 2 is returned when the score is below the requested threshold.

```bash
serverwatch --health-score --fail-under 80
serverwatch --health-score --json --fail-under 80
```

The threshold must be an integer from 0 to 100 and requires `--health-score`.
