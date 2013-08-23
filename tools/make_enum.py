#!/usr/bin/env python3

import operator
import pycparser
import argparse
import os
import hashlib
import sys


def compute_sha1_hash(file_to_hash):
    sha1 = hashlib.sha1()
    with open(file_to_hash, 'rb') as f:
        sha1.update(f.read())
    return sha1.hexdigest()


class EnumTranslator(pycparser.c_ast.NodeVisitor):
    """Docstring"""

    UNARYOPS = {
        '-': operator.neg
    }

    BINARYOPS = {
        '-': operator.sub,
        '+': operator.add
    }

    def __init__(self, ast, enum_name='', output_class_name='',
                 *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ast = ast
        self.enum_name = enum_name
        if not output_class_name:
            self.output_class_name = enum_name
        else:
            self.output_class_name = output_class_name
        self.output_buffer = []

    def _enumvalue(self, en):
        if isinstance(en.value, pycparser.c_ast.Constant):
            val = en.value.value
            return int(val, base=0)
        elif isinstance(en.value, pycparser.c_ast.UnaryOp):
            val = en.value.expr.value
            return self.__class__.UNARYOPS[en.value.op](int(val, base=0))
        elif isinstance(en.value, pycparser.c_ast.BinaryOp):
            lval = en.value.left.value
            rval = en.value.right.value
            return self.__class__.BINARYOPS[en.value.op](
                int(lval, base=0),
                int(rval, base=0))
        #FIXME
        """
        else:
            self.output_buffer.append(en.name)
            self.output_buffer.append(en.value)
            self.output_buffer.append(dir(en.value))
        """

    def _translate_enum(self, node):
        count = 0
        for elem in node.values.enumerators:
            if elem.value:
                value = self._enumvalue(elem)
                count = value
            else:
                value = count+1
                count += 1
            self.output_buffer.append('    {0} = {1}'.format(elem.name, value))
            self.output_buffer.append('\n')
            #FIXME
            if elem.name == 'AV_PIX_FMT_NB':
                break

    """for further detail please refer to pycparser/c_ast.py line 81"""
    def visit_Enum(self, node):
        if not self.enum_name or node.name == self.enum_name:
            self._translate_enum(node)

    def build_header(self, import_line=True, filepath='', comment='',
                     hash_type='', hash_value=''):
        if import_line:
            self.output_buffer.append('from enum import IntEnum')
            self.output_buffer.append('\n\n')
        self.output_buffer.append('class {}(IntEnum):'.format(self.enum_name))
        self.output_buffer.append('\n')
        self.output_buffer.append('    """')
        self.output_buffer.append('\n')
        if comment:
            self.output_buffer.append('    {}'.format(comment))
            self.output_buffer.append('\n')
        if filepath:
            fullpath = os.path.join(os.getcwd(), filepath)
            self.output_buffer.append('    File: {}'.format(fullpath))
            self.output_buffer.append('\n')
        if hash_type and hash_value:
            self.output_buffer.append(
                '    {0}: {1}'.format(hash_type, hash_value))
            self.output_buffer.append('\n')
        self.output_buffer.append('    """')
        self.output_buffer.append('\n')

    def build_body(self):
        self.visit(self.ast)

    def build_trailer(self):
        pass

    def flush(self, out_stream=sys.stdout):
        out_stream.write(''.join(self.output_buffer))

if __name__ == '__main__':
    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('header', help='the header file to parse')
    args_parser.add_argument('enum', help='name of enumerate in header file')
    args_parser.add_argument(
        '-l',
        '--output_class',
        help='name of enumerate in the output file')
    args_parser.add_argument(
        '-c',
        '--comment',
        help='comment to be added in generated class docstring')
    args_parser.add_argument(
        '-i',
        '--importline',
        help='add a line to import IntEnum module in generated file',
        action='store_true')
    args_parser.add_argument(
        '-o',
        '--output',
        help='output file name')
    args = args_parser.parse_args()

    if not args.output_class:
        args.output_class = args.enum
    if args.output:
        args.importline = True

    ast = pycparser.parse_file(args.header, use_cpp=True)

    et = EnumTranslator(ast, args.enum, args.output_class)

    et.build_header(
        args.importline,
        args.header,
        args.comment,
        'SHA-1',
        compute_sha1_hash(args.header))
    et.build_body()
    et.build_trailer()

    if args.output:
        with open(args.output, 'w') as f:
            et.flush(f)
    else:
        et.flush()
