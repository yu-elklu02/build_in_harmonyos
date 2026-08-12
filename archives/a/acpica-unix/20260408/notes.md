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

## 鸿蒙真机适配（6 处拦点 + build() aslts 跑段 + 真验统计）

| # | 拦点 | 根因 | 修法 |
|---|---|---|---|
| 1 | `break: can't break` + `#!/bin/bash: bad interpreter` | 鸿蒙真机无 `/bin/bash`，上游 aslts.sh + tests/aslts/bin/* 全用 `#!/bin/bash` shebang；回落 toybox `/bin/sh` 拒 break/continue/for-((;;)) | `tool_requires("bash/5.3")` + 0004 补丁把全 shebang 改 `#!/usr/bin/env bash` + `build()` 注 `PATH=<bash bindir>:$PATH` |
| 2 | `cc: No such file or directory` | aslts.sh 的 `make` 编 iasl/acpiexec/acpibin 时上游 Makefile 硬编 `cc`，鸿蒙真机 PATH 无 `cc`、要 `clang` | `build()` 注 `CC=clang` 给 aslts.sh 的 `make` 重编 |
| 3 | `mkfifo .../aslts-tmp/GMfifo: Operation not permitted` | aslts.sh 用 `make -j$(nproc)`=20 启 GNU make jobserver，jobserver 用 mkfifo 建在 TMPDIR；鸿蒙 MAC 拒 build folder 内 mkfifo | 0005 补丁把 `make -j$jobs` 那三行硬改 `-j1` + `build()` 注 `MAKEFLAGS=-j1` |
| 4 | `cp: /tmp/iasl-...: Read-only file system` | aslts.sh 装编工具到 `/tmp`，鸿蒙真机 `/tmp` 只读 | 0003 补丁把装路径绕 `${TMPDIR}` + `build()` 注 `TMPDIR=<build_folder>/aslts-tmp` |
| 5 | `install: No such file or directory` (Error 127) | aslts.sh 逐 case `make install` 调 GNU coreutils `install -d -m 775`，鸿蒙真机 PATH 无 `install` → 全 case 跳过、`__STATUS_OF_TEST_CASES` 空 | 0006 补丁把 `Makefile.def` 的 `INST= install`/`INST.dir` 改成 `mkdir`/`mkdir -p -m`（toybox built-in 支持） |
| 6 | `__STATUS_OF_TEST_CASES` 空 / Summary PASS-FAIL 空 | asltsrun 的 `do_summary_of_mode` 用 `cat | while read; ... break` 管道在 toybox 拒 break → 状态没真落盘 | 换口径 4：`build()` 把 aslts.sh stdout tee 到 `aslts-run.log`，统计段读日志里 `Type: <mode> Compile => ... Done` 行（bare Done=PASS、`**** Unexpected iASL failure`/`[[ Error:`=FAIL）；104 个失败保留为已知上游限制，不计为通过。 |

## 真机复验真通过率（不靠退出码/空 Summary）

```
acpica-unix/20260408: ACPI upstream ASLTS: 84 passed, 104 failed, 0 skipped
```

| 口径 | cases | passed | failed | skipped | pass_rate |
|---|---|---|---|---|---|
| per-case×mode Compile 行（aslts-run.log） | 188 | 84 | 104 | 0 | 84/188 (44.7%) |

104 FAIL 是 iasl 本身在鸿蒙 clang 15 + libc++ C++17 工具链上的真编译回归（`iasl -ta`/`-d`/`-p` 失败，非测试运行时问题），见 KNOWN_LIMITATIONS.md 的 24 个 case 列表 + 可行方向。

aslts.sh 真跑完（`ASL Test Suite Finished`、逐 case 真执行、失败被真统计）。188 个 Compile 口径中 84 个通过，104 个上游 iasl 回归失败，不将失败计入通过率。包的独立发布门禁是 `iasl` 消费者编/反编链（1/1 通过）；完整上游结果见 KNOWN_LIMITATIONS.md。
