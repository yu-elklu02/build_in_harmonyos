from conan import ConanFile
from conan.tools.files import get
from conan.tools.build import cross_building
import os


class Qt5Qt3DConan(ConanFile):
    name = "qt5-qt3d"
    version = "5.15.2"
    description = "Qt 3D module for Qt 5"
    homepage = "https://www.qt.io/"
    license = "LGPL-3.0-only OR GPL-2.0-only"
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires("qt5-qtbase/5.15.2")
        self.requires("qt5-qtdeclarative/5.15.2")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        qtbase = self.dependencies["qt5-qtbase"].package_folder
        qtdeclarative = self.dependencies["qt5-qtdeclarative"].package_folder
        self._qmake = os.path.join(qtbase, "bin", "qmake")
        self._qt_prefix = qtbase
        self._qtdeclarative_prefix = qtdeclarative

    def build(self):
        qmake = os.path.join(
            self.dependencies["qt5-qtbase"].package_folder, "bin", "qmake"
        )
        args = [
            qmake,
            "qt3d.pro",
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
        self.cpp_info.requires = [
            "qt5-qtbase::qt5-qtbase",
            "qt5-qtdeclarative::qt5-qtdeclarative",
        ]
        self.cpp_info.libs = [
            "Qt53DCore",
            "Qt53DRender",
            "Qt53DInput",
            "Qt53DLogic",
            "Qt53DAnimation",
            "Qt53DExtras",
            "Qt53DQuick",
            "Qt53DQuickRender",
            "Qt53DQuickInput",
            "Qt53DQuickAnimation",
            "Qt53DQuickExtras",
            "Qt53DQuickScene2D",
        ]
        self.cpp_info.set_property("cmake_file_name", "Qt5Qt3D")
        self.cpp_info.set_property("cmake_target_name", "Qt5Qt3D::Qt53DCore")
