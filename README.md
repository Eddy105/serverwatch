# ServerWatch

ServerWatch is a lightweight open-source command-line tool for monitoring Linux system resources.

## Features

- CPU, memory, swap, disk, and process count monitoring
- Filesystem-aware disk checks for arbitrary paths and mount points
- Host, kernel, architecture, and CPU information
- System uptime and load averages
- Network I/O counters
- Human-readable and JSON output
- Individual metric selectors
- Focused health-status output for scripts and monitoring checks
- Configurable warning and critical thresholds
- Monitoring-friendly exit codes
- Automated tests with GitHub Actions
- Automated GitHub releases for version tags

## Requirements

- Linux
- Python 3.10 or newer

## Installation

Clone the repository:

```bash
git clone git@github.com:Eddy105/serverwatch.git
cd serverwatch
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install ServerWatch:

```bash
pip install -e .
```

For development and testing:

```bash
pip install -e '.[dev]'
```

## Usage

Run the default system overview:

```bash
serverwatch
```

Show a single metric or information group:

```bash
serverwatch --cpu
serverwatch --memory
serverwatch --swap
serverwatch --disk
serverwatch --processes
serverwatch --system
serverwatch --uptime
serverwatch --load
serverwatch --network
```

Return only the current health state while preserving monitoring exit codes:

```bash
serverwatch --status
serverwatch --status --json
```

`--status` evaluates the same CPU, memory, and disk thresholds as the full system check. It prints only `HEALTHY`, `WARNING`, or `CRITICAL` and exits with code `0`, `1`, or `2` respectively. Custom thresholds and disk paths still apply:

```bash
serverwatch --status --disk-path /var --warning 70 --critical 90
```

Process count is informational and is available in both human-readable and JSON output:

```bash
serverwatch --processes
serverwatch --processes --json
```

Swap output includes utilization plus used and total bytes:

```bash
serverwatch --swap
serverwatch --swap --json
```

Monitor a specific filesystem path or mount point instead of `/`:

```bash
serverwatch --disk --disk-path /var
serverwatch --disk-path /srv --warning 80 --critical 90
```

The selected disk path is also included in JSON output:

```bash
serverwatch --disk --disk-path /home --json
```

All selectors support machine-readable JSON output:

```bash
serverwatch --network --json
serverwatch --system --json
```

Output the complete system overview as JSON:

```bash
serverwatch --json
```

Use custom health thresholds:

```bash
serverwatch --warning 70 --critical 85
```

Show all options:

```bash
serverwatch --help
```

Example output:

```text
SERVERWATCH
----------------------------
Host:         server01
Kernel:       6.8.0-79-generic
Uptime:       12d 4h 31m
Processes:    214

CPU usage   : 12.4 %
Memory usage: 38.2 %
Swap usage  : 4.6 %
Disk usage (/): 51.7 %
Load average: 0.42 0.38 0.31
Network RX:   24813921 bytes
Network TX:   10452890 bytes

Status: HEALTHY
```

## Exit codes

The full system check and `--status` return monitoring-friendly process exit codes:

| Code | Status |
| ---: | --- |
| 0 | HEALTHY |
| 1 | WARNING |
| 2 | CRITICAL |

Single-metric selectors return `0` when the metric was collected successfully. Swap usage and process count are currently informational and do not change the full health status. An unreadable disk path exits with an error instead of silently checking a different filesystem.

This makes ServerWatch useful in shell scripts and monitoring automation:

```bash
serverwatch --status --disk-path /var --warning 70 --critical 90
echo $?
```

## Development

Run the test suite with:

```bash
pytest
```

Pull requests are tested automatically with GitHub Actions. The quality workflow enforces Ruff linting and formatting plus a minimum test coverage of 80%.

## Releases

Pushing a semantic version tag such as `v0.3.0` triggers the release workflow. It runs the tests, builds wheel and source distributions, and creates a GitHub Release with generated release notes.

## Roadmap

Planned next steps include configuration files, structured logging, richer filesystem reporting, and remote monitoring capabilities.

## License

ServerWatch is released under the MIT License. See `LICENSE`.
