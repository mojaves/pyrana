"""
Helper tool to generate a Python class from a C enum type
"""

import operator
import pycparser
import argparse
import os
import hashlib
import sys


class NoValueException(Exception):
    """
    Used when we are searching for a specific
    enumerator value and we don't find an explicit
    value associated with it
    """
    pass


def compute_sha1_hash(file_to_hash):
    """
    Returns the SHA-1 hash of the file passed
    as input
    """
    sha1 = hashlib.sha1()
    with open(file_to_hash, 'rb') as fth:
        sha1.update(fth.read())
    return sha1.hexdigest()


class EnumTranslator(pycparser.c_ast.NodeVisitor):
    """
    Defines objects able to translate a C enum type
    in a Python class.
    Takes an AST as input, representing the C enum type
    and produces a corresponding Python class that
    inherits from IntEnum.
    To be able to visit the AST nodes, it inherits from
    NodeVisitor
    """

    UNARYOPS = {
        '-': operator.neg
    }

    BINARYOPS = {
        '-': operator.sub,
        '+': operator.add
    }

    def __init__(
            self,
            abstract_syntax_tree,
            enum_name='',
            output_class_name=''):
        self.ast = abstract_syntax_tree
        self.enum_name = enum_name
        if not output_class_name:
            self.output_class_name = enum_name
        else:
            self.output_class_name = output_class_name
        self.output_buffer = []

    def _search_enum_value(self, node, name_to_search):
        """
        Searches for the enumerators name_to_search contained
        in the portion of the AST identified by node
        Returns the value associated with that name if found,
        None otherwise
        """
        for elem in node.values.enumerators:
            if elem.name == name_to_search:
                if elem.value:
                    return self._enumvalue(elem)
                else:
                    raise NoValueException("No associated value for "
                                           "enumerator{}".format(elem.name))
        # FIXME
        """
        It is possible that the enumerator is not expressed as NAME = VALUE
        in the source header file, so we need to calculate the value
        associated to the enumerator (like we do in _translate_enum)
        """

    def _enumvalue(self, enum_token):
        """
        Translate an enumerate value to obtain the
        corresponding value
        """
        if isinstance(enum_token.value, pycparser.c_ast.Constant):
            val = enum_token.value.value
            return int(val, base=0)
        elif isinstance(enum_token.value, pycparser.c_ast.UnaryOp):
            val = enum_token.value.expr.value
            return self.__class__.UNARYOPS[enum_token.value.op](
                int(val, base=0))
        elif isinstance(enum_token.value, pycparser.c_ast.BinaryOp):
            lval = enum_token.value.left.value
            rval = enum_token.value.right.value
            return self.__class__.BINARYOPS[enum_token.value.op](
                int(lval, base=0),
                int(rval, base=0))

    def _translate_enum(self, node):
        """
        Searches for all the enumerate values
        in the enum to translate, saving in a buffer
        the corresponding Python class generated values
        """
        count = 0
        for elem in node.values.enumerators:
            if elem.value:
                value = self._enumvalue(elem)
                if value is None:
                    for (childname, child) in elem.children():
                        if isinstance(child, pycparser.c_ast.ID):
                            #FIXME
                            # This may lead to wrong enumerator value
                            # calculation
                            value = self._search_enum_value(node, child.name)
                count = value
            else:
                value = count+1
                count += 1
            self.output_buffer.append(
                '    {0} = {1}\n'.format(elem.name, value))

    def visit_Enum(self, node):
        """
        This method is called for each Enun node
        found while visiting the AST.
        For further detail please refer to
        pycparser/c_ast.py line 81
        """
        if not self.enum_name or node.name == self.enum_name:
            self._translate_enum(node)

    def _build_header(self, params):
        """
        Writes to an internal buffer the header lines of
        the generated Python class like:
        - the import statement, if required
        - the class declaration
        - a comments, if required
        - the filepath of the source enum alongside with its hash
        """

        import_line = params['import_line']
        comment = params['comment']
        filepath = params['header']
        hash_type = params['hash_type']
        hash_value = params['hash_value']

        if import_line:
            self.output_buffer.append('from enum import IntEnum\n')
            self.output_buffer.append('\n')
        self.output_buffer.append('class {}(IntEnum)'
                                  ':\n'.format(self.enum_name))
        self.output_buffer.append('    """\n')
        if comment:
            self.output_buffer.append('    {}\n'.format(comment))
        if filepath:
            fullpath = os.path.join(os.getcwd(), filepath)
            self.output_buffer.append('    File: {}\n'.format(fullpath))
        if hash_type and hash_value:
            self.output_buffer.append(
                '    {0}: {1}\n'.format(hash_type,
                hash_value))
        self.output_buffer.append('    """\n')

    def _build_body(self):
        """
        Writes to an internal buffer the lines related
        to the enum values
        """
        self.visit(self.ast)

    def translate(self, params):
        """
        Main method of the class, it creates a translation
        for the C enum and stores it in an internal buffer
        """
        self._build_header(params)
        self._build_body()

    def write(self, out_stream=sys.stdout):
        """
        Writes the generated class to an output stream
        """
        out_stream.write(''.join(self.output_buffer))


def _main():
    """
    Manage command line arguments and
    creates an EnumTranslator
    to obtain a Python class
    """
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
    args_obj = args_parser.parse_args()

    if not args_obj.output_class:
        args_obj.output_class = args_obj.enum
    if args_obj.output:
        args_obj.importline = True

    ast = pycparser.parse_file(args_obj.header, use_cpp=True)

    et_obj = EnumTranslator(ast, args_obj.enum, args_obj.output_class)
    translate_params = {
        'import_line': args_obj.importline,
        'header': args_obj.header,
        'comment': args_obj.comment,
        'hash_type': 'SHA-1',
        'hash_value': compute_sha1_hash(args_obj.header)
    }
    et_obj.translate(translate_params)

    if args_obj.output:
        with open(args_obj.output, 'w') as ftw:
            et_obj.write(ftw)
    else:
        et_obj.write()

if __name__ == '__main__':
    _main()
