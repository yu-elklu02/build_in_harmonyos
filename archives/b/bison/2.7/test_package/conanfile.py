import os

from conan import ConanFile


class BisonTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        bison = os.path.join(self.dependencies["bison"].package_folder, "bin", "bison")
        script = os.path.join(self.source_folder, "test.sh")
        self.run(f"sh {script} {bison}", env="conanrun")
