from conan import ConanFile
from conan.tools.files import get, export_conandata_patches
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class XcalcConan(ConanFile):
    name = "xcalc"
    version = "1.1.3"
    description = "Scientific calculator for the X Window System"
    homepage = "https://gitlab.freedesktop.org/xorg/app/xcalc"
    url = "https://gitlab.freedesktop.org/xorg/app/xcalc"
    license = "MIT"
    settings = "os", "compiler", "build_type", "arch"

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        prefix = "/storage/Users/currentUser/usr/local"
        tc.configure_args.extend([
            "--disable-dependency-tracking",
            "--with-appdefaultdir=/share/X11/app-defaults",
            f"--x-includes={prefix}/include",
            f"--x-libraries={prefix}/lib",
        ])
        tc.extra_cflags.append(f"-I{prefix}/include")
        tc.extra_ldflags.extend([
            f"-L{prefix}/lib",
            f"-Wl,-rpath,{prefix}/lib",
        ])
        tc.generate()

    def build(self):
        autotools = Autotools(self)
        autotools.configure()
        self.run('make -j1', cwd=self.build_folder, env="conanbuild")

    def package(self):
        autotools = Autotools(self)
        autotools.install()

    def package_info(self):
        self.cpp_info.libs = []
        self.cpp_info.bindirs = ["bin"]
