#!/usr/bin/env python3
"""Conan recipe — egl 1.0.5 (Norbert Nopper EGL desktop implementation)

OHOS 适配要点:
- 仅接受 OHOS 平台(上游不支持 OHOS,需补丁新增 OHOS 后端)
- 上游 CMakeLists.txt 通过补丁新增 CMAKE_SYSTEM_NAME STREQUAL "OHOS" 分支,
  选择新 src/egl_ohos.cpp(转发系统 libEGL.so),链接 CMAKE_DL_LIBS,跳过 examples
- 静态构建 libEGL.a,打包 include/EGL + include/KHR
- OHOS 后端不引入 X11/Wayland/Vulkan;pbuffer + OpenGL ES context 真实可用
"""
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import get, apply_conandata_patches, export_conandata_patches
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout


class EglConan(ConanFile):
    name = "egl"
    version = "1.0.5"
    description = "Khronos EGL 1.5 desktop implementation with OHOS system EGL forwarding backend"
    license = "MIT"
    homepage = "https://github.com/McNopper/EGL"
    url = ""

    package_type = "library"

    settings = "os", "arch", "compiler", "build_type"
    # R26: EGL 与系统同名库(/system/lib64/libEGL.so)同名 → 强制静态,避免 .so 污染 /lib、/lib64
    options = {"shared": [True, False]}
    default_options = {"shared": False}

    def export_sources(self):
        export_conandata_patches(self)

    def configure(self):
        # 仅接受 OHOS:上游原生后端是 WGL/GLX/Wayland,均不适用于 OHOS。
        # OHOS 通过补丁新增 egl_ohos.cpp 后端(转发系统 libEGL.so),其他平台不予拒绝。
        if self.settings.os != "OHOS":
            raise ConanInvalidConfiguration(
                "egl/1.0.5 仅支持 OHOS 平台(OHOS 后端经 dlopen 转发系统 libEGL.so)。"
                "其他平台请使用上游原生 WGL/GLX/Wayland 后端。")
        if self.options.shared:
            raise ConanInvalidConfiguration(
                "egl/1.0.5 与系统同名库 /system/lib64/libEGL.so 同名,必须静态构建(R26)。")

    def layout(self):
        cmake_layout(self, src_folder=".")

    def source(self):
        # codeload.github.com 的 tar.gz URL stem 是 ".../tar.gz/refs/tags/v1.0.5",
        # conan get() 按 basename 推断下载文件名 → 得到无扩展名的 "v1.0.5" →
        # unzip() 误判为 zip 报 BadZipFile。显式传 filename 让 conan 按 .tar.gz 解。
        get(self, **self.conan_data["sources"], strip_root=True,
            filename="egl-1.0.5.tar.gz")

    def generate(self):
        tc = CMakeToolchain(self)
        # R26: 系统同名库强制静态
        tc.variables["BUILD_SHARED_LIBS"] = "OFF"
        # 上游 CMake 默认靠 WIN32/UNIX 识别平台;OHOS 由补丁新增 CMAKE_SYSTEM_NAME STREQUAL "OHOS" 分支
        # CMakeToolchain 已通过 profile 注入 CMAKE_SYSTEM_NAME=OHOS,无需额外变量
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        # 上游 examples 众多且依赖窗口系统;补丁已在 CMake 跳过 add_subdirectory(examples),
        # 上游无 ctest 测试目标 → 不调用 cmake.test()(build_and_test.sh L2 会在 test_package �段真机验证)

    def package(self):
        cmake = CMake(self)
        cmake.install()
        # 上游 CMake 无 install() 规则: libEGL.a 产出到 ${CMAKE_SOURCE_DIR}/lib,
        # 公开头在 include/EGL + include/KHR。cmake --install 啥都不装 →
        # 显式把构建树残留产物 copy 到 package_folder 的标准位置(staging 隔离)。
        # conan CMake 把源码副本放 self.source_folder,add_library 的
        # ARCHIVE_OUTPUT_DIRECTORY=${CMAKE_SOURCE_DIR}/lib 即 <source_folder>/lib。
        from conan.tools.files import copy
        import os
        # 静态库 → <pkg>/lib/libEGL.a
        copy(self, "libEGL.a", dst=os.path.join(self.package_folder, "lib"),
             src=os.path.join(self.source_folder, "lib"))
        # 公开头 → <pkg>/include/EGL 与 <pkg>/include/KHR
        for sub in ("EGL", "KHR"):
            copy(self, "*.h", dst=os.path.join(self.package_folder, "include", sub),
                 src=os.path.join(self.source_folder, "include", sub))

    def package_info(self):
        self.cpp_info.libs = ["EGL"]
        # include/EGL 与 include/KHR 都是公开头目录(KHR/khrplatform.h 被 EGL/egl.h include)
        self.cpp_info.includedirs = ["include", "include/EGL", "include/KHR"]
        self.cpp_info.set_property("cmake_file_name", "EGL")
        self.cpp_info.set_property("cmake_target_name", "EGL::EGL")
        # 链接期需要 libdl(egl_ohos.cpp dlopen 转发系统 EGL);OHOS bionic 提供 dl
        if self.settings.os in ("Linux", "OHOS"):
            self.cpp_info.system_libs = ["dl"]
