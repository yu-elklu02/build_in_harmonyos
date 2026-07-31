# xom 1.4.4 OpenHarmony Adaptation

- Uses the official XOM 1.4.4 source archive from GitHub.
- Uses the codeload.github.com tarball endpoint because the device can fetch
  archive bytes from codeload while github.com tag archive URLs may time out.
- Treats the package as a Java application-style artifact, not a native Conan
  library, so `package_type = "application"` is used.
- Passes an explicit `filename` to `get()` because the codeload URL basename
  does not include `.tar.gz`.
- Builds the upstream JAR with Ant.
- Runs the upstream Ant test target during package build.
- The consumer test compiles and runs a small Java program against the packaged JAR.

## Path B knowledge extension

XOM is a Java/Ant source package. It is useful as a Java adaptation knowledge
case because the recipe can be made structurally correct, but the real build is
blocked if the OHOS builder has no Java toolchain.

Observed device blocker:

```text
ant: inaccessible or not found
java: not found
javac: not found
```

Conclusion:

- Java source packages built by Ant require `java`, `javac`, and `ant` in the
  build environment.
- If CI does not provide JDK + Ant, this class of package should not be reported
  as a normal passing Path A adaptation.
- A prebuilt JAR recipe is a different design and must use a verifiable upstream
  binary URL and SHA256, with test_package executing a real Java API/function
  check.
