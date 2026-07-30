# Meson 1.11.0

Meson is a pure Python tool. The package preserves the upstream `mesonbuild`
module and uses a small relocatable shell launcher to run it with the target
environment's Python 3.12 interpreter.

The consumer test configures and compiles a minimal C project with the packaged
Meson command, then runs the generated executable.
