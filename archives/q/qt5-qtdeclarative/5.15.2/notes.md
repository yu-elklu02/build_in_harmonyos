# qt5-qtdeclarative 5.15.2

Qt Declarative is built as a Qt 5 qmake module using the `qmake` supplied by
`qt5-qtbase/5.15.2` and the `harmonyos-clang` mkspec. The package installs
QtQml and QtQuick libraries, headers, QML plugins, and tools into the Conan
package folder. Cross builds use one make job because the OHOS jobserver does
not support the usual FIFO implementation.

The consumer test creates a `QQmlEngine` and checks that its root context is
available at runtime. Device validation is pending.
