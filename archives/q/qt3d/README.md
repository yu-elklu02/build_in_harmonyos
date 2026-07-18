# Qt3D

Qt3D provides Qt 5 APIs for 3D scene graphs, rendering, input, logic and animation.

## OpenHarmony adaptation

- Uses qmake, headers and libraries from the `qt5-qtbase/5.15.2` Conan dependency.
- Builds the Core, Render, Input, Logic, Animation and Extras modules with qmake.
- Builds Quick3D modules only when the Qt installation provides Qt Quick dependencies.
- Packages headers and shared libraries for Conan consumers.
