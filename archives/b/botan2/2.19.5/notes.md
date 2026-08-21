# botan2 2.19.5

Botan 2.19.5 uses its bundled Python `configure.py` to generate a Makefile.
The recipe requests a static library, builds it, and executes the upstream
`make check` target before packaging the generated `libbotan-2.a` and
`include/botan-2` headers.

The consumer test links the package and computes the SHA-256 digest of a fixed
UTF-8 payload through `Botan::HashFunction`, providing a functional assertion
beyond checking that the archive exists.

The prior OHOS `armv8` run successfully built the library and passed the
consumer SHA-256 assertion, but it only built `botan-test`; it did not execute
the upstream test suite. Run the following command to complete validation:

```bash
conan create archives/b/botan2/2.19.5 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
