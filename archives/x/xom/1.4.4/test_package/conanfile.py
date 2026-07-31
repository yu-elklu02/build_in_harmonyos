#!/usr/bin/env python3
"""Consumer test for xom 1.4.4."""

import os

from conan import ConanFile


class XomTestConan(ConanFile):
    settings = "os", "arch"
    test_type = "explicit"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        xom_jar = os.environ.get("XOM_JAR")
        if not xom_jar or not os.path.isfile(xom_jar):
            raise RuntimeError("XOM_JAR is not set to a packaged JAR")
        source = os.path.join(self.source_folder, "test_xom.java")
        self.run(f'javac -cp "{xom_jar}" -d "{self.build_folder}" "{source}"')
        self.run(f'java -cp "{xom_jar}{os.pathsep}{self.build_folder}" test_xom',
                 env="conanrun")
