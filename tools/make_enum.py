#!/usr/bin/env python3

import operator
import pycparser
import argparse
import os
import hashlib

UNARYOPS = {
    '-': operator.neg
}

BINARYOPS = {
    '-': operator.sub,
    '+': operator.add
}


def enumvalue(en):
    if isinstance(en.value, pycparser.c_ast.Constant):
        val = en.value.value
        return int(val, base=0)
    elif isinstance(en.value, pycparser.c_ast.UnaryOp):
        val = en.value.expr.value
        return UNARYOPS[en.value.op](int(val, base=0))
    elif isinstance(en.value, pycparser.c_ast.BinaryOp):
        lval = en.value.left.value
        rval = en.value.right.value
        return BINARYOPS[en.value.op](int(lval, base=0),
                                      int(rval, base=0))
    else:
        print(en.name)
        print(en.value)
        print(dir(en.value))


args_parser = argparse.ArgumentParser()
args_parser.add_argument('header', help='the header file to parse')
# Not used yet
args_parser.add_argument('enum', help='name of enumerate in header file')
args_parser.add_argument('-c', '--output_class',
                         help='name of enumerate in the output file')
args = args_parser.parse_args()
if not args.output_class:
    args.output_class = args.enum

ast = pycparser.parse_file(args.header, use_cpp=True)
count = 0

print('from enum import IntEnum\n\n')
print('class {}(IntEnum):'.format(args.output_class))
fullpath = os.path.join(os.getcwd(), args.header)
print('    """wraps the Pixel Formats in file')
print('    {}'.format(fullpath))
sha1 = hashlib.sha1()
with open(fullpath, 'rb') as header_hndl:
    sha1.update(header_hndl.read())
    print('    SHA-1: {}"""'.format(sha1.hexdigest()))
    print()

for x in ast.ext[0].type.values.enumerators:
    if x.value:
        value = enumvalue(x)
        count = value
    else:
        value = count+1
        count += 1
    print("    %s = %i" % (x.name, value))
    if x.name == 'AV_PIX_FMT_NB':
        break
