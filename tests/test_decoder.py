#!/usr/bin/python

import os.path
import unittest

import pyrana.ff
import pyrana.formats
import pyrana.errors
import pyrana.codec
import pyrana.video

from tests.mockslib import MockFF, MockFrame, MockLavu, MockSws


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



class TestImage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_cannot_create_image(self):
        with self.assertRaises(pyrana.errors.SetupError):
            img = pyrana.video.Image()

    def test_create_synth1(self):
        ffh = pyrana.ff.get_handle()
        ppframe = pyrana.codec._new_av_frame_pp(ffh)
        img = pyrana.video.Image.from_cdata(ppframe)
        assert(img.is_shared)
        ffh.lavc.avcodec_free_frame(ppframe)

    # FIXME: bulky. Also depends on decoder.
    def test_create_from_live_frame(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frames = dec.decode(dmx.stream(0))
            assert(frames)
            img = frames[0].image()
            assert(img)
            assert(repr(img))
            assert(len(img) >= img.width * img.height)
            assert(img.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frames = dec.decode(dmx.stream(0))
            img = frames[0].image(pyrana.video.PixelFormat.AV_PIX_FMT_RGB24)
            assert(img)
            assert(not img.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_bad(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frames = dec.decode(dmx.stream(0))
            with self.assertRaises(pyrana.errors.ProcessingError):
                img = frames[0].image(pyrana.video.PixelFormat.AV_PIX_FMT_NB)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_indirect(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frames = dec.decode(dmx.stream(0))
            img = frames[0].image()
            assert(img)
            assert(img.is_shared)
            img2 = img.convert(pyrana.video.PixelFormat.AV_PIX_FMT_RGB24)
            assert(img2)
            assert(not img2.is_shared)

    # FIXME: bulky. Also depends on decoder.
    def test_convert_from_live_frame_indirect_bad(self):
        with open(BBB_SAMPLE, 'rb') as f:
            dmx = pyrana.formats.Demuxer(f)
            dec = dmx.open_decoder(0)
            frames = dec.decode(dmx.stream(0))
            img = frames[0].image()
            with self.assertRaises(pyrana.errors.ProcessingError):
                img2 = img.convert(pyrana.video.PixelFormat.AV_PIX_FMT_NB)

    def test_cannot_create_sws_context(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_RGB24
        frame = MockFrame(pixfmt)
        ffh = MockFF(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, frame, pixfmt)

    def test_cannot_alloc_av_image(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_RGB24
        frame = MockFrame(pixfmt)
        ffh = MockFF(faulty=False)
        # inject only a faulty lavu
        ffh.lavu = MockLavu(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, frame, pixfmt)
        assert(ffh.lavu.img_allocs == 1)

    def test_cannot_convert(self):
        pixfmt = pyrana.video.PixelFormat.AV_PIX_FMT_YUV420P  # 0
        frame = MockFrame(pixfmt)
        ffh = MockFF(faulty=False)
        ffh.sws = MockSws(False, True, pixfmt)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.video._image_from_frame(ffh, frame, pixfmt)
        assert(ffh.sws.scale_done == 1)


if __name__ == "__main__":
    unittest.main()
