#!/usr/bin/env python

"""
the versions module provides the runtime verification
routines to ensure that pyrana will run smoothly in
the current environment.
DO NOT USE at your own risk! :)
"""

import pyrana.ff


def av_version_pack(major, minor, micro):
    """
    return the version as packed integer
    """
    return (major << 16 | minor << 8 | micro)


def av_version_unpack(version):
    """
    unpack a version integer into a tuple (of integers).
    """
    return (version >> 16) & 0xFF, (version >> 8) & 0xFF, (version) & 0xFF


def autoverify():
    """
    verifies the environment.
    If everything is fine, just returns the (packed) versions of the
    libraries needed by pyrana.
    Otherwise raises RuntimeError.
    """
    ff = pyrana.ff.FF()
    try:
        lavc, lavf, lavu = ff.versions()
    except OSError:
        raise RuntimeError("missing libraries")
    if lavc < av_version_pack(54, 0, 0):
        raise RuntimeError("unsupported libavcodec: found=%u required=%u")
    if lavf < av_version_pack(54, 0, 0):
        raise RuntimeError("unsupported libavformat (too old")
    if lavu < av_version_pack(52, 0, 0):
        raise RuntimeError("unsupported libavutil (too old")
    return (av_version_unpack(lavc),
            av_version_unpack(lavf),
            av_version_unpack(lavu))
