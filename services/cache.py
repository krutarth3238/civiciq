import time

_cache = {}
CACHE_TTL = 600  # 10 minutes

def get_cached(key: str):
    """Retrieve a cached value if it hasn't expired."""
    if key in _cache:
        value, timestamp = _cache[key]
        if time.time() - timestamp < CACHE_TTL:
            return value
        # Expired → remove it
        del _cache[key]
    return None

def set_cached(key: str, value):
    """Store a value in the cache with current timestamp."""
    _cache[key] = (value, time.time())

def clear_cache():
    """Clear all cached data."""
    _cache.clear()