# Memory details API

`serverwatch.memory_details.get_memory_details()` provides a reusable snapshot of RAM capacity and utilization.

```python
from serverwatch.memory_details import get_memory_details

memory = get_memory_details()
```

The returned mapping contains:

- `total`: total physical memory in bytes
- `used`: memory currently used in bytes
- `available`: memory available without swapping in bytes
- `free`: currently unused memory in bytes
- `percent`: memory utilization percentage

This API is useful for integrations that need detailed memory data without parsing CLI output.
