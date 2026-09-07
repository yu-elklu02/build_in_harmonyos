# Boost.Filesystem 1.84.0 HarmonyOS adaptation

Boost.Build executes shell probes that are incompatible with the OHOS target.
This recipe compiles Boost.Filesystem's upstream source files directly and
archives them as `libboost_filesystem.a`.

The consumer test creates a directory, writes a file, queries its size and
iterates the directory through Boost.Filesystem APIs.

The upstream test sweep records 12 passing targets and 4 explicit OHOS
skips. The skipped targets depend on Windows long-path semantics, HMDFS hard
links, root-directory permissions, or a libc++ overload boundary that is not
equivalent on OHOS. The `copy_test` compile path uses
`BOOST_SP_NO_PTHREAD_SETCANCELSTATE`, the Boost-supported fallback for the
pthread cancellation APIs absent from OHOS musl.
