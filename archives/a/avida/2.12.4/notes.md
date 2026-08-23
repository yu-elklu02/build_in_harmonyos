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

Run device validation with:

```bash
conan create archives/a/avida/2.12.4 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
