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
        # conan self.run's `env` only accepts predefined scope names, not a
        # ["PYTHONPATH=..."] list, so inline PYTHONPATH via the `env` command
        # as a prefix so aggdraw's native .so inside the conan cache package
        # folder is importable by the target Python.
        self.run(
            f'env PYTHONPATH="{package_folder}" "{sys.executable}" "{script}"',
        )
