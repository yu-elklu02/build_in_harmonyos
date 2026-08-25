# audiowmark 0.6.5

Audiowmark is built with its Autotools project and packages the `audiowmark`
command-line tool. FFTW, libsndfile, libgcrypt, libzita-resampler, and mpg123
are supplied by Conan. Automake and Libtool are Conan build requirements for
`autoreconf`. FFmpeg/HLS and documentation are disabled because they are optional.

On OHOS, the generated `configure` script must be explicitly invoked with the
profile-provided `CONFIG_SHELL`, because the kernel does not execute scripts
through their shebang.

OHOS armv8 validation is pending:

```bash
conan create archives/a/audiowmark/0.6.5 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
