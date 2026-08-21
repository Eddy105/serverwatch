# ServerWatch

ServerWatch is a lightweight open-source command-line tool for monitoring Linux system resources.

## Features

- CPU, memory, swap, disk, and process count monitoring
- Filesystem-aware disk and inode checks for arbitrary paths and mount points
- Mounted filesystem overview with capacity and usage details
- Aggregate disk I/O counters for read/write activity
- Hardware temperature sensor reporting when supported by the host
- Host, kernel, architecture, and CPU information
- System uptime and load averages
- Aggregate and per-interface network I/O counters
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
serverwatch --filesystems
serverwatch --inodes
serverwatch --disk-io
serverwatch --temperatures
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

Inspect all mounted physical filesystems in one view:

```bash
serverwatch --filesystems
serverwatch --filesystems --json
```

Filesystem output reports device, mount point, filesystem type, total bytes, used bytes, free bytes, and percentage utilization. Mounts that cannot be read are skipped rather than causing the complete overview to fail. This selector is informational and does not change the CPU/memory/disk health status.

Inspect inode consumption for a filesystem path or mount point:

```bash
serverwatch --inodes
serverwatch --inodes --disk-path /var
serverwatch --inodes --disk-path /srv --json
```

Inode output reports total, used, free, and percentage utilization. This is useful when a filesystem contains very large numbers of small files: available byte capacity can remain healthy while no new files can be created because the inode pool is exhausted. Inode usage is currently informational and does not change the CPU/memory/disk health status.

Inspect aggregate disk read/write activity since boot:

```bash
serverwatch --disk-io
serverwatch --disk-io --json
```

Disk I/O output reports aggregate read/write byte totals and operation counts. These counters are informational and do not change the CPU/memory/disk health status.

Inspect hardware temperature sensors exposed by Linux:

```bash
serverwatch --temperatures
serverwatch --temperatures --json
```

Temperature output includes the sensor chip, label, current temperature, and any high or critical limits exposed by the kernel. Some virtual machines, containers, and physical hosts do not expose temperature sensors; in that case ServerWatch exits with a clear error instead of returning an empty result. Temperature readings are currently informational and do not change the CPU/memory/disk health status.

Inspect aggregate network traffic or a specific Linux network interface:

```bash
serverwatch --network
serverwatch --network --network-interface eth0
serverwatch --network --network-interface enp3s0 --json
```

`--network-interface` is intentionally tied to the `--network` selector. Unknown interface names fail with a clear error instead of silently returning aggregate counters. JSON output includes the selected interface name.

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

Single-metric selectors return `0` when the metric was collected successfully. Swap usage, process count, filesystem overview, inode usage, disk I/O counters, and temperature readings are currently informational and do not change the full health status. An unreadable disk path, unavailable disk I/O counters or temperature sensors, or unknown requested network interface exits with an error instead of silently checking a different resource.

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
