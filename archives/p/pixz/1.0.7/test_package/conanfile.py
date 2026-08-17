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

        # pixz is dynamically linked against libarchive/xz/zlib. VirtualRunEnv
        # does not always expose transitive libdirs on OHOS, so collect them
        # explicitly and put them on LD_LIBRARY_PATH for the test run.
        # pixz links libarchive/liblzma/z statically on OHOS, so no runtime
        # LD_LIBRARY_PATH is needed. Run plain via env(1) to avoid conanrun
        # overriding PATH.
        self.run(
            f'env LD_LIBRARY_PATH= "{pixz_bin}" -k -t "{sample}" "{compressed}"',
        )
        self.run(
            f'env LD_LIBRARY_PATH= "{pixz_bin}" -d "{compressed}" "{output}"',
        )

        with open(sample, "rb") as f:
            expected = f.read()
        with open(output, "rb") as f:
            actual = f.read()
        if actual != expected:
            raise Exception("pixz round-trip output mismatch")

        self.output.info("pixz round-trip test passed")
