# lua-luv 1.51.0-1

## Build approach

luv normally carries Lua and libuv as Git submodules. This recipe disables
those bundled builds and uses the already adapted `lua/5.4.8` and
`libuv/1.52.1` Conan packages instead.

The upstream CMake file did not link the configured Lua library for its
non-Linux branch. The portability patch treats `OHOS` and `HarmonyOS` as
POSIX-like targets and links the configured Lua library plus `rt`.

## Test coverage

The upstream C test driver (`src/test.c`) is built and run with
`tests/manual-test-external-loop.lua`. The consumer test loads the packaged
`luv.so`, calls `uv.version_string()`, and drives a libuv timer through Lua.
