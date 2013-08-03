"""
Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg (http://ffmpeg.org)
libraries, but provides an independent API.
"""

import platform
try:
    import cffi
except ImportError:
    raise RuntimeError("you need cffi for pyrana")


if platform.python_implementation() == 'CPython':
    if platform.python_version_tuple() < ('3', '2'):
        raise RuntimeError("CPython < 3.2 not supported")

# backward compatibility
from pyrana.base import *

__all__ = ['versions', 'format']
