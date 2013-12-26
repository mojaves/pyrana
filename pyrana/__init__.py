"""
Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg (http://ffmpeg.org)
libraries, but provides an independent API.
"""

import platform

from . import formats
from . import packet
from . import audio
from . import video
from . import errors


__version_tuple__ = (0, 2, 90)  # aka the 'Version:'
__version__ = '.'.join(str(ver) for ver in __version_tuple__)


def _enforce_platform(plat):
    """
    enforce the platform conformancy.
    we don't support python 2.7 (yet?) so we want to be
    really sure and surely loud about the fact we think
    is not going to work.
    """
    if plat.python_implementation() == 'CPython':
        ver = plat.python_version_tuple()
        major, minor = int(ver[0]), int(ver[1])
        fail = False
        if major == 3 and minor < 3:
            fail = True
        elif major == 2 and minor < 7:
            fail = True
        if fail:
            raise RuntimeError("CPython < %i.%i not supported" % (major, minor))


_enforce_platform(platform)


# backward compatibility
from .packet import TS_NULL
from .errors import \
    LibraryVersionError, EOSError, NeedFeedError,\
    ProcessingError, SetupError, UnsupportedError,\
    NotFoundError
from .common import blob


# better explicit than implicit.
# I don't like the black magic at import time.
def setup():
    """
    initialized the underlying libav* libraries.
    you NEED to call this function before to access ANY attribute
    of the pyrana package.
    And this includes constants too.
    """
    from .common import all_formats, all_codecs
    from . import ff
    ff.setup()
    # we know all the supported formats/codecs only *after* the
    # registration process. So we must do this wiring here.
    if not formats.INPUT_FORMATS or \
       not formats.OUTPUT_FORMATS:
        ifmts, ofmts = all_formats()
        formats.INPUT_FORMATS = frozenset(ifmts)
        formats.OUTPUT_FORMATS = frozenset(ofmts)
    if not audio.INPUT_CODECS or \
       not audio.OUTPUT_CODECS or \
       not video.INPUT_CODECS or \
       not video.OUTPUT_CODECS:
        acl, vcl = all_codecs()
        acods, vcods = frozenset(acl), frozenset(vcl)
        audio.INPUT_CODECS = acods
        audio.OUTPUT_CODECS = acods
        video.INPUT_CODECS = vcods
        video.OUTPUT_CODECS = vcods


__all__ = ['formats', 'audio', 'video', 'packet', 'errors']
