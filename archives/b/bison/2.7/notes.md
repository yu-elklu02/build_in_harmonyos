# bison 2.7 HarmonyOS PC adaptation

## Scope

GNU Bison is an LALR/GLR parser generator. This recipe targets the native
`bison` command on OpenHarmony PC aarch64.

## Upstream

- Source: https://ftp.gnu.org/gnu/bison/bison-2.7.tar.gz
- Build system: Autotools
- Upstream test command: `make check -j1`
- Real-device result: 279/293 passed (95.2%), 14 failed, 0 skipped.
- The 14 remaining failures are split into three confirmed classes:
  4 `%define` diagnostic SIGSEGV failures, 2 RTC box-drawing output diffs,
  and 8 IELR/LAC state-splitting mismatches.

## HarmonyOS changes

1. `0001-build-aux-config.guess.patch` recognizes the HarmonyOS aarch64 host.
2. `0002-src-scan-gram.c.patch` fixes the generated grammar scanner for the
   OHOS compiler.
3. `0003-src-system.h.patch` declares gnulib multibyte helpers missing from
   the OHOS build.
4. `source()` makes the bundled configure helper scripts executable and
   teaches `config.sub` to accept the OHOS host triplet with Python text
   replacement. This avoids the old patch's line-ending and continuation
   issues on the vendored script.
5. `0005-configure-ohos-umask.patch` avoids the HMDFS temporary-directory
   permission failure during configure.
6. `0006-lib-math-noexcept.patch` aligns gnulib's generated C++ math overloads
   with OHOS libc++ by using `bool` return types and `noexcept` declarations.
7. `0007-location-null-file-ohos.patch` guards Bison's diagnostic location
   printer against empty location file names exposed by the OHOS `%define`
   error-reporting path.

The recipe uses the `aarch64-linux-ohos` host triplet, clang, and single-job
builds. On OHOS, Bison itself is compiled with `-O0 -fno-strict-aliasing` so
its legacy grammar-analysis C code is not exposed to aggressive alias-based
optimization. It does not use absolute local paths or prebuilt binaries.

## Consumer test

`test_package/test_bison.py` uses absolute bison and clang paths and Python
subprocesses, avoiding the restricted Conan run environment. It checks the
installed version, generates a parser from a small grammar, compiles it with
clang, and executes it against a functional assertion.

## Verification state

The package remains blocked because the upstream regression suite still has
non-zero failures. The next validation run checks whether the location guard
removes the 4 `%define` SIGSEGV failures; the 2 RTC output diffs and 8
IELR/LAC mismatches remain under investigation. No formal branch is created
while failures remain.
