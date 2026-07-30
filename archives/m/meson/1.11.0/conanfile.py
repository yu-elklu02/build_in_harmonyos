import os
import stat

from conan import ConanFile
from conan.tools.files import copy, get, save
from conan.tools.layout import basic_layout


class MesonConan(ConanFile):
    name = "meson"
    version = "1.11.0"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def layout(self):
        basic_layout(self, src_folder=".")

    def build(self):
        self.run("python3 run_tests.py", cwd=self.source_folder)

    def package(self):
        site_packages = os.path.join(
            self.package_folder, "lib", "python3.12", "site-packages"
        )
        copy(self, "meson.py", src=self.source_folder, dst=site_packages)
        copy(
            self,
            "*",
            src=os.path.join(self.source_folder, "mesonbuild"),
            dst=os.path.join(site_packages, "mesonbuild"),
        )

        launcher = os.path.join(self.package_folder, "bin", "meson")
        save(
            self,
            launcher,
            "#!/bin/sh\n"
            'here=$(CDPATH= cd "$(dirname "$0")" && pwd)\n'
            'exec python3 "$here/../lib/python3.12/site-packages/meson.py" "$@"\n',
        )
        os.chmod(launcher, os.stat(launcher).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = []
        self.cpp_info.includedirs = []
        self.buildenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))
