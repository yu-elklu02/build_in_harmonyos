# E337 - OHOS/aarch64 上 Python 2 上游测试框架迁移与子进程运行时适配

> Contributor: elklu02 | Team: 随便吧队 | Status: DRAFT | Created: 2026-08-25

## Reusable Pattern

老旧 C/C++ 第三方库的上游测试框架可能仍依赖 Python 2。迁移到 Python 3 后，除语法转换外，还需要处理已经移除的标准库 API、配置解析语义差异，以及 OHOS 子进程动态库加载和平台测试基线差异。

## Observed Failures

Avida 2.12.4 在 OHOS/aarch64 验证中先后出现：

- `ModuleNotFoundError: No module named 'dircache'`
- `ValueError: invalid mode: 'U'`
- `AttributeError: module 'string' has no attribute 'lstrip'`
- Python 2/3 `ConfigParser` 行内注释、插值和 fallback 行为不一致
- 子 Avida 通过 `system()` 启动时无法加载 `libc++_shared.so`
- aarch64 输出与上游 Linux golden baseline 不一致

## Recommended Solution

1. 使用 `lib2to3` 迁移上游 Python 2 测试树。
2. 对 `dircache`、`open("U")`、`string.lstrip` 提供窄范围兼容处理。
3. 保持 Python 2 `ConfigParser` 的调用约定和行内注释行为。
4. 直接调用上游测试运行器，使用 OHOS 可执行 shell。
5. 修复子进程运行时库路径继承，确保 `system()` 启动的子程序可加载共享库。
6. 先保存完整失败产物，再审核并加入 OHOS/aarch64 专用基线。
7. 对存在随机行为的测试固定随机种子，保证平台结果可复现。
8. 通过 XML 报告记录真实测试数量、失败数和 disabled 数量。

## Verification

Avida 2.12.4 在 HarmonyOS PC aarch64 上完成：

- `conan create`：`EXIT=0`
- 上游一致性测试：64/64 PASS
- XML：`tests=64 failures=0 disabled=0 errors=0`
- `test_package`：1/1 PASS
- 功能断言：`avida help assertion passed`

## Promotion Value

该方案可推广到使用 Python 2 测试脚本、配置文件驱动测试、`system()`/`fork()`/`exec()` 子进程、共享库运行时依赖和平台相关 golden baseline 的其他 C/C++ 第三方库。

## Related Knowledge

- E088：HarmonyOS musl namespace 与动态库加载路径
- 本条目新增：Python 2 测试运行器迁移、ConfigParser 兼容、上游测试基线和子进程运行时问题的组合诊断流程。
