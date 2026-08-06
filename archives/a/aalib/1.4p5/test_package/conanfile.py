from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout


class AAlibTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        CMake(self).configure()
        CMake(self).build()

    def test(self):
        CMake(self).test()
