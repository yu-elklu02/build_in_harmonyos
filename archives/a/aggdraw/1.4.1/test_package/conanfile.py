"""Conan consumer test for the aggdraw CPython extension."""
import os
import shutil
import sys
import tempfile
from glob import glob

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import can_run


class AggdrawTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"

    def requirements(self):
        self.requires(self.tested_reference_str)

    def test(self):
        if not can_run(self):
            self.output.info("Cross-built consumer cannot run on the build host.")
            return
        package_folder = self.dependencies["aggdraw"].package_folder
        script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_aggdraw.py")
        # OHOS CI stores Conan packages under HMDFS. Python dlopen rejects a
        # signed extension from that cache context with EACCES even though the
        # same artifact is loadable from a normal app-writable directory. Keep
        # consuming the actual package artifact, but execute it from TMPDIR so
        # the check covers the real native module without a false MAC failure.
        runtime_base = os.environ.get("TMPDIR") or self.build_folder
        os.makedirs(runtime_base, exist_ok=True)
        runtime_dir = tempfile.mkdtemp(
            prefix="aggdraw-test-",
            dir=runtime_base,
        )
        extensions = glob(os.path.join(package_folder, "aggdraw*.so"))
        if not extensions:
            raise ConanInvalidConfiguration("aggdraw extension is missing from the package")
        for extension in extensions:
            shutil.copy2(extension, os.path.join(runtime_dir, os.path.basename(extension)))
        # conan self.run's `env` only accepts predefined scope names, so inline
        # PYTHONPATH via the `env` command prefix.
        self.run(
            f'env PYTHONPATH="{runtime_dir}" "{sys.executable}" "{script}"',
        )
