# irrlicht 1.8.5

Irrlicht 1.8.5 is built with the upstream `source/Irrlicht/Makefile` targets
`sharedlib` and `staticlib`.

The upstream Linux Makefile branch links desktop X11/OpenGL libraries
unconditionally. OHOS validation uses a headless/null-device build instead:
the recipe injects `NO_IRR_COMPILE_WITH_*` macros for X11, SDL, framebuffer,
OpenGL/OpenGLES, Direct3D, Windows and OSX devices, and the patch removes the
Linux desktop X11/OpenGL link flags from the Makefile.

The test package compiles and executes a real Irrlicht smoke test. It creates
an `IrrlichtDevice` with `video::EDT_NULL`, checks that the device and video
driver are valid, and asserts that the driver type remains `video::EDT_NULL`.

W0 dependency preflight passed for `zlib/1.3.2`, `libpng/1.6.58`,
`libjpeg/10`, and `bzip2/1.0.8`; the actual build graph is aligned to
`zlib/1.3.1.1` because `libpng/1.6.58` depends on that revision. `irrlicht/1.8.5`
is not occupied in `ohpcd`.
