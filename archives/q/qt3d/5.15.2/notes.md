# qt3d 5.15.2 adaptation notes

## Build environment

- Target: OpenHarmony aarch64
- Build system: qmake + make
- Qt prefix: `qt5-qtbase/5.15.2` Conan package directory
- Qt dependency: `qt5-qtbase/5.15.2` (merged into the registry)

## Adaptation

The source builds as a Qt 5 addon module without source patches. qmake enables the
Quick3D submodules only when the Qt installation exposes the Qt Quick module.
`QMAKE_STRIP` is kept empty so the generated shared libraries remain loadable on OHOS.

The qmake install tree is staged with `INSTALL_ROOT`, then Qt3D libraries, headers,
module metadata and optional plugins are copied into a normal Conan package layout.
The target CI resolves `qt5-qtbase/5.15.2` from the registry.

## Tests

The test package builds and runs the upstream non-graphical
`tests/auto/core/qaspectjob/tst_qaspectjob.cpp` suite against the packaged
Qt3D Core library. It covers Qt3D aspect-job dependency addition, removal and
expired-dependency cleanup without requiring graphics services, private Qt
modules or an OpenGL context. It is built through Conan-generated CMake targets
instead of qmake because the Qt5 dependency package does not ship qmake mkspecs.
The remaining upstream suites are not built in this basic-adaptation path because
many require private Qt modules, graphics services and platform plugins unavailable
on the worker.

The Conan consumer test compiles and runs a small Qt3D Core and Render application.
It checks the entity parent relationship, component attachment and a QRenderSettings
render-policy round trip, proving that the packaged Core and Render headers, linkage
and runtime loading work through the packaged artifact. This is not an EGL/OpenGL ES
rendering test: validating an offscreen frame submission requires an OHOS graphics
stack and remains outside this basic adaptation path.

## Result

- Source checksum verified: pass
- Recipe/YAML static checks: pass
- OHOS build and both test-package executables: pending CI validation
