#!/usr/bin/python

import os.path
from contextlib import contextmanager
import unittest
import pyrana.ff
import pyrana.errors
import pyrana.packet
from pyrana.common import blob, get_field_int, AttrDict, strerror
from tests.mockslib import MockPlat


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
    def setUp(self):
        self.src = { 'ans':42, 'foo':'bar' }
        self.atd = AttrDict('Test', self.src)

    def test_creation(self):
        assert(self.src == self.atd)
        assert(len(self.src) == len(self.atd))

    def test_boolean(self):
        assert(self.atd)
        assert(bool(self.atd))  # explicit
        assert(self.atd.__bool__())  # py2 test

    def test_str(self):
        assert(str(self.atd))

    def test_frozen(self):
        assert(not self.atd.frozen)
        self.atd.freeze()
        assert(self.atd.frozen)
        assert(self.src == self.atd)
        assert(len(self.src) == len(self.atd))

    def test_str_freeze(self):
        s1 = str(self.atd)
        self.atd.freeze()
        s2 = str(self.atd)
        assert(len(s2) > len(s1))

    def test_match_data(self):
        for k in self.src:
            assert(self.src[k] == getattr(self.atd, k))

    def test_get_missing_attr(self):
        assert(self.atd.ans == 42)
        with self.assertRaises(AttributeError):
            x = self.atd.nonexistent

    def test_set_missing_attr(self):
        with self.assertRaises(AttributeError):
            self.atd.fizz = 'buzz'

    def test_set_attr(self):
        assert(self.atd.ans == 42)
        self.atd.ans = 41
        assert(self.atd.ans == 41)

    def test_set_attr_fails_frozen(self):
        assert(self.atd.ans == 42)
        self.atd.freeze()
        assert(self.atd.frozen)
        with self.assertRaises(AttributeError):
            self.atd.ans = 41

    def test_get_item(self):
        assert(self.atd['ans'] == 42)


BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


class TestBlob(object):
    def test_binary(self):
        data = b'123'
        # expected to NOT have __bytes__
        assert(blob(data) == bytes(data))

    def test_packet(self):
        pkt = pyrana.packet.Packet(0, b'xxx')
        # expected to have __bytes__
        assert(blob(pkt) == bytes(pkt))

    # FIXME: bulky. Also depends on decoder.
    def test_samples(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frm = dec.decode(dmx.stream(1))
            smp = frm.samples()
            assert(blob(smp) == bytes(smp))

    # FIXME: bulky. Also depends on decoder.
    def test_image(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frm = dec.decode(dmx.stream(0))
            img = frm.image()
            assert(blob(img) == bytes(img))


class TestErrors(unittest.TestCase):
    def test_strerror_no_error(self):
        assert (strerror(0).lower() == 'success')


class TestCommonData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_platform_CPy3x(self):
        pyrana._enforce_platform(MockPlat())
        assert(True)

    def test_platform_CPy31(self):
        with self.assertRaises(RuntimeError):
            pyrana._enforce_platform(MockPlat(vers=(3,1)))

    def test_platform_CPy2x(self):
        pyrana._enforce_platform(MockPlat(vers=(2,7)))
        assert(True)

    def test_platform_CPy26(self):
        with self.assertRaises(RuntimeError):
            pyrana._enforce_platform(MockPlat(vers=(2,6)))


if __name__ == "__main__":
    unittest.main()
