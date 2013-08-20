#!/usr/bin/python

from pyrana.errors import LibraryVersionError
import pyrana.versions
import unittest


# FIXME: remove duplicate definitions

class MockPlat:
    def __init__(self, impl='CPython', vers=(3,3)):
        self._impl = impl
        self._vers = tuple(str(v) for v in vers)

    def python_implementation(self):
        return self._impl
 
    def python_version_tuple(self):
        return self._vers


class MockHandle:
    def __init__(self, lavc, lavf, lavu):
        from pyrana.versions import av_version_pack
        self._lavc = av_version_pack(*lavc)
        self._lavf = av_version_pack(*lavf)
        self._lavu = av_version_pack(*lavu)

    def versions(self):
        return (self._lavc, self._lavf, self._lavu)


class MockHandleFaulty:
    def versions(self):
        raise OSError("will always fail!")



class TestCommonData(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyrana.setup()

    # this can fail, but it should not.
    def test_autoverify_sys(self):
        pyrana.versions.autoverify()
        assert(True)

    def test_autoverify_good(self):
        ver = (54, 0, 0)
        pyrana.versions.autoverify(MockHandle(ver, ver, ver))
        assert(True)

    def test_autoverify_bad_all(self):
        ver = (50, 0, 0)
        with self.assertRaises(LibraryVersionError):
           pyrana.versions.autoverify(MockHandle(ver, ver, ver))

    def test_autoverify_bad_lavc(self):
        bad = (50, 0, 0)
        good = (54, 0, 0)
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandle(bad, good, good))

    def test_autoverify_bad_lavf(self):
        bad = (50, 0, 0)
        good = (54, 0, 0)
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandle(good, bad, good))

    def test_autoverify_bad_lavu(self):
        bad = (50, 0, 0)
        good = (54, 0, 0)
        with self.assertRaises(LibraryVersionError):
            pyrana.versions.autoverify(MockHandle(good, good, bad))

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
