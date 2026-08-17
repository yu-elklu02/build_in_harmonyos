#!/usr/bin/env python3
"""Conan test_package for pixz."""

import os

from conan import ConanFile


class PixzTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        bash = os.environ.get("CONFIG_SHELL", "/data/service/hnp/bin/bash")
        dep = self.dependencies["pixz"]
        pixz_bin = os.path.join(dep.package_folder, "bin", "pixz")
        work = self.build_folder
        sample = os.path.join(work, "sample.txt")
        compressed = os.path.join(work, "sample.txt.xz")
        output = os.path.join(work, "sample.out")

        with open(sample, "w", encoding="utf-8") as f:
            f.write("pixz harmonyos round trip\\n" * 8)

        self.run(f'{bash} -c \'"{pixz_bin}" -k -t "{sample}" "{compressed}"\'', env="conanrun")
        self.run(f'{bash} -c \'"{pixz_bin}" -d "{compressed}" "{output}"\'', env="conanrun")

        with open(sample, "rb") as f:
            expected = f.read()
        with open(output, "rb") as f:
            actual = f.read()
        if actual != expected:
            raise Exception("pixz round-trip output mismatch")

        self.output.info("pixz round-trip test passed")
