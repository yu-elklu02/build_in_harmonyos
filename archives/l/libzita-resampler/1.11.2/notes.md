# libzita-resampler 1.11.2

The upstream release uses a hand-written Makefile and has no automated test target.
The recipe overrides its native `-march` default for portable OHOS armv8 builds and
installs the shared library, headers, and a pkg-config module consumed by audiowmark.
