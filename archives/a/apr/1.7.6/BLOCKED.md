# Device verification pending

The local Windows environment can validate recipe syntax and patch application, but cannot execute OHOS aarch64 binaries. No test result is claimed here. The validation branch must be run on an OHOS device with the project profile:

```bash
conan create archives/a/apr/1.7.6 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```

That command builds APR and executes the consumer `test_apr` binary when the device runner is available. Run the upstream `make check` separately in the device build directory after a successful create; it is intentionally not asserted as passed by this local preparation.
