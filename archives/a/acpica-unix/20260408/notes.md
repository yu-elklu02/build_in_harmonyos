# ACPICA Unix 20260408

The package builds the upstream `iasl` compiler/disassembler. ACPICA's Unix
makefiles default to `_CYGWIN` for an unrecognised uname, so the recipe passes
`ACPI_HOST=_LINUX` explicitly for HarmonyOS.

The upstream ASL test-suite is `tests/aslts.sh`. It is not invoked by CI
because the standard OHOS worker uses Toybox `/bin/sh`, which prevents the
suite's nested Bash result aggregation. It must be run separately by test
personnel in a full GNU Bash environment. The package-level test passed 1/1
by compiling, disassembling, and checking the restored ASL.
