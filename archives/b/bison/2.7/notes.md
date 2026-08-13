# bison 2.7 HarmonyOS PC adaptation

## Scope

GNU Bison is an LALR/GLR parser generator. This recipe targets the native
`bison` command on OpenHarmony PC aarch64.

## Upstream

- Source: https://ftp.gnu.org/gnu/bison/bison-2.7.tar.gz
- Build system: Autotools
- Upstream test command: `make check -j1`
- Real-device result: 279/293 passed (95.2%), 14 failed, 0 skipped.
- The 14 failed cases are `%define`-related bison segmentation faults on OHOS.

## HarmonyOS changes

1. `0001-build-aux-config.guess.patch` recognizes the HarmonyOS aarch64 host.
2. `0002-src-scan-gram.c.patch` fixes the generated grammar scanner for the
   OHOS compiler.
3. `0003-src-system.h.patch` declares gnulib multibyte helpers missing from
   the OHOS build.
4. `0004-build-aux-config.sub-ohos.patch` accepts the OHOS host triplet.
5. `0005-configure-ohos-umask.patch` avoids the HMDFS temporary-directory
   permission failure during configure.

The recipe uses the `aarch64-linux-ohos` host triplet, clang, and single-job
builds. It does not use absolute local paths or prebuilt binaries.

## Consumer test

`test_package/test.sh` is POSIX `sh`; it checks the installed version, generates
 a parser from a small grammar, compiles it with clang, and executes it against
 a functional assertion.

## Verification state

The package remains blocked because the upstream regression suite has 14 real
segmentation-fault failures. No formal branch is created while they remain.
