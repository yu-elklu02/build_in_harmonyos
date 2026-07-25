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

        # The GitHub archive omits generated Autotools output. Ship the
        # matching scripts and templates so offline CI can run configure.
        executable_files = (
            "configure", "compile", "missing", "install-sh", "depcomp",
            "config.guess", "config.sub",
        )
        template_files = (
            "aclocal.m4", "config.h.in", "Makefile.in",
            os.path.join("src", "Makefile.in"),
            os.path.join("man", "Makefile.in"),
        )
        for filename in executable_files + template_files:
            source = os.path.join(self.source_folder, "patches", filename)
            destination = os.path.join(self.source_folder, filename)
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            shutil.copy2(source, destination)
        for filename in executable_files:
            destination = os.path.join(self.source_folder, filename)
            os.chmod(destination, 0o755)
        self.output.info("Pre-generated Autotools files installed.")

    def generate(self):
        if str(self.settings.os) == "OHOS":
            tmpdir = os.path.expanduser("~/tmp/vsearch")
            os.makedirs(tmpdir, exist_ok=True)

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--prefix=/")
        if str(self.settings.os) == "OHOS":
            # The upstream configure script rejects config.guess' HarmonyOS
            # output. Use the OHOS triplet accepted by the bundled config.sub.
            triplet = "aarch64-unknown-linux-ohos"
            tc.configure_args.extend([f"--build={triplet}", f"--host={triplet}"])
        tc.generate()

    def build(self):
        apply_conandata_patches(self)

        if str(self.settings.os) == "OHOS":
            tmpdir = os.path.expanduser("~/tmp/vsearch")
            os.makedirs(tmpdir, exist_ok=True)
            # Conan 2.29 does not add recipe buildenv_info to conanbuildenv.
            # Set TMPDIR on this process so configure and config.status inherit it.
            os.environ["TMPDIR"] = tmpdir

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
