import sys
import argparse as _argparse
from pathlib import Path as _Path

import clang.cindex as _cindex

def check():
    args = parse_args(sys.argv[1:])

    ### Input
    if args.directory:
        print("specifying a header directory is not yet supported")
        exit(1)
    elif args.files:
        file_list = [str(name) for name in args.files.split(',')]

    filename = file_list[0]

    ### Set the path to llvm to find libclang
    if args.llvmlib:
        _cindex.Config.set_library_path(args.llvmlib)

    ### Create and parse index
    index = _cindex.Index.create()
    parse_arguments =  '--language c'.split()
    translation_unit = index.parse(filename, options=_cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD, args=parse_arguments)

    print('Translation unit:', translation_unit.spelling)
    # visit(translation_unit.cursor)
    for cursor in translation_unit.cursor.walk_preorder():
        if cursor.location.file is not None and cursor.location.file.name == filename:
            if cursor.kind in (_cindex.CursorKind.MACRO_INSTANTIATION, _cindex.CursorKind.MACRO_DEFINITION, _cindex.CursorKind.FUNCTION_DECL):
                print('Found %s Type %s DATA %s Extent %s [line=%s, col=%s]' % (cursor.displayname, cursor.kind, cursor.data, cursor.extent, cursor.location.line, cursor.location.column))




def get_documentables(translation_unit):
    filename = translation_unit.cursor.spelling

    macros = []
    variables = []
    typedefs = []
    enums = []
    structs = []
    functions = []
    comments = []

    ### Get functions
    for cursor in translation_unit.cursor.walk_preorder():
        if cursor.location.file is None:
            pass
        elif cursor.location.file.name != filename:
            pass
        elif cursor.kind == _cindex.CursorKind.MACRO_INSTANTIATION:
            macros.append(cursor)
        elif cursor.kind == _cindex.CursorKind.MACRO_DEFINITION:
            macros.append(cursor)
        # elif cursor.kind == _cindex.CursorKind.CALL_EXPR:
        #     calls.append(cursor)
        # if cursor.kind == _cindex.CursorKind.MACRO_DEFINITION: # _cindex.CursorKind.MACRO_INSTANTIATION,
            # macros.append(cursor)
        # elif cursor.kind == _cindex.CursorKind.:
        #     typedefs.append(cursor)
        elif cursor.kind == _cindex.CursorKind.TYPEDEF_DECL:
            typedefs.append(cursor)
        elif cursor.kind == _cindex.CursorKind.ENUM_DECL:
            enums.append(cursor)
        elif cursor.kind == _cindex.CursorKind.STRUCT_DECL:
            structs.append(cursor)
        elif cursor.kind == _cindex.CursorKind.FUNCTION_DECL:
            functions.append(cursor)

    ### Get comments
    for token in translation_unit.cursor.get_tokens():
        if token.kind == _cindex.TokenKind.COMMENT:
            comments.append(token)

    return macros, variables, typedefs, enums, structs, functions, comments


def docstring_from_function(function, file_string):
    full_function_name = ""
    if function.extent.start.line == function.extent.end.line:
        full_function_name = file_string.splitlines()[function.location.line-1][function.extent.start.column-1:function.extent.end.column-1].strip()
    else:
        full_function_name = file_string.splitlines()[function.extent.start.line-1].strip()
        for l in range(function.extent.start.line, function.extent.end.line-1):
            full_function_name += " " + file_string.splitlines()[l].strip()
        full_function_name += " " + file_string.splitlines()[function.extent.end.line-1].strip()
    if full_function_name.endswith(";"):
        full_function_name = full_function_name[:-1]
    return full_function_name


def docstring_from_comment(comment):
    text = comment.spelling.strip()
    if text.startswith("//") or text.startswith("/*"):
        text = text[2:]
    if text.endswith("*/"):
        text = text[:-3]
    text = text.strip()
    return text


def parse_args(args):
    parser = _argparse.ArgumentParser(
        description="clang-api-doc is a tool for automatic API documentation generation.",
        formatter_class=_argparse.ArgumentDefaultsHelpFormatter,
        fromfile_prefix_chars='@')

    parser.add_argument(
        '--debug',
        help='activate more detailed output',
        action='store_true')

    parser.add_argument(
        '-V', '--verbose',
        help='activate more detailed output',
        action='store_true')

    parser.add_argument(
        '-l', '--llvmlib',
        type=str,
        help='set the path to the llvm libclang')

    parser.add_argument(
        '-d', '--directory',
        type=_Path,
        help='set the header directory')

    parser.add_argument(
        '-f', '--files',
        type=str,
        default="",
        help='specify files explicitly instead of a directory (comma-separated list)')

    parser.add_argument(
        '-o', '--outfile',
        type=_Path,
        help='set the output file') # TODO: maybe output directory would be better

    return parser.parse_args(args=args)


