import os

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import Environment


class Qt3dTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps"

    def requirements(self):
        self.requires(self.tested_reference_str)
        # CMakeDeps only emits Qt5CoreConfig.cmake for a direct requirement.
        # Keep this explicit because the test project links Qt5::Core directly.
        self.requires("qt5-qtbase/5.15.2")

    def layout(self):
        cmake_layout(self)

    def generate(self):
        toolchain = CMakeToolchain(self)
        qt5 = self.dependencies["qt5-qtbase"]
        moc = os.path.join(
            qt5.package_folder, "bin", "moc"
        )
        if not os.path.isfile(moc):
            raise ConanException("qt5-qtbase does not provide bin/moc")
        toolchain.variables["CMAKE_AUTOMOC_EXECUTABLE"] = moc
        toolchain.generate()

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
            with run_env.vars(self).apply():
                for test_name in ("test_qt3d", "test_upstream_qaspectjob"):
                    self.run(
                        os.path.join(self.cpp.build.bindirs[0], test_name),
                        env="conanrun",
                    )
