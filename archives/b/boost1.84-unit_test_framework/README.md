# boost1.84-unit_test_framework

Boost.Test 1.84.0 `unit_test_framework` static library for OpenHarmony.

The recipe manually compiles the 19 Boost.Test implementation translation units
because Boost.Build is not usable in the OHOS build environment. It installs the
complete Boost header tree and exports `Boost::unit_test_framework`.
