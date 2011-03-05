#!/usr/bin/python

import pyrana
import os
import os.path
import configparser
import unittest


def get_samples_path(cfg="samples.cfg"):
    parser = configparser.ConfigParser()
    parser.read(cfg)
    basepath = parser.get("Samples", "samples_dir")
    res = {}
    for sample in ("ogg_av", "ogg_a", "mpg_a", "mpg_v", "mov_av", "avi_av"): # FIXME
        name = parser.get("Samples", "%s_sample" %(sample))
        root, ext = os.path.splitext(name)
        res[sample.upper()] = os.path.join(basepath, name)
    return res

def get_stream_info(samples):
    return {"OGG_AV":({
                        'name'        : 'theora',
                        'type'        : pyrana.MEDIA_VIDEO,
                        'pixel_format': 'yuv420p',
                        'width'       : 1280,
                        'height'      : 720,
                        'bit_rate'    : 0,
                        'extra_data'  : None,
                    },
                    {
                        'name'        : 'vorbis',
                        'type'        : pyrana.MEDIA_AUDIO,
                        'channels'    : 2,
                        'bit_rate'    : 192000,
                        'sample_rate' : 48000,
                        'sample_bytes': 2,
                        'extra_data'  : None,
                    })
            }


class BaseFormatTestCase(unittest.TestCase):
    def failUnlessEqualStreams(self, got, expected):
        for st, ex in zip(got, expected):
            self.assertTrue(len(st) == len(ex))
            for k in ex:
                if k == 'extra_data':
                    # we can't compare extradata (yet)
                    continue
                self.assertEqual(ex[k], st[k],
                                 "'%s' is different: ref='%s' got='%s'" \
                                 %(k, ex[k], st[k]))



