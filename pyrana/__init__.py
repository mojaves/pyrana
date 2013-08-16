"""
Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg (http://ffmpeg.org)
libraries, but provides an independent API.
"""

import platform

def _enforce_platform(plat):
    """
    enforce the platform conformancy.
    we don't support python 2.7 (yet?) so we want to be
    really sure and surely loud about the fact we think
    is not going to work.
    """
    if plat.python_implementation() == 'CPython':
        if plat.python_version_tuple() < ('3', '2'):
            raise RuntimeError("CPython < 3.2 not supported")


_enforce_platform(platform)


# backward compatibility
from pyrana.format import TS_NULL
# meh.
from pyrana.errors import *


def setup():
    """
    initialized the underlying libav* libraries.
    you NEED to call this function before to access ANY attribute
    of the pyrana package.
    And this includes constants too.
    """
    import pyrana.format
    import pyrana.versions
    pyrana.versions.autoverify()
    pyrana.ff.setup()
    ifmts, ofmts = pyrana.format.all_formats()
    pyrana.format.INPUT_FORMATS = frozenset(ifmts)
    pyrana.format.OUTPUT_FORMATS = frozenset(ofmts)


__all__ = ['versions', 'format', 'audio', 'video']
