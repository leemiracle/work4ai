# deepwiki torchrl §12 development-and-deployment
> 来源: https://deepwiki.com/pytorch/rl/12-development-and-deployment

$/$
$?

/$

DeepWiki

DeepWiki
pytorch/rl

$?

/$

Last indexed:  14 December 2025  (eaaa11)

  - Overview
  - Core Data Infrastructure
  - TensorDict System
  - TensorSpec System
  - Environments
  - EnvBase and Environment Specifications
  - Environment Transforms
  - Backend Integrations
  - Batched and Parallel Environments
  - Data Collection
  - Collector Architecture
  - Distributed Collection Strategies
  - Replay Buffers
  - ReplayBuffer Architecture
  - Advanced Replay Buffer Features
  - Modules and Models
  - TensorDictModule System
  - Actors, Critics, and Value Networks
  - Probability Distributions
  - Neural Network Architectures
  - Exploration Strategies
  - Learning Algorithms
  - Loss Module Architecture
  - On-Policy Algorithms
  - Off-Policy Algorithms
  - Value-Based Algorithms
  - Value Estimators
  - Training Infrastructure
  - Trainer System
  - Helper Utilities
  - LLM Integration
  - LLM Wrapper System
  - LLM Data Structures
  - LLM Training Objectives
  - LLM Environments and Tools
  - Multi-Agent Reinforcement Learning
  - Examples and Tutorials
  - Development and Deployment
  - Build System
  - Documentation System

Menu

## Development and Deployment

Relevant source files

  - .github/scripts/pre-build-script-win.sh

  - .github/scripts/pre-build-script.sh

  - .github/scripts/td_script.sh

  - .github/scripts/version_script.bat

  - .github/unittest/windows_optdepts/scripts/environment.yml

  - .github/workflows/build-wheels-aarch64-linux.yml

  - .github/workflows/build-wheels-linux.yml

  - .github/workflows/build-wheels-m1.yml

  - .github/workflows/build-wheels-windows.yml

  - .github/workflows/docs.yml

  - docs/requirements.txt

  - docs/source/conf.py

  - docs/source/index.rst

  - setup.py

  - test/smoke_test.py

  - version.txt

This document describes the build system, continuous integration/deployment pipelines, and documentation infrastructure for TorchRL. It covers how the library is built from source, packaged into distributable wheels, and how documentation is generated and deployed.

For information about using the high-level Trainer system for RL experiments, see Training Infrastructure. For details on the core library architecture, see Overview.

### Overview

TorchRL's development infrastructure consists of four main components:

  - Build System : Python package setup with C++ extension compilation

  - CI/CD Pipelines : Automated wheel building for multiple platforms

  - Documentation System : Sphinx-based documentation with automated deployment

  - Testing Infrastructure : Smoke tests and validation scripts

The build system compiles C++ extensions using PyTorch's build utilities, while CI/CD workflows handle cross-platform distribution. Documentation is generated from docstrings and RST files, then deployed to GitHub Pages.

### Build System Architecture

#### Setup Configuration

The build system is defined in setup.py1-112 which uses PyTorch's `torch.utils.cpp_extension` module to compile C++ extensions with platform-specific compiler flags.

```

```

Sources: setup.py1-112

#### Compiler Configuration

The build system adapts to different platforms with specific compiler flags:

| Platform | Compiler | Optimization | C++ Standard | Special Flags |
| Windows | MSVC | /O2 | /std:c++17 | /EHsc (exception handling) |
| Unix-like | GCC/Clang | -O3 | -std=c++17 | -fdiagnostics-color=always |

Debug mode can be enabled via the `DEBUG=1` environment variable, which switches optimization levels to `/Od` (Windows) or `-O0` (Unix) and adds debugging symbols (setup.py36-69).

Sources: setup.py26-69

#### C++ Extension Build Process

```

```

Sources: setup.py71-91

### Package Distribution

#### Wheel Build Workflows

TorchRL maintains separate CI/CD workflows for building binary wheels across multiple platforms:

```

```

Sources: .github/workflows/build-wheels-linux.yml1-50 .github/workflows/build-wheels-aarch64-linux.yml1-53 .github/workflows/build-wheels-windows.yml1-54 .github/workflows/build-wheels-m1.yml1-51

#### Build Matrix Configuration

Each platform workflow generates a build matrix specifying Python versions, CUDA versions (where applicable), and platform-specific settings:

