#!/usr/bin/env python3
import os
import shutil
import stat

from conan import ConanFile


class OpenSshSsh1TestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def _stage_ohos_executables(self, package_folder):
        # The Conan cache is on HMDFS on the OHOS CI device. ELF execution from
        # files labeled u:object_r:hmdfs:s0 is denied by SELinux, even when the
        # files are chmod +x. Stage only the binaries needed by this functional
        # smoke test into the HNP private bin directory, which is the executable
        # area exposed to the CI process.
        hnp_home = os.environ.get("HNP_PRIVATE_HOME", "/data/app")
        stage_root = os.path.join(
            hnp_home,
            "bin",
            f"openssh-ssh1-test-{os.getpid()}",
        )
        stage_bin = os.path.join(stage_root, "bin")
        os.makedirs(stage_bin, exist_ok=True)

        for name in ("ssh", "ssh-keygen"):
            src = os.path.join(package_folder, "bin", name)
            dst = os.path.join(stage_bin, name)
            shutil.copy2(src, dst)
            mode = os.stat(dst).st_mode
            os.chmod(
                dst,
                mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH,
            )

        return stage_root

    def test(self):
        package_folder = self.dependencies[self.tested_reference_str].package_folder
        staged_folder = None

        if self.settings.os == "OHOS":
            staged_folder = self._stage_ohos_executables(package_folder)
            package_folder = staged_folder

        try:
            self.run(
                f"sh test_openssh_ssh1.sh '{package_folder}'",
                env="conanrun",
            )
        finally:
            if staged_folder:
                shutil.rmtree(staged_folder, ignore_errors=True)

