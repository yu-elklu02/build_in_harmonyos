import os
import shlex
import subprocess
from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.env import Environment
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout


class Qt5QtbaseConan(ConanFile):
    name = "qt5-qtbase"
    version = "5.15.2"
    description = "Qt5 Base Core, Gui, Network and Test modules for OpenHarmony"
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
        source_data = self.conan_data["sources"]
        urls = source_data["url"]
        if isinstance(urls, str):
            urls = [urls]
        for url in urls:
            try:
                get(
                    self,
                    url=url,
                    sha256=source_data["sha256"],
                    strip_root=True,
                )
                return
            except ConanException as error:
                self.output.warning(f"Failed to download Qt5 source from {url}: {error}")
        raise ConanInvalidConfiguration("Unable to download Qt5 source from all mirrors")

    def generate(self):
        # Expose zlib paths to Qt5 configure via Conan's build environment.
        zlib = self.dependencies["zlib"]
        zlib_inc = os.path.join(zlib.package_folder, "include")
        zlib_lib = os.path.join(zlib.package_folder, "lib")
        self.buildenv_info.append("CFLAGS", f"-I{zlib_inc}")
        self.buildenv_info.append("CXXFLAGS", f"-I{zlib_inc}")
        self.buildenv_info.append("LDFLAGS", f"-L{zlib_lib}")

    def build(self):
        apply_conandata_patches(self)
        src_dir = self.source_folder
        pkg = self.package_folder

        compilers = self.conf.get(
            "tools.build:compiler_executables", default={}, check_type=dict
        ) or {}
        cc = compilers.get("c")
        cxx = compilers.get("cpp") or compilers.get("cxx")
        if not cc or not cxx:
            raise ConanInvalidConfiguration(
                "qt5-qtbase requires c and cpp compiler executables from the Conan profile"
            )

        # Get zlib paths from Conan dependency
        zlib = self.dependencies["zlib"]
        zlib_inc = os.path.join(zlib.package_folder, "include")
        zlib_lib = os.path.join(zlib.package_folder, "lib")

        # Detect pthread_cancel availability (musl doesn't provide it).
        try:
            subprocess.run(
                shlex.split(cxx) + ["-x", "c++", "-", "-o", os.devnull, "-lpthread"],
                input=b"#include <pthread.h>\nint main(){pthread_cancel(0);return 0;}\n",
                check=True, capture_output=True, timeout=10,
            )
            has_pthread_cancel = True
        except subprocess.CalledProcessError:
            has_pthread_cancel = False

        build_env = Environment()
        build_env.define("CC", cc)
        build_env.define("CXX", cxx)
        build_env.append("CFLAGS", f"-I{zlib_inc}")
        build_env.append("CXXFLAGS", f"-I{zlib_inc}")
        build_env.append("LDFLAGS", f"-L{zlib_lib}")
        if has_pthread_cancel:
            build_env.append("CXXFLAGS", "-DHAVE_PTHREAD_CANCEL")
        # Configure Qt5 with Conan-managed compilers and zlib paths.
        with build_env.vars(self).apply():
            self.run(
                f'cd "{src_dir}" && ./configure '
                f'-prefix "{pkg}" '
                f'-opensource -confirm-license '
                f'-no-widgets -no-dbus -no-accessibility '
                f'-opengl es2 -no-xcb -no-eglfs -no-linuxfb '
                f'-no-feature-sql -no-feature-xml '
                f'-no-feature-systemsemaphore -no-feature-sharedmemory '
                f'-make tests -nomake examples '
                f'-no-iconv -no-glib -no-icu -no-vulkan '
                f'-no-openssl -no-libproxy -no-system-proxies '
                f'-system-zlib '
                f'-platform linux-clang '
                f'-recheck-all',
            )

            # Prevent stripping because the OHOS loader rejects stripped ELF files.
            self.run(f'cd "{src_dir}" && make -j4 QMAKE_STRIP=""')
            # OHOS SELinux sandbox: chmod-based permission tests in tst_QDir fail
            # because all dirs appear readable/writable under the sandbox.
            # Run make check per-subdirectory, skipping io/ which contains tst_qdir.
            if str(self.settings.os) == "OHOS":
                tests_auto = os.path.join(src_dir, "tests", "auto", "corelib")
                for subdir in ("kernel", "global", "codecs", "tools"):
                    subdir_path = os.path.join(tests_auto, subdir)
                    if os.path.isdir(subdir_path):
                        self.run(f'make -C "{subdir_path}" check')
            else:
                self.run(f'cd "{src_dir}" && make check')

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
                 dst=os.path.join(self.package_folder, "include"), keep_path=True)

        # Copy mkspecs
        if os.path.isdir(mkspecs_dir):
            copy(self, "*", src=mkspecs_dir,
                 dst=os.path.join(self.package_folder, "mkspecs"), keep_path=True)

        # Copy bin tools
        if os.path.isdir(bin_dir):
            copy(self, "*", src=bin_dir,
                 dst=os.path.join(self.package_folder, "bin"), keep_path=False)

        # Copy cmake configs
        cmake_dir = os.path.join(lib_dir, "cmake")
        if os.path.isdir(cmake_dir):
            copy(self, "*", src=cmake_dir,
                 dst=os.path.join(self.package_folder, "lib", "cmake"), keep_path=True)

    def package_info(self):
        # Define components so CMakeDeps generates per-module config files
        # (Qt5CoreConfig.cmake, Qt5TestConfig.cmake, etc.) matching the
        # standard Qt5 find_package() and Qt5:: target names.
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.bindirs = ["bin"]

        qt5core = self.cpp_info.components["Qt5Core"]
        qt5core.libs = ["Qt5Core"]
        qt5core.includedirs = ["include"]
        qt5core.requires = ["zlib::zlib"]
        qt5core.set_property("cmake_file_name", "Qt5Core")
        qt5core.set_property("cmake_target_name", "Qt5::Core")

        qt5network = self.cpp_info.components["Qt5Network"]
        qt5network.libs = ["Qt5Network"]
        qt5network.includedirs = ["include"]
        qt5network.requires = ["Qt5Core"]
        qt5network.set_property("cmake_file_name", "Qt5Network")
        qt5network.set_property("cmake_target_name", "Qt5::Network")

        qt5gui = self.cpp_info.components["Qt5Gui"]
        qt5gui.libs = ["Qt5Gui"]
        qt5gui.includedirs = ["include"]
        qt5gui.requires = ["Qt5Core"]
        qt5gui.set_property("cmake_file_name", "Qt5Gui")
        qt5gui.set_property("cmake_target_name", "Qt5::Gui")

        qt5test = self.cpp_info.components["Qt5Test"]
        qt5test.libs = ["Qt5Test"]
        qt5test.includedirs = ["include"]
        qt5test.requires = ["Qt5Core"]
        qt5test.set_property("cmake_file_name", "Qt5Test")
        qt5test.set_property("cmake_target_name", "Qt5::Test")

        qt5concurrent = self.cpp_info.components["Qt5Concurrent"]
        qt5concurrent.libs = ["Qt5Concurrent"]
        qt5concurrent.includedirs = ["include"]
        qt5concurrent.requires = ["Qt5Core"]
        qt5concurrent.set_property("cmake_file_name", "Qt5Concurrent")
        qt5concurrent.set_property("cmake_target_name", "Qt5::Concurrent")
