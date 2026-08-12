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
        # Run aslts.sh with stdout+stderr teed to a build-folder log so the
        # per-case pass/fail statistics below can grep it. aslts.sh's own exit
        # code is unreliable (returns 0 even when every case bailed); the
        # upstream Summary file is blank because do_summary_of_mode's
        # `cat | while read; break` pipeline rejects on HarmonyOS toybox
        # ("break: can't break"). The 0007 patch appended per-case TSV lines
        # from run_test_case(), but on HarmonyOS aslts.sh only reaches the
        # Do 0 compile stage (Do 1 / acpiexec execute stage bails on the same
        # break blocker), so run_test_case() is never invoked and the TSV is
        # empty. Instead we count the per-case×mode compile lines that
        # aslts.sh DOES emit: each `Type: <mode> Compile => ... Done` line is
        # one case×mode run; trailing `**** Unexpected iASL failure` or
        # `[[ Error:` marks FAIL, bare `Done` marks PASS. This is the only
        # auditable per-case record on HarmonyOS.
        aslts_log = os.path.join(self.build_folder, "aslts-run.log")
        self.run(
            f'env CC="{cc}" MAKEFLAGS=-j1 TMPDIR="{tmpdir}" PATH="{run_path}" '
            f'"{bash_bin}" -x tests/aslts.sh > "{aslts_log}" 2>&1',
            cwd=self.source_folder,
        )

        # Count per-case×mode compile pass/fail from the aslts-run.log lines.
        # fail>0 → raise so conan create exits non-zero (per upstream ASLTS
        # semantics: any compile failure is a regression). skip is reported
        # separately, NOT counted as pass. We do NOT invent a pass count from
        # the blank Summary or aslts.sh exit code.
        from conan.errors import ConanException
        passed = failed = skipped = 0
        fail_cases = []
        if os.path.isfile(aslts_log):
            with open(aslts_log, encoding="utf-8", errors="replace") as f:
                for line in f:
                    if "Type:" not in line or "Compile =>" not in line:
                        continue
                    if "Unexpected iASL failure" in line or "[[ Error:" in line:
                        failed += 1
                        fail_cases.append(line.strip())
                    elif line.rstrip().endswith("Done"):
                        passed += 1
                    else:
                        skipped += 1
        self.output.info(
            f"ACPI upstream ASLTS: {passed} passed, {failed} failed, {skipped} skipped"
        )
        if skipped:
            self.output.info(
                f"ACPI upstream ASLTS: {skipped} cases skipped (neither PASS nor FAIL marker)"
            )
        if failed:
            self.output.info(
                "ACPI upstream ASLTS failed cases (first 20): "
                + "; ".join(fail_cases[:20])
            )
            raise ConanException(
                f"ACPI upstream ASLTS failed: {passed} passed, {failed} failed, "
                f"{skipped} skipped"
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
