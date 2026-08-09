# aggdraw 1.4.1

aggdraw is a CPython C++ extension exposing anti-aliased vector drawing
primitives.  Version 1.4.1 requires Python 3.11 or newer and is built by
setuptools.

## Source and dependencies

- Upstream: https://github.com/pytroll/aggdraw
- Source archive: PyPI sdist, fixed by SHA256 in `conandata.yml`.
- W0 dependency check: no Conan dependencies are declared by this recipe.
- The sdist contains no upstream test directory or `make test`/CTest target.

## Packaging

The recipe builds the C++ extension through the device Python and installs it
to a package-local staging directory.  `package_info()` exposes that directory
through `PYTHONPATH`, so the consumer test imports the packaged extension rather
than the source tree.

## Consumer test

`test_package/test_aggdraw.py` imports the packaged native module, checks its
version, builds a closed vector path, and creates Pen and Brush objects.
