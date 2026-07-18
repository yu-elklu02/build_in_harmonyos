#!/usr/bin/env python3
"""Conan test_package — gkrellm 2.3.11 (gkrellmd daemon)."""
from conan import ConanFile
from conan.tools.build import can_run


class GkrellmTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if can_run(self):
            # Verify gkrellmd binary runs and outputs version info.
            # No || true — failure must propagate (R9).
            self.run("gkrellmd --version || gkrellmd -V", env="conanrun")
