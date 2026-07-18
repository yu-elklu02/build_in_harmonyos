#!/usr/bin/env python3
"""Conan recipe — vsearch 2.30.5 (Autotools, C++ bioinformatics tool).

vsearch: Versatile open-source tool for microbiome analysis.
Build system: Autotools (configure.ac, needs autogen.sh to generate configure).
No mandatory external dependencies; optional zlib/bzip2 for compressed input.
Produces command-line executable: bin/vsearch.
"""
import os
import shutil
from conan import ConanFile
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches, chdir


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
        # vsearch GitHub archive does not include pre-generated configure;
        # run autogen.sh to create it.  On OHOS the toybox cp can fail to
        # copy automake auxiliary files, so we copy them manually first.
        self._copy_automake_aux_files()
        with chdir(self, self.source_folder):
            self.run("sh autogen.sh", env="conanbuild")

    def _copy_automake_aux_files(self):
        """Copy automake auxiliary files to source dir (workaround for
        toybox cp permission issue on OHOS, E-pattern from notes.md)."""
        aux_files = [
            "config.guess", "config.sub", "install-sh",
            "depcomp", "compile", "missing",
        ]
        # Typical automake data directories
        candidates = [
            "/usr/share/automake-1.17",
            "/usr/share/automake-1.16",
            "/data/service/hnp/automake/automake_1.17/share/automake-1.17",
            "/data/service/hnp/automake/automake_1.16/share/automake-1.16",
        ]
        src_dir = self.source_folder
        for aux in aux_files:
            dst = os.path.join(src_dir, aux)
            if os.path.exists(dst):
                continue
            for cand in candidates:
                src = os.path.join(cand, aux)
                if os.path.exists(src):
                    shutil.copy2(src, dst)
                    self.output.info(f"Copied {aux} from {cand}")
                    break

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
