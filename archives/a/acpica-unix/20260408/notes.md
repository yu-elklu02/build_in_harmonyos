# ACPICA Unix 20260408

The package builds the upstream `iasl` compiler/disassembler. ACPICA's Unix
makefiles default to `_CYGWIN` for an unrecognised uname, so the recipe passes
`ACPI_HOST=_LINUX` explicitly for HarmonyOS.

The upstream ASL test-suite is `tests/aslts.sh`. Its true-device result and
case count must be recorded before this version is promoted from `draft`.
