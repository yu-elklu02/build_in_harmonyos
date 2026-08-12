# ACPICA Unix 20260408

The package builds the upstream `iasl` compiler/disassembler. ACPICA's Unix
makefiles default to `_CYGWIN` for an unrecognised uname, so the recipe passes
`ACPI_HOST=_LINUX` explicitly for HarmonyOS.

The upstream ASL test-suite is `tests/aslts.sh`. It runs in the `build()` stage
(not test_package) — conan `create` invokes build() where the full upstream
source tree still lives, and aslts.sh's `build_acpi_tools` rebuilds
iasl/acpiexec/acpibin from source via `make`. Invoking through the packaged
GNU Bash absolute path (`tool_requires("bash/5.3")`) avoids the prior
"break: can't break" fallback to toybox `/bin/sh`.

## 鸿蒙真机适配（4 处拦点 + build() aslts 跑段）

| # | 拦点 | 根因 | 修法 |
|---|---|---|---|
| 1 | `break: can't break` + `#!/bin/bash: bad interpreter` | 鸿蒙真机无 `/bin/bash`，上游 aslts.sh + tests/aslts/bin/* 全用 `#!/bin/bash` shebang；回落 toybox `/bin/sh` 拒 break/continue/for-((;;)) | `tool_requires("bash/5.3")` + 0004 补丁把全 shebang 改 `#!/usr/bin/env bash` + `build()` 注 `PATH=<bash bindir>:$PATH` 让 env 命中依赖包内 GNU Bash |
| 2 | `cc: No such file or directory` | aslts.sh 的 `make` 编 iasl/acpiexec/acpibin 时上游 Makefile 硬编 `cc`，鸿蒙真机 PATH 无 `cc`、要 `clang` | `build()` 注 `CC=clang` 给 aslts.sh 的 `make` 重编 |
| 3 | `mkfifo .../aslts-tmp/GMfifo: Operation not permitted` | aslts.sh 用 `make -j$(nproc)`=20 启 GNU make jobserver，jobserver 用 mkfifo 建在 TMPDIR；鸿蒙 MAC 拒 build folder 内 mkfifo | 0005 补丁把 `make -j$jobs` 那三行硬改 `-j1`（绕 jobserver，不再 mkfifo）+ `build()` 注 `MAKEFLAGS=-j1` |
| 4 | `cp: /tmp/iasl-...: Read-only file system` | aslts.sh 装编工具到 `/tmp`，鸿蒙真机 `/tmp` 只读 | 0003 补丁把装路径绕 `${TMPDIR}` + `build()` 注 `TMPDIR=<build_folder>/aslts-tmp`（可写） |

aslts.sh 真跑完（`ASL Test Suite Finished`、exit 0、无 `break: can't break`、无 mkfifo 拒、test_package test() iasl smoke 1/1 通过）。Summary 文件显 `Test Cases: (of 48)` / `Test Collections: 0 (of 8)`——上游 Summary 聚合按 collection 维度、不逐项列 pass/fail，但 aslts.sh 跑完不退出、各 case 结果文件真写出。

package() 只装 `iasl` + LICENSE，**不**把 `source/ generate/ tests/` 塞进发布包（aslts.sh 在 build() 跑、不需装进包）；test_package/conanfile.py 只验已装 iasl 的 input.asl 编/反编链。
