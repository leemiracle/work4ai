<!-- source: DeepWiki mcp.deepwiki.com · repo pytorch/rl · page 12 Development and Deployment · fetched 2026-10-21 -->

# Development and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/RELEASE_AGENT_PROMPT.md](.github/RELEASE_AGENT_PROMPT.md)
- [.github/scripts/ci_timing_dashboard.html](.github/scripts/ci_timing_dashboard.html)
- [.github/scripts/pre-build-script-win.sh](.github/scripts/pre-build-script-win.sh)
- [.github/scripts/pre-build-script.sh](.github/scripts/pre-build-script.sh)
- [.github/scripts/td_script.sh](.github/scripts/td_script.sh)
- [.github/scripts/track_ci_timing.py](.github/scripts/track_ci_timing.py)
- [.github/scripts/version_script.bat](.github/scripts/version_script.bat)
- [.github/unittest/examples/scripts/run_all.sh](.github/unittest/examples/scripts/run_all.sh)
- [.github/unittest/examples/scripts/run_test.sh](.github/unittest/examples/scripts/run_test.sh)
- [.github/unittest/linux_olddeps/scripts_gym_0_13/install.sh](.github/unittest/linux_olddeps/scripts_gym_0_13/install.sh)
- [.github/workflows/build-wheels-aarch64-linux.yml](.github/workflows/build-wheels-aarch64-linux.yml)
- [.github/workflows/build-wheels-linux.yml](.github/workflows/build-wheels-linux.yml)
- [.github/workflows/build-wheels-m1.yml](.github/workflows/build-wheels-m1.yml)
- [.github/workflows/build-wheels-windows.yml](.github/workflows/build-wheels-windows.yml)
- [.github/workflows/ci-timing-tracker.yml](.github/workflows/ci-timing-tracker.yml)
- [.github/workflows/release.yml](.github/workflows/release.yml)
- [.python-version](.python-version)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [examples/collectors/collector_device.py](examples/collectors/collector_device.py)
- [pyproject.toml](pyproject.toml)
- [setup.py](setup.py)
- [sota-check/run_rnd_mujoco.sh](sota-check/run_rnd_mujoco.sh)
- [sota-implementations/rnd/config_mujoco.yaml](sota-implementations/rnd/config_mujoco.yaml)
- [sota-implementations/rnd/utils_mujoco.py](sota-implementations/rnd/utils_mujoco.py)
- [tutorials/sphinx-tutorials/memory_efficient_rl.py](tutorials/sphinx-tutorials/memory_efficient_rl.py)
- [version.txt](version.txt)

</details>



This document describes the build system, continuous integration/deployment pipelines, and documentation infrastructure for TorchRL. It covers how the library is built from source, packaged into distributable wheels, and how documentation is generated and deployed.

