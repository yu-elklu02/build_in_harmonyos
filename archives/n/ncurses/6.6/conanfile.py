#!/usr/bin/env python3
import os
import shlex

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class NcursesConan(ConanFile):
    name = "ncurses"
    version = "6.6"
    description = "Character screen handling library"
    license = "MIT"
    homepage = "https://invisible-island.net/ncurses/"
    url = "https://invisible-island.net/ncurses/"
    package_type = "library"

    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("ncurses supports Linux and OHOS")

    def layout(self):
        basic_layout(self, src_folder=".")
        self.folders.build = "."

    def source(self):
        sources = dict(self.conan_data["sources"])
        mirror_url = sources.pop("mirror_url", None)
        try:
            get(self, **sources, strip_root=True)
        except Exception as error:
            if not mirror_url:
                raise
            self.output.warning(f"Primary source failed ({error}); trying GNU mirror")
            get(self, url=mirror_url, sha256=sources["sha256"], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.extend([
            "--enable-widec",
            "--without-ada",
            "--without-cxx",
            "--without-cxx-binding",
            "--without-manpages",
            "--without-progs",
            "--without-tests",
            "--with-termlib",
        ])
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        if str(self.settings.os) == "OHOS":
            self._configure_with_ohos_shell()
        else:
            autotools.configure()
        autotools.make(args=["-j1"])

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(self, "COPYING", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.libs = ["ncursesw", "tinfow"]
        self.cpp_info.set_property("pkg_config_name", "ncursesw")
        self.cpp_info.set_property("cmake_file_name", "ncurses")
        self.cpp_info.set_property("cmake_target_name", "ncurses::ncurses")

    def _configure_with_ohos_shell(self):
        configure = os.path.join(self.build_folder, "configure")
        os.chmod(configure, 0o755)
        args = [
            "--disable-shared",
            "--enable-static",
            "--prefix=/",
            "--bindir=${prefix}/bin",
            "--sbindir=${prefix}/bin",
            "--libdir=${prefix}/lib",
            "--includedir=${prefix}/include",
            "--oldincludedir=${prefix}/include",
            "--host=aarch64-ohos",
            "--build=aarch64-linux-gnu",
            "--enable-widec",
            "--without-ada",
            "--without-cxx",
            "--without-cxx-binding",
            "--without-manpages",
            "--without-progs",
            "--without-tests",
            "--with-termlib",
        ]
        shell = "/data/service/hnp/bin/bash"
        command = " ".join([shlex.quote(configure)] + [shlex.quote(arg) for arg in args])
        self.run(f"CONFIG_SHELL={shell} SHELL={shell} {command}")
