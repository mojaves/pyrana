#!/usr/bin/python

from pyrana.common import MediaType
from pyrana.formats import STREAM_ANY
import pyrana.errors
import pyrana.formats
import pyrana
import io
import unittest
import hashlib
import os
import os.path

# FIXME
from tests.mockslib import MockLavf, MockFF, MockAVFormatContext


_uB = b'\0' * 64
_B = _uB * 1024
BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


def md5sum(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as fin:
        for chunk in iter(lambda: fin.read(128*md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()


def mock_new_pkt(ffh, size):
    return bytes(size)


def gen_packets(dmx, stream_id=STREAM_ANY):
    return iter(dmx) if stream_id == STREAM_ANY else dmx.stream(stream_id)


class TestDemuxer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_new_empty_just_init(self):
        with io.BytesIO(b'') as f:
            dmx = pyrana.formats.Demuxer(f, delay_open=True)
            assert dmx

    def test_open_empty_buf(self):
        with self.assertRaises(pyrana.errors.SetupError), \
                io.BytesIO(b'') as f:
            dmx = pyrana.formats.Demuxer(f)
            assert dmx

    def test_open_sample_ogg(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            assert dmx

    def test_open_sample_ogg_streams(self):
        with open(BBB_SAMPLE, 'rb') as f:
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
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            pkt = dmx.read_frame()
            assert pkt
            assert len(pkt)

    def test_read_faulty(self):
        ffh = MockFF(faulty=True)
        ctx = MockAVFormatContext()
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.formats._read_frame(ffh, ctx, mock_new_pkt, 0)

    def test_read_empty(self):
        ffh = MockFF(faulty=False)
        ctx = MockAVFormatContext()
        with self.assertRaises(pyrana.errors.EOSError):
            pyrana.formats._read_frame(ffh, ctx, mock_new_pkt, 0)

    def test_open_decoder_invalid_stream1(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            with self.assertRaises(pyrana.errors.ProcessingError):
                dec = dmx.open_decoder(-1)

    def test_open_decoder_invalid_stream2(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            with self.assertRaises(pyrana.errors.ProcessingError):
                dec = dmx.open_decoder(1024)

    def test_open_decoder(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            assert dec

    def stream_md5(self, stream_id=STREAM_ANY):
        md5 = hashlib.md5()
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            for pkt in gen_packets(dmx, stream_id):
                md5.update(bytes(pkt))
        return md5.hexdigest()

    def stream_exp_md5(self, stream_id=STREAM_ANY):
        md5 = hashlib.md5()
        with open(BBB_SAMPLE, 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            try:
                it = gen_packets(dmx, stream_id)
                while True:
                    pkt = it.next()
                    md5.update(bytes(pkt))
            except StopIteration:
                pass
        return md5.hexdigest()

    def stream_ref_md5(self, stream_id=STREAM_ANY):
        filename = os.path.join('tests', 'data', 'bbb_sample_{}.ref'.format(
            stream_id if stream_id != STREAM_ANY else 'any'))
        with open(filename) as fin:
            dig = fin.readline()
        return dig

    def test_extract_stream_it_0(self):
        assert(self.stream_md5(0) ==
               self.stream_ref_md5(0))

    def test_extract_stream_it_1(self):
        assert(self.stream_md5(1) ==
               self.stream_ref_md5(1))

    def test_extract_stream_it_any(self):
        assert(self.stream_md5() ==
               self.stream_ref_md5())

    def test_extract_stream_it_any_exp(self):
        assert(self.stream_exp_md5() ==
               self.stream_ref_md5())

if __name__ == "__main__":
    unittest.main()
