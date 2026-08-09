import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get


class AdlplugConan(ConanFile):
    name = "adlplug"
    version = "1.0.2"
    description = "FM synthesizer core from the ADLplug audio plugin"
    license = "BSL-1.0"
    homepage = "https://github.com/jpcima/ADLplug"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "static-library"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    def validate(self):
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration(
                "adlplug/1.0.2 currently supports only OHOS armv8"
            )

    def layout(self):
        cmake_layout(self)

    def source(self):
        source = self.conan_data["sources"]
        get(self, url=source["url"], sha256=source["sha256"], strip_root=True)
        for info in self.conan_data["submodules"].values():
            get(
                self,
                url=info["url"],
                sha256=info["sha256"],
                destination=os.path.join(self.source_folder, info["destination"]),
                strip_root=True,
            )

    def generate(self):
        toolchain = CMakeToolchain(self)
        toolchain.variables["ADLplug_VST2"] = False
        toolchain.variables["ADLplug_VST3"] = False
        toolchain.variables["ADLplug_LV2"] = False
        toolchain.variables["ADLplug_AU"] = False
        toolchain.variables["ADLplug_Standalone"] = False
        toolchain.variables["ADLplug_Jack"] = False
        toolchain.variables["ADLplug_PCH"] = False
        toolchain.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build(target="ADLplug_core")

    def test(self):
        if not cross_building(self):
            cmake = CMake(self)
            cmake.build(target="ADLplug_core")

    def package(self):
        libdir = os.path.join(self.package_folder, "lib")
        copy(self, "*.a", src=self.build_folder, dst=libdir, keep_path=False)
        copy(
            self,
            "*.h",
            src=os.path.join(self.source_folder, "sources"),
            dst=os.path.join(self.package_folder, "include", "adlplug"),
            keep_path=True,
        )
        copy(
            self,
            "*.h",
            src=os.path.join(self.source_folder, "thirdparty", "libADLMIDI", "include"),
            dst=os.path.join(self.package_folder, "include"),
            keep_path=True,
        )
        copy(
            self,
            "*.h",
            src=os.path.join(self.source_folder, "thirdparty", "wopl"),
            dst=os.path.join(self.package_folder, "include"),
            keep_path=True,
        )

    def package_info(self):
        self.cpp_info.libs = ["ADLplug_core", "ADLMIDI"]
        self.cpp_info.includedirs = ["include", os.path.join("include", "adlplug")]
        self.cpp_info.set_property("cmake_file_name", "adlplug")
        self.cpp_info.set_property("cmake_target_name", "adlplug::adlplug")
