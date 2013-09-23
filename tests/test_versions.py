#!/usr/bin/python

from pyrana.errors import LibraryVersionError
import pyrana.versions
import unittest
from tests.mockslib import MockPlat, MockHandle, MockHandleFaulty


class TestCommonData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    # this can fail, but it should not.
    def test_autoverify_sys(self):
        pyrana.versions.autoverify()
        assert(True)

    def test_autoverify_good(self):
        ver = (54, 0, 0)
        pyrana.versions.autoverify(MockHandle(ver, ver, ver, ver, ver))
        assert(True)

    def test_autoverify_bad_all(self):
        ver = (50, 0, 0)
        swr = (0, 0, 0)
        with self.assertRaises(LibraryVersionError):
           pyrana.versions.autoverify(MockHandle(ver, ver, ver, ver, swr))

    def test_autoverify_bad_lavc_low(self):
        bad = (53, 0, 0)
        good = (54, 0, 0)
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandle(bad, good, good, good, good))

    def test_autoverify_bad_lavc_high(self):
        bad = (55, 0, 0)
        good = (54, 0, 0)
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandle(bad, good, good, good, good))

    def test_autoverify_bad_lavf(self):
        bad = (50, 0, 0)
        good = (54, 0, 0)
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandle(good, bad, good, good, good))

    def test_autoverify_bad_lavu(self):
        bad = (50, 0, 0)
        good = (54, 0, 0)
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandle(good, good, bad, good, good))

    def test_autoverify_bad_sws(self):
        bad = (1, 0, 0)
        good = (54, 0, 0)
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandle(good, good, good, bad, good))

    def test_autoverify_bad_swr(self):
        bad = (0, 0, 0)
        good = (54, 0, 0)
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandle(good, good, good, good, bad))

    def test_autoverify_no_libs(self):
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandleFaulty())

    def test_platform_CPy3x(self):
        pyrana._enforce_platform(MockPlat())
        assert(True)

    def test_platform_CPy31(self):
        with self.assertRaises(RuntimeError):
            pyrana._enforce_platform(MockPlat(vers=(3,1)))

    def test_platform_CPy2x(self):
        with self.assertRaises(RuntimeError):
            pyrana._enforce_platform(MockPlat(vers=(2,7)))


if __name__ == "__main__":
    unittest.main()
