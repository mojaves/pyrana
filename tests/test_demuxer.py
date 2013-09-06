#!/usr/bin/python

from pyrana.common import MediaType
import pyrana.errors
import pyrana.formats
import pyrana
import io
import unittest
import hashlib
import os

# FIXME
from tests.mockslib import MockLavf, MockFF, MockPacket, MockAVFormatContext


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

    def test_extract_stream(self):
        basepath = 'tests/data/'
        test_f = 'bbb_sample.ogg'
        test_path = basepath + test_f
        out_rf_f0 = 'out0_read_frame.ogg'
        out_rf_f1 = 'out1_read_frame.ogg'
        out_it_f0 = 'out0_iter.ogg'
        out_it_f1 = 'out1_iter.ogg'

        with open(test_path, 'rb') as fin, \
                open(basepath + out_rf_f0, 'wb') as fout:
            dmx = pyrana.formats.Demuxer(fin)
            while True:
                try:
                    pkt = dmx.read_frame(0)
                    w = fout.write(bytes(pkt))
                except pyrana.errors.EOSError:
                    break
        rf0_dig = md5sum(basepath + out_rf_f0)
        os.remove(basepath + out_rf_f0)

        with open(test_path, 'rb') as fin, \
                open(basepath + out_rf_f1, 'wb') as fout:
            dmx = pyrana.formats.Demuxer(fin)
            while True:
                try:
                    pkt = dmx.read_frame(1)
                    w = fout.write(bytes(pkt))
                except pyrana.errors.EOSError:
                    break
        rf1_dig = md5sum(basepath + out_rf_f1)
        os.remove(basepath + out_rf_f1)

        with open(test_path, 'rb') as fin, \
                open(basepath + out_it_f0, 'wb') as fout:
            dmx = pyrana.formats.Demuxer(fin)
            for pkt in dmx.stream(0):
                w = fout.write(bytes(pkt))
        iter0_dig = md5sum(basepath + out_it_f0)
        os.remove(basepath + out_it_f0)

        with open(test_path, 'rb') as fin, \
                open(basepath + out_it_f1, 'wb') as fout:
            dmx = pyrana.formats.Demuxer(fin)
            for pkt in dmx.stream(1):
                w = fout.write(bytes(pkt))
        iter1_dig = md5sum(basepath + out_it_f1)
        os.remove(basepath + out_it_f1)

        assert(rf0_dig == iter0_dig)
        assert(rf1_dig == iter1_dig)

if __name__ == "__main__":
    unittest.main()
