# Swap details

The `--swap-details` selector provides current swap capacity, utilization, and paging activity:

```bash
serverwatch --swap-details
serverwatch --swap-details --json
```

Human-readable output includes total, used, free, percentage utilization, bytes swapped in, and bytes swapped out. JSON output exposes the same values under `swap_details`.

The selector is informational and returns exit code `0` when swap information is collected successfully. It does not change the existing `--swap` metric or the CPU/memory/disk health score.