class _Environment:
    def __init__(self, args):
        self.files_in  = []
        self.files_out = []

        ### Input
        if args.directory:
            print("specifying a header directory is not yet supported")
            exit(1)
        elif args.files:
            self.files_in = [_Path(str(name)).resolve() for name in args.files.split(',')]


        ### Output
        if args.outfile:
            self.files_out = [args.outfile.resolve()]
        else:
            self.files_out = [_Path("clang-api-doc.md").resolve()]

        ### Set the path to llvm to find libclang
        if args.llvmlib:
            _cindex.Config.set_library_path(args.llvmlib)


def main():
    args = parse_args(sys.argv[1:])

    # print("args:",args)
    environment = _Environment(args)

    file_in = environment.files_in[0]
    file_out = environment.files_out[0]

    ### Create and parse index
    index = _cindex.Index.create()
    parse_arguments =  '--language c'.split()
    translation_unit = index.parse(str(file_in), options=_cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD, args=parse_arguments)

    print(file_in, "->", file_out)

    ### Get functions and comments
    macros, variables, typedefs, enums, structs, functions, comments = get_documentables(translation_unit)

    ### Output file header
    with open(file_out, 'w') as content_file:
        content_file.write("C API documentation\n===================")

    ### Read input to string
    content = ""
    with open(file_in, 'r') as content_file:
        content = content_file.read()


    # comment_end_lines = [comment.extent.end.line for comment in comments]
    macro_lines = [macro.location.line for macro in macros]
    variable_lines = [variable.location.line for variable in variables]
    typedef_lines = [typedef.location.line for typedef in typedefs]
    enum_lines = [enum.location.line for enum in enums]
    struct_lines = [struct.location.line for struct in structs]
    function_lines = [function.location.line for function in functions]


    for idx_c, comment in enumerate(comments):

        comment_text = docstring_from_comment(comment)
        output = ""

        next_line = comment.extent.end.line + 1

        ### The comment is followed by a variable
        if next_line in variable_lines:
            variable = variables[variable_lines.index(next_line)]
            name = docstring_from_function(variable, content)
            # name = typedef.spelling
            output = f"\n\n**`{name}`:**\n\n" + comment_text + "\n\n-------------------------------\n"

        ### The comment is followed by a typedef
        elif next_line in typedef_lines:
            typedef = typedefs[typedef_lines.index(next_line)]
            name = docstring_from_function(typedef, content)
            # name = typedef.spelling
            output = f"\n\n**`{name}`:**\n\n" + comment_text + "\n\n-------------------------------\n"

        ### The comment is followed by an enum
        elif next_line in enum_lines:
            enum = enums[enum_lines.index(next_line)]
            name = docstring_from_function(enum, content)
            # name = enum.spelling
            output = f"\n\n**`{name}`:**\n\n" + comment_text + "\n\n-------------------------------\n"

        ### The comment is followed by a function
        elif next_line in function_lines:
            function = functions[function_lines.index(next_line)]
            full_function_name = docstring_from_function(function, content)
            output = f"\n\n**`{full_function_name}`:**\n\n" + comment_text + "\n\n-------------------------------\n"

        ### The comment is followed by a struct
        elif next_line in struct_lines:
            struct = structs[struct_lines.index(next_line)]
            name = docstring_from_function(struct, content)
            # name = struct.spelling
            output = f"\n\n**`{name}`:**\n\n" + comment_text + "\n\n-------------------------------\n"

        ### The comment is followed by a macro
        elif next_line in macro_lines:
            macro = macros[macro_lines.index(next_line)]
            name = docstring_from_function(macro, content)
            # name = typedef.spelling
            output = f"\n\n**`{name}`:**\n\n" + comment_text + "\n\n-------------------------------\n"

        ### The comment is free-standing
        elif not content.splitlines()[next_line-1].strip():
            output = f"\n\n" + comment_text + "\n\n-------------------------------\n"

        ### Otherwise we may have made a mistake?
        else:
            pass

        ### Add to file
        # print(output)
        with open(file_out, 'a') as outfile:
            for l in output.splitlines():
                print(l, file=outfile)



if __name__ == '__main__':
    main()