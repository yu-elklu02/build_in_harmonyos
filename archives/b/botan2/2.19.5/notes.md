# botan2 2.19.5

Botan 2.19.5 uses its bundled Python `configure.py` to generate a Makefile.
The recipe requests a static library and the upstream `tests` target, then
packages the generated `libbotan-2.a` and `include/botan-2` headers.

The consumer test links the package and computes the SHA-256 digest of a fixed
UTF-8 payload through `Botan::HashFunction`, providing a functional assertion
beyond checking that the archive exists.

OHOS `armv8` validation is pending:

```bash
conan create archives/b/botan2/2.19.5 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
