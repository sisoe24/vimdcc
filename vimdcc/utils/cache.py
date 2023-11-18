from typing import Any, TypeVar, Callable

GenericFunc = Callable[..., Any]

T = TypeVar('T')

_CACHE: dict[GenericFunc, Any] = {}


def cache(func: GenericFunc) -> GenericFunc:
    def wrapper(*args: Any, **kwargs: Any):
        if func not in _CACHE:
            _CACHE[func] = func(*args, **kwargs)
        return _CACHE[func]
    return wrapper


def clear_cache():
    _CACHE.clear()
