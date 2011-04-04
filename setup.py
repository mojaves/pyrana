from distutils.core import setup
from distutils.core import Extension

import sys
import subprocess
import shutil
import os
import os.path

def pkginfo():
    info = {}
    f = open("PKG-INFO")
    for line in f:
        try:
            k, v = line.strip().split(':')
            info[k.strip()] = v.strip()
        except ValueError:
            continue
    return info

def quote(s):
    return "\"%s\"" %s

def version(info={}):
    if not info:
        info = pkginfo()
    ver = "UNKNOWN"
    try:
         ver = info["Version"]
    except KeyError:
        pass
    return quote(ver)


# courtesy of http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/502261
def pkgconfig(*packages, **kw):
    flag_map = {b'-I': 'include_dirs', b'-L': 'library_dirs', b'-l': 'libraries'}
    # ffmpeg pkg-config braindamage^W oddity
    cmdline = ["pkg-config", "--static", "--libs", "--cflags" ]
    cmdline += list(packages)
    args = {}
    for token in subprocess.check_output(cmdline).split():
        # TODOpy3: bytes VS strings
        flag = flag_map.get(token[:2])
        val = token[2:].decode('utf-8', 'strict')
        args.setdefault(flag, []).append(val)
    return args

info = pkginfo()

 # FIXME feels hacky, need to figure out a better way
inc_dirs   = [ "." ]
lib_dirs   = []
extra_libs = []

conf_map = {"include_dirs":inc_dirs, "library_dirs":lib_dirs, "libraries":extra_libs}

for pkg_name in ("libavutil", "libavcodec", "libavformat"):
    pkg = pkgconfig(pkg_name)
    for k, v in conf_map.items():
        try:
            v.extend(pkg[k])
        except KeyError:
            pass


# purge duplicates
inc_dirs = list(set(inc_dirs))
lib_dirs = list(set(lib_dirs))
extra_libs = list(set(extra_libs))

pyrana_ext = Extension('pyrana',
                       [
                        'pyrana/errors.c', 'pyrana/pyrana.c',
                        'pyrana/format/format.c', 'pyrana/format/pyfileproto.c',
                        'pyrana/format/demuxer.c', 'pyrana/format/muxer.c',
                        'pyrana/format/packet.c',
                        'pyrana/video/video.c', 'pyrana/video/codec.c',
                        'pyrana/video/decoder.c', 'pyrana/video/encoder.c',
                        'pyrana/video/picture.c',
                        'pyrana/audio/audio.c', 'pyrana/audio/samples.c'
                       ],
                       include_dirs=inc_dirs,
                       library_dirs=lib_dirs,
                       libraries=extra_libs,
                       define_macros=[('PYRANA_VERSION_STRING', version(info)),
# the buffer protocol isn't yet included into the PEP384,
# but we really need it
#                                      ('Py_LIMITED_API', 1),
                                     ]
                      )

setup(name='pyrana',
      version='0.0.1',
      description='package for simple manipulation of multimedia files',
      author='Francesco Romani',
      author_email='fromani@gmail.com',
      url='http://github.com/mojaves/pyrana',
      ext_modules=[pyrana_ext]
      )

