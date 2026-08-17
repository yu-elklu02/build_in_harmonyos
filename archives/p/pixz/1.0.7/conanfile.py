#!/usr/bin/env python3
"""Conan recipe for pixz 1.0.7."""

import os
import shutil
from pathlib import Path

from conan import ConanFile
from conan.tools.build import load_toolchain_args
from conan.tools.env import Environment
from conan.tools.files import get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsDeps, AutotoolsToolchain, PkgConfigDeps
from conan.tools.layout import basic_layout


class PixzConan(ConanFile):
    name = "pixz"
    version = "1.0.7"
    description = "Parallel indexed xz compressor and decompressor"
    license = "BSD-2-Clause"
    homepage = "https://github.com/vasi/pixz"
    url = "https://github.com/vasi/pixz"
    package_type = "application"

    settings = "os", "compiler", "build_type", "arch"

    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires("libarchive/3.8.7")
        self.requires("xz/5.6.2")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        AutotoolsDeps(self).generate()
        PkgConfigDeps(self).generate()

        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--build=aarch64-unknown-linux-gnu")
        tc.generate()

        gen_dir = Path(self.generators_folder)
        xz_pc = gen_dir / "xz.pc"
        liblzma_pc = gen_dir / "liblzma.pc"
        if xz_pc.is_file() and not liblzma_pc.is_file():
            shutil.copy2(xz_pc, liblzma_pc)

        env = Environment()
        for dep_name in ("libarchive", "xz"):
            dep = self.dependencies[dep_name]
            for bindir in dep.cpp_info.bindirs:
                env.prepend_path("PATH", str(bindir))
            for libdir in dep.cpp_info.libdirs:
                env.prepend_path("LD_LIBRARY_PATH", str(libdir))
        config_shell = os.environ.get("CONFIG_SHELL")
        if config_shell:
            env.define("CONFIG_SHELL", config_shell)
        env.vars(self).save_script("pixz_ohos_env")

    def build(self):
        self._patch_sources()
        configure = os.path.join(self.source_folder, "configure")
        if os.path.isfile(configure):
            os.chmod(configure, 0o755)

        autotools = Autotools(self)
        configure_args = load_toolchain_args(self.generators_folder).get("configure_args")
        if self.settings.os == "OHOS":
            config_shell = os.environ.get("CONFIG_SHELL") or shutil.which("bash") or "/system/bin/sh"
            os.makedirs(self.build_folder, exist_ok=True)
            self.run(f'CONFIG_SHELL="{config_shell}" "{config_shell}" "{configure}" {configure_args}',
                     cwd=self.build_folder, env=["conanbuild", "pixz_ohos_env"])
        else:
            autotools.configure()

        self.run("make -j1", cwd=self.build_folder, env=["conanbuild", "pixz_ohos_env"])
        self.run("make check -j1", cwd=self.build_folder, env=["conanbuild", "conanrun", "pixz_ohos_env"])

    def _patch_sources(self):
        config_guess = os.path.join(self.source_folder, "config.guess")
        replace_in_file(
            self,
            config_guess,
            "    *:NetBSD:*:*)",
            """    *:HarmonyOS:*:*)
\tcase "$UNAME_MACHINE" in
\t    aarch64|arm64) machine=aarch64 ;;
\t    armv7*|armv8*) machine=arm ;;
\t    x86_64|amd64)  machine=x86_64 ;;
\t    i?86)          machine=i686 ;;
\t    *)             machine="$UNAME_MACHINE" ;;
\tesac
\techo "$machine-unknown-linux-ohos"
\texit ;;
    *:NetBSD:*:*)""",
            strict=True,
        )

        config_sub = os.path.join(self.source_folder, "config.sub")
        replace_in_file(
            self,
            config_sub,
            "  nto-qnx* | linux-gnu* | linux-android* | linux-dietlibc | linux-newlib* | \\",
            "  nto-qnx* | linux-gnu* | linux-android* | linux-ohos* | linux-dietlibc | linux-newlib* | \\",
            strict=True,
        )
        replace_in_file(
            self,
            config_sub,
            """  android-linux)
    os=-linux-android
    basic_machine=`echo "$1" | sed 's/^\\(.*\\)-\\([^-]*-[^-]*\\)$/\\1/'`-unknown
    ;;""",
            """  android-linux)
    os=-linux-android
    basic_machine=`echo "$1" | sed 's/^\\(.*\\)-\\([^-]*-[^-]*\\)$/\\1/'`-unknown
    ;;
  ohos-linux)
    os=-linux-ohos
    basic_machine=`echo "$1" | sed 's/^\\(.*\\)-\\([^-]*-[^-]*\\)$/\\1/'`-unknown
    ;;""",
            strict=True,
        )
        replace_in_file(
            self,
            config_sub,
            "      | -midipix* | -mingw32* | -mingw64* | -linux-gnu* | -linux-android* \\",
            "      | -midipix* | -mingw32* | -mingw64* | -linux-gnu* | -linux-android* | -linux-ohos* \\",
            strict=True,
        )

        configure = os.path.join(self.source_folder, "configure")
        if os.path.isfile(configure):
            replace_in_file(self, configure, "umask 077 && mktemp -d", "umask 022 && mktemp -d", strict=False)
            replace_in_file(self, configure, 'umask 077 && mkdir "$tmp"', 'umask 022 && mkdir "$tmp"', strict=False)

    def package(self):
        self.run("make install", cwd=self.build_folder, env=["conanbuild", "pixz_ohos_env"])

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.runenv_info.prepend_path("PATH", bindir)
