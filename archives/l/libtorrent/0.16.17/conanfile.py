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
from conan.tools.gnu import Autotools, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout


class LibtorrentConan(ConanFile):
    name = "libtorrent"
    version = "0.16.17"
    description = "Rakshasa high-performance BitTorrent library"
    license = "GPL-2.0-or-later"
    homepage = "https://github.com/rakshasa/libtorrent"
    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def requirements(self):
        self.requires("libcurl/8.5.0")
        self.requires("zlib/1.3.1.1")
        self.requires("openssl/3.5.6")

    def build_requirements(self):
        self.test_requires("cppunit/1.15.1")

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("libtorrent is only supported on Linux/OHOS")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("libtorrent supports OHOS armv8 only")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self)

    def source(self):
        get(
            self,
            **self.conan_data["sources"],
            filename=f"libtorrent-{self.version}.tar.gz",
            strip_root=True,
        )
        apply_conandata_patches(self)

    def generate(self):
        PkgConfigDeps(self).generate()
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--enable-shared" if self.options.shared else "--disable-shared",
            "--disable-static" if self.options.shared else "--enable-static",
        ])
        tc.generate()

    def build(self):
        previous_pkg_config_path = os.environ.get("PKG_CONFIG_PATH")
        os.environ["PKG_CONFIG_PATH"] = self.generators_folder
        try:
            autotools = Autotools(self)
            autotools.configure()
            autotools.make()
            autotools.make(target="check")
        finally:
            if previous_pkg_config_path is None:
                os.environ.pop("PKG_CONFIG_PATH", None)
            else:
                os.environ["PKG_CONFIG_PATH"] = previous_pkg_config_path

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(self, "COPYING", self.source_folder,
             os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["torrent"]
        self.cpp_info.system_libs = ["pthread"]
