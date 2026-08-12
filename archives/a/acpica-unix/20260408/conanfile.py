import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.layout import basic_layout


class AcpicaUnixConan(ConanFile):
    name = "acpica-unix"
    version = "20260408"
    description = "ACPICA Unix tools, including the iASL compiler"
    license = "Intel ACPI Software License Agreement"
    homepage = "https://github.com/acpica/acpica"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "application"
    settings = "os", "compiler", "build_type", "arch"

    # aslts.sh + all helpers/tests/aslts/bin/* entry points use #!/bin/bash and
    # break/continue/for-((;;)) features that toybox /bin/sh rejects ("break:
    # can't break"). Declare a GNU Bash build-tool dependency so the test()
    # runner can invoke aslts.sh through the packaged bash absolute path.
    tool_requires = "bash/5.3"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("acpica-unix supports Linux and OHOS")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("acpica-unix supports only OHOS armv8")

    def layout(self):
        basic_layout(self)

    def export_sources(self):
        export_conandata_patches(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def build(self):
        apply_conandata_patches(self)
        cc = os.environ.get("CC", "clang")
        # ACPICA defaults to _CYGWIN when uname is unfamiliar. Explicitly use
        # the Unix host configuration on HarmonyOS and build only iasl.
        # NOWERROR=TRUE avoids upgrading GCC-only warning options rejected by
        # clang into errors.
        self.run(f'make iasl CC="{cc}" ACPI_HOST=_LINUX NOWERROR=TRUE', cwd=self.source_folder)

        # Run the upstream ASL Test Suite (aslts.sh, 174 cases) in the build
        # stage — conan `create` invokes build() unconditionally, and this is
        # where the full upstream source tree still lives (aslts.sh's
        # build_acpi_tools rebuilds iasl/acpiexec/acpibin from source via
        # `make`, which needs source/ + generate/ + tests/ together). Invoke
        # through the GNU Bash declared as tool_requires("bash/5.3") so the
        # #!/bin/bash shebang + break/continue/for-((;;)) features don't fall
        # back to toybox /bin/sh ("break: can't break"). CC=clang injects the
        # compiler into aslts.sh's `make` rebuild (upstream Makefile hardcodes
        # `cc` which HarmonyOS PATH lacks). MAKEFLAGS=-j1 disables GNU make's
        # jobserver so it does NOT create a FIFO in TMPDIR — HarmonyOS MAC
        # rejects mkfifo in the build folder ("Operation not permitted").
        # TMPDIR points the 0003-patched staging at a writable build folder
        # subdir (HarmonyOS /tmp is readonly).
        bash_dep = self.dependencies.build["bash"]
        bash_bin = os.path.join(bash_dep.package_folder, "bin", "bash")
        bash_bindir = os.path.join(bash_dep.package_folder, "bin")
        tmpdir = os.path.join(self.build_folder, "aslts-tmp")
        os.makedirs(tmpdir, exist_ok=True)
        cur_path = os.environ.get("PATH", "")
        run_path = f"{bash_bindir}:{cur_path}" if cur_path else bash_bindir
        self.run(
            f'env CC="{cc}" MAKEFLAGS=-j1 TMPDIR="{tmpdir}" PATH="{run_path}" '
            f'"{bash_bin}" -x tests/aslts.sh',
            cwd=self.source_folder,
        )

    def test(self):
        # Smoke-test the packaged iasl binary.
        self.run("generate/unix/bin/iasl -v", cwd=self.source_folder)

    def package(self):
        copy(
            self,
            "iasl",
            src=os.path.join(self.source_folder, "generate", "unix", "bin"),
            dst=os.path.join(self.package_folder, "bin"),
            keep_path=False,
        )
        copy(
            self,
            "LICENSE",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
            keep_path=False,
        )

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.cpp_info.libdirs = []
        self.cpp_info.libs = []
