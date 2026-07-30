# Meson 1.11.0

Meson is a pure Python tool. The package preserves the upstream `mesonbuild`
module and uses a small relocatable shell launcher to run it with the target
environment's Python 3.12 interpreter.

The consumer test configures and compiles a minimal C project with the packaged
Meson command, then runs the generated executable.

The full upstream suite exceeds the Conan build timeout on the target. `build()`
therefore runs the upstream `common/1 trivial` project test with one worker. It
performs configure, compile, test, and install steps and completes within CI
limits.
