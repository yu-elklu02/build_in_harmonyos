"""Conan recipe for aggdraw 1.4.1, a CPython C++ drawing extension."""
import os
import sys

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class AggdrawConan(ConanFile):
    name = "aggdraw"
    version = "1.4.1"
    package_type = "application"
    description = "High-quality drawing interface for PIL"
    license = "Python (MIT style)"
    homepage = "https://github.com/pytroll/aggdraw"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    topics = ("python", "graphics", "drawing", "cxx-extension")

    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration(
                f"aggdraw is adapted for Linux/OHOS, got {self.settings.os}"
            )
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration(
                f"aggdraw/1.4.1 is validated for OHOS armv8, got {self.settings.arch}"
            )

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def build(self):
        # The target Python on the HarmonyOS PC device builds this CPython C++
        # extension in place.  Disable build isolation and dependency resolution
        # so Conan never downloads undeclared build dependencies.
        #
        # HarmonyOS python_3.12 hardcodes CXX="c++" into sysconfig at its own
        # build time; setuptools build_ext reads sysconfig.get_config_var('CXX')
        # → "c++" but the device only ships clang/clang++ in PATH, so the wheel
        # build dies "command 'c++' failed: No such file or directory".  Override
        # CXX via env so setuptools picks clang++ instead.  LDSHARED is likewise
        # hardcoded to "cc -shared ..."; the same env override switches the
        # linker to clang so the .so is produced.
        staging = os.path.join(self.build_folder, "staging")
        # conan self.run's `env` only accepts predefined scope names, not dict
        # overrides, so inline CXX/LDSHARED/LDFLAGS via the `env` command prefix.
        #
        # HarmonyOS python_3.12 statically links libpython into the python3.12
        # main binary and does NOT export Python C-API symbols (PyModule_Create2,
        # etc.) to extensions at runtime — aggdraw.cpython-312.so's NEEDED is
        # only libc++_shared/libc, so `import aggdraw` dies
        # "PyModule_Create2: symbol not found".  Link aggdraw.so against the
        # shipped libpython3.12.so (which DOES export PyModule_Create2) by
        # appending -L<lib> -lpython3.12 to LDSHARED + LDFLAGS so the .so picks
        # up the Python C-API symbols at link time.
        # Resolve the libpython3.12.so directory from the running Python's own
        # install layout, NOT a hardcoded /data/service/hnp/lib. sys.prefix is
        # the Python installation root (e.g. .../python_3.12) and libpython
        # ships at <prefix>/lib/libpython3.12.so on both the HarmonyOS PC device
        # and the CI SDK layout. sysconfig.get_config_var('LIBDIR') is wrong
        # here (returns "/python3/lib", a relic of the python.org build's DESTDIR
        # staging), so derive from sys.prefix instead. This is the same path
        # the running sys.executable lives under, so it tracks whichever Python
        # Conan invokes — device or CI — without a hardcoded absolute.
        py_lib_dir = os.path.join(sys.prefix, "lib")
        # CI's SDK lld loads an incompatible libxml2.so.16. The HNP linker is
        # the repository-standard fallback for native OHOS C/C++ links.
        linker = ""
        if self.settings.os == "OHOS":
            linker = "-fuse-ld=/data/service/hnp/bin/ld "
        self.run(
            f'env CXX=clang++ '
            f'LDSHARED="clang++ -shared {linker}-L{py_lib_dir} -lpython3.12" '
            f'LDFLAGS="{linker}-L{py_lib_dir} -lpython3.12" '
            f'"{sys.executable}" -m pip install . --target "{staging}" '
            "--no-build-isolation --no-deps",
            cwd=self.source_folder,
        )

    def package(self):
        staging = os.path.join(self.build_folder, "staging")
        copy(self, "*", src=staging, dst=self.package_folder, keep_path=True)
        copy(
            self,
            "LICENSE.txt",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        # HarmonyOS MAC (hmmac=use_task) rejects exec of unsigned ELF loaded
        # from the conan cache p/ folder → test_package's `import aggdraw` dies
        # "Error loading shared library aggdraw.cpython-312.so: Permission
        # denied". Re-sign the packaged .so in place: llvm-objcopy strips any
        # stale .codesign section (tolerate "section not found" on first-sign),
        # binary-sign-tool sign -selfSign 1 emits a signed copy, os.replace
        # swaps it in, chmod 0o755 keeps it other-readable+executable. Same
        # pattern as the daemon/ent/zig/ispell recipes in this repo. Missing
        # tool or failed sign must fail the build — test_package exec depends
        # on the signature; do not silently skip.
        if self.settings.os == "OHOS":
            sign_tool = "/data/service/hnp/bin/binary-sign-tool"
            objcopy = "/data/service/hnp/bin/llvm-objcopy"
            # Wheel build tags the .so with the platform ABI
            # (aggdraw.cpython-312-aarch64-linux-ohos.so on CI,
            # aggdraw.cpython-312.so on device); glob-match every aggdraw*.so
            # in the package folder so the re-sign hits whichever file the
            # build actually produced. A missed match silently skips the
            # signature → MAC rejects exec in test_package.
            import glob as _glob
            so_pattern = os.path.join(self.package_folder, "aggdraw*.so")
            extension_modules = _glob.glob(so_pattern)
            if not extension_modules:
                raise ConanInvalidConfiguration(
                    "aggdraw extension module was not packaged; cannot sign it for OHOS"
                )
            for so_file in extension_modules:
                if not os.path.isfile(so_file):
                    continue
                tmp_signed = so_file + ".signed"
                self.run(
                    f'"{objcopy}" --remove-section .codesign "{so_file}" 2>/dev/null || true',
                    quiet=True,
                )
                self.run(
                    f'"{sign_tool}" sign -inFile "{so_file}" -outFile "{tmp_signed}" '
                    f'-selfSign 1',
                    quiet=True,
                )
                os.replace(tmp_signed, so_file)
                os.chmod(so_file, 0o755)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)
