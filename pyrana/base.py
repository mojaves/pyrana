
import cffi
import pyrana.versions
import pyrana.format


class PyranaError(Exception):
    pass


class EOSError(PyranaError):
    "End Of Stream"
    pass


class NeedFeedError(PyranaError):
    "More data is needed"
    pass


class ProcessingError(PyranaError):
    pass


class SetupError(PyranaError):
    pass


class UnsupportedError(PyranaError):
    pass


def _collect_formats(ffi, format_next):
    fmt = format_next(ffi.NULL)
    res = []
    while fmt != ffi.NULL:
        name = ffi.string(fmt.name)
        res.append(name.decode('utf-8'))
        fmt = format_next(fmt)
    return res


def _formats():
    ffi = cffi.FFI()
    ffi.cdef(
"""
typedef struct AVInputFormat {
const char *name;
} AVInputFormat;
typedef struct AVOutputFormat {
const char *name;
} AVOutputFormat;
AVInputFormat *av_iformat_next(AVInputFormat *F);
AVOutputFormat *av_oformat_next(AVOutputFormat *F);
""")
    lavf = ffi.dlopen("avformat")
    return (_collect_formats(ffi, lavf.av_iformat_next),
            _collect_formats(ffi, lavf.av_oformat_next))


def setup():
    pyrana.versions.autoverify()
    ver = cffi.FFI()
    ver.cdef("void av_register_all(void);")
    ver.cdef("void avcodec_register_all(void);")
    lavc = ver.dlopen("avcodec")
    lavf = ver.dlopen("avformat")
    lavc.avcodec_register_all()
    lavf.av_register_all();
    ifmts, ofmts = _formats() 
    pyrana.format.input_formats = frozenset(ifmts)
    pyrana.format.output_formats = frozenset(ofmts)
