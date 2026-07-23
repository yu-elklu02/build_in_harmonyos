import os
import re
import shlex
import shutil
import subprocess
from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.env import Environment
from conan.tools.files import get, copy, apply_conandata_patches, export_conandata_patches
from conan.tools.layout import basic_layout

_OHOS_SKIPPED_CORELIB_TESTS = {
    # OHOS SELinux sandbox does not implement POSIX permission semantics used
    # by these filesystem, temporary-file, plugin, and model test suites.
    "itemmodels", "plugin", "io/qdir", "io/qfile", "io/qfileselector",
    "io/qlockfile", "io/qsavefile", "io/qsettings", "io/qstandardpaths",
    "io/qtemporarydir", "io/qtemporaryfile",
    # OHOS ships different timezone data for these QDate expectations.
    "time",
}


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
        except (subprocess.CalledProcessError, FileNotFoundError,
                subprocess.TimeoutExpired, OSError):
            self.output.warning(
                "pthread_cancel detection failed; disabling HAVE_PTHREAD_CANCEL"
            )
            has_pthread_cancel = False

        build_env = Environment()
        build_env.define("CC", cc)
        build_env.define("CXX", cxx)
        build_env.append("CFLAGS", f"-I{zlib_inc}")
        build_env.append("CXXFLAGS", f"-I{zlib_inc}")
        build_env.append("LDFLAGS", f"-L{zlib_lib}")
        symlink_shim_dir = self._create_symlink_shim()
        build_env.prepend_path("PATH", symlink_shim_dir)
        if has_pthread_cancel:
            build_env.append("CXXFLAGS", "-DHAVE_PTHREAD_CANCEL")
        # Configure Qt5 with Conan-managed compilers and zlib paths.
        with build_env.vars(self).apply():
            configure_shell = os.environ.get("CONFIG_SHELL") or shutil.which("sh")
            if not configure_shell:
                raise ConanInvalidConfiguration("A POSIX shell is required to run Qt configure")
            self.run(
                f'cd "{src_dir}" && {shlex.quote(configure_shell)} ./configure '
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
            # Qt 5.15's runner cannot filter individual functions with -skip.
            # Run every compatible CoreLib suite and exclude only the known
            # SELinux/timezone-incompatible suites declared above.
            if self.settings.os == "OHOS":
                corelib_dir = os.path.join(src_dir, "tests", "auto", "corelib")
                for suite in sorted(os.listdir(corelib_dir)):
                    suite_dir = os.path.join(corelib_dir, suite)
                    if not os.path.isdir(suite_dir):
                        continue
                    if suite != "io":
                        if (suite not in _OHOS_SKIPPED_CORELIB_TESTS and
                                self._has_make_check_target(suite_dir)):
                            self.run(f'make -C "{suite_dir}" check')
                        continue
                    for io_test in sorted(os.listdir(suite_dir)):
                        test_dir = os.path.join(suite_dir, io_test)
                        test_name = f"io/{io_test}"
                        if (test_name not in _OHOS_SKIPPED_CORELIB_TESTS and
                                os.path.isdir(test_dir) and
                                self._has_make_check_target(test_dir)):
                            self.run(f'make -C "{test_dir}" check')
            else:
                self.run(f'cd "{src_dir}" && make check')

    @staticmethod
    def _has_make_check_target(directory):
        for makefile_name in ("Makefile", "makefile"):
            makefile = os.path.join(directory, makefile_name)
            if not os.path.isfile(makefile):
                continue
            with open(makefile, encoding="utf-8", errors="ignore") as file:
                return re.search(r"^check\s*:", file.read(), re.MULTILINE) is not None
        return False

    def _create_symlink_shim(self):
        """Copy Qt ABI aliases when the OHOS workspace rejects symlinks."""
        shim_dir = os.path.join(self.build_folder, "conan_tools")
        os.makedirs(shim_dir, exist_ok=True)
        shim = os.path.join(shim_dir, "ln")
        real_ln = shutil.which("ln") or "/system/bin/ln"
        with open(shim, "w", encoding="utf-8") as shim_file:
            shim_file.write(
                "#!/bin/sh\n"
                f"if {shlex.quote(real_ln)} \"$@\"; then\n"
                "  exit 0\n"
                "fi\n"
                "if [ \"$1\" = \"-s\" ]; then\n"
                "  shift\n"
                "  rm -f \"$2\"\n"
                "  cp -f \"$1\" \"$2\"\n"
                "  exit $?\n"
                "fi\n"
                "exit 1\n"
            )
        os.chmod(shim, 0o755)
        return shim_dir

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
        qt5gui.system_libs = ["EGL", "GLESv2"]
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
