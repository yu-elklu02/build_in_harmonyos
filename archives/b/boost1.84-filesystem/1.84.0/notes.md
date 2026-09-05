# Boost.Filesystem 1.84.0 HarmonyOS adaptation

Boost.Build executes shell probes that are incompatible with the OHOS target.
This recipe compiles Boost.Filesystem's upstream source files directly and
archives them as `libboost_filesystem.a`.

The consumer test creates a directory, writes a file, queries its size and
iterates the directory through Boost.Filesystem APIs.
