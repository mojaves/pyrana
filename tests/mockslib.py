#!/usr/bin/python

#TODO: learn the mock package


class MockLavc:
    def av_new_packet(self, pkt, size):
        return -1


class MockLavf:
    def __init__(self, faulty):
        self.faulty = faulty

    def url_feof(self, pb):
        return False if self.faulty else True

    def av_read_frame(self, ctx, pkt):
        return -1


class MockFF:
    def __init__(self, faulty):
        self.lavf = MockLavf(faulty)
        self.lavc = MockLavc()


class MockPacket:
    from contextlib import contextmanager
    @contextmanager
    def raw_pkt(self):
        yield {}


class MockAVFormatContext:
    def __init__(self):
        self.pb = None


class MockPlat:
    def __init__(self, impl='CPython', vers=(3,3)):
        self._impl = impl
        self._vers = tuple(str(v) for v in vers)

    def python_implementation(self):
        return self._impl
 
    def python_version_tuple(self):
        return self._vers


class MockHandle:
    def __init__(self, lavc, lavf, lavu):
        from pyrana.versions import av_version_pack
        self._lavc = av_version_pack(*lavc)
        self._lavf = av_version_pack(*lavf)
        self._lavu = av_version_pack(*lavu)

    def versions(self):
        return (self._lavc, self._lavf, self._lavu)


class MockHandleFaulty:
    def versions(self):
        raise OSError("will always fail!")
