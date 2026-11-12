<!-- source: DeepWiki mcp.deepwiki.com · repo openai/gpt-oss · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [awesome-gpt-oss.md](awesome-gpt-oss.md)
- [examples/reinforcement-fine-tuning.ipynb](examples/reinforcement-fine-tuning.ipynb)

</details>



This document provides a technical overview of the gpt-oss repository, which implements OpenAI's open-weight language models and supporting infrastructure. The repository contains two sparse mixture-of-experts (MoE) models (`gpt-oss-120b` and `gpt-oss-20b`), multiple inference backends, integrated tools, client applications, and evaluation frameworks.

For detailed model specifications, see [Models](#2). For deployment instructions, see [Getting Started](#3). For tool integration details, see [Tools and Capabilities](#5).

## System Architecture

The following diagram maps the high-level system components to their corresponding code entities:

**System Component Map**
```mermaid
graph TB
    subgraph "Model_Variants" ["Model Variants"]
        GPT120B["gpt-oss-120b<br/>117B params, 5.1B active<br/>MXFP4 quantized"]
        GPT20B["gpt-oss-20b<br/>21B params, 3.6B active<br/>MXFP4 quantized"]
    end
    
    subgraph "Core_Framework" ["Core Framework"]
        HarmonyLib["openai-harmony package<br/>Message encoding<br/>HarmonyEncodingName.HARMONY_GPT_OSS"]
        HarmonyFormat["Harmony Response Format<br/>render_conversation_for_completion()<br/>parse_messages_from_completion_tokens()"]
    end
    
    subgraph "Inference_Backends" ["Inference Backends"]
        TorchImpl["gpt_oss.torch.model<br/>PyTorchModel class<br/>Tensor parallelism"]
        TritonImpl["gpt_oss.triton<br/>triton_kernels MoE<br/>MXFP4 support"]
        MetalImpl["gpt_oss.metal<br/>gptoss_context_process<br/>Apple Silicon Metal C API"]
        vLLMBackend["vLLM integration<br/>vllm serve command<br/>High throughput"]
    end
    
    subgraph "Tools_Layer" ["Tools Layer"]
        BrowserTool["SimpleBrowserTool<br/>gpt_oss/tools/simple_browser/<br/>ExaBackend / YouComBackend"]
        PythonTool["PythonTool<br/>gpt_oss/tools/python_docker/<br/>docker_tool.py"]
        ApplyPatch["apply_patch tool<br/>File manipulation<br/>Create/update/delete"]
    end
    
    subgraph "Client_Apps" ["Client Applications"]
        ChatCLI["gpt_oss.chat<br/>Terminal interface<br/>--backend selection"]
        ResponsesAPI["gpt_oss.responses_api.serve<br/>/v1/responses endpoint<br/>Streaming SSE events"]
        WebUIs["streamlit_chat.py<br/>gradio_chat.py<br/>Web interfaces"]
    end
    
    GPT120B --> HarmonyLib
    GPT20B --> HarmonyLib
    HarmonyLib --> HarmonyFormat
    
    HarmonyFormat --> TorchImpl
    HarmonyFormat --> TritonImpl
    HarmonyFormat --> MetalImpl
    HarmonyFormat --> vLLMBackend
    
    BrowserTool --> HarmonyLib
    PythonTool --> HarmonyLib
    ApplyPatch --> HarmonyLib
    
    TorchImpl --> ChatCLI
    TritonImpl --> ChatCLI
    vLLMBackend --> ResponsesAPI
    ResponsesAPI --> WebUIs
```

Sources: [README.md:14-46](), [README.md:104-168](), [README.md:300-335](), [awesome-gpt-oss.md:83-86]()

## Core Components

The gpt-oss system consists of several interconnected components that work together to provide a complete language model inference and interaction platform:

| Component | Purpose | Key Code Entities |
|-----------|---------|-------------------|
| **Model Variants** | Two sparse MoE models with different parameter counts | `openai/gpt-oss-120b`, `openai/gpt-oss-20b` |
| **Harmony Framework** | Essential message encoding and tool integration | `openai_harmony`, `load_harmony_encoding` |
| **Inference Backends** | Multiple computational backends for model execution | `gpt_oss.torch`, `gpt_oss.triton`, `gpt_oss.metal` |
| **Tools Ecosystem** | Integrated capabilities for web browsing and code execution | `SimpleBrowserTool`, `PythonTool`, `gpt-oss-mcp-server` |
| **Client Applications** | Various interfaces for model interaction | `gpt_oss.chat`, `api_server.py`, `streamlit_chat.py` |
| **Evaluation System** | Benchmarking and testing framework | `gpt_oss.evals`, `HealthBenchEval`, `GPQAEval` |

Sources: [README.md:16-19](), [README.md:104-118](), [awesome-gpt-oss.md:7-13]()

## Model Variants

The repository provides two model variants optimized for different use cases:

### gpt-oss-120b
- **Parameters**: 117B total, 5.1B active per forward pass [README.md:18-18]()
- **Memory**: Fits on a single 80GB GPU (NVIDIA H100 or AMD MI300X) [README.md:18-18]()
- **Quantization**: MXFP4 quantization of the MoE weights [README.md:45-45]()
- **Use Case**: Production, general purpose, high reasoning use cases [README.md:18-18]()

### gpt-oss-20b  
- **Parameters**: 21B total, 3.6B active per forward pass [README.md:19-19]()
- **Memory**: Runs within 16GB of memory [README.md:45-45]()
- **Quantization**: MXFP4 quantization of the MoE weights [README.md:45-45]()
- **Use Case**: Lower latency, local or specialized use cases [README.md:19-19]()

Both models were trained using the Harmony response format and require it for correct operation [README.md:21-21](). They support configurable reasoning effort (low, medium, high) and provide full access to the chain-of-thought process [README.md:41-42]().

## Deployment Ecosystem

The following diagram illustrates the deployment options and their corresponding code integration points:

**Deployment and Client Flow**
```mermaid
graph LR
    subgraph "Local_Deployment" ["Local Deployment"]
        OllamaLocal["ollama run gpt-oss:20b<br/>Consumer hardware"]
        LMStudio["LM Studio<br/>Desktop GUI interface"]
        DirectTriton["python -m gpt_oss.generate<br/>--backend triton<br/>Single GPU optimized"]
    end
    
    subgraph "Cloud_Services" ["Cloud Services"]
        vLLMCloud["vllm serve<br/>OpenAI-compatible API<br/>Production server"]
        GroqCloud["GroqCloud<br/>Fast inference acceleration"]
        WorkersAI["Cloudflare Workers AI<br/>Edge deployment"]
    end
    
    subgraph "Client_Interfaces" ["Client Interfaces"]
        TerminalChat["python -m gpt_oss.chat<br/>Harmony conversation loop"]
        ResponsesServer["api_server.py (FastAPI)<br/>/v1/responses endpoint"]
        AgentSDK["Agents SDK (TS/Python)<br/>MCP server support"]
    end
    
    OllamaLocal --> TerminalChat
    DirectTriton --> TerminalChat
    vLLMCloud --> ResponsesServer
    GroqCloud --> ResponsesServer
    ResponsesServer --> AgentSDK
    ResponsesServer --> TerminalChat
```

Sources: [README.md:79-92](), [README.md:176-183](), [awesome-gpt-oss.md:17-76]()

## Build System Architecture

The repository uses a custom PEP 517 build backend that supports dynamic selection between standard Python packaging and native Metal compilation for Apple Silicon.

**Build Pipeline**
```mermaid
graph TD
    subgraph "Build_Backend" ["Custom Build Backend"]
        BuildBackend["gpt_oss_build_backend/backend.py<br/>PEP 517 implementation"]
    end
    
    subgraph "Standard_Mode" ["Standard Mode"]
        SetuptoolsBackend["setuptools.build_meta<br/>Pure Python wheel"]
    end
    
    subgraph "Metal_Mode" ["Metal Extension Mode"]
        ScikitBuild["scikit_build_core.build<br/>GPTOSS_BUILD_METAL=1"]
        MetalC["gpt-oss.h / functions.h<br/>Native Metal kernels"]
    end
    
    BuildBackend --> SetuptoolsBackend
    BuildBackend --> ScikitBuild
    ScikitBuild --> MetalC
```

The build system automatically delegates to `scikit-build-core` when building with Metal support, which handles the compilation of `.metallib` files and the C++ Python bindings [README.md:31-31]().

Sources: [README.md:31-31](), [awesome-gpt-oss.md:39-40]()

## Key Technologies

- **MXFP4 Quantization**: Native quantization format for MoE weights, enabling large models to run on significantly reduced hardware footprints (e.g., 120b on a single 80GB GPU) [README.md:45-45]().
- **Harmony Response Format**: A specialized chat format library (`openai-harmony`) required for model operation. It manages `Conversation`, `Message`, and `Role` objects, and handles the rendering of tool descriptions and stop tokens [README.md:104-168]().
- **Sparse MoE Architecture**: Efficient mixture-of-experts design where only a small subset of parameters (5.1B for the 120b model) are active during any single inference step [README.md:18-19]().
- **Multi-Backend Support**: Pluggable inference backends ranging from educational PyTorch implementations to high-performance Triton kernels and native Metal implementations for Apple Silicon [README.md:29-31]().
- **Agentic Capabilities**: Native support for tool calling, including web browsing via `SimpleBrowserTool` and secure code execution via `PythonTool` [README.md:44-44](), [awesome-gpt-oss.md:83-86]().
- **Reinforcement Fine-Tuning**: Support for training models using GRPO (Group Relative Policy Optimization) for strategy-based tasks like the 2048 game [examples/reinforcement-fine-tuning.ipynb:19-35]().

Sources: [README.md:18-46](), [README.md:104-168](), [examples/reinforcement-fine-tuning.ipynb:19-35]()

---

