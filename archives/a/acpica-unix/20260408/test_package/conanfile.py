import os

from conan import ConanFile


class AcpicaUnixTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "VirtualRunEnv"
    test_type = "explicit"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package_bin = os.path.join(
            self.dependencies[self.tested_reference_str].package_folder, "bin"
        )
        # Smoke-test the packaged iasl through the test.sh consumer script.
        # The upstream ASL Test Suite (aslts.sh, 174 cases) runs in the main
        # recipe's build() stage — conan `create` invokes build() where the
        # full upstream source tree still lives, so aslts.sh can rebuild
        # iasl/acpiexec/acpibin from source. test_package only validates the
        # packaged iasl binary end-to-end via input.asl.
        self.run(f'PATH="{package_bin}:$PATH" sh test.sh', env="conanrun")
