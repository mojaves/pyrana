import os.path
from distutils.core import setup


def version():
    # MUST fail if cannot open the source file
    with open('PKG-INFO', 'rt') as info:
        for line in info:
            if line.startswith('Version'):
                name, value = line.strip().split(':')
                return value.strip()


def dependencies():
    # MUST fail if cannot open the source file
    with open('requirements.txt', 'rt') as reqs:
        return reqs.read().splitlines()


def description():
    try:
        with open(os.path.join('docs', 'pyrana-intro.rst'), 'rt') as desc:
            return desc.read()
    except IOError:
        return """
Pyrana is a pure-python package which provides easy, pythonic and
powerful handling of multimedia files, using the FFmpeg libraries
under the hood.
"""

setup(name='pymedia2-pyrana',
      version=version(),
      description='Package for simple manipulation of multimedia files',
      long_description=description(),
      platforms = [ 'posix' ],
      license = 'zlib',
      author = 'Francesco Romani',
      author_email = 'fromani@gmail.com',
      url='http://bitbucket.org/mojaves/pyrana',
      download_url='http://bitbucket.org/mojaves/pyrana',
      packages=[ 'pyrana' ],
      package_data={'pyrana': ['hfiles/*.*']},
      install_requires=[
        "cffi>=0.7.2",
        "enum34>=0.9.16",
        "pycparser>=2.10"
      ],
      classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: zlib/libpng License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
        'Topic :: Multimedia :: Video :: Conversion',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
      ])

