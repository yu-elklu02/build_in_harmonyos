#!/usr/bin/env python3
"""Conan recipe for Apache APR-util 1.6.3."""

import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout


class AprUtilConan(ConanFile):
    name = "apr-util"
    version = "1.6.3"
    description = "Apache Portable Runtime utility library"
    license = "Apache-2.0"
    homepage = "https://apr.apache.org/"
    url = "https://apr.apache.org/"
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("Only Linux and OHOS are supported")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("OHOS builds currently support armv8 only")

    def requirements(self):
        self.requires("apr/1.7.6")
        self.requires("expat/2.8.2")

    def layout(self):
        basic_layout(self)

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        PkgConfigDeps(self).generate()
        tc = AutotoolsToolchain(self)
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        apr = self.dependencies["apr"].package_folder
        expat = self.dependencies["expat"].package_folder
        args = [
            f"--prefix={self.package_folder}",
            f"--with-apr={apr}",
            f"--with-expat={expat}",
            "--disable-dbm",
            "--disable-util-dso",
            "--disable-util-ldap",
            "--without-ldap",
            "--without-crypto",
            "--disable-debug",
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--enable-static" if not self.options.shared else "--disable-static",
        ]
        if self.settings.os == "OHOS":
            shell = os.environ.get("CONFIG_SHELL", "/data/service/hnp/bin/bash")
            self.run(
                f'"{shell}" configure ' + " ".join(args),
                cwd=self.build_folder,
                env="conanbuild",
            )
            self.run(f'make -j2 SHELL="{shell}"', cwd=self.build_folder, env="conanbuild")
        else:
            autotools = Autotools(self)
            autotools.configure(args=args)
            autotools.make()
        if self.settings.os == "OHOS":
            self.run(f'make check SHELL="{shell}"', cwd=self.build_folder, env="conanbuild")
        else:
            self.run("make check", cwd=self.build_folder)

    def package(self):
        if self.settings.os == "OHOS":
            shell = os.environ.get("CONFIG_SHELL", "/data/service/hnp/bin/bash")
            self.run(
                f'make install SHELL="{shell}"',
                cwd=self.build_folder,
                env="conanbuild",
            )
        else:
            Autotools(self).install()
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["aprutil-1"]
        self.cpp_info.set_property("pkg_config_name", "apu-1")
        self.cpp_info.set_property("cmake_file_name", "apr-util")
        self.cpp_info.set_property("cmake_target_name", "apr-util::apr-util")
