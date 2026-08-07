import os
import shutil

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
from conan.tools.layout import basic_layout


class AlassConan(ConanFile):
    name = "alass"
    version = "2.0.0"
    description = "Automatic language-agnostic subtitle synchronization tool"
    license = "GPL-3.0-only"
    homepage = "https://github.com/kaegi/alass"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "application"
    settings = "os", "compiler", "build_type", "arch"

    def validate(self):
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("alass/2.0.0 supports only OHOS armv8")
        if not shutil.which("cargo"):
            raise ConanInvalidConfiguration("alass/2.0.0 requires Cargo in PATH")

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def build(self):
        cc = os.environ.get("CC", "clang")
        cxx = os.environ.get("CXX", "clang++")
        # Cargo defaults to the `cc` linker; the OHOS sysroot only ships clang.
        # RUSTFLAGS reaches rustc's linker selection (CC=clang alone does not).
        rustflags = os.environ.get("RUSTFLAGS", "-C linker=clang")
        env_prefix = f"CC={cc} CXX={cxx} RUSTFLAGS='{rustflags}'"
        # alass v2.0.0's Cargo.lock pins libc v0.2.62 (2021), which does not
        # know the OHOS linux_like target subset and emits 662 unresolved
        # symbols. libc v0.2.170+ added OHOS support; bump libc before testing.
        self.run(f"{env_prefix} cargo update -p libc", env="conanbuild")
        self.run(f"{env_prefix} cargo update -p nix", env="conanbuild")
        self.run(f"{env_prefix} cargo update -p ctrlc", env="conanbuild")
        self.run(f"{env_prefix} cargo test --release --workspace --jobs 1 --bins --lib --tests", env="conanbuild")
        self.run(f"{env_prefix} cargo build --release --package alass-cli --jobs 1", env="conanbuild")

    def package(self):
        copy(self, "alass-cli", src=os.path.join(self.source_folder, "target", "release"), dst=os.path.join(self.package_folder, "bin"), keep_path=False)

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
        self.runenv_info.append_path("PATH", os.path.join(self.package_folder, "bin"))
