#!/usr/bin/python

import pyrana
import unittest

class AFrameTestCase(unittest.TestCase):
    def _new_buf(self, bps, rate, chans):
        return "\0" * bps * rate * chans
    def _new_aframe(self, fmt, bps, rate, chans, ts=pyrana.TS_NULL):
        buf = self._new_buf(bps, rate, chans)
        f = pyrana.audio.Frame(buf, ts, fmt, rate, chans)
        return f, buf
    def _new_blank_frame(self, fmt, bps, rate, chans, ts=pyrana.TS_NULL):
        try:
            return self._new_aframe(fmt, bps, rate, chans, ts)
        except pyrana.PyranaError, x:
            self.fail("failed creation from base string (%s,%i,%i,%i): %s" \
                      %(fmt, bps, rate, chans, str(x)))

    def _assertCannotResetField(self, field_name, old_value, new_value):
        f, buf = self._new_blank_frame("u8", 1, 8000, 1)
        self.assertTrue(getattr(f, field_name) == old_value)
        self.assertRaises(AttributeError, setattr, f, field_name, new_value)
        self.assertTrue(getattr(f, field_name) == old_value)

    def test_NewFromStringMini(self):
        self._new_blank_frame("u8", 1, 8000, 1)
    def test_NewFromStringMiddle(self):
        self._new_blank_frame("s16", 2, 48000, 6)
    def test_NewFromStringHuge(self):
        self._new_blank_frame("float", 4, 96000, 6)

    def test_NewInvalidSampleRate(self):
        self.assertRaises(pyrana.SetupError,
                          self._new_aframe, "s16", 2, 1, 2)
        self.assertRaises(pyrana.SetupError,
                          self._new_aframe, "s16", 2, 123000, 2)
    def test_NewInvalidChannels(self):
        self.assertRaises(pyrana.SetupError,
                          self._new_aframe, "s16", 2, 44100, 0)
        self.assertRaises(pyrana.SetupError,
                          self._new_aframe, "s16", 2, 44100, 16)

    def test_IsAlwaysKey(self):
        f, buf = self._new_blank_frame("u8", 1, 8000, 1)
        self.assertTrue(f.is_key)

    def test_PTSisNull(self):
        f, buf = self._new_blank_frame("u8", 1, 8000, 1)
        self.assertTrue(f.pts == pyrana.TS_NULL)
    def test_PTSisGiven(self):
        pts = 2323
        f, buf = self._new_blank_frame("u8", 1, 8000, 1, pts)
        self.assertTrue(f.pts == pts)

    def test_SizeMatches(self):
        f, buf = self._new_blank_frame("u8", 1, 8000, 1)
        self.assertTrue(1 * 8000 * 1)
        f, buf = self._new_blank_frame("s16", 2, 44100, 2)
        self.assertTrue(2 * 44100 * 2)

    def test_DataMatches(self):
        f, buf = self._new_blank_frame("u8", 1, 8000, 1)
        self.assertTrue(f.data == buf)
        f, buf = self._new_blank_frame("s16", 2, 44100, 2)
        self.assertTrue(f.data == buf)

    def test_CannotResetIsKey(self):
        self._assertCannotResetField("is_key", 1, 0)
    def test_CannotResetPTS(self):
        self._assertCannotResetField("pts", pyrana.TS_NULL, 4242)
    def test_CannotResetSampleFormat(self):
        self._assertCannotResetField("sample_format", "u8", "s16")
    def test_CannotResetSampleRate(self):
        self._assertCannotResetField("sample_rate", 8000, 11050)
    def test_CannotResetChannels(self):
        self._assertCannotResetField("channels", 1, 2)
    def test_CannotResetSize(self):
        self._assertCannotResetField("size", 1 * 8000 * 1, 4223)
    def test_CannotResetData(self):
        f, old_buf = self._new_blank_frame("u8", 1, 8000, 1)
        new_buf = self._new_buf(2, 48000, 2)
        self.assertRaises(AttributeError, setattr, f, "data", new_buf)



if __name__ == "__main__":
    unittest.main()
 
