#!/usr/bin/python

import pyrana.errors
import pyrana.formats
import pyrana
import io
import unittest

# FIXME
from tests.mockslib import MockLavf, MockFF, MockPacket, MockAVFormatContext


_B = b'\0' * 1024 * 64


class TestDemuxer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_new_empty_just_init(self):
        with io.BytesIO(_B) as f:
            dmx = pyrana.formats.Demuxer(f, delay_open=True)
            assert dmx

    def test_open_zero_buf(self):
        with self.assertRaises(pyrana.errors.SetupError), \
             io.BytesIO(_B) as f:
            dmx = pyrana.formats.Demuxer(f)
            assert dmx

    def test_open_sample_ogg(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            assert dmx

    def test_open_sample_ogg_streams(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            self.assertEqual(len(dmx.streams), 2)

    def test_empty_streams_without_open(self):
        with self.assertRaises(pyrana.errors.ProcessingError), \
             io.BytesIO(_B) as f:
            dmx = pyrana.formats.Demuxer(f, delay_open=True)
            assert dmx.streams  # raised here

    def test_invalid_decoder_without_open(self):
        with self.assertRaises(pyrana.errors.ProcessingError), \
             io.BytesIO(_B) as f:
            dmx = pyrana.formats.Demuxer(f, delay_open=True)
            dec = dmx.open_decoder(0)  # FIXME

    def test_invalid_read_without_open(self):
        with self.assertRaises(pyrana.errors.ProcessingError), \
             io.BytesIO(_B) as f:
            dmx = pyrana.formats.Demuxer(f, delay_open=True)
            frame = dmx.read_frame()
            assert not frame

    def test_read_first_packet(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            pkt = dmx.read_frame()
            assert pkt
            assert len(pkt)

    def test_read_faulty(self):
        ffh = MockFF(faulty=True)
        pkt = MockPacket()
        ctx = MockAVFormatContext()
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.formats._read_frame(ffh, ctx, pkt, 0)

    def test_read_empty(self):
        ffh = MockFF(faulty=False)
        pkt = MockPacket()
        ctx = MockAVFormatContext()
        with self.assertRaises(pyrana.errors.EOSError):
            pyrana.formats._read_frame(ffh, ctx, pkt, 0)

    def test_flush_empty_before_read(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            with self.assertRaises(pyrana.errors.EOSError):
                pkt = dmx.flush()
                assert not len(pkt)


if __name__ == "__main__":
    unittest.main()
