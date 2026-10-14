# xcalc 1.1.3

XCalc is an X11 Athena-widget scientific calculator. The recipe uses the
upstream autotools build and disables documentation generation. Runtime GUI
interaction requires an X server, which is unavailable in the headless OHOS
build worker; the test package therefore verifies the installed executable and
its ELF dependencies.

## Verification

- Target: HarmonyOS armv8
- Build: autotools configure, make, and make install
- Consumer test: confirms `bin/xcalc` is installed and executable
- Upstream GUI tests: not run because they require an X server
