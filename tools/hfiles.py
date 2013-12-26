#!/usr/bin/env python3

from pprint import pprint
from pyrana.ff import get_handle

ffh = get_handle()
pprint(ffh.hfiles)
#print(ffh.content)
