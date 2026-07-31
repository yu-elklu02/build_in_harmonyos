"""Conan test_package for ispell 3.4.06.
R34: Must actually exercise the tested binary.
"""
import os

from conan import ConanFile
from conan.tools.build import can_run


class IspellTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not can_run(self):
            self.output.info("Cross-building: skipping execution test.")
            return

        dep = self.dependencies["ispell"]
        bin_dir = os.path.join(dep.package_folder, "bin")
        test_dir = os.path.dirname(os.path.abspath(__file__))

        self.run(
            f'zsh "{test_dir}/test_ispell.sh" "{bin_dir}"',
            env="conanrun",
        )
