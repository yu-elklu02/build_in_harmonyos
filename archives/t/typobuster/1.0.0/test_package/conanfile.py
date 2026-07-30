import os

from conan import ConanFile
from conan.tools.build import can_run


class TypobusterTestConan(ConanFile):
    settings = "os", "arch"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not can_run(self):
            return
        package_folder = self.dependencies["typobuster"].package_folder
        test_script = os.path.join(self.source_folder, "test_typobuster.py")
        python = "python3" if str(self.settings.os) == "OHOS" else "python"
        self.run(f'{python} "{test_script}" "{package_folder}"', env="conanrun")
