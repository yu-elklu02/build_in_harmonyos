import os
import shlex

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get, replace_in_file, save
from conan.tools.layout import basic_layout


_EXPECTED_FALLBACK = r"""#pragma once
#if __has_include(<expected>) && !defined(BTOP_FORCE_EXPECTED_FALLBACK)
#include <expected>
#else
#include <utility>

namespace std {
template <class E>
class unexpected {
public:
    constexpr explicit unexpected(E value) : value_(std::move(value)) {}
    constexpr const E& error() const & noexcept { return value_; }
    constexpr E& error() & noexcept { return value_; }
private:
    E value_;
};

template <class T, class E>
class expected {
public:
    constexpr expected(const T& value) : has_(true), value_(value), error_() {}
    constexpr expected(T&& value) : has_(true), value_(std::move(value)), error_() {}
    constexpr expected(const unexpected<E>& error) : has_(false), value_(), error_(error.error()) {}
    constexpr expected(unexpected<E>&& error) : has_(false), value_(), error_(std::move(error.error())) {}
    constexpr bool has_value() const noexcept { return has_; }
    constexpr explicit operator bool() const noexcept { return has_; }
    constexpr T& value() & noexcept { return value_; }
    constexpr const T& value() const & noexcept { return value_; }
    constexpr E& error() & noexcept { return error_; }
    constexpr const E& error() const & noexcept { return error_; }
private:
    bool has_ {};
    T value_ {};
    E error_ {};
};
}  // namespace std
#endif
"""


