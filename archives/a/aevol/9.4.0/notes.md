# aevol 9.4.0

The recipe builds the upstream `aevol-9.4.0` branch with CMake and clang. OpenMP is disabled on OHOS because the target profile does not provide an OpenMP runtime. The two upstream CMake FetchContent dependencies are downloaded and hashed by Conan during `source()` so the build does not perform network access from the CMake configure step.

Upstream tests are run by `cmake --build . --target all-with-gtests` followed by `ctest --output-on-failure`. The source registers 76 upstream test items: 4 example-parameter CTest cases, 2 CTest build/data-generation gates, and 70 GoogleTest cases. The final pass count and device-specific constraints must be updated from the AtomCode real-device result before the formal branch is pushed.
