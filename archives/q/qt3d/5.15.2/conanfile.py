import glob
import os
import shlex

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
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
            self._run_upstream_core_test(qmake)

    def _run_upstream_core_test(self, qmake):
        """Build and run a public-API-only Qt3D upstream test suite."""
        test_dir = os.path.join(
            self.source_folder, "tests", "auto", "core", "qaspectjob"
        )
        quoted_test_dir = shlex.quote(test_dir)
        quoted_qmake = shlex.quote(qmake)
        _, qt_root = self._qt_installation()
        test_env = Environment()
        # qmake creates Qt3D's module .pri files in the Conan build folder.
        # Preserve the installed Qt5 module root as well, so QMAKEPATH does
        # not hide Qt5Core and Qt5Test from the qmake executable.
        test_env.define(
            "QMAKEPATH",
            os.pathsep.join((self.build_folder, qt_root)),
        )
        test_env.prepend_path(
            "LD_LIBRARY_PATH", os.path.join(self.build_folder, "lib")
        )
        test_env.prepend_path("LD_LIBRARY_PATH", os.path.join(qt_root, "lib"))

        with test_env.vars(self).apply():
            self.run(
                f"cd {quoted_test_dir} && {quoted_qmake} qaspectjob.pro QMAKE_STRIP=''"
            )
            self.run(f"cd {quoted_test_dir} && make -j2 QMAKE_STRIP=''")
            self.run(
                f"cd {quoted_test_dir} && QT_QPA_PLATFORM=offscreen ./tst_qaspectjob"
            )

    def package(self):
        _, qt_root = self._qt_installation()
        stage = os.path.join(self.build_folder, "package-stage")
        with self._qt_environment(qt_root).vars(self).apply():
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

        self.cpp_info.components["Core"].requires.append(
            "qt5-qtbase::Qt5Core"
        )

        self.cpp_info.set_property("cmake_file_name", "qt3d")
        self.runenv_info.prepend_path(
            "LD_LIBRARY_PATH", os.path.join(self.package_folder, "lib")
        )
