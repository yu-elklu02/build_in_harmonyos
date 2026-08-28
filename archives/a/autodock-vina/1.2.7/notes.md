# AutoDock Vina 1.2.7

## Source

- Upstream: https://github.com/ccsb-scripps/AutoDock-Vina
- Tag: `v1.2.7`
- Build system: the upstream Linux release Makefile

## OHOS adaptation

The upstream Makefile assumes `/usr` and `g++`. The Conan recipe redirects
those paths to the published Boost package and the Conan compiler, disables
the upstream static-link default, adds an OHOS-compatible RUNPATH, and passes
the profile shell to `make`.

The release contains no automated upstream test target. The Conan test package
therefore performs two real CLI assertions: `vina --version` and `vina --help`.

