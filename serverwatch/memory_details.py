"""Reusable detailed memory metrics."""

import psutil


def get_memory_details():
    """Return total, used, available, free, and utilization for RAM."""
    memory = psutil.virtual_memory()
    return {
        "total": memory.total,
        "used": memory.used,
        "available": memory.available,
        "free": memory.free,
        "percent": memory.percent,
    }
