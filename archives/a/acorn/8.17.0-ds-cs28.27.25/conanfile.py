import os
import shutil
import stat

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout


class AcornConan(ConanFile):
    name = "acorn"
    version = "8.17.0-ds-cs28.27.25"
    description = "ECMAScript parser command-line tool"
    license = "MIT"
    homepage = "https://github.com/acornjs/acorn"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "application"
    settings = "os", "arch"

    def validate(self):
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("acorn supports only OHOS armv8")
        if not shutil.which("node") or not shutil.which("npm"):
            raise ConanInvalidConfiguration("acorn requires Node.js and npm in PATH")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def build(self):
        self.run("npm ci --ignore-scripts --no-audit --no-fund", cwd=self.source_folder)
        self.run("npm run test", cwd=self.source_folder)

    def package(self):
        app_dir = os.path.join(self.package_folder, "res", "acorn")
        copy(self, "*", src=os.path.join(self.source_folder, "acorn", "dist"), dst=os.path.join(app_dir, "dist"), keep_path=True)
        copy(self, "acorn", src=os.path.join(self.source_folder, "acorn", "bin"), dst=os.path.join(app_dir, "bin"), keep_path=False)
        copy(self, "LICENSE", src=os.path.join(self.source_folder, "acorn"), dst=os.path.join(self.package_folder, "licenses"), keep_path=False)
        launcher = os.path.join(self.package_folder, "bin", "acorn")
        save(self, launcher, "#!/bin/sh\nset -eu\nscript_dir=$(CDPATH= cd -- \"$(dirname -- \"$0\")\" && pwd)\nexec node --jitless \"$script_dir/../res/acorn/bin/acorn\" \"$@\"\n")
        os.chmod(launcher, os.stat(launcher).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = []
        self.cpp_info.libs = []
