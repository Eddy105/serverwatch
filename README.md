# ServerWatch

ServerWatch is a lightweight open-source command-line tool for monitoring Linux system resources.

## Features

- CPU, memory, and disk usage monitoring
- Human-readable and JSON output
- Individual metric flags (`--cpu`, `--memory`, `--disk`)
- Configurable warning and critical thresholds
- Automated tests for status logic

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

## Development

Run the test suite with:

```bash
pytest
```

## Roadmap

Planned next steps include CI with GitHub Actions, structured logging, configuration files, and improved packaging/release automation.

## License

A license will be added before the first public release.
