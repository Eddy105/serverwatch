# Normalized load averages

The `--load --json` selector now includes the logical CPU count and load averages normalized per logical CPU.

Example fields:

```json
{
  "load_average": {
    "1m": 4.0,
    "5m": 2.0,
    "15m": 1.0,
    "cpu_count": 4,
    "per_cpu_1m": 1.0,
    "per_cpu_5m": 0.5,
    "per_cpu_15m": 0.25
  }
}
```

The existing human-readable `--load` output remains unchanged. The normalized values make JSON output easier to compare across machines with different CPU counts without changing the existing load-average values.
