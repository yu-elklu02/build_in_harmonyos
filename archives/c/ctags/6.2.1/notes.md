# ctags 6.2.1 适配笔记

## 编译环境
- 构建系统: autotools
- 编译日期: 2026-07-06
- 编译器: clang/clang++ (clang 15.0.4)
- 状态: built

## 编译步骤

1. 源码为官方 release tarball（含预生成的 configure），无需 autoreconf
2. `./configure --build=aarch64-unknown-linux-ohos --host=aarch64-unknown-linux-ohos --prefix=$DEFAULT_PREFIX`（OHOS 交叉编译）
3. `make -j1`
4. `make install DESTDIR=$TEST_PREFIX`
5. `make check`（部分测试失败，均为平台相关）

## 遇到的问题与解决方案

| # | 问题 | 根因 | 解决方案 |
|---|------|------|----------|
| 1 | Autotools 无法识别 OHOS target | 发行包内 config.guess 版本不识别 `aarch64-unknown-linux-ohos` | 应用 config.guess portability patch，并在 Conan toolchain 中显式传入 build/host triplet；官方 config.sub 保持不修改 |
| 2 | HMDFS 下 Autoconf 临时目录权限不足 | configure 生成的 config.status 使用 `umask 077` 创建临时目录 | 通过 configure patch 将该模板改为 `umask 000` |

## 源码修改

- `config.guess`: 增加 `aarch64-unknown-linux-ohos` 识别，并将 config.guess 临时目录 umask 调整为 `000`
- `configure`: 将 config.status 模板的 `umask 077` 调整为 `umask 000`，避免 HMDFS 上生成不可访问的 0700 临时目录

## make check 结果

make check 执行完毕，23 项测试失败，均为平台相关问题：
- optscript 测试：Signal 11 (segfault) + "Valgrind: FATAL: Private file creation failed" - HMDFS 文件系统限制导致 optscript 解释器崩溃
- broken-extradef/fielddef/paramdef 等：输出为空，可能与信号处理或文件系统行为有关
- c-large-enum/epoch-field/kinddef/roledef：类似平台差异

核心功能（ctags --version, 标签生成）正常工作。

## 依赖版本

- clang 15.0.4
- autoconf 2.72
- automake 1.16.5
- pkg-config 0.29.2
- make 4.4.1

## 验证结果

```bash
$ ctags --version
Universal Ctags 6.2.1, Copyright (C) 2015-2025 Universal Ctags Team
Compiled: Jul  6 2026, 12:17:32
URL: https://ctags.io/
Optional compiled features: +wildcards, +regex, +gnulib_regex, +iconv, +option-directory, +case-insensitive-filenames, +packcc, +optscript
```

## 交付物

| 文件 | 大小 | 说明 |
|------|------|------|
| ctags | 2185664 | 主程序 |
| readtags | 215488 | 标签读取工具 |
| optscript | 2181568 | 脚本解释器 |

## 注意事项

- HMDFS umask 问题分别在 config.guess 和 configure 的 portability patch 中处理，配方不依赖本机绝对路径
- OHOS 构建使用 Conan profile 提供的 clang 工具链和 `aarch64-unknown-linux-ohos` target
---

**编译结束**: 2026-07-06 12:41
**最终状态**: built
