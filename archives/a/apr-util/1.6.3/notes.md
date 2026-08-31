# apr-util 1.6.3 适配说明

本配方使用 Autotools 构建 APR-util，依赖 APR 1.7.6 和 Expat 2.8.2。
OHOS 构建显式使用 profile shell，并应用 config.guess/config.sub 与
configure 临时目录权限补丁。

构建时执行 `make check`，test_package 通过 APR-util 的 XML parser 公共
API 创建解析器，验证头文件、链接库和运行时均可用。
