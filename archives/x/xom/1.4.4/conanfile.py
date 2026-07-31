#!/usr/bin/env python3
"""Conan recipe for XOM 1.4.4."""

import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class XomConan(ConanFile):
    name = "xom"
    version = "1.4.4"
    description = "Tree-based Java API for processing XML"
    license = "LGPL-2.1-or-later"
    homepage = "https://xom.nu/"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "library"
    settings = "os", "arch"

    def validate(self):
        if self.settings.os != "OHOS" or self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("xom/1.4.4 is validated for OHOS/armv8")

    def layout(self):
        basic_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        self.run("ant jar")
        self.run("ant test")

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "xom-*.jar", src=os.path.join(self.source_folder, "build"),
             dst=os.path.join(self.package_folder, "libexec"), keep_path=False)

    def package_info(self):
        jar_path = os.path.join(self.package_folder, "libexec", f"xom-{self.version}.jar")
        self.runenv_info.define_path("XOM_JAR", jar_path)
        self.buildenv_info.define_path("XOM_JAR", jar_path)
