# libtorrent 0.16.17

## W0 dependencies

- `libcurl/8.5.0`
- `zlib/1.3.1.1`
- `openssl/3.5.6`
- `cppunit/1.15.1` for upstream CppUnit tests

## Build and tests

The recipe uses the rakshasa `rtorrent` release asset for libtorrent, not the
GitHub codeload tag archive, because the release asset includes generated
`configure` and `Makefile.in` files. This avoids requiring `automake`/`aclocal`
on OHOS CI workers.

The recipe runs the upstream CppUnit suite with `make check`. The consumer test
creates a value, string, and map `torrent::Object` to verify that headers,
library linkage, and runtime behavior work together.
