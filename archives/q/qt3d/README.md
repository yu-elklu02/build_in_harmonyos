# Qt3D

Qt3D provides Qt 5 APIs for 3D scene graphs, rendering, input, logic and animation.

## OpenHarmony adaptation

- Uses the Qt 5.15.2 installation at `/storage/Users/currentUser/usr/local/Qt5`.
- Builds the Core, Render, Input, Logic, Animation and Extras modules with qmake.
- Builds Quick3D modules only when the Qt installation provides Qt Quick dependencies.
- Packages headers and shared libraries for Conan consumers.
