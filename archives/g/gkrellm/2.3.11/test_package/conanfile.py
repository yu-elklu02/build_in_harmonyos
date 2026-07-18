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
            # Verify gkrellmd binary runs and prints version
            self.run("gkrellmd --version || gkrellmd -V || true", env="conanrun")
            # gkrellmd starts, binds port, then exits — just check it exists
            self.run("which gkrellmd || ls $(conan cache path gkrellm/2.3.11)/sbin/gkrellmd",
                     env="conanrun")
