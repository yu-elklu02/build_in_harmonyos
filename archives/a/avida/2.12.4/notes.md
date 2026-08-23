# Avida 2.12.4

The official release archive from SourceForge is required because the GitHub tag
uses submodules and its generated tarball omits `avida-core`.

The command-line interface is built with the ncurses viewer disabled. The bundled
`tcmalloc-1.4` component is disabled for OHOS armv8 because its implementation
contains x86-specific assembly.

## OHOS Adaptation

### Patch 0001: tcmalloc-optional
Makes `AVD_USE_TCMALLOC` a CMake option in the top-level CMakeLists.txt.

### Patch 0002: C++17/musl/aarch64 compatibility
- **Atomic.h**: Replaces x86 inline assembly (`lock; xaddl`, `mfence`) with
  portable GCC/Clang `__atomic` builtins.
- **Thread.cc**: Replaces `pthread_cancel` with `pthread_kill(0)` (musl does
  not provide `pthread_cancel`). Adds `#include <signal.h>`.
- **cRandom.h**: Adds `<numeric>` and `<random>` includes; removes custom
  `std::iota` definition (C++ standard provides it); replaces
  `std::random_shuffle` with `std::shuffle` + `std::mt19937`.
- **tArray.h**: Adds `<cstdlib>` and `<cstring>` includes for `qsort`.
- **PrintActions.cc, cGenomeUtil.cc, cPopulation.cc**: Replaces all
  `std::random_shuffle` calls with `std::shuffle` + `std::mt19937`.
- **cPopulation.cc**: Adds explicit `std::string()` conversion for `cString`
  return value (C++17 no longer allows implicit conversion).
- **avida-core/CMakeLists.txt**: Makes tcmalloc find_library conditional on
  `AVD_USE_TCMALLOC` to prevent `TCMALLOC_LIBRARY-NOTFOUND` errors.

### CMake configuration
- `CMAKE_SYSTEM_NAME=Linux` (CMake does not recognize HarmonyOS)
- `CMAKE_C_COMPILER_WORKS=TRUE` / `CMAKE_CXX_COMPILER_WORKS=TRUE` to skip
  try-compile (CMake clears MAKEFLAGS internally, causing make to use /bin/sh)
- `MAKEFLAGS=SHELL=/data/service/hnp/bin/bash -j1` to override make's default
  shell (OHOS has no /bin/sh)

### Upstream tests
Cannot execute `./run_tests` because:
1. The script uses `#!/bin/sh` (OHOS has no /bin/sh)
2. Its `testrunner.py` uses Python 2 syntax (`print` without parentheses),
   incompatible with Python 3.12 on OHOS

Run device validation with:

```bash
conan create archives/a/avida/2.12.4 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
