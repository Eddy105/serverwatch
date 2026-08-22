# Network status CLI filtering

ServerWatch can limit network interface status output to one interface.

Human-readable output:

```bash
serverwatch --network-status --network-interface eth0
```

For automation:

```bash
serverwatch --network-status --network-interface eth0 --json
```

The existing `--network-interface` option for `--network` remains unchanged. An interface filter without either `--network` or `--network-status` is rejected.

If the requested interface does not exist, ServerWatch returns an error instead of silently returning an empty result.
