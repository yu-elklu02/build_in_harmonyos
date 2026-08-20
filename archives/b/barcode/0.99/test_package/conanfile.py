import os

from conan import ConanFile
from conan.tools.build import cross_building


class BarcodeTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if cross_building(self):
            return
        barcode = os.path.join(self.dependencies["barcode"].package_folder, "bin", "barcode")
        # -S selects SVG output; -b gives the data to encode; -e sets the encoding.
        self.run(f'"{barcode}" -S -b 1234567890 -e code128 -o barcode.svg', env="conanrun")
        self.run('grep -q "<svg" barcode.svg && grep -q "1234567890" barcode.svg', env="conanrun")
