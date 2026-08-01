import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import can_run
from conan.tools.env import Environment
from conan.tools.files import apply_conandata_patches, get, replace_in_file, save
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class BerkeleyDbConan(ConanFile):
    name = "berkeley-db"
    version = "18.1.40"
    description = "Berkeley DB embedded database"
    license = "AGPL-3.0-only OR LicenseRef-Oracle-Berkeley-DB"
    url = "https://www.oracle.com/database/technologies/related/berkeleydb.html"
    package_type = "library"
    exports_sources = "conandata.yml", "patches/*"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False]}
    default_options = {"shared": True}

    def requirements(self):
        self.requires("tcl/9.0.3.1")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def validate(self):
        if self.settings.os != "OHOS" or self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("berkeley-db is packaged for OHOS armv8 only")
        if not self.options.shared:
            raise ConanInvalidConfiguration(
                "Berkeley DB Tcl regression tests require a shared libdb_tcl module"
            )

    def generate(self):
        tcl_root = self.dependencies["tcl"].package_folder
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--prefix=/")
        tc.configure_args.extend([
            "--enable-shared",
            "--disable-static",
            "--enable-tcl",
            "--enable-test",
            "--with-tcl={}".format(os.path.join(tcl_root, "lib")),
        ])
        # Tcl 9 no longer provides the legacy CONST compatibility macro.
        tc.extra_cflags.append("-DCONST=const")
        if self.settings.os == "OHOS":
            # Berkeley DB's bundled config.guess does not recognize HarmonyOS.
            tc.configure_args.append("--build=aarch64-unknown-linux-gnu")
            tc.configure_args.append("--host=aarch64-unknown-linux-gnu")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        tcl_root = self.dependencies["tcl"].package_folder
        tcl_lib = os.path.join(tcl_root, "lib")
        autotools = Autotools(self)
        configure_env = Environment()
        configure_env.define("TCL_ROOT", tcl_root)
        with configure_env.vars(self).apply():
            autotools.configure(build_script_folder="dist")
        replace_in_file(
            self,
            os.path.join(self.build_folder, "include.tcl"),
            "${TCL_ROOT}",
            tcl_root,
            strict=True,
        )
        autotools.make()
        autotools.make(target="test_mutex")
        if can_run(self):
            self.run(
                os.path.join(self.build_folder, "test_mutex") + " -p 2 -n 10 -l 10",
                env="conanrun",
            )
            tcl_runner = os.path.join(self.build_folder, "run_tcl_tests.tcl")
            save(
                self,
                tcl_runner,
                "puts \"BDB_TMPDIR=$::env(BDB_TMPDIR)\"\nsource {{{}}}\nrun_all\nif {{[info exists ::failed] && $::failed != 0}} {{exit 1}}\n".format(
                    os.path.join(self.source_folder, "test", "tcl", "test.tcl")
                ),
            )
            tmp_dir = os.path.join(self.build_folder, "tmp")
            os.makedirs(tmp_dir, exist_ok=True)
            test_env = Environment()
            test_env.define("TCL_ROOT", tcl_root)
            test_env.define_path("TCL_LIBRARY", os.path.join(tcl_lib, "tcl9.0"))
            test_env.define("TMPDIR", tmp_dir)
            test_env.define("TMP", tmp_dir)
            test_env.define("TEMP", tmp_dir)
            test_env.define("BDB_TMPDIR", tmp_dir)
            test_env.prepend_path("LD_LIBRARY_PATH", tcl_lib)
            test_env.prepend_path("LD_LIBRARY_PATH", os.path.join(self.build_folder, ".libs"))
            with test_env.vars(self).apply():
                self.run(
                    '"{}" "{}"'.format(os.path.join(tcl_root, "bin", "tclsh9.0"), tcl_runner),
                    cwd=self.build_folder,
                    env="conanrun",
                )

    def package(self):
        autotools = Autotools(self)
        autotools.install(args=["-j1"])

    def package_info(self):
        self.cpp_info.libs = ["db"]
