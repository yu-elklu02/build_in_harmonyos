from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class BarcodeConan(ConanFile):
    name = "barcode"
    version = "0.99"
    package_type = "application"
    description = "GNU Barcode command-line generator"
    license = "GPL-3.0-or-later"
    homepage = "https://www.gnu.org/software/barcode/"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    topics = ("barcode", "svg", "ean", "upc")

    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration(
                f"barcode is adapted for Linux/OHOS, got {self.settings.os}"
            )
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration(
                f"barcode/0.99 is validated for OHOS armv8, got {self.settings.arch}"
            )

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        if self.settings.os == "OHOS":
            # The bundled 2013 config scripts predate HarmonyOS. The compiler
            # still targets OHOS; these portable triplets only avoid an OS-name
            # rejection in configure's feature detection.
            tc.configure_args.extend([
                "--build=aarch64-unknown-linux-gnu",
                "--host=aarch64-unknown-linux-gnu",
            ])
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(self, "COPYING", src=self.source_folder, dst=f"{self.package_folder}/licenses")

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.libs = []
        self.cpp_info.bindirs = ["bin"]
