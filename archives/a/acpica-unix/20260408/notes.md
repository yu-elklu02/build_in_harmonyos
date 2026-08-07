# ACPICA Unix 20260408

The package builds the upstream `iasl` compiler/disassembler. ACPICA's Unix
makefiles default to `_CYGWIN` for an unrecognised uname, so the recipe passes
`ACPI_HOST=_LINUX` explicitly for HarmonyOS.

The upstream ASL test-suite is `tests/aslts.sh`. It is declared in the test
manifest but is not invoked by `conan create`; the package-level true-device
test passed 1/1 by compiling, disassembling, and checking the restored ASL.
