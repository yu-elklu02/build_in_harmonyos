# boost1.84-unit_test_framework 适配说明

Boost.Build 在 OHOS 上不可用，本配方直接编译 Boost.Test 的 19 个实现源文件，
生成 `libboost_unit_test_framework.a`，并安装完整 Boost 头文件树。

构建阶段执行上游 `libs/test/test/test_tools_test.cpp`，消费者测试通过
`Boost::unit_test_framework` 真实链接并运行一个 Boost.Test 测试模块。

当前版本未声明未经设备实际执行的通过率；真机验证后应将实际结果回填到
`manifest.yaml` 和 `test_package/MANIFEST.yml`。
