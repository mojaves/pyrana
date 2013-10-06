
Pyrana - python package for simple manipulation of multimedia files
===================================================================

(C) 2010-2013 Francesco Romani < fromani | gmail : com >


Overview
--------

Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg (http://ffmpeg.org)
libraries, but provides an independent API.
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


Requirements
------------


* [python](http://www.python.org) version 3.3. Tested under CPython only (yet).

* [ffmpeg](http://ffmpeg.org) version 1.2.x. The version 2.0.x is unsupported. May or may not work.
  [libav](http://libav.org) any version, is unsupported. May or may not work.

* [cffi](http://cffi.readthedocs.org/en/release-0.7.2/)


Getting started
---------------

see [here](http://docs.python.org/install/index.html) for details.


See also
--------

If pyrana does not fit your needs, you may want to try the following:

* [pymedia](http://pymedia.org): is a Python module for wav, mp3, ogg, avi, divx, dvd, cdda etc files manipulations.
* [pyffmpeg](http://code.google.com/p/pyffmpeg/): a ffmpeg wrapper.


