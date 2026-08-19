# Verification note

The OHOS device validation for `conan create` and `test_package/test_apr` is complete with `EXIT=0`. The upstream `make check` suite is recorded but was not executed in the reported device run; do not infer its pass rate from the consumer test. The local Windows environment cannot execute OHOS aarch64 binaries. To reproduce the package validation on an OHOS device:

```bash
conan create archives/a/apr/1.7.6 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```

The command builds APR and executes the consumer `test_apr` binary. Run upstream `make check` separately if a full upstream-suite result is required.
