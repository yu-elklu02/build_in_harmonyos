#!/usr/bin/env python3
"""Conan recipe — vsearch 2.30.5 (Autotools, C++ bioinformatics tool).

vsearch: Versatile open-source tool for microbiome analysis.
The GitHub archive does not include a pre-generated configure script.
patches/configure is a pre-generated configure (via autoreconf -fi on Ubuntu)
shipped with this recipe to avoid requiring autoconf/automake on the CI worker.
"""
import os
import shutil
from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches, copy


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
    exports_sources = "patches/configure"

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)
        # Copy pre-generated configure into source folder and make executable.
        # The GitHub archive does not include configure; we ship it with the recipe.
        src_configure = os.path.join(self.recipe_folder, "patches", "configure")
        dst_configure = os.path.join(self.source_folder, "configure")
        shutil.copy2(src_configure, dst_configure)
        os.chmod(dst_configure, 0o755)
        self.output.info("Pre-generated configure installed.")

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--prefix=/")
        tc.configure_args.append("--without-zlib")
        tc.configure_args.append("--without-bz2")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        # Restore execute bit on configure after Conan copies sources to build dir
        configure = os.path.join(self.build_folder, "configure")
        if os.path.isfile(configure):
            os.chmod(configure, 0o755)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()
        autotools.make(target="check")

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = []



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
        # vsearch does not ship a pre-generated configure in its GitHub archive.
        # configure.ac uses AM_* macros (automake), so we need both autoconf
        # and automake's m4 macro files. On OHOS CI, automake is not in PATH
        # but its m4 files may exist in versioned HNP directories.
        env = Environment()

        # Find autoconf binary
        autoconf_bin = None
        for candidate in [
            "/data/service/hnp/autoconf.org/autoconf_2.72/bin",
            "/data/service/hnp/bin",
            "/usr/local/bin",
            "/usr/bin",
        ]:
            if os.path.isfile(os.path.join(candidate, "autoconf")):
                autoconf_bin = candidate
                env.prepend_path("PATH", candidate)
                self.output.info(f"Using autoconf from {candidate}")
                break

        # Find automake m4 macro files (needed for AM_* macros in configure.ac)
        aclocal_dirs = []
        search_roots = [
            "/data/service/hnp/automake.org",
            "/data/service/hnp",
            "/usr/share",
            "/usr/local/share",
        ]
        for root in search_roots:
            if not os.path.isdir(root):
                continue
            # Direct aclocal dir
            direct = os.path.join(root, "aclocal")
            if os.path.isdir(direct):
                aclocal_dirs.append(direct)
                self.output.info(f"Found aclocal m4 at {direct}")
            # Versioned subdir: automake.org/automake_1.17/share/aclocal
            try:
                for entry in os.listdir(root):
                    candidate = os.path.join(root, entry, "share", "aclocal")
                    if os.path.isdir(candidate):
                        aclocal_dirs.append(candidate)
                        self.output.info(f"Found aclocal m4 at {candidate}")
            except (PermissionError, NotADirectoryError):
                pass

        # Build autoconf command with -I flags for each aclocal directory
        include_flags = " ".join(f"-I {d}" for d in aclocal_dirs)
        with env.vars(self).apply():
            self.run(f"autoconf {include_flags}")

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


