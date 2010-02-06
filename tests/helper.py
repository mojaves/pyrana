#!/usr/bin/python

import os
import os.path
import ConfigParser

def get_samples_path(cfg="samples.cfg"):
    parser = ConfigParser.ConfigParser()
    parser.read(cfg)
    basepath = parser.get("Samples", "samples_dir")
    res = {}
    for sample in ("ogg_av", "ogg_a", "mp3_a"): # FIXME
        name = parser.get("Samples", "%s_sample" %(sample))
        root, ext = os.path.splitext(name)
        res[sample.upper()] = os.path.join(basepath, name)
    return res

def get_stream_info(samples):
    return {"OGG_AV":({
                        'name'       : 'theora',
                        'type'       : 'video',
                        'pixfmt'     : 'yuv420p',
                        'width'      : 1280,
                        'height'     : 720,
                        'bitrate'    : 0,
                        'extradata'  : None,
                    },
                    {
                        'name'       : 'vorbis',
                        'type'       : 'audio',
                        'channels'   : 2,
                        'bitrate'    : 192000,
                        'samplerate' : 48000,
                        'samplebytes': 2,
                        'extradata'  : None,
                    })
            }

