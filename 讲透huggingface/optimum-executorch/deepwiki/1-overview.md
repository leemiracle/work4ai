<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-executorch · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

Optimum ExecuTorch is a bridge library that enables conversion and deployment of HuggingFace models using Meta's ExecuTorch runtime framework. This document provides a comprehensive overview of the system's architecture, core components, and capabilities for optimizing transformer models for mobile and edge device deployment.

This overview covers the high-level system design and main workflows. For detailed installation instructions, see [Installation and Setup](#1.1). For step-by-step usage examples, see [Quick Start Guide](#1.2). For comprehensive model export details, see [Model Export System](#2). For inference and runtime information, see [Runtime and Inference](#3).

## System Architecture

The optimum-executorch system operates as a bridge between the HuggingFace ecosystem and ExecuTorch runtime, providing model conversion, optimization, and inference capabilities.

### High-Level Architecture

```mermaid
graph TB
    subgraph "HuggingFace_Ecosystem" ["HuggingFace Ecosystem"]
        HF_Models["HuggingFace Models<br/>• meta-llama/Llama-3.2-1B<br/>• HuggingFaceTB/SmolLM2-135M<br/>• google/gemma-2-2b"]
        AutoTokenizer["AutoTokenizer<br/>AutoProcessor"]
        HF_Hub["HuggingFace Hub<br/>Model Repository"]
    end
    
    subgraph "Optimum_ExecuTorch" ["Optimum ExecuTorch Bridge"]
        CLI["optimum-cli export executorch<br/>Command Interface"]
        Python_API["Python API<br/>ExecuTorchModelForCausalLM<br/>ExecuTorchModelForSeq2SeqLM<br/>ExecuTorchModelForImageClassification"]
        Export_System["Export System<br/>Task Registry<br/>ExportableModule Wrappers<br/>Recipe System"]
        Optimization["Optimization Layer<br/>custom_sdpa<br/>custom_kv_cache<br/>Quantization"]
    end
    
    subgraph "ExecuTorch_Runtime" ["ExecuTorch Runtime"]
        ET_Backend["ExecuTorch Backends<br/>XnnpackPartitioner<br/>CoreMLPartitioner<br/>PortableBackend"]
        PTE_Files[".pte Model Files<br/>Portable Executables"]
        ET_Module["ExecuTorchModule<br/>Runtime Instance"]
    end
    
    subgraph "Deployment_Targets" ["Deployment Targets"]
        Mobile["Mobile Devices<br/>iOS/Android<br/>Samsung Galaxy S22<br/>iPhone 15 Pro"]
        Edge["Edge Devices<br/>Various Hardware"]
    end
    
    HF_Models --> CLI
    HF_Models --> Python_API
    HF_Hub --> CLI
    HF_Hub --> Python_API
    AutoTokenizer --> Python_API
    
    CLI --> Export_System
    Python_API --> Export_System
    Export_System --> Optimization
    Optimization --> ET_Backend
    
    ET_Backend --> PTE_Files
    PTE_Files --> ET_Module
    Python_API --> ET_Module
    
    ET_Module --> Mobile
    ET_Module --> Edge
```

Sources: [README.md:1-233]()

### Core Components

The system consists of three primary layers:

| Component | Purpose | Key Classes/Functions |
|-----------|---------|----------------------|
| **Export Layer** | Convert HuggingFace models to ExecuTorch format | `CausalLMExportableModule`, `Seq2SeqLMExportableModule`, `VisionEncoderExportableModule` |
| **Optimization Layer** | Apply performance optimizations | `custom_sdpa`, `custom_kv_cache`, quantization schemes |
| **Runtime Layer** | Execute optimized models | `ExecuTorchModelForCausalLM`, `ExecuTorchModelForSeq2SeqLM`, `ExecuTorchModule` |

Sources: [README.md:15-19](), [README.md:54-116]()

## Key Capabilities

### Model Support

Optimum ExecuTorch supports a comprehensive range of transformer architectures:

- **Text Models**: Causal LM (Llama, Gemma, Qwen), Seq2Seq (T5), Masked LM (BERT, RoBERTa)
- **Vision Models**: Image classification (ViT, EfficientNet, Swin)
- **Audio Models**: Speech recognition (Whisper)

The system handles over 20 model families with variants, including popular models like `HuggingFaceTB/SmolLM2-135M`, `meta-llama/Llama-3.2-1B`, and `google/gemma-2-2b`.

Sources: [README.md:141-193]()

### Performance Optimizations

The library implements several key optimizations:

- **Custom SDPA**: 3x performance improvement over default attention
- **Custom KV Cache**: 2.5x improvement with in-place cache updates
- **Quantization**: int8 dynamic activations with int4 grouped weights (`8da4w`)
- **Batch Prefill**: 20x faster time-to-first-token processing

Sources: [README.md:121-139]()

## Export and Inference Workflow

### Model Export Pipeline

```mermaid
graph LR
    subgraph "Input_Processing" ["Input Processing"]
        HF_Model["HuggingFace Model<br/>model_id or local path"]
        Task_Loading["Task-Specific Loading<br/>load_causal_lm_model<br/>load_seq2seq_speech_model<br/>load_vision_model"]
    end
    
    subgraph "ExportableModule_Layer" ["ExportableModule Layer"]
        CLM_Wrapper["CausalLMExportableModule<br/>text-generation wrapper"]
        S2S_Wrapper["Seq2SeqLMExportableModule<br/>seq2seq wrapper"]
        Vision_Wrapper["VisionEncoderExportableModule<br/>vision wrapper"]
    end
    
    subgraph "Recipe_System" ["Recipe System"]
        Recipes["Export Recipes<br/>xnnpack<br/>portable<br/>coreml_fp32_cpu"]
        Backend_Delegation["Backend Delegation<br/>XnnpackPartitioner<br/>CoreMLPartitioner"]
        ET_Lowering["ExecuTorch Lowering<br/>to_edge_transform_and_lower"]
    end
    
    subgraph "Output_Generation" ["Output Generation"]
        PTE_File[".pte Model File<br/>Portable Executable"]
        Metadata["Model Metadata<br/>Configuration"]
    end
    
    HF_Model --> Task_Loading
    Task_Loading --> CLM_Wrapper
    Task_Loading --> S2S_Wrapper
    Task_Loading --> Vision_Wrapper
    
    CLM_Wrapper --> Recipes
    S2S_Wrapper --> Recipes
    Vision_Wrapper --> Recipes
    
    Recipes --> Backend_Delegation
    Backend_Delegation --> ET_Lowering
    ET_Lowering --> PTE_File
    ET_Lowering --> Metadata
```

Sources: [README.md:84-96](), [README.md:128-131]()

### Runtime Inference System

```mermaid
graph TB
    subgraph "Model_Loading" ["Model Loading"]
        from_pretrained["ExecuTorchModelForXXX.from_pretrained()"]
        Model_Sources["Model Sources<br/>• HuggingFace Hub ID<br/>• Local .pte file<br/>• Local directory"]
    end
    
    subgraph "Runtime_Classes" ["Runtime Classes"]
        CLM_Runtime["ExecuTorchModelForCausalLM<br/>• text_generation()<br/>• generate()"]
        S2S_Runtime["ExecuTorchModelForSeq2SeqLM<br/>• text_generation()"]
        Speech_Runtime["ExecuTorchModelForSpeechSeq2Seq<br/>• transcribe()"]
        Vision_Runtime["ExecuTorchModelForImageClassification<br/>• forward()"]
    end
    
    subgraph "ExecuTorch_Core" ["ExecuTorch Core"]
        ET_Module["ExecuTorchModule<br/>Low-level runtime"]
        Methods["Runtime Methods<br/>• forward<br/>• get_metadata<br/>• method_names"]
    end
    
    subgraph "Inference_Features" ["Inference Features"]
        Generation["Text Generation<br/>• Autoregressive decoding<br/>• Batch prefill<br/>• Custom stopping"]
        Cache_Management["KV Cache<br/>• Static Cache<br/>• Custom KV Cache<br/>• Ring KV Cache"]
    end
    
    Model_Sources --> from_pretrained
    from_pretrained --> CLM_Runtime
    from_pretrained --> S2S_Runtime
    from_pretrained --> Speech_Runtime
    from_pretrained --> Vision_Runtime
    
    CLM_Runtime --> ET_Module
    S2S_Runtime --> ET_Module
    Speech_Runtime --> ET_Module
    Vision_Runtime --> ET_Module
    
    ET_Module --> Methods
    CLM_Runtime --> Generation
    CLM_Runtime --> Cache_Management
```

Sources: [README.md:55-77](), [README.md:100-116]()

## Usage Patterns

The system supports two primary usage patterns:

1. **One-Step API**: Direct model loading with on-the-fly export using `ExecuTorchModelForCausalLM.from_pretrained()`
2. **Two-Step Process**: Separate export via CLI (`optimum-cli export executorch`) followed by runtime loading

Both approaches support the same optimization features including custom attention, quantization, and backend delegation.

Sources: [README.md:52-116]()

## Performance Characteristics

Optimum ExecuTorch achieves significant performance improvements on mobile devices:

| Device | SmolLM2-135M Performance |
|--------|-------------------------|
| Samsung Galaxy S22 5G | 202.28 tok/s |
| iPhone 15 Pro | 29.64 tok/s |
| iPhone 15 | 7.47 tok/s |

These benchmarks utilize custom SDPA, KV-cache optimization, and 8da4w quantization for optimal mobile performance.

Sources: [README.md:195-210]()

---

