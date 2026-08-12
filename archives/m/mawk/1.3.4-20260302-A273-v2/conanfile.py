import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class MawkConan(ConanFile):
    name = "mawk"
    version = "1.3.4-20260302-a273-v2"
    package_type = "application"
    description = "Interpreter for the AWK programming language"
    license = "GPL-2.0-only"
    homepage = "https://invisible-island.net/mawk/"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("mawk supports Linux and OHOS")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("mawk supports only OHOS armv8")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def build(self):
        host = " --host=aarch64-linux-ohos" if self.settings.os == "OHOS" else ""
        self.run(
            f'sh ./configure{host} --prefix="{self.package_folder}"',
            cwd=self.source_folder,
        )
        self.run("make -j1", cwd=self.source_folder)
        self.run("make check", cwd=self.source_folder)

    def package(self):
        self.run("make install", cwd=self.source_folder)
        copy(self, "COPYING", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = []
