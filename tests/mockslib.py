#!/usr/bin/python

#TODO: learn the mock package


class MockFrame:
    def __init__(self, fmt,
                 width=320, height=200,
                 sample_rate=44100,
                 channel_layout=0xFF):
        self.format = fmt
        self.width = width
        self.height = height
        self.sample_rate = sample_rate
        self.channel_layout = channel_layout
        self.nb_samples = 128
        self.data = []
        self.linesize = []


class MockSws:
    def __init__(self, faulty, supported=True, bad_pix_fmt=0):
        self.faulty = faulty
        self.supported = supported
        self.bad_pix_fmt = bad_pix_fmt
        self.src_pix_fmt = None
        self.dst_pix_fmt = None
        self.context_got = 0
        self.scale_done = 0

    def sws_isSupportedOutput(self, pixfmt):
        return self.supported

    def sws_getCachedContext(self, ctx,
                             src_w, src_h, src_format,
                             dst_w, dst_h, dst_format,
                             *args):
        if self.faulty:
            return None
        self.src_pix_fmt = src_format
        self.dst_pix_fmt = dst_format
        self.context_got += 1
        return {'src_pixfmt':src_format, 'dst_pixfmt':dst_format }

    def sws_scale(self, ctx, data, linesize, flags, height, dst_data, dst_linesize):
        self.scale_done += 1
        return -1 if self.faulty or self.bad_pix_fmt == self.dst_pix_fmt else 0


class MockSwr:
    def __init__(self, faulty, bad_smp_fmt=0):
        self.faulty = faulty
        self.bad_smp_fmt = bad_smp_fmt
        self.in_smp_fmt = None
        self.out_smp_fmt = None
        self.ctx_allocs = 0
        self.ctx_inited = 0
        self.conversions = 0

    def swr_alloc_set_opts(self, ctx,
                           out_ch_layout, out_sample_fmt, out_sample_rate,
                           in_ch_layout, in_sample_fmt, in_sample_rate,
                           log_offset, log_ctx):
        self.in_smp_fmt = in_sample_fmt
        self.out_smp_fmt = out_sample_fmt
        self.ctx_allocs += 1
        return None if self.faulty else {'ctx':ctx}

    def swr_init(self, ctx):
        bad = (self.in_smp_fmt == self.bad_smp_fmt)
        self.ctx_inited += 1
        return -1 if self.faulty or bad else 0

    def swr_convert(self, ctx,
                    out_data, out_count,
                    in_data , in_count):
        self.conversions += 1
        return -1  # if self.faulty else 0


class MockLavc:
    @staticmethod
    def av_init_packet(pkt):
        pass

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

    @staticmethod
    def avcodec_alloc_frame():
        return MockFrame(0)  # XXX

    @staticmethod
    def avcodec_free_frame(frame):
        pass


class MockLavf:
    def __init__(self, faulty):
        self.faulty = faulty

    def url_feof(self, pb):
        return False if self.faulty else True

    @staticmethod
    def av_read_frame(ctx, pkt):
        return -1


class MockLavu:
    def __init__(self, faulty):
        self.faulty = faulty
        self.img_allocs = 0
        self.smp_allocs = 0

    def av_rescale_rnd(self, a, b, c, AVRounding):
        return a

    def av_image_alloc(self, data, linesize,
                       width, height, pixfmt, align):
        self.img_allocs += 1
        return -1 if self.faulty else 0

    def av_samples_alloc(self, audio_data, linesize, nb_channels,
                         nb_samples, sample_fmt, align):
        self.smp_allocs += 1
        return -1 if self.faulty else 0

    def av_get_channel_layout_nb_channels(self, channel_layout):
        return 2  # I have just two speakers :(


class MockCFFI:
    def __init__(self):
        self.NULL = None

    def new(self, what):
        class Sink(object):
            def __init__(self):
                self.data = []
                self.linesize = 0
            def __setitem__(self, key, value):
                pass
            def __getitem__(self, key):
                return self
        return Sink()


class MockFF:
    def __init__(self, faulty):
        self.ffi = MockCFFI()
        self.lavc = MockLavc()
        self.lavf = MockLavf(faulty)
        self.lavu = MockLavu(faulty)
        self.sws = MockSws(faulty)
        self.swr = MockSwr(faulty)


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


def av_version_pack(major, minor, micro):
    """
    return the version as packed integer
    """
    return (major << 16 | minor << 8 | micro)


class MockHandle:
    def __init__(self, lavu, lavc, lavf, sws, swr):
        self._lavf = av_version_pack(*lavf)
        self._lavu = av_version_pack(*lavu)
        self._lavc = av_version_pack(*lavc)
        self._sws = av_version_pack(*sws)
        self._swr = av_version_pack(*swr)

    def versions(self):
        return (self._lavu, self._lavc, self._lavf,
                self._sws, self._swr)


class MockHandleFaulty:
    def versions(self):
        raise OSError("will always fail!")
