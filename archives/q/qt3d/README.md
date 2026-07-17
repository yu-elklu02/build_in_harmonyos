# Qt3D

Qt3D provides Qt 5 APIs for 3D scene graphs, rendering, input, logic and animation.

## OpenHarmony adaptation

- Detects qmake from the Worker PATH and queries its Qt 5 installation prefix.
- Builds the Core, Render, Input, Logic, Animation and Extras modules with qmake.
- Builds Quick3D modules only when the Qt installation provides Qt Quick dependencies.
- Packages headers and shared libraries for Conan consumers.
