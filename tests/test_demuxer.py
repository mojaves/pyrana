#!/usr/bin/python

from pyrana.common import MediaType
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


_B = b'\0' * 1024 * 64


def md5sum(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as fin:
        for chunk in iter(lambda: fin.read(128*md5.block_size), b''):
            md5.update(chunk)
    return md5.hexdigest()


def mock_new_pkt(ffh, size):
    return bytes(size)


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
        ctx = MockAVFormatContext()
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.formats._read_frame(ffh, ctx, mock_new_pkt, 0)

    def test_read_empty(self):
        ffh = MockFF(faulty=False)
        ctx = MockAVFormatContext()
        with self.assertRaises(pyrana.errors.EOSError):
            pyrana.formats._read_frame(ffh, ctx, mock_new_pkt, 0)

    def test_flush_empty_before_read(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            with self.assertRaises(pyrana.errors.EOSError):
                pkt = dmx.flush()
                assert not len(pkt)

    def test_open_decoder_invalid_stream1(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            with self.assertRaises(pyrana.errors.ProcessingError):
                dec = dmx.open_decoder(-1)

    def test_open_decoder_invalid_stream2(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            with self.assertRaises(pyrana.errors.ProcessingError):
                dec = dmx.open_decoder(1024)

    def test_open_decoder(self):
        with open('tests/data/bbb_sample.ogg', 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            assert dec

    def get_stream_md5(self, sid):
        md5 = hashlib.md5()
        with open('tests/data/bbb_sample.ogg', 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            for pkt in dmx.stream(sid):        
                md5.update(bytes(pkt))
        return md5.hexdigest()

    def get_stream_md5(self, sid):
        md5 = hashlib.md5()
        with open('tests/data/bbb_sample.ogg', 'rb') as fin:
            dmx = pyrana.formats.Demuxer(fin)
            if sid == -1:
                for pkt in dmx:        
                    md5.update(bytes(pkt))
            else:
                for pkt in dmx.stream(sid):        
                    md5.update(bytes(pkt))
        return md5.hexdigest()
    
    def get_stream_ref_md5(self, sid):
        filename = 'tests/data/bbb_sample_{}.ref'.format(
            sid if sid != -1 else 'any')
        with open(filename) as fin:
            dig = fin.readline()
        return dig

    def test_extract_stream_it_0(self):
        assert(self.get_stream_md5(0) ==
            self.get_stream_ref_md5(0))
    
    def test_extract_stream_it_1(self):
        assert(self.get_stream_md5(1) ==
            self.get_stream_ref_md5(1))

    def test_extract_stream_it_any(self):
        assert(self.get_stream_md5(-1) ==
            self.get_stream_ref_md5(-1))

if __name__ == "__main__":
    unittest.main()