For information about using the high-level Trainer system for RL experiments, see [Training Infrastructure](#8). For details on the core library architecture, see [Overview](#1).

---

## Overview

TorchRL's development infrastructure consists of four main components:

1.  **Build System**: Python package setup with C++ extension compilation
2.  **CI/CD Pipelines**: Automated wheel building for multiple platforms
3.  **Documentation System**: Sphinx-based documentation with automated deployment
4.  **Testing Infrastructure**: Smoke tests and validation scripts

The build system compiles C++ extensions using PyTorch's build utilities, while CI/CD workflows handle cross-platform distribution. Documentation is generated from docstrings and RST files, then deployed to GitHub Pages.

---

## Build System Architecture

### Setup Configuration

The build system is defined in [setup.py:1-434](), which uses PyTorch's `torch.utils.cpp_extension` module to compile C++ extensions with platform-specific compiler flags. The `pyproject.toml` file also defines build system requirements and project metadata [pyproject.toml:1-270]().

```mermaid
graph TB
    subgraph "Build Entry Point"
        main["main()<br/>(setup.py:300)"]
        setup["setup()<br/>(setuptools)"]
    end

    subgraph "Extension Configuration"
        get_ext["get_extensions()<br/>(setup.py:200)"]
        platform_check{"Platform?"}
        win_flags["Windows MSVC Flags<br/>/O2, /std:c++17, /EHsc<br/>(setup.py:229-235)"]
        unix_flags["Unix GCC/Clang Flags<br/>-O3, -std=c++17<br/>(setup.py:248-254)"]
        cxx20_flag["_get_cxx20_compatibility_flag()<br/>(setup.py:104)"]
    end

    subgraph "Source Files"
        cpp_files["*.cpp files<br/>torchrl/csrc/<br/>(setup.py:273)"]
        include_dirs["Include Directories<br/>. and PYTHON_INCLUDE_DIR<br/>(setup.py:276-279)"]
    end

    subgraph "Build Process"
        cpp_ext["CppExtension<br/>torchrl._torchrl<br/>(setup.py:282-288)"]
        build_ext["BuildExtension<br/>(torch.utils)<br/>(setup.py:298)"]
    end

    main --> get_ext
    main --> setup
    get_ext --> platform_check
    platform_check -->|"sys.platform == win32"| win_flags
    platform_check -->|"Unix-like"| unix_flags
    get_ext --> cpp_files
    get_ext --> include_dirs
    win_flags --> cpp_ext
    unix_flags --> cpp_ext
    cxx20_flag --> cpp_ext
    cpp_files --> cpp_ext
    include_dirs --> cpp_ext
    cpp_ext --> build_ext
    build_ext --> setup
```

**Sources**: [setup.py:1-434](), [pyproject.toml:1-270]()

### Compiler Configuration

The build system adapts to different platforms with specific compiler flags. It also checks for `pybind11` installation [setup.py:31-49]() and handles stale builds due to PyTorch/Python version changes [setup.py:145-191]().

| Platform | Compiler | Optimization | C++ Standard | Special Flags |
|----------|----------|--------------|--------------|---------------|
| Windows | MSVC | `/O2` | `/std:c++17` | `/EHsc` (exception handling) |
| Unix-like | GCC/Clang | `-O3` | `-std=c++17` | `-fdiagnostics-color=always`, `-std=c++2a` (if C++20 not available) |

Debug mode can be enabled via the `DEBUG=1` environment variable, which switches optimization levels to `/Od` (Windows) or `-O0` (Unix) and adds debugging symbols [setup.py:236-268](). CUDA extensions are built conditionally based on `CUDA_HOME` and `FORCE_CUDA` environment variables, and CUDA version compatibility with PyTorch [setup.py:54-95]().

**Sources**: [setup.py:31-49](), [setup.py:54-95](), [setup.py:104-131](), [setup.py:145-191](), [setup.py:229-268]()

### C++ Extension Build Process

```mermaid
graph LR
    subgraph "Input"
        csrc["torchrl/csrc/*.cpp<br/>(setup.py:273)"]
        headers["Include dirs: .<br/>PYTHON_INCLUDE_DIR<br/>(setup.py:276-279)"]
    end

    subgraph "Compilation"
        compile["Compile with<br/>extra_compile_args<br/>(setup.py:286)"]
        link["Link with<br/>extra_link_args<br/>(setup.py:287)"]
    end

    subgraph "Output"
        ext["torchrl._torchrl<br/>extension module<br/>(setup.py:283)"]
    end

    csrc --> compile
    headers --> compile
    compile --> link
    link --> ext
```

**Sources**: [setup.py:270-291]()

---

## Package Distribution

### Wheel Build Workflows

TorchRL maintains separate CI/CD workflows for building binary wheels across multiple platforms. These workflows are triggered by pushes to `nightly`, `main`, `release/*` branches, release candidate tags, pull requests, or manual `workflow_dispatch` events [build-wheels-linux.yml:3-14](), [build-wheels-aarch64-linux.yml:3-14](), [build-wheels-windows.yml:3-14](), [build-wheels-m1.yml:3-14]().

```mermaid
graph TB
    subgraph "Trigger Events"
        push["Push to branches:<br/>nightly, main, release/*"]
        tag["Release tags:<br/>v[0-9]+.[0-9]+.[0-9]+-rc[0-9]+"]
        pr["Pull requests"]
        manual["workflow_dispatch"]
    end

    subgraph "Linux Builds"
        linux["build-wheels-linux.yml"]
        linux_matrix["generate-matrix<br/>os: linux<br/>package-type: wheel"]
        linux_build["build_wheels_linux.yml<br/>pytorch/test-infra"]
    end

    subgraph "Aarch64 Builds"
        aarch64["build-wheels-aarch64-linux.yml"]
        aarch64_matrix["generate-matrix<br/>os: linux-aarch64<br/>with-cuda: disable"]
        aarch64_build["build_wheels_linux.yml<br/>architecture: aarch64"]
    end

    subgraph "Windows Builds"
        windows["build-wheels-windows.yml"]
        windows_matrix["generate-matrix<br/>os: windows"]
        windows_build["build_wheels_windows.yml<br/>env-script: version_script.bat"]
    end

    subgraph "M1 Builds"
        m1["build-wheels-m1.yml"]
        m1_matrix["generate-matrix<br/>os: macos-arm64"]
        m1_build["build_wheels_macos.yml<br/>runner: macos-m2-15"]
    end

    push --> linux
    push --> aarch64
    push --> windows
    push --> m1
    tag --> linux
    tag --> windows
    tag --> m1
    pr --> linux
    pr --> aarch64
    pr --> windows
    pr --> m1
    manual --> linux
    manual --> aarch64
    manual --> windows
    manual --> m1

    linux --> linux_matrix
    linux_matrix --> linux_build

    aarch64 --> aarch64_matrix
    aarch64_matrix --> aarch64_build

    windows --> windows_matrix
    windows_matrix --> windows_build

    m1 --> m1_matrix
    m1_matrix --> m1_build
```

**Sources**: [.github/workflows/build-wheels-linux.yml:3-14](), [.github/workflows/build-wheels-aarch64-linux.yml:3-14](), [.github/workflows/build-wheels-windows.yml:3-14](), [.github/workflows/build-wheels-m1.yml:3-14]()

### Build Matrix Configuration

Each platform workflow generates a build matrix specifying Python versions, CUDA versions (where applicable), and platform-specific settings. These matrices are generated by `pytorch/test-infra/.github/workflows/generate_binary_build_matrix.yml` [build-wheels-linux.yml:76](), [build-wheels-aarch64-linux.yml:76](), [build-wheels-windows.yml:66](), [build-wheels-m1.yml:56]().

| Workflow | OS | Python Versions | CUDA | ROCm | CPU | Special Configuration |
|----------|----|-----------------|------|------|-----|----------------------|
| `build-wheels-linux.yml` | `linux` | `["3.10", "3.11", "3.12", "3.13", "3.14"]` | `enable` | `disable` | `enable` | `env-var-script: .github/scripts/td_script.sh` |
| `build-wheels-aarch64-linux.yml` | `linux-aarch64` | `["3.10", "3.11", "3.12", "3.13", "3.14"]` | `disable` | `disable` | `enable` | `env-var-script: .github/scripts/td_script.sh` |
| `build-wheels-windows.yml` | `windows` | `["3.10", "3.11", "3.12", "3.13", "3.14"]` | `disable` | N/A | `enable` | `env-script: .github/scripts/version_script.bat`, `post-script: "python packaging/wheel/relocate.py"` |
| `build-wheels-m1.yml` | `macos-arm64` | `["3.10", "3.11", "3.12", "3.13", "3.14"]` | N/A | N/A | `enable` | `env-var-script: .github/scripts/td_script.sh`, `setup-miniconda: true` |

**Sources**: [.github/workflows/build-wheels-linux.yml:76-91](), [.github/workflows/build-wheels-aarch64-linux.yml:76-91](), [.github/workflows/build-wheels-windows.yml:66-80](), [.github/workflows/build-wheels-m1.yml:56-67]()

### Version Management

Version information is centralized and managed through multiple files. The `pyproject.toml` uses `setuptools_scm` for dynamic versioning, with a fallback to `0.14.0` [pyproject.toml:223-229]().

```mermaid
graph LR
    subgraph "Version Sources"
        version_txt["version.txt<br/>0.14.0"]
        td_script["td_script.sh<br/>TORCHRL_BUILD_VERSION=${BUILD_VERSION:-0.14.0}"]
        version_bat["version_script.bat<br/>TORCHRL_BUILD_VERSION=%BUILD_VERSION% or 0.14.0"]
        setuptools_scm["pyproject.toml<br/>dynamic = ['version']<br/>fallback_version = '0.14.0'"]
    end

    subgraph "Build Processes"
        linux["Linux/Aarch64<br/>Wheel Builds"]
        windows["Windows<br/>Wheel Builds"]
        m1["M1<br/>Wheel Builds"]
    end

    version_txt -.default.-> setuptools_scm
    td_script --> linux
    td_script --> m1
    version_bat --> windows
    setuptools_scm --> linux
    setuptools_scm --> windows
    setuptools_scm --> m1
```

**Sources**: [version.txt:1](), [.github/scripts/td_script.sh:3](), [.github/scripts/version_script.bat:2-6](), [pyproject.toml:223-229]()

### Pre-Build Dependencies

Each platform has specific pre-build scripts that install dependencies:

**Linux/macOS** ([.github/scripts/td_script.sh:1-51]()):
- Sets `TORCHRL_BUILD_VERSION` and strips `+cpu` suffix for PyPI compatibility.
- Upgrades `setuptools` and `packaging`.
- Installs `pybind11[global]`, `cloudpickle`, `importlib_metadata`, `numpy`, `orjson`, `pyvers`.
- Installs `tensordict` from PyPI (stable) for release branches/tags or from git (latest development) otherwise.
- Conditionally installs PyTorch if not already present or for smoke tests.

**Windows** ([.github/scripts/version_script.bat:1-79]()):
- Sets `TORCHRL_BUILD_VERSION` and strips `+cpu` suffix.
- Sets up MSVC environment using `vswhere.exe` to find `vcvarsall.bat`.
- Handles `VC_VERSION_LOWER`/`UPPER` based on `VC_YEAR`.
- Calls `vcvarsall.bat` for x64 architecture.
- Conditionally sets up Intel oneAPI for XPU builds.
- Sets `DISTUTILS_USE_SDK=1`.
- Upgrades `setuptools` to `72.1.0`.
- Workaround for free-threaded Python on Windows by copying `python3XXt.lib` to `python3XX.lib`.

**Sources**: [.github/scripts/td_script.sh:1-51](), [.github/scripts/version_script.bat:1-79](), [.github/scripts/pre-build-script.sh:1-8](), [.github/scripts/pre-build-script-win.sh:1-6]()

---

## Documentation System

### Sphinx Configuration

The documentation is built using Sphinx with the PyTorch theme. Configuration is centralized in `docs/source/conf.py`.

```mermaid
graph TB
    subgraph "Configuration"
        conf["conf.py<br/>Sphinx configuration"]
        project["Project: torchrl<br/>Theme: pytorch_sphinx_theme"]
        version_logic{"RL_SANITIZE_VERSION_STR_IN_DOCS?"}
        release_ver["Release version<br/>X.Y only"]
        main_ver["Main branch<br/>main (X.Y.Z)"]
    end

    subgraph "Extensions"
        autodoc["sphinx.ext.autodoc"]
        autosummary["sphinx.ext.autosummary"]
        napoleon["sphinx.ext.napoleon"]
        gallery["sphinx_gallery.gen_gallery"]
        myst["myst_parser"]
    end

    subgraph "Content Generation"
        kb_gen["generate_knowledge_base_references()"]
        tut_gen["generate_tutorial_references()"]
    end

    conf --> project
    project --> version_logic
    version_logic -->|"Set"| release_ver
    version_logic -->|"Unset"| main_ver

    conf --> autodoc
    conf --> autosummary
    conf --> napoleon
    conf --> gallery
    conf --> myst

    conf --> kb_gen
    conf --> tut_gen
```

**Sources**: `docs/source/conf.py`

### Documentation Build Workflow

The documentation build process is orchestrated by `.github/workflows/docs.yml`:

```mermaid
graph TB
    subgraph "Triggers"
        push_main["Push to:<br/>nightly, main, release/*"]
        tags["Tags:<br/>v[0-9]+.[0-9]+.[0-9]+"]
        pr["Pull requests"]
    end

    subgraph "Build Environment Setup"
        runner["Runner: linux.g5.4xlarge.nvidia.gpu"]
        yum_deps["Install system deps:<br/>Mesa, OpenGL, Xvfb"]
        conda["Install Miniconda<br/>Python 3.12"]
        pytorch["Install PyTorch<br/>+ tensordict"]
        torchrl["pip install -e .<br/>--no-build-isolation"]
        docs_deps["Install docs deps:<br/>requirements.txt"]
    end

    subgraph "Documentation Build"
        sanitize{"Release build?<br/>(docs.yml:94)"}
        set_env["Set RL_SANITIZE_VERSION_STR_IN_DOCS<br/>(docs.yml:98)"]
        sphinx["PYOPENGL_PLATFORM=egl<br/>MUJOCO_GL=egl<br/>sphinx-build ./source _local_build"]
    end

    subgraph "Deployment"
        artifact["Upload to artifact dir"]
        upload_job["upload job"]
        gh_pages["Deploy to gh-pages"]
        target_folder["Target folder:<br/>main or X.Y"]
    end

    push_main --> runner
    tags --> runner
    pr --> runner

    runner --> yum_deps
    yum_deps --> conda
    conda --> pytorch
    pytorch --> torchrl
    torchrl --> docs_deps
    docs_deps --> sanitize

    sanitize -->|"Yes"| set_env
    sanitize -->|"No"| sphinx
    set_env --> sphinx

    sphinx --> artifact
    artifact --> upload_job
    upload_job --> gh_pages
    gh_pages --> target_folder
```

**Sources**: `.github/workflows/docs.yml`

### Documentation Requirements

Documentation dependencies are specified in `docs/requirements.txt`:

| Category | Packages |
|----------|----------|
| Sphinx Core | `sphinx===5.0.0`, `sphinx-copybutton`, `sphinx-gallery`, `sphinx-autodoc-typehints` |
| Theme | `pytorch_sphinx_theme` (from GitHub) |
| Parsers | `myst-parser`, `docutils` |
| RL Environments | `dm_control`, `mujoco<3.3.6`, `gymnasium[classic_control,atari]`, `vmas` |
| Utilities | `matplotlib`, `numpy`, `tqdm`, `ipython`, `imageio[ffmpeg,pyav]` |
| Export | `onnxscript`, `onnxruntime`, `onnx` |
| Configuration | `hydra-core>=1.1`, `omegaconf` |

**Sources**: `docs/requirements.txt`

### Documentation Structure

The documentation entry point is `docs/source/index.rst`, which defines the structure.

```mermaid
graph TB
    subgraph "Main Index"
        index["index.rst<br/>TorchRL Documentation"]
    end

    subgraph "Getting Started"
        gs0["getting-started-0"]
        gs1["getting-started-1"]
        gs2["getting-started-2"]
        gs3["getting-started-3"]
        gs4["getting-started-4"]
        gs5["getting-started-5"]
    end

    subgraph "Tutorials"
        basic["Basic:<br/>coding_ppo, pendulum, torchrl_demo"]
        intermediate["Intermediate:<br/>multiagent_ppo, torchrl_envs,<br/>dqn_with_rnn, rb_tutorial"]
        advanced["Advanced:<br/>multiagent_competitive_ddpg,<br/>multi_task, coding_ddpg"]
    end

    subgraph "API Reference"
        api["reference/index"]
    end

    subgraph "Knowledge Base"
        kb["reference/knowledge_base"]
    end

    index --> gs0
    index --> basic
    index --> intermediate
    index --> advanced
    index --> api
    index --> kb
```

**Sources**: `docs/source/index.rst`

### Sphinx Gallery Configuration

The gallery configuration in `docs/source/conf.py` controls tutorial generation:

-   `examples_dirs`: `reference/generated/tutorials/` (source)
-   `gallery_dirs`: `tutorials` (output)
-   `abort_on_example_error`: `True` (strict mode)
-   `plot_gallery`: `"False"` (no gallery plots)
-   `reset_modules`: Custom `kill_procs` function + matplotlib/seaborn

The `kill_procs` function (`docs/source/conf.py`) terminates child processes after each gallery example to prevent resource leaks.

**Sources**: `docs/source/conf.py`

---

## Continuous Integration Details

### Build Job Configuration

All wheel build workflows follow a common pattern using PyTorch's test infrastructure. They call shared workflows like `pytorch/test-infra/.github/workflows/build_wheels_macos.yml` [build-wheels-m1.yml:78](), `build_wheels_windows.yml` [build-wheels-windows.yml:93](), and `build_wheels_linux.yml` [build-wheels-linux.yml:102](), [build-wheels-aarch64-linux.yml:102]().

```mermaid
graph LR
    subgraph "Job Definition"
        repo["repository: pytorch/rl"]
        ref["ref: empty (use trigger ref)"]
        test_infra["test-infra-repository:<br/>pytorch/test-infra"]
        matrix["build-matrix:<br/>from generate-matrix"]
    end

    subgraph "Package Configuration"
        pkg_name["package-name: torchrl"]
        smoke["smoke-test-script:<br/>test/smoke_test.py"]
        pre_script["pre-script:<br/>platform-specific"]
        env_script["env-script:<br/>platform-specific"]
    end

    subgraph "Execution"
        shared_workflow["uses:<br/>pytorch/test-infra/.github/workflows/<br/>build_wheels_*.yml@main"]
    end

    repo --> shared_workflow
    ref --> shared_workflow
    test_infra --> shared_workflow
    matrix --> shared_workflow
    pkg_name --> shared_workflow
    smoke --> shared_workflow
    pre_script --> shared_workflow
    env_script --> shared_workflow
```

**Sources**: [.github/workflows/build-wheels-linux.yml:92-112](), [.github/workflows/build-wheels-aarch64-linux.yml:91](), [.github/workflows/build-wheels-windows.yml:81-105](), [.github/workflows/build-wheels-m1.yml:68-95]()

### Smoke Test

The smoke test validates basic imports and functionality [test/smoke_test.py:1-20](). It ensures that core TorchRL modules can be imported and a `PrioritizedReplayBuffer` can be instantiated.

```mermaid
graph LR
    subgraph "test_imports()"
        imports["Import core modules:<br/>ReplayBuffer<br/>PrioritizedReplayBuffer<br/>TensorSpec<br/>Transform, TransformedEnv<br/>GymLikeEnv<br/>SafeModule<br/>LossModule"]
        instantiate["Instantiate:<br/>PrioritizedReplayBuffer<br/>(alpha=1.1, beta=1.1)"]
    end

    imports --> instantiate
```

**Sources**: [test/smoke_test.py:8-20]()

### Documentation Deployment Strategy

Documentation is deployed to different folders based on the trigger. The `release.yml` workflow also updates `gh-pages` docs by creating a stable symlink [release.yml:5]().

| Trigger Type | Ref Name | Target Folder | Example |
|--------------|----------|---------------|---------|
| Push to main | `main` | `main` | `/main/` |
| Release tag | `v0.15.2` | `0.15` (major.minor) | `/0.15/` |
| RC tag | `v0.15.2-rc1` | Skipped (no upload) | N/A |

The upload job (`.github/workflows/docs.yml`) uses git operations to commit and push to the `gh-pages` branch:

1.  Downloads artifact from build job
2.  Determines target folder from ref type/name
3.  Clears existing folder content
4.  Copies new documentation via `rsync`
5.  Updates `_static` folder if building for main branch
6.  Commits with pytorchbot credentials
7.  Pushes to gh-pages

**Sources**: `.github/workflows/docs.yml`, [release.yml:5]()

---

## Environment Variables

Key environment variables used across the build system:

| Variable | Purpose | Set In | Values |
|----------|---------|--------|--------|
| `TORCHRL_BUILD_VERSION` | Package version for wheel builds | Version scripts | `0.14.0` |
| `DEBUG` | Enable debug mode compilation | User/CI | `0` or `1` |
| `PYTHON_INCLUDE_DIR` | Additional Python headers | User/CI | Path to Python includes |
| `RL_SANITIZE_VERSION_STR_IN_DOCS` | Sanitize version in docs | docs.yml | `1` (if set) |
| `TORCHRL_CONSOLE_STREAM` | Console output stream | conf.py, docs.yml | `stdout` |
| `PYOPENGL_PLATFORM` | OpenGL platform for rendering | docs.yml | `egl` |
| `MUJOCO_GL` | MuJoCo graphics backend | docs.yml | `egl` |
| `MAX_IDLE_COUNT` | Collector timeout (docs build) | docs.yml | `180` |
| `BATCHED_PIPE_TIMEOUT` | Pipe timeout (docs build) | docs.yml | `180` |
| `TENSORDICT_SOURCE` | Source for TensorDict installation | build-wheels-*.yml | `auto`, `stable`, `git` |
| `RELEASE_TAG` | Release tag for `release.yml` | release.yml | e.g., `v0.11.0` |
| `TEST_INFRA_REF` | PyTorch test-infra ref | release.yml | `main` or `release/X.Y` |
| `DRY_RUN` | Dry run mode for `release.yml` | release.yml | `true` or `false` |

**Sources**: [setup.py:236,256](), [.github/scripts/td_script.sh:3](), [.github/scripts/version_script.bat:2](), `docs/source/conf.py`, `.github/workflows/docs.yml`, [.github/workflows/build-wheels-linux.yml:69](), [.github/workflows/build-wheels-aarch64-linux.yml:69](), [.github/workflows/build-wheels-windows.yml:59](), [.github/workflows/build-wheels-m1.yml:49](), [.github/workflows/release.yml:87-96]()

---

## Contributing Workflow

This section provides a high-level overview of contributing to TorchRL. For detailed guidelines, see [Contributing and Repo Automation](#12.5).

### Development Installation

For local development, it is recommended to install TorchRL and TensorDict in editable mode. The `CONTRIBUTING.md` provides instructions for `pip install` and `uv run` [CONTRIBUTING.md:5-54]().

```bash
# Using pip
git clone https://github.com/pytorch/tensordict
git clone https://github.com/pytorch/rl
cd tensordict
python setup.py develop
cd ../rl
python setup.py develop

# Using uv (recommended for local development)
# From the root of the cloned TorchRL repository
uv run pytest test/test_tensordictmodules.py
# For CUDA 13.0 nightly wheels on Linux
uv run --index pytorch-nightly=https://download.pytorch.org/whl/nightly/cu130 pytest test/test_tensordictmodules.py
```

**Sources**: [CONTRIBUTING.md:5-54]()

### Build from Source

Standard installation builds C++ extensions automatically:

```bash
pip install -e . --no-build-isolation
```

The `--no-build-isolation` flag is used in CI (`.github/workflows/docs.yml`) to reuse the environment's build dependencies.

**Sources**: [CONTRIBUTING.md:23-25](), `.github/workflows/docs.yml`

### Code Formatting and Linting

TorchRL uses `pre-commit` hooks for linting and formatting. Contributors are encouraged to install and run `pre-commit` locally [CONTRIBUTING.md:69-79](). The `CLAUDE.md` file provides specific guidelines for AI agent contributions, including rules for imports, cross-version compatibility, logging, TensorDict usage, type hints, `torch.compile` friendliness, and testing [CLAUDE.md:1-281]().

**Sources**: [CONTRIBUTING.md:69-79](), [CLAUDE.md:1-281]()

### Pull Requests and Issues

The project actively welcomes pull requests. Contributors are asked to fork the repository, create a branch, add tests for new code, update documentation for API changes, ensure tests and documentation pass, and make sure code lints. A Contributor License Agreement (CLA) is required. Issues are tracked on GitHub, and contributors can assign themselves to issues [CONTRIBUTING.md:84-116]().

**Sources**: [CONTRIBUTING.md:84-116]()

---

## Platform-Specific Details

### Windows Build Configuration

Windows builds require special handling ([.github/scripts/version_script.bat:1-79]()):

1.  **Visual Studio Detection**: Uses `vswhere.exe` to locate MSVC installation.
2.  **Version Support**: Supports VS 2017 (v15), 2019 (v16), 2022 (v17).
3.  **Environment Setup**: Calls `vcvarsall.bat` with x64 architecture.
4.  **Intel XPU Support**: Conditional oneAPI setup for XPU builds.
5.  **Setuptools**: Pins to version `72.1.0` for compatibility.
6.  **Python Library Workaround**: Copies `python3XXt.lib` to `python3XX.lib` for free-threaded Python.

**Sources**: [.github/scripts/version_script.bat:1-79]()

### Aarch64 Build Configuration

Aarch64 builds have specific requirements:

-   **CUDA**: Disabled (`with-cuda: disable`) due to limited aarch64 CUDA support [build-wheels-aarch64-linux.yml:88]().
-   **Miniconda**: Disabled (`setup-miniconda: false`) in favor of system Python [build-wheels-aarch64-linux.yml:110]().
-   **Dependencies**: Uses `td_script.sh` for TensorDict and other dependencies [build-wheels-aarch64-linux.yml:112]().

**Sources**: [.github/workflows/build-wheels-aarch64-linux.yml:88](), [.github/workflows/build-wheels-aarch64-linux.yml:91](), [.github/workflows/build-wheels-aarch64-linux.yml:91]()

---

## Summary

The TorchRL development infrastructure provides:

1.  **Cross-platform builds** via `setup.py` with PyTorch's C++ extension utilities.
2.  **Automated wheel distribution** for Linux, Windows, macOS (x86\_64/ARM), and aarch64.
3.  **Sphinx-based documentation** with automated deployment to GitHub Pages.
4.  **Smoke tests** validating core functionality across platforms.

All workflows leverage PyTorch's shared test infrastructure (`pytorch/test-infra`) for consistency with the broader PyTorch ecosystem. Version management is centralized through `version.txt` and `pyproject.toml`, and platform-specific scripts handle environment configuration.

For details on specific aspects of the development process, refer to the child pages:
-   [Build System](#12.1)
-   [Documentation System](#12.2)
-   [Testing and CI](#12.3)
-   [Benchmarking](#12.4)
-   [Contributing and Repo Automation](#12.5)

---

