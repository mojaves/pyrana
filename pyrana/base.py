"""
Common definitions, exception hierarchy, utiliy
and initialization functions which doesn't
fit elsewhere. Should NOT be used directly
by the external code.
"""

import cffi
import pyrana.versions
import pyrana.format


class PyranaError(Exception):
    """
    Root of the pyrana error tree.
    """
    pass


class EOSError(PyranaError):
    """
    End Of Stream
    """
    pass


class NeedFeedError(PyranaError):
    """
    More data is needed
    """
    pass


class ProcessingError(PyranaError):
    """
    Runtime processing error
    """
    pass


class SetupError(PyranaError):
    """
    Error while setting up a pyrana object
    """
    pass


class UnsupportedError(PyranaError):
    """
    Requested an unsupported feature.
    """
    pass


def _fmt_names(ffi, format_next):
    """
    generator. Produces the names as strings
    of all the format supported by libavformat.
    """
    fmt = format_next(ffi.NULL)
    while fmt != ffi.NULL:
        name = ffi.string(fmt.name)
        yield name.decode('utf-8')
        fmt = format_next(fmt)
    raise StopIteration


def _formats():
    """
    builds the sets of the formats supported by
    libavformat, and which, in turn, by pyrana.
    """
    ffi = cffi.FFI()
    ffi.cdef("""
            typedef struct AVInputFormat {
                const char *name;
            } AVInputFormat;
            typedef struct AVOutputFormat {
                const char *name;
            } AVOutputFormat;
            AVInputFormat *av_iformat_next(AVInputFormat *F);
            AVOutputFormat *av_oformat_next(AVOutputFormat *F);
            """)
    avf = ffi.dlopen("avformat")
    return ([x for x in _fmt_names(ffi, avf.av_iformat_next)],
            [x for x in _fmt_names(ffi, avf.av_oformat_next)])


def setup():
    """
    initialized the underlying libav* libraries.
    you NEED to call this function before to access ANY attribute
    of the pyrana package.
    And this includes constants too.
    """
    pyrana.versions.autoverify()
    ver = cffi.FFI()
    ver.cdef("void av_register_all(void);")
    ver.cdef("void avcodec_register_all(void);")
    lavc = ver.dlopen("avcodec")
    lavf = ver.dlopen("avformat")
    lavc.avcodec_register_all()
    lavf.av_register_all()
    ifmts, ofmts = _formats()
    pyrana.format.INPUT_FORMATS = frozenset(ifmts)
    pyrana.format.OUTPUT_FORMATS = frozenset(ofmts)
