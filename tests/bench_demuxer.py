#!/usr/bin/env python3


import sys
import time
import hashlib
import pyrana.formats
import pyrana.errors

pyrana.setup()


def extract_stream(src, ctx, sid=pyrana.formats.STREAM_ANY):
    try:
        cnt = 0
        dmx = pyrana.formats.Demuxer(src)
        while True:
            pkt = dmx.read_frame(sid)
            w = ctx.update(bytes(pkt))
            cnt += 1
    except pyrana.errors.EOSError:
        pass
    except pyrana.errors.PyranaError as err:
        sys.stderr.write("%s\n" % err)
    finally:
        return cnt


def _main(fname, sid):
    ctx = hashlib.sha256()
    start = time.time()
    with open(fname, "rb") as fin:
        num = extract_stream(fin, ctx, sid)
    elapsed = time.time() - start
    print("%i pkts, %.3fs, %.3f pps: stream %s = %s" % (
            num, elapsed, num/elapsed, sid, ctx.hexdigest()))


if __name__ == "__main__":
    sid = pyrana.formats.STREAM_ANY
    args = sys.argv[1:]
    if len(args) == 1:
        src = args[0]
    elif len(args) >= 2:
        src = args[0]
        sid = int(args[1])
    else:
        sys.stderr.write("usage: %s source_file [stream_id]\n" % sys.argv[0])
        sys.exit(1)
    _main(src, sid)
