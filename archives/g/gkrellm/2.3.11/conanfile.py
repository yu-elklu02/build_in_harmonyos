#!/usr/bin/env python3
"""Conan recipe — gkrellm/gkrellmd 2.3.11 (Makefile, C system monitor daemon).

Only the gkrellmd daemon is built — the GTK2/X11 GUI client is excluded
because OHOS has no GTK/X11 stack.  gkrellmd is a headless server that
collects system metrics and serves them over a TCP socket; it has zero
GUI dependencies and compiles cleanly with clang on OHOS.

Build system: plain Makefile in the server/ subdirectory.
"""
import os
from conan import ConanFile
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches
from conan.tools.env import VirtualBuildEnv, Environment


class GkrellmConan(ConanFile):
    name = "gkrellm"
    version = "2.3.11"
    description = (
        "GKrellM system monitor — gkrellmd daemon only. "
        "Collects CPU, memory, disk, network metrics and serves them "
        "over a TCP socket to gkrellm clients."
    )
    license = "GPL-2.0-or-later"
    homepage = "https://github.com/toppk/gkrellm"
    url = ""  # CI fills this

    package_type = "application"

    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        # R33: obtain compiler paths from Conan conf, not bare shell variables
        vbe = VirtualBuildEnv(self)
        vbe.generate()
        cc = self.conf.get("tools.build:compiler_executables", {}).get("c", "clang")
        cxx = self.conf.get("tools.build:compiler_executables", {}).get("cpp", "clang++")
        env = Environment()
        env.define("CC", cc)
        env.define("CXX", cxx)
        env.vars(self).save_script("conanbuild")

    def build(self):
        apply_conandata_patches(self)
        server_dir = os.path.join(self.source_folder, "server")
        cc = self.conf.get("tools.build:compiler_executables", {}).get("c", "clang")
        # OHOS does not provide lm-sensors.  Skipping its configure probe also
        # avoids attempting to link a cross-compiled probe executable.
        glib_includes = (
            "-I$HOME/usr/local/include/glib-2.0 "
            "-I$HOME/usr/local/lib/glib-2.0/include"
        )
        glib_libs = "-lglib-2.0 -lgmodule-2.0 -lgthread-2.0 -lintl"
        self.run(
            f"make -C \"{server_dir}\" -j1 V=1 "
            f"CC=\"{cc}\" PKG_CONFIG=true "
            f"PKG_INCLUDE='{glib_includes}' PKG_LIB='{glib_libs}' "
            "without-libsensors=yes",
            env="conanbuild",
        )

    def package(self):
        server_dir = os.path.join(self.source_folder, "server")
        install_root = self.package_folder
        self.run(
            f"make -C \"{server_dir}\" install "
            f"PREFIX=\"{install_root}\" without-libsensors=yes",
            env="conanbuild",
        )

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = []
