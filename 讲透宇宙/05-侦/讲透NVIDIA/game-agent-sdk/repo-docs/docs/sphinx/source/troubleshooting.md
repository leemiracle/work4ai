# Troubleshooting

## Profiling with Tracy

The Game Agent SDK is instrumented with [Tracy](https://github.com/wolfpld/tracy) profiling zones at every public API entry point. Instrumentation is gated behind the `TRACY_ENABLE` compile-time define and compiles to nothing by default, so there is no runtime cost in standard builds.

To build with profiling enabled, add `TRACY_ENABLE=1` to the preprocessor defines for the `ACE.SDK` project. The simplest way is to extend the project block in `premake.lua`:

```
defines { "TRACY_ENABLE=1" }
```

Then rebuild from scratch with `setup.bat` followed by `build.bat`. Both the SDK and any sample that links against it will now emit Tracy zones at runtime.

The Tracy profiler GUI is not bundled with the release. Three ways to obtain it:

- Download a prebuilt release from the [Tracy releases page](https://github.com/wolfpld/tracy/releases). Pick the version that matches the Tracy client library pinned by the SDK (currently 0.12.2; see `THIRD-PARTY-LICENSES.md`).
- Build from source. The full Tracy source tree is included under `external/tracy/`, including the `profiler/` subdirectory.
- Install via a package manager (for example `vcpkg install tracy`, or `winget`).

Launch the rebuilt sample, then launch the Tracy profiler GUI and connect to the local process. Named zones from every SDK API entry point appear in the timeline.