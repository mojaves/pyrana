import platform
try:
    import cffi
except ImportError:
    raise RuntimeError("you need cffi for pyrana")


if platform.python_implementation() == 'CPython':
    if platform.python_version_tuple() < ('3','2'):
        raise RuntimeError("CPython < 3.2 not supported")

__all__ = ['versions']

