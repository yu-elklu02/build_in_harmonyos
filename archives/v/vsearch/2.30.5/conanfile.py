#!/usr/bin/env python3
"""Conan recipe for vsearch 2.30.5 on OpenHarmony.

The GitHub archive omits configure. The recipe ships a pre-generated configure
script so the CI worker does not need autoconf or automake.
"""
import os
import shutil

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain


class VsearchConan(ConanFile):
    name = "vsearch"
    version = "2.30.5"
    description = "Versatile open-source tool for microbiome analysis."
    license = "BSD-2-Clause OR GPL-3.0-or-later"
    homepage = "https://github.com/torognes/vsearch"
    url = ""  # CI fills this
    package_type = "application"

    settings = "os", "arch", "compiler", "build_type"
    # Export the directory so source() can access patches/configure from the
    # exported recipe cache, preserving the path used below.
    exports_sources = "patches/*"

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

        # The GitHub archive does not include configure; ship a generated copy
        # to avoid requiring Autotools generators on the OHOS CI worker.
        # exports_sources are materialized next to self.source_folder, not in
        # self.recipe_folder, during Conan's source() phase.
        src_configure = os.path.join(
            os.path.dirname(self.source_folder), "patches", "configure"
        )
        dst_configure = os.path.join(self.source_folder, "configure")
        shutil.copy2(src_configure, dst_configure)
        os.chmod(dst_configure, 0o755)
        self.output.info("Pre-generated configure installed.")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend(["--prefix=/", "--without-zlib", "--without-bz2"])
        tc.generate()

    def build(self):
        apply_conandata_patches(self)

        # Conan source copies can lose the executable bit on OHOS HMDFS.
        configure = os.path.join(self.build_folder, "configure")
        if os.path.isfile(configure):
            os.chmod(configure, 0o755)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make()
        autotools.make(target="check")

    def package(self):
        Autotools(self).install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = []
