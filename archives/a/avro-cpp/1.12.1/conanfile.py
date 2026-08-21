from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import get


class AvroCppConan(ConanFile):
    name = "avro-cpp"
    version = "1.12.1"
    package_type = "library"
    description = "Apache Avro C++ serialization library"
    license = "Apache-2.0"
    homepage = "https://avro.apache.org/"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    topics = ("serialization", "schema", "apache-avro")
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": False, "fPIC": True}

    def config_options(self):
        if self.settings.os == "Windows":
            self.options.rm_safe("fPIC")

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("avro-cpp supports Linux and OHOS only")
        if self.settings.os == "OHOS" and self.settings.arch != "armv8":
            raise ConanInvalidConfiguration("avro-cpp OHOS validation requires armv8")

    def requirements(self):
        self.requires("boost/1.84.0")
        self.requires("zlib/1.3.1.1")
        self.requires("fmt/11.2.0-r1")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=False)

    def layout(self):
        cmake_layout(self, src_folder="source/lang/c++")

    def generate(self):
        CMakeDeps(self).generate()
        tc = CMakeToolchain(self)
        tc.variables["AVRO_BUILD_STATIC"] = not self.options.shared
        tc.variables["AVRO_BUILD_SHARED"] = bool(self.options.shared)
        tc.variables["AVRO_BUILD_TESTS"] = True
        tc.variables["AVRO_BUILD_EXECUTABLES"] = False
        tc.variables["AVRO_USE_BOOST"] = True
        tc.variables["FETCHCONTENT_FULLY_DISCONNECTED"] = True
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
        cmake.test()

    def package(self):
        CMake(self).install()

    def package_info(self):
        self.cpp_info.libs = ["avrocpp_s"]
        self.cpp_info.set_property("cmake_file_name", "avrocpp")
        self.cpp_info.set_property("cmake_target_name", "avrocpp_s")
        self.cpp_info.set_property("pkg_config_name", "avro-cpp")
