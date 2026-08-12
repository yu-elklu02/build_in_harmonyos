# aggdraw 1.4.1

aggdraw is a CPython C++ extension exposing anti-aliased vector drawing
primitives.  Version 1.4.1 requires Python 3.11 or newer and is built by
setuptools.

## Source and dependencies

- Upstream: https://github.com/pytroll/aggdraw
- Source archive: PyPI sdist, fixed by SHA256 in `conandata.yml`.
- W0 dependency check: no Conan dependencies are declared by this recipe.
- The sdist contains no upstream test directory or `make test`/CTest target.

## Packaging

The recipe builds the C++ extension through the device Python and installs it
to a package-local staging directory.  `package_info()` exposes that directory
through `PYTHONPATH`, so the consumer test imports the packaged extension rather
than the source tree.

The OHOS CI SDK `lld` loads an incompatible `libxml2.so.16`, so the recipe
selects the HNP linker through `-fuse-ld=/data/service/hnp/bin/ld`.

## Consumer test

`test_package/test_aggdraw.py` imports the packaged native module, checks its
version, builds a closed vector path, and creates Pen and Brush objects.

## 鸿蒙真机适配（3 处拦点）

aggdraw 上游是纯 setuptools 配方，鸿蒙真机复验撞 3 处鸿蒙特定拦点，配方在 `build()` / `test_package test()` 段用环境变量绕法处理：

| # | 拦点 | 根因 | 修法 |
|---|---|---|---|
| 1 | `command 'c++' failed: No such file or directory` | 鸿蒙 python_3.12 编译时把 `CXX="c++"` 硬编码进 sysconfig；setuptools build_ext 走 `sysconfig.get_config_var('CXX')` 拿 `c++` 当编译器名，但真机 PATH 只装了 `clang`/`clang++`、无 `c++` 软链接 | `build()` 段命令行内联 `env CXX=clang++` 覆盖 sysconfig 默认（同 `LDSHARED` 也从硬编码的 `cc -shared` 换成 `clang++ -shared`） |
| 2 | `ImportError: Error relocating aggdraw.cpython-312.so: PyModule_Create2: symbol not found` | 鸿蒙 python3.12 主程**静态编进 libpython**、不 export Python C-API 符号给 extension；aggdraw.so 的 NEEDED 只有 `libc++_shared.so`/`libc.so`，运行时找 `PyModule_Create2` 就空 | `build()` 段给 `LDSHARED` + `LDFLAGS` 加 `-L<python_lib_dir> -lpython3.12`，让 aggdraw.so 链鸿蒙自带的 `libpython3.12.so`（它真 export `PyModule_Create2`：`nm -D` 显 `0000000000291288 T PyModule_Create2`），符号运行时从 libpython3.12.so 找到 |
| 3 | `ModuleNotFoundError: No module named 'aggdraw'` | 上游 `test()` 段用 conan `self.run(..., env=[f"PYTHONPATH={package_folder}"])` 注环境变量，但 conan `self.run` 的 `env` 参数只接预定义 scope 名（`conanrun`/`conanbuild`），不接 `["PYTHONPATH=..."]` 列表 | `test()` 段命令行内联 `env PYTHONPATH=<package_folder> python3 test_aggdraw.py` 绕 conan `self.run` env 参数限制 |

另：aggdraw setup.py 的 freetype 探测**非致命**——`=== freetype not available` 是警告、extension 照编（只是关字体支持），鸿蒙真机无 freetype-config/pkgconfig 也能编，故配方未声明 freetype 依赖。

## 构建状态

- [x] SHA256 已填写
- [x] W0 依赖检查通过（无 Conan 依赖）
- [x] conan create 通过（exit 0、aggdraw.cpython-312.so 真编出来）
- [x] test_package 执行通过（`aggdraw native Path/Pen/Brush API: PASSED`）
- [x] aggdraw.so 链 libpython3.12.so（PyModule_Create2 符号运行时解析）
- [x] 鸿蒙真机复验通过（HarmonyOS HongMeng Kernel 1.12.0 aarch64, clang 15.0.4, python 3.12）
