# Avida 2.12.4

The official release archive from SourceForge is required because the GitHub tag
uses submodules and its generated tarball omits `avida-core`.

The command-line interface is built with the ncurses viewer disabled. The bundled
`tcmalloc-1.4` component is disabled for OHOS armv8 because its implementation
contains x86-specific assembly.

Run device validation with:

```bash
conan create archives/a/avida/2.12.4 \
  -pr:h ci/conan/profiles/ohos-aarch64 \
  -pr:b ci/conan/profiles/ohos-aarch64 \
  -r=ohpcd --build=missing
```
