from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout

class Qt5QtbaseTestConan(ConanFile):
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
        cmake = CMake(self)
        cmake.test()
        self.run("echo 'qt5-qtbase test package passed'")
