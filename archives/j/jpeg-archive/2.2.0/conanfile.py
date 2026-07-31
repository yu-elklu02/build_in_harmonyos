"""Conan recipe for jpeg-archive 2.2.0.

jpeg-archive provides utilities for archiving JPEGs for long-term storage:
  jpeg-recompress  — re-encode JPEG to smallest size preserving visual quality
  jpeg-compare     — compare two JPEGs for visual similarity (SSIM/MS-SSIM)
  jpeg-hash        — pixel-data-based hash (stable across re-encodes)
  jpeg-archive     — batch parallel re-compression wrapper

Build system: CMake
Dependencies: mozjpeg (libjpeg API), libpng (PNG input support)
Upstream: https://github.com/danielgtaylor/jpeg-archive
License: MIT
"""
import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get


class JpegArchiveConan(ConanFile):
    name = "jpeg-archive"
    version = "2.2.0"
    package_type = "application"
    description = (
        "Utilities for archiving JPEGs for long-term storage: "
        "jpeg-recompress, jpeg-compare, jpeg-hash, jpeg-archive"
    )
    license = "MIT"
    homepage = "https://github.com/danielgtaylor/jpeg-archive"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    topics = ("jpeg", "image", "compression", "archive", "cli")

    settings = "os", "arch", "compiler", "build_type"

    def export_sources(self):
        export_conandata_patches(self)

    def validate(self):
        # R32: check os in ("Linux", "OHOS"), not == "Linux"
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration(
                f"jpeg-archive is only supported on Linux/OHOS, got {self.settings.os}"
            )
        if self.settings.arch != "armv8":
            raise ConanInvalidConfiguration(
                f"jpeg-archive/2.2.0 is adapted and validated for armv8 (aarch64) only, "
                f"got {self.settings.arch}"
            )

    def requirements(self):
        # mozjpeg provides libjpeg.a (libjpeg-compatible API)
        self.requires("mozjpeg/4.1.1")
        # libpng for PNG→JPEG input support
        self.requires("libpng/1.6.58")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        apply_conandata_patches(self)

    def generate(self):
        CMakeDeps(self).generate()
        tc = CMakeToolchain(self)

        # Compatibility with older cmake_minimum_required in upstream
        tc.variables["CMAKE_POLICY_VERSION_MINIMUM"] = "3.5"

        # CMake's FindJPEG looks for JPEG_LIBRARY / JPEG_INCLUDE_DIR.
        # mozjpeg in Conan is named "mozjpeg", not "JPEG", so we point
        # FindJPEG to mozjpeg's package folder manually.
        mozjpeg_dep = self.dependencies["mozjpeg"]
        moz_dir = mozjpeg_dep.package_folder.replace("\\", "/")
        tc.variables["JPEG_LIBRARY"] = f"{moz_dir}/lib/libjpeg.a"
        tc.variables["JPEG_INCLUDE_DIR"] = f"{moz_dir}/include"

        # CMake's FindPNG: point to Conan libpng package
        libpng_dep = self.dependencies["libpng"]
        png_dir = libpng_dep.package_folder.replace("\\", "/")
        tc.variables["PNG_LIBRARY"] = f"{png_dir}/lib/libpng.a"
        tc.variables["PNG_PNG_INCLUDE_PATH"] = f"{png_dir}/include"
        tc.variables["PNG_INCLUDE_DIRS"] = f"{png_dir}/include"

        # zlib is a transitive dep (via libpng); Conan 2 exposes all resolved
        # deps in self.dependencies, so access it directly
        zlib_dep = self.dependencies["zlib"]
        zlib_dir = zlib_dep.package_folder.replace("\\", "/")
        tc.variables["ZLIB_LIBRARY"] = f"{zlib_dir}/lib/libz.a"
        tc.variables["ZLIB_INCLUDE_DIR"] = f"{zlib_dir}/include"

        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(
            variables={
                "CMAKE_POLICY_VERSION_MINIMUM": "3.5",
            }
        )
        cmake.build()

    def package(self):
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        # jpeg-archive is a pure CLI tool set — no library to link against
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libs = []
        self.cpp_info.includedirs = []
