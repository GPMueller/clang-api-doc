clang-api-doc
=============================

Generate C API documentation using libclang Python bindings.

For an example see the [documentation](https://clang-api-doc.readthedocs.io).

[![CI](https://github.com/GPMueller/clang-api-doc/actions/workflows/ci.yml/badge.svg)](https://github.com/GPMueller/clang-api-doc/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/clang-api-doc.svg)](https://badge.fury.io/py/clang-api-doc)


Why?
-----------------------------

Ideally, code should be self-documenting. To me that means little to no documentation should be needed in
the code itself, as it strongly tends to harm readability if the code already explains itself. The
remaining use-cases for documentation are typically
 - **API references**, in particular assumed usage contracts
 - usage examples
 - installation instructions
 - general introductions

This project focuses on generating API references, as the other use-cases tend to be written separate from
the code.


Installation
-----------------------------

The `clang-api-doc` package is on PyPI, so you can use `pip`, `poetry`, or whatever you like to install it,
for example `pip install clang-api-doc`.

To install it locally and in editable mode, simply install poetry and run `poetry install` and to load the
virtual environment run `poetry shell`


CLI usage
-----------------------------

Simply call `clang-api-doc` once per file you wish to document, e.g.

```bash
clang-api-doc -i 'include/mylib/first.h' -o 'docs/first.md'
clang-api-doc -i 'include/mylib/second.h' -o 'docs/second.md'
```

or once per folder, e.g.

```bash
clang-api-doc -i 'include/mylib/' -o 'docs/'
```

These files can then be used in any way you wish to create your final documentation, for example
- transform to a different format using `pandoc`
- write an `index.md` file and use `sphinx` to create html docs


Python package usage
-----------------------------

```python
from clang_api_doc import clang_api_doc

for file_in, file_out in zip(input_files, output_files):
    clang_api_doc.transform_file(file_in, file_out)
```