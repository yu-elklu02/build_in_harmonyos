# boost1.84-unit_test_framework 适配说明

Boost.Build 在 OHOS 上不可用，本配方直接编译 Boost.Test 的 19 个实现源文件，
生成 `libboost_unit_test_framework.a`，并安装完整 Boost 头文件树。

真机验证执行 `libs/test/test` 下的 299 个上游 b2 目标。AArch64 上
`system-exception-test` 的整数除零不产生 SIGFPE，按 E215 作为平台门控记录；
其余 298 个目标通过。`algorithm-test`、`message-in-datatestcase-test`、
`assertion-construction-test` 和 `doc-exception_check` 的 Boost.Build 调用会
错误注入 `--target=arm64-pc-linux`，使 OHOS clang 找不到 `cstddef`，或错误地
no-op；按 E216 移除该参数后，真机直编、链接和运行稳定通过。消费者测试
通过 `Boost::unit_test_framework` 真实链接并运行一个 Boost.Test 测试模块，
3 个断言全部通过，`conan create` 在 OHOS aarch64 上返回 0。

验证环境为 clang 15 + libc++，未发现 SELinux、seclabel 或执行权限 denial。
