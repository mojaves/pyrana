#!/usr/bin/python

import os.path
import unittest

import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec


BBB_SAMPLE = os.path.join('tests', 'data', 'bbb_sample.ogg')


class TestBaseCodecs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_base_decoder_bad_input_codec(self):
        with self.assertRaises(pyrana.errors.SetupError):
            dec = pyrana.codec.BaseDecoder(0)

    def test_base_decoder_video(self):
        dec = pyrana.codec.BaseDecoder("mjpeg")
        assert(dec)
        assert(repr(dec))

    def test_base_decoder_audio(self):
        dec = pyrana.codec.BaseDecoder("flac")
        assert(dec)
        assert(repr(dec))

    def test_decoder_video(self):
        dec = pyrana.video.Decoder("mpeg1video")
        assert(dec)
        assert(repr(dec))

    def test_decoder_audio_empty_flush(self):
        dec = pyrana.audio.Decoder("flac")
        with self.assertRaises(pyrana.errors.NeedFeedError):
            frame = dec.flush()

    def test_decoder_video_empty_flush(self):
        dec = pyrana.video.Decoder("mpeg1video")
        with self.assertRaises(pyrana.errors.NeedFeedError):
            frame = dec.flush()

    # FIXME
    def test_decoder_audio_first_packet(self):
        with open(os.path.join('tests/data/bbb_sample.ogg'), 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(1)
            frame = dec.decode(dmx.stream(1))
            assert(frame)
            assert(repr(frame))

    # FIXME
    def test_decoder_video_first_packet(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frame = dec.decode(dmx.stream(0))
            assert(frame)
            assert(repr(frame))

    def test_decoder_video_from_file_xdata(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            assert(dec.extra_data)


class TestFrameBinder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()


if __name__ == "__main__":
    unittest.main()
