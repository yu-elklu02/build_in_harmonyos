#!/usr/bin/env python3
"""Conan recipe for Boost.Test unit_test_framework 1.84.0."""

import os

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, get


class BoostUnitTestFrameworkConan(ConanFile):
    name = "boost1.84-unit_test_framework"
    version = "1.84.0"
    description = "Boost.Test unit_test_framework 1.84.0 static library"
    license = "BSL-1.0"
    homepage = "https://www.boost.org/doc/libs/1_84_0/libs/test/"
    url = "https://github.com/boostorg/test"
    package_type = "static-library"
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    _sources = (
        "compiler_log_formatter", "debug", "decorator", "execution_monitor",
        "framework", "junit_log_formatter", "plain_report_formatter",
        "progress_monitor", "results_collector", "results_reporter",
        "test_framework_init_observer", "test_tools", "test_tree",
        "unit_test_log", "unit_test_main", "unit_test_monitor",
        "unit_test_parameters", "xml_log_formatter", "xml_report_formatter",
    )

    def layout(self):
        pass

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def _compiler(self):
        configured = self.conf.get(
            "tools.build:compiler_executables", default={}, check_type=dict
        ) or {}
        return configured.get("cpp", "clang++"), configured.get("ar", "llvm-ar")

    def build(self):
        apply_conandata_patches(self)
        cxx, ar = self._compiler()
        opt = "-O0 -g" if str(self.settings.build_type) == "Debug" else "-O2 -DNDEBUG"
        flags = (
            f"-std=c++17 -stdlib=libc++ {opt} -fPIC "
            f"-I{self.source_folder} -DBOOST_ALL_NO_LIB -DBOOST_TEST_NO_LIB"
        )
        obj_dir = os.path.join(self.build_folder, "obj")
        os.makedirs(obj_dir, exist_ok=True)
        objects = []
        for name in self._sources:
            src = os.path.join(self.source_folder, "libs", "test", "src", name + ".cpp")
            obj = os.path.join(obj_dir, name + ".o")
            self.run(f'"{cxx}" {flags} -c "{src}" -o "{obj}"')
            objects.append(obj)
        lib_dir = os.path.join(self.build_folder, "lib")
        os.makedirs(lib_dir, exist_ok=True)
        lib_path = os.path.join(lib_dir, "libboost_unit_test_framework.a")
        self.run(f'"{ar}" rcs "{lib_path}" ' + " ".join(f'"{obj}"' for obj in objects))

        # Run one official Boost.Test source during the package build. This keeps
        # the upstream test boundary real even though b2 itself is unavailable.
        upstream_test = os.path.join(
            self.source_folder, "libs", "test", "test", "test_tools_test.cpp"
        )
        test_bin = os.path.join(self.build_folder, "upstream_test_tools_test")
        self.run(
            f'"{cxx}" {flags} "{upstream_test}" -L"{lib_dir}" '
            f"-lboost_unit_test_framework -o \"{test_bin}\""
        )
        self.run(f'"{test_bin}"')

    def package(self):
        copy(self, "boost/*", src=self.source_folder,
             dst=os.path.join(self.package_folder, "include"))
        copy(self, "LICENSE_1_0.txt", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        copy(self, "libboost_unit_test_framework.a",
             src=os.path.join(self.build_folder, "lib"),
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Boost")
        self.cpp_info.set_property("pkg_config_name", "boost")
        component = self.cpp_info.components["unit_test_framework"]
        component.includedirs = ["include"]
        component.libdirs = ["lib"]
        component.libs = ["boost_unit_test_framework"]
        component.set_property("cmake_target_name", "Boost::unit_test_framework")
        component.set_property("pkg_config_name", "libboost_unit_test_framework")
        component.defines = ["BOOST_TEST_DYN_LINK=0"]
