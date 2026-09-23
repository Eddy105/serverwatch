# CPU details

The `--cpu-details` selector provides a compact CPU snapshot without requiring users to parse the full system overview.

```bash
serverwatch --cpu-details
serverwatch --cpu-details --json
```

The output includes:

- current CPU utilization
- logical CPU count
- physical CPU count
- current, minimum, and maximum frequency when Linux exposes frequency information

Some hosts, virtual machines, or restricted environments do not expose CPU frequency data. In that case the selector reports the frequency as unavailable while still returning the other CPU details.

The selector is informational and returns exit code `0` when the CPU data is collected successfully.
