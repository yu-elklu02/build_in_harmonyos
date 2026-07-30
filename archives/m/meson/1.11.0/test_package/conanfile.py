from conan import ConanFile
from conan.tools.build import cross_building


class MesonTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualBuildEnv"

    def build_requirements(self):
        self.tool_requires(self.tested_reference_str)

    def build(self):
        self.run("meson setup build", env="conanbuild")
        self.run("meson compile -C build", env="conanbuild")

    def test(self):
        if cross_building(self):
            self.output.info("Cross-building: package execution is skipped.")
            return
        self.run("./build/conan-probe")
