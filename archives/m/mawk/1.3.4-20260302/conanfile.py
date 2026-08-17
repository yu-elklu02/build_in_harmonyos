import os
import re

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import (
    copy,
    get,
    replace_in_file,
)
from conan.tools.layout import basic_layout


class MawkConan(ConanFile):
    name = "mawk"
    version = "1.3.4-20260302"
    package_type = "application"
    description = "Interpreter for the AWK programming language"
    license = "GPL-2.0-only"
    homepage = "https://invisible-island.net/mawk/"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("mawk supports Linux and OHOS")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("mawk supports only OHOS armv8")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def _ohos_env_prefix(self):
        if self.settings.os != "OHOS":
            return ""
        tmpdir = os.path.join(self.build_folder, "mawk-tmp")
        os.makedirs(tmpdir, exist_ok=True)
        return f'CC=clang CFLAGS="-DMAWK_OHOS" TMPDIR="{tmpdir}" '

    def _fix_ohos_man_install(self):
        if self.settings.os != "OHOS":
            return
        makefile = os.path.join(self.source_folder, "man", "Makefile")
        with open(makefile, "rb") as makefile_obj:
            data = makefile_obj.read()
        fixed = re.sub(rb"(?m)^INSTALL[^\r\n]*$", b"INSTALL = ../install-sh -c", data)
        if fixed != data:
            with open(makefile, "wb") as makefile_obj:
                makefile_obj.write(fixed)

    def build(self):
        triplets = ""
        if self.settings.os == "OHOS":
            replace_in_file(
                self,
                os.path.join(self.source_folder, "configure"),
                'tmp=`(umask 077 && mktemp -d -q "$TMPDIR/csXXXXXX") 2>/dev/null` &&',
                'tmp="$TMPDIR/cs-fixed"\nrm -rf "$tmp"\n(umask 077 && mkdir "$tmp") &&',
            )
            replace_in_file(
                self,
                os.path.join(self.source_folder, "print.c"),
                "#if (defined(HAVE_ISINF) && defined(HAVE_ISNAN))",
                "#if (defined(HAVE_ISINF) && defined(HAVE_ISNAN)) || defined(MAWK_OHOS)",
                strict=True,
            )
            replace_in_file(
                self,
                os.path.join(self.source_folder, "print.c"),
                "isinf(p->dval) || isnan(p->dval)",
                "__builtin_isinf(p->dval) || __builtin_isnan(p->dval)",
                strict=True,
            )
            replace_in_file(
                self,
                os.path.join(self.source_folder, "print.c"),
                "isinf(cp->dval) || isnan(cp->dval)",
                "__builtin_isinf(cp->dval) || __builtin_isnan(cp->dval)",
                strict=True,
            )
            replace_in_file(
                self,
                os.path.join(self.source_folder, "execute.c"),
                "#if defined(HAVE_ISNAN)",
                "#if defined(HAVE_ISNAN) || defined(MAWK_OHOS)",
                strict=True,
            )
            replace_in_file(
                self,
                os.path.join(self.source_folder, "execute.c"),
                "isnan(cp->dval) || isnan((cp + 1)->dval)",
                "__builtin_isnan(cp->dval) || __builtin_isnan((cp + 1)->dval)",
                strict=True,
            )
            triplets = " --build=aarch64-unknown-linux-gnu --host=aarch64-linux-ohos"
        env_prefix = self._ohos_env_prefix()
        self.run(
            f'{env_prefix}sh ./configure{triplets} --prefix="{self.package_folder}"',
            cwd=self.source_folder,
        )
        self._fix_ohos_man_install()
        self.run(f"{env_prefix}make -j1", cwd=self.source_folder)
        self.run(f"{env_prefix}make check", cwd=self.source_folder)

    def package(self):
        self.run(f"{self._ohos_env_prefix()}make install", cwd=self.source_folder)
        copy(self, "COPYING", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = []
