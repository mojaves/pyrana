"""
CFFI frontend code for pyrana.
This module is not part of the pyrana public API.
"""

from functools import wraps
import ctypes
import os
import os.path
import glob
import cffi
from .errors import LibraryVersionError

# we leverage ctypes for the bootstrap of CFFI.
# TODO: explain


# The dreaded singleton. It is a necessary evil[1] and this is the reason why:
# bitbucket.org/cffi/cffi/issue/4/typeerror-initializer-for-ctype-double

# http://wiki.python.org/moin/PythonDecoratorLibrary#Singleton
def singleton(cls):
    """Use class as singleton."""

    cls.__new_original__ = staticmethod(cls.__new__)

    @wraps(cls.__new__)
    def singleton_new(cls, *args, **kw):
        """the singleton workhorse."""

        _it = cls.__dict__.get('__it__')
        if _it is not None:
            return _it

        _it = cls.__new_original__(cls, *args, **kw)
        cls.__it__ = _it
        _it.__init_original__(*args, **kw)
        return _it

    cls.__new__ = staticmethod(singleton_new)
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__

    return cls


def av_version_unpack(version):
    """
    unpack a version integer into a tuple (of integers).
    """
    return (version >> 16) & 0xFF, (version >> 8) & 0xFF, (version) & 0xFF


def _gather(names):
    """load all the pyrana pseudo-headers."""
    hfiles = []
    for name in names:
        hfiles.extend(glob.glob(name))
    data = []
    for hfile in hfiles:
        data.append('/*** HFile: %s ***/\n\n' % hfile)
        with open(hfile) as src:
            data.append(src.read())
    return ''.join(data)


class HLoader(object):
    """
    Finds and loads the HFiles describing the FFMpeg libraries,
    given their versions.
    """

    def _hpath(self, name):
        """
        builds the complete relative path for the given pseudoheader.
        """
        return os.path.join(self._root, self._path, name)

    @property
    def hfiles(self):
        """
        print the name of the hfiles required by
        the corrisponding system FFMpeg libraries.
        """
        return self._find(self._vers)

    @property
    def decls(self):
        """
        return a string containing all the decls found
        in the gathered hfiles, in the correct order.
        """
        return _gather(self.hfiles)

    def _find(self, vertuples):
        """
        find the most suitable (nearest compatible to the available
        major version) pseudo headers and returns them as list.
        """
        libs = [ 'avutil', 'avcodec', 'avformat', 'swscale', 'swresample' ]
        hnames = []
        for name, (major, minor, micro) in zip(libs, vertuples):
            hfile = self._hpath('%s%i.h' % (name, major))
            if os.access(hfile, os.R_OK):
                hnames.append(hfile)
            else:
                msg = 'missing hfile for %s %i.%i.%i' \
                      % (name, major, minor, micro)
                raise LibraryVersionError(msg)
        return hnames

    def __init__(self, vers, path="hfiles"):
        self._root = os.path.abspath(os.path.dirname(__file__))
        self._path = path
        self._vers = vers


def versions():
    """
    fetch the version of the FFMpeg libraries.
    """
    lavu = ctypes.CDLL('libavutil.so')
    lavc = ctypes.CDLL('libavcodec.so')
    lavf = ctypes.CDLL('libavformat.so')
    sws = ctypes.CDLL('libswscale.so')
    swr = ctypes.CDLL('libswresample.so')
    return [ av_version_unpack(v)
             for v in (lavu.avutil_version(),
                       lavc.avcodec_version(),
                       lavf.avformat_version(),
                       sws.swscale_version(),
                       swr.swresample_version()) ]


@singleton
class FF(object):
    """
    FFMpeg abstraction objects.
    Needs to be a singleton because the FFI instance has to be
    one and exactly one.
    Do not use directly. Use get_handle() instead.
    """

    def __init__(self):
        # beware of singleton before to add parameters here
        self._vers = versions()
        _hl = HLoader(self._vers)
        self.ffi = cffi.FFI()
        self.ffi.cdef(_hl.decls)
        self.lavc = self.ffi.dlopen("avcodec")
        self.lavf = self.ffi.dlopen("avformat")
        self.lavu = self.ffi.dlopen("avutil")
        self.sws = self.ffi.dlopen("swscale")
        self.swr = self.ffi.dlopen("swresample")

    def setup(self):
        """
        initialize the FFMpeg libraries.
        """
        # note: libav* already protects against multiple calls.
        self.lavc.avcodec_register_all()
        self.lavf.av_register_all()
        return self.versions()

    def versions(self):
        """
        fetch the version of the FFMpeg libraries.
        """
        return self._vers


def get_handle():
    """
    return a FF instance, taking care of bookkeeping.
    Safe to call multiple times.
    Do not instantiate FF directly.
    """
    return FF()


def setup():
    """
    return an already-setup ready-to-go FF instance.
    Safe to call multiple times.
    Do not instantiate FF directly.
    """
    ffh = FF()
    ffh.setup()
    return ffh
