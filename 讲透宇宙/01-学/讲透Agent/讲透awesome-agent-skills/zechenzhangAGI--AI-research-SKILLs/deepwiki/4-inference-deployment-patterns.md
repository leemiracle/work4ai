<!-- source: DeepWiki mcp.deepwiki.com · repo zechenzhangAGI/AI-research-SKILLs · page 4 Inference & Deployment Patterns · fetched 2026-10-26 -->

# Inference & Deployment Patterns

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [10-optimization/gptq/SKILL.md](10-optimization/gptq/SKILL.md)
- [11-evaluation/lm-evaluation-harness/SKILL.md](11-evaluation/lm-evaluation-harness/SKILL.md)
- [12-inference-serving/llama-cpp/SKILL.md](12-inference-serving/llama-cpp/SKILL.md)
- [12-inference-serving/sglang/SKILL.md](12-inference-serving/sglang/SKILL.md)
- [12-inference-serving/tensorrt-llm/SKILL.md](12-inference-serving/tensorrt-llm/SKILL.md)

</details>



This document covers best practices for deploying LLMs in production across different hardware configurations and performance requirements. It provides decision frameworks for selecting inference engines, quantization strategies, and deployment architectures based on your constraints (latency, throughput, hardware, cost).

**Scope**: This page focuses on inference-time deployment patterns. For training and optimization, see [Training & Fine-Tuning Skills](#2.3) and [Optimization Skills](#2.6). For specific inference engine implementations, see [Inference & Serving Skills](#2.8). For production monitoring, see [Production Observability with Phoenix](#4.3).

## Model Format Transformation Pipeline

LLM deployment begins with model format conversion. The format you choose determines which inference engines you can use and what hardware you can target.

```mermaid
flowchart LR
    subgraph "Training Outputs"
        FP16["FP16/BF16<br/>Base Model<br/>14GB (7B)<br/>140GB (70B)"]
    end
    
    subgraph "Post-Training Quantization"
        GPTQ["GPTQ 4-bit<br/>AutoGPTQForCausalLM<br/>3.5GB (7B)<br/>35GB (70B)"]
        BNB["Bitsandbytes<br/>8-bit/4-bit<br/>7GB/3.5GB (7B)"]
    end
    
    subgraph "Deployment Formats"
        GGUF["GGUF<br/>Q4_K_M/Q6_K<br/>4GB/5.5GB (7B)<br/>llama.cpp"]
        TRT["TensorRT-LLM<br/>FP8/INT4<br/>7GB/3.5GB (7B)<br/>NVIDIA only"]
    end
    
    subgraph "Inference Engines"
        TRTLLM["TensorRT-LLM<br/>LLM class<br/>Max throughput<br/>NVIDIA"]
        VLLM["vLLM<br/>PagedAttention<br/>High throughput<br/>Multi-GPU"]
        SGLANG["SGLang<br/>RadixAttention<br/>Prefix caching<br/>Agents"]
        LLAMACPP["llama.cpp<br/>llama-cli/llama-server<br/>CPU/Metal/ROCm<br/>Edge"]
    end
    
    FP16 --> GPTQ
    FP16 --> BNB
    FP16 --> TRT
    GPTQ --> GGUF
    
    FP16 --> TRTLLM
    FP16 --> VLLM
    FP16 --> SGLANG
    GPTQ --> VLLM
    GPTQ --> SGLANG
    TRT --> TRTLLM
    GGUF --> LLAMACPP
    
    style FP16 fill:#f9f9f9
    style GGUF fill:#f9f9f9
    style LLAMACPP fill:#f9f9f9
```

**Key Format Decision Points**:

| Starting Point | Target Hardware | Recommended Path | Inference Engine |
|---------------|-----------------|------------------|------------------|
| FP16 Base Model | NVIDIA A100/H100 | FP16 → TensorRT-LLM FP8 | TensorRT-LLM |
| FP16 Base Model | Multi-GPU NVIDIA | FP16 → vLLM | vLLM |
| FP16 Base Model | Agents/Prefix Reuse | FP16 → SGLang | SGLang |
| FP16 Base Model | CPU/Apple Silicon | FP16 → GPTQ → GGUF | llama.cpp |
| FP16 Base Model | Consumer GPU (RTX) | FP16 → GPTQ | vLLM or llama.cpp |

**Sources**: [12-inference-serving/tensorrt-llm/SKILL.md:1-187](), [12-inference-serving/sglang/SKILL.md:1-443](), [12-inference-serving/llama-cpp/SKILL.md:1-259](), [10-optimization/gptq/SKILL.md:1-451]()

## Inference Engine Architecture Comparison

Each inference engine optimizes for different bottlenecks. Understanding their architectural differences is critical for deployment decisions.

```mermaid
graph TB
    subgraph "TensorRT-LLM Architecture"
        TRT_INPUT["Input Batching<br/>In-flight batching"]
        TRT_KV["KV Cache<br/>Paged management"]
        TRT_KERNEL["Optimized Kernels<br/>Flash Attention<br/>FP8/INT4 kernels"]
        TRT_PARA["Parallelism<br/>TP/PP/Expert"]
        TRT_OUTPUT["Output: 24K tok/s<br/>Llama 3-8B H100"]
        
        TRT_INPUT --> TRT_KV
        TRT_KV --> TRT_KERNEL
        TRT_KERNEL --> TRT_PARA
        TRT_PARA --> TRT_OUTPUT
    end
    
    subgraph "vLLM Architecture"
        VLLM_INPUT["Input Batching<br/>Continuous batching"]
        VLLM_KV["PagedAttention<br/>Non-contiguous blocks"]
        VLLM_KERNEL["Standard Kernels<br/>PyTorch/Triton"]
        VLLM_PARA["Parallelism<br/>TP only"]
        VLLM_OUTPUT["Output: 2.8K tok/s<br/>Llama 3-8B A100"]
        
        VLLM_INPUT --> VLLM_KV
        VLLM_KV --> VLLM_KERNEL
        VLLM_KERNEL --> VLLM_PARA
        VLLM_PARA --> VLLM_OUTPUT
    end
    
    subgraph "SGLang Architecture"
        SGL_INPUT["Input with Prefixes<br/>Radix tree matching"]
        SGL_RADIX["RadixAttention<br/>Prefix reuse 5-10x"]
        SGL_STRUCT["Structured Gen<br/>JSON/regex/grammar"]
        SGL_CACHE["Automatic Caching<br/>Zero config"]
        SGL_OUTPUT["Output: 5K tok/s<br/>With prefix reuse"]
        
        SGL_INPUT --> SGL_RADIX
        SGL_RADIX --> SGL_STRUCT
        SGL_STRUCT --> SGL_CACHE
        SGL_CACHE --> SGL_OUTPUT
    end
    
    subgraph "llama.cpp Architecture"
        LLAMA_INPUT["Input Processing<br/>Single/batch"]
        LLAMA_QUANT["GGUF Quantization<br/>Q4_K_M/Q6_K"]
        LLAMA_BACKEND["Backend Selection<br/>Metal/CUDA/ROCm/CPU"]
        LLAMA_THREAD["Threading<br/>Multi-core CPU"]
        LLAMA_OUTPUT["Output: 50 tok/s<br/>M3 Max CPU"]
        
        LLAMA_INPUT --> LLAMA_QUANT
        LLAMA_QUANT --> LLAMA_BACKEND
        LLAMA_BACKEND --> LLAMA_THREAD
        LLAMA_THREAD --> LLAMA_OUTPUT
    end
```

**Architectural Differentiators**:

**TensorRT-LLM** [`tensorrt_llm.LLM`]:
- **Optimization**: Compiled CUDA kernels, FP8 on H100
- **Batching**: In-flight batching (continuous)
- **Strength**: Absolute maximum throughput on NVIDIA
- **Limitation**: NVIDIA GPUs only, complex setup

**vLLM** [PagedAttention]:
- **Optimization**: PagedAttention (non-contiguous KV blocks)
- **Batching**: Continuous batching
- **Strength**: Simple Python API, stable production
- **Limitation**: Lower throughput than TensorRT-LLM

**SGLang** [`sgl.function`, `sgl.gen`, RadixAttention]:
- **Optimization**: RadixAttention (automatic prefix caching)
- **Batching**: Continuous with prefix reuse
- **Strength**: 5-10× faster for agents/few-shot
- **Limitation**: Newer system, less battle-tested

**llama.cpp** [`llama-cli`, `llama-server`]:
- **Optimization**: GGUF quantization, CPU/Metal kernels
- **Batching**: Simple batching
- **Strength**: Runs anywhere (CPU/Metal/ROCm)
- **Limitation**: Slower than GPU solutions

**Sources**: [12-inference-serving/tensorrt-llm/SKILL.md:92-110](), [12-inference-serving/sglang/SKILL.md:117-143](), [12-inference-serving/llama-cpp/SKILL.md:34-104]()

## Hardware-to-Engine Decision Matrix

The optimal inference engine depends on your available hardware. This matrix provides concrete recommendations.

```mermaid
flowchart TD
    START["Select Inference Engine"]
    
    HW_QUESTION{"Available Hardware?"}
    
    NVIDIA["NVIDIA GPU<br/>A100/H100/RTX"]
    CPU["CPU Only<br/>or Apple Silicon"]
    AMD["AMD GPU<br/>MI250/MI300"]
    
    NVIDIA_TYPE{"GPU Type?"}
    DATACENTER["Datacenter<br/>A100/H100"]
    CONSUMER["Consumer<br/>RTX 3090/4090"]
    
    WORKLOAD_DC{"Workload?"}
    WORKLOAD_CONSUMER{"Need?"}
    
    MAX_PERF["Maximum<br/>Throughput"]
    AGENTS["Agents/<br/>Prefix Reuse"]
    SIMPLE["Simple<br/>Generation"]
    
    CPU_TYPE{"Hardware?"}
    APPLE["Apple Silicon<br/>M1/M2/M3"]
    X86["x86 CPU<br/>Intel/AMD"]
    
    ENGINE_TRT["Use TensorRT-LLM<br/>trtllm-serve<br/>24K tok/s"]
    ENGINE_SGL["Use SGLang<br/>sgl.launch_server<br/>5-10x prefix speedup"]
    ENGINE_VLLM["Use vLLM<br/>Simple setup<br/>2.8K tok/s"]
    ENGINE_LLAMA_METAL["Use llama.cpp<br/>LLAMA_METAL=1<br/>50 tok/s"]
    ENGINE_LLAMA_CPU["Use llama.cpp<br/>CPU backend<br/>30-40 tok/s"]
    ENGINE_LLAMA_ROCM["Use llama.cpp<br/>LLAMA_HIP=1<br/>or vLLM"]
    ENGINE_QUANT["Quantize with GPTQ<br/>AutoGPTQForCausalLM<br/>4x memory reduction"]
    
    START --> HW_QUESTION
    
    HW_QUESTION -->|NVIDIA| NVIDIA
    HW_QUESTION -->|CPU/Mac| CPU
    HW_QUESTION -->|AMD| AMD
    
    NVIDIA --> NVIDIA_TYPE
    
    NVIDIA_TYPE -->|A100/H100| DATACENTER
    NVIDIA_TYPE -->|RTX| CONSUMER
    
    DATACENTER --> WORKLOAD_DC
    
    WORKLOAD_DC -->|Max perf| MAX_PERF
    WORKLOAD_DC -->|Agents| AGENTS
    WORKLOAD_DC -->|Simple| SIMPLE
    
    MAX_PERF --> ENGINE_TRT
    AGENTS --> ENGINE_SGL
    SIMPLE --> ENGINE_VLLM
    
    CONSUMER --> WORKLOAD_CONSUMER
    WORKLOAD_CONSUMER -->|Need to fit 70B| ENGINE_QUANT
    WORKLOAD_CONSUMER -->|13B or less| ENGINE_VLLM
    
    ENGINE_QUANT --> ENGINE_VLLM
    
    CPU --> CPU_TYPE
    
    CPU_TYPE -->|Mac| APPLE
    CPU_TYPE -->|x86| X86
    
    APPLE --> ENGINE_LLAMA_METAL
    X86 --> ENGINE_LLAMA_CPU
    AMD --> ENGINE_LLAMA_ROCM
```

**Decision Table**:

| Hardware | Model Size | Workload | Recommended Engine | Command |
|----------|-----------|----------|-------------------|---------|
| H100 GPU | Any | Max throughput | TensorRT-LLM | `trtllm-serve model --tp_size 4` |
| A100 GPU (8×) | 70B+ | General | vLLM | `python -m vllm.entrypoints.openai.api_server` |
| A100 GPU | 7-70B | Agents/Tools | SGLang | `python -m sglang.launch_server --enable-radix-cache` |
| RTX 4090 | 70B | Need to fit | GPTQ + vLLM | `AutoGPTQForCausalLM.from_quantized()` |
| RTX 3090/4090 | 7-13B | General | vLLM | `python -m vllm.entrypoints.openai.api_server` |
| M3 Max | 7-13B | Local/Edge | llama.cpp | `make LLAMA_METAL=1; ./llama-server -ngl 999` |
| Intel/AMD CPU | 7B | Edge/Server | llama.cpp | `./llama-server --threads 32` |
| AMD MI300 | Any | General | llama.cpp (ROCm) | `make LLAMA_HIP=1` |

**Sources**: [12-inference-serving/tensorrt-llm/SKILL.md:16-33](), [12-inference-serving/sglang/SKILL.md:16-33](), [12-inference-serving/llama-cpp/SKILL.md:16-33](), [10-optimization/gptq/SKILL.md:16-32]()

## Quantization Strategy by Deployment Target

Quantization reduces model size and increases speed, but introduces quality degradation. The optimal quantization depends on your deployment constraints.

### Quantization Format Mapping

```mermaid
graph LR
    subgraph "Model Formats"
        FP16_MODEL["FP16 Base Model<br/>14GB (7B model)<br/>Training output"]
    end
    
    subgraph "Datacenter Quantization"
        FP8_FORMAT["FP8<br/>TensorRT-LLM<br/>7GB<br/>H100 only"]
        INT4_TRT["INT4<br/>TensorRT-LLM<br/>3.5GB<br/>A100+"]
    end
    
    subgraph "Consumer GPU Quantization"
        GPTQ_FORMAT["GPTQ 4-bit<br/>AutoGPTQForCausalLM<br/>bits=4, group_size=128<br/>3.5GB"]
        BNB_FORMAT["Bitsandbytes<br/>load_in_4bit=True<br/>3.5GB"]
    end
    
    subgraph "CPU/Edge Quantization"
        GGUF_Q4["GGUF Q4_K_M<br/>llama.cpp<br/>4GB<br/>Balanced"]
        GGUF_Q2["GGUF Q2_K<br/>llama.cpp<br/>2.7GB<br/>Max compression"]
        GGUF_Q6["GGUF Q6_K<br/>llama.cpp<br/>5.5GB<br/>Max quality"]
    end
    
    FP16_MODEL --> FP8_FORMAT
    FP16_MODEL --> INT4_TRT
    FP16_MODEL --> GPTQ_FORMAT
    FP16_MODEL --> BNB_FORMAT
    GPTQ_FORMAT --> GGUF_Q4
    GPTQ_FORMAT --> GGUF_Q2
    GPTQ_FORMAT --> GGUF_Q6
```

### Quantization Decision Table

| Deployment Target | Model Size | Quantization | Format | Quality Loss | Speed Gain | Code Reference |
|------------------|-----------|--------------|---------|-------------|-----------|----------------|
| H100 datacenter | 7-70B | FP8 | TensorRT-LLM | <1% | 2× | `dtype="fp8"` in `LLM()` |
| A100 datacenter | 70B+ | INT4 | TensorRT-LLM | 1-2% | 4× | `dtype="int4"` |
| RTX 4090 | 70B | GPTQ 4-bit | group_size=128 | 1.5% | 3-4× | `BaseQuantizeConfig(bits=4, group_size=128)` |
| RTX 3090 | 13B | GPTQ 4-bit | group_size=128 | 1.5% | 3-4× | Same as above |
| M3 Max | 7-13B | GGUF Q4_K_M | llama.cpp | 2% | 4-10× vs FP16 | `Q4_K_M.gguf` |
| Raspberry Pi | 7B | GGUF Q2_K | llama.cpp | 5-8% | 10× | `Q2_K.gguf` |
| CPU server (quality) | 7B | GGUF Q6_K | llama.cpp | <1% | 2× | `Q6_K.gguf` |

**Quantization Code Patterns**:

**GPTQ Quantization** [10-optimization/gptq/SKILL.md:76-116]():
```python
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

# Quantize for consumer GPU deployment
config = BaseQuantizeConfig(
    bits=4,              # 4-bit quantization
    group_size=128,      # Recommended default
    desc_act=False,      # Faster CUDA kernel
    damp_percent=0.01
)

model = AutoGPTQForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-chat-hf",
    quantize_config=config
)

# Calibration data
from datasets import load_dataset
dataset = load_dataset("c4", split="train", streaming=True)
calibration_data = [
    tokenizer(example["text"])["input_ids"][:512]
    for example in dataset.take(128)
]

model.quantize(calibration_data)
model.save_quantized("llama-2-7b-gptq")
```

**GGUF Conversion for Edge Deployment** [12-inference-serving/llama-cpp/SKILL.md:59-68]():
```bash
# Convert GPTQ to GGUF for CPU/Metal deployment
python convert_hf_to_gguf.py models/llama-2-7b-gptq/

# Result: Multiple quantization levels
# Q2_K: 2.7GB (fastest, lower quality)
# Q4_K_M: 4GB (recommended default)
# Q6_K: 5.5GB (best quality)
```

**Sources**: [10-optimization/gptq/SKILL.md:86-116](), [12-inference-serving/llama-cpp/SKILL.md:108-134](), [12-inference-serving/tensorrt-llm/SKILL.md:114-128]()

## Production Deployment Architectures

### Single-GPU Deployment Pattern

For models that fit on a single GPU (7B-13B), the deployment is straightforward.

```mermaid
graph TB
    subgraph "Client Layer"
        HTTP_CLIENT["HTTP Client<br/>OpenAI SDK compatible"]
    end
    
    subgraph "Server Layer (Single GPU)"
        SERVER_PROCESS["Inference Server<br/>sglang.launch_server<br/>or llama-server<br/>Port 30000"]
        
        RADIX_CACHE["RadixAttention Cache<br/>Prefix reuse<br/>5-10x speedup"]
        
        MODEL_LOAD["Loaded Model<br/>meta-llama/Llama-3-8B<br/>16GB VRAM"]
        
        SERVER_PROCESS --> RADIX_CACHE
        RADIX_CACHE --> MODEL_LOAD
    end
    
    subgraph "OpenAI-Compatible API"
        ENDPOINT_CHAT["/v1/chat/completions"]
        ENDPOINT_COMPLETE["/v1/completions"]
        ENDPOINT_EMBED["/v1/embeddings"]
    end
    
    HTTP_CLIENT --> ENDPOINT_CHAT
    HTTP_CLIENT --> ENDPOINT_COMPLETE
    HTTP_CLIENT --> ENDPOINT_EMBED
    
    ENDPOINT_CHAT --> SERVER_PROCESS
    ENDPOINT_COMPLETE --> SERVER_PROCESS
    ENDPOINT_EMBED --> SERVER_PROCESS
```

**Implementation Example** [12-inference-serving/sglang/SKILL.md:52-70]():
```bash
# Launch SGLang server (single GPU)
python -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3-8B-Instruct \
    --port 30000 \
    --enable-radix-cache  # Automatic prefix caching

# Or llama.cpp server for CPU/Metal
./llama-server \
    -m models/llama-3-8b.Q4_K_M.gguf \
    --host 0.0.0.0 \
    --port 8080 \
    -ngl 999  # Offload all layers to GPU/Metal
```

**Client Usage** [12-inference-serving/sglang/SKILL.md:377-404]():
```python
from openai import OpenAI

# Works with any OpenAI-compatible server
client = OpenAI(
    base_url="http://localhost:30000/v1",
    api_key="EMPTY"
)

response = client.chat.completions.create(
    model="default",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Explain quantum computing"}
    ],
    temperature=0.7,
    max_tokens=200
)

print(response.choices[0].message.content)
```

**Sources**: [12-inference-serving/sglang/SKILL.md:52-104](), [12-inference-serving/llama-cpp/SKILL.md:86-104]()

### Multi-GPU Deployment Pattern

For large models (70B+), tensor parallelism splits the model across GPUs.

```mermaid
graph TB
    subgraph "Load Balancer"
        LB["nginx/HAProxy<br/>Round-robin"]
    end
    
    subgraph "Inference Server (8× A100 80GB)"
        SERVER["trtllm-serve or SGLang<br/>Tensor Parallelism TP=8"]
        
        subgraph "Model Sharding"
            GPU0["GPU 0<br/>Layers 0-9<br/>+ Embeddings"]
            GPU1["GPU 1<br/>Layers 10-19"]
            GPU2["GPU 2<br/>Layers 20-29"]
            GPU3["GPU 3<br/>Layers 30-39"]
            GPU4["GPU 4<br/>Layers 40-49"]
            GPU5["GPU 5<br/>Layers 50-59"]
            GPU6["GPU 6<br/>Layers 60-69"]
            GPU7["GPU 7<br/>Layers 70-79<br/>+ LM Head"]
        end
        
        NCCL["NCCL Communication<br/>All-reduce for<br/>attention outputs"]
        
        SERVER --> GPU0
        SERVER --> GPU1
        SERVER --> GPU2
        SERVER --> GPU3
        SERVER --> GPU4
        SERVER --> GPU5
        SERVER --> GPU6
        SERVER --> GPU7
        
        GPU0 --> NCCL
        GPU1 --> NCCL
        GPU2 --> NCCL
        GPU3 --> NCCL
        GPU4 --> NCCL
        GPU5 --> NCCL
        GPU6 --> NCCL
        GPU7 --> NCCL
    end
    
    LB --> SERVER
```

**Implementation Example** [12-inference-serving/tensorrt-llm/SKILL.md:129-138]():
```bash
# TensorRT-LLM with 8-way tensor parallelism
trtllm-serve meta-llama/Meta-Llama-3-70B \
    --tp_size 8 \              # Split across 8 GPUs
    --max_batch_size 256 \
    --max_num_tokens 8192

# Or SGLang
python -m sglang.launch_server \
    --model-path meta-llama/Meta-Llama-3-70B-Instruct \
    --tp 8 \                   # Tensor parallelism
    --port 30000
```

**Multi-GPU with GPTQ** [10-optimization/gptq/SKILL.md:341-362]():
```python
from auto_gptq import AutoGPTQForCausalLM

# Automatic device mapping across GPUs
model = AutoGPTQForCausalLM.from_quantized(
    "TheBloke/Llama-2-70B-GPTQ",
    device_map="auto",  # Automatically split across GPUs
    max_memory={
        0: "40GB",  # GPU 0
        1: "40GB"   # GPU 1
    }
)

# Or manual layer mapping
device_map = {
    "model.embed_tokens": 0,
    "model.layers.0-39": 0,   # First 40 layers on GPU 0
    "model.layers.40-79": 1,  # Last 40 layers on GPU 1
    "model.norm": 1,
    "lm_head": 1
}

model = AutoGPTQForCausalLM.from_quantized(
    model_name,
    device_map=device_map
)
```

**Sources**: [12-inference-serving/tensorrt-llm/SKILL.md:129-138](), [12-inference-serving/sglang/SKILL.md:64-70](), [10-optimization/gptq/SKILL.md:341-362]()

### Hybrid CPU+GPU Deployment

For very large models on limited GPU memory, offload layers to CPU.

```mermaid
graph TB
    subgraph "Hybrid Deployment Architecture"
        INPUT["Input Tokens<br/>Batch of prompts"]
        
        subgraph "GPU Memory (24GB RTX 4090)"
            GPU_EMB["Embeddings<br/>Layer 0"]
            GPU_L1_20["Transformer Layers<br/>1-20<br/>GPU resident"]
            GPU_LM["LM Head<br/>Output"]
        end
        
        subgraph "CPU Memory (64GB RAM)"
            CPU_L21_40["Transformer Layers<br/>21-40<br/>CPU offload<br/>Slower but fits"]
        end
        
        PCIE["PCIe Transfer<br/>Activations only<br/>Bottleneck"]
        
        INPUT --> GPU_EMB
        GPU_EMB --> GPU_L1_20
        GPU_L1_20 --> PCIE
        PCIE --> CPU_L21_40
        CPU_L21_40 --> PCIE
        PCIE --> GPU_LM
    end
```

**Implementation** [12-inference-serving/llama-cpp/SKILL.md:154-160]():
```bash
# llama.cpp hybrid deployment
./llama-cli \
    -m llama-70b.Q4_K_M.gguf \
    -ngl 20  # Offload only 20 layers to GPU
             # Remaining 60 layers run on CPU
             # Slower but allows 70B on single RTX 4090

# GPTQ with CPU offloading
```

**GPTQ CPU Offloading** [10-optimization/gptq/SKILL.md:366-378]():
```python
model = AutoGPTQForCausalLM.from_quantized(
    "TheBloke/Llama-2-405B-GPTQ",
    device_map="auto",
    max_memory={
        0: "80GB",      # GPU 0
        1: "80GB",      # GPU 1
        2: "80GB",      # GPU 2
        "cpu": "200GB"  # Offload overflow to CPU
    }
)
```

**Performance Impact**:
- GPU layers: ~50-100 tok/s
- CPU layers: ~5-10 tok/s
- Bottleneck: PCIe bandwidth (16 GB/s)
- Use case: Inference when throughput > latency priority

**Sources**: [12-inference-serving/llama-cpp/SKILL.md:154-160](), [10-optimization/gptq/SKILL.md:366-378]()

## Performance Benchmarking Workflow

Before deploying to production, benchmark your specific configuration.

```mermaid
flowchart LR
    subgraph "Benchmark Setup"
        MODEL["Select Model<br/>meta-llama/Llama-3-8B"]
        HARDWARE["Configure Hardware<br/>A100/H100/RTX/CPU"]
        ENGINE["Choose Engine<br/>TensorRT/vLLM/SGLang"]
    end
    
    subgraph "Load Testing"
        EVAL_HARNESS["lm_eval for Quality<br/>MMLU/GSM8K/HumanEval"]
        THROUGHPUT["Throughput Test<br/>Batch inference<br/>Measure tok/s"]
        LATENCY["Latency Test<br/>Single request<br/>TTFT/TPOT"]
    end
    
    subgraph "Results Analysis"
        QUALITY["Quality Metrics<br/>Accuracy degradation<br/>from quantization"]
        PERF["Performance Metrics<br/>Throughput: tok/s<br/>Latency: ms/token"]
        COST["Cost Analysis<br/>$/1M tokens<br/>GPU hours"]
    end
    
    subgraph "Decision"
        DEPLOY{"Meets SLA?"}
        OPTIMIZE["Optimize<br/>Quantization<br/>Batching<br/>Parallelism"]
        PRODUCTION["Deploy to<br/>Production"]
    end
    
    MODEL --> EVAL_HARNESS
    HARDWARE --> THROUGHPUT
    ENGINE --> LATENCY
    
    EVAL_HARNESS --> QUALITY
    THROUGHPUT --> PERF
    LATENCY --> PERF
    
    QUALITY --> DEPLOY
    PERF --> DEPLOY
    COST --> DEPLOY
    
    DEPLOY -->|No| OPTIMIZE
    DEPLOY -->|Yes| PRODUCTION
    OPTIMIZE --> EVAL_HARNESS
```

**Quality Benchmarking** [11-evaluation/lm-evaluation-harness/SKILL.md:99-116]():
```bash
# Benchmark quantized model quality
lm_eval --model hf \
  --model_args pretrained=TheBloke/Llama-2-7B-GPTQ,load_in_4bit=True \
  --tasks mmlu,gsm8k,hellaswag,truthfulqa,arc_challenge \
  --num_fewshot 5 \
  --batch_size 8 \
  --output_path results/gptq-eval.json

# Compare against FP16 baseline
lm_eval --model hf \
  --model_args pretrained=meta-llama/Llama-2-7b-hf \
  --tasks mmlu,gsm8k,hellaswag,truthfulqa,arc_challenge \
  --num_fewshot 5 \
  --output_path results/fp16-baseline.json
```

**Throughput Benchmarking** [12-inference-serving/sglang/SKILL.md:144-153]():
```python
import sglang as sgl
import time

# Batch throughput test
prompts = [f"Question {i}: Explain concept" for i in range(100)]

start = time.time()
outputs = llm.generate(
    prompts,
    sampling_params=SamplingParams(max_tokens=200)
)
end = time.time()

total_tokens = sum(len(o.text.split()) for o in outputs)
throughput = total_tokens / (end - start)
print(f"Throughput: {throughput:.0f} tokens/sec")
```

**Expected Results by Configuration**:

| Engine | Hardware | Model | Throughput | Latency (TTFT) | Use Case |
|--------|----------|-------|-----------|----------------|----------|
| TensorRT-LLM | H100 | Llama 3-8B | 24,000 tok/s | ~10ms | Max throughput |
| SGLang | A100 | Llama 3-8B | 5,000 tok/s (agents) | ~15ms | Prefix reuse |
| vLLM | A100 | Llama 3-8B | 2,800 tok/s | ~20ms | General purpose |
| llama.cpp | M3 Max | Llama 3-8B Q4 | 50 tok/s | ~50ms | Local/edge |

**Sources**: [11-evaluation/lm-evaluation-harness/SKILL.md:99-116](), [12-inference-serving/tensorrt-llm/SKILL.md:154-164](), [12-inference-serving/sglang/SKILL.md:277-302]()

## Common Deployment Anti-Patterns

**Anti-Pattern 1: Using TensorRT-LLM on AMD GPUs**
- TensorRT-LLM requires NVIDIA CUDA
- Solution: Use llama.cpp with `LLAMA_HIP=1` for ROCm, or vLLM

**Anti-Pattern 2: Quantizing Already-Quantized Models**
- GPTQ → GGUF is valid (format conversion)
- GPTQ → GPTQ again degrades quality significantly
- Solution: Always quantize from FP16 baseline

**Anti-Pattern 3: Not Measuring Actual Workload Performance**
- Synthetic benchmarks don't match real workload
- Solution: Benchmark with representative prompts (length, structure)

**Anti-Pattern 4: Over-Provisioning GPUs for Small Models**
- 7B model doesn't need 8× H100s
- Solution: Use cost-effective GPU (single A10, L4, or even CPU)

**Anti-Pattern 5: Ignoring Batch Size Impact**
- Single-request latency ≠ throughput
- Solution: Tune batch size for your latency SLA

**Sources**: [12-inference-serving/tensorrt-llm/SKILL.md:24-33](), [10-optimization/gptq/SKILL.md:16-32]()

## Integration Patterns

### OpenAI-Compatible API Pattern

All major inference engines expose OpenAI-compatible APIs, enabling drop-in replacement.

```mermaid
graph LR
    subgraph "Application Code"
        APP["Application<br/>OpenAI SDK"]
    end
    
    subgraph "Inference Backends (Swappable)"
        OPENAI_API["OpenAI API<br/>api.openai.com"]
        TRT_API["TensorRT-LLM<br/>localhost:8000/v1"]
        SGL_API["SGLang<br/>localhost:30000/v1"]
        LLAMA_API["llama.cpp<br/>localhost:8080/v1"]
    end
    
    subgraph "Common Interface"
        ENDPOINT_CHAT_INT["/v1/chat/completions<br/>/v1/completions<br/>/v1/embeddings"]
    end
    
    APP --> ENDPOINT_CHAT_INT
    ENDPOINT_CHAT_INT --> OPENAI_API
    ENDPOINT_CHAT_INT --> TRT_API
    ENDPOINT_CHAT_INT --> SGL_API
    ENDPOINT_CHAT_INT --> LLAMA_API
```

**Implementation** [12-inference-serving/sglang/SKILL.md:397-404]():
```python
from openai import OpenAI

# Point to local inference server (swap base_url)
client = OpenAI(
    base_url="http://localhost:30000/v1",  # SGLang
    # base_url="http://localhost:8080/v1",  # llama.cpp
    # base_url="http://localhost:8000/v1",  # TensorRT-LLM
    api_key="EMPTY"
)

# Same code works with all backends
response = client.chat.completions.create(
    model="default",
    messages=[{"role": "user", "content": "Hello"}]
)
```

**Sources**: [12-inference-serving/sglang/SKILL.md:377-404](), [12-inference-serving/llama-cpp/SKILL.md:86-104]()

### Agent Function Calling Pattern

For agentic workflows, structured generation with tool definitions.

```mermaid
graph TB
    subgraph "Agent Runtime"
        AGENT["Agent Logic<br/>AutoGPT/LangChain"]
        TOOLS["Tool Definitions<br/>JSON schema"]
    end
    
    subgraph "SGLang Server"
        SGL_FUNC["@sgl.function<br/>agent_workflow"]
        
        RADIX["RadixAttention<br/>System prompt cached<br/>5x speedup"]
        
        STRUCT_GEN["Structured Generation<br/>sgl.gen with tools<br/>JSON schema validation"]
    end
    
    subgraph "Tool Execution"
        TOOL_1["get_weather API"]
        TOOL_2["book_flight API"]
        TOOL_3["search_web API"]
    end
    
    AGENT --> TOOLS
    TOOLS --> SGL_FUNC
    SGL_FUNC --> RADIX
    RADIX --> STRUCT_GEN
    STRUCT_GEN --> TOOL_1
    STRUCT_GEN --> TOOL_2
    STRUCT_GEN --> TOOL_3
```

**Implementation** [12-inference-serving/sglang/SKILL.md:214-276]():
```python
import sglang as sgl

# Define tools (cached system prompt)
tools = [
    {
        "name": "get_weather",
        "description": "Get weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"}
            }
        }
    }
]

@sgl.function
def agent_workflow(s, user_query, tools):
    # System prompt (cached with RadixAttention)
    s += "You are a helpful assistant with access to tools.\n"
    s += f"Available tools: {tools}\n\n"
    
    # User query (new each time)
    s += f"User: {user_query}\n"
    s += "Assistant: "
    
    # Generate with function calling
    s += sgl.gen(
        "response",
        max_tokens=200,
        tools=tools,  # SGLang handles tool format
        stop=["User:", "\n\n"]
    )

# First call: computes system prompt
state1 = agent_workflow.run(
    user_query="What's the weather in NYC?",
    tools=tools
)

# Second call: reuses system prompt (5× faster)
state2 = agent_workflow.run(
    user_query="Book a flight to LA",
    tools=tools
)
```

**Sources**: [12-inference-serving/sglang/SKILL.md:214-276]()

## Summary: Decision Framework

**Step 1: Identify Hardware Constraints**
- NVIDIA datacenter (A100/H100) → TensorRT-LLM or SGLang
- NVIDIA consumer (RTX) → vLLM or GPTQ + vLLM
- Apple Silicon → llama.cpp with Metal
- CPU only → llama.cpp
- AMD GPU → llama.cpp with ROCm

**Step 2: Identify Workload Type**
- Maximum throughput → TensorRT-LLM
- Agents with tool calls → SGLang (RadixAttention)
- Simple generation → vLLM
- Edge deployment → llama.cpp

**Step 3: Select Quantization**
- H100: FP8 (2× speed, <1% loss)
- A100/RTX: GPTQ 4-bit (4× compression, ~1.5% loss)
- CPU/Edge: GGUF Q4_K_M (4× compression, ~2% loss)
- Quality critical: GGUF Q6_K or no quantization

**Step 4: Benchmark Before Production**
- Quality: `lm_eval --tasks mmlu,gsm8k,hellaswag`
- Throughput: Batch inference test
- Latency: Single request TTFT/TPOT

**Step 5: Monitor in Production**
- See [Production Observability with Phoenix](#4.3)

**Sources**: All files in [12-inference-serving/]() and [10-optimization/gptq/]()

---

