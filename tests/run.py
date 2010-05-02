#!/usr/bin/env python

import sys
import glob
import os
import os.path
import shutil
import subprocess


class RunTestError(Exception):
    def __init__(self, msg):
        self._msg = msg
    def __str___(self):
        return self._msg


# FIXME: looks fragile. Has setuptools something better?
def pyrana_cpython_version(pyrapath):
    ver = None
    toks = pyrapath.split(os.path.sep)
    updir, build, libdir, pyramod = toks
    lib, arch, ver= libdir.split('-')
    return ver

#FIXME: ditto
def find_executable(exe, paths=None, dirsep=":"):
    exepath = ""
    if not paths:
        paths = os.environ["PATH"]
    for d in paths.split(dirsep):
        exepath = os.path.join(d, exe)
        if os.path.isfile(exepath):
            break
    return exepath


def die(msg):
    sys.stderr.write("%s\n" %(msg))
    sys.exit(1)


def pyrana_local_path():
    pyrapath = glob.glob("../build/lib*/pyrana.so")[0]
    if not os.path.exists(pyrapath):
        raise IOError("build pyrana first")
    return pyrapath


def setup(pyrapath, pyramod="pyrana.so"):
    if not os.path.islink(pyramod):
        os.symlink(pyrapath, pyramod)

def teardown(pyramod="pyrana.so"):
    if os.path.islink("pyrana.so"):
        os.remove("pyrana.so")


def run(cpython, args):
    args = [ cpython ] + list(args)
    retcode = subprocess.call(args)


def _main(args):
    try:
        pyrapath = pyrana_local_path()
        pyver = pyrana_cpython_version(pyrapath)
        cpython = find_executable("python%s" %(pyver))
        if not cpython:
            raise RunTestError("cannot find python v%s" %(pyver))

        setup(pyrapath)
        run(cpython, args)
        teardown()
    except RunTestError, ex:
        die(str(ex))
    except IOError, ex:
        die(str(ex))


if __name__ == "__main__":
    _main(sys.argv[1:])


