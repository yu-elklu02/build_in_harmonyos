# E254 draft: Java/Ant source package toolchain prerequisite

## Error signature

```text
ant: inaccessible or not found
java: not found
javac: not found
```

## Root cause

Java source packages that build upstream JARs with Ant require a Java build
toolchain on the OHOS builder. A Conan recipe can correctly download and export
the package, but it cannot run `ant jar` or `ant test` when `java`, `javac`, and
`ant` are absent from the environment.

## Recommended handling

1. Check `command -v java`, `command -v javac`, and `command -v ant` before
   treating a Java/Ant package as a normal passing source-build adaptation.
2. If the tools are missing, document the result as a blocked Java/Ant toolchain
   prerequisite or as a Path B knowledge extension.
3. Do not claim upstream Ant tests passed unless `ant test` actually ran.
4. If using a prebuilt JAR instead, treat that as a separate recipe design:
   download a verifiable JAR, check SHA256, package it, and run a real Java
   functional test.

## Source event

xom/1.4.4 OHOS validation reached `build()` and failed at the missing Java/Ant
toolchain boundary after recipe-side fixes for codeload URL, `package_type`, and
explicit archive filename.
