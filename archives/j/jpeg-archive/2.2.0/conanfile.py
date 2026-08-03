from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.gnu import Make
import os


class JpegArchiveConan(ConanFile):
    name = "jpeg-archive"
    version = "2.2.0"
    package_type = "application"
    license = "MIT"
    homepage = "https://github.com/danielgtaylor/jpeg-archive"
    url = "https://github.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    description = "Utilities for archiving and comparing JPEG images"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("jpeg-archive supports Linux/OHOS only")
        if self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("jpeg-archive is adapted for armv8 only")

    def requirements(self):
        self.requires("mozjpeg/4.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        Make(self).build(vars={
            "MOZJPEG_PREFIX": self.dependencies["mozjpeg"].package_folder,
        })

    def package(self):
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        Make(self).install(vars={
            "PREFIX": self.package_folder,
            "MOZJPEG_PREFIX": self.dependencies["mozjpeg"].package_folder,
        })

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = []
        self.cpp_info.includedirs = []
