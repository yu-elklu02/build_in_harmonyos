# Meson 1.11.0

Meson is a pure Python tool. The package preserves the upstream `mesonbuild`
module and uses a small relocatable shell launcher to run it with the target
environment's Python 3.12 interpreter.

The consumer test configures and compiles a minimal C project with the packaged
Meson command, then runs the generated executable.

The complete upstream suite runs through `python3 run_tests.py` in `build()`.
Its pass/skip/fail total is recorded from the completed device validation log.

The adaptation adds the upstream test's missing OHOS system-definition mapping:
Meson reports `host_machine.system()` as `harmonyos`, and the OHOS Clang
toolchain defines `__OHOS__` as `1`.

The complete upstream suite receives `zlib/1.3.1.1` as a test-only build
requirement. The recipe generates local pkg-config and CMake metadata so that
the suite's dependency-discovery tests exercise a real OHOS zlib package.
