# Verification note

The OHOS device validation for `conan create` and `test_package/test_apr` is complete with `EXIT=0` for the previous recipe. The current recipe additionally runs the upstream `make check` target during `build()`, so this validation branch must be rerun on an OHOS device. The local Windows environment cannot execute OHOS aarch64 binaries. To reproduce the package validation on an OHOS device:

```bash
conan create archives/a/apr/1.7.6 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```

The command builds APR, runs upstream `make check`, and executes the consumer `test_apr` binary.
