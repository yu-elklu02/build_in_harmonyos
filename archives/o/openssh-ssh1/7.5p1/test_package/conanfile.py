#!/usr/bin/env python3
import os

from conan import ConanFile


class OpenSshSsh1TestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_folder = self.dependencies["openssh-ssh1"].package_folder
        ssh_keygen = os.path.join(package_folder, "bin", "ssh-keygen")
        key_path = os.path.join(self.build_folder, "openssh_ssh1_test_key")

        self.run(f'"{ssh_keygen}" -q -t ed25519 -N "" -f "{key_path}"',
                 env="conanrun")

        if not os.path.getsize(key_path):
            raise Exception("ssh-keygen did not create a private key")
        if not os.path.getsize(key_path + ".pub"):
            raise Exception("ssh-keygen did not create a public key")

        self.run(f'"{ssh_keygen}" -y -f "{key_path}"', env="conanrun")

