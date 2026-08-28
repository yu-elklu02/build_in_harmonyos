# AutoDock Vina 1.2.7

## Source

- Upstream: https://github.com/ccsb-scripps/AutoDock-Vina
- Tag: `v1.2.7`
- Build system: the upstream Linux release Makefile

## OHOS adaptation

The upstream Makefile assumes `/usr` and `g++`. The Conan recipe redirects
those paths to the published Boost packages and the Conan compiler, disables
the upstream static-link default, adds an OHOS-compatible RUNPATH, and passes
the profile shell to `make`.

Boost 1.90.0.1 supplies the compiled libraries, but its published OHOS package
omits the `boost/log` and `boost/ptr_container` headers required by Vina. The
published OHOS Boost 1.84.0 package contains both components, so the recipe
uses it as a build-context header provider while retaining 1.90.0.1 for host
link libraries.

OHOS musl does not declare `pthread_setcancelstate`, which Boost 1.84.0
references from `boost/core/detail/sp_thread_sleep.hpp`. The recipe adds
Boost's official `BOOST_SP_NO_PTHREAD_SETCANCELSTATE` compile-time switch on
OHOS to select the portable sleep path.

Boost.System is header-only since Boost 1.69. The upstream Makefile still
lists `-l boost_system`, so the recipe removes that obsolete linker argument
for the published OHOS Boost packages.

The release contains no automated upstream test target. The Conan test package
therefore performs two real CLI assertions: `vina --version` and `vina --help`.
