# typobuster 1.0.0 adaptation notes

## Source and build

The upstream v1.0.0 tag is a Python GTK3 application. It has no CMake, Makefile, or upstream automated test suite. The recipe downloads the tagged source archive, verifies its SHA-256, and compiles the complete `typobuster` module tree with `python3 -m compileall`.

## Package layout

The recipe installs the Python module, distribution metadata, and bundled language/icon assets under `lib`, desktop metadata under `share`, and a launcher under `bin/typobuster`. The launcher adds the packaged module directory to `PYTHONPATH` before running `typobuster.main`.

## Runtime requirements

The GUI requires Python 3, PyGObject, GTK3, and GtkSourceView4 in the OpenHarmony runtime environment. The package does not vendor these platform components.

## Tests

Upstream v1.0.0 contains no automated test target. The consumer test executes the packaged `typobuster --version` launcher and loads the packaged `typobuster.tools` module to verify five real text transformations without opening a GUI.
