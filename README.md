clang-api-doc
=============

Generate C API documentation using libclang Python bindings.

For an example see the [documentation](https://clang-api-doc.readthedocs.io).


Usage
-------------

Simply call `clang-api-doc` once per file you wish to document, e.g.

```bash
clang-api-doc -f 'include/mylib/first.h' -o 'first.md'
clang-api-doc -f 'include/mylib/second.h' -o 'second.md'
```

These files can then be used in any way you wish to create your final documentation, for example
- transform to a different format using `pandoc`
- write an `index.md` file and use `sphinx` to create html docs


Installation
-------------

The `clang-api-doc` package is on PyPI, so you can use `pip`, `poetry`, or whatever you like to install it.