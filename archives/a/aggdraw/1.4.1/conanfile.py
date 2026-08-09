"""Conan recipe for aggdraw 1.4.1, a CPython C++ drawing extension."""
import os
import sys

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class AggdrawConan(ConanFile):
    name = "aggdraw"
    version = "1.4.1"
    package_type = "application"
    description = "High-quality drawing interface for PIL"
    license = "Python (MIT style)"
    homepage = "https://github.com/pytroll/aggdraw"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    topics = ("python", "graphics", "drawing", "cxx-extension")

    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration(
                f"aggdraw is adapted for Linux/OHOS, got {self.settings.os}"
            )
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration(
                f"aggdraw/1.4.1 is validated for OHOS armv8, got {self.settings.arch}"
            )

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        # The target Python on the HarmonyOS PC device builds this CPython C++
        # extension in place.  Disable build isolation and dependency resolution
        # so Conan never downloads undeclared build dependencies.
        staging = os.path.join(self.build_folder, "staging")
        self.run(
            f'"{sys.executable}" -m pip install . --target "{staging}" '
            "--no-build-isolation --no-deps",
            cwd=self.source_folder,
        )

    def package(self):
        staging = os.path.join(self.build_folder, "staging")
        copy(self, "*", src=staging, dst=self.package_folder, keep_path=True)
        copy(
            self,
            "LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)
