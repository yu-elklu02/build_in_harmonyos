import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get
from conan.tools.env import VirtualBuildEnv
from conan.tools.layout import basic_layout


class Abcm2psConan(ConanFile):
    name = "abcm2ps"
    version = "8.14.15"
    description = "ABC music notation to PostScript and SVG converter"
    license = "GPL-3.0-or-later"
    homepage = "https://github.com/lewdlime/abcm2ps"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "application"

    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        basic_layout(self)

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        VirtualBuildEnv(self).generate()

    def build(self):
        apply_conandata_patches(self)
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration(
                "abcm2ps/c currently supports only OHOS armv8"
            )

        config_shell = os.environ.get("CONFIG_SHELL", "bash")
        prefix = self.package_folder.replace("\\", "/")
        self.run(
            f"{config_shell} ./configure --prefix={prefix}",
            env="conanbuild",
        )
        self.run("make -j1", env="conanbuild")
        self.run("make test", env="conanbuild")
        self.run("make install", env="conanbuild")

    def package_info(self):
        self.buildenv_info.define_path("PATH", os.path.join(self.package_folder, "bin"))
