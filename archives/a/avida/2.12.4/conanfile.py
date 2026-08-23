import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.env import Environment
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
        # E092: CMake does not recognize HarmonyOS; force Linux platform
        toolchain.cache_variables["CMAKE_SYSTEM_NAME"] = "Linux"
        toolchain.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
        toolchain.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        toolchain.generator = "Unix Makefiles"
        # E093: CMake's try-compile launches make which uses /bin/sh,
        # but OHOS has no /bin/sh. Skip compiler tests to avoid this.
        toolchain.cache_variables["CMAKE_C_COMPILER_WORKS"] = "TRUE"
        toolchain.cache_variables["CMAKE_CXX_COMPILER_WORKS"] = "TRUE"
        toolchain.generate()

        # Fix: make uses /bin/sh by default, but OHOS has no /bin/sh.
        # MAKEFLAGS=SHELL=xxx overrides make's internal SHELL variable.
        bash = "/data/service/hnp/bin/bash"
        env = Environment()
        env.define("MAKEFLAGS", f"SHELL={bash} -j1")
        env.vars(self, scope="build").save_script("conanfixenv")

    def build(self):
        apply_conandata_patches(self)

        # Fix: conanbuild.sh sources profile [buildenv] AFTER our custom env
        # script. Append MAKEFLAGS override at the end to ensure it takes effect.
        conanbuild_sh = os.path.join(self.generators_folder, "conanbuild.sh")
        if os.path.exists(conanbuild_sh):
            with open(conanbuild_sh, "r") as f:
                content = f.read()
            bash = "/data/service/hnp/bin/bash"
            fix = (
                '\n# Override MAKEFLAGS for OHOS (no /bin/sh)\n'
                f'export MAKEFLAGS="SHELL={bash} -j1"\n'
            )
            if "# Override MAKEFLAGS for OHOS" not in content:
                with open(conanbuild_sh, "w") as f:
                    f.write(content + fix)

        cmake = CMake(self)
        cmake.configure()
        cmake.build(cli_args=["--parallel", "1"])

    def package(self):
        copy(self, "avida", src=os.path.join(self.build_folder, "bin"), dst=os.path.join(self.package_folder, "bin"))
        copy(self, "*.cfg", src=os.path.join(self.source_folder, "avida-core", "support", "config"), dst=os.path.join(self.package_folder, "res"))
        copy(self, "*.org", src=os.path.join(self.source_folder, "avida-core", "support", "config"), dst=os.path.join(self.package_folder, "res"))
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
