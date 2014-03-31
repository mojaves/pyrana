
Pyrana - python package for simple manipulation of multimedia files
===================================================================

``(C) 2010-2014 Francesco Romani < fromani | gmail : com >``


.. image:: https://landscape.io/github/mojaves/pyrana/master/landscape.png
   :alt: Code quality

`See on Landscape`_


Overview
--------

Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg_
libraries, but provides an independent API.

Pyrana sets you free from the tyranny of subprocess_.
Without pyrana, almost every piace of code which wanted to use the mighty
FFmpeg, had to subprocess it. You had no choice.
pyrana provides an powerful, pythonic alternative.
If you *do want* to subprocess() FFmpeg, pyrana may be what you were looking for.

Pyrana aims to be the spiritual successor of pymedia_.
The Pyrana API is insipired by the PyMedia API, but being compatible
with the latter is not a main objective (yet).
The two projects share a similar objective but no code and they
are full independent. However, for the reasons just outlined it is
indexed and advertised on pypi_ as pymedia2-pyrana.


License Notice
--------------

While Pyrana itself is licensed under the MIT license (see LICENSE),
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
          require FFmpeg packages from deb-multimedia_.

* fedora: supported starting from version 20, work in progress.
          require FFmpeg packages from rpmfusion_.

* ubuntu: supported starting from Trusty Thar (14.04), work in progress.

* generic linux: see Requirements below.

* others: see Requirements below. Patches welcome :)


Requirements
------------


* python_ version 3.4.z, 3.3.z, or 2.7.z.
  The version 3.x is preferred, 2.7 is supported as legacy. Tested under CPython only (yet).

* ffmpeg_  version 1.2.x or 2.1.x.
  libav_ any version, is unsupported. May or may not work.

* cffi_ version 0.7.x (x >= 2). Previous versions, most notably the 0.6
  shipped with pypy 2.0, are unsupported.


Getting started
---------------

`See here for details`_.


Documentation
-------------

See the ``docs/`` and the ``examples/`` folder.
`This category of posts`_ on the author's techinical blog provide even more documentation.


See also
--------

If pyrana does not fit your needs, you may want to try the following:

* pymedia_: is a Python module for wav, mp3, ogg, avi, divx, dvd, cdda etc files manipulations.
* pyffmpeg_: a ffmpeg wrapper.


.. _See on Landscape: https://landscape.io/github/mojaves/pyrana/master
.. _FFmpeg: http://ffmpeg.org
.. _subprocess: http://docs.python.org/3/library/subprocess.html
.. _pymedia: http://pymedia.org
.. _pypi: http://pypi.python.org/pypi
.. _deb-multimedia: http://deb-multimedia.org
.. _rpmfusion: http://rpmfusion.net
.. _python: http://www.python.org
.. _ffmpeg: http://ffmpeg.org
.. _libav: http://libav.org
.. _This category of posts: http://mojaves.github.io/category/pyrana.html
.. _cffi: http://cffi.readthedocs.org
.. _See here for details: http://docs.python.org/install/index.html
.. _pymedia: http://pymedia.org
.. _pyffmpeg: http://code.google.com/p/pyffmpeg
