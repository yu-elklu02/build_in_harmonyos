# Validation Blocked

## Current state

- The recipe and consumer test are prepared for `crc32c/1.1.2`.
- This workstation does not have `conan` or `cmake` on `PATH`, so local `conan create` and `test_package` verification cannot be claimed here.
- No `.ci-result.json` was created or edited manually.

## Required device verification

Run the HarmonyOS PC Conan environment setup, then execute the `conan create` command from the repository root. The command must build the recipe and run the consumer test on the target device. Record the real return code and output in the version-level test report before changing the manifest state.

## Platform fallback

If the consumer executable cannot run because of SELinux, seclabel, execution permission, or device policy restrictions, keep the build result separate from the test result. Record the exact denial and the fallback evidence (successful compile/link plus artifact inspection) in the test report; do not mark `test_package` as passed.
