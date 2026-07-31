# jpeg-archive 2.2.0 适配笔记

## 概述

jpeg-archive 是一组 JPEG 优化工具，依赖 mozjpeg 进行高压缩率编码。
安装 4 个二进制工具：jpeg-recompress、jpeg-compare、jpeg-hash、jpeg-archive。

## 关键适配点

### 1. SHA256 填写

首次运行前需要在真机上计算 SHA256：

```bash
curl -L https://github.com/danielgtaylor/jpeg-archive/archive/refs/tags/v2.2.0.tar.gz \
     -o /tmp/ja.tar.gz && sha256sum /tmp/ja.tar.gz
```

将结果填入 `conandata.yml` 的 `sha256` 字段，再运行 `conan create`。

### 2. mozjpeg 依赖适配（FindJPEG 问题）

jpeg-archive 的 CMakeLists.txt 使用 `find_package(JPEG REQUIRED)`，
但 Conan 中 mozjpeg 包名为 `mozjpeg`（CMake target `mozjpeg::mozjpeg`），
FindJPEG 不会自动识别。

解决方案：在 `generate()` 中通过 CMakeToolchain 直接设置：
- `JPEG_LIBRARY` → mozjpeg 包目录的 `lib/libjpeg.a`
- `JPEG_INCLUDE_DIR` → mozjpeg 包目录的 `include`

CMake 的 FindJPEG 模块在 cache 变量已设置时会直接使用，不再搜索。

### 3. libpng / zlib 类似处理

同样通过 toolchain 变量：
- `PNG_LIBRARY`, `PNG_PNG_INCLUDE_PATH`
- `ZLIB_LIBRARY`, `ZLIB_INCLUDE_DIR`

### 4. cmake_minimum_required 兼容

上游 CMakeLists.txt 可能使用 2.x 旧语法，需要设置：
```
CMAKE_POLICY_VERSION_MINIMUM = 3.5
```

### 5. W0 依赖发布检查（重要）

适配前必须确认以下依赖已发布到 OHOS Conan 制品仓：
```bash
conan download "mozjpeg/4.1.1" -r=ohpcd --only-recipe
conan download "libpng/1.6.58" -r=ohpcd --only-recipe
```
如果 mozjpeg/4.1.1 的 MR 尚未合并，需先等待或从本地缓存构建。

## 构建状态

- [ ] SHA256 已填写
- [ ] conan create 通过
- [ ] test_package 执行通过
- [ ] 上游 ctest 通过（如适用）
