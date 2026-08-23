import os

from conan import ConanFile


class AvidaTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package = self.dependencies[self.tested_reference_str].package_folder
        executable = os.path.join(package, "bin", "avida")
        self.run(f'python test_avida.py "{executable}"', cwd=self.source_folder, env="conanrun")
