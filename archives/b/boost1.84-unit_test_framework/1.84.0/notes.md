# boost1.84-unit_test_framework 适配说明

Boost.Build 在 OHOS 上不可用，本配方直接编译 Boost.Test 的 19 个实现源文件，
生成 `libboost_unit_test_framework.a`，并安装完整 Boost 头文件树。

构建阶段执行上游 `libs/test/test/writing-test-ts/test_tools-test.cpp`，在
`libs/test/test` 工作目录中完成 32 个 case 和 baseline 输出比对；消费者测试
通过 `Boost::unit_test_framework` 真实链接并运行一个 Boost.Test 测试模块，
3 个断言全部通过，`conan create` 在 OHOS aarch64 上返回 0。

验证环境为 clang 15 + libc++，未发现 SELinux、seclabel 或执行权限 denial。
