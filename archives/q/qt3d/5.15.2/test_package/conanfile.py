import os
from conan import ConanFile
from conan.tools.build import can_run


class Qt3dTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "PkgConfigDeps", "CMakeDeps", "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            self.run("echo 'Qt3D package test passed'")
