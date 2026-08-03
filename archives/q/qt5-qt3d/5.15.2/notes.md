# qt5-qt3d 5.15.2

## Source

- URL: https://github.com/qt/qt3d/archive/refs/tags/v5.15.2.tar.gz
- SHA256: 4752c8ea92070e742e5de4eae07b562e65f3e9ffe0e844f0f3830fe18162d5be

## Build

Qt3D is a Qt 5 qmake module. The recipe invokes the `qmake` shipped by
`qt5-qtbase`, uses the `harmonyos-clang` mkspec, and installs into the Conan
package folder. It requires `qt5-qtbase/5.15.2` and
`qt5-qtdeclarative/5.15.2`.

The recipe does not use an absolute host path or a source patch. Cross builds
use a single make job to avoid the OHOS jobserver limitation.

## Consumer test

`test_package` links against the generated Qt5Qt3D CMake target, creates a
`QEntity` parent/child hierarchy, attaches a `QTransform`, and asserts the
parent relationship, component count, and transform scale at runtime.

Device validation is pending.
