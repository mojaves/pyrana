#!/usr/bin/python

import pyrana
import pyrana.format
import unittest

_B = "a".encode('utf-8')

class TestPacket(unittest.TestCase):
    def test_new_from_string(self):
        try:
            f = pyrana.format.Packet(0, _B)
        except pyrana.PyranaError as x:
            self.fail("failed creation from simple string: %s" %str(x))
    def test_new_from_string_huge(self):
        try:
            f = pyrana.format.Packet(0, _B * 1024 * 1024 * 32)
        except:
            self.fail("failed creation from huge string")
    def test_new_from_packet(self):
        try:
            f = pyrana.format.Packet(0, _B)
            g = pyrana.format.Packet(1, f)
            # assert f == g
            # assert f is not g
        except pyrana.PyranaError as x:
            self.fail("failed creation from another packet")
    def test_data_values_matches(self):
        f = pyrana.format.Packet(0, _B)
        self.assertTrue(f.data == b"a")
        self.assertTrue(f.size == 1)
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
        self.assertRaises(AttributeError, setattr, f, "stream_id", 23)
        self.assertTrue(f.stream_id == 0)
    def test_cannot_reset_is_key(self):
        f = pyrana.format.Packet(0, "gammaray".encode('utf-8'))
        self.assertFalse(f.is_key)
        self.assertRaises(AttributeError, setattr, f, "is_key", 1)
        self.assertFalse(f.is_key)
    def test_cannot_reset_pts(self):
        f = pyrana.format.Packet(0, "R'Yleh".encode('utf-8'))
        self.assertTrue(f.pts == pyrana.TS_NULL)
        self.assertRaises(AttributeError, setattr, f, "pts", 42)
        self.assertTrue(f.pts == pyrana.TS_NULL)
    def test_cannot_reset_dts(self):
        f = pyrana.format.Packet(0, "R'Yleh".encode('utf-8'))
        self.assertTrue(f.dts == pyrana.TS_NULL)
        self.assertRaises(AttributeError, setattr, f, "dts", 42)
        self.assertTrue(f.dts == pyrana.TS_NULL)
    def test_cannot_reset_data(self):
        d = b"O RLY?!?"
        f = pyrana.format.Packet(0, d)
        self.assertTrue(f.data == d)
        self.assertRaises(AttributeError, setattr, f, "data", b"YA, RLY")
        self.assertTrue(f.data == d)
    def test_cannot_reset_size(self):
        d = b"YA, RLY!!!"
        l = len(d)
        f = pyrana.format.Packet(0, d)
        self.assertTrue(f.size == l)
        self.assertRaises(AttributeError, setattr, f, "size", len(b"YA, RLY"))
        self.assertTrue(f.size == l)



if __name__ == "__main__":
    unittest.main()
 
