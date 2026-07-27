import os

from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import can_run
from conan.tools.layout import basic_layout


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        basic_layout(self)

    def test(self):
        if not can_run(self):
            return

        test_dir = os.path.join(self.build_folder, "functional_test")
        os.makedirs(test_dir, exist_ok=True)
        with open(os.path.join(test_dir, "input.txt"), "w", encoding="utf-8") as fixture:
            fixture.write("OpenHarmony Parchive functional test\\n")

        par = os.path.join(self.dependencies["parchive"].cpp_info.bindirs[0], "par")
        self.run('"{}" add -n1 archive.par input.txt'.format(par), cwd=test_dir, env="conanrun")
        self.run('"{}" check archive.par'.format(par), cwd=test_dir, env="conanrun")

        if not os.path.isfile(os.path.join(test_dir, "archive.P01")):
            raise ConanException("Parchive did not create the expected recovery volume")
