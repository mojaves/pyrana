#!/usr/bin/python

import itertools
import unittest
import pyrana.ff
import pyrana.errors
from pyrana.ff import singleton, HLoader


class TestHLoader(unittest.TestCase):
    def test_bad_vers(self):
        vers = tuple(itertools.repeat((0, 0, 0), 5))
        _hl = HLoader(vers)
        with self.assertRaises(pyrana.errors.LibraryVersionError):
            x = _hl.hfiles


class TestSingletonDecorator(unittest.TestCase):
    def test_singleton(self):
        @singleton
        class Klass(object):
            pass
        c1 = Klass()
        c2 = Klass()
        assert(c1 is c2)


class TestFFSingleton(unittest.TestCase):
    def test_handle_is_singleton(self):
        h1 = pyrana.ff.get_handle()
        h2 = pyrana.ff.get_handle()
        assert(h1 is h2)

    def test_setup_is_singleton(self):
        h1 = pyrana.ff.setup()
        h2 = pyrana.ff.setup()
        assert(h1 is h2)


if __name__ == "__main__":
    unittest.main()
