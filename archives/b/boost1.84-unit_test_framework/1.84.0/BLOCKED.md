# Validation Blocked

The recipe and consumer test are prepared, but this workstation does not have
the HarmonyOS Conan toolchain or a target device. No Conan build or test result
is claimed here.

Device validation must run `conan create` and record the actual return code and
test output. If execution is blocked by SELinux, seclabel, or device policy,
record the exact denial and keep compile/link evidence separate from a passed
runtime test.
