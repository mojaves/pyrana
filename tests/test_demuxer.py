#!/usr/bin/python

import pyrana.errors
import pyrana.format
import pyrana
import io
import unittest


_B = b'\0' * 1024 * 64


#TODO: factorize the mocks
class MockFaultyFF:
    class MockFaultyLavf:
        def av_read_frame(self, ctx, pkt):
            return -1

    def __init__(self):
        self.lavf = MockFaultyFF.MockFaultyLavf()


class TestDemuxer(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        pyrana.setup()

    def test_new_empty_just_init(self):
        with io.BytesIO(_B) as f:
            dmx = pyrana.format.Demuxer(f, delay_open=True)
            assert dmx

    def test_open_zero_buf(self):
        with self.assertRaises(pyrana.errors.SetupError), \
             io.BytesIO(_B) as f:
            dmx = pyrana.format.Demuxer(f)
            assert dmx

    def test_open_sample_ogg(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.format.Demuxer(f)
            assert dmx

    def test_open_sample_ogg_streams(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.format.Demuxer(f)
            self.assertEquals(len(dmx.streams), 2)

    def test_empty_streams_without_open(self):
        with self.assertRaises(pyrana.errors.ProcessingError), \
             io.BytesIO(_B) as f:
            dmx = pyrana.format.Demuxer(f, delay_open=True)
            assert dmx.streams  # raised here

    def test_invalid_decoder_without_open(self):
        with self.assertRaises(pyrana.errors.ProcessingError), \
             io.BytesIO(_B) as f:
            dmx = pyrana.format.Demuxer(f, delay_open=True)
            dec = dmx.open_decoder(0)  # FIXME

    def test_invalid_read_without_open(self):
        with self.assertRaises(pyrana.errors.ProcessingError), \
             io.BytesIO(_B) as f:
            dmx = pyrana.format.Demuxer(f, delay_open=True)
            frame = dmx.read_frame()
            assert not frame

    def test_read_first_packet(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.format.Demuxer(f)
            pkt = dmx.read_frame()
            assert pkt
            assert len(pkt)

    def test_read_faulty(self):
        class MockPacket:
            def cpkt(self):
                return {}
        ffh = MockFaultyFF()
        pkt = MockPacket()
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.format._read_frame(ffh, {}, pkt, 0)  # FIXME: proper types


if __name__ == "__main__":
    unittest.main()
