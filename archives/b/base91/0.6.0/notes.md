# base91 0.6.0

The upstream project is a plain Makefile build. Its Makefile sets `CC = gcc`,
so the recipe passes the profile-selected C compiler directly on each make
invocation.

`make check` runs the upstream `test/test.sh` functional suite. It encodes and
decodes bundled data, then checks expected checksums and decoded output.

The package installs `base91` plus `b91enc` and `b91dec` command aliases. The
consumer test performs an independent encode/decode round trip with the
installed `base91` binary.

Device validation is pending:

```bash
conan create archives/b/base91/0.6.0 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
