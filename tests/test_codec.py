#!/usr/bin/python

import unittest
from pyrana.common import MediaType, to_media_type
from pyrana.codec import CodecMixin
import pyrana.audio
import pyrana.video


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


class TestCodecFuncs(unittest.TestCase):
    def test_builder_unsupported(self):
        class MockAVCodecContext:
            def __init__(self, codec_type, codec=None):
                self.codec_type = codec_type
                self.codec = codec

        with self.assertRaises(pyrana.errors.ProcessingError):
            ctx = MockAVCodecContext(MediaType.AVMEDIA_TYPE_NB)
            # this media type will always be invalid
            dec = pyrana.codec.decoder_for_stream(ctx, 0,
                                                  pyrana.video.Decoder,
                                                  pyrana.audio.Decoder)



if __name__ == "__main__":
    unittest.main()
