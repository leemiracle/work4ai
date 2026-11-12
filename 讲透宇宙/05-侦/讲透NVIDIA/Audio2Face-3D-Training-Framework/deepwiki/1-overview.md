<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Audio2Face-3D-Training-Framework · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [configs/example-diffusion-min/config_train.py](configs/example-diffusion-min/config_train.py)
- [configs/example-diffusion/config_train.py](configs/example-diffusion/config_train.py)
- [configs/example-regression-min/config_train.py](configs/example-regression-min/config_train.py)
- [docker/run_preproc.sh](docker/run_preproc.sh)
- [docker/run_shell.sh](docker/run_shell.sh)
- [docs/config_details.md](docs/config_details.md)
- [docs/training_framework.md](docs/training_framework.md)

</details>



This document provides a comprehensive overview of the Audio2Face-3D Training Framework, explaining its architecture, core components, and execution model. The framework is a containerized system designed to train high-fidelity facial animation models that generate realistic facial movements, including skin, jaw, tongue, and eye animations, from audio input.

For detailed configuration parameters, see [Configuration System](#3). For data preparation requirements, see [Data Preparation](#4). For training specifics, see [Training Framework](#5).

## System Purpose and Capabilities

The Audio2Face-3D Training Framework enables users to train custom facial animation models from synchronized audio-visual datasets. The system supports two primary model architectures:

- **Regression Models**: Standard approach using PCA-compressed geometry with faster training
- **Diffusion Models**: Advanced approach using absolute pose representation with higher fidelity output

The framework operates entirely within Docker containers and follows a sequential four-stage pipeline: preprocessing, training, deployment, and inference.

**Sources:** [README.md:9-13](), [docs/training_framework.md:12-25]()

## System Architecture

The framework consists of interconnected systems that process facial animation data through a standardized pipeline:

```mermaid
graph TB
    subgraph "Audio2Face-3D Training Framework"
        subgraph "Configuration Layer"
            ConfigBase["`audio2face/config_base/
            config_dataset_base.py
            config_train_regression_base.py
            config_train_diffusion_base.py`"]
            ConfigUser["`configs/<CONFIG_NAME>/
            config_dataset.py
            config_train.py
            config_inference.py`"]
        end
        
        subgraph "Execution Pipeline"
            RunPreproc["run_preproc.py"]
            RunTrain["run_train.py"]
            RunDeploy["run_deploy.py"] 
            RunInference["run_inference.py"]
        end
        
        subgraph "Core Systems"
            DataPipeline["Data Processing Pipeline"]
            TrainingEngine["Training Engine"]
            AudioProcessor["Audio Processing"]
            DiffusionEngine["Gaussian Diffusion"]
        end
        
        subgraph "Containerization"
            DockerEnv["`docker/run_*.sh
            audio2face-framework-env:latest`"]
        end
        
        subgraph "Output Artifacts"
            PreprocArtifacts["/workspace/output_preproc"]
            TrainArtifacts["/workspace/output_train"]
            DeployArtifacts["/workspace/output_deploy"]
        end
    end
    
    ConfigBase --> ConfigUser
    ConfigUser --> RunPreproc
    RunPreproc --> DataPipeline
    DataPipeline --> PreprocArtifacts
    PreprocArtifacts --> RunTrain
    RunTrain --> TrainingEngine
    TrainingEngine --> AudioProcessor
    TrainingEngine --> DiffusionEngine
    TrainingEngine --> TrainArtifacts
    TrainArtifacts --> RunDeploy
    RunDeploy --> DeployArtifacts
    DeployArtifacts --> RunInference
    
    DockerEnv --> RunPreproc
    DockerEnv --> RunTrain  
    DockerEnv --> RunDeploy
    DockerEnv --> RunInference
```

**Sources:** [docs/training_framework.md:28-44](), [docker/run_preproc.sh:18-44](), [README.md:172-238]()

## Core Component Architecture

This diagram shows the relationship between high-level system concepts and their corresponding code entities:

```mermaid
graph TD
    subgraph "Data Layer"
        AudioRoot["`AUDIO_ROOT
        16kHz+ WAV files`"]
        SkinCache["`SKIN_CACHE_ROOT
        Maya cache/PC2/NPY`"]
        TongueCache["`TONGUE_CACHE_ROOT
        Tongue mesh data`"]
        JawData["`JAW_ANIM_DATA_FPATH
        NPZ transforms`"]
        EyeData["`EYE_ANIM_DATA_FPATH
        Eye rotations/blinks`"]
    end
    
    subgraph "Processing Systems"
        AudioMethods["`AUDIO_PREPROC_METHOD
        w2v | nva2f`"]
        PCAsystem["`SKIN_PCA_VARIANCE_THRESHOLD
        Dimensionality reduction`"]
        PhonemeAlign["`Charsiu alignment
        PHONEME_FORCING_LANGS`"]
    end
    
    subgraph "Model Architectures"
        NetworkReg["`NETWORK_TYPE: regression
        NETWORK_NAME: conv_w2v_autocorr`"]
        NetworkDiff["`NETWORK_TYPE: diffusion  
        NETWORK_NAME: diffusion_rnn`"]
    end
    
    subgraph "Target Channels"
        TargetChannels["`TARGET_CHANNELS
        skin_coeffs | skin_pose
        tongue_coeffs | tongue_pose
        jaw | eye`"]
    end
    
    subgraph "Loss Functions"
        LossFunctions["`LOSS_MSE_ALPHA
        LOSS_MOTION_ALPHA
        LOSS_LIP_DIST_ALPHA
        LOSS_PHONEME_ALPHA`"]
    end
    
    AudioRoot --> AudioMethods
    SkinCache --> PCAsystem
    AudioMethods --> PhonemeAlign
    
    PCAsystem --> TargetChannels
    PhonemeAlign --> NetworkReg
    PhonemeAlign --> NetworkDiff
    
    TargetChannels --> NetworkReg
    TargetChannels --> NetworkDiff
    
    NetworkReg --> LossFunctions
    NetworkDiff --> LossFunctions
```

**Sources:** [docs/config_details.md:24-143](), [docs/config_details.md:414-419](), [docs/config_details.md:518-534]()

## Execution Pipeline

The framework executes through four sequential stages, each handled by dedicated Python scripts running in Docker containers:

```mermaid
graph LR
    subgraph "Stage 1: Preprocessing"
        Input1["`Raw Dataset
        /datasets/`"]
        Script1["`python run_preproc.py
        <CONFIG_NAME> <ACTOR_NAME>`"]
        Output1["`PCA Coefficients
        Audio Features
        /workspace/output_preproc/`"]
    end
    
    subgraph "Stage 2: Training"
        Input2["`PREPROC_RUN_NAME_FULL
        CLIPS configuration`"]
        Script2["`python run_train.py
        <CONFIG_NAME>`"]
        Output2["`Trained Networks
        /workspace/output_train/`"]
    end
    
    subgraph "Stage 3: Deployment"
        Input3["`TRAINING_RUN_NAME_FULL
        Network checkpoints`"]
        Script3["`python run_deploy.py
        <CONFIG_NAME> <RUN_NAME>`"]
        Output3["`Maya-ACE Ready Models
        /workspace/output_deploy/`"]
    end
    
    subgraph "Stage 4: Inference"
        Input4["`Deployed models
        Audio input`"]
        Script4["`python run_inference.py
        <CONFIG_NAME> <RUN_NAME>`"]
        Output4["`Generated Animation
        NPY/Maya cache`"]
    end
    
    Output1 --> Input2
    Output2 --> Input3  
    Output3 --> Input4
    
    Script1 --> Output1
    Script2 --> Output2
    Script3 --> Output3
    Script4 --> Output4
```

**Sources:** [README.md:175-238](), [docs/training_framework.md:104-151]()

## Configuration System Architecture

The framework implements a two-tier configuration system that separates base parameter definitions from user customizations:

| Layer | Location | Purpose | Key Files |
|-------|----------|---------|-----------|
| Base Layer | `audio2face/config_base/` | Parameter definitions with defaults | `config_dataset_base.py`, `config_train_regression_base.py`, `config_train_diffusion_base.py` |
| User Layer | `configs/<CONFIG_NAME>/` | User overrides and customizations | `config_dataset.py`, `config_train.py`, `config_inference.py` |

### Configuration Merge Process

```mermaid
graph LR
    BaseConfigs["`Base Configurations
    audio2face/config_base/
    All parameters + defaults`"]
    UserConfigs["`User Configurations  
    configs/<CONFIG_NAME>/
    Override parameters only`"]
    RuntimeMerge["`Runtime Merge Process
    User overrides base`"]
    FinalConfig["`Final Configuration
    Passed to framework modules`"]
    
    BaseConfigs --> RuntimeMerge
    UserConfigs --> RuntimeMerge
    RuntimeMerge --> FinalConfig
```

**Sources:** [docs/training_framework.md:48-101](), [docs/config_details.md:1-13]()

## Model Types and Capabilities

The framework supports two distinct neural network architectures with different characteristics:

### Regression Models

- **Network Class**: `conv_w2v_autocorr`
- **Target Representation**: PCA coefficients (`skin_coeffs`, `tongue_coeffs`)
- **Batch Processing**: `BATCH_SIZE = 32`, `SEQ_LEN = 2`
- **Training Features**: Phoneme supervision, emotion embeddings
- **Use Case**: Standard approach with faster training and good quality

### Diffusion Models

- **Network Class**: `diffusion_rnn` 
- **Target Representation**: Absolute poses (`skin_pose`, `tongue_pose`)
- **Batch Processing**: `BATCH_SIZE = 1`, `GRADIENT_ACCUMULATION_STEPS = 4`
- **Training Features**: `DIFFUSION_STEPS = 1000`, temporal RNN modeling
- **Use Case**: Advanced approach with higher fidelity output

| Feature | Regression | Diffusion |
|---------|------------|-----------|
| Data Representation | PCA compressed | Absolute geometry |
| Sequence Handling | Fixed length (`SEQ_LEN`) | Variable length |
| Training Speed | Faster | Slower |
| Output Quality | Good | Higher fidelity |
| Memory Usage | Lower | Higher |

**Sources:** [configs/example-regression-min/config_train.py:25](), [configs/example-diffusion-min/config_train.py:25](), [docs/config_details.md:356-360]()

---

