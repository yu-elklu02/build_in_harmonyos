# Avida 2.12.4

The official release archive from SourceForge is required because the GitHub tag
uses submodules and its generated tarball omits `avida-core`.

The command-line interface is built with the ncurses viewer disabled. The bundled
`tcmalloc-1.4` component is disabled for OHOS armv8 because its implementation
contains x86-specific assembly.

The upstream `run_tests` wrapper depends on `/bin/sh` and its Python 2 test
scripts use obsolete syntax. The recipe runs Python 3 `lib2to3` over the
`avida-core/tests` tree and invokes the original `testrunner.py` directly,
preserving the upstream test discovery and result reporting without the shell
wrapper. The removed Python 2 `dircache` module is replaced with an
`os.listdir` compatibility shim. The device log is the source of truth for the
final test count.

The migration also repairs the upstream testrunner's malformed
`testrunner-name` long-option declaration so Python 3 `getopt` accepts the
original runner option.

Python 3's `configparser` makes `raw` and `vars` keyword-only, while Avida's
Python 2 runner passes them positionally. The compatibility wrapper preserves
the original call contract so each `test_list` is read rather than silently
falling back to defaults. The runner writes an XML report so the test total,
passed, failed, and disabled counts are recorded from actual execution.

## HarmonyOS validation (2026-08-24)

The OHOS armv8 `conan create` completed with `EXIT=0`. The upstream runner's
XML report recorded `tests=1`, `failures=0`, and `disabled=0`; the selected
`string_producing_and_donating` consistency test passed. The remaining source
test directories were not selected by this `run_tests` mode, so they are not
claimed as executed. The `test_package` compiled and executed `avida --help`,
printing `avida help assertion passed`.

The upstream `testrunner.cfg` refers to its historical `cbuild/work/avida`
location. Before executing tests, the recipe rewrites only that configuration
value to Conan's current `build/bin/avida` output path.

Several upstream `test_list` files also carry Python 2 era inline comments or
placeholder typos on their `app =` lines. The recipe strips those comments and
normalizes the known `%(app)s` / `%(defailt_app)s` cases so the runner can
discover and execute the full consistency-test set.

The compatibility `ConfigParser.get()` wrapper also preserves Python 2's
missing-option exception behavior. This matters for the upstream
`string_producing_and_donating` directory, which has a config directory but no
`test_list`; the original runner catches the missing option and uses the
default Avida executable.

The Python 2 universal-newline mode `open(filename, "U")` is also rewritten to
ordinary text mode `"r"`, which has universal-newline behavior by default in
Python 3.

The removed Python 2 `string.lstrip()` helper is rewritten to the equivalent
`str.lstrip()` method in the test runner.

The config parser wrapper strips inline `;` comments from every returned value,
matching Python 2 `ConfigParser` semantics. This preserves `enabled = yes`
and the other per-test flags in the upstream `test_list` files.

The upstream runner is invoked with `-j 1 --long-tests --verbose` on OHOS. Its
test subprocess shell is explicitly set to `/data/service/hnp/bin/bash`
instead of the unavailable `/bin/sh`. Serial
execution avoids concurrent Avida processes competing for the device sandbox,
and `--long-tests` includes the seven tests normally skipped by default.

Patch `0003-analyze-child-library-path.patch` preserves the OHOS runtime
library path before analyze scripts invoke child Avida processes through
`system()`.

The runner's Python 2 wait-status decoding is also adapted for Python 3's
direct `Popen.wait()` return code. The `analyze_resize_max_batches` fixture is
an intentional nonzero test (its final command is documented as "Should fail"),
so its migrated `test_list` uses `nonzeroexit = require`.

When a consistency test has output variance, the migrated runner preserves its
actual output under `avida-upstream-failures/<test-name>` in the build folder.
These artifacts are required before adding any OHOS-specific baseline; the
recipe does not silently replace upstream expected files.

Run device validation with:

```bash
conan create archives/a/avida/2.12.4 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
