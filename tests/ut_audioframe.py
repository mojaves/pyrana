#!/usr/bin/python

import pyrana
import unittest

class AFrameTestCase(unittest.TestCase):
    def _new_buf(self, bps, rate, chans):
        return "\0" * bps * rate * chans
    def _new_aframe(self, fmt, bps, rate, chans, ts=pyrana.TS_NULL):
        buf = self._new_buf(bps, rate, chans)
        f = pyrana.audio.Frame(buf, ts, fmt, rate, chans)
        return f
    def _new_blank_frame(self, fmt, bps, rate, chans, ts=pyrana.TS_NULL):
        try:
            return self._new_aframe(fmt, bps, rate, chans, ts)
        except pyrana.PyranaError, x:
            self.fail("failed creation from base string (%s,%i,%i,%i): %s" \
                      %(fmt, bps, rate, chans, str(x)))

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



if __name__ == "__main__":
    unittest.main()
 
