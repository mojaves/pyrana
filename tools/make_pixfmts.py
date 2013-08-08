#!/usr/bin/env python3

import operator
import pycparser

UNARYOPS = {
    '-':operator.neg
}

BINARYOPS = {
    '-':operator.sub,
    '+':operator.add
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


ast = pycparser.parse_file('/usr/include/libavutil/pixfmt.h', use_cpp=True)
count = 0
print('from flufl.enum import IntEnum\n')
print('class PixelFormat(IntEnum):')
for x in ast.ext[0].type.values.enumerators:
    if x.value:
        value = enumvalue(x)
        count = value
    else:
        value = count+1
        count += 1
    print("    %s = %i" %(x.name, value))
    if x.name == 'AV_PIX_FMT_NB':
        break
