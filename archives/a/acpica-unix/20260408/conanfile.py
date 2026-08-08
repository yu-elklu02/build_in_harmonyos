import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
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

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("acpica-unix supports Linux and OHOS")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("acpica-unix supports only OHOS armv8")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def build(self):
        cc = os.environ.get("CC", "clang")
        # ACPICA defaults to _CYGWIN when uname is unfamiliar. Explicitly use
        # the Unix host configuration on HarmonyOS and build only iasl.
        # Makefile.config hard-codes -Werror plus gcc-only warning options
        # (-Wlogical-op, -Wmissing-parameter-type, -Wold-style-declaration)
        # that clang rejects as -Wunknown-warning-option; -Werror upgrades
        # those to hard errors. NOWERROR=TRUE toggles the ifneq guard on
        # Makefile.config:226 and drops -Werror, so the unknown options stay
        # warnings and the build completes under clang.
        self.run(f'make iasl CC="{cc}" ACPI_HOST=_LINUX NOWERROR=TRUE', cwd=self.source_folder)
        # Run the upstream ASL test suite after the compiler build. The suite
        # builds its own iasl/acpiexec variants and exercises compilation,
        # disassembly, and execution of the upstream ASL cases.
        # aslts.sh:8-10 hard-codes /tmp/iasl-$postfix, /tmp/acpiexec-*, and
        # /tmp/acpibin-*; OHOS mounts /tmp read-only, so the cp into that path
        # aborts ('Read-only file system') and the suite gives up with 'iasl
        # compiler not found'. Rewrite those three tmp_* assignments to honor
        # TMPDIR (mktemp-style ${TMPDIR:-/tmp}), then point TMPDIR at a home
        # location so the suite's scratch dir + iasl copy land somewhere
        # writable before running.
        aslts_sh = os.path.join(self.source_folder, "tests", "aslts.sh")
        with open(aslts_sh) as f:
            aslts_text = f.read()
        aslts_text = aslts_text.replace("/tmp/iasl-$postfix", "${TMPDIR:-/tmp}/iasl-$postfix")
        aslts_text = aslts_text.replace("/tmp/acpiexec-$postfix", "${TMPDIR:-/tmp}/acpiexec-$postfix")
        aslts_text = aslts_text.replace("/tmp/acpibin-$postfix", "${TMPDIR:-/tmp}/acpibin-$postfix")
        with open(aslts_sh, "w") as f:
            f.write(aslts_text)
        # asltsrun:260 spawns each test case via `xargs ... bash -c '...'`.
        # GNU xargs execs the command through /bin/sh -c, and OHOS /bin/sh is
        # toybox (no loop break, no [[ ]]), so the bash -c subshell lands in
        # toybox and aborts ('break: can't break'). Pin the bash -c invocation
        # to the real hnp bash absolute path so xargs execs hnp bash directly,
        # skipping the toybox /bin/sh layer entirely. hnp_bash is also used
        # below to rewrite the bin/ shebangs, so declare it here upfront.
        hnp_bash = "/data/service/hnp/bin/bash"
        asltsrun = os.path.join(self.source_folder, "tests", "aslts", "bin", "asltsrun")
        with open(asltsrun) as f:
            asltsrun_text = f.read()
        # asltsrun:260 spawns each test case via `xargs -P -I {} bash -c '...'`.
        # GNU xargs execs the command through /bin/sh -c, and OHOS /bin/sh is
        # toybox (no loop break, no [[ ]]), so the bash -c subshell lands in
        # toybox and aborts ('break: can't break'). Pin the inner bash -c to
        # the real hnp bash absolute path AND replace the xargs parallel
        # dispatch with a bash while-read + & + wait loop that keeps hnp bash
        # as the exec shell throughout (no /bin/sh layer at all).
        asltsrun_text = asltsrun_text.replace(" bash -c ", f" {hnp_bash} -c ")
        # do_summary_of_test_case (:395) and do_all_summary (:506) use
        # `cat "$1" | while [ 1 ]; do ... break ... done` and `ls "$1" | while`
        # constructs. Under bash the pipeline right-hand runs as a bash
        # subshell, but OHOS toybox `cat`/`ls` exec the pipeline RHS through
        # /bin/sh, so the `break` lands in toybox (no loop break) and aborts.
        # Rewrite each as a bash process substitution `< <(cat "$1")` /
        # `< <(ls "$1")` so the while loop stays in hnp bash, not /bin/sh.
        asltsrun_text = asltsrun_text.replace(
            '\tcat "$1" |\\\n\twhile [ 1 ]\n\tdo',
            '\twhile [ 1 ]\n\tdo\n\t\tread line < <(cat "$1")',
        )
        asltsrun_text = asltsrun_text.replace(
            '\tls "$1" |\\\n\twhile [ 1 ]\n\tdo',
            '\twhile [ 1 ]\n\tdo\n\t\tread filename < <(ls "$1")',
        )
        old_xargs = (
            '\tprintf \'%s\\n\' "${test_case_arr[@]}" |\\\n'
            '\txargs -n 1 -P $procs -I {} /data/service/hnp/bin/bash -c '
            "'run_test_case $1 $2 > $3/$4/$1'\\\n"
            "\t_ {} $bit_mode $res_dir $modepart\n"
        )
        new_loop = (
            '\t# OHOS: xargs execs via /bin/sh (toybox, no break), replaced with '
            'a bounded bash & + wait loop keeping hnp bash as exec shell.\n'
            '\tlocal _ohos_pids=()\n'
            '\tfor _tc in "${test_case_arr[@]}"; do\n'
            f'\t\t{hnp_bash} -c \'run_test_case "$1" "$2" > "$3/$4/$1"\' '
            'bash "$_tc" "$bit_mode" "$res_dir" "$modepart" &\n'
            '\t\t_ohos_pids+=($!)\n'
            '\t\twhile [ $(jobs -rp | wc -l) -ge $procs ]; do sleep 0.1; done\n'
            '\tdone\n'
            '\twait "${_ohos_pids[@]}" 2>/dev/null\n'
        )
        if old_xargs not in asltsrun_text:
            # The exact whitespace may differ; try a looser match by splitting
            # on the printf line and the trailing _ {} ... line.
            import re
            pat = re.compile(
                r"\tprintf '%s\\n' \"\$\{test_case_arr\[@\]\}\" \|\\?\n"
                r"\txargs -n 1 -P \$procs -I \{\} /data/service/hnp/bin/bash -c "
                r"'run_test_case \$1 \$2 > \$3/\$4/\$1'\\?\n"
                r"\t_ \{\} \$bit_mode \$res_dir \$modepart\n",
                re.MULTILINE,
            )
            asltsrun_text, n = pat.subn(new_loop, asltsrun_text, count=1)
        else:
            asltsrun_text = asltsrun_text.replace(old_xargs, new_loop)
        with open(asltsrun, "w") as f:
            f.write(asltsrun_text)
        # tests/aslts/bin/Do and 9 sibling scripts hard-code '#!/bin/bash';
        # OHOS has no /bin/bash (bash lives in /data/service/hnp/bin/bash and
        # /bin is a read-only symlink to /system/bin). These scripts use bash
        # constructs (export -f, [[ ]], extglob), so /bin/sh is not enough.
        # Rewrite their shebang to the real hnp bash path (v5.3, supports the
        # bash-isms the suite relies on).
        aslts_bin = os.path.join(self.source_folder, "tests", "aslts", "bin")
        for name in os.listdir(aslts_bin):
            p = os.path.join(aslts_bin, name)
            if not os.path.isfile(p):
                continue
            with open(p) as f:
                head = f.read(12)
            if head.startswith("#!/bin/bash"):
                with open(p) as f:
                    body = f.read()
                with open(p, "w") as f:
                    f.write("#!" + hnp_bash + "\n" + body[9:])
        aslts_tmp = os.path.join(os.path.expanduser("~"), "aslts-tmp")
        os.makedirs(aslts_tmp, exist_ok=True)
        # asltsrun:260 uses `xargs -n 1 -P $procs -I {} bash -c '...'`; the
        # OHOS busybox xargs rejects -I ('Unknown option'). Harmonybrew's
        # findutils ships GNU xargs (supports -I), so prepend its bin for
        # the suite run alongside the TMPDIR redirect.
        hb_bin = os.path.expanduser("~/.harmonybrew/bin")
        # aslts.sh uses relative paths (pushd templates at :131, cd into
        # generation_dir at :81) that resolve against tests/ — templates/
        # lives at tests/templates, not tests/aslts/templates. So run the
        # suite with cwd at tests/ rather than the source root. During build
        # self.source_folder resolves to .../b/build-release (basic_layout
        # build_type subdir), so step up to the real build root first.
        build_root = os.path.dirname(self.build_folder)
        tests_dir = os.path.join(build_root, "tests")
        self.run(
            f'PATH="{hb_bin}:$PATH" TMPDIR="{aslts_tmp}" CC="{cc}" ACPI_HOST=_LINUX NOWERROR=TRUE bash aslts.sh',
            cwd=tests_dir,
        )

    def test(self):
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
