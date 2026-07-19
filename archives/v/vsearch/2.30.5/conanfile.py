#!/usr/bin/env python3
"""Conan recipe — vsearch 2.30.5 (Autotools, C++ bioinformatics tool).

vsearch: Versatile open-source tool for microbiome analysis.
The GitHub archive tarball does NOT include a pre-generated configure script.
autogen.sh must be run to generate it. On OHOS, automake/aclocal are in
versioned HNP directories and must be added to PATH manually.
"""
import os
import shutil
from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches
from conan.tools.env import Environment


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

    def _find_hnp_tool(self, name):
        """Search for a tool in OHOS HNP versioned directories."""
        search_roots = [
            "/data/service/hnp",
            "/data/service/hnp/automake.org",
            "/usr/local/bin",
            "/usr/bin",
        ]
        for root in search_roots:
            if not os.path.isdir(root):
                continue
            # Direct path
            direct = os.path.join(root, name)
            if os.path.isfile(direct):
                return os.path.dirname(direct)
            # Versioned subdir: automake.org/automake_1.17/bin/aclocal
            try:
                for entry in os.listdir(root):
                    candidate = os.path.join(root, entry, "bin", name)
                    if os.path.isfile(candidate):
                        return os.path.join(root, entry, "bin")
            except PermissionError:
                pass
        return None

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

        # Build extra PATH for automake/autoconf tools on OHOS HNP
        env = Environment()
        for tool in ("aclocal", "automake", "autoconf", "autoreconf"):
            tool_dir = self._find_hnp_tool(tool)
            if tool_dir:
                env.prepend_path("PATH", tool_dir)
                self.output.info(f"Found {tool} at {tool_dir}")

        # Also set explicit AUTOCONF if found in HNP
        autoconf_path = None
        for candidate in [
            "/data/service/hnp/autoconf.org/autoconf_2.72/bin/autoconf",
            "/data/service/hnp/bin/autoconf",
            "/usr/bin/autoconf",
        ]:
            if os.path.isfile(candidate):
                autoconf_path = candidate
                break
        if autoconf_path:
            env.define("AUTOCONF", autoconf_path)

        with env.vars(self).apply():
            self.run("sh autogen.sh")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--prefix=/")
        tc.configure_args.append("--without-zlib")
        tc.configure_args.append("--without-bz2")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        # configure was generated in source(); run it via sh to avoid
        # execute-bit issues on OHOS HMDFS
        self.run(
            "sh configure "
            "--prefix=/ "
            "--bindir=${prefix}/bin "
            "--sbindir=${prefix}/bin "
            "--libdir=${prefix}/lib "
            "--includedir=${prefix}/include "
            "--without-zlib "
            "--without-bz2",
            env="conanbuild"
        )
        autotools = Autotools(self)
        autotools.make()
        autotools.make(target="check")

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = []


