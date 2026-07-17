import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout


class Qt3dTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            qt3d = self.dependencies["qt3d"]
            qt3d_lib = os.path.join(qt3d.package_folder, "lib")
            qt_roots = [
                os.environ.get("QTDIR"),
                "/storage/Users/currentUser/usr/local",
                "/storage/Users/currentUser/usr/local/Qt5",
            ]
            qt5_lib = next(
                os.path.join(root, "lib")
                for root in qt_roots
                if root
                and os.path.exists(os.path.join(root, "lib", "libQt5Core.so.5"))
            )
            os.environ["LD_LIBRARY_PATH"] = os.pathsep.join(
                [qt3d_lib, qt5_lib, os.environ.get("LD_LIBRARY_PATH", "")]
            )
            test_binary = os.path.join(
                self.cpp.build.bindirs[0], "test_qt3d"
            )
            self.run(test_binary, env="conanrun")
