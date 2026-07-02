import os
from conan import ConanFile
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout


class Qt5QtbaseConan(ConanFile):
    name = "qt5-qtbase"
    version = "5.15.2"
    description = "Qt5 Base module (with Qt5Test + abstract socket patch + no strip)"
    license = "LGPL-3.0"
    homepage = "https://www.qt.io/"
    url = ""

    settings = "os", "compiler", "build_type", "arch"
    package_type = "shared-library"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self)

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration(
                f"qt5-qtbase only supports Linux and OHOS, got {self.settings.os}"
            )

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        src_dir = self.source_folder

        # Configure Qt5 (without -no-feature-testlib to enable Qt5Test)
        self.run(f'cd "{src_dir}" && ./configure '
                 f'-prefix $PREFIX '
                 f'-opensource -confirm-license '
                 f'-no-gui -no-widgets -no-dbus -no-opengl -no-accessibility '
                 f'-no-feature-sql -no-feature-xml '
                 f'-nomake tests -nomake examples '
                 f'-no-iconv -no-glib -no-icu -no-opengl -no-vulkan '
                 f'-no-openssl -no-libproxy -no-system-proxies '
                 f'-platform linux-clang '
                 f'-recheck-all')

        # Build with QMAKE_STRIP="" to prevent stripping (OHOS E215)
        self.run(f'cd "{src_dir}" && make -j1 QMAKE_STRIP=""')

        # Build libz.so (libQt5Core dependency, not available on OHOS)
        zlib_url = "https://zlib.net/zlib-1.2.13.tar.gz"
        get(self, zlib_url, destination=os.path.join(src_dir, "zlib-src"), strip_root=True)
        self.run(f'cd "{src_dir}/zlib-src" && '
                 f'clang -shared -fPIC -Wl,-soname,libz.so '
                 f'-o "{src_dir}/lib/libz.so" '
                 f'adler32.c compress.c crc32.c deflate.c '
                 f'gzclose.c gzlib.c gzread.c gzwrite.c '
                 f'infback.c inffast.c inflate.c inftrees.c '
                 f'trees.c uncompr.c zutil.c')

    def package(self):
        src_dir = self.source_folder
        lib_dir = os.path.join(src_dir, "lib")
        include_dir = os.path.join(src_dir, "include")
        mkspecs_dir = os.path.join(src_dir, "mkspecs")
        bin_dir = os.path.join(src_dir, "bin")

        # Copy libraries (unstripped)
        copy(self, "*.so*", src=lib_dir,
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.prl", src=lib_dir,
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.la", src=lib_dir,
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)
        copy(self, "*.pc", src=lib_dir,
             dst=os.path.join(self.package_folder, "lib"), keep_path=False)

        # Copy headers
        if os.path.isdir(include_dir):
            copy(self, "*", src=include_dir,
                 dst=os.path.join(self.package_folder, "include"), keep_path=False)

        # Copy mkspecs
        if os.path.isdir(mkspecs_dir):
            copy(self, "*", src=mkspecs_dir,
                 dst=os.path.join(self.package_folder, "mkspecs"), keep_path=False)

        # Copy bin tools
        if os.path.isdir(bin_dir):
            copy(self, "*", src=bin_dir,
                 dst=os.path.join(self.package_folder, "bin"), keep_path=False)

        # Copy cmake configs
        cmake_dir = os.path.join(lib_dir, "cmake")
        if os.path.isdir(cmake_dir):
            copy(self, "*", src=cmake_dir,
                 dst=os.path.join(self.package_folder, "lib", "cmake"), keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["Qt5Core", "Qt5Network", "Qt5Test", "z"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]
