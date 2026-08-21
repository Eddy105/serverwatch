# Network interface status

ServerWatch can report the operational state of every network interface exposed by the operating system:

```bash
serverwatch --network-status
serverwatch --network-status --json
```

The check reports:

- interface name
- whether the interface is currently up
- reported link speed in Mbps
- MTU

Example:

```text
eth0: UP 1000 Mbps, MTU 1500
lo: UP 0 Mbps, MTU 65536
```

This is an informational check. It does not change the overall CPU/memory/disk health status or monitoring exit code. It is useful for quickly distinguishing a running system from a host whose network interface is down.

The exact link speed may be reported as `0` by virtual interfaces or operating systems that do not expose a physical link speed.
