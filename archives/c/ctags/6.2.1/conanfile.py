#!/usr/bin/env python3
"""Conan recipe — ctags 6.2.1 (Universal Ctags).

Autotools project. Official release tarball includes pre-generated configure.
Platform adaptation: HMDFS umask 077 fix for config.status.
"""
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class CtagsConan(ConanFile):
    name = "ctags"
    version = "6.2.1"
    description = "Universal Ctags - a multilanguage code indexing tool"
    license = "MIT"
    homepage = "https://ctags.io/"
    url = ""  # CI fills this

    settings = "os", "compiler", "build_type", "arch"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        # No external Conan dependencies required
        # ctags optionally uses libxml2, jansson, libseccomp, yaml, libpcre2
        # but all are optional and not required for basic functionality
        pass

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        # R26: Terminal tools must be statically linked
        tc.extra_ldflags.append("-static")
        if str(self.settings.os) == "OHOS":
            if str(self.settings.arch) != "armv8":
                raise ConanInvalidConfiguration("ctags OHOS packages require armv8")
            # Keep Autotools target identification deterministic for OHOS.
            tc.configure_args.extend([
                "--build=aarch64-unknown-linux-ohos",
                "--host=aarch64-unknown-linux-ohos",
            ])
        tc.generate()

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        # ctags is a terminal tool, no shared libraries provided
        self.cpp_info.libs = []
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["bin"]
