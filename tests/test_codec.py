#!/usr/bin/python

import unittest
from pyrana.common import MediaType, to_media_type
from pyrana.codec import CodecMixin, BaseDecoder, BaseFrame, Payload
import pyrana.audio
import pyrana.video

from tests import fakes


class TestCommonData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def _assert_valid_collection(self, col):
        self.assertTrue(len(col) > 0)

    def test_input_video_codecs(self):
        self._assert_valid_collection(pyrana.video.InputCodec)

    def test_output_video_codecs(self):
        self._assert_valid_collection(pyrana.video.OutputCodec)

    def test_pixel_formats(self):
        self._assert_valid_collection(pyrana.video.PixelFormat)

    def test_input_audio_codecs(self):
        self._assert_valid_collection(pyrana.audio.InputCodec)

    def test_output_audio_codecs(self):
        self._assert_valid_collection(pyrana.audio.OutputCodec)

    def test_sample_formats(self):
        self._assert_valid_collection(pyrana.audio.SampleFormat)

    def test_valid_input_video_codecs(self):
        self.assertTrue(all(len(name.value) > 0
                            for name in pyrana.video.InputCodec))

    def test_valid_output_video_codecs(self):
        self.assertTrue(all(len(name.value) > 0
                            for name in pyrana.video.OutputCodec))

    def test_valid_input_audio_codecs(self):
        self.assertTrue(all(len(name.value) > 0
                            for name in pyrana.audio.InputCodec))

    def test_valid_output_audio_codecs(self):
        self.assertTrue(all(len(name.value) > 0
                            for name in pyrana.audio.OutputCodec))


class TestCodecMixin(unittest.TestCase):
    def test_no_params(self):
        cmx = CodecMixin()
        assert not cmx.params

    def test_params(self):
        params = { 'ans': 42, 'foo': 'bar', 'x': [0, 1, 2] }
        cmx = CodecMixin(params)
        assert cmx.params == params

    def test_extradata(self):
        cmx = CodecMixin()
        assert not cmx.extra_data


class TestPayload(unittest.TestCase):
    def setUp(self):
        self._p = Payload()

    def test_len(self):
        with self.assertRaises(NotImplementedError):
            x = len(self._p)

    def test_blob(self):
        with self.assertRaises(NotImplementedError):
            x = self._p.blob()

    def test_get_item(self):
        with self.assertRaises(NotImplementedError):
            x = self._p[0]


class TestBaseFrame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_new_empty(self):
        frame = BaseFrame()
        assert(frame)
        assert(repr(frame))


def av_decode_dummy(ctx, pframe, flag, pkt):
    flag[0] = 1
    return 0


class TestBaseDecoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_new_empty_just_init(self):
        dec = BaseDecoder('mjpeg', delay_open=True)
        assert dec
        assert dec.media_type == MediaType.AVMEDIA_TYPE_VIDEO

    def test_open_fail(self):
        dec = BaseDecoder('mjpeg', delay_open=True)
        ffh = fakes.FF(faulty=True)
        with self.assertRaises(pyrana.errors.SetupError):
            dec.open(ffh)

    def test_decode_fail(self):
        dec = BaseDecoder('mjpeg')
        with self.assertRaises(pyrana.errors.ProcessingError):
            dec._decode_pkt(b'XXX')  # FIXME

    def test_stub_decode_no_frame(self):
        dec = BaseDecoder('mjpeg')
        dec._av_decode = av_decode_dummy
        with self.assertRaises(pyrana.errors.ProcessingError):
            frame = dec._decode_pkt(None)

    def test_stub_flush(self):
        ref = {}
        def new_frame_dummy(unused):
            return ref
        dec = BaseDecoder('mjpeg')
        dec._av_decode = av_decode_dummy
        dec._new_frame = new_frame_dummy
        frame = dec.flush()
        assert(frame is ref)

    def test_decode_stop_iteration(self):
        def gen():
            yield pyrana.packet.Packet(0, b"")
            raise StopIteration
        dec = BaseDecoder('mjpeg')
        assert(dec)
        with self.assertRaises(pyrana.errors.EOSError):
            dec.decode(gen())


class TestCodecFuncs(unittest.TestCase):
    def test_builder_unsupported(self):
       with self.assertRaises(pyrana.errors.ProcessingError):
            ctx = fakes.AVCodecContext(MediaType.AVMEDIA_TYPE_NB)
            # this media type will always be invalid
            dec = pyrana.codec.make_codec(pyrana.video.Decoder,
                                          pyrana.audio.Decoder,
                                          0, ctx)

    def test_fetcher_list(self):
        data = list(range(16))
        fetch = pyrana.codec.make_fetcher(data)
        assert([fetch(), fetch(), fetch()] == [0,1,2])
        assert(list(data) == list(range(3, 16)))

    def test_fetcher_gen(self):
        def gen(N):
            i = 0
            while i < N:
                yield i
                i += 1
        data = gen(16)
        fetch = pyrana.codec.make_fetcher(data)
        assert([fetch(), fetch(), fetch()] == [0,1,2])
        assert(list(data) == list(range(3, 16)))

    def test_fetcher_tuple(self):
        data = tuple(range(16))
        with self.assertRaises(pyrana.errors.ProcessingError):
            fetch = pyrana.codec.make_fetcher(data)


if __name__ == "__main__":
    unittest.main()
