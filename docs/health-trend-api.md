# Health score trend API

The `get_health_trend()` function compares two health-score measurements without duplicating score calculations.

```python
from serverwatch.health_trend import get_health_trend

get_health_trend(82, 75)
# {'current': 82, 'previous': 75, 'delta': 7, 'direction': 'improving'}
```

The direction is `improving`, `degrading`, or `stable`. Both scores must be between 0 and 100.
