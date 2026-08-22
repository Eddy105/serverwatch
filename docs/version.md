# Version information

ServerWatch exposes its packaged version through the CLI:

```bash
serverwatch --version
python -m serverwatch --version
```

Both entry points use the same package metadata and print a compact value such as:

```text
serverwatch 0.2.0
```

The command exits with status `0` and does not collect system metrics. This makes it suitable for scripts that need to verify which installed ServerWatch release is being executed.
