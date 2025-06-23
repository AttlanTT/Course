from functools import wraps

def memoize(max_size=None):
    cache = {}

    def decorator(func):
        @wraps(func)
        def wrapper(*args):
            if args in cache:
                return cache[args]
            result = func(*args)
            cache[args] = result
            if max_size and len(cache) > max_size:
                cache.pop(next(iter(cache)))
            return result
        return wrapper
    return decorator
