"""
CFFI frontend code for pyrana.
This module is not part of the pyrana public API.
"""

from functools import wraps
import os
import os.path
import glob
import cffi
from .errors import SetupError


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


@singleton
class FF(object):
    """
    FFMpeg abstraction objects.
    Needs to be a singleton because the FFI instance has to be
    one and exactly one.
    Do not use directly. Use get_handle() instead.
    """

    def _hpath(self, name):
        """
        builds the complete relative path for the given pseudoheader.
        """
        return os.path.join(self._root, self._path, name)

    def _find(self):
        """
        find the most suitable (nearest compatible to the available
        major version) pseudo headers and returns them as list.
        """
        lavc, lavf, lavu = self.versions()
        # we need reordering. lavu must be loaded first.
        libs = [ 'avutil', 'avcodec', 'avformat', 'swscale', 'swresample' ]
        vers = zip(libs,
                   [ av_version_unpack(v)[0] for v in
                     ( lavu, lavc, lavf ) + self.aux_versions() ])
        hnames = []
        for name, major in vers:
            found = False
            hfiles = ('%s%i.h' % (name, major), '%s.h' % (name))
            for cand in hfiles:
                hfile = self._hpath(cand)
                if os.access(hfile, os.R_OK):
                    found = True
                    break
            if found:
                hnames.append(hfile)
            else:
                raise SetupError('missing hfile for %s %i' % (name, major))
        return hnames

    def __init__(self, path="hfiles"):
        self._root = os.path.abspath(os.path.dirname(__file__))
        self._path = path
        self.ffi = cffi.FFI()
        # step 1: gather the versions of the FFmpeg libraries
        self.ffi.cdef(self._gather([self._hpath("_version.h")]))
        self.lavc = self.ffi.dlopen("avcodec")
        self.lavf = self.ffi.dlopen("avformat")
        self.lavu = self.ffi.dlopen("avutil")
        self.sws = self.ffi.dlopen("swscale")
        self.swr = self.ffi.dlopen("swresample")
        # step 2: load the best hfiles
        hfiles = self._find()
        self.ffi.cdef(self._gather(hfiles))

    def _gather(self, names):
        """load all the pyrana pseudo-headers."""
        hfiles = []
        for name in names:
            hfiles.extend(glob.glob(name))
        data = []
        for hfile in hfiles:
            with open(hfile) as src:
                data.append(src.read())
        return ''.join(data)

    def setup(self):
        """
        initialize the FFMpeg libraries.
        """
        # libav* already protects against multiple calls.
        self.lavc.avcodec_register_all()
        self.lavf.av_register_all()

    def versions(self):
        """
        fetch the version of the FFMpeg libraries.
        """
        return (self.lavc.avcodec_version(),
                self.lavf.avformat_version(),
                self.lavu.avutil_version())

    def aux_versions(self):
        """
        fetch the version of the FFMpeg auxiliary libraries.
        """
        return (self.sws.swscale_version(),
                self.swr.swresample_version())


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
