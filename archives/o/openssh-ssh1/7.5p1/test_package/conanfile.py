#!/usr/bin/env python3
from conan import ConanFile


class OpenSshSsh1TestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["openssh-ssh1"].package_folder
        self.run(
            f"sh test_openssh_ssh1.sh '{package_folder}'",
            env="conanrun",
        )

