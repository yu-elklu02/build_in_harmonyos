import os

from conan import ConanFile
from conan.tools.files import get
from conan.tools.layout import basic_layout


class Qt3dConan(ConanFile):
    name = "qt3d"
    version = "5.15.2"

    description = "Qt 3D module for Qt5"
    homepage = "https://www.qt.io"
    license = "LGPL-3.0"

    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        pass

    def layout(self):
        basic_layout(self)

    def source(self):
        get(
            self,
            **self.conan_data["sources"]["5.15.2"],
            strip_root=True
        )

    def build(self):
        self.run(
            "qmake "
            + os.path.join(self.source_folder, "qt3d.pro")
            + " CONFIG-=quick3d"
        )
        self.run("make -j$(nproc)")

    def package(self):
        self.run("make install INSTALL_ROOT={}".format(self.package_folder))

    def package_info(self):
        self.cpp_info.libs = [
            "Qt53DCore",
            "Qt53DRender",
            "Qt53DInput",
            "Qt53DLogic",
            "Qt53DAnimation",
            "Qt53DExtras",
        ]
