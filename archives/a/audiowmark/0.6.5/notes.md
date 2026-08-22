# audiowmark 0.6.5

Audiowmark is built with its Autotools project and packages the `audiowmark`
command-line tool. FFTW, libsndfile, libgcrypt, and mpg123 are supplied by
Conan. FFmpeg/HLS and documentation are disabled because they are optional.

OHOS armv8 validation is pending:

```bash
conan create archives/a/audiowmark/0.6.5 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
