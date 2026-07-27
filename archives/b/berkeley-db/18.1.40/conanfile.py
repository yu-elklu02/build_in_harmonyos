import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import can_run
from conan.tools.files import apply_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class BerkeleyDbConan(ConanFile):
    name = "berkeley-db"
    version = "18.1.40"
    description = "Berkeley DB embedded database"
    license = "AGPL-3.0-only OR LicenseRef-Oracle-Berkeley-DB"
    url = "https://www.oracle.com/database/technologies/related/berkeleydb.html"
    package_type = "library"
    exports_sources = "conandata.yml", "patches/*"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        if self.settings.os != "OHOS" or self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("berkeley-db is packaged for OHOS armv8 only")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--prefix=/")
        if self.settings.os == "OHOS":
            # Berkeley DB's bundled config.guess does not recognize HarmonyOS.
            tc.configure_args.append("--build=aarch64-unknown-linux-gnu")
            tc.configure_args.append("--host=aarch64-unknown-linux-gnu")
        if self.options.shared:
            tc.configure_args.extend(["--disable-static", "--enable-shared"])
        else:
            tc.configure_args.extend(["--enable-static", "--disable-shared"])
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure(build_script_folder="dist")
        autotools.make()
        autotools.make(target="test_mutex")
        if can_run(self):
            self.run(
                os.path.join(self.build_folder, "test_mutex") + " -p 2 -n 10 -l 10",
                env="conanrun",
            )

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = ["db"]
