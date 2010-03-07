#!/usr/bin/python

import pyrana
import time
import sys

args = sys.argv[1:]
if len(args) != 1:
    sys.stderr.write("usage: %s filename\n" %(sys.argv[0]))
    sys.exit(1)

def stressWhile(name):
    f = open(name, "rb")
    dmx = pyrana.format.Demuxer(f)

    sys.stdout.write("stressWhile()\n")
    frames = 0
    hasData = True
    while hasData:
        try:
            Fr = dmx.readFrame()
        except pyrana.EOSError:
            sys.stdout.write("\nmaster stream ends here!\n")
            hasData = False
        print Fr
        sys.stdout.write("elapsed frames: %i\r" %(frames))
        frames += 1
    sys.stdout.write("\n")
    f.close()

def stressIter(name):
    f = open(name, "rb")
    dmx = pyrana.format.Demuxer(f)

    sys.stdout.write("stressIter()\n")
    frames = 0
    for Fr in dmx:
        sys.stdout.write("elapsed frames: %i\r" %(frames))
        frames += 1
    sys.stdout.write("\nmaster stream ends here!\n")
    sys.stdout.write("\n")
    f.close()



stressWhile(args[0])
stressIter(args[0])

