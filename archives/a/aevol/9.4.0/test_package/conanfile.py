import os

from conan import ConanFile
from conan.tools.build import can_run


class AevolTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not can_run(self):
            self.output.info("Cross-built consumer cannot run on the build host.")
            return
        package = self.dependencies["aevol"].package_folder
        for name in ("aevol_create_2b", "aevol_run_2b"):
            self.run(f'"{os.path.join(package, "bin", name)}" --help', env="conanrun")
