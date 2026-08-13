# bison 2.7 HarmonyOS PC adaptation

## Scope

GNU Bison is an LALR/GLR parser generator. This recipe targets the native
`bison` command on OpenHarmony PC aarch64.

## Upstream

- Source: https://ftp.gnu.org/gnu/bison/bison-2.7.tar.gz
- Build system: Autotools
- Upstream test command: `make check -j1`
- Test counts: to be recorded from the AtomCode real-device run; no result is
  claimed before that run.

## HarmonyOS changes

1. `0001-build-aux-config.guess.patch` recognizes the HarmonyOS aarch64 host.
2. `0002-src-scan-gram.c.patch` fixes the generated grammar scanner for the
   OHOS compiler.
3. `0003-src-system.h.patch` declares gnulib multibyte helpers missing from
   the OHOS build.

The recipe uses the `aarch64-linux-ohos` host triplet, clang, and single-job
builds. It does not use absolute local paths or prebuilt binaries.

## Consumer test

`test_package/test.sh` checks the installed version, generates a parser from a
small grammar, compiles it with clang, and executes it against a functional
assertion.

## Verification state

The package is on the validation branch. `make check -j1` and the consumer test
must both complete on the AtomCode OpenHarmony PC device before a formal branch
is created.
