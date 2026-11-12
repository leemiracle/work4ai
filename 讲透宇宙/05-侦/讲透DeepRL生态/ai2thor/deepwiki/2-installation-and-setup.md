> 来源: [https://deepwiki.com/allenai/ai2thor/2-installation-and-setup](https://deepwiki.com/allenai/ai2thor/2-installation-and-setup)
> DeepWiki allenai/ai2thor | Last indexed: 16 September 2025 (24f798

# Installation and Setup

  Relevant source files 
 - [.coveragerc](https://github.com/allenai/ai2thor/blob/24f79883/.coveragerc)
 - [.csharpierignore](https://github.com/allenai/ai2thor/blob/24f79883/.csharpierignore)
 - [.editorconfig](https://github.com/allenai/ai2thor/blob/24f79883/.editorconfig)
 - [.github/workflows/black.yaml](https://github.com/allenai/ai2thor/blob/24f79883/.github/workflows/black.yaml)
 - [.gitignore](https://github.com/allenai/ai2thor/blob/24f79883/.gitignore)
 - [CONTRIBUTING.md](https://github.com/allenai/ai2thor/blob/24f79883/CONTRIBUTING.md?plain=1)
 - [ai2thor/tests/__init__.py](https://github.com/allenai/ai2thor/blob/24f79883/ai2thor/tests/__init__.py)
 - [pyproject.toml](https://github.com/allenai/ai2thor/blob/24f79883/pyproject.toml)
 - [pytest.ini](https://github.com/allenai/ai2thor/blob/24f79883/pytest.ini)
 - [requirements-dev.txt](https://github.com/allenai/ai2thor/blob/24f79883/requirements-dev.txt)
 - [requirements.txt](https://github.com/allenai/ai2thor/blob/24f79883/requirements.txt)
 - [setup.py](https://github.com/allenai/ai2thor/blob/24f79883/setup.py)
 - [unity/Assets/MagicMirror/Prefab/MirrorCameraScript.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/MagicMirror/Prefab/MirrorCameraScript.cs)
 - [unity/Assets/MessagePack/MessagePackSerializer.NonGeneric.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/MessagePack/MessagePackSerializer.NonGeneric.cs)
 - [unity/Assets/MessagePack/Resolvers/StandardResolver.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/MessagePack/Resolvers/StandardResolver.cs)
 - [unity/Assets/MessagePack/Resolvers/TypelessContractlessStandardResolver.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/MessagePack/Resolvers/TypelessContractlessStandardResolver.cs)
 - [unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove.meta](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Physics/SimObjsPhysics/Custom Project Objects/FurnMove.meta)
 - [unity/Assets/Scripts/ThorContractlessStandardResolver.cs](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ThorContractlessStandardResolver.cs)
 - [unity/Packages/manifest.json](https://github.com/allenai/ai2thor/blob/24f79883/unity/Packages/manifest.json)
 - [unity/Packages/packages-lock.json](https://github.com/allenai/ai2thor/blob/24f79883/unity/Packages/packages-lock.json)
 - [unity/ProjectSettings/ProjectVersion.txt](https://github.com/allenai/ai2thor/blob/24f79883/unity/ProjectSettings/ProjectVersion.txt)
 - [unity/ProjectSettings/UnityConnectSettings.asset](https://github.com/allenai/ai2thor/blob/24f79883/unity/ProjectSettings/UnityConnectSettings.asset)
 - [unity/ProjectSettings/VersionControlSettings.asset](https://github.com/allenai/ai2thor/blob/24f79883/unity/ProjectSettings/VersionControlSettings.asset)
 
  This document covers the installation and configuration of AI2-THOR, including Python package setup, Unity dependencies, and build system configuration. AI2-THOR is a near photo-realistic interactive framework for embodied AI agents that consists of both Python API components and Unity simulation environments.

 For information about using the Python Controller API after installation, see [Controller Class](https://deepwiki.com/allenai/ai2thor/4.1-controller-class). For details about the build system and deployment pipeline, see [Build System and Deployment](https://deepwiki.com/allenai/ai2thor/4.2-build-system-and-deployment).

 
## System Requirements and Dependencies

 AI2-THOR requires both Python and Unity components to function properly. The framework supports multiple platforms and deployment targets.

 
### Python Environment Requirements

 The Python package supports Python 3.5 through 3.8 as specified in [setup.py38-43](https://github.com/allenai/ai2thor/blob/24f79883/setup.py#L38-L43) The core Python dependencies are managed through requirements files:

 
| Dependency Category | File | Key Components |
|---|---|---|
| Core Runtime | requirements.txt | Flask 2.0.1, numpy, PyYAML, requests |
| Communication | requirements.txt | msgpack, Werkzeug 2.0.1, compress_pickle |
| Development | requirements-dev.txt | pytest, black, jsonschema |

 **Installation Flow Diagram**

 
```

```

 Sources: [setup.py1-59](https://github.com/allenai/ai2thor/blob/24f79883/setup.py#L1-L59) [requirements.txt1-16](https://github.com/allenai/ai2thor/blob/24f79883/requirements.txt#L1-L16) [requirements-dev.txt1-9](https://github.com/allenai/ai2thor/blob/24f79883/requirements-dev.txt#L1-L9) [unity/Packages/manifest.json1-58](https://github.com/allenai/ai2thor/blob/24f79883/unity/Packages/manifest.json#L1-L58)

 
### Unity Environment Requirements

 The Unity project requires Unity Editor 2020.3.25f1 as specified in [unity/ProjectSettings/ProjectVersion.txt1-2](https://github.com/allenai/ai2thor/blob/24f79883/unity/ProjectSettings/ProjectVersion.txt#L1-L2) The project uses the Unity Package Manager for dependency management.

 **Unity Dependency Resolution**

 
```

```

 Sources: [unity/ProjectSettings/ProjectVersion.txt1-3](https://github.com/allenai/ai2thor/blob/24f79883/unity/ProjectSettings/ProjectVersion.txt#L1-L3) [unity/Packages/manifest.json11-26](https://github.com/allenai/ai2thor/blob/24f79883/unity/Packages/manifest.json#L11-L26) [unity/Assets/Scripts/ThorContractlessStandardResolver.cs226-277](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ThorContractlessStandardResolver.cs#L226-L277)

 
## Python Package Installation

 
### Standard Installation

 Install the AI2-THOR Python package using pip:

 
```

```

 The package is configured through [setup.py25-59](https://github.com/allenai/ai2thor/blob/24f79883/setup.py#L25-L59) with the following key metadata:

 
 - Package name: `ai2thor`
 - License: Apache License 2.0
 - Platforms: macOS, Unix
 - Scripts: `ai2thor-xorg` for X server configuration
 
 
### Development Installation

 For development work, clone the repository and install in development mode:

 
```

```

 **Package Structure and Entry Points**

 
```

```

 Sources: [setup.py53-57](https://github.com/allenai/ai2thor/blob/24f79883/setup.py#L53-L57) [pytest.ini1-6](https://github.com/allenai/ai2thor/blob/24f79883/pytest.ini#L1-L6) [pyproject.toml1-22](https://github.com/allenai/ai2thor/blob/24f79883/pyproject.toml#L1-L22) [.editorconfig10-25](https://github.com/allenai/ai2thor/blob/24f79883/.editorconfig#L10-L25)

 
## Unity Development Setup

 
### Unity Editor Configuration

 For Unity development, install Unity 2020.3.25f1 and open the project located in the `unity/` directory. The project configuration includes:

 
 - **Package Dependencies**: Managed through [unity/Packages/manifest.json11-57](https://github.com/allenai/ai2thor/blob/24f79883/unity/Packages/manifest.json#L11-L57)
 - **Project Settings**: Version control, analytics, and editor configurations
 - **Build Targets**: Multiple platform support including standalone and WebGL
 
 
### MessagePack Serialization Setup

 AI2-THOR uses a custom MessagePack serialization system for Unity-Python communication. The key components are:

 
| Component | File | Purpose |
|---|---|---|
| ThorContractlessStandardResolver | unity/Assets/Scripts/ThorContractlessStandardResolver.cs226-277 | Main serialization resolver |
| Vector3Formatter | unity/Assets/Scripts/ThorContractlessStandardResolver.cs174-224 | Unity Vector3 serialization |
| NavMeshPathFormatter | unity/Assets/Scripts/ThorContractlessStandardResolver.cs21-45 | Navigation mesh path serialization |

 
```

```

 Sources: [unity/Assets/Scripts/ThorContractlessStandardResolver.cs1-318](https://github.com/allenai/ai2thor/blob/24f79883/unity/Assets/Scripts/ThorContractlessStandardResolver.cs#L1-L318)

 
## Build System Configuration

 
### Environment Setup

 The build system uses Python's `invoke` task runner and requires specific environment configurations:

 **Gitignore Configuration**: The [.gitignore1-133](https://github.com/allenai/ai2thor/blob/24f79883/.gitignore#L1-L133) file excludes build artifacts, temporary files, and platform-specific directories:

 
 - Unity build directories: `unity/[Bb]uilds/`
 - Python artifacts: `ai2thor.egg-info/`, `dist/`, `.pytest_cache`
 - Generated files: `ai2thor/_builds.py`, `ai2thor/_version.py`
 
 **Code Formatting**: The project enforces consistent code formatting:

 
 - **Python**: Black formatter configured in [pyproject.toml1-3](https://github.com/allenai/ai2thor/blob/24f79883/pyproject.toml#L1-L3) with 100-character line length
 - **C#**: EditorConfig rules in [.editorconfig13-25](https://github.com/allenai/ai2thor/blob/24f79883/.editorconfig#L13-L25) with specific brace and newline preferences
 
 
### Platform Support

 AI2-THOR supports multiple deployment targets and platforms as configured in the Unity package dependencies:

 
```

```

 Sources: [unity/Packages/manifest.json25](https://github.com/allenai/ai2thor/blob/24f79883/unity/Packages/manifest.json#L25-L25) [unity/Packages/packages-lock.json145-154](https://github.com/allenai/ai2thor/blob/24f79883/unity/Packages/packages-lock.json#L145-L154) [setup.py46-47](https://github.com/allenai/ai2thor/blob/24f79883/setup.py#L46-L47)

 
## Verification and Testing

 
### Test Configuration

 The testing framework is configured through [pytest.ini1-6](https://github.com/allenai/ai2thor/blob/24f79883/pytest.ini#L1-L6) with the following settings:

 
 - **Test Discovery**: `testpaths = ai2thor/tests/`
 - **Logging**: DEBUG level with timestamp formatting
 - **Timeout**: 60 seconds per test
 - **Coverage**: Configured in [.coveragerc1-3](https://github.com/allenai/ai2thor/blob/24f79883/.coveragerc#L1-L3) to omit test files
 
 
### Development Workflow Verification

 After installation, verify the setup by running the test suite:

 
```

```

 The continuous integration system enforces code formatting through GitHub Actions as configured in [.github/workflows/black.yaml1-10](https://github.com/allenai/ai2thor/blob/24f79883/.github/workflows/black.yaml#L1-L10)

 **Testing and Quality Assurance Flow**

 
```

```

 Sources: [pytest.ini1-6](https://github.com/allenai/ai2thor/blob/24f79883/pytest.ini#L1-L6) [.coveragerc1-3](https://github.com/allenai/ai2thor/blob/24f79883/.coveragerc#L1-L3) [.github/workflows/black.yaml1-10](https://github.com/allenai/ai2thor/blob/24f79883/.github/workflows/black.yaml#L1-L10) [CONTRIBUTING.md16-22](https://github.com/allenai/ai2thor/blob/24f79883/CONTRIBUTING.md?plain=1#L16-L22)
