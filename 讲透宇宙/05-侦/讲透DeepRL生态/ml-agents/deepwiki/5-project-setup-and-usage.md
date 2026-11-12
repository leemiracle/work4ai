> 来源: [https://deepwiki.com/Unity-Technologies/ml-agents/5-project-setup-and-usage](https://deepwiki.com/Unity-Technologies/ml-agents/5-project-setup-and-usage)
> DeepWiki Unity-Technologies/ml-agents | Last indexed: 22 May 2026 (d52b00

# Project Setup and Usage

  Relevant source files 
 - [.pre-commit-config.yaml](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/.pre-commit-config.yaml)
 - [com.unity.ml-agents/Documentation~/Examples-setup.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/Examples-setup.md?plain=1)
 - [com.unity.ml-agents/Documentation~/Examples.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/Examples.md?plain=1)
 - [com.unity.ml-agents/Documentation~/Get-Started.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/Get-Started.md?plain=1)
 - [com.unity.ml-agents/Documentation~/Inference-Engine.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/Inference-Engine.md?plain=1)
 - [com.unity.ml-agents/Documentation~/Installation.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/Installation.md?plain=1)
 - [com.unity.ml-agents/Documentation~/Learning-Environment-Examples.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/Learning-Environment-Examples.md?plain=1)
 - [com.unity.ml-agents/Documentation~/ML-Agents-Overview.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/ML-Agents-Overview.md?plain=1)
 - [com.unity.ml-agents/Documentation~/Migrating.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/Migrating.md?plain=1)
 - [com.unity.ml-agents/Documentation~/Python-Gym-API.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/Python-Gym-API.md?plain=1)
 - [com.unity.ml-agents/Documentation~/Sample.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/Sample.md?plain=1)
 - [com.unity.ml-agents/Documentation~/TableOfContents.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/TableOfContents.md?plain=1)
 - [com.unity.ml-agents/Documentation~/index.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Documentation~/index.md?plain=1)
 - [com.unity.ml-agents/Runtime/Actuators/IActionReceiver.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Actuators/IActionReceiver.cs)
 - [com.unity.ml-agents/Runtime/Actuators/IDiscreteActionMask.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Actuators/IDiscreteActionMask.cs)
 - [com.unity.ml-agents/Runtime/Agent.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs)
 - [com.unity.ml-agents/Runtime/Demonstrations/DemonstrationRecorder.cs](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Demonstrations/DemonstrationRecorder.cs)
 - [docs/Installation-Anaconda-Windows.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation-Anaconda-Windows.md?plain=1)
 - [docs/Installation.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1)
 - [docs/Migrating.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Migrating.md?plain=1)
 - [docs/Training-on-Amazon-Web-Service.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Amazon-Web-Service.md?plain=1)
 - [docs/Training-on-Microsoft-Azure.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Microsoft-Azure.md?plain=1)
 - [docs/Using-Virtual-Environment.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Using-Virtual-Environment.md?plain=1)
 - [ml-agents-envs/README.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/README.md?plain=1)
 - [ml-agents-envs/mlagents_envs/registry/binary_utils.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/registry/binary_utils.py)
 - [ml-agents-envs/setup.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/setup.py)
 - [ml-agents/README.md](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/README.md?plain=1)
 - [ml-agents/setup.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/setup.py)
 - [utils/validate_release_links.py](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/utils/validate_release_links.py)
 
  This document provides a comprehensive guide for setting up and using the ML-Agents toolkit. It covers Python package installation, Unity package setup, CLI tool usage, and development environment configuration.

 For information about training configuration and parameters, see [Training Configuration Files](https://deepwiki.com/Unity-Technologies/ml-agents/5.2-training-configuration-files). For details about the CI/CD testing pipeline, see [Testing and CI/CD](https://deepwiki.com/Unity-Technologies/ml-agents/5.3-testing-and-cicd).

 
## Python Environment Setup

 The ML-Agents toolkit consists of two main Python packages that must be installed in the correct order. The minimum supported version is Python 3.10.12 [docs/Migrating.md7-9](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Migrating.md?plain=1#L7-L9)

 
### Package Dependencies

 
```

```

 
### Installation Process

 The standard installation requires Python 3.10.12 [docs/Installation.md40-42](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L40-L42) It is highly recommended to use a virtual environment like `conda` or `venv` [docs/Using-Virtual-Environment.md1-13](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Using-Virtual-Environment.md?plain=1#L1-L13)

 
```

```

 The `mlagents` package provides several CLI entry points defined in [ml-agents/setup.py79-85](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/setup.py#L79-L85):

 
| Command | Purpose | Code Reference |
|---|---|---|
| mlagents-learn | Main training CLI | mlagents.trainers.learn:main |
| mlagents-run-experiment | Experiment runner | mlagents.trainers.run_experiment:main |
| mlagents-push-to-hf | HuggingFace upload | mlagents.utils.push_to_hf:main |
| mlagents-load-from-hf | HuggingFace download | mlagents.utils.load_from_hf:main |

 **Sources:** [ml-agents/setup.py56-78](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/setup.py#L56-L78) [ml-agents-envs/setup.py55-66](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/setup.py#L55-L66) [docs/Installation.md21-32](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L21-L32)

 
### Development Installation

 For development or modifying the source code, install packages in editable mode from a cloned repository [docs/Installation.md57-64](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L57-L64):

 
```

```

 **Sources:** [docs/Installation.md141-158](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L141-L158) [ml-agents/setup.py38-54](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/setup.py#L38-L54)

 
## Unity Package Installation

 The Unity ML-Agents C# SDK is distributed as the `com.unity.ml-agents` package [docs/Installation.md5-8](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L5-L8)

 
### Package Structure

 
```

```

 
### Installation Methods

 The official version of Unity supported is **6000.0** or later [docs/Migrating.md21-24](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Migrating.md?plain=1#L21-L24)

 
 - **Package Manager Registry**: Search for `com.unity.ml-agents` in the Unity Package Manager [docs/Installation.md94-98](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L94-L98)
 - **Local Disk**: Navigate to `Window` -> `Package Manager`, select `Add package from disk...`, and point to `com.unity.ml-agents/package.json` [docs/Installation.md103-114](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L103-L114)
 
 **Sources:** [docs/Installation.md34-38](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Installation.md?plain=1#L34-L38) [com.unity.ml-agents/Runtime/Agent.cs13-113](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Agent.cs#L13-L113)

 
## CLI Tools and Usage

 
### Main Training Command

 The primary interface for training is `mlagents-learn`. On Windows, if using visual observations, training is typically done in headless mode [docs/Training-on-Microsoft-Azure.md62-64](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Microsoft-Azure.md?plain=1#L62-L64)

 
```

```

 
### Command Flow

 
```

```

 
### Plugin System

 The toolkit includes a plugin system for extending statistics and trainer types [ml-agents/setup.py86-93](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/setup.py#L86-L93):

 
 - `ML_AGENTS_STATS_WRITER`: Handles how training metrics are logged (e.g., TensorBoard).
 - `ML_AG_TRAINER_TYPE`: Allows registration of custom RL algorithms.
 
 **Sources:** [ml-agents/setup.py79-93](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents/setup.py#L79-L93) [docs/Training-on-Microsoft-Azure.md75-80](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Microsoft-Azure.md?plain=1#L75-L80)

 
## Development Environment Setup

 
### Pre-commit Hooks

 The project uses `pre-commit` to ensure code quality across Python and C# [.pre-commit-config.yaml1-5](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ .pre-commit-config.yaml#L1-L5)

 
```

```

 
### Code Quality Tools

 
| Tool | Purpose | Files | Code Reference |
|---|---|---|---|
| black | Python formatting | *.py | .pre-commit-config.yaml2-11 |
| mypy | Static typing | ml-agents/ | .pre-commit-config.yaml13-27 |
| flake8 | Style linting | *.py | .pre-commit-config.yaml28-38 |
| dotnet format | C# formatting | *.cs | .pre-commit-config.yaml95-100 |

 **Sources:** [.pre-commit-config.yaml1-141](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/.pre-commit-config.yaml#L1-L141)

 
## Cloud and Specialized Setup

 
### Amazon Web Services (AWS)

 Instructions exist for using a pre-configured AMI (`ami-016ff5559334f8619`) or configuring a custom EC2 instance with X Server for visual observations [docs/Training-on-Amazon-Web-Service.md9-22](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Amazon-Web-Service.md?plain=1#L9-L22)

 
### Microsoft Azure

 Training can be performed on N-Series GPU VMs or via Azure Container Instances (ACI). Headless mode requires the `--no-graphics` flag [docs/Training-on-Microsoft-Azure.md12-22](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Microsoft-Azure.md?plain=1#L12-L22) [docs/Training-on-Microsoft-Azure.md62-64](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Microsoft-Azure.md?plain=1#L62-L64)

 
### Demonstration Recording

 For Imitation Learning, the `DemonstrationRecorder` component must be attached to an `Agent` in Unity to record `.demo` files [com.unity.ml-agents/Runtime/Demonstrations/DemonstrationRecorder.cs11-26](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Demonstrations/DemonstrationRecorder.cs#L11-L26)

 **Sources:** [docs/Training-on-Amazon-Web-Service.md51-60](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Amazon-Web-Service.md?plain=1#L51-L60) [docs/Training-on-Microsoft-Azure.md1-10](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/docs/Training-on-Microsoft-Azure.md?plain=1#L1-L10) [com.unity.ml-agents/Runtime/Demonstrations/DemonstrationRecorder.cs112-126](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/com.unity.ml-agents/Runtime/Demonstrations/DemonstrationRecorder.cs#L112-L126)

 
## Binary Environment Management

 
### Environment Registry

 The toolkit includes a binary utility system for downloading and managing Unity environments programmatically.

 
```

```

 
### Binary Utilities

 The `binary_utils.py` module provides platform-specific path resolution [ml-agents-envs/mlagents_envs/registry/binary_utils.py27-40](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/registry/binary_utils.py#L27-L40):

 
 - **Linux**: Appends `.x86_64`
 - **Windows**: Appends `.exe`
 - **macOS**: Appends `.app`
 
 **Sources:** [ml-agents-envs/mlagents_envs/registry/binary_utils.py27-104](https://github.com/Unity-Technologies/ml-agents/blob/d52b0062/ml-agents-envs/mlagents_envs/registry/binary_utils.py#L27-L104)
