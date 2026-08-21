# Process details

The existing process selector can show a bounded list of the most resource-intensive processes:

```bash
serverwatch --processes --sort cpu
serverwatch --processes --sort memory --top 5
serverwatch --processes --sort cpu --top 10 --json
```

The output includes:

- PID
- user
- process name
- CPU percentage
- memory percentage
- command line

`--processes` without `--sort` keeps the original informational process-count behavior.

CPU usage is sampled over a short interval before sorting. Processes that disappear or deny access while being collected are skipped instead of failing the complete command.

This selector is informational and does not change the CPU/memory/disk health status or monitoring exit code.
