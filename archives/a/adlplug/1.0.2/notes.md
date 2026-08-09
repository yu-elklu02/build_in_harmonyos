# ADLplug 1.0.2

ADLplug is a JUCE-based VST/LV2 synthesizer plugin. OpenHarmony PC does not
provide the desktop plugin host stack used by the upstream frontends, so this
recipe builds the upstream `ADLplug_core` target only. The core retains the
ADLMIDI synthesis engine and is tested through its `Player` API.

HarmonyOS PC real-device validation passed: the package built successfully and
the `test_package` Player API test passed 1/1.

The upstream release uses five pinned Git submodules. Their exact archives and
SHA256 values are declared in `conandata.yml`; no mutable branch clone is used
during the Conan build.
