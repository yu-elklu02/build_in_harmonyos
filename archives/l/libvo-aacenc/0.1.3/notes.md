# libvo-aacenc 0.1.3

## OpenHarmony adaptation

- Build system: autotools
- Target: OpenHarmony armv8
- Library type: static (`--disable-shared --enable-static`)
- Patches: make configure temporary directories group-readable and recognize
  OpenHarmony target triplets in `config.guess` and `config.sub`.

## Test coverage

The upstream release has no standalone unit-test suite; `make check` is an
empty automake target. The recipe enables upstream's `aac-enc` example and
runs it against one generated 44.1 kHz mono PCM WAV frame. It succeeds only
when the encoder produces a non-empty AAC output file.

`test_package` independently initializes the public API, configures AAC-LC
encoding, submits 1024 silent PCM samples, and verifies that the returned
output is a non-empty ADTS frame.
