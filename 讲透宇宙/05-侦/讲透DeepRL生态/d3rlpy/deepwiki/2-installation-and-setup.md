> 来源: [https://deepwiki.com/takuseno/d3rlpy/2-installation-and-setup](https://deepwiki.com/takuseno/d3rlpy/2-installation-and-setup)
> DeepWiki takuseno/d3rlpy | Last indexed: 25 June 2025 (4f0956

# Installation and Setup

  Relevant source files 
 - [d3rlpy/__init__.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/__init__.py)
 - [d3rlpy/cli.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py)
 - [d3rlpy/datasets.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py)
 - [d3rlpy/envs/wrappers.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/envs/wrappers.py)
 - [docker/Dockerfile](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docker/Dockerfile)
 - [docs/cli.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/cli.rst)
 - [docs/index.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/index.rst)
 - [docs/installation.rst](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/installation.rst)
 - [examples/custom_algo.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/examples/custom_algo.py)
 - [examples/deepmind_control.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/examples/deepmind_control.py)
 - [mypy.ini](https://github.com/takuseno/d3rlpy/blob/4f0956ba/mypy.ini)
 - [requirements.txt](https://github.com/takuseno/d3rlpy/blob/4f0956ba/requirements.txt)
 - [scripts/build-docker](https://github.com/takuseno/d3rlpy/blob/4f0956ba/scripts/build-docker)
 - [setup.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py)
 - [tests/test_datasets.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/tests/test_datasets.py)
 
  This document covers the installation and setup procedures for d3rlpy, including dependency management, CLI configuration, and optional package installation. It focuses on the technical installation workflows and their underlying implementation.

 For information about using d3rlpy after installation, see [Quick Start Tutorial](https://deepwiki.com/takuseno/d3rlpy/3-quick-start-tutorial). For details about the CLI commands available after installation, see [CLI and Utilities](https://deepwiki.com/takuseno/d3rlpy/9-cli-and-utilities).

 
## Installation Methods Overview

 D3rlpy supports multiple installation approaches, each implemented through different mechanisms in the codebase. The installation system is configured through several key files that define dependencies, entry points, and optional components.

 
### Installation Workflow Diagram

 
```

```

 Sources: [setup.py1-53](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L1-L53) [requirements.txt1-11](https://github.com/takuseno/d3rlpy/blob/4f0956ba/requirements.txt#L1-L11) [docker/Dockerfile1-43](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docker/Dockerfile#L1-L43) [d3rlpy/__init__.py69-70](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/__init__.py#L69-L70)

 
## Core Dependencies

 The core dependencies are defined in `setup.py` and provide the essential functionality for d3rlpy's operation. These packages are automatically installed with any installation method.

 
| Package | Version Requirement | Purpose |
|---|---|---|
| torch | >=2.5.0 | PyTorch deep learning framework |
| gymnasium | ==1.0.0 | OpenAI Gym environment interface |
| gym | >=0.26.0 | Legacy Gym compatibility |
| tqdm | >=4.66.3 | Progress bars |
| h5py | No version specified | HDF5 file format support |
| click | No version specified | CLI framework |
| structlog | No version specified | Structured logging |
| scikit-learn | No version specified | Machine learning utilities |

 Sources: [setup.py35-47](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L35-L47) [requirements.txt1-11](https://github.com/takuseno/d3rlpy/blob/4f0956ba/requirements.txt#L1-L11)

 
### Dependency Configuration Diagram

 
```

```

 Sources: [setup.py35-47](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L35-L47) [setup.py49](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L49-L49) [setup.py51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L51-L51)

 
## PyPI Installation

 The standard installation method uses PyPI and pip, configured through the `setup.py` file:

 
```

```

 The setup configuration defines the package metadata, dependencies, and CLI entry points:

 
 - **Package name**: `d3rlpy`
 - **Python compatibility**: `>=3.9.0`
 - **Platform support**: Linux, macOS, Windows
 - **CLI command**: `d3rlpy` (registered via `console_scripts`)
 
 Sources: [setup.py10-12](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L10-L12) [setup.py49](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L49-L49) [setup.py51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L51-L51) [docs/installation.rst16-18](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/installation.rst#L16-L18)

 
## Conda Installation

 D3rlpy is available through conda-forge:

 
```

```

 This method uses the same `setup.py` configuration but handles dependency resolution through conda's package manager.

 Sources: [docs/installation.rst23-25](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/installation.rst#L23-L25)

 
## Docker Installation

 The Docker setup provides a complete environment with all dependencies pre-installed. The configuration is defined in `docker/Dockerfile`:

 
### Docker Environment Specifications

 
 - **Base image**: `pytorch/pytorch:2.5.1-cuda12.4-cudnn9-devel`
 - **GPU support**: CUDA 12.4 with cuDNN 9
 - **Pre-installed packages**: d4rl-atari, Cython
 - **Exposed port**: 6006 (for TensorBoard)
 
 
```

```

 The Dockerfile installs d3rlpy from the GitHub master branch and includes additional system dependencies for rendering and scientific computing.

 Sources: [docker/Dockerfile1-43](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docker/Dockerfile#L1-L43) [docs/installation.rst31-33](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/installation.rst#L31-L33)

 
## Source Installation

 For development or accessing the latest features, install from source:

 
```

```

 This method uses the same `setup.py` configuration but installs in editable mode, allowing modifications to take effect immediately.

 Sources: [docs/installation.rst41-45](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/installation.rst#L41-L45)

 
## CLI Tool Setup

 After installation, the `d3rlpy` command becomes available in the system PATH. The CLI is implemented through the Click framework and provides subcommands for various operations.

 
### CLI Command Structure

 
```

```

 Sources: [d3rlpy/cli.py61-63](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L61-L63) [d3rlpy/cli.py373-401](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L373-L401) [setup.py51](https://github.com/takuseno/d3rlpy/blob/4f0956ba/setup.py#L51-L51)

 
## Optional Package Installation

 D3rlpy supports optional packages for extended functionality, installed through the CLI `install` command. The available packages are defined in the `INSTALL_OPTIONS` dictionary.

 
### Available Optional Packages

 
| Package | Description | Installation Command |
|---|---|---|
| atari | Atari 2600 environments for Gym | d3rlpy install atari |
| d4rl_atari | Datasets for Atari 2600 | d3rlpy install d4rl_atari |
| d4rl | D4RL benchmark datasets | d3rlpy install d4rl |
| minari | Minari dataset format | d3rlpy install minari |
| dm_control | DeepMind Control via Shimmy | d3rlpy install dm_control |

 
### Optional Package Installation Implementation

 The installation system uses subprocess calls to pip for package management:

 
 - **Installation function**: `_install_module()` in [d3rlpy/cli.py353-357](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L353-L357)
 - **Uninstallation function**: `_uninstall_module()` in [d3rlpy/cli.py360-361](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L360-L361)
 - **Package definitions**: `INSTALL_OPTIONS` dict in [d3rlpy/cli.py364-370](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L364-L370)
 
 Sources: [d3rlpy/cli.py364-370](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L364-L370) [d3rlpy/cli.py373-401](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/cli.py#L373-L401) [docs/cli.rst138-152](https://github.com/takuseno/d3rlpy/blob/4f0956ba/docs/cli.rst#L138-L152)

 
### Optional Package Dependencies in Code

 Several modules demonstrate conditional imports for optional packages:

 
```

```

 Sources: [d3rlpy/datasets.py221-263](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py#L221-L263) [d3rlpy/datasets.py417-462](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py#L417-L462) [d3rlpy/datasets.py495-586](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/datasets.py#L495-L586)

 
## Post-Installation Verification

 After installation, d3rlpy runs an automatic health check to verify the setup. This process is implemented in the package initialization:

 
### Health Check Process

 
 - **Automatic execution**: Triggered during package import
 - **Implementation**: `run_healthcheck()` function
 - **GPU optimization**: Enables autograd compilation if CUDA is available
 - **Environment registration**: Registers Shimmy environments if available
 
 
```

```

 Sources: [d3rlpy/__init__.py69-84](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/__init__.py#L69-L84) [d3rlpy/healthcheck.py](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/healthcheck.py)

 
## Environment Configuration

 D3rlpy automatically configures various aspects of the runtime environment during initialization:

 
### Configuration Steps

 
 - **Random seed utilities**: Available via `d3rlpy.seed()` function
 - **GPU optimization**: Automatic PyTorch optimizations for CUDA
 - **Environment registration**: Optional Shimmy integration
 - **Type checking**: MyPy configuration for development
 
 The MyPy configuration in `mypy.ini` defines strict type checking rules and handles imports for optional dependencies.

 Sources: [d3rlpy/__init__.py56-67](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/__init__.py#L56-L67) [d3rlpy/__init__.py72-84](https://github.com/takuseno/d3rlpy/blob/4f0956ba/d3rlpy/__init__.py#L72-L84) [mypy.ini1-77](https://github.com/takuseno/d3rlpy/blob/4f0956ba/mypy.ini#L1-L77)
