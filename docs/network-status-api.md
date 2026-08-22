# Network status API

`get_network_status()` returns link state, speed, duplex mode, and MTU for network interfaces.

To inspect all interfaces:

```python
from serverwatch import get_network_status

statuses = get_network_status()
```

To inspect one interface:

```python
status = get_network_status("eth0")
```

The filtered call returns a one-element list with the same structure as the unfiltered result. An unknown interface raises `NetworkInterfaceError`, matching the existing behavior of `get_network_io()`.

The optional filter is intended for integrations that already know which interface they need to monitor. It does not change the existing unfiltered API.
