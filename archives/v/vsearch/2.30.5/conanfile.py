#!/usr/bin/env python3
"""Conan recipe — vsearch 2.30.5 (Autotools, C++ bioinformatics tool).

vsearch: Versatile open-source tool for microbiome analysis.
Build system: Autotools. The GitHub release tarball includes a pre-generated
configure script — autogen.sh is NOT needed.
Produces command-line executable: bin/vsearch.
"""
import os
from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches


class VsearchConan(ConanFile):
    name = "vsearch"
    version = "2.30.5"
    description = (
        "Versatile open-source tool for microbiome analysis. "
        "Supports chimera detection, clustering, full-length and prefix "
        "dereplication, searching, sorting and pairwise alignment."
    )
    license = "BSD-2-Clause OR GPL-3.0-or-later"
    homepage = "https://github.com/torognes/vsearch"
    url = ""  # CI fills this

    package_type = "application"

    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)
        # The GitHub release tarball already includes a pre-generated configure
        # script — no autogen.sh/autoreconf needed.

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--prefix=/")
        tc.configure_args.append("--without-zlib")
        tc.configure_args.append("--without-bz2")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()
        # Run upstream test suite (shell scripts in test/)
        autotools.make(target="check")

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = []

