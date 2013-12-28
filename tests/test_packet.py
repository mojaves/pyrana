#!/usr/bin/python

import sys
import unittest
import pytest
import pyrana.packet
import pyrana.errors
from tests.mockslib import MockFF


_B = b'A'


class TestPacket(unittest.TestCase):
    def test_new_from_string(self):
        try:
            pkt = pyrana.packet.Packet(0, _B)
        except pyrana.errors.PyranaError as x:
            self.fail("failed creation from simple string: %s" % x)

    def test_faulty_alloc(self):
        ffh = MockFF(faulty=True)
        with self.assertRaises(pyrana.errors.ProcessingError):
            pyrana.packet._new_cpkt(ffh, 128)

    def test_zero_alloc(self):
        ffh = MockFF(faulty=True)
        pkt = pyrana.packet._new_cpkt(ffh, 0)
        assert(pkt.size == 0)

    def test_new_from_string_huge(self):
        try:
            pkt = pyrana.packet.Packet(0, _B * 1024 * 1024 * 32)
        except:
            self.fail("failed creation from huge string")

    def test_new_from_packet(self):
        try:
            pkt = pyrana.packet.Packet(0, _B)
            pkt2 = pyrana.packet.Packet(1, pkt)
            assert pkt == pkt2
            assert pkt is not pkt2
        except pyrana.errors.PyranaError as x:
            self.fail("failed creation from another packet")

    def test_repr(self):
        pkt = pyrana.packet.Packet()
        assert pkt
        assert repr(pkt)

    @pytest.mark.skipif(sys.version_info < (3,),
                       reason="requires python3")
    def test_repr_str_equals(self):
        pkt = pyrana.packet.Packet()
        assert pkt
        assert (repr(pkt) == str(pkt))

    def test_data_values_matches(self):
        pkt = pyrana.packet.Packet(0, _B)
        self.assertTrue(pkt.data == _B)

    def test_data_sizes(self):
        pkt = pyrana.packet.Packet(0, _B)
        self.assertTrue(pkt.size >= len(_B))
        self.assertTrue(len(pkt) >= len(_B))

    def test_default_values(self):
        f = pyrana.packet.Packet(0, _B)
        self.assertFalse(f.is_key)
        self.assertTrue(f.pts == pyrana.TS_NULL)
        self.assertTrue(f.dts == pyrana.TS_NULL)
        self.assertTrue(f.stream_id  == 0)

    def test_init_values(self):
        f = pyrana.packet.Packet(3, "abracadabra".encode('utf-8'),
                                 pts=200, dts=300, is_key=True)
        self.assertTrue(f.stream_id == 3)
        self.assertTrue(f.is_key)
        self.assertTrue(f.pts == 200)
        self.assertTrue(f.dts == 300)

    def test_cannot_reset_stream_index(self):
        f = pyrana.packet.Packet(0, "gammaray".encode('utf-8'))
        self.assertTrue(f.stream_id == 0)
        with self.assertRaises(AttributeError):
            f.stream_id = 23
        self.assertTrue(f.stream_id == 0)

    def test_cannot_reset_is_key(self):
        f = pyrana.packet.Packet(0, "gammaray".encode('utf-8'))
        self.assertFalse(f.is_key)
        with self.assertRaises(AttributeError):
            f.is_key = True
        self.assertFalse(f.is_key)

    def test_cannot_reset_pts(self):
        f = pyrana.packet.Packet(0, "R'Yleh".encode('utf-8'))
        self.assertTrue(f.pts == pyrana.TS_NULL)
        with self.assertRaises(AttributeError):
            f.pts = 42
        self.assertTrue(f.pts == pyrana.TS_NULL)

    def test_cannot_reset_dts(self):
        f = pyrana.packet.Packet(0, "R'Yleh".encode('utf-8'))
        self.assertTrue(f.dts == pyrana.TS_NULL)
        with self.assertRaises(AttributeError):
            f.pts = 42
        self.assertTrue(f.dts == pyrana.TS_NULL)

    def test_cannot_reset_data(self):
        d = b"O RLY?!?"
        pkt = pyrana.packet.Packet(0, d)
        self.assertTrue(pkt.data == d)
        with self.assertRaises(AttributeError):
            pkt.data = b"YA, RLY"
        self.assertTrue(pkt.data == d)

    def test_cannot_reset_size(self):
        d = b"YA, RLY!!!"
        l = len(d)
        f = pyrana.packet.Packet(0, d)
        self.assertTrue(f.size >= l)
        with self.assertRaises(AttributeError):
            f.size = len(b"YA, RLY")
        self.assertTrue(f.size >= l)

    def test_to_bytes(self):
        pkt = pyrana.packet.Packet(0, _B)
        buf = bytes(pkt)
        assert(buf)

    def test_hash(self):
        pkt = pyrana.packet.Packet(0, _B)
        assert(hash(pkt))

    def test_raw_pkt(self):
        pkt = pyrana.packet.Packet(0, _B)
        with pkt.raw_pkt() as cpkt:
            assert(cpkt)

    def test_get_item(self):
        f = pyrana.packet.Packet(0, b'cthlhu')
        for i in range(len(f)):
            assert(f[i] == f.data[i])



if __name__ == "__main__":
    unittest.main()
