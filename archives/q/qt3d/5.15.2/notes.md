# qt3d 5.15.2 adaptation notes

## Build environment

- Target: OpenHarmony aarch64
- Build system: qmake + make
- Qt prefix: `/storage/Users/currentUser/usr/local/Qt5`
- Qt dependency: Worker-provided system installation (not a Conan requirement)

## Adaptation

The source builds as a Qt 5 addon module without source patches. qmake enables the
Quick3D submodules only when the Qt installation exposes the Qt Quick module.
`QMAKE_STRIP` is kept empty so the generated shared libraries remain loadable on OHOS.

The qmake install tree is staged with `INSTALL_ROOT`, then Qt3D libraries, headers,
module metadata and optional plugins are copied into a normal Conan package layout.
The CI artifact registry does not contain `qt/5.15.2`, so declaring that old wrapper
reference would fail dependency resolution before the build starts.

## Tests

The upstream archive contains 251 `tst_*.cpp` programs under `tests/auto`. They are
not built in this basic-adaptation path because many require private Qt modules,
graphics services and platform plugins that are unavailable on the worker.

The Conan consumer test compiles and runs a small Qt3D Core application. It checks
the entity parent relationship and component attachment, proving that headers,
linkage and runtime loading work through the packaged artifact.

## Result

- Source checksum verified locally: pass
- Recipe/YAML static checks: pending
- OHOS build and consumer test: pending CI
