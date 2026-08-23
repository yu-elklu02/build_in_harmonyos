import os
import json
import shutil

from conan import ConanFile
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.env import VirtualRunEnv


class LibZitaResamplerTestConan(ConanFile):
    settings = "os", "arch", "compiler", "build_type"
    def requirements(self):
        self.requires(self.tested_reference_str)

    def generate(self):
        CMakeDeps(self).generate()
        CMakeToolchain(self).generate()
        VirtualRunEnv(self).generate()
        preset = os.path.join(self.generators_folder, "CMakePresets.json")
        if os.path.isfile(preset):
            with open(preset, encoding="utf-8") as handle:
                data = json.load(handle)
            for item in data.get("configurePresets", []):
                item["generator"] = "Ninja"
            with open(preset, "w", encoding="utf-8") as handle:
                json.dump(data, handle, indent=2)

    def layout(self):
        cmake_layout(self)

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        binary = os.path.join(self.cpp.build.bindirs[0], "test_zita_resampler")
        if str(self.settings.os) == "OHOS":
            files_dir = os.path.join(self.build_folder, "files")
            os.makedirs(files_dir, exist_ok=True)
            signed_binary = os.path.join(files_dir, "test_zita_resampler")
            shutil.copy2(binary, signed_binary)
            signer = "/data/service/hnp/bin/binary-sign-tool"
            package_lib = os.path.join(
                self.dependencies[self.tested_reference_str].package_folder,
                "lib",
                "libzita-resampler.so.1.11.2",
            )
            if os.path.isfile(package_lib):
                shutil.copy2(package_lib, os.path.join(files_dir, "libzita-resampler.so.1.11.2"))
                shutil.copy2(package_lib, os.path.join(files_dir, "libzita-resampler.so.1"))
                shutil.copy2(package_lib, os.path.join(files_dir, "libzita-resampler.so"))
            if os.path.isfile(signer):
                self.run(f'{signer} sign -inFile "{signed_binary}" -outFile "{signed_binary}.signed" -selfSign 1')
                os.replace(signed_binary + ".signed", signed_binary)
            self.run(f'patchelf --set-rpath "$ORIGIN" "{signed_binary}"', ignore_errors=True)
            binary = signed_binary
        self.run(f'"{binary}"', env="conanrun")
