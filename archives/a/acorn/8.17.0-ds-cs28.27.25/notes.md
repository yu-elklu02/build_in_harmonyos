# acorn 8.17.0-ds-cs28.27.25

This is Debian's repackaged source for Acorn 8.17.0 and its component sources.
The Conan version normalizes Debian's `+ds+~cs28.27.25` syntax because the
Conan registry rejects that version syntax.

The upstream test runner loads 35 parser test suites through `npm run test`.
The consumer test invokes the packaged CLI, parses JavaScript, and validates
the JSON AST structure.

The initial HarmonyOS adaptation is restricted to armv8. True-device validation
is required before changing this package's status from `draft`.
