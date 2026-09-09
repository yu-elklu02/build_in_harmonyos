#!/usr/bin/env python3
"""Conan recipe for Apache APR-util 1.6.3."""

import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, PkgConfigDeps
from conan.tools.layout import basic_layout


class AprUtilConan(ConanFile):
    name = "apr-util"
    version = "1.6.3"
    description = "Apache Portable Runtime utility library"
    license = "Apache-2.0"
    homepage = "https://apr.apache.org/"
    url = "https://apr.apache.org/"
    # Always static: see note below on the legacy buildconf build system.
    package_type = "static-library"

    settings = "os", "arch", "compiler", "build_type"
    options = {"fPIC": [True, False]}
    default_options = {"fPIC": True}

    # APR-util 1.6.3 uses the legacy buildconf build system, which does not
    # understand --enable-shared/--disable-static and always produces the
    # static libaprutil-1.a. So this package is static (matching apr).

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("Only Linux and OHOS are supported")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("OHOS builds currently support armv8 only")

    def requirements(self):
        # apr-util's public headers include APR core headers (apr_pools.h,
        # apr_general.h, ...) and consumers link libapr-1 via the static
        # aprutil, so apr's headers (and libs) must be transitive.
        self.requires("apr/1.7.6.1", transitive_headers=True)
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
            # NB: the legacy buildconf configure does not accept
            # --enable-shared/--disable-static (it warns "unrecognized
            # options" and always builds the static libaprutil-1.a).
        ]
        if self.settings.os == "OHOS":
            shell = os.environ.get("CONFIG_SHELL", "/data/service/hnp/bin/bash")
            configure = os.path.join(self.source_folder, "configure")
            self.run(
                f'"{shell}" "{configure}" ' + " ".join(args),
                cwd=self.build_folder,
                env="conanbuild",
            )
            self.run(f'make -j2 SHELL="{shell}"', cwd=self.build_folder, env="conanbuild")
        else:
            autotools = Autotools(self)
            autotools.configure(args=args)
            autotools.make()
        if self.settings.os == "OHOS":
            # make check runs the freshly built test binaries, which need the
            # shared deps (expat) at runtime; the build env alone has no
            # LD_LIBRARY_PATH.
            dep_libs = ":".join(
                os.path.join(dep.package_folder, "lib")
                for dep in (self.dependencies["expat"], self.dependencies["apr"])
                if os.path.isdir(os.path.join(dep.package_folder, "lib"))
            )
            self.run(
                f'"{shell}" -c "LD_LIBRARY_PATH={dep_libs}${{LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}} make check SHELL={shell}"',
                cwd=self.build_folder,
                env="conanbuild",
            )
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
        # apr-util public headers live in include/apr-1/ (apr_general.h,
        # apr_pools.h, apr_xml.h, ...), not directly under include/.
        self.cpp_info.includedirs = ["include/apr-1"]
        self.cpp_info.set_property("pkg_config_name", "apu-1")
        self.cpp_info.set_property("cmake_file_name", "apr-util")
        self.cpp_info.set_property("cmake_target_name", "apr-util::apr-util")
