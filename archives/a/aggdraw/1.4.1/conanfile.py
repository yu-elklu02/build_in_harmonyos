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
        py_lib_dir = os.path.join(os.path.dirname(sys.executable), "..", "lib")
        py_lib_dir = os.path.abspath(py_lib_dir)
        self.run(
            f'env CXX=clang++ '
            f'LDSHARED="clang++ -shared -L{py_lib_dir} -lpython3.12" '
            f'LDFLAGS="-L{py_lib_dir} -lpython3.12" '
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

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)
