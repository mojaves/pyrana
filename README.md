
Pyrana - python package for simple manipulation of multimedia files
===================================================================

(C) 2010-2011 Francesco Romani < fromani | gmail : com >


Overview
--------

Pyrana is a python package designed to provides simple access to
multimedia files. Pyrana is based on the FFmpeg (http://ffmpeg.org)
libraries, but provides an independent API.


License Notice
--------------

While Pyrana itself is licensed under the ZLIB license (see COPYING),
the package needs the FFmpeg libraries, which have different licenses
(most notably LGPL and GPL) depending on the configuration.


API Stability
-------------

The API is unstable (= free to change without notice) until the
stable milestone is reached. The API WILL BE maintained stable 
in every major release.


Requirements
------------

* python >= 3.2 (do not forget the development package)
* FFmpeg >= 0.6.1 (the last SVN/GIT snapshot is usually fine).
* The usual build toolchain (gcc, make, development packages - install
`build-essential` on ubuntu/debian)


Getting started
---------------

To build the extension, just run

`python setup.py build`

to install it

`python setup.py install`

see [here](http://docs.python.org/install/index.html) for details.


See also
--------

If pyrana does not fit your needs, you may want to try the following:

* [pymedia](http://pymedia.org): spiritual predecessor of pyrana.
* [pyffmpeg](http://code.google.com/p/pyffmpeg/): a ffmpeg wrapper.


