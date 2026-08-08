import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout


class ConcurrencyKitConan(ConanFile):
    name = "concurrencykit"
    version = "0.7.2"
    description = "Concurrent data structures and synchronization primitives"
    license = "BSD-2-Clause"
    homepage = "https://github.com/concurrencykit/ck"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "library"
    settings = "os", "compiler", "build_type", "arch"

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("concurrencykit supports Linux and OHOS")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("concurrencykit supports only OHOS armv8")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        cc = os.environ.get("CC", "clang")
        self.run(f'./configure CC="{cc}" --prefix=/usr', cwd=self.source_folder)
        self.run("make", cwd=self.source_folder)

    def test(self):
        self.run("test -f lib/libck.a", cwd=self.source_folder)

    def package(self):
        self.run(f'make install prefix="{self.package_folder}"', cwd=self.source_folder)

    def package_info(self):
        self.cpp_info.libs = ["ck"]
