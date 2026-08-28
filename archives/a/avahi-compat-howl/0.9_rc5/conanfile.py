#!/usr/bin/env python3
"""Conan recipe for Avahi's HOWL compatibility library."""

import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
from conan.tools.files import copy, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.gnu import PkgConfigDeps
from conan.tools.layout import basic_layout


class AvahiCompatHowlConan(ConanFile):
    name = "avahi-compat-howl"
    version = "0.9_rc5"
    description = "HOWL compatibility library from Avahi"
    license = "LGPL-2.1-or-later"
    homepage = "https://github.com/lathiat/avahi"
    url = "https://github.com/lathiat/avahi"
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
        self.requires("dbus/1.14.10")

    def build_requirements(self):
        self.tool_requires("automake/1.18")
        self.tool_requires("libtool/2.5.4")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        PkgConfigDeps(self).generate()
        tc = AutotoolsToolchain(self)
        tc.generate()
        VirtualBuildEnv(self).generate()
        VirtualRunEnv(self).generate()

    def build(self):
        shell = os.environ.get("CONFIG_SHELL", "/bin/sh")
        if self.settings.os == "OHOS":
            shell = os.environ.get("CONFIG_SHELL", "/data/service/hnp/bin/bash")
            configure = os.path.join(self.source_folder, "configure")
            # Avahi's gettext bootstrap invokes autopoint.  OHOS workers ship
            # the matching gettext templates outside the Conan environment.
            gettext_root = os.environ.get(
                "GETTEXT_ROOT", "/data/service/hnp/gettext.org/gettext_0.26"
            )
            gettext_bin = os.path.join(gettext_root, "bin")
            gettext_data = os.path.join(gettext_root, "share", "gettext")
            os.environ["PATH"] = (
                gettext_bin + os.pathsep + os.environ.get("PATH", "")
            )
            os.environ["gettext_datadir"] = gettext_data
            self.run(f'"{shell}" -c "umask 000; autoreconf -fi"', cwd=self.source_folder, env="conanbuild")
            self.run(
                "sed -i 's/umask 077/umask 000/g' configure",
                cwd=self.source_folder,
                env="conanbuild",
            )
            args = [
                "--prefix=/",
                "--enable-shared" if self.options.shared else "--disable-shared",
                "--enable-static" if not self.options.shared else "--disable-static",
                "--enable-compat-howl",
                "--disable-compat-libdns_sd",
                "--disable-glib",
                "--disable-gobject",
                "--disable-libevent",
                "--disable-qt3",
                "--disable-qt4",
                "--disable-qt5",
                "--disable-gtk",
                "--disable-gtk3",
                "--disable-python",
                "--disable-gdbm",
                "--disable-libdaemon",
                "--disable-autoipd",
                "--disable-manpages",
                "--disable-xmltoman",
                "--with-xml=none",
                "--enable-tests",
                "--with-systemdsystemunitdir=no",
                "--with-dbus-sys=no",
                "--with-distro=none",
                "--build=aarch64-unknown-linux-ohos",
            ]
            self.run(
                f'"{shell}" "{configure}" ' + " ".join(args),
                cwd=self.build_folder,
                env="conanbuild",
            )
        else:
            autotools = Autotools(self)
            autotools.configure()
        if self.settings.os == "OHOS":
            self.run(f'make -j2 SHELL="{shell}"', cwd=self.build_folder, env="conanbuild")
        else:
            autotools.make()

    def package(self):
        if self.settings.os == "OHOS":
            shell = os.environ.get("CONFIG_SHELL", "/data/service/hnp/bin/bash")
            self.run(
                f'make install DESTDIR="{self.package_folder}" SHELL="{shell}"',
                cwd=self.build_folder,
                env="conanbuild",
            )
        else:
            Autotools(self).install()
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

    def package_info(self):
        self.cpp_info.libs = ["howl", "avahi-client", "avahi-common"]
        self.cpp_info.set_property("pkg_config_name", "avahi-compat-howl")
        self.cpp_info.set_property("cmake_file_name", "avahi-compat-howl")
        self.cpp_info.set_property(
            "cmake_target_name", "avahi-compat-howl::avahi-compat-howl"
        )
        self.cpp_info.includedirs = [
            "include",
            "include/avahi-compat-howl",
            "include/avahi-client",
            "include/avahi-common",
        ]
