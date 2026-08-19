# APR 1.7.6 HarmonyOS adaptation

## Build environment

- Build system: autotools
- Target: HarmonyOS PC, `os=OHOS`, `arch=armv8`
- Compiler: clang/clang++
- Status: validated on device with `conan create`

## Adaptation

The recipe applies three focused patches:

- `0011-config.guess-ohos.patch`: recognizes `HarmonyOS` and maps aarch64 to `aarch64-unknown-linux-ohos`; avoids the device `/tmp` limitation during libc detection.
- `0012-config.sub-ohos.patch`: accepts the `ohos-linux` triplet.
- `0013-configure-hmdfs-umask.patch`: changes temporary-directory creation from umask `077` to `022` for HMDFS compatibility.

## Dependencies

APR has no Conan runtime dependencies.

## Verification

```text
conan create archives/a/apr/1.7.6 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
EXIT=0
configure: aarch64-unknown-linux-ohos
test_package: test_apr built and executed
```

The upstream test suite is recorded in `test_package/MANIFEST.yml` as `make check` with 45 test modules. The device report confirms the Conan consumer test; this local Windows environment cannot execute OHOS binaries, so no upstream pass rate is claimed.
