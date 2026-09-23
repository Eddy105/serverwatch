# Load details CLI

Use `--load-details` to inspect the system load averages together with the logical CPU count and load normalized per logical CPU.

```text
$ serverwatch --load-details
Load average: 4.00 2.00 1.00
CPU count:    4
Per-CPU load: 1.00 0.50 0.25
```

Use `--load-details --json` for machine-readable output. The selector reuses the same load-average data as `--load --json` and does not change the existing `--load` output.
