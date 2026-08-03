from conan import ConanFile
from conan.tools.build import cross_building
from conan.tools.files import get
import os


class Qt5QtDeclarativeConan(ConanFile):
    name = "qt5-qtdeclarative"
    version = "5.15.2"
    description = "Qt QML and Qt Quick modules for Qt 5"
    homepage = "https://www.qt.io/"
    license = "LGPL-3.0-only OR GPL-2.0-only"
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires("qt5-qtbase/5.15.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        qmake = os.path.join(
            self.dependencies["qt5-qtbase"].package_folder, "bin", "qmake"
        )
        args = [
            qmake,
            "qtdeclarative.pro",
            "-spec",
            "harmonyos-clang",
            "-prefix",
            self.package_folder,
        ]
        self.run(" ".join('"{}"'.format(arg) for arg in args), cwd=self.source_folder)
        jobs = "-j1" if cross_building(self) else "-j2"
        self.run("make {}".format(jobs), cwd=self.source_folder)

    def package(self):
        self.run("make install", cwd=self.source_folder)

    def package_info(self):
        self.cpp_info.requires = ["qt5-qtbase::qt5-qtbase"]
        self.cpp_info.libs = [
            "Qt5Qml",
            "Qt5QmlModels",
            "Qt5Quick",
            "Qt5QuickParticles",
            "Qt5QuickShapes",
            "Qt5QuickTest",
            "Qt5QuickWidgets",
            "Qt5QuickControls2",
            "Qt5QuickTemplates2",
        ]
        self.cpp_info.set_property("cmake_file_name", "Qt5QtDeclarative")
        self.cpp_info.set_property(
            "cmake_target_name", "Qt5QtDeclarative::Qt5Qml"
        )
