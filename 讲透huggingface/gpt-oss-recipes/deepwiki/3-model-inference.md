<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/gpt-oss-recipes · page 3 Model Inference · fetched 2026-10-26 -->

# Model Inference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [generate_all.py](generate_all.py)

</details>



## Purpose and Scope

This document provides an overview of the inference capabilities in the GPT-OSS recipes repository. The system offers four progressive inference scripts that demonstrate different optimization techniques for running OpenAI's GPT-OSS models (20B and 120B parameters). Each script builds upon the previous one, adding increasingly sophisticated optimizations for memory efficiency and throughput.

For detailed implementation of each optimization technique, see [Basic Tensor Parallelism](#3.1), [Flash Attention Optimization](#3.2), [Continuous Batching](#3.3), and [Advanced Inference Optimizations](#3.4). For training capabilities, see [Model Training](#4).

## Inference Script Progression

The repository provides four inference scripts that represent a progressive enhancement of optimization techniques:

**Optimization Progression Diagram**
```mermaid
graph LR
    generate_tp["generate_tp.py<br/>Tensor Parallelism"]
    generate_flash_attention["generate_flash_attention.py<br/>TP + Flash Attention"]
    generate_tp_continuous_batching["generate_tp_continuous_batching.py<br/>TP + Flash + Continuous Batching"]
    generate_all["generate_all.py<br/>All Optimizations + Expert Parallelism"]
    
    generate_tp --> generate_flash_attention
    generate_flash_attention --> generate_tp_continuous_batching
    generate_tp_continuous_batching --> generate_all
    
    subgraph "Optimization Techniques"
        TP["Tensor Parallelism"]
        FA["Flash Attention"]
        CB["Continuous Batching"]
        EP["Expert Parallelism"]
    end
    
    TP -.-> generate_tp
    TP -.-> generate_flash_attention
    TP -.-> generate_tp_continuous_batching
    TP -.-> generate_all
    
    FA -.-> generate_flash_attention
    FA -.-> generate_tp_continuous_batching
    FA -.-> generate_all
    
    CB -.-> generate_tp_continuous_batching
    CB -.-> generate_all
    
    EP -.-> generate_all
```

Sources: [README.md:7-10](), [generate_all.py:1-49]()

## Model Configuration System

All inference scripts support both 20B and 120B model variants through a unified configuration system. The `model_path` variable controls both model selection and automatic device mapping configuration:

**Model Configuration Flow**
```mermaid
graph TD
    model_path_config["model_path variable<br/>(Line 6-7 in each script)"]
    
    model_path_config --> size_check{"Model Size Detection"}
    
    size_check -->|"Contains '120b'"| large_config["120B Configuration<br/>tp_plan: 'auto'"]
    size_check -->|"Contains '20b'"| small_config["20B Configuration<br/>device_map: 'auto'"]
    
    large_config --> AutoModelForCausalLM_large["AutoModelForCausalLM.from_pretrained()<br/>with tp_plan"]
    small_config --> AutoModelForCausalLM_small["AutoModelForCausalLM.from_pretrained()<br/>with device_map"]
    
    subgraph "Model Variants"
        gpt_120b["openai/gpt-oss-120b"]
        gpt_20b["openai/gpt-oss-20b"]
    end
    
    gpt_120b --> large_config
    gpt_20b --> small_config
    
    subgraph "Runtime Configuration"
        torch_dtype["torch_dtype: 'auto'"]
        attn_implementation["attn_implementation:<br/>'kernels-community/vllm-flash-attn3'"]
    end
    
    torch_dtype --> AutoModelForCausalLM_large
    torch_dtype --> AutoModelForCausalLM_small
    attn_implementation --> AutoModelForCausalLM_large
    attn_implementation --> AutoModelForCausalLM_small
```

Sources: [generate_all.py:5-7](), [generate_all.py:24-30](), [generate_all.py:33-38]()

## Script Selection Guide

Choose the appropriate inference script based on your performance requirements and available hardware:

| Script | Optimizations | Use Case | Resource Requirements |
|--------|---------------|----------|----------------------|
| `generate_tp.py` | Tensor Parallelism | Basic distributed inference | Multiple GPUs |
| `generate_flash_attention.py` | TP + Flash Attention | Memory-efficient inference | Multiple GPUs with flash attention support |
| `generate_tp_continuous_batching.py` | TP + Flash + Continuous Batching | High-throughput serving | Multiple GPUs with batching optimization |
| `generate_all.py` | All optimizations + Expert Parallelism | Maximum performance | Multiple GPUs with full optimization stack |

Sources: [README.md:7-10]()

## Execution Modes

The inference scripts support both single-node and distributed execution patterns:

### Single Node Execution
```bash
python generate_<script_name>.py
```

### Distributed Execution
```bash
torchrun --nproc_per_node=x generate_<script_name>.py
```

### Configuration Variables

Each script contains standard configuration variables:

| Variable | Purpose | Example Values |
|----------|---------|----------------|
| `model_path` | Model selection | `"openai/gpt-oss-120b"`, `"openai/gpt-oss-20b"` |
| `GenerationConfig.max_new_tokens` | Output length control | `1024` |
| `attn_implementation` | Attention mechanism | `"kernels-community/vllm-flash-attn3"` |
| `torch_dtype` | Precision control | `"auto"` |

Sources: [README.md:58-67](), [generate_all.py:20-22](), [generate_all.py:36]()

## Common Generation Pattern

All inference scripts follow a consistent pattern:

**Inference Execution Flow**
```mermaid
graph TD
    AutoTokenizer_load["AutoTokenizer.from_pretrained(model_path)"]
    messages_setup["Chat message setup<br/>role: 'user', content: prompt"]
    apply_chat_template["tokenizer.apply_chat_template(messages)"]
    GenerationConfig_create["GenerationConfig(max_new_tokens=1024)"]
    
    AutoTokenizer_load --> messages_setup
    messages_setup --> apply_chat_template
    apply_chat_template --> GenerationConfig_create
    
    AutoModelForCausalLM_load["AutoModelForCausalLM.from_pretrained()"]
    model_eval["model.eval()"]
    
    AutoModelForCausalLM_load --> model_eval
    
    tokenizer_encode["tokenizer(chat_prompt, return_tensors='pt')"]
    model_generate["model.generate(**inputs, generation_config)"]
    tokenizer_decode["tokenizer.decode(outputs[0])"]
    
    GenerationConfig_create --> tokenizer_encode
    model_eval --> tokenizer_encode
    tokenizer_encode --> model_generate
    model_generate --> tokenizer_decode
```

Sources: [generate_all.py:9-48]()

---

