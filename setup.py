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

setup(name='pymedia2-pyrana',
      version='0.0.6',
      description='Package for simple manipulation of multimedia files',
      long_description=\
"""
Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg (http://ffmpeg.org)
libraries, but provides an independent API.
""",
      platforms = [ 'posix' ],
      license = 'zlib',
      author = 'Francesco Romani',
      author_email = 'fromani@gmail.com',
      url='http://bitbucket.org/france/pyrana',
      ext_modules=[pyrana_ext],
      classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: zlib/libpng License',
        'Operating System :: POSIX',
        'Programming Language :: C',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
      ])

