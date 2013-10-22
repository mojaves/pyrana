#!/usr/bin/python

from contextlib import contextmanager
import unittest
import pyrana.ff
import pyrana.errors
from pyrana.common import get_field_int, AttrDict


@contextmanager
def lavf_ctx():
    ffh = pyrana.ff.get_handle()
    ctx = ffh.lavf.avformat_alloc_context()
    yield ctx
    ffh.lavf.avformat_free_context(ctx)


class TestFormatFuncs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_avf_get_valid(self):
        with lavf_ctx() as ctx:
            probesize = get_field_int(ctx, "probesize")
            assert probesize

    def test_avf_get_inexistent(self):
        with self.assertRaises(pyrana.errors.NotFoundError), \
             lavf_ctx() as ctx:
            probesize = get_field_int(ctx, "inexistent_attr")
            assert probesize


class TestAttrDict(unittest.TestCase):
    def test_creation(self):
        src = { 'ans':42, 'foo':'bar' }
        atd = AttrDict('Test', src)
        assert(src == atd)
        assert(len(src) == len(atd))

    def test_str(self):
        src = { 'ans':42, 'foo':'bar' }
        atd = AttrDict('Test', src)
        assert(str(atd))

    def test_frozen(self):
        src = { 'ans':42, 'foo':'bar' }
        atd = AttrDict('Test', src)
        assert(not atd.frozen)
        atd.freeze()
        assert(atd.frozen)
        assert(src == atd)
        assert(len(src) == len(atd))

    def test_str_freeze(self):
        src = { 'ans':42, 'foo':'bar' }
        atd = AttrDict('Test', src)
        s1 = str(atd)
        atd.freeze()
        s2 = str(atd)
        assert(len(s2) > len(s1))

    def test_match_data(self):
        src = { 'ans':42, 'foo':'bar' }
        atd = AttrDict('Test', src)
        for k in src:
            assert(src[k] == getattr(atd, k))

    def test_get_missing_attr(self):
        src = { 'ans':42, 'foo':'bar' }
        atd = AttrDict('Test', src)
        assert(atd.ans == 42)
        with self.assertRaises(AttributeError):
            x = atd.nonexistent

    def test_set_missing_attr(self):
        src = { 'ans':42, 'foo':'bar' }
        atd = AttrDict('Test', src)
        with self.assertRaises(AttributeError):
            atd.fizz = 'buzz'

    def test_set_attr(self):
        src = { 'ans':41, 'foo':'bar' }
        atd = AttrDict('Test', src)
        assert(atd.ans == 41)
        atd.ans = 42
        assert(atd.ans == 42)

    def test_set_attr_fails_frozen(self):
        src = { 'ans':41, 'foo':'bar' }
        atd = AttrDict('Test', src)
        assert(atd.ans == 41)
        atd.freeze()
        assert(atd.frozen)
        with self.assertRaises(AttributeError):
            atd.ans = 42


if __name__ == "__main__":
    unittest.main()
