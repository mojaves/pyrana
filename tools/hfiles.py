#!/usr/bin/env python3

import os.path
import argparse
from pyrana.ff import HLoader, versions

def _main():
    argp = argparse.ArgumentParser()
    argp.add_argument(
        '-l',
        '--list-hfiles',
        help='show hthe hfiles to load')
    argp.add_argument(
        '-d',
        '--dump-content',
        help='dump the loaded content')
    args = argp.parse_args()

    vers = versions()
    hl = HLoader(vers)
    if args.list_hfiles:
        names = ('libavutil', 'libavcodec', 'libavformat',
                 'libswrescale', 'libswresample')
        for name, ver, hf in zip(names, vers, hl.hfiles):
            vs = '%i.%i.%i' % ver
            print('* %14s: %12s -> %s' % (name, vs, os.path.basename(hf)))
    elif args.dump_content:
        print(hl.decls)

if __name__ == '__main__':
    _main()
