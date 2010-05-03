#!/usr/bin/python

import pyrana
import unittest

import helper


def makeMux(fmtname="yuv4mpegpipe", filename="/dev/null"):
    f = open(filename, "wb")
    mux = pyrana.format.Muxer(f, fmtname)
    return mux

class MuxerTestCase(helper.BaseFormatTestCase):
    def failUnlessEqualStreams(self, got, expected):
        for st, ex in zip(got, expected):
            self.assertTrue(len(st) == len(ex))
            for k in ex:
                if k == 'extraData':
                    # we can't compare extradata (yet)
                    continue
                self.failUnlessEqual(ex[k], st[k],
                                     "'%s' is different: ref='%s' got='%s'" \
                                     %(k, ex[k], st[k]))

    def test_CreateEmptyMuxer(self):
        mux = makeMux()
        assert(mux)
    def test_CantCreateMuxerUnknown(self):
        self.assertRaises(pyrana.SetupError, makeMux, "Innsmouth")
       


if __name__ == "__main__":
    unittest.main() 

