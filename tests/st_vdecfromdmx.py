#!/usr/bin/python

import pyrana
import time
import sys

args = sys.argv[1:]
if len(args) != 1:
    sys.stderr.write("usage: %s filename\n" %(sys.argv[0]))
    sys.exit(1)

def decodeLoop(j, dmx, dec):
    frames = 0
    decoding = True
    while decoding:
        try:
            pkt = dmx.readFrame(j)
            frm = dec.decode(pkt)       
            sys.stdout.write("elapsed frames: %i\r" %(frames))
            frames += 1
        except pyrana.EOSError:
            decoding = False

def flushLoop(dec):
    frames = 0
    flushing = True
    while flushing:
        try:
            frm = dec.flush()
            frames += 1
        except pyrana.ProcessingError:
            flushing = False




def decAll(name):
    f = open(name, "rb")
    dmx = pyrana.format.Demuxer(f)
   
    j = pyrana.format.find_stream(dmx.streams, 0, pyrana.MEDIA_VIDEO);
    dec = dmx.openDecoder(j)

    sys.stdout.write("decAll()\n")
    decodeLoop(j, dmx, dec)
    flushLoop(dec)

    sys.stdout.write("\nmaster stream ends here!\n")
    sys.stdout.write("\n")
    f.close()



decAll(args[0])

