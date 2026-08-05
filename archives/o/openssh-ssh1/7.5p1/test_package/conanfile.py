#!/usr/bin/env python3
from conan import ConanFile


class OpenSshSsh1TestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        # 真机 SELinux seclabel 策略拒执行：conan cache 落在 HMFS 上，
        # 文件 seclabel 是 u:object_r:hmdfs:s0，内核拒执行任何此类 ELF
        # （Operation not permitted，与 static/dynamic 无关——static
        # linked ssh 同样被拒；可执行标签 u:object_r:hnp_file:s0 的
        # 分区如 /data/service/hnp/ 真机无写权限）。can_run() 只看构建
        # 配置不看 seclabel，故对 OHOS 显式跳过，靠编译通过 + 配方
        # 完整性证明。曾尝试 -static linking 绕 dynamic loader，但
        # 根因是 seclabel 非 loader，static 救不了，已还原。
        if self.settings.os == "OHOS":
            self.output.info("OHOS SELinux hmdfs seclabel denies binary execution: skipping SSH1 execution test.")
            return

        package_folder = self.dependencies["openssh-ssh1"].package_folder
        self.run(
            f"sh test_openssh_ssh1.sh '{package_folder}'",
            env="conanrun",
        )

