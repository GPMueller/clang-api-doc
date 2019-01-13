import sys
import argparse as _argparse
from pathlib import Path as _Path

import clang.cindex as _cindex

def find_functions_and_calls(tu):
    """ Retrieve lists of function declarations and call expressions in a translation unit
    """
    filename = tu.cursor.spelling
    calls = []
    functions = []
    for cursor in tu.cursor.walk_preorder():
        if cursor.location.file is None:
            pass
        elif cursor.location.file.name != filename:
            pass
        elif cursor.kind == _cindex.CursorKind.CALL_EXPR:
            calls.append(cursor)
        elif cursor.kind == _cindex.CursorKind.FUNCTION_DECL:
            functions.append(cursor)
    return functions, calls

def fully_qualified(cursor):
    """ Retrieve a fully qualified function name (with namespaces)
    """
    res = cursor.spelling
    cursor = cursor.semantic_parent
    while cursor.kind != _cindex.CursorKind.TRANSLATION_UNIT:
        res = cursor.spelling + '::' + res
        cursor = cursor.semantic_parent
    return res

def find_comments(tu):
    tokens = []
    for token in tu.cursor.get_tokens():
        if token.kind == _cindex.TokenKind.COMMENT:
            tokens.append(token)
    return tokens

def main():
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

    args = parser.parse_args(args=sys.argv[1:])
    # print("args:",args)


    ### Input
    if args.directory:
        print("specifying a header directory is not yet supported")
        exit(1)
    elif args.files:
        file_list = [str(name) for name in args.files.split(',')]

    filename = file_list[0]

    ### Output
    if args.outfile:
        outfilename = args.outfile.resolve()
    else:
        outfilename = "clang-api-doc.md"

    idx = _cindex.Index.create()
    args =  '--language c'.split()

    print(filename, "->", outfilename)

    tu = idx.parse(filename, args=args)
    functions, calls = find_functions_and_calls(tu)
    comments = find_comments(tu)

    with open(outfilename, 'w') as content_file:
        content_file.write("C API documentation\n===================")

    content = ""
    with open(filename, 'r') as content_file:
        content = content_file.read()

    for comment in comments:
        # print(f"comment: '{comment.spelling}' lines {comment.extent.start.line}-{comment.extent.end.line}")

        for function in functions:
            if function.location.line == comment.extent.end.line + 1:
                text = comment.spelling.strip()
                if text.startswith("//") or text.startswith("/*"):
                    text = text[2:]
                if text.endswith("*/"):
                    text = text[:-3]
                text = text.strip()

                full_function_name = ""
                if function.extent.start.line == function.extent.end.line:
                    full_function_name = content.splitlines()[function.location.line-1][function.extent.start.column-1:function.extent.end.column-1].strip()
                else:
                    full_function_name = content.splitlines()[function.extent.start.line-1].strip()
                    for l in range(function.extent.start.line, function.extent.end.line-1):
                        full_function_name += " " + content.splitlines()[l].strip()
                    full_function_name += " " + content.splitlines()[function.extent.end.line-1][:-2].strip()

                output = f"\n\n**`{full_function_name}`:**\n\n" + text + "\n\n-------------------------------\n"

                print(output)

                with open(outfilename, 'a') as content_file:
                    for l in output.splitlines():
                        print(l, file=content_file)

if __name__ == '__main__':
    main()