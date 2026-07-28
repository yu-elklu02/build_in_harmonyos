import os

from conan import ConanFile
from conan.tools.build import can_run
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.env import Environment


class Qt3dTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)
        # CMakeDeps only emits Qt5CoreConfig.cmake for a direct requirement.
        # Keep this explicit because the test project links Qt5::Core directly.
        self.requires("qt5-qtbase/5.15.2")

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if can_run(self):
            qt3d = self.dependencies["qt3d"]
            qt5 = self.dependencies["qt5-qtbase"]
            qt3d_lib = os.path.join(qt3d.package_folder, "lib")
            qt5_lib = os.path.join(qt5.package_folder, "lib")
            run_env = Environment()
            run_env.prepend_path("LD_LIBRARY_PATH", qt5_lib)
            run_env.prepend_path("LD_LIBRARY_PATH", qt3d_lib)
            test_binary = os.path.join(
                self.cpp.build.bindirs[0], "test_qt3d"
            )
            with run_env.vars(self).apply():
                self.run(test_binary, env="conanrun")
