import os

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, cmake_layout
from conan.tools.files import copy, get, replace_in_file


class AevolConan(ConanFile):
    name = "aevol"
    version = "9.4.0"
    package_type = "application"
    description = "An in silico experimental evolution platform"
    license = "GPL-3.0-or-later"
    homepage = "https://www.aevol.fr/"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    topics = ("evolution", "simulation", "genetics", "bioinformatics")

    settings = "os", "arch", "compiler", "build_type"

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("aevol is adapted for Linux/OHOS")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("aevol/9.4.0 is validated for OHOS armv8")

    def layout(self):
        cmake_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)
        get(self, **self.conan_data["sources"]["json-3.12.0"], strip_root=True,
            destination=os.path.join(self.source_folder, "_deps", "json"))
        get(self, **self.conan_data["sources"]["googletest-1.14.0"], strip_root=True,
            destination=os.path.join(self.source_folder, "_deps", "googletest"))
        replace_in_file(
            self, os.path.join(self.source_folder, "CMakeLists.txt"),
            """include(FetchContent)
FetchContent_Declare(
    json
    URL      https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz
    URL_HASH SHA256=42f6e95cad6ec532fd372391373363b62a14af6d771056dbfc86160e6dfff7aa
)
Message(STATUS \"Getting external dependencies...\")
FetchContent_MakeAvailable(json)
Message(STATUS \"Getting external dependencies... Done\")""",
            "add_subdirectory(${CMAKE_SOURCE_DIR}/_deps/json ${CMAKE_BINARY_DIR}/_deps/json EXCLUDE_FROM_ALL)",
        )
        replace_in_file(
            self, os.path.join(self.source_folder, "test", "gtest", "CMakeLists.txt"),
            """FetchContent_Declare(
    googletest
    GIT_REPOSITORY https://github.com/google/googletest.git
    GIT_TAG        v1.14.0
)
Message(STATUS \"Getting external dependency (googletest)...\")
FetchContent_MakeAvailable(googletest)
Message(STATUS \"Getting external dependency (googletest)... Done\")""",
            "add_subdirectory(${CMAKE_SOURCE_DIR}/_deps/googletest ${CMAKE_BINARY_DIR}/_deps/googletest EXCLUDE_FROM_ALL)",
        )

    def build(self):
        cmake = CMake(self)
        cmake.configure(variables={
            "with-omp": "OFF",
            "CMAKE_C_COMPILER": "clang",
            "CMAKE_CXX_COMPILER": "clang++",
        })
        cmake.build(target="all-with-gtests", args=["-j2"])
        cmake.test()
        cmake.build(target="install", args=["-j2"])

    def package(self):
        copy(self, "COPYING", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.bindirs = ["bin"]
