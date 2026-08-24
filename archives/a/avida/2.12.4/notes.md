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

The initial OHOS armv8 `conan create` completed with `EXIT=0`, but its Python 3
migration did not preserve the legacy `ConfigParser.get()` positional API.
That made the runner report an empty consistency-test selection, so the result
cannot be used as the upstream test statistic. The corrected runner discovers
68 upstream consistency tests and emits `avida-upstream-tests.xml`; the next
OHOS validation must provide its actual pass/fail count before PR metadata is
finalized. The existing `test_package` compiled and executed `avida --help`,
printing `avida help assertion passed`.

The upstream `testrunner.cfg` refers to its historical `cbuild/work/avida`
location. Before executing tests, the recipe rewrites only that configuration
value to Conan's current `build/bin/avida` output path.

Several upstream `test_list` files also carry Python 2 era inline comments or
placeholder typos on their `app =` lines. The recipe strips those comments and
normalizes the known `%(app)s` / `%(defailt_app)s` cases so the runner can
discover and execute the full consistency-test set.

Run device validation with:

```bash
conan create archives/a/avida/2.12.4 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
