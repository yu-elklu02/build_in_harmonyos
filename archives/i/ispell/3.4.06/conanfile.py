"""Conan recipe for ispell 3.4.06.

ispell is an interactive spell-checking program for Unix.
Build system: traditional Makefile (no configure script).
Configuration is done via local.h (copied from local.h.samp + make overrides).

Upstream: https://www.cs.hmc.edu/~geoff/ispell.html
License: BSD-4-Clause
"""
import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout


class IspellConan(ConanFile):
    name = "ispell"
    version = "3.4.06"
    package_type = "application"
    description = "Interactive spell-checking program for Unix"
    license = "BSD-4-Clause"
    homepage = "https://www.cs.hmc.edu/~geoff/ispell.html"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    topics = ("spell", "spellcheck", "text", "cli")

    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        # R32: must use in(), not ==
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration(
                f"ispell only supports Linux/OHOS, got {self.settings.os}"
            )
        if self.settings.arch != "armv8":
            raise ConanInvalidConfiguration(
                f"ispell/3.4.06 is adapted and validated for armv8 only, "
                f"got {self.settings.arch}"
            )

    def requirements(self):
        # ispell requires ncurses (wide-character) for terminal UI
        self.requires("ncurses/6.5")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        # Create local.h from sample before applying patches
        src = self.source_folder
        samp = os.path.join(src, "local.h.samp")
        dest = os.path.join(src, "local.h")
        if os.path.exists(samp) and not os.path.exists(dest):
            shutil.copy(samp, dest)
        apply_conandata_patches(self)

    def build(self):
        # R33: get compiler from Conan toolchain conf, never from shell env
        compilers = self.conf.get(
            "tools.build:compiler_executables", default={}, check_type=dict
        ) or {}
        cc = compilers.get("c", "clang")

        # ncurses package provides include/ and lib/
        ncurses_dep = self.dependencies["ncurses"]
        ncurses_dir = ncurses_dep.package_folder.replace("\\", "/")
        ncurses_inc = f"{ncurses_dir}/include"
        ncurses_lib = f"{ncurses_dir}/lib"

        self.run(
            f'make -j1 '
            f'CC="{cc}" '
            f'CFLAGS="-I{ncurses_inc}" '
            f'LDFLAGS="-L{ncurses_lib}" '
            f'TERMLIB="-lncursesw" '
            f'TERMINCLUDE="-I{ncurses_inc}/ncursesw" '
            f'LANGUAGES=""',  # skip building default language (requires Perl + data)
            cwd=self.source_folder,
            env=["conanbuild"],
        )

    def package(self):
        copy(
            self, "README*",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        self.run(
            f'make install '
            f'DESTDIR="{self.package_folder}" '
            f'BINDIR=/bin '
            f'LIBDIR=/lib/ispell '
            f'MANDIR=/share/man '
            f'LANGUAGES=""',
            cwd=self.source_folder,
            env=["conanbuild"],
        )

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = []
        self.cpp_info.includedirs = []
