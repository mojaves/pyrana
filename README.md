
Pyrana - python package for simple manipulation of multimedia files
===================================================================

(C) 2010-2014 Francesco Romani < fromani | gmail : com >


[![Code Quality](https://landscape.io/github/mojaves/pyrana/master/landscape.png)](https://landscape.io/github/mojaves/pyrana/master)
<!-- [![Build Status](https://travis-ci.org/mojaves/pyrana.png?branch=master)](https://travis-ci.org/mojaves/pyrana) -->


Overview
--------

Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the [FFmpeg](http://ffmpeg.org)
libraries, but provides an independent API.

Pyrana sets you free from the tyranny of [subprocess](http://docs.python.org/3/library/subprocess.html).
Without pyrana, almost every piace of code which wanted to use the mighty
FFmpeg, had to subprocess it. You had no choice.
pyrana provides an powerful, pythonic alternative.
If you *do want* to subprocess() FFmpeg, pyrana may be what you were looking for.

Pyrana aims to be the spiritual successor of [pymedia](http://pymedia.org).
The Pyrana API is insipired by the PyMedia API, but being compatible
with the latter is not a main objective (yet).
The two projects share a similar objective but no code and they
are full independent. However, for the reasons just outlined it is
indexed and advertised on [pypi](http://pypi.python.org/pypi) as
pymedia2-pyrana.


License Notice
--------------

While Pyrana itself is licensed under the ZLIB license (see LICENSE),
the package needs the FFmpeg libraries, which have different licenses
(most notably LGPL and GPL) depending on the configuration.


API Stability
-------------

The API is unstable (= free to change without notice) until the
stable milestone is reached. The API WILL BE maintained stable 
in every major release.


Supported systems
-----------------


* debian: main development host.
          require FFmpeg packages from [deb-multimedia](http://deb-multimedia.org)

* fedora: supported starting from version 20, work in progress.
          require FFmpeg packages from [rpmfusion](http://rpmfusion.net).

* ubuntu: supported starting from Trusty Thar (14.04), work in progress.

* generic linux: see Requirements below.

* others: see Requirements below. Patches welcome :)


Requirements
------------


* [python](http://www.python.org) version 3.4.z, 3.3.z, or 2.7.z.
  The version 3.x is preferred, 2.7 is supported as legacy. Tested under CPython only (yet).

* [ffmpeg](http://ffmpeg.org) version 1.2.x or 2.1.x.
  [libav](http://libav.org) any version, is unsupported. May or may not work.

* [cffi](http://cffi.readthedocs.org) version 0.7.x (x >= 2). Previous versions, most notably the 0.6
  shipped with pypy 2.0, are unsupported.


Getting started
---------------

see [here](http://docs.python.org/install/index.html) for details.


Documentation
-------------

See the `docs/` and the `examples/` folder.
[This category of posts](http://mojaves.github.io/category/pyrana.html) on the author's techinical blog provide even more documentation.


See also
--------

If pyrana does not fit your needs, you may want to try the following:

* [pymedia](http://pymedia.org): is a Python module for wav, mp3, ogg, avi, divx, dvd, cdda etc files manipulations.
* [pyffmpeg](http://code.google.com/p/pyffmpeg/): a ffmpeg wrapper.

