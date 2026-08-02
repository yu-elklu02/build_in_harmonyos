#!/usr/bin/env python3
import os

from conan import ConanFile


class LeelaZeroTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        exe = os.path.join(self.dependencies["leela-zero"].package_folder, "bin", "leelaz")
        output = os.path.join(self.build_folder, "leelaz-help.txt")
        self.run(f"{exe} --help > {output}", env="conanrun")
        with open(output, "r", encoding="utf-8") as handle:
            text = handle.read()
        if "Generic options" not in text or "--gtp" not in text:
            raise AssertionError("leelaz --help output is incomplete")
