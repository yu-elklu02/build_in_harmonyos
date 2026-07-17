#!/usr/bin/env python3
"""Conan recipe for VCFtools 0.1.17 (Autotools) on OpenHarmony.

The release builds one C++ executable and installs a suite of Perl tools. The
C++ executable links zlib; the Perl tools use bgzip/tabix from HTSlib for
indexed VCF operations.
"""
import os

from conan import ConanFile
from conan.tools.env import Environment, VirtualRunEnv
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    download,
    export_conandata_patches,
    get,
    replace_in_file,
)
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout


class VcftoolsConan(ConanFile):
    name = "vcftools"
    version = "0.1.17"
    description = "C++ and Perl command-line tools for working with VCF files"
    license = "LGPL-3.0-only"
    homepage = "https://vcftools.github.io/"
    url = "https://github.com/vcftools/vcftools"
    package_type = "application"

    settings = "os", "compiler", "build_type", "arch"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("zlib/1.3.1")
        self.requires(
            "htslib/1.24-r0",
            headers=False,
            libs=False,
            run=True,
        )

    def layout(self):
        basic_layout(self, src_folder=".")
        self.folders.build = "."

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

        # The release archive omits src/perl/test.t even though it is present
        # in the matching upstream tag. Fetch that exact test with a checksum.
        test_data = self.conan_data["upstream_tests"]["perl_test"]
        test_path = os.path.join(self.source_folder, "src", "perl", "test.t")
        download(self, filename=test_path, **test_data)

    def generate(self):
        AutotoolsDeps(self).generate()
        PkgConfigDeps(self).generate()
        VirtualRunEnv(self).generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--prefix=/",
            "--disable-silent-rules",
            "--with-pmdir=lib/perl5/site_perl",
        ])
        tc.generate()

        # OHOS /tmp may be read-only. Autoconf and the Perl tests both honor
        # TMPDIR, so provide a writable location through Conan's build env.
        tmpdir = os.path.expanduser("~/tmp")
        os.makedirs(tmpdir, exist_ok=True)
        env = Environment()
        env.define_path("TMPDIR", tmpdir)
        env.vars(self).save_script("vcftools_tmpdir")

    def build(self):
        apply_conandata_patches(self)

        autotools = Autotools(self)
        autotools.configure()
        autotools.make(args=["-j1"])

        test_path = os.path.join(self.source_folder, "src", "perl", "test.t")

        # Test::Most is not part of Perl core, while every assertion used by
        # upstream test.t is provided by core Test::More. Keep all 75 tests.
        replace_in_file(
            self,
            test_path,
            "use Test::Most tests => 75;",
            "use Test::More tests => 75;",
        )

        # Upstream test.t lives in src/perl but points one level up for the
        # top-level examples directory. Correct the omitted directory level.
        replace_in_file(
            self,
            test_path,
            "$path/../examples",
            "$path/../../examples",
        )

        self.run(
            "perl test.t",
            cwd=os.path.dirname(test_path),
            env="conanrun",
        )

    def package(self):
        Autotools(self).install()
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = []
        self.cpp_info.libs = []

        perl_lib = os.path.join(self.package_folder, "lib", "perl5", "site_perl")
        self.runenv_info.prepend_path("PERL5LIB", perl_lib)
        self.buildenv_info.prepend_path("PERL5LIB", perl_lib)
