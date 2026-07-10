import os

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
        # Run test binary directly with LD_LIBRARY_PATH set to the
        # package's lib dir (OHOS conanrun env doesn't set it)
        dep = self.dependencies["qt5-qtbase"]
        libdir = os.path.join(dep.package_folder, dep.cpp_info.libdirs[0])
        test_bin = os.path.join(self.cpp.build.bindirs[0], "test_qt5_qtbase")
        os.environ["LD_LIBRARY_PATH"] = libdir + ":" + os.environ.get("LD_LIBRARY_PATH", "")
        self.run(test_bin)
