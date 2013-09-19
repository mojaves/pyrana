#!/usr/bin/python

#TODO: learn the mock package


class MockFrame:
    def __init__(self, pixfmt, width=320, height=200):
        self.width = width
        self.height = height
        self.format = pixfmt


class MockSws:
    def __init__(self, faulty, supported=True):
        self.faulty = faulty
        self.supported = supported

    def sws_isSupportedOutput(self, pixfmt):
        return self.supported

    def sws_getCachedContext(self, *args):
        if self.faulty:
            return None
        return {}  # FIXME


class MockLavc:
    @staticmethod
    def av_new_packet(pkt, size):
        return -1

    @staticmethod
    def avcodec_find_decoder_by_name(name):
        return None

    @staticmethod
    def avcodec_alloc_context3(codec):
        return {}

    @staticmethod
    def avcodec_open2(context, codec, params):
        return -1


class MockLavf:
    def __init__(self, faulty):
        self.faulty = faulty

    def url_feof(self, pb):
        return False if self.faulty else True

    @staticmethod
    def av_read_frame(ctx, pkt):
        return -1


class MockCFFI:
    def __init__(self):
        self.NULL = None

    def new(self, what):
        return {}


class MockFF:
    def __init__(self, faulty):
        self.ffi = MockCFFI()
        self.lavc = MockLavc()
        self.lavf = MockLavf(faulty)
        self.sws = MockSws(faulty)


class MockAVFormatContext:
    def __init__(self):
        self.pb = None


class MockAVCodecContext:
    def __init__(self, codec_type=None, codec=None):
        self.codec_type = codec_type
        self.codec = codec
 

class MockPlat:
    def __init__(self, impl='CPython', vers=(3,3)):
        self._impl = impl
        self._vers = tuple(str(v) for v in vers)

    def python_implementation(self):
        return self._impl
 
    def python_version_tuple(self):
        return self._vers


class MockHandle:
    def __init__(self, lavc, lavf, lavu, sws):
        from pyrana.versions import av_version_pack
        self._lavc = av_version_pack(*lavc)
        self._lavf = av_version_pack(*lavf)
        self._lavu = av_version_pack(*lavu)
        self._sws = av_version_pack(*sws)

    def versions(self):
        return (self._lavc, self._lavf, self._lavu)

    def aux_versions(self):
        return (self._sws, )


class MockHandleFaulty:
    def versions(self):
        raise OSError("will always fail!")
