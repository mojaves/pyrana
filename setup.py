from distutils.core import setup
from distutils.core import Extension

import commands
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
    flag_map = {'-I': 'include_dirs', '-L': 'library_dirs', '-l': 'libraries'}
#    for token in commands.getoutput("pkg-config --libs --cflags %s" % ' '.join(packages)).split():
    # ffmpeg pkg-config br^W^W oddity
    for token in commands.getoutput("pkg-config --static --libs --cflags %s" % ' '.join(packages)).split():
        kw.setdefault(flag_map.get(token[:2]), []).append(token[2:])
    return kw

info = pkginfo()
lavu = pkgconfig("libavutil") 
lavc = pkgconfig("libavcodec") 
lavf = pkgconfig("libavformat") 

inc_dirs   = [ "." ] # FIXME feels hacky, need to figure out a better way
inc_dirs  += list(set(lavu["include_dirs"] + lavc["include_dirs"] + lavf["include_dirs"]))
lib_dirs   = list(set(lavu["library_dirs"] + lavc["library_dirs"] + lavf["library_dirs"]))
extra_libs = list(set(lavu["libraries"] + lavc["libraries"] + lavf["libraries"]))

pyrana_ext = Extension('pyrana',
                       ['pyrana/errors.c', 'pyrana/pyrana.c',
                        'pyrana/format/format.c', 'pyrana/format/pyfileproto.c',
                        'pyrana/format/packet.c', 'pyrana/format/demuxer.c'],
                       include_dirs=inc_dirs,
                       library_dirs=lib_dirs,
                       libraries=extra_libs,
                       define_macros=[('PYRANA_VERSION_STRING', version(info)),]
                      )

setup(name='pyrana',
      version='0.0.1',
      description='package for simple manipulation of multimedia files',
      author='Francesco Romani',
      author_email='fromani@gmail.com',
      url='http://github.com/mojaves/pyrana',
      ext_modules=[pyrana_ext]
      )

