# Memory details

The `--memory-details` selector provides the current memory capacity and utilization without requiring the full system overview:

```bash
serverwatch --memory-details
serverwatch --memory-details --json
```

Human-readable output includes total, used, available, free, and percentage utilization. JSON output exposes the same values under `memory_details`.

The selector is informational and returns exit code `0` when memory information is collected successfully. It does not change the existing `--memory` metric or the health score calculation.
