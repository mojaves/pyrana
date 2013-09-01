#!/usr/bin/python

from contextlib import contextmanager
import unittest
import pyrana.ff
import pyrana.errors
from pyrana.common import get_field_int
from pyrana.common import CodecMixin


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


class TestCodecMixin(unittest.TestCase):
    def test_no_params(self):
        cmx = CodecMixin()
        assert not cmx.params

    def test_params(self):
        params = { 'ans': 42, 'foo': 'bar', 'x': [0, 1, 2] }
        cmx = CodecMixin(params)
        assert cmx.params == params

    @unittest.expectedFailure
    def test_extradata(self):
        cmx = CodecMixin()
        assert not cmx.extra_data


if __name__ == "__main__":
    unittest.main()
