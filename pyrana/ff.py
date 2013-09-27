"""
CFFI frontend code for pyrana.
This module is not part of the pyrana public API.
"""

import cffi
from functools import wraps
import os.path
import glob


# The dreaded singleton. It is a necessary evil[1] and this is the reason why:
# bitbucket.org/cffi/cffi/issue/4/typeerror-initializer-for-ctype-double

# http://wiki.python.org/moin/PythonDecoratorLibrary#Singleton
def singleton(cls):
    """Use class as singleton."""

    cls.__new_original__ = cls.__new__

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

    cls.__new__ = singleton_new
    cls.__init_original__ = cls.__init__
    cls.__init__ = object.__init__

    return cls


@singleton
class FF(object):
    """
    FFMpeg abstraction objects.
    Needs to be a singleton because the FFI instance has to be
    one and exactly one.
    Do not use directly. Use get_handle() instead.
    """
    def __init__(self, path="hfiles"):
        self._path = path
        self.ffi = cffi.FFI()
        self.ffi.cdef(self._gather(["_version.h"]))
        self.ffi.cdef(self._gather(['avutil*.h',
                                    'avcodec*.h',
                                    'avformat*.h',
                                    'swscale*.h',
                                    'swresample*.h']))
        self.lavc = self.ffi.dlopen("avcodec")
        self.lavf = self.ffi.dlopen("avformat")
        self.lavu = self.ffi.dlopen("avutil")
        self.sws = self.ffi.dlopen("swscale")
        self.swr = self.ffi.dlopen("swresample")

    def _gather(self, names):
        """load all the pyrana pseudo-headers."""
        root = os.path.abspath(os.path.dirname(__file__))
        hfiles = []
        for name in names:
            hfiles.extend(glob.glob(os.path.join(root, self._path, name)))
        data = []
        for hfile in hfiles:
            with open(hfile, 'rt') as src:
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
