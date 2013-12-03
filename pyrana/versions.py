#!/usr/bin/env python

"""
the versions module provides the runtime verification
routines to ensure that pyrana will run smoothly in
the current environment.
DO NOT USE at your own risk! :)
"""

from .errors import LibraryVersionError
from .ff import get_handle, av_version_pack, av_version_unpack


def autoverify(ffh=None):
    """
    verifies the environment.
    If everything is fine, just returns the (packed) versions of the
    libraries needed by pyrana.
    Otherwise raises LibraryVersionError.
    """
    if ffh is None:
        ffh = ff.get_handle()
    try:
        lavc, lavf, lavu = ffh.versions()
        sws, swr = ffh.aux_versions()
    except OSError:
        raise LibraryVersionError("missing libraries")
    if lavc < av_version_pack(54, 0, 0):
        raise LibraryVersionError("unsupported libavcodec")
    if lavc >= av_version_pack(55, 0, 0):
        raise LibraryVersionError("unsupported libavcodec")
    if lavf < av_version_pack(54, 0, 0):
        raise LibraryVersionError("unsupported libavformat")
    if lavu < av_version_pack(52, 0, 0):
        raise LibraryVersionError("unsupported libavutil")
    if sws < av_version_pack(2, 0, 0):
        raise LibraryVersionError("unsupported swscale")
    if swr < av_version_pack(0, 1, 0):
        raise LibraryVersionError("unsupported swscale")
    return (av_version_unpack(lavc),
            av_version_unpack(lavf),
            av_version_unpack(lavu))
