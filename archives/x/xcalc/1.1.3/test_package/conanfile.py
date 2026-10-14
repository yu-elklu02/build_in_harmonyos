import os

from conan import ConanFile


class XcalcTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        package = self.dependencies["xcalc"].package_folder
        executable = os.path.join(package, "bin", "xcalc")
        self.output.info(f"Checking packaged executable: {executable}")
        if not os.path.isfile(executable):
            raise RuntimeError("xcalc executable was not installed")
        if not os.access(executable, os.X_OK):
            raise RuntimeError("xcalc executable is not executable")
        self.run("file \"{}\"".format(executable), ignore_errors=False)
        self.run('sh "{}" "{}"'.format(
            os.path.join(self.recipe_folder, "test_xcalc.sh"), package),
            ignore_errors=False)
