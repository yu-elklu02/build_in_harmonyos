# Berkeley DB 18.1.40

The recipe builds the C API from `dist/configure` for OHOS armv8. Java, Tcl,
and SQL bindings are disabled because they require host runtimes unavailable in
the target package build.

The upstream `test_mutex` binary is built during `build()`. On device, run
`./test_mutex -p 2 -n 10 -l 10`; success prints `test succeeded`.
