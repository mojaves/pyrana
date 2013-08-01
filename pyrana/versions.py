#!/usr/bin/env python

from collections import namedtuple
import cffi


def av_version_pack(a, b, c):
    return (a << 16 | b << 8 | c)


def av_version_unpack(v):
    return (v >> 16) & 0xFF, (v >> 8) & 0xFF, (v) & 0xFF


def ffmpeg_versions():
    ver = cffi.FFI()
    ver.cdef("unsigned avcodec_version(void);")
    ver.cdef("unsigned avformat_version(void);")
    ver.cdef("unsigned avutil_version(void);")
    lavc = ver.dlopen("libavcodec.so")
    lavf = ver.dlopen("libavformat.so")
    lavu = ver.dlopen("libavutil.so")
    return (lavc.avcodec_version(),
            lavf.avformat_version(),
            lavu.avutil_version())


def autoverify():
    try:
        lavc, lavf, lavu = ffmpeg_versions()
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

