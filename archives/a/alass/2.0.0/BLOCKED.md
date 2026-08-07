# True-device validation blocked

## Result

The ohos-aarch64 validation run ended with `CONAN_EXIT=6` before source or
build execution.

## Cause

Alass is a Rust/Cargo project. The true device has neither `cargo` nor `rustc`
in its configured PATH, and its Conan cache has no Rust toolchain package. The
recipe correctly stops in `validate()` with `alass/2.0.0 requires Cargo in PATH`.

## Evidence

- `which cargo rustc` produced no paths.
- `cargo --version` reported `inaccessible or not found`.
- The ohos-aarch64 profile only configures the C and C++ clang compilers.

## Required environment change

Install a compatible Rust toolchain that provides `cargo` and `rustc` on the
ohos-aarch64 device, then rerun `conan create archives/a/alass/2.0.0
--profile=ohos-aarch64 --build=missing`.

No build or test result is claimed until that command succeeds.
