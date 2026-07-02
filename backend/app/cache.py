import time
from functools import wraps


def cache(ttl_seconds):
    """Simple in-memory cache decorator with a TTL."""
    def decorator(fn):
        cached = None
        cached_at = 0.0

        @wraps(fn)
        def wrapper(*args, **kwargs):
            nonlocal cached, cached_at
            now = time.time()
            if cached is None or now - cached_at > ttl_seconds:
                cached = fn(*args, **kwargs)
                cached_at = now
            return cached

        return wrapper

    return decorator
