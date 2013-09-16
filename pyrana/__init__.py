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
from pyrana.packet import TS_NULL
from pyrana.errors import \
    LibraryVersionError, EOSError, NeedFeedError,\
    ProcessingError, SetupError, UnsupportedError,\
    NotFoundError


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
    import pyrana.formats
    import pyrana.audio
    import pyrana.video
    pyrana.ff.setup()
    pyrana.versions.autoverify()
    # we know all the supported formats/codecs only *after* the
    # registration process. So we must do this wiring here.
    if not pyrana.formats.INPUT_FORMATS or \
       not pyrana.formats.OUTPUT_FORMATS:
        ifmts, ofmts = all_formats()
        pyrana.formats.INPUT_FORMATS = frozenset(ifmts)
        pyrana.formats.OUTPUT_FORMATS = frozenset(ofmts)
    if not pyrana.audio.INPUT_CODECS or \
       not pyrana.audio.OUTPUT_CODECS or \
       not pyrana.video.INPUT_CODECS or \
       not pyrana.video.OUTPUT_CODECS:
        acl, vcl = all_codecs()
        acods, vcods = frozenset(acl), frozenset(vcl)
        pyrana.audio.INPUT_CODECS = acods
        pyrana.audio.OUTPUT_CODECS = acods
        pyrana.video.INPUT_CODECS = vcods
        pyrana.video.OUTPUT_CODECS = vcods


__all__ = ['versions', 'formats', 'audio', 'video', 'packet', 'errors']
