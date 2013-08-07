"""
Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg (http://ffmpeg.org)
libraries, but provides an independent API.
"""

import platform

if platform.python_implementation() == 'CPython':
    if platform.python_version_tuple() < ('3', '2'):
        raise RuntimeError("CPython < 3.2 not supported")


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
    pyrana.versions.autoverify()
    ff = pyrana.ff.FF()
    ff.lavc.avcodec_register_all()
    ff.lavf.av_register_all()
    ifmts, ofmts = _formats(ff)
    pyrana.format.INPUT_FORMATS = frozenset(ifmts)
    pyrana.format.OUTPUT_FORMATS = frozenset(ofmts)


__all__ = ['versions', 'format']
