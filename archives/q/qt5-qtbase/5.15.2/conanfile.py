import os
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
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
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        # Expose zlib paths to Qt5 configure via build env
        # (build() also sets os.environ as fallback)
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

        # Get zlib paths from Conan dependency
        zlib = self.dependencies["zlib"]
        zlib_inc = os.path.join(zlib.package_folder, "include")
        zlib_lib = os.path.join(zlib.package_folder, "lib")

        # Detect pthread_cancel availability (musl doesn't provide it).
        import subprocess
        try:
            subprocess.run(
                f'echo \'#include <pthread.h>\nint main(){{pthread_cancel(0);return 0;}}\' | {os.environ.get("CXX","clang++")} -x c++ - -o /dev/null -lpthread',
                shell=True, check=True, capture_output=True, timeout=10
            )
            has_pthread_cancel = True
        except Exception:
            has_pthread_cancel = False

        if has_pthread_cancel:
            os.environ["CXXFLAGS"] = os.environ.get("CXXFLAGS", "") + " -DHAVE_PTHREAD_CANCEL"

        # Detect the socket length type instead of branching on a platform name.
        try:
            subprocess.run(
                f'echo \'#include <sys/socket.h>\nint main(){{socklen_t n=0; return accept(-1,nullptr,&n);}}\' | {os.environ.get("CXX","clang++")} -x c++ - -o /dev/null',
                shell=True, check=True, capture_output=True, timeout=10
            )
            has_socklen_t = True
        except Exception:
            has_socklen_t = False

        if has_socklen_t:
            os.environ["CXXFLAGS"] = os.environ.get("CXXFLAGS", "") + " -DQT_USE_SOCKLEN_T"

        # Configure Qt5 (with -system-zlib to use Conan-managed zlib)
        os.environ["CFLAGS"] = f"-I{zlib_inc} " + os.environ.get("CFLAGS", "")
        os.environ["CXXFLAGS"] = f"-I{zlib_inc} " + os.environ.get("CXXFLAGS", "")
        os.environ["LDFLAGS"] = f"-L{zlib_lib} " + os.environ.get("LDFLAGS", "")

        self.run(
            f'cd "{src_dir}" && ./configure '
            f'-prefix "{pkg}" '
            f'-opensource -confirm-license '
            f'-no-widgets -no-dbus -no-accessibility '
            f'-opengl es2 -no-xcb -no-eglfs -no-linuxfb '
            f'-no-feature-sql -no-feature-xml '
            f'-nomake tests -nomake examples '
            f'-no-iconv -no-glib -no-icu -no-vulkan '
            f'-no-openssl -no-libproxy -no-system-proxies '
            f'-system-zlib '
            f'-platform linux-clang '
            f'-recheck-all',
        )

        # Build with QMAKE_STRIP="" to prevent stripping (OHOS E215)
        self.run(f'cd "{src_dir}" && make -j4 QMAKE_STRIP=""')

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
        qt5core.requires = ["zlib"]
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
