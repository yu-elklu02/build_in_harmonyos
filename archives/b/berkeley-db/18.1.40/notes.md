# Berkeley DB 18.1.40

The build enables the upstream Tcl API and executes the upstream Tcl regression
suite with `test.tcl`'s `run_all` entry point. This requires the published
OHOS `tcl/9.0.3.1` package, including its target `tclsh`, shared library, and
relocated `tclConfig.sh`.

The upstream Tcl module link rule does not normally retain the Tcl runtime as
an ELF dependency. A portability patch adds Tcl's configured link flags to
`libdb_tcl`, so the module can be loaded by the target `tclsh` on OHOS.

The recipe builds the C and Tcl APIs from `dist/configure` for OHOS armv8.
Java and SQL bindings remain disabled because they require runtimes unavailable
in the target package build.

The upstream `test_mutex` binary is built during `build()`. On device, run
`./test_mutex -p 2 -n 10 -l 10`; success prints `test succeeded`.

The bundled Autoconf `config.status` creates temporary AWK scripts with mode
0700. On HMDFS this prevents the script reader from accessing them, so the
recipe applies a portability patch that creates the temporary directory with
mode 0755 instead.

The source archive does not contain every entry listed by `install_docs`.
The package installs headers, libraries, and standard utilities but omits
those unavailable documentation files.
