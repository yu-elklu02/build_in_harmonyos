# QuaZip 1.4 adaptation notes

## Build environment

- Target: OpenHarmony aarch64
- Build system: CMake
- Dependencies: qt5-qtbase/5.15.2 and zlib/1.3.1

## Adaptation

The upstream project uses find_package(Qt5 COMPONENTS Core). The recipe maps
the Conan Qt package to the upstream Qt5 CMake package name while preserving
the generated Qt component targets. Bzip2 support is disabled because it is not
needed for the upstream ZIP coverage.

CMakeDeps does not export the Qt5::moc executable target, so the recipe supplies
the Conan-provided moc path through CMAKE_AUTOMOC_EXECUTABLE.

The source recipe tries a checksum-verified proxy mirror before the canonical
GitHub release URL, because GitHub connectivity is intermittent on OHOS workers.

## Tests

The recipe enables and runs upstream qztest through CTest. The consumer test
creates a ZIP archive, writes an entry, reopens it and verifies the payload.
