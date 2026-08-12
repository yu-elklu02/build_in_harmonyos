import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    replace_in_file,
)
from conan.tools.layout import basic_layout


class MawkConan(ConanFile):
    name = "mawk"
    version = "1.3.4-20260302-a273-v2"
    package_type = "application"
    description = "Interpreter for the AWK programming language"
    license = "GPL-2.0-only"
    homepage = "https://invisible-island.net/mawk/"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("mawk supports Linux and OHOS")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("mawk supports only OHOS armv8")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def export_sources(self):
        export_conandata_patches(self)

    def build(self):
        triplets = ""
        if self.settings.os == "OHOS":
            tmpdir = os.path.join(self.build_folder, "mawk-tmp")
            os.makedirs(tmpdir, exist_ok=True)
            replace_in_file(
                self,
                os.path.join(self.source_folder, "configure"),
                'tmp=`(umask 077 && mktemp -d -q "$TMPDIR/csXXXXXX") 2>/dev/null` &&',
                'tmp="$TMPDIR/cs-fixed"\nrm -rf "$tmp"\n(umask 077 && mkdir "$tmp") &&',
            )
            triplets = " --build=aarch64-unknown-linux-gnu --host=aarch64-linux-ohos"
            apply_conandata_patches(self)
            env_prefix = f'CC=clang TMPDIR="{tmpdir}" '
        else:
            env_prefix = ""
        self.run(
            f'{env_prefix}sh ./configure{triplets} --prefix="{self.package_folder}"',
            cwd=self.source_folder,
        )
        self.run(f"{env_prefix}make -j1", cwd=self.source_folder)
        self.run(f"{env_prefix}make check", cwd=self.source_folder)

    def package(self):
        self.run("make install", cwd=self.source_folder)
        copy(self, "COPYING", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = []
