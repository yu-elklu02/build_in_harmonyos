# libtorrent 0.16.17

## W0 dependencies

- `libcurl/8.5.0`
- `zlib/1.3.1.1`
- `openssl/3.5.6`
- `cppunit/1.15.1` for upstream CppUnit tests

## Build and tests

The upstream GitHub source archive requires `autoreconf -ivf` before
configuration. The recipe runs the upstream CppUnit suite with `make check`.
The consumer test creates a value, string, and map `torrent::Object` to verify
that headers, library linkage, and runtime behavior work together.

