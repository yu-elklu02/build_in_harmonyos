# AutoDock Vina 1.2.7

## Source

- Upstream: https://github.com/ccsb-scripps/AutoDock-Vina
- Tag: `v1.2.7`
- Build system: the upstream Linux release Makefile

## OHOS adaptation

The upstream Makefile assumes `/usr` and `g++`. The Conan recipe redirects
those paths to the published Boost 1.84.0 package and the Conan compiler, disables
the upstream static-link default, adds an OHOS-compatible RUNPATH, and passes
the profile shell to `make`.

Boost 1.90.0.1 was checked first but its published OHOS package omits the
`boost/log` and `boost/ptr_container` headers required by Vina. The published
OHOS Boost 1.84.0 package contains both components and is used instead.

The release contains no automated upstream test target. The Conan test package
therefore performs two real CLI assertions: `vina --version` and `vina --help`.
