<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Audio2Face-3D-Training-Framework · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/example-diffusion-min/config_preproc.py](configs/example-diffusion-min/config_preproc.py)
- [configs/example-diffusion/config_preproc.py](configs/example-diffusion/config_preproc.py)
- [configs/example-regression-min/config_preproc.py](configs/example-regression-min/config_preproc.py)
- [configs/example-regression/config_preproc.py](configs/example-regression/config_preproc.py)
- [docker/run_deploy.sh](docker/run_deploy.sh)
- [docker/run_inference.sh](docker/run_inference.sh)
- [docker/run_shell.sh](docker/run_shell.sh)
- [docker/run_train.sh](docker/run_train.sh)
- [docs/training_framework.md](docs/training_framework.md)

</details>



This page provides the essential setup and installation steps needed to begin using the Audio2Face-3D Training Framework. It covers system requirements, Docker environment setup, and the basic workflow to train your first model.

For detailed configuration parameters, see [Configuration System](#3). For data preparation requirements, see [Data Preparation](#4). For advanced training concepts, see [Training Framework](#5).

## Prerequisites

Before installing the framework, ensure your system meets the minimum requirements:

| Requirement | Specification |
|------------|---------------|
| **Storage** | Minimum 1 GB free disk space |
| **Hardware** | CUDA-compatible NVIDIA GPU with ≥6 GB VRAM |
| **NVIDIA Driver** | Linux: 575.57-579.x, Windows/WSL2: 576.57-579.x |
| **Operating System** | Linux or Windows with WSL2 |

**Container Architecture**

```mermaid
graph TD
    subgraph "Host System"
        HostOS["Host OS<br/>(Linux/Windows+WSL2)"]
        NvidiaDriver["NVIDIA Driver<br/>(575.57-579.x)"]
        DockerEngine["Docker Engine"]
        NvidiaToolkit["NVIDIA Container Toolkit"]
    end
    
    subgraph "Docker Container: audio2face-framework-env:latest"
        ContainerOS["Ubuntu Container"]
        PythonEnv["Python 3.10 Environment"]
        CudaRuntime["CUDA Runtime"]
        A2FFramework["Audio2Face Framework"]
    end
    
    subgraph "Volume Mounts"
        DatasetsVol["/datasets ← A2F_DATASETS_ROOT"]
        WorkspaceVol["/workspace ← A2F_WORKSPACE_ROOT"] 
        FrameworkVol["/framework ← A2F_FRAMEWORK_ROOT"]
    end
    
    HostOS --> DockerEngine
    NvidiaDriver --> NvidiaToolkit
    DockerEngine --> ContainerOS
    NvidiaToolkit --> CudaRuntime
    
    DatasetsVol -.-> ContainerOS
    WorkspaceVol -.-> ContainerOS
    FrameworkVol -.-> ContainerOS
```

Sources: [docs/training_framework.md:261-272](), [docker/run_shell.sh:31-43]()

## Installation Steps

### 1. Clone the Repository

```bash
mkdir -p ~/audio2face && cd ~/audio2face
git clone https://github.com/NVIDIA/Audio2Face-3D-Training-Framework.git
```

### 2. Create Directory Structure

```bash
mkdir -p ~/audio2face/datasets
mkdir -p ~/audio2face/workspace
cd ~/audio2face/Audio2Face-3D-Training-Framework
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
nano .env
```

Set the following paths in `.env`:
```bash
A2F_DATASETS_ROOT="/absolute/path/to/datasets"
A2F_WORKSPACE_ROOT="/absolute/path/to/workspace" 
A2F_FRAMEWORK_ROOT="/absolute/path/to/Audio2Face-3D-Training-Framework"
```

### 4. Build Docker Container

```bash
chmod +x docker/*.sh
./docker/build_docker.sh
```

Sources: [docs/training_framework.md:405-461]()

## Framework Architecture

**Execution Environment Structure**

```mermaid
graph TB
    subgraph "Host File System"
        EnvFile[".env<br/>Environment Configuration"]
        DatasetDir["~/audio2face/datasets/<br/>Raw Training Data"]
        WorkspaceDir["~/audio2face/workspace/<br/>Processing Outputs"]
        FrameworkDir["~/audio2face/Audio2Face-3D-Training-Framework/<br/>Framework Code"]
    end
    
    subgraph "Docker Scripts (docker/)"
        RunShell["run_shell.sh<br/>Interactive Development"]
        RunPreproc["run_preproc.sh<br/>Data Preprocessing"]
        RunTrain["run_train.sh<br/>Model Training"] 
        RunDeploy["run_deploy.sh<br/>Model Deployment"]
        RunInference["run_inference.sh<br/>Inference Testing"]
    end
    
    subgraph "Container Execution"
        ContainerMounts["/datasets, /workspace, /framework<br/>Volume Mounts"]
        PythonRunners["runners/<br/>run_preproc.py<br/>run_train.py<br/>run_deploy.py<br/>run_inference.py"]
        ConfigSystem["configs/<CONFIG_NAME>/<br/>User Configuration Overrides"]
    end
    
    EnvFile --> RunShell
    EnvFile --> RunPreproc  
    EnvFile --> RunTrain
    EnvFile --> RunDeploy
    EnvFile --> RunInference
    
    DatasetDir -.-> ContainerMounts
    WorkspaceDir -.-> ContainerMounts
    FrameworkDir -.-> ContainerMounts
    
    RunShell --> ContainerMounts
    RunPreproc --> PythonRunners
    RunTrain --> PythonRunners
    RunDeploy --> PythonRunners
    RunInference --> PythonRunners
    
    ConfigSystem --> PythonRunners
```

Sources: [docs/training_framework.md:26-44](), [docker/run_shell.sh:18-43](), [docker/run_train.sh:18-44]()

## Configuration Overview

The framework uses a two-tier configuration system where base configurations define all available parameters, and user configurations override specific values for your use case.

**Configuration System Architecture**

```mermaid
graph LR
    subgraph "Base Configurations (audio2face/config_base/)"
        ConfigDatasetBase["config_dataset_base.py<br/>Dataset parameters"]
        ConfigPreprocBase["config_preproc_base.py<br/>Preprocessing parameters"]
        ConfigTrainRegBase["config_train_regression_base.py<br/>Regression training"]
        ConfigTrainDiffBase["config_train_diffusion_base.py<br/>Diffusion training"]
        ConfigInfRegBase["config_inference_regression_base.py<br/>Regression inference"]
        ConfigInfDiffBase["config_inference_diffusion_base.py<br/>Diffusion inference"]
    end
    
    subgraph "User Configuration (configs/<CONFIG_NAME>/)"
        ConfigDataset["config_dataset.py<br/>Dataset overrides"]
        ConfigPreproc["config_preproc.py<br/>Preprocessing overrides"] 
        ConfigTrain["config_train.py<br/>Training overrides"]
        ConfigInference["config_inference.py<br/>Inference overrides"]
    end
    
    subgraph "Example Configurations"
        ExampleDiffusion["example-diffusion/<br/>Full diffusion setup"]
        ExampleDiffusionMin["example-diffusion-min/<br/>Minimal diffusion setup"]
        ExampleRegression["example-regression/<br/>Full regression setup"] 
        ExampleRegressionMin["example-regression-min/<br/>Minimal regression setup"]
    end
    
    ConfigDatasetBase -.->|"Base defaults"| ConfigDataset
    ConfigPreprocBase -.->|"Base defaults"| ConfigPreproc
    ConfigTrainRegBase -.->|"Base defaults"| ConfigTrain
    ConfigTrainDiffBase -.->|"Base defaults"| ConfigTrain
    
    ExampleDiffusion --> ConfigDataset
    ExampleDiffusion --> ConfigPreproc
    ExampleDiffusion --> ConfigTrain
    
    ExampleRegression --> ConfigDataset
    ExampleRegression --> ConfigPreproc  
    ExampleRegression --> ConfigTrain
```

Sources: [docs/training_framework.md:48-100](), [configs/example-diffusion/config_preproc.py:16-20](), [configs/example-regression/config_preproc.py:16-20]()

## Quick Start Workflow

The complete training pipeline consists of four sequential stages, each executed through Docker scripts:

**Pipeline Execution Flow**

```mermaid
graph TD
    subgraph "Stage 1: Data Preprocessing"
        ConfigDatasetPy["configs/<CONFIG_NAME>/config_dataset.py<br/>Dataset paths and parameters"]
        ConfigPreprocPy["configs/<CONFIG_NAME>/config_preproc.py<br/>RUN_NAME, preprocessing settings"]
        RunPreprocCmd["python run_preproc.py <CONFIG_NAME> <ACTOR_NAME>"]
        PreprocOutput["workspace/output_preproc/<PREPROC_RUN_NAME_FULL><br/>PCA coefficients, audio features"]
    end
    
    subgraph "Stage 2: Model Training"
        ConfigTrainPy["configs/<CONFIG_NAME>/config_train.py<br/>PREPROC_RUN_NAME_FULL, CLIPS, model params"]
        RunTrainCmd["python run_train.py <CONFIG_NAME>"]
        TrainOutput["workspace/output_train/<TRAINING_RUN_NAME_FULL><br/>Trained model weights"]
    end
    
    subgraph "Stage 3: Model Deployment"
        ConfigInferencePy["configs/<CONFIG_NAME>/config_inference.py<br/>Post-processing parameters"]
        RunDeployCmd["python run_deploy.py <CONFIG_NAME> <TRAINING_RUN_NAME_FULL>"]
        DeployOutput["workspace/output_deploy/<TRAINING_RUN_NAME_FULL><br/>Maya-ACE compatible model"]
    end
    
    subgraph "Stage 4: Inference Testing"
        RunInferenceCmd["python run_inference.py <CONFIG_NAME> <TRAINING_RUN_NAME_FULL>"]
        InferenceOutput["Animation results for validation"]
    end
    
    ConfigDatasetPy --> RunPreprocCmd
    ConfigPreprocPy --> RunPreprocCmd
    RunPreprocCmd --> PreprocOutput
    
    PreprocOutput --> ConfigTrainPy
    ConfigTrainPy --> RunTrainCmd
    RunTrainCmd --> TrainOutput
    
    TrainOutput --> ConfigInferencePy
    ConfigInferencePy --> RunDeployCmd
    RunDeployCmd --> DeployOutput
    
    DeployOutput --> RunInferenceCmd
    RunInferenceCmd --> InferenceOutput
```

Sources: [docs/training_framework.md:102-152]()

## Basic Usage Example

### 1. Start with Example Configuration

Copy one of the provided example configurations:
- `configs/example-diffusion/` - Advanced diffusion-based training
- `configs/example-regression/` - Standard regression-based training  
- `configs/example-diffusion-min/` - Minimal diffusion setup
- `configs/example-regression-min/` - Minimal regression setup

### 2. Configure Your Dataset

Edit `configs/<CONFIG_NAME>/config_dataset.py`:
```python
ACTOR_NAMES = ["your_actor_name"]
AUDIO_ROOT = "/datasets/your_dataset/audio"
SKIN_CACHE_ROOT = "/datasets/your_dataset/cache/skin"
```

### 3. Run Preprocessing

```bash
python run_preproc.py <CONFIG_NAME> <ACTOR_NAME>
```

### 4. Configure Training

Edit `configs/<CONFIG_NAME>/config_train.py` to reference the preprocessing output:
```python
PREPROC_RUN_NAME_FULL = {"actor_name": "YYYYMMDD_HHMMSS_actor_name"}
```

### 5. Run Training

```bash
python run_train.py <CONFIG_NAME>
```

### 6. Deploy Model

```bash
python run_deploy.py <CONFIG_NAME> <TRAINING_RUN_NAME_FULL>
```

Sources: [docs/training_framework.md:104-152](), [configs/example-diffusion-min/config_preproc.py:17-20]()

## Development Environment

For interactive development and debugging, use the development shell:

```bash
./docker/run_shell.sh
```

This provides:
- Interactive container access with all framework dependencies
- Volume mounts for live code editing
- GPU access for development testing
- Full Python environment with debugging capabilities

Sources: [docker/run_shell.sh:31-43](), [docs/training_framework.md:193-257]()

## Next Steps

After completing basic setup:

1. **Prepare Your Data**: See [Data Preparation](#4) for detailed requirements on audio files, animation caches, and geometry data
2. **Configure Training**: See [Configuration System](#3) for comprehensive parameter documentation  
3. **Understand Model Types**: See [Training Framework](#5) for details on regression vs diffusion models
4. **Deploy to Maya**: See [Deployment and Inference](#6) for Maya-ACE integration

The framework supports both single-actor and multi-actor training scenarios. For production workflows, review the complete configuration system to optimize training parameters for your specific dataset characteristics.

Sources: [docs/training_framework.md:100](), [docs/training_framework.md:154-192]()

---

