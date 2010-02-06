#!/usr/bin/python

import pyrana
import time
import sys

args = sys.argv[1:]
if len(args) != 1:
    sys.stderr.write("usage: %s filename\n" %(sys.argv[0]))
    sys.exit(1)

f = open(args[0], "rb")
dmx = pyrana.format.Demuxer(f)

frames = 0
hasData = True
while hasData:
    try:
        Fr = dmx.readFrame()
    except pyrana.EOSError:
        sys.stdout.write("\nmaster stream ends here!\n")
        hasData = False
    sys.stdout.write("elapsed frames: %i\r" %(frames))
    frames += 1

sys.stdout.write("\n")

