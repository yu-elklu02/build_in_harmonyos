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

When no consistency tests are selected, the upstream runner returns two
counters while its caller expects success, disabled, and failure counters. The
compatibility step normalizes that empty result to a three-counter tuple.

## HarmonyOS validation (2026-08-24)

The OHOS armv8 `conan create` completed with `EXIT=0`. The upstream runner
completed with `All tests passed`; its selected consistency-test set was empty,
so it reported zero failures and no countable consistency cases. The
`test_package` compiled and executed `avida --help`, printing `avida help
assertion passed`.

Run device validation with:

```bash
conan create archives/a/avida/2.12.4 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
