import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
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

    def requirements(self):
        # R27/R18: zlib as Conan dependency, not inline build
        self.requires("zlib/1.3.1")

    def validate(self):
        # R32: settings.os check must use in ("Linux", "OHOS")
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration(
                f"qt5-qtbase only supports Linux and OHOS, got {self.settings.os}"
            )

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        # Expose zlib paths to Qt5 configure via env vars
        zlib = self.dependencies["zlib"]
        zlib_inc = os.path.join(zlib.package_folder, "include")
        zlib_lib = os.path.join(zlib.package_folder, "lib")
        self.runenv_info.append("CFLAGS", f"-I{zlib_inc}")
        self.runenv_info.append("CXXFLAGS", f"-I{zlib_inc}")
        self.runenv_info.append("LDFLAGS", f"-L{zlib_lib}")

    def build(self):
        apply_conandata_patches(self)
        src_dir = self.source_folder
        pkg = self.package_folder

        # Get zlib paths from Conan dependency
        zlib = self.dependencies["zlib"]
        zlib_inc = os.path.join(zlib.package_folder, "include")
        zlib_lib = os.path.join(zlib.package_folder, "lib")

        # Configure Qt5 (with -system-zlib to use Conan-managed zlib)
        env = os.environ.copy()
        env["CFLAGS"] = f"-I{zlib_inc} " + env.get("CFLAGS", "")
        env["CXXFLAGS"] = f"-I{zlib_inc} " + env.get("CXXFLAGS", "")
        env["LDFLAGS"] = f"-L{zlib_lib} " + env.get("LDFLAGS", "")

        self.run(
            f'cd "{src_dir}" && ./configure '
            f'-prefix "{pkg}" '
            f'-opensource -confirm-license '
            f'-no-gui -no-widgets -no-dbus -no-opengl -no-accessibility '
            f'-no-feature-sql -no-feature-xml '
            f'-nomake tests -nomake examples '
            f'-no-iconv -no-glib -no-icu -no-opengl -no-vulkan '
            f'-no-openssl -no-libproxy -no-system-proxies '
            f'-system-zlib '
            f'-platform linux-clang '
            f'-recheck-all',
            env=env,
        )

        # Build with QMAKE_STRIP="" to prevent stripping (OHOS E215)
        self.run(f'cd "{src_dir}" && make -j1 QMAKE_STRIP=""', env=env)

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
        # zlib is a separate Conan dependency, not bundled
        self.cpp_info.libs = ["Qt5Core", "Qt5Network", "Qt5Test"]
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]
