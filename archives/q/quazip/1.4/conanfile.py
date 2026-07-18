import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import get


class QuazipConan(ConanFile):
    name = "quazip"
    version = "1.4"
    description = "Qt/C++ wrapper over minizip for accessing ZIP archives"
    homepage = "https://github.com/stachenov/quazip"
    license = "LGPL-2.1-or-later"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    generators = "CMakeDeps"

    def requirements(self):
        self.requires("zlib/1.3.1")
        self.requires("qt5-qtbase/5.15.2")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["QUAZIP_QT_MAJOR_VERSION"] = "5"
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["QUAZIP_ENABLE_TESTS"] = True
        tc.variables["QUAZIP_BZIP2"] = False
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.test(cli_args=["--output-on-failure"])

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["quazip1-qt5"]
        self.cpp_info.includedirs = ["include/QuaZip-Qt5"]
