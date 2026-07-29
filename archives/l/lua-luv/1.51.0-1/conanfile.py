#!/usr/bin/env python3
"""Conan recipe for luv 1.51.0-1 on OpenHarmony."""

import os

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, export_conandata_patches, get


class LuaLuvConan(ConanFile):
    name = "lua-luv"
    version = "1.51.0-1"
    description = "Lua bindings for libuv"
    license = "Apache-2.0"
    homepage = "https://github.com/luvit/luv"
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("lua/5.4.8")
        self.requires("libuv/1.52.1")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        CMakeDeps(self).generate()
        tc = CMakeToolchain(self)
        # Use already adapted Conan packages instead of luv's bundled submodules.
        tc.variables["WITH_LUA_ENGINE"] = "Lua"
        tc.variables["LUA_BUILD_TYPE"] = "System"
        tc.variables["WITH_SHARED_LIBUV"] = "ON"
        tc.variables["BUILD_MODULE"] = "ON"
        tc.variables["BUILD_STATIC_LIBS"] = "ON"
        tc.variables["BUILD_SHARED_LIBS"] = "OFF"
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.build(target="test")

        # This is luv's upstream C test driver executing its external-loop case.
        test_binary = os.path.join(self.build_folder, "test")
        test_script = os.path.join(self.source_folder, "tests", "manual-test-external-loop.lua")
        self.run(f'"{test_binary}" "{test_script}"', env="conanrun")

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = ["luv"]
        self.cpp_info.requires = ["lua::lua", "libuv::libuv"]
        self.cpp_info.system_libs = ["dl", "rt", "m"]
        self.cpp_info.set_property("cmake_file_name", "lua-luv")
        self.cpp_info.set_property("cmake_target_name", "lua-luv::lua-luv")
