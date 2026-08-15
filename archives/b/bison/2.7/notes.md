# bison 2.7 HarmonyOS PC adaptation

## Scope

GNU Bison is an LALR/GLR parser generator. This recipe targets the native
`bison` command on OpenHarmony PC aarch64.

## Upstream

- Source: https://ftp.gnu.org/gnu/bison/bison-2.7.tar.gz
- Build system: Autotools
- Upstream test command: `make check -j1`
- Upstream test scope: 293 GNU Bison 2.7 tests.

## Current verification state

The historical OHOS failures have been reduced to zero in targeted real-device
validation:

- 14 historical failing groups were re-run and all passed:
  `25/26/28/29/98/100/110/114/118/122/183/184/260/266`.
- The previous failure classes covered C++ `isnan` declarations, `%define`
  diagnostic location handling, IELR/LAC state splitting, and sed trace
  extraction portability.
- A direct `bison --version` check reports `bison (GNU Bison) 2.7`.

The final full `conan create` run is still pending a long-timeout environment:
the AtomCode sandbox killed the Conan stage at 300 seconds before the complete
293-test `make check`, install, and `test_package` stages could finish. This is
a sandbox timeout limitation, not a reproduced test failure. Do not claim a full
293/293 result until a long-timeout `conan create` or CI run completes.

## HarmonyOS changes

1. `0001-build-aux-config.guess.patch` recognizes the HarmonyOS aarch64 host.
2. `0002-src-scan-gram.c.patch` fixes the generated grammar scanner for the
   OHOS compiler.
3. `0003-src-system.h.patch` declares gnulib multibyte helpers missing from the
   OHOS build.
4. `source()` makes the bundled configure helper scripts executable and teaches
   `config.sub` to accept the OHOS host triplet with Python text replacement.
5. `0005-configure-ohos-umask.patch` avoids the HMDFS temporary-directory
   permission failure during configure.
6. `0006-lib-math-noexcept.patch` aligns gnulib's generated C++ math overloads
   with OHOS libc++ by using `bool` return types and `noexcept`, then avoids
   redefining libc++'s existing C++ `isnan` overloads under `_LIBCPP_VERSION`.
7. `0007-location-null-file-ohos.patch` guards Bison's diagnostic location
   printer against empty location file names, initializes decoded `%define`
   locations, and compares same-file diagnostics by string content rather than
   uniqstr pointer identity.
8. `0008-percent-define-loc-fallback-ohos.patch` stores raw `%define`
   diagnostic locations at insertion time and uses them as a fallback when the
   legacy location decoder returns an empty location on OHOS.
9. `0009-annotation-insert-side-effect-ohos.patch` keeps
   `AnnotationList__insertInto()` outside `aver/assert`, because OHOS release
   builds use `-DNDEBUG` and assert would otherwise remove the side-effect call.
10. `0010-sets-sed-explicit-quiet-ohos.patch` changes the grammar-set tests to
    call `sed -n -f extract.sed` explicitly instead of relying on sed's `#n`
    first-line extension, which is not portable to OHOS toybox sed.

The recipe uses the `aarch64-linux-ohos` host triplet, clang, and single-job
builds. On OHOS, Bison itself is compiled with `-O0 -fno-strict-aliasing` to
avoid exposing legacy grammar-analysis C code to aggressive alias-based
optimization. It does not use absolute local paths or prebuilt binaries.

## Consumer test

`test_package/test_bison.py` uses absolute bison and clang paths and Python
subprocesses, avoiding the restricted Conan run environment. It checks the
installed version, generates a parser from a small grammar, compiles it with
clang, and executes it against a functional assertion.

## Path B knowledge summary

This adaptation produced reusable OHOS compatibility knowledge for old GNU
toolchain projects:

1. Old gnulib math headers may declare C++ math overloads as `int` and without
   `noexcept`; OHOS libc++ declares `bool noexcept`, so return type and exception
   specification must match or the C++ skeleton build fails.
2. Legacy diagnostic location code may pass NULL file names into quoting or file
   open helpers. OHOS runs exposed those paths as SIGSEGV in `%define`
   diagnostics.
3. Old code may assume uniqstr pointer equality means string equality. On the
   OHOS fallback path, equal file names can have different pointers, so same-file
   diagnostics must compare string content.
4. Side effects inside `assert`/`aver` are unsafe under release builds with
   `-DNDEBUG`. Bison's IELR annotation insertion was removed by the macro and
   state splitting silently degraded.
5. Some old tests rely on sed's `#n` first-line extension to suppress default
   output. OHOS toybox sed does not behave like GNU sed here; use explicit
   `sed -n`.
