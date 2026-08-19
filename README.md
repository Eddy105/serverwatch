# ServerWatch

ServerWatch is a lightweight open-source command-line tool for monitoring Linux system resources.

## Features

- CPU, memory, and disk usage monitoring
- Human-readable and JSON output
- Individual metric flags (`--cpu`, `--memory`, `--disk`)
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

Show a single metric:

```bash
serverwatch --cpu
serverwatch --memory
serverwatch --disk
```

Machine-readable output:

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

CPU usage   : 12.4 %
Memory usage: 38.2 %
Disk usage  : 51.7 %

Status: HEALTHY
```

## Exit codes

The full system check returns monitoring-friendly process exit codes:

| Code | Status |
| ---: | --- |
| 0 | HEALTHY |
| 1 | WARNING |
| 2 | CRITICAL |

This makes ServerWatch useful in shell scripts and monitoring automation:

```bash
serverwatch --warning 70 --critical 90
echo $?
```

## Development

Run the test suite with:

```bash
pytest
```

Pull requests are tested automatically with GitHub Actions.

## Releases

Pushing a semantic version tag such as `v0.3.0` triggers the release workflow. It runs the tests, builds wheel and source distributions, and creates a GitHub Release with generated release notes.

## Roadmap

Planned next steps include a package-oriented source layout, configuration files, structured logging, additional metrics, and remote monitoring capabilities.

## License

ServerWatch is released under the MIT License. See `LICENSE`.
