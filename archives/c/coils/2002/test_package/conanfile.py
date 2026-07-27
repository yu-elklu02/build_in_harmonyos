import os

from conan import ConanFile
from conan.tools.build import can_run


class CoilsTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not can_run(self):
            return

        package = self.dependencies["coils"].package_folder
        ncoils = os.path.join(package, "bin", "ncoils")
        sample = os.path.join(self.source_folder, "1srya.fa")
        output = os.path.join(self.build_folder, "1srya-coils.fasta")
        self.run(f'"{ncoils}" -f < "{sample}" > "{output}"', env="conanrun")
        self.run(f'grep -q "^>1srya " "{output}"', env="conanrun")
