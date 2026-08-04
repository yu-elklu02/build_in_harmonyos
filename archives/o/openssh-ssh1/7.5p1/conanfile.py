#!/usr/bin/env python3
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
)
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class OpenSshSsh1Conan(ConanFile):
    name = "openssh-ssh1"
    version = "7.5p1"
    description = "Portable OpenSSH SSH1-compatible release"
    license = "BSD-2-Clause"
    homepage = "https://www.openssh.com/portable.html"
    package_type = "application"

    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def requirements(self):
        self.requires("zlib/1.3.1.1")
        self.requires("openssl/1.1.1w")

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration(
                f"{self.name} is only supported on Linux/OHOS"
            )
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration(
                f"{self.name} currently supports OHOS armv8 only"
            )

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        tc = AutotoolsToolchain(self)
        zlib_root = self.dependencies["zlib"].package_folder
        openssl_root = self.dependencies["openssl"].package_folder

        tc.configure_args.extend([
            "--prefix=/",
            "--sysconfdir=/etc/ssh",
            "--libexecdir=/libexec",
            "--with-ssh1",
            f"--with-zlib={zlib_root}",
            f"--with-ssl-dir={openssl_root}",
            "--with-sandbox=no",
            "--without-zlib-version-check",
            "--without-openssl-header-check",
            "--disable-utmp",
            "--disable-utmpx",
            "--disable-wtmp",
            "--disable-wtmpx",
            "--disable-lastlog",
        ])

        if self.settings.os == "OHOS":
            tc.configure_args.append("ac_cv_header_linux_if_tun_h=no")
            tc.extra_cflags.append("-D_GNU_SOURCE")
            tc.extra_cflags.append("-D__USE_GNU")

        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()
        autotools.make(target="tests")

    def package(self):
        autotools = Autotools(self)
        autotools.make(
            target="install-nokeys",
            args=[f"DESTDIR={self.package_folder}"],
        )
        copy(self, "LICENCE", self.source_folder,
             os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.bindirs = ["bin", "sbin"]
        self.runenv_info.prepend_path(
            "PATH", os.path.join(self.package_folder, "bin")
        )
        self.runenv_info.prepend_path(
            "PATH", os.path.join(self.package_folder, "sbin")
        )
