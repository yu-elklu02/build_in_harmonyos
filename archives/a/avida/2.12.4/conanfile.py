import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, get


class AvidaConan(ConanFile):
    name = "avida"
    version = "2.12.4"
    package_type = "application"
    license = "GPL-3.0-only"
    homepage = "https://avida.devosoft.org/"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    description = "Digital evolution research platform"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "patches/*"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("avida supports Linux and OHOS only")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("avida OHOS validation requires armv8")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["AVD_CMDLINE"] = True
        toolchain.variables["AVD_GUI_NCURSES"] = False
        toolchain.variables["AVD_UNIT_TESTS"] = False
        toolchain.variables["APTO_UNIT_TESTS"] = False
        toolchain.variables["AVD_USE_TCMALLOC"] = False
        toolchain.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "avida", src=os.path.join(self.build_folder, "bin"), dst=os.path.join(self.package_folder, "bin"))
        copy(self, "*.cfg", src=os.path.join(self.source_folder, "avida-core", "support", "config"), dst=os.path.join(self.package_folder, "res"))
        copy(self, "*.org", src=os.path.join(self.source_folder, "avida-core", "support", "config"), dst=os.path.join(self.package_folder, "res"))
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
