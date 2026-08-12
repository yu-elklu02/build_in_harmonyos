# mawk 1.3.4-20260302-a273-v2

mawk is a standalone AWK interpreter implemented in C. It uses Autotools and
has no Conan runtime or build requirements. On HarmonyOS the recipe passes an
explicit `aarch64-linux-ohos` host triplet because the upstream config.guess
does not recognize HarmonyOS directly, while config.sub accepts linux-ohos.

The upstream `make check` suite and the installed-package consumer assertions
must be updated with real-device results before the formal branch is pushed.
