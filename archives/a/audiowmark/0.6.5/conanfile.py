import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout
from conan.tools.files import get
from conan.tools.gnu import PkgConfigDeps


class AudiowmarkConan(ConanFile):
    name = "audiowmark"
    version = "0.6.5"
    package_type = "application"
    description = "Audio watermarking command-line tool"
    license = "GPL-3.0-or-later"
    homepage = "https://github.com/swesterfeld/audiowmark"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    topics = ("audio", "watermark", "signal-processing")

    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("audiowmark supports Linux and OHOS only")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("audiowmark OHOS validation requires armv8")

    def requirements(self):
        self.requires("fftw/3.3.10")
        self.requires("libsndfile/1.2.2")
        self.requires("libgcrypt/1.11.0")
        self.requires("mpg123/1.33.5")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        basic_layout(self)

    def generate(self):
        PkgConfigDeps(self).generate()
        AutotoolsToolchain(self).generate()

    def build(self):
        self.run("autoreconf -fi", cwd=self.source_folder)
        autotools = Autotools(self)
        autotools.configure(args=["--with-ffmpeg=no", "--with-docs=no"])
        autotools.make()
        self.run("make check", cwd=self.build_folder, env="conanbuild")

    def package(self):
        Autotools(self).install()
        self.run("true", cwd=self.build_folder)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
