import glob
import os

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.env import Environment
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

    def requirements(self):
        self.requires("qt5-qtbase/5.15.2")

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
        qt_root = self.dependencies["qt5-qtbase"].package_folder
        qmake = os.path.join(qt_root, "bin", "qmake")
        if not os.path.isfile(qmake):
            raise ConanInvalidConfiguration(
                "qt5-qtbase/5.15.2 does not contain bin/qmake"
            )
        return qmake, qt_root

    @staticmethod
    def _qt_environment(qt_root):
        env = Environment()
        env.define("QTDIR", qt_root)
        env.prepend_path("PATH", os.path.join(qt_root, "bin"))
        env.prepend_path("LD_LIBRARY_PATH", os.path.join(qt_root, "lib"))
        return env

    def build(self):
        qmake, qt_root = self._qt_installation()

        project = os.path.join(self.source_folder, "qt3d.pro")
        with self._qt_environment(qt_root).vars(self).apply():
            self.run(f'"{qmake}" "{project}" QMAKE_STRIP=""')
            # The OHOS worker does not support GNU make's jobserver FIFO reliably.
            self.run('make -j2 QMAKE_STRIP=""')

    def package(self):
        # The qmake project does not declare install rules for the addon.
        # Package its completed build artifacts directly.
        build_root = os.path.join(self.build_folder, "build-release")
        build_lib = os.path.join(build_root, "lib")
        copy(
            self,
            "libQt53D*.so*",
            src=build_lib,
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        copy(
            self,
            "libQt53D*.prl",
            src=build_lib,
            dst=os.path.join(self.package_folder, "lib"),
            keep_path=False,
        )
        module_map = {
            "core": "Qt3DCore",
            "render": "Qt3DRender",
            "input": "Qt3DInput",
            "logic": "Qt3DLogic",
            "animation": "Qt3DAnimation",
            "extras": "Qt3DExtras",
        }
        for source_module, package_module in module_map.items():
            copy(
                self,
                "*.h",
                src=os.path.join(self.source_folder, "src", source_module),
                dst=os.path.join(self.package_folder, "include", package_module),
                keep_path=False,
            )

        for cmake_dir in glob.glob(os.path.join(build_lib, "cmake", "Qt53D*")):
            copy(
                self,
                "*",
                src=cmake_dir,
                dst=os.path.join(
                    self.package_folder, "lib", "cmake", os.path.basename(cmake_dir)
                ),
            )

        package_lib = os.path.join(self.package_folder, "lib")
        if not glob.glob(os.path.join(package_lib, "libQt53DCore.so*")):
            raise ConanException(
                "Qt3D build completed without producing libQt53DCore.so"
            )
        if not os.path.isfile(
            os.path.join(self.package_folder, "include", "Qt3DCore", "qentity.h")
        ):
            raise ConanException("Qt3D package is missing the public qentity.h header")

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

        self.cpp_info.components["Core"].requires.append(
            "qt5-qtbase::Qt5Core"
        )

        self.cpp_info.set_property("cmake_file_name", "qt3d")
        self.runenv_info.prepend_path(
            "LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib")
        )
