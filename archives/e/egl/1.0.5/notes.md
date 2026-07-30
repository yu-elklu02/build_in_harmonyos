# egl 1.0.5 OHOS 适配笔记

## 上游与平台现状
- 上游 v1.0.5 后端:WGL(Windows)/GLX+X11(Linux)/Wayland+GLX,可选 GLES 转发(egl_linux_gles.cpp)。
- 上游 `include/EGL/eglctxinternals.h` 与 `src/egl_internal.h` 的平台 `#if` 仅覆盖 `_WIN32` / `WL_EGL_PLATFORM` / `USE_X11` / `__unix__`,**OHOS 落入空白分支**:
  - `egl_internal.h` 末尾有 `#else #error "Platform not recognized"`,会直接编译失败 → 补丁新增 OHOS 分支。
  - `eglctxinternals.h` 末尾仅 `#endif`(无 #error),OHOS 落入空白 → `EGLContextInternals` 结构不存在 → 补丁新增 OHOS 分支(虽然 OHOS 后端未直接用此结构,但其他平台无关文件可能引用)。
- OHOS 真机库:`/system/lib64/libEGL.so`、`/system/lib64/libEGL_mesa.so`、`/system/lib64/libGLESv3.so`(**无 libGLESv2.so**)。
  → `egl_ohos.cpp` 只 dlopen `libEGL.so`,ES 调用由系统 EGL 内部统一转发(系统 EGL 已支持 ES context)。

## 补丁设计(0001-add-ohos-system-egl-pbuffer-backend.patch)
单补丁覆盖 4 处改动:
1. **`CMakeLists.txt`**:新增 `elseif(CMAKE_SYSTEM_NAME STREQUAL "OHOS")` 分支
   - `EGL_PLATFORM_SOURCES = src/egl_ohos.cpp`
   - `target_link_libraries(EGL PUBLIC ${CMAKE_DL_LIBS})`
   - 不 `find_package(X11/OpenGL/Vulkan/Wayland)`
   - 在 `add_subdirectory(examples)` 外包 `if(NOT CMAKE_SYSTEM_NAME STREQUAL "OHOS")` 跳过 examples
2. **`src/egl_internal.h`**:新增 `#elif defined(__OHOS__)` 分支
   - 定义 `NativeBackend { EGL_BACKEND_OHOS = 0 }`、`NativeSurfaceContainer`、`NativeContextContainer`、`NativeLocalStorageContainer`、`NativePbufferType`(用系统 EGLSurface/EGLContext 存转发指针)
   - 定义 `__getDefaultNativeDisplay` / `__matchPlatformDisplay`(OHOS 无原生 display token,返回 EGL_DEFAULT_DISPLAY / 仅接受 EGL_PLATFORM_DEVICE_EXT)
3. **`include/EGL/eglctxinternals.h`**:新增 `#elif defined(__OHOS__)` 分支,定义最小 `_EGLContextInternals`(display/surface/context 三 void*)
4. **新增 `src/egl_ohos.cpp`**:实现全部 `_egl*` 后端函数,模式参考 `egl_x11_glx.cpp` + `egl_linux_gles.cpp`:
   - `__internalInit`:`dlopen("libEGL.so")`,dlsym 全部系统 EGL 入口
   - `_eglInitialize` → 系统 `eglInitialize`;`_eglGetDisplay` → 系统 `eglGetDisplay(EGL_DEFAULT_DISPLAY)`
   - `_eglChooseConfig` / `_eglGetConfigAttrib` / `_eglGetConfigs`:转发系统 EGL,枚举系统 config
   - `_eglCreatePbufferSurface`:转发系统 `eglCreatePbufferSurface`(OHOS 真机 EGL 1.4 拒 ≥2px pbuffer,仅 1×1 可创建,test 用最小可用尺寸)
   - `_eglCreateContext`:`eglBindAPI(EGL_OPENGL_ES_API)` 后 `eglCreateContext`(ES3 context)
   - `_eglMakeCurrent` / `_eglSwapBuffers` / `_eglDestroySurface` / `_eglDestroyContext` / `_eglTerminate`:转发
   - `_eglGetProcAddress` → `__getProcAddress`:先系统 `eglGetProcAddress`,失败再 `dlsym(libEGL, name)`
   - **`_eglCreateWindowSurface` / `_eglCreatePixmapSurface` / `_eglCopyBuffers`**:OHOS 无原生窗口系统,返回 `EGL_FALSE` 并置 `EGL_BAD_MATCH` / `EGL_BAD_NATIVE_PIXMAP`,**不假装支持**
   - 资源释放:`_eglTerminate` 调系统 `eglTerminate` 并 `dlclose`

## test_package 真机验证
`test_package/test.cpp` 真实运行 EGL 生命周期(参考 `egl_linux_gles.cpp` 的 chooseDefaultConfig 模式):
`eglGetDisplay(EGL_DEFAULT_DISPLAY)` → `eglInitialize` → `eglBindAPI(EGL_OPENGL_ES_API)` →
`eglChooseConfig`(EGL_SURFACE_TYPE+EGL_PBUFFER_BIT, EGL_RENDERABLE_TYPE+EGL_OPENGL_ES3_BIT, RGBA888, NONE) →
`eglCreatePbufferSurface`(1×1,OHOS 真机 EGL 1.4 �拒 ≥2px) → `eglCreateContext`(ES3, context_major_version=3) →
`eglMakeCurrent` → `eglGetProcAddress("glGetString")`(非 NULL) →
`eglMakeCurrent(EGL_NO_DISPLAY, EGL_NO_SURFACE, EGL_NO_SURFACE, EGL_NO_CONTEXT)` 解绑 →
`eglDestroyContext` / `eglDestroySurface` / `eglTerminate`。每步失败即 abort 并报告 EGL error。

## 验证命令
```
python3 scripts/ohc-run.py submit --check egl 1.0.5
python3 scripts/ohc-run.py conan-verify egl 1.0.5
bash ci/conan/build_and_test.sh egl/1.0.5
```
