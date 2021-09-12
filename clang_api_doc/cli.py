import sys
import argparse as _argparse
from pathlib import Path as _Path
from glob import iglob as _iglob

import clang.cindex as _cindex

from . import clang_api_doc


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
        '-r', '--recursive',
        help='search recursively',
        action='store_true')

    parser.add_argument(
        '-l', '--llvmlib',
        type=str,
        help='set the path to the llvm libclang')

    parser.add_argument(
        '-i',
        dest='input',
        type=_Path,
        default="",
        help='file or folder. Specify either a file explicitly or a directory')

    parser.add_argument(
        '-o',
        dest='output',
        type=_Path,
        help='file or folder. Specify either a file explicitly or a directory. Must match input')

    return parser.parse_args(args=args)


def main():
    root_input_folder = None
    input_files = []
    root_output_folder = None
    output_files = []
    debug = False
    verbose = False
    recursive = False

    args = parse_args(sys.argv[1:])

    if not args.input.is_file() and not args.input.is_dir():
        print(f"Error: input path \"{args.input}\" could not be found")
        exit(1)

    if not args.output:
        print("Error: you must specify an output path")
        exit(1)

    # Set the path to llvm to find libclang
    if args.llvmlib:
        _cindex.Config.set_library_path(args.llvmlib)

    # Figure out input file(s)
    if args.input.is_file():
        root_input_folder = _Path(args.input).parent
        input_files = [_Path(args.input)]
    else:
        root_input_folder = _Path(args.input)
        input_files = [_Path(f) for f in _iglob(str(root_input_folder)+'/*', recursive=recursive) if _Path(f).is_file()]

    output_is_file = args.output.suffixes
    if args.output.exists():
        if args.output.is_file():
            output_is_file = True

    # Check compatibility of input and output
    if output_is_file and len(input_files) > 1:
        print(f"Error: cannot use single file output \"{args.output}\" with folder input, which contains multiple files: {input_files}")
        exit(1)

    # Figure out output file(s)
    if output_is_file:
        root_output_folder = _Path(args.output).parent
        output_files = [_Path(args.output)]
    else:
        root_output_folder = _Path(args.output)
        for infile in input_files:
            relative_path = infile.parent.relative_to(root_input_folder)
            stem = infile.stem
            output_files = [root_output_folder / relative_path / (stem + ".md")]

    for file_in, file_out in zip(input_files, output_files):
        clang_api_doc.transform_file(file_in, file_out)


if __name__ == '__main__':
    main()