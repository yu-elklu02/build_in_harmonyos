import os

from conan import ConanFile, ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class BisonConan(ConanFile):
    name = "bison"
    version = "2.7"
    description = "GNU parser generator"
    homepage = "https://www.gnu.org/software/bison/"
    license = "GPL-3.0-or-later"
    package_type = "application"
    settings = "os", "compiler", "build_type", "arch"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)
        build_aux = os.path.join(self.source_folder, "build-aux")
        for name in ("config.sub", "config.guess", "install-sh", "missing"):
            path = os.path.join(build_aux, name)
            if os.path.isfile(path):
                os.chmod(path, 0o755)

        config_sub = os.path.join(build_aux, "config.sub")
        text = open(config_sub, encoding="utf-8").read()
        replacements = (
            (
                "  knetbsd*-gnu* | netbsd*-gnu* | \\\n"
                "  kopensolaris*-gnu* | \\\n",
                "  knetbsd*-gnu* | netbsd*-gnu* | \\\n"
                "  linux-ohos* | \\\n"
                "  kopensolaris*-gnu* | \\\n",
            ),
            (
                "              | -mingw32* | -mingw64* | -linux-gnu* | -linux-android* \\\n"
                "              | -linux-newlib* | -linux-musl* | -linux-uclibc* \\\n",
                "              | -mingw32* | -mingw64* | -linux-gnu* | -linux-android* \\\n"
                "              | -linux-ohos* | \\\n"
                "              | -linux-newlib* | -linux-musl* | -linux-uclibc* \\\n",
            ),
            (
                "\t-linux-dietlibc)\n"
                "\t\tos=-linux-dietlibc\n"
                "\t\t;;\n",
                "\t-linux-dietlibc)\n"
                "\t\tos=-linux-dietlibc\n"
                "\t\t;;\n"
                "\t-linux-ohos*)\n"
                "\t\tos=-linux-ohos\n"
                "\t\t;;\n",
            ),
        )
        for old, new in replacements:
            if old not in text:
                raise ConanInvalidConfiguration(
                    "bison config.sub does not match the expected 2.7 source"
                )
            text = text.replace(old, new, 1)
        with open(config_sub, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)

    def generate(self):
        tc = AutotoolsToolchain(self)
        if self.settings.os == "OHOS":
            tc.configure_args.extend([
                "--build=aarch64-unknown-linux-gnu",
                "--host=aarch64-linux-ohos",
                "--disable-nls",
            ])
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make(args=["-j1"])
        self.run("make check -j1", env="conanbuild")

    def package(self):
        Autotools(self).install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.runenv_info.define_path("PATH", os.path.join(self.package_folder, "bin"))
