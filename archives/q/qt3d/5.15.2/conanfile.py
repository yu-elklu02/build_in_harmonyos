import glob
import os
import shutil
import subprocess

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class Qt3dConan(ConanFile):
    name = "qt3d"
    version = "5.15.2"
    description = "Qt 3D module for Qt 5"
    homepage = "https://www.qt.io"
    license = "LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only"
    package_type = "shared-library"

    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        basic_layout(self)

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration(
                "qt3d supports only Linux and OHOS builds"
            )

    def source(self):
        get(self, **self.conan_data["sources"][str(self.version)], strip_root=True)

    def _qt_installation(self):
        qmake_candidates = [
            os.environ.get("QMAKE"),
            shutil.which("qmake-qt5"),
            shutil.which("qmake5"),
            shutil.which("qmake"),
            "/storage/Users/currentUser/usr/local/bin/qmake-qt5",
            "/storage/Users/currentUser/usr/local/bin/qmake5",
            "/storage/Users/currentUser/usr/local/bin/qmake",
            "/storage/Users/currentUser/usr/local/Qt5/bin/qmake",
            os.path.expanduser("~/usr/local/bin/qmake"),
            os.path.expanduser("~/usr/local/Qt5/bin/qmake"),
        ]
        for qmake in qmake_candidates:
            if not qmake or not os.path.isfile(qmake):
                continue
            try:
                version = subprocess.run(
                    [qmake, "-query", "QT_VERSION"],
                    check=True,
                    capture_output=True,
                    text=True,
                ).stdout.strip()
                if not version.startswith("5."):
                    continue
                result = subprocess.run(
                    [qmake, "-query", "QT_INSTALL_PREFIX"],
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except (OSError, subprocess.CalledProcessError):
                continue
            qt_root = result.stdout.strip() or os.path.dirname(os.path.dirname(qmake))
            return qmake, qt_root
        raise ConanInvalidConfiguration(
            "Qt 5.15.2 qmake was not found in PATH; set QMAKE to its executable"
        )

    def build(self):
        qmake, qt_root = self._qt_installation()
        qt_bin = os.path.join(qt_root, "bin")
        qt_lib = os.path.join(qt_root, "lib")

        os.environ["QTDIR"] = qt_root
        os.environ["PATH"] = qt_bin + os.pathsep + os.environ.get("PATH", "")
        os.environ["LD_LIBRARY_PATH"] = (
            qt_lib + os.pathsep + os.environ.get("LD_LIBRARY_PATH", "")
        )

        project = os.path.join(self.source_folder, "qt3d.pro")
        self.run(f'"{qmake}" "{project}" QMAKE_STRIP=""')
        # The OHOS worker does not support GNU make's jobserver FIFO reliably.
        self.run('make -j2 QMAKE_STRIP=""')

    def package(self):
        _, qt_root = self._qt_installation()
        stage = os.path.join(self.build_folder, "package-stage")
        self.run(f'make install INSTALL_ROOT="{stage}" QMAKE_STRIP=""')

        staged_prefix = os.path.join(stage, qt_root.lstrip("/\\"))
        staged_lib = os.path.join(staged_prefix, "lib")

        copy(
            self,
            "libQt53D*.so*",
            src=staged_lib,
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            "libQt53D*.prl",
            src=staged_lib,
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            "*",
            src=os.path.join(staged_prefix, "include"),
            dst=os.path.join(self.package_folder, "include"),
        )

        modules_dir = os.path.join(staged_prefix, "mkspecs", "modules")
        copy(
            self,
            "qt_lib_3d*.pri",
            src=modules_dir,
            dst=os.path.join(self.package_folder, "mkspecs", "modules"),
            keep_path=False,
        )

        for cmake_dir in glob.glob(os.path.join(staged_lib, "cmake", "Qt53D*")):
            copy(
                self,
                "*",
                src=cmake_dir,
                dst=os.path.join(
                    self.package_folder, "lib", "cmake", os.path.basename(cmake_dir)
                ),
            )

        for directory in ("plugins", "qml"):
            copy(
                self,
                "*",
                src=os.path.join(staged_prefix, directory),
                dst=os.path.join(self.package_folder, directory),
            )

    def package_info(self):
        component_data = {
            "Core": ("Qt53DCore", []),
            "Render": ("Qt53DRender", ["Core"]),
            "Input": ("Qt53DInput", ["Core"]),
            "Logic": ("Qt53DLogic", ["Core"]),
            "Animation": ("Qt53DAnimation", ["Core", "Render"]),
            "Extras": ("Qt53DExtras", ["Core", "Render", "Input", "Logic"]),
        }
        for name, (library, dependencies) in component_data.items():
            component = self.cpp_info.components[name]
            component.libs = [library]
            component.includedirs = ["include"]
            component.requires = dependencies
            component.set_property("cmake_target_name", f"qt3d::{name}")

        self.cpp_info.set_property("cmake_file_name", "qt3d")
        self.runenv_info.prepend_path(
            "LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib")
        )
