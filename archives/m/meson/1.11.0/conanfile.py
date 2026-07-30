import os
import stat

from conan import ConanFile
from conan.tools.env import Environment
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    save,
)
from conan.tools.layout import basic_layout


class MesonConan(ConanFile):
    name = "meson"
    version = "1.11.0"
    package_type = "application"
    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def build_requirements(self):
        # These libraries are used only by Meson's complete upstream suite.
        # They are not dependencies of the packaged Meson application.
        self.tool_requires("zlib/1.3.1.1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder=".")

    def build(self):
        test_deps = os.path.join(self.build_folder, "upstream-test-deps")
        pkgconfig_dir = os.path.join(test_deps, "pkgconfig")
        cmake_dir = os.path.join(test_deps, "lib", "cmake", "ZLIB")
        os.makedirs(pkgconfig_dir, exist_ok=True)
        os.makedirs(cmake_dir, exist_ok=True)

        zlib = self.dependencies.build["zlib"]
        zlib_prefix = zlib.package_folder.replace("\\", "/")
        save(
            self,
            os.path.join(pkgconfig_dir, "zlib.pc"),
            "prefix={0}\n"
            "libdir=${{prefix}}/lib\n"
            "includedir=${{prefix}}/include\n\n"
            "Name: zlib\n"
            "Description: zlib supplied for Meson upstream tests\n"
            "Version: 1.3.1\n"
            "Libs: -L${{libdir}} -lz\n"
            "Cflags: -I${{includedir}}\n".format(zlib_prefix),
        )
        save(
            self,
            os.path.join(cmake_dir, "ZLIBConfig.cmake"),
            "add_library(ZLIB::ZLIB STATIC IMPORTED)\n"
            "set_target_properties(ZLIB::ZLIB PROPERTIES\n"
            "  IMPORTED_LOCATION \"{0}/lib/libz.a\"\n"
            "  INTERFACE_INCLUDE_DIRECTORIES \"{0}/include\")\n"
            "set(ZLIB_FOUND TRUE)\n"
            "set(ZLIB_VERSION_STRING \"1.3.1\")\n"
            "set(ZLIB_LIBRARIES ZLIB::ZLIB)\n"
            "set(ZLIB_INCLUDE_DIRS \"{0}/include\")\n".format(zlib_prefix),
        )
        test_env = Environment()
        test_env.prepend_path("PKG_CONFIG_PATH", pkgconfig_dir)
        test_env.prepend_path("CMAKE_PREFIX_PATH", test_deps)
        test_env.define_path("ZLIB_ROOT", zlib_prefix)
        with test_env.vars(self).apply():
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
