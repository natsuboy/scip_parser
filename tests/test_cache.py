"""
Tests for CacheManager and PerformanceMonitor.
"""

import time

from scip_parser.utils.cache import CacheManager, PerformanceMonitor, cached


def test_cache_manager():
    cache = CacheManager()

    # Test set/get
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

    # Test miss
    assert cache.get("key2") is None

    # Test clear
    cache.clear()
    assert cache.get("key1") is None


def test_cached_decorator():
    call_count = 0

    @cached
    def expensive_func(x):
        nonlocal call_count
        call_count += 1
        return x * 2

    # First call
    assert expensive_func(10) == 20
    assert call_count == 1

    # Second call (cached)
    assert expensive_func(10) == 20
    assert call_count == 1  # Should not increment

    # Different arg
    assert expensive_func(20) == 40
    assert call_count == 2


def test_performance_monitor():
    monitor = PerformanceMonitor()

    with monitor.measure("task1"):
        time.sleep(0.01)

    metrics = monitor.get_metrics()
    assert "task1" in metrics
    assert metrics["task1"]["count"] == 1
    assert metrics["task1"]["total_time"] > 0

    # Second run
    with monitor.measure("task1"):
        pass

    metrics = monitor.get_metrics()
    assert metrics["task1"]["count"] == 2
