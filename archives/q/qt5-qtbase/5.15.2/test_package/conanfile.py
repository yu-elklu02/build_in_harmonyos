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
        package_folder = self.dependencies["qt5-qtbase"].package_folder
        cmake.configure(variables={
            "Qt5Core_DIR": os.path.join(package_folder, "lib", "cmake", "Qt5Core"),
            "Qt5Gui_DIR": os.path.join(package_folder, "lib", "cmake", "Qt5Gui"),
            "Qt5Network_DIR": os.path.join(package_folder, "lib", "cmake", "Qt5Network"),
            "Qt5Test_DIR": os.path.join(package_folder, "lib", "cmake", "Qt5Test"),
        })
        cmake.build()

    def test(self):
        # Run test binary directly with LD_LIBRARY_PATH set to the
        # package's lib dir (OHOS conanrun env doesn't set it)
        dep = self.dependencies["qt5-qtbase"]
        zlib = self.dependencies["zlib"]
        libdir = os.path.join(dep.package_folder, dep.cpp_info.libdirs[0])
        zlib_libdir = os.path.join(zlib.package_folder, zlib.cpp_info.libdirs[0])
        test_bin = os.path.join(self.cpp.build.bindirs[0] if self.cpp.build.bindirs else ".", "test_qt5_qtbase")
        os.environ["LD_LIBRARY_PATH"] = ":".join(
            [libdir, zlib_libdir, os.environ.get("LD_LIBRARY_PATH", "")]
        )
        self.run(test_bin)
