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
        # Build the extension directly. The CI Python image does not guarantee
        # setuptools, while pyproject.toml would require setuptools.build_meta.
        # Direct compilation keeps the package independent of worker site-packages.
        compiler_executables = self.conf.get(
            "tools.build:compiler_executables", default={}, check_type=dict
        ) or {}
        cxx = compiler_executables.get("cpp") or "clang++"
        import sysconfig

        py_include = sysconfig.get_path("include")
        py_platinclude = sysconfig.get_path("platinclude")
        # OHOS Python can report a stale build-time LIBDIR; libpython is next to
        # the running interpreter under sys.prefix on both device and CI.
        py_lib_dir = os.path.join(sys.prefix, "lib")
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"
        source_files = [
            "aggdraw.cxx",
            "agg2/src/agg_arc.cpp",
            "agg2/src/agg_bezier_arc.cpp",
            "agg2/src/agg_curves.cpp",
            "agg2/src/agg_rounded_rect.cpp",
            "agg2/src/agg_path_storage.cpp",
            "agg2/src/agg_rasterizer_scanline_aa.cpp",
            "agg2/src/agg_trans_affine.cpp",
            "agg2/src/agg_vcgen_contour.cpp",
            "agg2/src/agg_vcgen_stroke.cpp",
        ]
        objects_dir = os.path.join(self.build_folder, "objects")
        staging = os.path.join(self.build_folder, "staging")
        os.makedirs(objects_dir, exist_ok=True)
        os.makedirs(staging, exist_ok=True)
        include_flags = f'-I"{self.source_folder}/agg2/include" -I"{py_include}"'
        if py_platinclude and py_platinclude != py_include:
            include_flags += f' -I"{py_platinclude}"'
        object_files = []
        for source in source_files:
            source_path = os.path.join(self.source_folder, source)
            object_path = os.path.join(objects_dir, os.path.basename(source) + ".o")
            self.run(
                f'"{cxx}" -fPIC -O2 -DVERSION=1.4.1 {include_flags} '
                f'-c "{source_path}" -o "{object_path}"'
            )
            object_files.append(object_path)
        linker = "-fuse-ld=/data/service/hnp/bin/ld " if self.settings.os == "OHOS" else ""
        extension = os.path.join(staging, "aggdraw" + ext_suffix)
        objects = " ".join(f'"{obj}"' for obj in object_files)
        self.run(
            f'"{cxx}" -shared {linker}{objects} '
            f'-L"{py_lib_dir}" -lpython{py_version} -o "{extension}"'
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
            if not os.path.isfile(sign_tool) or not os.path.isfile(objcopy):
                raise ConanInvalidConfiguration(
                    "OHOS signing tools are required for the aggdraw extension"
                )
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
                )
                self.run(
                    f'"{sign_tool}" sign -inFile "{so_file}" -outFile "{tmp_signed}" '
                    f'-selfSign 1',
                )
                if not os.path.isfile(tmp_signed):
                    raise ConanInvalidConfiguration(
                        f"binary-sign-tool did not produce {tmp_signed}"
                    )
                os.replace(tmp_signed, so_file)
                os.chmod(so_file, 0o755)

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = []
        self.runenv_info.append_path("PYTHONPATH", self.package_folder)
