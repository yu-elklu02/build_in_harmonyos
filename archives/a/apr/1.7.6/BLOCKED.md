# Verification note

The OHOS device validation for the library build and `test_package/test_apr` is complete with `EXIT=0`. The upstream `make check` target was attempted separately and returned `Error 159` for `testmutexscope` and `testall`; this is recorded as a platform test failure and is not claimed as passed. The recipe intentionally does not run the failing full suite. The local Windows environment cannot execute OHOS aarch64 binaries. To reproduce the supported package validation on an OHOS device:

```bash
conan create archives/a/apr/1.7.6 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```

The command builds APR and executes the consumer `test_apr` binary. Do not interpret it as a full upstream-suite pass.
