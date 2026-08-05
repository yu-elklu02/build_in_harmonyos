#!/usr/bin/env python3
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import (
    apply_conandata_patches,
    copy,
    export_conandata_patches,
    get,
    patch,
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
        # 0003 是 Fedora/Debian 针 7.3p1 的 openssl-1.1.0 compat vendor patch，
        # 套到 7.5p1 有 hunk 头偏移（上下文行序不同）。conan 的 patch() 即便
        # fuzz=True 也用严格行号校验，拒收；但 git apply --check 在干净 7.5p1
        # 源码树上能过。改用 git apply 走宽松匹配算法。
        for p in self.conan_data.get("patches", []):
            pf = os.path.join(self.source_folder, p["patch_file"])
            self.run(f"git apply --whitespace=nowarn -p1 '{pf}'",
                     cwd=self.source_folder)

    def generate(self):
        tc = AutotoolsToolchain(self)
        zlib_root = self.dependencies["zlib"].package_folder
        openssl_root = self.dependencies["openssl"].package_folder

        # AutotoolsToolchain 在 OHOS 上不自动注入 --build/--host triplet，
        # 上游 config.sub 又不认 HarmonyOS，导致 "cannot guess build type"。
        # 这里显式传 aarch64-linux-ohos（profile 注释确认 get_gnu_triplet
        # 自动将 OHOS 映射为 linux-ohos），并配合 0001-config.sub-ohos.patch。
        tc.configure_args.extend([
            "--build=aarch64-linux-ohos",
            "--host=aarch64-linux-ohos",
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
            # OHOS sysroot ships <shadow.h> with struct spwd but no getspnam
            # declaration or symbol. configure sets HAVE_SHADOW_H=1 from the
            # header, defines.h then #defines USE_SHADOW, and auth.c/auth-shadow.c/
            # xcrypt.c all take the shadow branch and call getspnam — which is
            # undeclared, so clang rejects assigning the implicit int return to
            # struct spwd *. Force the header cache var to no so HAVE_SHADOW_H
            # stays unset, USE_SHADOW is never defined, and the three shadow
            # branches fall through to their pw->pw_passwd fallbacks.
            tc.configure_args.append("ac_cv_header_shadow_h=no")
            tc.extra_cflags.append("-D_GNU_SOURCE")
            tc.extra_cflags.append("-D__USE_GNU")

        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        autotools.make()
        # 上游 `make tests` 编译阶段在真机已通过（accessor backport +
        # banana typo patch + -j1 避竞态），但运行阶段卡在 test_sshbuf
        # 的 tmpfile() 调用：真机 /tmp 是只读文件系统，OHOS libc 的
        # tmpfile() 不读 TMPDIR 只硬走 P_tmpdir="/tmp"，故返回 NULL，
        # 触发 ASSERT_PTR_NE(out, NULL) core dump。
        # 这是真机环境 + OHOS libc 的运行时缺陷，非配方或源码问题。
        # 不在 build() 跑 make tests，靠 test_package 的 SSH1 功能断言
        # （ssh -1 -G localhost、ssh-keygen -t rsa1）验证实际功能。

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
