# audiofile 0.3.6

`audiofile` is an Autotools C/C++ library for common audio file formats.

The recipe deliberately configures `--disable-flac`: FLAC is optional upstream
functionality and enabling it would require a separate packaged FLAC dependency.
The retained upstream suite contains 35 tests under `test/` and one
`libaudiofile/UnitTests` target, all invoked through `make check` in `build()`.

The consumer test writes a two-channel 16-bit WAV file through the public
`audiofile.h` API, reads it back, and checks its format, metadata, and samples.

HarmonyOS validation is pending. The bundled Autotools helper supplies the
cross-compilation host triplet; any device configure or test failure must be
recorded with its command and log evidence before changing this recipe.
