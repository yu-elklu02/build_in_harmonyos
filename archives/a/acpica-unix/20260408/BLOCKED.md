# BLOCKED — acpica-unix/20260408 upstream ASLTS on HarmonyOS

## 真机复验结论（2026-08-12）

**conan create 非零退出**（按你定的真验逻辑：fail>0 → raise ConanException）。

```
acpica-unix/20260408: ACPI upstream ASLTS: 84 passed, 104 failed, 0 skipped
acpica-unix/20260408: ERROR: Error in build() method, line 123
        raise ConanException(
ConanException: ACPI upstream ASLTS failed: 84 passed, 104 failed, 0 skipped
Package '...' build failed
```

按口径统计（不靠 aslts.sh 退出码、不靠空 Summary）：

| 口径 | cases | passed | failed | skipped | pass_rate |
|---|---|---|---|---|---|
| per-case×mode Compile 行（aslts-run.log） | 188 | 84 | 104 | 0 | 84/188 (44.7%) |

- **不得**把 104 FAIL 算作通过、**不得**把 manifest 写成 passed。
- **不得**把 skip 算作 pass（本轮 skip=0，无歧义）。

## 104 FAIL case 列表（iasl 编译失败，非测试运行时问题）

从 aslts-run.log 的 `**** Unexpected iASL failure in .../MAIN.asl!` 行提真失败 case（去重后 24 个 case × 4 mode = ~104 行）：

```
bdemo/ACPICA/bdemo
complex/misc
complex/namespace
complex/operand/tests/oconversion
complex/result/tests/rcopyobject
complex/result/tests/rexplicitconv
complex/result/tests/rindecrement
complex/result/tests/roptional
complex/result/tests/rstore
exceptions/exc
exceptions/exc_operand/exc_operand1
exceptions/exc_operand/exc_operand2
exceptions/exc_ref
exceptions/exc_result/exc_result2
exceptions/exc_tbl
functional/control
functional/descriptor
functional/external
functional/manipulation
functional/name
functional/reference
functional/region
functional/table
Identity2MS/abbu
IMPL/ACPICA/tests/dynobj
```

## 根因分析

这些 FAIL **不是**测试运行时问题（GNU Bash 5.3 + install→mkdir + mkfifo 绕法已让逐 case 真跑通），而是 **iasl 本身在鸿蒙 clang/libc++ 工具链上的编译回归**：

- `iasl -ta`（编译 ASL→AML）对某些 case 的 MAIN.asl 失败 → `Unexpected iASL failure`
- `iasl -d`（反汇编 AML→DSL）后重编 DSL→AML 失败 → `[[ Error: re-compilation of X-.dsl failed ]]`
- `iasl -p X-extInPlace -oE`（externals in place 编）失败 → `[[ Error: compiling X.aml with externals in place failed ]]`

这些是 iasl/ACPICA 上游在鸿蒙 clang 15 + libc++ C++17 工具链上的真兼容回归，**不是** aslts.sh 跑不通——aslts.sh 跑完了、逐 case 真执行了、失败被真统计出来了。

## 可行方向（等用户决策）

1. **上游 iasl clang/libc++ 兼容修复**：调查 24 个 case 的 iasl 编译失败根因（可能是 clang 某警告升级为错、或 libc++ 某头缺失），补 iasl 编译补丁让 104 FAIL→0。
2. **容忍已知失败**：在 manifest 标 `known_failures: [24 case list]`，配方统计时把已知失败排除出 fail 计数（但**不能**假装通过）。
3. **放弃适配**：鸿蒙真机 iasl 在这 24 个 case 上有真回归，本轮无法绕过。

本轮不推 feat 分支（104 FAIL ≠ 0），等用户检查验证分支后定夺方向。
