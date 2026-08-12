# Known Limitations

## Upstream ASLTS on HarmonyOS

The upstream `tests/aslts.sh` suite completes on HarmonyOS with GNU Bash 5.3,
`CC=clang`, `MAKEFLAGS=-j1`, and a writable `TMPDIR`. The auditable result is
recorded from per-case-by-mode Compile entries in `aslts-run.log`:

| Cases | Passed | Failed | Skipped | Pass rate |
|---:|---:|---:|---:|---:|
| 188 | 84 | 104 | 0 | 44.7% |

The 104 failures are not counted as passes. They are upstream `iasl` compiler
regressions observed on the HarmonyOS clang 15/libc++ toolchain, including
ASL-to-AML compilation, disassembled DSL recompilation, and external-symbol
compilation. The packaged `iasl` consumer test independently passes its ASL
compile and disassemble round trip.

Affected upstream case groups include `bdemo`, `namespace`, `exc`, `control`,
`descriptor`, `manipulation`, `name`, `reference`, `region`, `table`,
`external`, `oconversion`, `rcopyobject`, `rexplicitconv`, `rindecrement`,
`roptional`, `rstore`, `exc_operand1`, `exc_operand2`, `exc_ref`,
`exc_result2`, `exc_tbl`, `Identity2MS`, and `IMPL-dynobj`.
