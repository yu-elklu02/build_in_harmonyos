#!/usr/bin/env python3
"""Conan test_package for egl 1.0.5 — Conan L1 official test.

R34: test_package test() must really exercise the EGL lifecycle
(eglInitialize → eglBindAPI(ES) → choose config → create 16×16 pbuffer →
ES2 context → eglMakeCurrent → eglGetProcAddress → release/destroy).
Uses CMake (CMakeDeps + CMakeToolchain) so the compiler is handled by Conan
toolchain, not raw shell env vars (R33).
"""
import os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout


class EglTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "CMakeDeps", "CMakeToolchain"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        # OHOS /bin/sh (mksh) cannot exec ELF binaries → wrap with bash (R5).
        bash = os.environ.get("CONFIG_SHELL", "/data/service/hnp/bin/bash")
        test_bin = os.path.join(self.build_folder, "test_egl")
        self.run(f"{bash} -c '{test_bin}'", env="conanrun")
