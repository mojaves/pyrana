"""
Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg (http://ffmpeg.org)
libraries, but provides an independent API.
"""

from enum import Enum
import platform

from . import formats
from . import packet
from . import audio
from . import video
from . import errors


__version_tuple__ = (0, 5, 2)  # aka the 'Version:'
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
            msg = "CPython < %i.%i not supported" % (major, minor)
            raise RuntimeError(msg)


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
    if formats.InputFormat is None or \
       formats.OutputFormat is None:
        ifmts, ofmts = all_formats()
        formats.InputFormat = Enum('InputFormat', ifmts)
        formats.OutputFormat = Enum('OutputFormat', ofmts)
    if not audio.InputCodec or \
       not audio.OutputCodec or \
       not video.InputCodec or \
       not video.OutputCodec:
        acods, vcods = all_codecs()
        acodecs = Enum('AudioCodec', acods)
        vcodecs = Enum('VideoCodec', vcods)
        audio.InputCodec = acodecs
        audio.OutputCodec = acodecs
        video.InputCodec = vcodecs
        video.OutputCodec = vcodecs


__all__ = ['formats', 'audio', 'video', 'packet', 'errors']
