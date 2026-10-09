#!/usr/bin/env python3
"""Conan recipe for Boost.Test unit_test_framework 1.84.0."""

import os

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get


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

    def export_sources(self):
        export_conandata_patches(self)

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
            f"-I{self.source_folder} -DBOOST_ALL_NO_LIB -DBOOST_TEST_NO_LIB "
            f"-DBOOST_SP_NO_PTHREAD_SETCANCELSTATE"
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
        # 1.84 layout: the Test Tools upstream test lives in writing-test-ts/.
        upstream_test = os.path.join(
            self.source_folder, "libs", "test", "test", "writing-test-ts", "test_tools-test.cpp"
        )
        test_bin = os.path.join(self.build_folder, "upstream_test_tools_test")
        self.run(
            f'"{cxx}" {flags} "{upstream_test}" -L"{lib_dir}" '
            f"-lboost_unit_test_framework -o \"{test_bin}\""
        )
        # test_tools-test reads its expected-output pattern via the relative
        # path ./baseline-outputs/test_tools-test.pattern, so it must run with
        # cwd at libs/test/test (where baseline-outputs/ lives).
        self.run(
            f'"{test_bin}"',
            cwd=os.path.join(self.source_folder, "libs", "test", "test"),
        )

        # On AArch64 integer division by zero does not raise SIGFPE.  The
        # upstream run-fail target therefore returns 0 on OHOS/Linux AArch64,
        # although the source guard only covers Apple AArch64 and PPC.
        if str(self.settings.arch) == "armv8":
            exception_test = os.path.join(
                self.source_folder, "libs", "test", "test",
                "prg_exec_monitor-ts", "system-exception-test.cpp",
            )
            # The source defines cpp_main() and b2 normally supplies the
            # corresponding entry point from boost_prg_exec_monitor.
            exception_shim = os.path.join(
                self.source_folder, "libs", "test", "src", "cpp_main.cpp",
            )
            shim_obj = os.path.join(self.build_folder, "cpp_main-gate.o")
            exception_bin = os.path.join(self.build_folder, "system-exception-test")
            self.run(f'"{cxx}" {flags} -c "{exception_shim}" -o "{shim_obj}"')
            self.run(
                f'"{cxx}" {flags} "{exception_test}" "{shim_obj}" -L"{lib_dir}" '
                f'-lboost_unit_test_framework -o "{exception_bin}"'
            )
            self.run(f'"{exception_bin}" --', cwd=os.path.dirname(exception_test), ignore_errors=True)

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
        # Same guard the other boost1.84 split recipes expose: the packaged
        # header tree (boost/thread, boost/smart_ptr) references
        # pthread_setcancelstate, which OHOS musl does not provide.
        # NOTE: do NOT define BOOST_TEST_DYN_LINK (even =0) for consumers —
        # config.hpp gates BOOST_TEST_ALTERNATIVE_INIT_API on `defined()`,
        # so `=0` still flips the unit_test_main signature and breaks the
        # link against this static lib.
        component.defines = ["BOOST_SP_NO_PTHREAD_SETCANCELSTATE"]
