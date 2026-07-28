#!/usr/bin/env python3
"""Conan recipe for libvo-aacenc 0.1.3."""

import os
import wave

from conan import ConanFile
from conan.errors import ConanException, ConanInvalidConfiguration
from conan.tools.build import cross_building
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get
from conan.tools.gnu import Autotools, AutotoolsToolchain
from conan.tools.layout import basic_layout


class LibvoaacencConan(ConanFile):
    name = "libvo-aacenc"
    version = "0.1.3"
    description = "VisualOn AAC encoder library"
    license = "Apache-2.0"
    homepage = "https://opencore-amr.sourceforge.net/"
    url = ""  # CI fills this
    package_type = "static-library"

    settings = "os", "compiler", "build_type", "arch"

    def validate(self):
        if str(self.settings.os) != "OpenHarmony":
            raise ConanInvalidConfiguration(
                "libvo-aacenc is currently adapted for OpenHarmony only"
            )
        if str(self.settings.arch) != "armv8":
            raise ConanInvalidConfiguration(
                "libvo-aacenc is currently adapted for armv8 only"
            )

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self)

    def source(self):
        get(self, **self.conan_data["sources"], strip_root=True)

    def generate(self):
        tc = AutotoolsToolchain(self)
        tc.configure_args.append("--disable-shared")
        tc.configure_args.append("--enable-static")
        tc.configure_args.append("--enable-example")
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        autotools = Autotools(self)
        autotools.configure()
        autotools.make(args=["-j1"])
        autotools.make(target="check", args=["-j1"])

        if not cross_building(self):
            input_wav = os.path.join(self.build_folder, "silence.wav")
            output_aac = os.path.join(self.build_folder, "silence.aac")
            with wave.open(input_wav, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(44100)
                wav_file.writeframes(b"\x00\x00" * 1024)
            self.run(
                "{} {} {}".format(
                    os.path.join(self.build_folder, "aac-enc"),
                    input_wav,
                    output_aac,
                )
            )
            if not os.path.isfile(output_aac) or os.path.getsize(output_aac) < 7:
                raise ConanException(
                    "upstream aac-enc example did not produce an ADTS AAC frame"
                )

    def package(self):
        autotools = Autotools(self)
        autotools.install()
        copy(
            self,
            "COPYING",
            src=self.source_folder,
            dst=os.path.join(self.package_folder, "licenses"),
        )

    def package_info(self):
        self.cpp_info.libs = ["vo-aacenc"]
        self.cpp_info.set_property("pkg_config_name", "vo-aacenc")
