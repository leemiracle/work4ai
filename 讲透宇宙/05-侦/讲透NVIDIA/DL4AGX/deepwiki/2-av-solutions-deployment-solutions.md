<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DL4AGX · page 2 AV-Solutions: Deployment Solutions · fetched 2026-10-26 -->

# AV-Solutions: Deployment Solutions

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AV-Solutions/README.md](AV-Solutions/README.md)
- [README.md](README.md)

</details>



## Purpose and Scope

The AV-Solutions directory provides deployment solutions for state-of-the-art autonomous vehicle models on NVIDIA DRIVE platforms using TensorRT. This system encompasses model optimization techniques, hardware-specific deployment pipelines, and inference applications designed for production autonomous vehicle systems.

This document covers the overall architecture and organization of deployment solutions. For detailed information about efficient model architectures designed for deployment, see [Models: Efficient Architectures](#3). For specific deployment workflows and implementation details of individual solutions, refer to the respective subsection pages [2.1](#2.1) through [2.7](#2.7).

## System Architecture

### Overall Deployment Pipeline

```mermaid
graph TD
    A["PyTorch Models"] --> B["ONNX Export"]
    B --> C["Model Optimization"]
    C --> D["TensorRT Engine Build"]
    D --> E["NVIDIA Drive Orin Deployment"]
    
    subgraph OPT ["Optimization Techniques"]
        C1["INT8 Quantization"]
        C2["Structured Sparsity"]
        C3["Explicit Quantization"]
        C4["Multi-device Pipeline"]
    end
    
    subgraph TOOLS ["Development Tools"]
        T1["onnx-export-guidance/"]
        T2["SparsityINT8/"]
        T3["mtmi/"]
    end
    
    subgraph DEPLOY ["Model Deployments"]
        D1["streampetr-trt/"]
        D2["uniad-trt/"]
        D3["bevformer-int8-eq/"]
        D4["far3d-trt/"]
        D5["dcnv4-trt/"]
        D6["vad-trt/"]
        D7["petr-trt/"]
        D8["llms-trtllm/"]
    end
    
    C --> C1
    C --> C2
    C --> C3
    C --> C4
    
    T1 --> B
    T2 --> C2
    T3 --> C4
    
    D --> D1
    D --> D2
    D --> D3
    D --> D4
    D --> D5
    D --> D6
    D --> D7
    D --> D8
```

Sources: [AV-Solutions/README.md:1-37](), [README.md:8-19]()

### Model Categories and Solutions Mapping

```mermaid
graph LR
    subgraph CATEGORIES ["Model Categories"]
        A["3D Object Detection"]
        B["BEV Perception"]
        C["End-to-End Driving"]
        D["Language Models"]
        E["Specialized Components"]
    end
    
    subgraph SOLUTIONS ["Deployment Solutions"]
        A --> A1["streampetr-trt/"]
        A --> A2["far3d-trt/"]
        A --> A3["petr-trt/"]
        A --> A4["vad-trt/"]
        
        B --> B1["bevformer-int8-eq/"]
        
        C --> C1["uniad-trt/"]
        
        D --> D1["llms-trtllm/"]
        
        E --> E1["dcnv4-trt/"]
    end
    
    subgraph TECHNIQUES ["Optimization Techniques"]
        T1["SparsityINT8/"]
        T2["mtmi/"]
        T3["onnx-export-guidance/"]
    end
    
    A1 --> T1
    B1 --> T1
    C1 --> T2
    A1 --> T3
    B1 --> T3
```

Sources: [AV-Solutions/README.md:13-35]()

## Deployment Solutions Overview

The AV-Solutions system is organized into three main categories: model-specific deployment solutions, optimization techniques, and development tools.

### Model-Specific Deployments

| Solution | Target Model | Primary Focus | Hardware Target |
|----------|--------------|---------------|-----------------|
| `streampetr-trt/` | [StreamPETR](https://github.com/exiawsh/StreamPETR) | 3D Object Detection | NVIDIA Drive Orin |
| `uniad-trt/` | [UniAD](https://arxiv.org/abs/2212.10156) | End-to-End Autonomous Driving | NVIDIA Drive Orin |
| `dcnv4-trt/` | [DCNv4](https://github.com/OpenGVLab/DCNv4) | Deformable Convolution Optimization | NVIDIA Drive Orin |
| `bevformer-int8-eq/` | [BEVFormer](https://github.com/fundamentalvision/BEVFormer) | BEV Perception with INT8 | NVIDIA GPUs |
| `far3d-trt/` | [Far3D](https://github.com/megvii-research/Far3D) | 3D Object Detection | NVIDIA Drive Orin |
| `llms-trtllm/` | Llama-3.1-8B, DeepSeek-R1 | Large Language Models | NVIDIA Drive Orin |
| `vad-trt/` | [VADv1](https://github.com/hustvl/VAD) | Vector-based Autonomous Driving | NVIDIA Drive Orin |
| `petr-trt/` | [PETRv1&v2](https://github.com/megvii-research/PETR) | 3D Object Detection | NVIDIA Drive Orin |

Sources: [AV-Solutions/README.md:13-35]()

### Optimization Techniques and Tools

| Component | Purpose | Key Features |
|-----------|---------|--------------|
| `SparsityINT8/` | Combines structured sparsity with INT8 quantization | PyTorch training workflow, TensorRT inference |
| `mtmi/` | Multi-task model inference across GPU and DLA | Simultaneous GPU/DLA deployment |
| `onnx-export-guidance/` | ONNX export best practices | TorchScript-based export guidance |

Sources: [AV-Solutions/README.md:4-11]()

## Hardware Architecture and Optimization

### NVIDIA Drive Orin Deployment Strategy

```mermaid
graph TB
    subgraph ORIN ["NVIDIA Drive Orin Platform"]
        GPU["GPU Cores<br/>(CUDA, FP16/FP32)"]
        DLA["DLA Cores<br/>(INT8 Inference)"]
    end
    
    subgraph MODELS ["Deployed Models"]
        M1["3D Detection Models"]
        M2["BEV Perception Models"] 
        M3["End-to-End Driving Models"]
        M4["Language Models"]
    end
    
    subgraph OPTIMIZATION ["Optimization Pipeline"]
        O1["INT8 Quantization"]
        O2["Structured Sparsity"]
        O3["TensorRT Engine Build"]
        O4["Multi-device Pipeline"]
    end
    
    M1 --> O1
    M2 --> O1
    M3 --> O4
    M4 --> O1
    
    O1 --> DLA
    O2 --> GPU
    O3 --> GPU
    O3 --> DLA
    O4 --> GPU
    O4 --> DLA
```

Sources: [AV-Solutions/README.md:10-11](), [AV-Solutions/README.md:22-35]()

## Technology Stack Integration

The deployment solutions leverage a consistent technology stack across all model implementations:

- **Framework Pipeline**: PyTorch → ONNX → TensorRT → NVIDIA Drive Orin
- **Optimization Methods**: INT8 quantization, structured sparsity, explicit quantization
- **Hardware Utilization**: GPU and DLA acceleration with multi-device inference
- **Development Support**: Docker environments, custom TensorRT plugins, calibration tools

The system provides both model-specific optimization examples and general-purpose tools for deploying autonomous vehicle deep learning models in production environments.

Sources: [AV-Solutions/README.md:1-37](), [README.md:5-19]()

---

