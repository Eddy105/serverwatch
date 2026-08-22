# Health score breakdown

`get_health_breakdown()` exposes the three components used to calculate the ServerWatch health score.

```python
from serverwatch import get_health_breakdown

breakdown = get_health_breakdown(82.5, 30, 40)
# {"cpu": 50.0, "memory": 100.0, "disk": 100.0}
```

Each component is scored from 0 to 100 using the same warning and critical thresholds as the overall health score:

- at or below the warning threshold: `100`
- at or above the critical threshold: `0`
- between the thresholds: linear interpolation

The overall `get_health_score()` is the rounded arithmetic mean of the three component scores. This breakdown is useful to integrations that need to explain why a host received a particular score without duplicating the scoring logic.
