# ispell 3.4.06 适配笔记

## 概述

ispell 是经典的 Unix 交互式拼写检查器，纯 C 实现，依赖 ncurses 提供终端 UI。
构建系统为传统 Makefile，无 configure 脚本，需要手动配置 `local.h`。

## 关键适配点

### 1. SHA256 填写

真机首次运行前：

```bash
curl -L https://www.cs.hmc.edu/~geoff/ispell/ispell-3.4.06.tar.gz \
     -o ~/tmp/ispell.tar.gz && sha256sum ~/tmp/ispell.tar.gz
```

将哈希填入 `conandata.yml` 的 `sha256` 字段。

### 2. local.h 配置

ispell 需要 `local.h`（从 `local.h.samp` 复制）才能编译。
配方在 `source()` 中自动完成此步骤。

Makefile 支持通过命令行变量覆盖 `local.h` 中的设置，已设置：
- `CC` → 从 Conan toolchain conf 获取的 clang
- `TERMLIB` → `-lncursesw`
- `TERMINCLUDE` → ncurses 包的 include 路径
- `LANGUAGES=""` → 跳过需要 Perl 和 wordlist 数据的语言字典构建

### 3. ncurses 依赖

ispell 使用宽字符 ncurses（`libncursesw`），依赖 `ncurses/6.5`。
需要先确认此依赖已发布到 OHOS Conan 制品仓：

```bash
conan download "ncurses/6.5" -r=ohpcd --only-recipe && echo "OK"
```

若未发布，需先适配 ncurses/6.5。

### 4. LANGUAGES="" 的含义

ispell 上游 Makefile 在 `make install` 时会尝试安装英语词典（需要 Perl + 数据文件）。
通过传递 `LANGUAGES=""` 跳过此步骤，只安装核心二进制工具。
用户自行安装词典（如 `iamerican`、`ibritish` 等包）。

### 5. 可能的 OHOS 适配问题

- `strlcpy`/`strlcat`：musl 提供，应无问题
- `HAVE_GETTIMEOFDAY`、`HAVE_STDLIB_H` 等：标准头文件，OHOS 应支持
- 链接器：如遇 BFD linker 问题，需在 LDFLAGS 里指定 `-fuse-ld=bfd`

## 构建状态

- [ ] SHA256 已填写
- [ ] W0 依赖检查通过（ncurses/6.5 在制品仓）
- [ ] conan create 通过
- [ ] test_package 执行通过
