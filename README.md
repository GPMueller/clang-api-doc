clang-api-doc
=============

Generate C API documentation using libclang Python bindings.

For an example see the [documentation](https://clang-api-doc.readthedocs.io).

[![CI](https://github.com/GPMueller/clang-api-doc/actions/workflows/ci.yml/badge.svg)](https://github.com/GPMueller/clang-api-doc/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/clang-api-doc.svg)](https://badge.fury.io/py/clang-api-doc)


Usage
-------------

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


Installation
-------------

The `clang-api-doc` package is on PyPI, so you can use `pip`, `poetry`, or whatever you like to install it.