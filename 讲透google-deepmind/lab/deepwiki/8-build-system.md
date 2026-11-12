<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/lab · page 8 Build System · fetched 2026-10-26 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/precommit.yml](.github/workflows/precommit.yml)
- [.precommit.bazelrc](.precommit.bazelrc)
- [BUILD](BUILD)
- [WORKSPACE](WORKSPACE)
- [bazel/dm_env.BUILD](bazel/dm_env.BUILD)
- [bazel/pybind11.BUILD](bazel/pybind11.BUILD)
- [bazel/tree.BUILD](bazel/tree.BUILD)
- [docs/users/build.md](docs/users/build.md)
- [public/dmlab_connect_test.cc](public/dmlab_connect_test.cc)
- [python/tests/BUILD](python/tests/BUILD)
- [python/tests/utils/BUILD](python/tests/utils/BUILD)
- [python_system.bzl](python_system.bzl)

</details>



DeepMind Lab uses the [Bazel](https://bazel.build/) build system to manage its compilation, testing, and packaging processes. This document provides a comprehensive overview of the build system architecture, key build targets, dependency management, and configuration options. For information about getting started with building DeepMind Lab, see [Getting Started](#2).

## Build System Architecture

DeepMind Lab's build system is based on Bazel, which provides a structured and reproducible build environment. The system is organized around several key files:

- **WORKSPACE**: Defines external dependencies
- **BUILD**: Defines build targets and rules
- **.precommit.bazelrc**: Contains common build configurations
- Various subdirectory BUILD files: Define component-specific targets

### High-Level Build Architecture

```mermaid
graph TD
    Bazel["Bazel Build Tool"] -->|reads| WORKSPACE["WORKSPACE File"]
    Bazel -->|reads| BUILD["BUILD Files"]
    Bazel -->|uses| BazelRC[".precommit.bazelrc"]
    
    WORKSPACE -->|defines| ExternalDeps["External Dependencies"]
    BUILD -->|defines| BuildTargets["Build Targets"]
    BazelRC -->|defines| BuildOpts["Build Options"]
    
    ExternalDeps -->|includes| ThirdParty["Third-Party Libraries"]
    BuildTargets -->|produces| Binaries["Binaries"]
    BuildTargets -->|produces| Libraries["Libraries"]
    BuildTargets -->|produces| Assets["Game Assets"]
    BuildTargets -->|produces| Tests["Tests"]
    
    Binaries -->|includes| GameBin["game"]
    Binaries -->|includes| PythonMod["deepmind_lab.so"]
    Libraries -->|supports| GameBin
    Libraries -->|supports| PythonMod
    Assets -->|used by| GameBin
    Assets -->|used by| PythonMod
    Tests -->|validates| GameBin
    Tests -->|validates| PythonMod
```

Sources: [WORKSPACE](), [BUILD](), [.precommit.bazelrc](), [docs/users/build.md]()

## Key Build Targets

DeepMind Lab's main BUILD file defines several critical targets that produce the primary artifacts of the system.

### Core Libraries

```mermaid
graph TD
    GameLibs["Game Libraries"] -->|includes| SDL["game_lib_sdl"]
    GameLibs -->|includes| OSMesa["game_lib_headless_osmesa"]
    GameLibs -->|includes| GLX["game_lib_headless_glx"]
    GameLibs -->|includes| EGL["game_lib_headless_egl"]
    
    SDL -->|supports| GameBin["game binary"]
    OSMesa -->|renderer for| HeadlessSW["libdmlab_headless_sw.so"]
    GLX -->|renderer for| HeadlessHW["libdmlab_headless_hw.so"]
    EGL -->|renderer for| HeadlessHW
    
    HeadlessSW -->|loaded by| SOLoader["dmlab_so_loader"]
    HeadlessHW -->|loaded by| SOLoader
    SOLoader -->|supports| PythonLib["deepmind_lab.so"]
```

The core libraries provide different rendering backends:

- **game_lib_sdl**: For windowed operation with SDL
- **game_lib_headless_osmesa**: Software-based headless rendering
- **game_lib_headless_glx**: Hardware-accelerated headless rendering using GLX
- **game_lib_headless_egl**: Hardware-accelerated headless rendering using EGL

Sources: [BUILD:802-892]()

### Main Executables

The key executable targets include:

- **game**: The main game binary for interactive use
- **deepmind_lab.so**: Python module that provides API access
- **python_random_agent**: Example agent that interacts with the environment

```bash
# Build the Python module
bazel build -c opt //:deepmind_lab.so

# Build and run the game
bazel build -c opt //:game
bazel run -c opt //:game

# Run an example random agent
bazel run -c opt //:python_random_agent
```

Sources: [BUILD:907-914](), [BUILD:1012-1033](), [BUILD:1047-1052]()

### Game Assets

DeepMind Lab packages various assets required by the game:

```mermaid
graph TD
    Assets["Game Assets"] -->|includes| NonPK3["non_pk3_assets"]
    Assets -->|includes| GameScripts["game_script_assets"]
    Assets -->|includes| BuiltMaps["built_maps"]
    Assets -->|includes| AssetsPK3["assets_pk3"]
    Assets -->|includes| AssetsOAPK3["assets_oa_pk3"]
    Assets -->|includes| AssetsBotsPK3["assets_bots_pk3"]
    Assets -->|includes| VMPK3["vm_pk3"]
    
    NonPK3 -->|contains| ConfigFiles["Configuration Files"]
    GameScripts -->|contains| LuaScripts["Lua Scripts"]
    BuiltMaps -->|contains| Maps[".bsp and .aas Files"]
    AssetsPK3 -->|contains| Models["Models, Textures, Shaders"]
    AssetsOAPK3 -->|contains| Shaders["OpenArena Shaders"]
    AssetsBotsPK3 -->|contains| BotFiles["Bot Definition Files"]
    VMPK3 -->|contains| QVMs["Quake Virtual Machines"]
    
    QVMs -->|includes| CGAME["cgame.qvm"]
    QVMs -->|includes| QAGAME["qagame.qvm"]
    QVMs -->|includes| Q3UI["ui.qvm"]
```

Sources: [BUILD:659-799]()

## Dependency Management

DeepMind Lab uses Bazel's dependency management system to handle both external and internal dependencies.

### External Dependencies

The WORKSPACE file defines external dependencies including:

- **Google Libraries**: GoogleTest, Abseil
- **Graphics Libraries**: SDL, OpenGL/EGL/OSMesa
- **Compression Libraries**: zlib, JPEG, PNG
- **Scripting**: Lua
- **Python**: Python bindings and libraries (numpy, six, etc.)

```
http_archive(
    name = "com_google_googletest",
    strip_prefix = "googletest-main",
    urls = ["https://github.com/google/googletest/archive/main.zip"],
)
```

Sources: [WORKSPACE:6-10](), [WORKSPACE:12-153]()

### Python Dependencies

Python dependencies are handled specially since they need to interact with the system's Python installation:

```mermaid
graph TD
    PythonRepo["python_repo rule"] -->|creates| PythonSystem["@python_system"]
    PythonSystem -->|provides| PyHeaders["python_headers"]
    PythonSystem -->|links to| SystemPython["System Python Installation"]
    PythonSystem -->|links to| NumPy["System NumPy Installation"]
    
    PyHeaders -->|used by| DeepMindLabSO["deepmind_lab.so"]
    DeepMindLabSO -->|Python module| PyAPI["Python API"]
```

The WORKSPACE uses a custom repository rule (`python_repo`) to locate system Python installations and NumPy libraries.

Sources: [WORKSPACE:162-165](), [python_system.bzl]()

## Build Configuration

DeepMind Lab provides several build configuration options to customize the build process.

### Rendering Backends

The build system supports multiple rendering backends through configuration settings:

```
config_setting(
    name = "dmlab_graphics_sdl",
    define_values = {"graphics": "sdl"},
)

config_setting(
    name = "dmlab_graphics_osmesa_or_glx",
    define_values = {"graphics": "osmesa_or_glx"},
)

config_setting(
    name = "dmlab_graphics_osmesa_or_egl",
    define_values = {"graphics": "osmesa_or_egl"},
)
```

These can be selected at build time using `--define graphics=...` flags.

Sources: [BUILD:937-950]()

### Platform Detection

The build system uses configuration settings to detect the underlying platform:

```
config_setting(
    name = "is_linux",
    constraint_values = ["@platforms//os:linux"],
)

config_setting(
    name = "is_macos",
    constraint_values = ["@platforms//os:macos"],
)
```

Sources: [BUILD:9-17]()

### C++ Standard

The build system uses C++17 as specified in the .precommit.bazelrc file:

```
build --cxxopt=-std=c++17
```

Sources: [.precommit.bazelrc:6]()

## Quake Virtual Machine (QVM) Compilation

DeepMind Lab is built on the Quake III Arena engine, which uses Quake Virtual Machines (QVMs) for game logic. The build system includes a multi-step process to compile these components:

```mermaid
graph TD
    QVMSrc["QVM Source (.c)"] -->|compiled by| Q3LCC["q3lcc Compiler"]
    Q3LCC -->|produces| QVMAsm[".asm Files"]
    QVMAsm -->|assembled by| Q3ASM["q3asm Assembler"]
    Q3ASM -->|produces| QVMFiles[".qvm Files"]
    
    QVMFiles -->|packaged into| VMPK3["vm.pk3"]
    VMPK3 -->|used by| GameEngine["Game Engine"]
    
    Q3LCC -->|uses| Q3CPP["q3cpp Preprocessor"]
    Q3LCC -->|uses| Q3RCC["q3rcc Compiler"]
```

Sources: [BUILD:45-60](), [BUILD:80-113](), [BUILD:239-254](), [BUILD:411-442]()

## Testing Framework

DeepMind Lab includes comprehensive testing capabilities:

- **Python Module Tests**: Validate the Python bindings functionality
- **Level Load Tests**: Ensure levels can load correctly
- **Seed Tests**: Verify deterministic behavior with fixed seeds

```bash
# Run all tests
bazel test -c opt //...

# Run a specific test
bazel test -c opt //python/tests:python_module_test
```

Sources: [python/tests/BUILD](), [BUILD:1072-1115]()

## Build Artifacts

When built, DeepMind Lab produces several key artifacts:

| Artifact | Description | Build Command |
|----------|-------------|--------------|
| `deepmind_lab.so` | Python module for agent integration | `bazel build -c opt //:deepmind_lab.so` |
| `game` | Interactive game binary | `bazel build -c opt //:game` |
| `python_random_agent` | Example agent implementation | `bazel build -c opt //:python_random_agent` |
| `libdmlab_headless_hw.so` | Headless hardware-accelerated library | `bazel build -c opt //:libdmlab_headless_hw.so` |
| `libdmlab_headless_sw.so` | Headless software-rendered library | `bazel build -c opt //:libdmlab_headless_sw.so` |

Sources: [BUILD:952-975](), [BUILD:907-914](), [BUILD:1012-1033]()

## GitHub CI Integration

DeepMind Lab includes GitHub Actions workflow configurations for continuous integration:

```mermaid
graph TD
    GitHubAction[".github/workflows/precommit.yml"] -->|defines| CIJobs["CI Jobs"]
    CIJobs -->|runs| Builds["Builds"]
    CIJobs -->|runs| Tests["Tests"]
    
    Builds -->|uses| Configurations["Matrix of Configurations"]
    Configurations -->|includes| GCC["GCC"]
    Configurations -->|includes| LLVM["LLVM+libstdc++"]
    Configurations -->|includes| LLVMlibcpp["LLVM+libc++"]
    
    Tests -->|includes| CoreTests["Core Tests"]
    Tests -->|includes| PythonModuleTest["Python Module Test"]
    Tests -->|includes| DMEnvTest["DMEnv Module Test"]
    Tests -->|includes| RandomAgent["Random Agent"]
```

Sources: [.github/workflows/precommit.yml]()

## Related Systems

For more information on related systems, see:

- [Python API](#3) for details on the Python interface
- [Lua Scripting](#5) for level scripting capabilities
- [Level Generation](#6) for creating and customizing levels
- [Observations and Actions](#7) for agent interfaces

---