| Workflow | Platform | Runner | Special Configuration |
| build-wheels-linux.yml | Linux x86_64 | linux | env-var-script: td_script.sh |
| build-wheels-aarch64-linux.yml | Linux aarch64 | linux-aarch64 | setup-miniconda: false, with-cuda: disable |
| build-wheels-windows.yml | Windows | windows | env-script: version_script.bat, post-script: relocate.py |
| build-wheels-m1.yml | macOS ARM64 | macos-m2-15 | env-var-script: td_script.sh |

Sources: .github/workflows/build-wheels-linux.yml21-49 .github/workflows/build-wheels-aarch64-linux.yml21-53 .github/workflows/build-wheels-windows.yml21-54 .github/workflows/build-wheels-m1.yml21-51

#### Version Management

Version information is centralized and managed through multiple files:

```

```

Sources: version.txt1 .github/scripts/td_script.sh3 .github/scripts/version_script.bat2 .github/scripts/pre-build-script-win.sh5

#### Pre-Build Dependencies

Each platform has specific pre-build scripts that install dependencies:

Linux/macOS (.github/scripts/td_script.sh1-31):

  - Upgrades setuptools

  - Installs pybind11[global]

  - Installs tensordict from GitHub (main branch)

  - Conditional PyTorch installation for smoke tests

Windows (.github/scripts/version_script.bat1-57):

  - Sets up MSVC environment using vswhere.exe

  - Configures Visual Studio variables ( VS15VCVARSALL )

  - Upgrades setuptools to version 72.1.0

  - Sets DISTUTILS_USE_SDK=1 for SDK builds

Sources: .github/scripts/td_script.sh1-31 .github/scripts/version_script.bat1-57 .github/scripts/pre-build-script.sh1-8 .github/scripts/pre-build-script-win.sh1-6

### Documentation System

#### Sphinx Configuration

The documentation is built using Sphinx with the PyTorch theme. Configuration is centralized in docs/source/conf.py1-220

```

```

Sources: docs/source/conf.py1-220

#### Documentation Build Workflow

The documentation build process is orchestrated by .github/workflows/docs.yml1-186:

```

```

Sources: .github/workflows/docs.yml1-186

#### Documentation Requirements

Documentation dependencies are specified in docs/requirements.txt1-35:

| Category | Packages |
| Sphinx Core | sphinx===5.0.0 , sphinx-copybutton , sphinx-gallery , sphinx-autodoc-typehints |
| Theme | pytorch_sphinx_theme (from GitHub) |
| Parsers | myst-parser , docutils |
| RL Environments | dm_control , mujoco<3.3.6 , gymnasium[classic_control,atari] , vmas |
| Utilities | matplotlib , numpy , tqdm , ipython , imageio[ffmpeg,pyav] |
| Export | onnxscript , onnxruntime , onnx |
| Configuration | hydra-core>=1.1 , omegaconf |

Sources: docs/requirements.txt1-35

#### Documentation Structure

The documentation entry point is docs/source/index.rst1-143 which defines the structure:

```

```

Sources: docs/source/index.rst1-143

#### Sphinx Gallery Configuration

The gallery configuration in docs/source/conf.py103-118 controls tutorial generation:

  - examples_dirs : reference/generated/tutorials/ (source)

  - gallery_dirs : tutorials (output)

  - abort_on_example_error : True (strict mode)

  - plot_gallery : "False" (no gallery plots)

  - reset_modules : Custom kill_procs function + matplotlib/seaborn

The `kill_procs` function (docs/source/conf.py89-101) terminates child processes after each gallery example to prevent resource leaks.

Sources: docs/source/conf.py89-118

### Continuous Integration Details

#### Build Job Configuration

All wheel build workflows follow a common pattern using PyTorch's test infrastructure:

```

```

Sources: .github/workflows/build-wheels-linux.yml28-49 .github/workflows/build-wheels-windows.yml28-53 .github/workflows/build-wheels-m1.yml28-51

#### Smoke Test

The smoke test validates basic imports and functionality (test/smoke_test.py1-20):

```

```

Sources: test/smoke_test.py8-20

#### Documentation Deployment Strategy

Documentation is deployed to different folders based on the trigger:

| Trigger Type | Ref Name | Target Folder | Example |
| Push to main | main | main | /main/ |
| Release tag | v0.15.2 | 0.15 (major.minor) | /0.15/ |
| RC tag | v0.15.2-rc1 | Skipped (no upload) | N/A |

