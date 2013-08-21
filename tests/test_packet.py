#!/usr/bin/python

import pyrana.format
import unittest


_B = "a".encode('utf-8')


class TestPacket(unittest.TestCase):
    def test_new_from_string(self):
        try:
            pkt = pyrana.format.Packet(0, _B)
        except pyrana.PyranaError as x:
            self.fail("failed creation from simple string: %s" %str(x))

    def test_new_from_string_huge(self):
        try:
            pkt = pyrana.format.Packet(0, _B * 1024 * 1024 * 32)
        except:
            self.fail("failed creation from huge string")

    def test_new_from_packet(self):
        try:
            pkt = pyrana.format.Packet(0, _B)
            pkt2 = pyrana.format.Packet(1, pkt)
#            assert pkt == pkt2
            assert pkt is not pkt2
        except pyrana.PyranaError as x:
            self.fail("failed creation from another packet")

    def test_data_values_matches(self):
        f = pyrana.format.Packet(0, _B)
        self.assertTrue(f.data == _B)

    def test_data_sizes_matches(self):
        pkt = pyrana.format.Packet(0, _B)
        self.assertTrue(pkt.size == len(_B))
        self.assertTrue(len(pkt) == len(_B))

    def test_default_values(self):
        f = pyrana.format.Packet(0, _B)
        self.assertFalse(f.is_key)
        self.assertTrue(f.pts == pyrana.TS_NULL)
        self.assertTrue(f.dts == pyrana.TS_NULL)
        self.assertTrue(f.stream_id  == 0)

    def test_init_values(self):
        f = pyrana.format.Packet(3, "abracadabra".encode('utf-8'), 200, 300, True)
        self.assertTrue(f.stream_id == 3)
        self.assertTrue(f.is_key)
        self.assertTrue(f.pts == 200)
        self.assertTrue(f.dts == 300)

    def test_cannot_reset_stream_index(self):
        f = pyrana.format.Packet(0, "gammaray".encode('utf-8'))
        self.assertTrue(f.stream_id == 0)
        with self.assertRaises(AttributeError):
            f.stream_id = 23
        self.assertTrue(f.stream_id == 0)

    def test_cannot_reset_is_key(self):
        f = pyrana.format.Packet(0, "gammaray".encode('utf-8'))
        self.assertFalse(f.is_key)
        with self.assertRaises(AttributeError):
            f.is_key = True
        self.assertFalse(f.is_key)

    def test_cannot_reset_pts(self):
        f = pyrana.format.Packet(0, "R'Yleh".encode('utf-8'))
        self.assertTrue(f.pts == pyrana.TS_NULL)
        with self.assertRaises(AttributeError):
            f.pts = 42
        self.assertTrue(f.pts == pyrana.TS_NULL)

    def test_cannot_reset_dts(self):
        f = pyrana.format.Packet(0, "R'Yleh".encode('utf-8'))
        self.assertTrue(f.dts == pyrana.TS_NULL)
        with self.assertRaises(AttributeError):
            f.pts = 42
        self.assertTrue(f.dts == pyrana.TS_NULL)

    def test_cannot_reset_data(self):
        d = b"O RLY?!?"
        f = pyrana.format.Packet(0, d)
        self.assertTrue(f.data == d)
        with self.assertRaises(AttributeError):
            f.data = b"YA, RLY"
        self.assertTrue(f.data == d)

    def test_cannot_reset_size(self):
        d = b"YA, RLY!!!"
        l = len(d)
        f = pyrana.format.Packet(0, d)
        self.assertTrue(f.size == l)
        with self.assertRaises(AttributeError):
            f.size = len(b"YA, RLY")
        self.assertTrue(f.size == l)

    def test_to_bytes(self):
        pkt = pyrana.format.Packet(0, _B)
        buf = bytes(pkt)
        assert(buf)

    def test_hash(self):
        pkt = pyrana.format.Packet(0, _B)
        assert(hash(pkt))


if __name__ == "__main__":
    unittest.main()
