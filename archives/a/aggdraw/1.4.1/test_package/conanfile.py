"""Conan consumer test for the aggdraw CPython extension."""
import os
import sys

from conan import ConanFile
from conan.tools.build import can_run


class AggdrawTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not can_run(self):
            self.output.info("Cross-built consumer cannot run on the build host.")
            return
        package_folder = self.dependencies["aggdraw"].package_folder
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_aggdraw.py")
        self.run(
            f'"{sys.executable}" "{script}"',
            env=[f"PYTHONPATH={package_folder}"],
        )
