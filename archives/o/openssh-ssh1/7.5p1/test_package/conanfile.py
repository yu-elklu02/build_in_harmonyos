#!/usr/bin/env python3
from conan import ConanFile


class OpenSshSsh1TestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    generators = "VirtualRunEnv"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        # OHOS cross-build 场景下真机 HMDFS 默认禁执行二进制
        #（/storage 与 /data/local/tmp 均无 exec 标志，ssh -V 报
        # "Operation not permitted"）。can_run() 只看构建配置同
        # host/target 不看文件系统执行位，故对 OHOS 显式跳过，
        # 靠编译通过 + 配方完整性证明。
        if self.settings.os == "OHOS":
            self.output.info("OHOS HMDFS disables binary execution: skipping SSH1 execution test.")
            return

        package_folder = self.dependencies["openssh-ssh1"].package_folder
        self.run(
            f"sh test_openssh_ssh1.sh '{package_folder}'",
            env="conanrun",
        )

