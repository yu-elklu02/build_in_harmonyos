# ACPICA Unix 20260408

The package builds the upstream `iasl` compiler/disassembler. ACPICA's Unix
makefiles default to `_CYGWIN` for an unrecognised uname, so the recipe passes
`ACPI_HOST=_LINUX` explicitly for HarmonyOS.

The upstream ASL test-suite is `tests/aslts.sh` and is invoked by `build()`.
Its true-device case/pass count must be recorded after the validation rerun;
the package-level test already passed 1/1 by compiling, disassembling, and
checking the restored ASL.
