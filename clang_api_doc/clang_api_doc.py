import sys
import argparse as _argparse
from pathlib import Path as _Path
from glob import iglob as _iglob

import clang.cindex as _cindex

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


def full_name_from_cursor(cursor, file_string):
    full_name = ""
    if cursor.extent.start.line == cursor.extent.end.line:
        full_name = file_string.splitlines()[cursor.location.line-1][cursor.extent.start.column-1:cursor.extent.end.column-1].strip()
    else:
        full_name = file_string.splitlines()[cursor.extent.start.line-1].strip()
        for l in range(cursor.extent.start.line, cursor.extent.end.line-1):
            full_name += " " + file_string.splitlines()[l].strip()
        full_name += " " + file_string.splitlines()[cursor.extent.end.line-1].strip()
    if full_name.endswith(";"):
        full_name = full_name[:-1]
    return full_name


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
        '-f',
        dest='in_file_folder',
        type=_Path,
        default="",
        help='file or folder. Specify either a file explicitly or a directory')

    parser.add_argument(
        '-o',
        dest='out_file_folder',
        type=_Path,
        help='file or folder. Specify either a file explicitly or a directory. Must match input')

    return parser.parse_args(args=args)


class _Environment:
    def __init__(self, args):
        self.files_in  = []
        self.files_out = []

        recursive = False

        ### Input
        if args.in_file_folder:
            path_in = args.in_file_folder.resolve()
        else:
            path_in = _Path(".").resolve()

        ### Output
        if args.out_file_folder:
            path_out = args.out_file_folder.resolve()
        else:
            path_out = _Path(".").resolve()

        ###
        if path_in.is_file():
            ### Input
            self.files_in = [path_in]
            ### Output
            if path_out.is_file():
                self.files_out = [args.out_file_folder.resolve()]
            elif path_out.is_dir():
                self.files_out = [(args.out_file_folder.joinpath(self.files_in[0])).resolve()]
            else:
                print("Output path could not be found")
                exit(1)
        elif path_in.is_dir():
            if path_out.is_dir():
                ### Input
                self.files_in = [_Path(f).resolve() for f in _iglob(str(path_in)+'/*', recursive=recursive) if _Path(f).is_file()]
                ### Output
                self.files_out = [path_out.joinpath(str(file_in.stem) + ".md") for file_in in self.files_in]
            elif path_out.is_file():
                print("Input is a folder, but the output specified is a file. This is not allowed")
                exit(1)
            else:
                print("Output path could not be found")
                exit(1)

        ### Set the path to llvm to find libclang
        if args.llvmlib:
            _cindex.Config.set_library_path(args.llvmlib)


def transform_file(file_in, file_out):

    ### Create and parse index
    index = _cindex.Index.create()
    parse_arguments =  '--language c'.split()
    translation_unit = index.parse(str(file_in), options=_cindex.TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD, args=parse_arguments)

    print(file_in, "->", file_out)

    ### Get functions and comments
    macros, variables, typedefs, enums, structs, functions, comments = get_documentables(translation_unit)

    ### Output file header
    with open(file_out, 'w') as content_file:
        content_file.write("")#"C API documentation\n===================")

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
            short_name = variable.spelling
            full_name = full_name_from_cursor(variable, content)
            output = f"\n\n### {short_name}\n\n```C\n{full_name}\n```\n\n" + comment_text + "\n\n"#"\n\n-------------------------------\n"

        ### The comment is followed by a typedef
        elif next_line in typedef_lines:
            typedef = typedefs[typedef_lines.index(next_line)]
            short_name = typedef.spelling
            full_name = full_name_from_cursor(struct, typedef)
            output = f"\n\n### {short_name}\n\n```C\n{full_name}\n```\n\n" + comment_text + "\n\n"#"\n\n-------------------------------\n"

        ### The comment is followed by an enum
        elif next_line in enum_lines:
            enum = enums[enum_lines.index(next_line)]
            short_name = enum.spelling
            full_name = full_name_from_cursor(enum, content)
            output = f"\n\n### {short_name}\n\n```C\n{full_name}\n```\n\n" + comment_text + "\n\n"#"\n\n-------------------------------\n"

        ### The comment is followed by a function
        elif next_line in function_lines:
            function = functions[function_lines.index(next_line)]
            short_name = function.spelling
            full_name = full_name_from_cursor(function, content)
            output = f"\n\n### {short_name}\n\n```C\n{full_name}\n```\n\n" + comment_text + "\n\n"#"\n\n-------------------------------\n"

        ### The comment is followed by a struct
        elif next_line in struct_lines:
            struct = structs[struct_lines.index(next_line)]
            short_name = struct.spelling
            full_name = full_name_from_cursor(struct, content)
            output = f"\n\n### {short_name}\n\n```C\n{full_name}\n```\n\n" + comment_text + "\n\n"#"\n\n-------------------------------\n"

        ### The comment is followed by a macro
        elif next_line in macro_lines:
            macro = macros[macro_lines.index(next_line)]
            short_name = macro.spelling
            full_name = full_name_from_cursor(macro, content)
            output = f"\n\n### {short_name}\n\n```C\n{full_name}\n```\n\n" + comment_text + "\n\n"#"\n\n-------------------------------\n"

        ### The comment is free-standing
        elif not content.splitlines()[next_line-1].strip():
            output = f"\n\n" + comment_text + "\n\n"#"\n\n-------------------------------\n"

        ### Otherwise we may have made a mistake?
        else:
            pass

        ### Add to file
        # print(output)
        with open(file_out, 'a') as outfile:
            for l in output.splitlines():
                print(l, file=outfile)


def check():
    args = parse_args(sys.argv[1:])

    environment = _Environment(args)

    filename = str(environment.files_in[0])

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


def main():
    args = parse_args(sys.argv[1:])

    environment = _Environment(args)

    size = len(environment.files_in)
    for idx in range(size):
        transform_file(environment.files_in[idx], environment.files_out[idx])


if __name__ == '__main__':
    main()