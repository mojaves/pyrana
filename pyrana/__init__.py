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


# better explicit than implicit.
# I don't like the black magic at import time.
def setup():
    """
    initialized the underlying libav* libraries.
    you NEED to call this function before to access ANY attribute
    of the pyrana package.
    And this includes constants too.
    """
    from pyrana.common import all_formats, all_codecs
    import pyrana.versions
    import pyrana.ff
    import pyrana.format
    import pyrana.audio
    import pyrana.video
    pyrana.ff.setup()
    pyrana.versions.autoverify()
    # we know all the supported formats/codecs only *after* the
    # registration process. So we must do this wiring here.
    ifmts, ofmts = all_formats()
    pyrana.format.INPUT_FORMATS = frozenset(ifmts)
    pyrana.format.OUTPUT_FORMATS = frozenset(ofmts)
    acl, vcl = all_codecs()
    acods, vcods = frozenset(acl), frozenset(vcl)
    pyrana.audio.INPUT_CODECS = acods
    pyrana.audio.OUTPUT_CODECS = acods
    pyrana.video.INPUT_CODECS = vcods
    pyrana.video.OUTPUT_CODECS = vcods
    

__all__ = ['versions', 'format', 'audio', 'video']
