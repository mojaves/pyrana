#!/usr/bin/python

import unittest
from pyrana.common import MediaType, to_media_type
from pyrana.codec import CodecMixin, BaseDecoder, BaseFrame
import pyrana.audio
import pyrana.video

from tests.mockslib import MockAVCodecContext, MockFF


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


class TestBaseFrame(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_new_empty(self):
        frame = BaseFrame()
        assert(frame)
        assert(repr(frame))


class TestBaseDecoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pyrana.setup()

    def test_new_empty_just_init(self):
        dec = BaseDecoder('mjpeg', delay_open=True)
        assert dec

    def test_open_fail(self):
        dec = BaseDecoder('mjpeg', delay_open=True)
        ffh = MockFF(faulty=True)
        with self.assertRaises(pyrana.errors.SetupError):
            dec._open(ffh)

    def test_decode_fail(self):
        dec = BaseDecoder('mjpeg')
        with self.assertRaises(pyrana.errors.ProcessingError):
            dec._decode_pkt(None)  # FIXME


class TestCodecFuncs(unittest.TestCase):
    def test_builder_unsupported(self):
       with self.assertRaises(pyrana.errors.ProcessingError):
            ctx = MockAVCodecContext(MediaType.AVMEDIA_TYPE_NB)
            # this media type will always be invalid
            dec = pyrana.codec.decoder_for_stream(ctx, 0,
                                                  pyrana.video.Decoder,
                                                  pyrana.audio.Decoder)



if __name__ == "__main__":
    unittest.main()
