# Health score threshold

The script-friendly `--health-score` selector can optionally enforce a minimum score:

```bash
serverwatch --health-score --fail-under 80
```

The command always prints the numeric score. Without `--fail-under`, it exits with `0` after a successful collection. With `--fail-under`, it returns exit code `2` when the score is strictly below the requested threshold and `0` when the score is equal to or above it.

This is useful in shell scripts and simple monitoring checks where the numeric score should remain visible while the process exit code controls success/failure.

The threshold must be an integer from `0` to `100`.
