import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
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
            # Bison 2.7's grammar-analysis code predates modern Clang and
            # relies on aliasing-sensitive C idioms. Keep the OHOS binary
            # conservative while preserving the upstream test suite.
            tc.extra_cflags.extend(["-O0", "-fno-strict-aliasing"])
            tc.extra_cxxflags.extend(["-O0", "-fno-strict-aliasing"])
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
        # Pass BISON explicitly so the test suite uses the just-built 2.7
        # binary instead of falling back to any system bison on PATH.
        # On OHOS the system already has bison 3.8.2 at
        # /data/service/hnp/bin/bison; without this override make check
        # picks that up and every diagnostic-format test fails.
        bison_bin = os.path.join(self.build_folder, "src", "bison")
        self.run(
            "make check -j1 BISON={}".format(bison_bin),
            env="conanbuild",
        )

    def package(self):
        Autotools(self).install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.runenv_info.define_path("PATH", os.path.join(self.package_folder, "bin"))