class BtopConan(ConanFile):
    name = "btop"
    version = "1.4.7"
    description = "Resource monitor that shows CPU, memory, disk, network and process information"
    license = "Apache-2.0"
    homepage = "https://github.com/aristocratos/btop"
    url = "https://gitcode.com/OpenHarmonyPCDeveloper/build_in_harmonyos"
    package_type = "application"
    settings = "os", "compiler", "build_type", "arch"

    def layout(self):
        basic_layout(self)

    def validate(self):
        if self.settings.os not in ("Linux", "OHOS"):
            raise ConanInvalidConfiguration("btop supports Linux/OHOS only in this recipe")

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def build(self):
        self._patch_ohos()
        cxx = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict).get("cpp", "c++")
        cc = self.conf.get("tools.build:compiler_executables", default={}, check_type=dict).get("c", "cc")
        cxxflags = "-DBTOP_FORCE_EXPECTED_FALLBACK -DBTOP_OHOS"
        args = [
            "make",
            "PLATFORM=linux",
            "GPU_SUPPORT=false",
            "INTEL_GPU_SUPPORT=false",
            "STATIC=false",
            "STRIP=false",
            "QUIET=true",
            "VERBOSE=false",
            "THREADS=1",
            "BUILD_TYPE=Release",
            "CXX={}".format(shlex.quote(cxx)),
            "CC={}".format(shlex.quote(cc)),
            "ADDFLAGS={}".format(shlex.quote(cxxflags)),
            "-j1",
        ]
        self.run(" ".join(args), cwd=self.source_folder, env="conanbuild")

    def _patch_ohos(self):
        save(self, os.path.join(self.source_folder, "include", "btop_expected_fallback.hpp"), _EXPECTED_FALLBACK)
        cli_header = os.path.join(self.source_folder, "src", "btop_cli.hpp")
        replace_in_file(
            self,
            cli_header,
            "#include <expected>",
            "#include <btop_expected_fallback.hpp>",
            strict=False,
        )
        tools_header = os.path.join(self.source_folder, "src", "btop_tools.hpp")
        replace_in_file(
            self,
            tools_header,
            """\t//* Split <string> at all occurrences of <delim> and return as vector of strings
\tconstexpr auto ssplit(std::string_view str, char delim = ' ') {
\t\treturn str | std::views::split(delim) | std::views::filter([](auto&& range) { return !std::ranges::empty(range); }) |
\t\t\t   std::ranges::to<std::vector<std::string>>();
\t}
""",
            """\t//* Split <string> at all occurrences of <delim> and return as vector of strings
\tinline auto ssplit(std::string_view str, char delim = ' ') {
\t\tstd::vector<std::string> out;
\t\tfor (auto&& range : str | std::views::split(delim)) {
\t\t\tif (std::ranges::empty(range)) continue;
\t\t\tout.emplace_back(std::string_view { range });
\t\t}
\t\treturn out;
\t}
""",
            strict=False,
        )
        main_cpp = os.path.join(self.source_folder, "src", "main.cpp")
        replace_in_file(
            self,
            main_cpp,
            """auto main(int argc, const char* argv[]) -> int {
\treturn btop_main(std::views::counted(std::next(argv), argc - 1) | std::ranges::to<std::vector<std::string_view>>());
}
""",
            """auto main(int argc, const char* argv[]) -> int {
\tstd::vector<std::string_view> args;
\targs.reserve(argc > 0 ? static_cast<std::size_t>(argc - 1) : 0);
\tfor (int i = 1; i < argc; ++i) args.emplace_back(argv[i]);
\treturn btop_main(args);
}
""",
            strict=False,
        )
        linux_collect = os.path.join(self.source_folder, "src", "linux", "btop_collect.cpp")
        replace_in_file(
            self,
            linux_collect,
            "return std::views::iota(0, Shared::coreCount) | std::ranges::to<std::vector<std::int32_t>>();",
            "auto cpus = std::vector<std::int32_t>{}; for (int i = 0; i < Shared::coreCount; ++i) cpus.push_back(i); return cpus;",
            strict=False,
        )
        btop_cpp = os.path.join(self.source_folder, "src", "btop.cpp")
        replace_in_file(
            self,
            btop_cpp,
            """\t#if defined __APPLE__ || defined __OpenBSD__ || defined __NetBSD__
\t\tif (pthread_join(Runner::runner_id, nullptr) != 0) {
\t\t\tLogger::warning("Failed to join _runner thread on exit!");
\t\t\tpthread_cancel(Runner::runner_id);
\t\t}
\t#else
\t\tconstexpr struct timespec ts { .tv_sec = 5, .tv_nsec = 0 };
\t\tif (pthread_timedjoin_np(Runner::runner_id, nullptr, &ts) != 0) {
\t\t\tLogger::warning("Failed to join _runner thread on exit!");
\t\t\tpthread_cancel(Runner::runner_id);
\t\t}
\t#endif
""",
            """\t#if defined __APPLE__ || defined __OpenBSD__ || defined __NetBSD__ || defined BTOP_OHOS
\t\tif (pthread_join(Runner::runner_id, nullptr) != 0) {
\t\t\tLogger::warning("Failed to join _runner thread on exit!");
\t\t}
\t#else
\t\tconstexpr struct timespec ts { .tv_sec = 5, .tv_nsec = 0 };
\t\tif (pthread_timedjoin_np(Runner::runner_id, nullptr, &ts) != 0) {
\t\t\tLogger::warning("Failed to join _runner thread on exit!");
\t\t\tpthread_cancel(Runner::runner_id);
\t\t}
\t#endif
""",
            strict=False,
        )
        replace_in_file(
            self,
            btop_cpp,
            """\t\tif (active) {
\t\t\tLogger::error("Stall in Runner thread, restarting!");
\t\t\tset_active(false);
\t\t\t// exit(1);
\t\t\tpthread_cancel(Runner::runner_id);

\t\t\t// Wait for the thread to actually terminate before creating a new one
\t\t\tvoid* thread_result;
\t\t\tint join_result = pthread_join(Runner::runner_id, &thread_result);
\t\t\tif (join_result != 0) {
\t\t\t\tLogger::warning("Failed to join cancelled thread: {}", strerror(join_result));
\t\t\t}

\t\t\tif (pthread_create(&Runner::runner_id, nullptr, &Runner::_runner, nullptr) != 0) {
\t\t\t\tGlobal::exit_error_msg = "Failed to re-create _runner thread!";
\t\t\t\tclean_quit(1);
\t\t\t}
\t\t}
""",
            """\t\tif (active) {
\t\t\tLogger::error("Stall in Runner thread, restarting!");
\t\t\tset_active(false);
\t\t\t// exit(1);
\t\t#ifndef BTOP_OHOS
\t\t\tpthread_cancel(Runner::runner_id);

\t\t\t// Wait for the thread to actually terminate before creating a new one
\t\t\tvoid* thread_result;
\t\t\tint join_result = pthread_join(Runner::runner_id, &thread_result);
\t\t\tif (join_result != 0) {
\t\t\t\tLogger::warning("Failed to join cancelled thread: {}", strerror(join_result));
\t\t\t}

\t\t\tif (pthread_create(&Runner::runner_id, nullptr, &Runner::_runner, nullptr) != 0) {
\t\t\t\tGlobal::exit_error_msg = "Failed to re-create _runner thread!";
\t\t\t\tclean_quit(1);
\t\t\t}
\t\t#endif
\t\t}
""",
            strict=False,
        )
        replace_in_file(
            self,
            linux_collect,
            """        return buf | std::views::split(',') | std::views::transform([](auto&& range) -> auto {
                   auto view = std::string_view { range };
                   auto dash = view.find('-');

                   if (dash == std::string_view::npos) {
                       // Single CPU, return iota of single element
                       auto value = to_int(view);
                       return std::views::iota(value, value + 1);
                   }

                   auto start = to_int(view.substr(0, dash));
                   auto end = to_int(view.substr(dash + 1));
                   return std::views::iota(start, end + 1);
               }) |
               std::views::join | std::ranges::to<std::vector<std::int32_t>>();
""",
            """        auto cpus = std::vector<std::int32_t>{};
        for (auto&& range : buf | std::views::split(',')) {
            auto view = std::string_view { range };
            auto dash = view.find('-');
            if (dash == std::string_view::npos) {
                cpus.push_back(static_cast<std::int32_t>(to_int(view)));
                continue;
            }
            auto start = to_int(view.substr(0, dash));
            auto end = to_int(view.substr(dash + 1));
            for (auto value = start; value <= end; ++value) cpus.push_back(static_cast<std::int32_t>(value));
        }
        return cpus;
""",
            strict=False,
        )

    def package(self):
        self.run(
            "make install PREFIX=/usr/local DESTDIR={}".format(shlex.quote(self.package_folder)),
            cwd=self.source_folder,
            env="conanbuild",
        )
        copy(self, "LICENSE", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []
        self.cpp_info.bindirs = ["bin"]
        self.runenv_info.define_path("PATH", os.path.join(self.package_folder, "bin"))
