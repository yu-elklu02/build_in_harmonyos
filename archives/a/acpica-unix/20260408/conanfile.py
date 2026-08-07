import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class AcpicaUnixConan(ConanFile):
    name = "acpica-unix"
    version = "20260408"
    description = "ACPICA Unix tools, including the iASL compiler"
    license = "Intel ACPI Software License Agreement"
    homepage = "https://github.com/acpica/acpica"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "application"
    settings = "os", "compiler", "build_type", "arch"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("acpica-unix supports Linux and OHOS")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("acpica-unix supports only OHOS armv8")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def build(self):
        cc = os.environ.get("CC", "clang")
        # ACPICA defaults to _CYGWIN when uname is unfamiliar. Explicitly use
        # the Unix host configuration on HarmonyOS and build only iasl.
        # Makefile.config hard-codes -Werror plus gcc-only warning options
        # (-Wlogical-op, -Wmissing-parameter-type, -Wold-style-declaration)
        # that clang rejects as -Wunknown-warning-option; -Werror upgrades
        # those to hard errors. NOWERROR=TRUE toggles the ifneq guard on
        # Makefile.config:226 and drops -Werror, so the unknown options stay
        # warnings and the build completes under clang.
        self.run(f'make iasl CC="{cc}" ACPI_HOST=_LINUX NOWERROR=TRUE', cwd=self.source_folder)

    def test(self):
        self.run("generate/unix/bin/iasl -v", cwd=self.source_folder)

    def package(self):
        copy(
            self,
            "iasl",
            src=os.path.join(self.source_folder, "generate", "unix", "bin"),
            dst=os.path.join(self.package_folder, "bin"),
            keep_path=False,
        )
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
            keep_path=False,
        )

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = []
        self.cpp_info.libs = []
