#!/usr/bin/env python3

import sys
import pprint
import pygame
import pyrana
from pyrana.formats import Demuxer, MediaType, find_stream


def ovvplayer(dmx, sid):
    pprint.pprint(dmx.streams[sid])
    w, h = dmx.streams[sid].width, dmx.streams[sid].height
    vdec = dmx.open_decoder(sid)
    # Open overlay with the resolution specified
    pygame.display.set_mode((w, h))
    ovl = pygame.Overlay(pygame.YV12_OVERLAY, (w, h))
    ovl.set_location(0, 0, w, h)
    
    vframes = []
    while True:
        vframes.extend(vdec.decode(dmx.stream(sid)))
        for vf in vframes:
            ovl.display((vf.plane(0),
                         vf.plane(1),
                         vf.plane(2)))
            pygame.time.wait(10)
            for ev in pygame.event.get():
                if ev.type in (pygame.KEYDOWN, pygame.QUIT): 
                    break


def main(fname):
    """play video file fname"""
    pygame.init()
    pyrana.setup()
    try:
        with open(path, "rb") as fth:
            dmx = Demuxer(fth)
            sid = find_stream(dmx.streams,
                              0,
                              MediaType.AVMEDIA_TYPE_VIDEO)
            ovplayer(dmx)
    finally:
        pygame.quit()

if __name__== '__main__':
    if len(sys.argv) != 2:
        print ("Usage: play_file <file_pattern>")
    else:
        main(sys.argv[1])
