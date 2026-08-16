import os
import shlex

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.files import copy, get, replace_in_file
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class RemindConan(ConanFile):
    name = "remind"
    version = "06.02.08"
    description = "Sophisticated calendar and alarm program"
    homepage = "https://dianne.skoll.ca/projects/remind/"
    license = "GPL-2.0-only"
    package_type = "application"
    settings = "os", "compiler", "build_type", "arch"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("remind supports Linux and OHOS only")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-perl-build-artifacts")
        if self.settings.os == "OHOS":
            tc.configure_args.extend([
                "--build=aarch64-linux-ohos",
                "--host=aarch64-linux-ohos",
                "ac_cv_lib_readline_readline=no",
                "ac_cv_func_readline=no",
            ])
        tc.generate()

    def build(self):
        if self.settings.os == "OHOS":
            self._patch_ohos_shells()
            self._patch_ohos_configure()
            self._prepare_out_of_source_configure_inputs()
        autotools = Autotools(self)
        autotools.configure()
        src_build_dir = os.path.join(self.build_folder, "src")
        tests_dir = os.path.join(self.source_folder, "tests")
        shell = "/system/bin/sh" if self.settings.os == "OHOS" else "sh"
        self.run("make -C {} -j1".format(shlex.quote(src_build_dir)), env="conanbuild")
        check_env = (
            "REMIND_CMD={} REM2PS={} ".format(
                shlex.quote(os.path.join(src_build_dir, "remind")),
                shlex.quote(os.path.join(src_build_dir, "rem2ps")),
            )
        )
        basic_rc = self.run(
            "{} {} {}".format(check_env, shell, shlex.quote(os.path.join(tests_dir, "test-rem"))),
            env="conanbuild",
            ignore_errors=True,
        )
        tz_rc = self.run(
            "{} {} {}".format(check_env, shell, shlex.quote(os.path.join(tests_dir, "test-timezone-support"))),
            env="conanbuild",
            ignore_errors=True,
        )
        if basic_rc != 0 or tz_rc != 0:
            self._report_test_outputs()
            raise ConanException("remind upstream make test failed")

    def _patch_ohos_shells(self):
        for path in (
            os.path.join(self.source_folder, "tests", "test-rem"),
            os.path.join(self.source_folder, "tests", "test-timezone-support"),
        ):
            if os.path.isfile(path):
                replace_in_file(self, path, "#!/bin/sh", "#!/system/bin/sh")
        makefile_in = os.path.join(self.source_folder, "src", "Makefile.in")
        if os.path.isfile(makefile_in):
            replace_in_file(self, makefile_in, "SHELL= /bin/sh", "SHELL= /system/bin/sh")

    def _patch_ohos_configure(self):
        configure = os.path.join(self.source_folder, "configure")
        if not os.path.isfile(configure):
            return
        # Autoconf's config.status helper creates ./confXXXXXX with umask 077.
        # On the OHOS Conan sandbox this private 0700 directory can become
        # inaccessible to the subprocess that writes subs1.awk.  Keep the temp
        # directory local to the build tree, but avoid the private umask.
        replace_in_file(self, configure, "umask 077 && mktemp", "umask 002 && mktemp")
        replace_in_file(self, configure, "umask 077 && mkdir", "umask 002 && mkdir")

    def _prepare_out_of_source_configure_inputs(self):
        docs_dir = os.path.join(self.build_folder, "docs")
        os.makedirs(docs_dir, exist_ok=True)
        copy(self, "WHATSNEW", src=os.path.join(self.source_folder, "docs"), dst=docs_dir)

    def _report_test_outputs(self):
        for name in ("test.out", "tz.out"):
            path = os.path.join(self.source_folder, "tests", name)
            if not os.path.isfile(path):
                continue
            self.output.error("===== remind {} tail =====".format(name))
            with open(path, encoding="utf-8", errors="replace") as handle:
                lines = [line.rstrip() for line in handle.readlines()]
            for line in lines[-120:]:
                self.output.error(line)

    def package(self):
        self.run(
            "make -C {} install DESTDIR={}".format(
                shlex.quote(os.path.join(self.build_folder, "src")),
                shlex.quote(self.package_folder),
            ),
            env="conanbuild",
        )
        copy(self, "COPYRIGHT", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        for name in ("remind", "rem2ps", "tkremind", "rem2html"):
            path = os.path.join(self.package_folder, "bin", name)
            if os.path.isfile(path):
                os.chmod(path, 0o755)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.libs = []
        self.cpp_info.bindirs = ["bin"]
        self.runenv_info.define_path("PATH", os.path.join(self.package_folder, "bin"))
