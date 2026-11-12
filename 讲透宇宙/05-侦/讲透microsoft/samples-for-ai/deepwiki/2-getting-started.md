<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/samples-for-ai · page 2 Getting Started · fetched 2026-10-26 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/download_data.md](docs/download_data.md)
- [docs/local_run.md](docs/local_run.md)
- [docs/prerequisites.md](docs/prerequisites.md)
- [docs/submit_job_to_pai.md](docs/submit_job_to_pai.md)
- [examples/README.md](examples/README.md)
- [installer/gpu_detector_linux](installer/gpu_detector_linux)
- [installer/gpu_detector_mac](installer/gpu_detector_mac)
- [installer/gpu_detector_win.exe](installer/gpu_detector_win.exe)
- [installer/install.py](installer/install.py)
- [projects/StyleTransfer/StyleTransferTraining/src/README.md](projects/StyleTransfer/StyleTransferTraining/src/README.md)
- [zh-hans/README.md](zh-hans/README.md)
- [zh-hant/README.md](zh-hant/README.md)

</details>



This page provides an overview of how to set up your development environment and start working with the samples-for-ai repository. It covers the initial setup process, system architecture, and basic workflow to get you running AI/ML examples across multiple frameworks.

For detailed installation procedures and environment configuration, see [Installation and Environment Setup](#2.1). For Visual Studio integration and development tools setup, see [Visual Studio and Development Tools](#2.2). For information about the available framework examples and projects, see [Framework Examples](#3).

## System Overview

The samples-for-ai repository consists of three main components: an automated installer system, framework-specific example collections, and development environment integrations.

```mermaid
graph TB
    subgraph "Core Installation System"
        INSTALLER["install.py<br/>Automated Setup"]
        GPU_DETECTOR["gpu_detector_*<br/>Hardware Detection"]
        SYS_INFO["sys_info<br/>System Configuration"]
    end
    
    subgraph "Framework Examples"
        TF_EXAMPLES["TensorflowExamples.sln<br/>MNIST, CIFAR-10, YOLO"]
        PYTORCH_EXAMPLES["PyTorchExamples.sln<br/>Transfer Learning, Sentiment"]
        KERAS_EXAMPLES["KerasExamples.sln<br/>GANs, DenseNet, CapsNet"]
        CNTK_EXAMPLES["CNTK Examples<br/>BrainScript & Python"]
    end
    
    subgraph "Development Environment"
        VS_TOOLS["Visual Studio Tools for AI"]
        VSCODE_TOOLS["VS Code Tools for AI"]
        OPENPAI["OpenPAI Integration<br/>Distributed Training"]
    end
    
    INSTALLER --> GPU_DETECTOR
    INSTALLER --> SYS_INFO
    SYS_INFO --> TF_EXAMPLES
    SYS_INFO --> PYTORCH_EXAMPLES
    SYS_INFO --> KERAS_EXAMPLES
    SYS_INFO --> CNTK_EXAMPLES
    
    VS_TOOLS --> TF_EXAMPLES
    VS_TOOLS --> PYTORCH_EXAMPLES
    VS_TOOLS --> OPENPAI
    VSCODE_TOOLS --> KERAS_EXAMPLES
    VSCODE_TOOLS --> CNTK_EXAMPLES
```

Sources: [installer/install.py:16-26](), [README.md:9-24](), [examples/README.md:3-13]()

## Prerequisites Summary

Before using the samples, ensure you have the following baseline requirements:

| Component | Requirement | Detection Function |
|-----------|-------------|-------------------|
| Operating System | 64-bit Windows 10, Linux, or macOS | `detect_os()` |
| Python | Version 3.5 or 3.6 | `detect_python_version()` |
| GPU (Optional) | NVIDIA GPU with CUDA support | `detect_gpu()` |
| CUDA | Version 8.0 or 9.0 (if GPU present) | `detect_cuda_()` |
| Development IDE | Visual Studio 2015/2017 or VS Code | `detect_vs()` |

The installation system automatically detects your hardware and software configuration through the `sys_info` dictionary in [installer/install.py:16-26]().

Sources: [installer/install.py:251-275](), [installer/install.py:315-332](), [installer/install.py:278-294](), [docs/prerequisites.md:20-24]()

## Quick Start Workflow

The typical workflow for getting started involves system detection, automated installation, and running your first example:

```mermaid
graph TD
    START["Clone Repository"]
    DETECT["System Detection<br/>detect_os(), detect_gpu()<br/>detect_python_version()"]
    INSTALL["Run install.py<br/>Framework Installation"]
    VALIDATE["Environment Validation<br/>sys_info populated"]
    CHOOSE["Select Framework Example<br/>TensorFlow, PyTorch, Keras, CNTK"]
    RUN["Execute Sample<br/>Local or OpenPAI"]
    
    START --> DETECT
    DETECT --> INSTALL
    INSTALL --> VALIDATE
    VALIDATE --> CHOOSE
    CHOOSE --> RUN
    
    subgraph "Installation Options"
        USER_INSTALL["--user flag<br/>User directory install"]
        CUDA80["--cuda80 flag<br/>Force CUDA 8.0"]
        SYSTEM_INSTALL["System-wide install<br/>Requires admin rights"]
    end
    
    INSTALL --> USER_INSTALL
    INSTALL --> CUDA80
    INSTALL --> SYSTEM_INSTALL
```

Sources: [docs/prerequisites.md:26-47](), [installer/install.py:119-141](), [installer/install.py:629-653]()

## Installation Process Overview

The automated installer ([installer/install.py]()) handles the complete setup process through several key phases:

### System Detection Phase
The installer first detects your system configuration using these functions:
- `detect_os()` - Determines platform (`TOOLSFORAI_OS_WIN`, `TOOLSFORAI_OS_LINUX`, `TOOLSFORAI_OS_MACOS`)
- `detect_gpu()` - Checks for NVIDIA GPU availability using platform-specific detectors
- `detect_python_version()` - Validates Python 3.5/3.6 installation
- `detect_cuda_()` - Identifies CUDA version if GPU is present

### Framework Installation Phase  
Based on the detected configuration, the installer installs appropriate frameworks:
- `pip_install_tensorflow()` - TensorFlow with GPU support if available
- `pip_install_pytorch()` - PyTorch with CUDA bindings
- `pip_install_keras()` - Keras with backend configuration
- `pip_install_cntk()` - Microsoft Cognitive Toolkit

### Environment Configuration
The installer updates system environment variables and validates the installation through the `sys_info` dictionary which tracks:
- OS platform and architecture
- GPU availability and CUDA version
- Installed framework versions
- Python environment details

Sources: [installer/install.py:251-275](), [installer/install.py:692-701](), [installer/install.py:704-725](), [installer/install.py:727-745]()

## Example Structure

Once installation is complete, you can access framework-specific examples organized in Visual Studio solution format:

```mermaid
graph LR
    subgraph "Solution Files"
        TF_SLN["TensorflowExamples.sln"]
        PT_SLN["PyTorchExamples.sln"] 
        KERAS_SLN["KerasExamples.sln"]
        CNTK_SLN["CNTK Solutions"]
    end
    
    subgraph "Common Datasets"
        MNIST["MNIST<br/>Handwritten Digits"]
        CIFAR10["CIFAR-10<br/>Image Classification"]  
        COCO["MS COCO<br/>Object Detection"]
    end
    
    subgraph "Training Options"
        LOCAL["Local Training<br/>CPU/GPU"]
        OPENPAI_SUBMIT["OpenPAI Submission<br/>Distributed Training"]
    end
    
    TF_SLN --> MNIST
    TF_SLN --> CIFAR10
    PT_SLN --> MNIST
    PT_SLN --> COCO
    KERAS_SLN --> MNIST
    
    TF_SLN --> LOCAL
    PT_SLN --> LOCAL  
    TF_SLN --> OPENPAI_SUBMIT
    PT_SLN --> OPENPAI_SUBMIT
```

Sources: [examples/README.md:3-13](), [docs/local_run.md:5-12](), [docs/submit_job_to_pai.md:15-23]()

## Next Steps

After completing the basic setup:

1. **Environment Setup**: Follow the detailed installation guide in [Installation and Environment Setup](#2.1) to run the `install.py` script and configure your development environment.

2. **Development Tools**: Set up Visual Studio or VS Code integration using [Visual Studio and Development Tools](#2.2) for enhanced debugging and project management.

3. **Choose a Framework**: Explore the available examples in [Framework Examples](#3) to find implementations that match your learning objectives or project requirements.

4. **Data Preparation**: Review data download requirements in the framework-specific documentation, as most examples can automatically download datasets but some require manual setup.

5. **Run First Example**: Start with basic examples like MNIST digit recognition to validate your environment before moving to more complex projects.

The automated installer significantly simplifies the traditionally complex process of setting up multiple AI frameworks with proper GPU support and dependency management.

Sources: [README.md:26-38](), [docs/download_data.md:1-9](), [docs/local_run.md:1-17]()

---

