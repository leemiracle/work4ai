<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-V3.2-Exp · page 3 Deployment Guide · fetched 2026-10-30 -->

# Deployment Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This document provides comprehensive instructions for deploying DeepSeek-V3.2-Exp across different environments and hardware configurations. The guide covers local development setups for experimentation and research, as well as production deployment options for serving the model at scale.

The deployment guide focuses on the practical aspects of running the 671B parameter MoE model with its DeepSeek Sparse Attention mechanism. For technical details about the model architecture, see [System Architecture](#1.1). For understanding the inference pipeline components, see [Inference Pipeline](#2).

## Deployment Architecture Overview

DeepSeek-V3.2-Exp supports multiple deployment pathways, each optimized for different use cases and hardware configurations. The deployment ecosystem is built around three primary approaches: local HuggingFace inference for development, SGLang for production serving, and vLLM for high-performance inference.

### Deployment Options Matrix

| Deployment Method | Use Case | Hardware Support | Key Features |
|-------------------|----------|------------------|--------------|
| HuggingFace Local | Development, Research | Multi-GPU | Weight conversion, Interactive chat |
| SGLang | Production, Serving | H200, MI350, NPU A2/A3 | Docker containers, Multi-hardware |
| vLLM | High-performance Inference | Standard GPUs | Day-0 support, Production ready |

### Overall Deployment Architecture

```mermaid
graph TB
    subgraph "Model Source"
        HF_Repo["deepseek-ai/DeepSeek-V3.2-Exp"]
    end
    
    subgraph "Local Development Path"
        convert_py["convert.py"]
        generate_py["generate.py"]
        config_json["config_671B_v3.2.json"]
        torchrun["torchrun --nproc-per-node"]
        
        convert_py --> generate_py
        config_json --> generate_py
        generate_py --> torchrun
    end
    
    subgraph "Production SGLang Path"
        docker_h200["lmsysorg/sglang:dsv32"]
        docker_rocm["lmsysorg/sglang:dsv32-rocm"]
        docker_a2["lmsysorg/sglang:dsv32-a2"]
        docker_a3["lmsysorg/sglang:dsv32-a3"]
        sglang_server["sglang.launch_server"]
        
        docker_h200 --> sglang_server
        docker_rocm --> sglang_server
        docker_a2 --> sglang_server
        docker_a3 --> sglang_server
    end
    
    subgraph "vLLM Production Path"
        vllm_recipes["vLLM Recipes"]
        vllm_engine["vLLM Engine"]
        
        vllm_recipes --> vllm_engine
    end
    
    subgraph "Hardware Targets"
        nvidia_h200["NVIDIA H200"]
        amd_mi350["AMD MI350"]
        npu_a2["NPU A2"]
        npu_a3["NPU A3"]
    end
    
    HF_Repo --> convert_py
    HF_Repo --> sglang_server
    HF_Repo --> vllm_engine
    
    docker_h200 --> nvidia_h200
    docker_rocm --> amd_mi350
    docker_a2 --> npu_a2
    docker_a3 --> npu_a3
```

Sources: [README.md:88-127]()

## Local Development

Local development deployment enables researchers and developers to run DeepSeek-V3.2-Exp on their own hardware for experimentation and testing. This approach uses the HuggingFace model format with custom conversion and generation scripts.

### Weight Conversion Process

The local deployment begins with converting HuggingFace model weights to the format required by the inference system. The `convert.py` script handles the transformation and sharding across multiple GPUs.

```mermaid
graph LR
    subgraph "Input"
        hf_ckpt_path["${HF_CKPT_PATH}"]
    end
    
    subgraph "Conversion Process"
        convert_py["convert.py"]
        experts_256["EXPERTS=256"]
        model_parallel["MODEL_PARALLEL=${MP}"]
    end
    
    subgraph "Output"
        save_path["${SAVE_PATH}"]
        converted_weights["Converted Weights"]
    end
    
    subgraph "Configuration"
        config_671B["config_671B_v3.2.json"]
    end
    
    hf_ckpt_path --> convert_py
    experts_256 --> convert_py
    model_parallel --> convert_py
    convert_py --> save_path
    save_path --> converted_weights
    config_671B --> converted_weights
```

The conversion command structure:

```bash
export EXPERTS=256
python convert.py --hf-ckpt-path ${HF_CKPT_PATH} --save-path ${SAVE_PATH} --n-experts ${EXPERTS} --model-parallel ${MP}
```

Key parameters:
- `EXPERTS=256`: Configures the number of MoE experts
- `MP`: Model parallel degree matching available GPU count
- Output format optimized for distributed inference

Sources: [README.md:90-95]()

### Interactive Generation Setup

After weight conversion, the system launches an interactive chat interface using `torchrun` for multi-GPU execution:

```mermaid
graph TB
    subgraph "Launch Configuration"
        save_path_env["${SAVE_PATH}"]
        config_env["CONFIG=config_671B_v3.2.json"]
        mp_env["${MP}"]
    end
    
    subgraph "Execution Environment"
        torchrun_cmd["torchrun --nproc-per-node ${MP}"]
        generate_py["generate.py"]
        interactive_flag["--interactive"]
    end
    
    subgraph "Runtime Components"
        ckpt_path["--ckpt-path ${SAVE_PATH}"]
        config_param["--config ${CONFIG}"]
        distributed_execution["torch.distributed"]
    end
    
    save_path_env --> ckpt_path
    config_env --> config_param
    mp_env --> torchrun_cmd
    
    torchrun_cmd --> generate_py
    ckpt_path --> generate_py
    config_param --> generate_py
    interactive_flag --> generate_py
    
    generate_py --> distributed_execution
```

Launch command:
```bash
export CONFIG=config_671B_v3.2.json
torchrun --nproc-per-node ${MP} generate.py --ckpt-path ${SAVE_PATH} --config ${CONFIG} --interactive
```

Sources: [README.md:97-101]()

## Production Deployment

Production deployment options are designed for serving the model at scale with high availability and performance. The system supports both SGLang and vLLM frameworks with specialized configurations for different hardware platforms.

### SGLang Deployment

SGLang provides Docker-based deployment with specialized images for different hardware architectures. Each Docker image is optimized for specific hardware capabilities and includes all necessary dependencies.

#### Docker Image Architecture

```mermaid
graph TB
    subgraph "SGLang Docker Images"
        base_image["lmsysorg/sglang:dsv32"]
        rocm_image["lmsysorg/sglang:dsv32-rocm"]
        a2_image["lmsysorg/sglang:dsv32-a2"]
        a3_image["lmsysorg/sglang:dsv32-a3"]
    end
    
    subgraph "Hardware Targets"
        h200_gpu["NVIDIA H200"]
        mi350_gpu["AMD MI350"]
        npu_a2_chip["NPU A2"]
        npu_a3_chip["NPU A3"]
    end
    
    subgraph "SGLang Server Configuration"
        launch_server["python -m sglang.launch_server"]
        model_param["--model deepseek-ai/DeepSeek-V3.2-Exp"]
        tp_param["--tp 8"]
        dp_param["--dp 8"]
        page_size["--page-size 64"]
    end
    
    base_image --> h200_gpu
    rocm_image --> mi350_gpu
    a2_image --> npu_a2_chip
    a3_image --> npu_a3_chip
    
    h200_gpu --> launch_server
    mi350_gpu --> launch_server
    npu_a2_chip --> launch_server
    npu_a3_chip --> launch_server
    
    launch_server --> model_param
    launch_server --> tp_param
    launch_server --> dp_param
    launch_server --> page_size
```

#### Hardware-Specific Deployment

| Hardware | Docker Image | Optimization Features |
|----------|--------------|----------------------|
| NVIDIA H200 | `lmsysorg/sglang:dsv32` | CUDA optimizations, high memory bandwidth |
| AMD MI350 | `lmsysorg/sglang:dsv32-rocm` | ROCm support, AMD GPU acceleration |
| NPU A2 | `lmsysorg/sglang:dsv32-a2` | Specialized AI chip optimization |
| NPU A3 | `lmsysorg/sglang:dsv32-a3` | Advanced NPU architecture support |

Docker pull commands:
```bash
# H200
docker pull lmsysorg/sglang:dsv32

# MI350
docker pull lmsysorg/sglang:dsv32-rocm

# NPUs
docker pull lmsysorg/sglang:dsv32-a2
docker pull lmsysorg/sglang:dsv32-a3
```

#### SGLang Server Configuration

The SGLang server launch command provides fine-grained control over parallelization and memory management:

```bash
python -m sglang.launch_server --model deepseek-ai/DeepSeek-V3.2-Exp --tp 8 --dp 8 --page-size 64
```

Configuration parameters:
- `--tp 8`: Tensor parallelism degree for model sharding
- `--dp 8`: Data parallelism for batch processing
- `--page-size 64`: Memory page size for attention computation
- `--model`: Direct HuggingFace model identifier

Sources: [README.md:104-122]()

### vLLM Integration

vLLM provides day-0 support for DeepSeek-V3.2-Exp with optimized inference capabilities. The integration offers high-performance serving with minimal configuration requirements.

```mermaid
graph LR
    subgraph "vLLM Deployment"
        vllm_recipes["vLLM Recipes Documentation"]
        vllm_engine["vLLM Inference Engine"]
        model_integration["DeepSeek-V3.2-Exp Integration"]
    end
    
    subgraph "Features"
        day0_support["Day-0 Support"]
        high_performance["High Performance Inference"]
        production_ready["Production Ready"]
    end
    
    subgraph "Documentation"
        recipe_docs["docs.vllm.ai/projects/recipes"]
        deepseek_guide["DeepSeek-V3_2-Exp.html"]
    end
    
    vllm_recipes --> vllm_engine
    vllm_engine --> model_integration
    
    model_integration --> day0_support
    model_integration --> high_performance
    model_integration --> production_ready
    
    vllm_recipes --> recipe_docs
    recipe_docs --> deepseek_guide
```

The vLLM integration provides immediate compatibility without requiring specialized Docker images or complex configuration. Detailed deployment instructions are available in the official vLLM recipes documentation.

Sources: [README.md:124-126]()

### Deployment Comparison

| Aspect | SGLang | vLLM | Local HF |
|--------|--------|------|----------|
| Setup Complexity | Medium | Low | High |
| Hardware Support | Specialized | Standard | Multi-GPU |
| Production Readiness | High | High | Development |
| Docker Support | Yes | Standard | No |
| Custom Optimization | Hardware-specific | General | Research-focused |

The choice of deployment method depends on specific requirements: SGLang for specialized hardware optimization, vLLM for standard production deployment, and local HuggingFace inference for development and research workflows.

Sources: [README.md:88-127]()

---

