import os
import stat

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, save
from conan.tools.layout import basic_layout


class TypobusterConan(ConanFile):
    name = "typobuster"
    version = "1.0.0"
    description = "Lightweight GTK text editor with transformations and typo correction"
    license = "GPL-3.0-or-later"
    homepage = "https://github.com/nwg-piotr/typobuster"
    url = "https://github.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "application"

    settings = "os", "arch"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self)

    def source(self):
        source = self.conan_data["sources"][0]
        get(self, url=source["url"], sha256=source["sha256"], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        python = "python3" if str(self.settings.os) == "OHOS" else "python"
        self.run(f'{python} -m compileall -q "typobuster"', cwd=self.source_folder)

    def package(self):
        copy(
            self,
            "*",
            src=os.path.join(self.source_folder, "typobuster"),
            dst=os.path.join(self.package_folder, "lib", "typobuster"),
            excludes=["__pycache__", "*.pyc"],
        )
        copy(self, "typobuster.desktop", src=self.source_folder, dst=os.path.join(self.package_folder, "share", "applications"))
        copy(self, "typobuster.svg", src=self.source_folder, dst=os.path.join(self.package_folder, "share", "pixmaps"))
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        save(
            self,
            os.path.join(self.package_folder, "bin", "typobuster"),
            "#!/data/service/hnp/bin/bash\n"
            "set -eu\n"
            "package_dir=$(CDPATH= cd -- \"$(dirname -- \"$0\")/..\" && pwd)\n"
            "export PYTHONPATH=\"$package_dir/lib${PYTHONPATH:+:$PYTHONPATH}\"\n"
            "exec python3 -m typobuster.main \"$@\"\n",
        )
        launcher = os.path.join(self.package_folder, "bin", "typobuster")
        os.chmod(launcher, os.stat(launcher).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.libs = []
