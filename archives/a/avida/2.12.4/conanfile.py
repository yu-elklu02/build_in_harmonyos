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
        toolchain.cache_variables["CMAKE_SYSTEM_NAME"] = "Linux"
        toolchain.cache_variables["CMAKE_SYSTEM_PROCESSOR"] = "aarch64"
        toolchain.cache_variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"
        toolchain.generator = "Unix Makefiles"
        toolchain.cache_variables["CMAKE_C_COMPILER_WORKS"] = "TRUE"
        toolchain.cache_variables["CMAKE_CXX_COMPILER_WORKS"] = "TRUE"
        toolchain.generate()
        env = Environment()
        env.define("MAKEFLAGS", "SHELL=/data/service/hnp/bin/bash -j1")
        env.vars(self, scope="build").save_script("conanfixenv")

    def build(self):
        apply_conandata_patches(self)
        conanbuild_sh = os.path.join(self.generators_folder, "conanbuild.sh")
        if os.path.exists(conanbuild_sh):
            with open(conanbuild_sh, "r", encoding="utf-8") as handle:
                content = handle.read()
            marker = "# Override MAKEFLAGS for OHOS"
            if marker not in content:
                with open(conanbuild_sh, "a", encoding="utf-8") as handle:
                    handle.write("\n" + marker + "\nexport MAKEFLAGS=\"SHELL=/data/service/hnp/bin/bash -j1\"\n")
        cmake = CMake(self)
        cmake.configure()
        cmake.build(cli_args=["--parallel", "1"])
        tests = os.path.join(self.source_folder, "avida-core", "tests")
        runner = os.path.join(tests, "_testrunner", "testrunner.py")
        test_config = os.path.join(tests, "_testrunner", "testrunner.cfg")
        executable = os.path.join(self.build_folder, "bin", "avida")
        with open(test_config, "r", encoding="utf-8") as handle:
            content = handle.read()
        upstream_app = "app = %(builddir)s/work/avida"
        if upstream_app not in content:
            raise ConanInvalidConfiguration("Unexpected Avida test runner application setting")
        with open(test_config, "w", encoding="utf-8") as handle:
            lines = []
            for line in content.splitlines():
                if line.startswith("app = "):
                    lines.append(f"app = {executable}")
                else:
                    lines.append(line)
            handle.write("\n".join(lines) + "\n")
        self.run(f'python -m lib2to3 -w "{tests}"', env="conanbuild")
        configparser_compat = (
            "import configparser\n"
            "_AvidaConfigParser = configparser.ConfigParser\n"
            "class AvidaConfigParser(_AvidaConfigParser):\n"
            "    def get(self, section, option, raw=False, vars=None, fallback=None):\n"
            "        return super().get(section, option, raw=raw, vars=vars, fallback=fallback)\n"
            "configparser.ConfigParser = AvidaConfigParser\n"
        )
        dircache_compat = (
            "import os\n"
            "class dircache:\n"
            "    @staticmethod\n"
            "    def listdir(path):\n"
            "        entries = os.listdir(path)\n"
            "        entries.sort()\n"
            "        return entries\n"
            "    @staticmethod\n"
            "    def annotate(head, entries):\n"
            "        for index, entry in enumerate(entries):\n"
            "            if os.path.isdir(os.path.join(head, entry)):\n"
            "                entries[index] = entry + '/'\n"
        )
        for root, _, files in os.walk(tests):
            for filename in files:
                if not filename.endswith(".py"):
                    continue
                path = os.path.join(root, filename)
                with open(path, "r", encoding="utf-8") as handle:
                    content = handle.read()
                if "import dircache" in content:
                    content = content.replace("import dircache", dircache_compat)
                if path == runner:
                    content = content.replace("import configparser", configparser_compat)
                    content = content.replace("-testrunner-name=", "testrunner-name=")
                    content = content.replace("---testrunner-name", "--testrunner-name")
                    content = content.replace("return 0, 0", "return 0, 0, 0")
                    content = content.replace("return (0, 0)", "return (0, 0, 0)")
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(content)
        report = os.path.join(self.build_folder, "avida-upstream-tests.xml")
        self.run(
            f'python "{runner}" --testrunner-name=./run_tests --xml-report="{report}"',
            cwd=self.source_folder,
            env="conanrun",
        )

    def package(self):
        copy(self, "avida", src=os.path.join(self.build_folder, "bin"), dst=os.path.join(self.package_folder, "bin"))
        copy(self, "*.cfg", src=os.path.join(self.source_folder, "avida-core", "support", "config"), dst=os.path.join(self.package_folder, "res"))
        copy(self, "*.org", src=os.path.join(self.source_folder, "avida-core", "support", "config"), dst=os.path.join(self.package_folder, "res"))
        copy(self, "COPYING", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
