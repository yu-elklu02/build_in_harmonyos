# Validation Blocked

## Current state

- The recipe and consumer test are prepared for `crc32c/1.1.2`.
- This workstation does not have `conan` or `cmake` on `PATH`, so local `conan create` and `test_package` verification cannot be claimed here.
- No `.ci-result.json` was created or edited manually.

## Required device verification

Run the HarmonyOS PC Conan environment setup, then execute the `conan create` command from the repository root. The command must build the recipe and run the consumer test on the target device. Record the real return code and output in the version-level test report before changing the manifest state.

## Expected result

The verification is complete only when all of the following are true:

1. `conan create` finishes successfully for the OHOS/aarch64 profile.
2. The consumer test executable starts on the device and exits with code 0.
3. The output contains `Extend consistency: OK`, `C API consistency: OK`, and `All crc32c tests passed!`.
4. The fixed vectors pass: `0x4300918A` for `{0x12, 0x34, 0x56, 0x78}` and `0x48674BC7` for four zero bytes.
5. The test report records the exact command, device/platform, return code, and observed output. Only then may the version manifest be changed from `built` to the appropriate verified state.

## Self-repair procedure

If verification fails, diagnose and repair the issue on the device before reporting it:

1. Save the complete error output and classify it as dependency, Conan recipe, CMake, compile/link, runtime, permission, or test failure.
2. Search this repository for similar Conan recipes and device reports, especially CMake libraries with `test_package`, `CMakeDeps`, `CMakeToolchain`, and OHOS/aarch64 testing. Reuse proven local patterns where applicable.
3. Apply the smallest fix only under `archives/c/crc32c/1.1.2`, rerun the relevant local checks, and rerun the device verification.
4. Repeat until the expected result is reached. Do not mark the test as passed based on compilation alone.
5. If the failure is caused by a genuine platform restriction or remains blocked after checking comparable recipes and evidence, update the report with the exact blocker and send the failure details back for review.

## Platform fallback

If the consumer executable cannot run because of SELinux, seclabel, execution permission, or device policy restrictions, keep the build result separate from the test result. Record the exact denial and the fallback evidence (successful compile/link plus artifact inspection) in the test report; do not mark `test_package` as passed.
