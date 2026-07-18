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
    options = {"qt_major": ["5", "6"], "shared": [True, False]}
    default_options = {"qt_major": "5", "shared": True}

    generators = "CMakeDeps"

    def requirements(self):
        self.requires("zlib/1.3.1")
        if self.options.qt_major == "5":
            self.requires("qt/5.15.18")
        else:
            self.requires("qt/6.5.3")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["QUAZIP_QT_MAJOR_VERSION"] = self.options.qt_major
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
        self.cpp_info.libs = ["quazip1-qt" + str(self.options.qt_major.value)]
        self.cpp_info.includedirs = ["include/QuaZip-Qt" + str(self.options.qt_major.value)]