The upload job (.github/workflows/docs.yml124-186) uses git operations to commit and push to the `gh-pages` branch:

  - Downloads artifact from build job

  - Determines target folder from ref type/name

  - Clears existing folder content

  - Copies new documentation via rsync

  - Updates _static folder if building for main branch

  - Commits with pytorchbot credentials

  - Pushes to gh-pages

Sources: .github/workflows/docs.yml136-185

### Environment Variables

Key environment variables used across the build system:

| Variable | Purpose | Set In | Values |
| TORCHRL_BUILD_VERSION | Package version for wheel builds | Version scripts | 0.10.0 |
| DEBUG | Enable debug mode compilation | User/CI | 0 or 1 |
| PYTHON_INCLUDE_DIR | Additional Python headers | User/CI | Path to Python includes |
| RL_SANITIZE_VERSION_STR_IN_DOCS | Sanitize version in docs | docs.yml | 1 (if set) |
| TORCHRL_CONSOLE_STREAM | Console output stream | conf.py, docs.yml | stdout |
| PYOPENGL_PLATFORM | OpenGL platform for rendering | docs.yml | egl |
| MUJOCO_GL | MuJoCo graphics backend | docs.yml | egl |
| MAX_IDLE_COUNT | Collector timeout (docs build) | docs.yml | 180 |
| BATCHED_PIPE_TIMEOUT | Pipe timeout (docs build) | docs.yml | 180 |

Sources: setup.py36-57 .github/scripts/td_script.sh3 .github/scripts/version_script.bat2 docs/source/conf.py43-51 .github/workflows/docs.yml98-115

### Contributing Workflow

#### Development Installation

For local development, install from source with editable mode:

```

```

This approach is documented in docs/source/index.rst53-63

#### Build from Source

Standard installation builds C++ extensions automatically:

```

```

The `--no-build-isolation` flag is used in CI (.github/workflows/docs.yml88) to reuse the environment's build dependencies.

Sources: docs/source/index.rst53-63 .github/workflows/docs.yml88

### Platform-Specific Details

#### Windows Build Configuration

Windows builds require special handling (.github/scripts/version_script.bat1-57):

  - Visual Studio Detection : Uses vswhere.exe to locate MSVC installation

  - Version Support : Supports VS 2017 (v15), 2019 (v16), 2022 (v17)

  - Environment Setup : Calls vcvarsall.bat with x64 architecture

  - Intel XPU Support : Conditional oneAPI setup for XPU builds

  - Setuptools : Pins to version 72.1.0 for compatibility

#### Aarch64 Build Configuration

Aarch64 builds have specific requirements:

  - CUDA : Disabled ( with-cuda: disable ) due to limited aarch64 CUDA support

  - Miniconda : Disabled ( setup-miniconda: false ) in favor of system Python

  - Dependencies : Uses td_script.sh with aarch64-specific conditionals

Sources: .github/scripts/version_script.bat1-57 .github/workflows/build-wheels-aarch64-linux.yml28-52

### Summary

The TorchRL development infrastructure provides:

  - Cross-platform builds via setup.py with PyTorch's C++ extension utilities

  - Automated wheel distribution for Linux, Windows, macOS (x86_64/ARM), and aarch64

  - Sphinx-based documentation with automated deployment to GitHub Pages

  - Smoke tests validating core functionality across platforms

All workflows leverage PyTorch's shared test infrastructure (`pytorch/test-infra`) for consistency with the broader PyTorch ecosystem. Version management is centralized through `version.txt`, and platform-specific scripts handle environment configuration.



#### On this page

  - Development and Deployment
  - Overview
  - Build System Architecture
  - Setup Configuration
  - Compiler Configuration
  - C++ Extension Build Process
  - Package Distribution
  - Wheel Build Workflows
  - Build Matrix Configuration
  - Version Management
  - Pre-Build Dependencies
  - Documentation System
  - Sphinx Configuration
  - Documentation Build Workflow
  - Documentation Requirements
  - Documentation Structure
  - Sphinx Gallery Configuration
  - Continuous Integration Details
  - Build Job Configuration
  - Smoke Test
  - Documentation Deployment Strategy
  - Environment Variables
  - Contributing Workflow
  - Development Installation
  - Build from Source
  - Platform-Specific Details
  - Windows Build Configuration
  - Aarch64 Build Configuration
  - Summary

$!/$$/$
