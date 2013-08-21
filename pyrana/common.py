"""
common code which do not fits better elsewhere.
You should not use this directly.
"""
from enum import IntEnum

import pyrana.ff


class MediaType(IntEnum):
    AVMEDIA_TYPE_UNKNOWN = -1
    AVMEDIA_TYPE_VIDEO = 0
    AVMEDIA_TYPE_AUDIO = 1
    AVMEDIA_TYPE_DATA = 2
    AVMEDIA_TYPE_SUBTITLE = 3
    AVMEDIA_TYPE_ATTACHMENT = 4
    AVMEDIA_TYPE_NB = 5


def _iter_fmts(ffi, format_next):
    """
    generator. Produces the names as strings
    of all the format supported by libavformat.
    """
    fmt = format_next(ffi.NULL)
    while fmt != ffi.NULL:
        name = ffi.string(fmt.name)
        yield name.decode('utf-8'), fmt
        fmt = format_next(fmt)


def find_format_by_name(name, next_fmt):
    ffh = pyrana.ff.get_handle()
    for fname, fdesc in _iter_fmts(ffh.ffi, next_fmt):
        if name == fname:
            return fdesc
    raise pyrana.errors.UnsupportedError


def _iter_codec(ffi, codec_next):
    rmap = dict(enumerate(MediaType, -1))  # WARNING!
    codec = codec_next(ffi.NULL)
    while codec != ffi.NULL:
        name = ffi.string(codec.name)
        _type = rmap.get(codec.type, MediaType.AVMEDIA_TYPE_UNKNOWN)
        yield (name.decode('utf-8'), _type, codec)
        codec = codec_next(codec)


def all_formats():
    """
    builds the sets of the formats supported by
    libavformat, and which, in turn, by pyrana.
    """
    ffh = pyrana.ff.get_handle()
    next_in = ffh.lavf.av_iformat_next
    next_out = ffh.lavf.av_oformat_next
    return ([x for x, _ in _iter_fmts(ffh.ffi, next_in)],
            [x for x, _ in _iter_fmts(ffh.ffi, next_out)])


def all_codecs():
    ffh = pyrana.ff.get_handle()
    audio, video = [], []
    for name, _type, _ in _iter_codec(ffh.ffi, ffh.lavc.av_codec_next):
        if _type == MediaType.AVMEDIA_TYPE_AUDIO:
            audio.append(name)
        elif _type == MediaType.AVMEDIA_TYPE_VIDEO:
            video.append(name)
    return audio, video
