<!-- source: DeepWiki mcp.deepwiki.com · repo deepseek-ai/DeepSeek-V3.2-Exp · extra page Text Generation · fetched 2026-10-30 -->

# Text Generation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [inference/generate.py](inference/generate.py)

</details>



This document covers the text generation interface provided by `generate.py`, which serves as the primary interactive and batch inference system for DeepSeek-V3.2-Exp. This module handles distributed token generation, conversation management, and provides both command-line and interactive interfaces for model inference.

For information about the underlying model architecture, see [Model Implementation](#2.3.3). For details about weight conversion prior to generation, see [Weight Conversion](#2.3.1).

## Purpose and Architecture

The text generation system is built around the `generate.py` script, which provides a complete inference pipeline supporting:

- **Distributed Execution**: Multi-GPU inference using `torch.distributed`
- **Interactive Chat**: Conversational interface with chat template support
- **Batch Processing**: File-based batch inference for multiple prompts
- **Temperature Sampling**: Configurable token sampling with temperature control

## Generation Pipeline Overview

```mermaid
graph TD
    CLI["ArgumentParser"] --> Main["main()"]
    Main --> DistInit["dist.init_process_group()"]
    Main --> ModelLoad["Transformer + safetensors loading"]
    Main --> TokenizerLoad["AutoTokenizer.from_pretrained()"]
    
    ModelLoad --> Interactive["Interactive Mode"]
    ModelLoad --> Batch["Batch Mode"]
    
    Interactive --> ChatLoop["Chat Message Loop"]
    Batch --> FileRead["File Prompt Processing"]
    
    ChatLoop --> ApplyTemplate["tokenizer.apply_chat_template()"]
    FileRead --> ApplyTemplate
    
    ApplyTemplate --> Generate["generate()"]
    Generate --> ForwardPass["model.forward()"]
    ForwardPass --> Sample["sample()"]
    Sample --> TokenDecoding["tokenizer.decode()"]
    
    style Generate fill:#e8f5e8
    style ForwardPass fill:#fff3e0
    style Sample fill:#e3f2fd
```

Sources: [inference/generate.py:81-186]()

## Core Generation Functions

### Token Generation Loop

The primary generation logic is implemented in the `generate()` function, which handles autoregressive token generation with distributed execution support:

```mermaid
graph TD
    GenerateStart["generate(model, prompt_tokens, max_new_tokens, eos_id, temperature)"] --> TokenInit["tokens = torch.full((batch_size, total_len), -1)"]
    TokenInit --> PromptFill["Fill initial prompt tokens"]
    PromptFill --> GenLoop["Generation Loop: cur_pos in range(min_prompt_lens, total_len)"]
    
    GenLoop --> ModelForward["logits = model.forward(tokens[:, prev_pos:cur_pos], prev_pos)"]
    ModelForward --> TempCheck{"temperature > 0?"}
    
    TempCheck -->|Yes| SampleCall["next_token = sample(logits, temperature)"]
    TempCheck -->|No| ArgMax["next_token = logits.argmax(dim=-1)"]
    
    SampleCall --> MaskCheck["Apply prompt_mask"]
    ArgMax --> MaskCheck
    
    MaskCheck --> TokenAssign["tokens[:, cur_pos] = next_token"]
    TokenAssign --> EosCheck["Check finished condition (EOS tokens)"]
    EosCheck --> AllFinished{"finished.all()?"}
    
    AllFinished -->|No| GenLoop
    AllFinished -->|Yes| CompletionExtract["Extract completion_tokens"]
    CompletionExtract --> ReturnTokens["return completion_tokens"]
    
    style ModelForward fill:#fff3e0
    style SampleCall fill:#e3f2fd
    style EosCheck fill:#e8f5e8
```

Sources: [inference/generate.py:30-78]()

### Temperature Sampling

The `sample()` function implements temperature-controlled token sampling using the Gumbel-max trick:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `logits` | `torch.Tensor` | Raw model predictions for next token |
| `temperature` | `float` | Controls randomness (1.0 = normal, <1.0 = more deterministic, >1.0 = more random) |

The sampling process applies temperature scaling, softmax normalization, and Gumbel-max sampling for efficient token selection.

Sources: [inference/generate.py:14-27]()

## Execution Modes

### Interactive Mode

Interactive mode provides a conversational interface with persistent chat history:

```mermaid
graph TD
    InteractiveStart["interactive=True"] --> MessageInit["messages = []"]
    MessageInit --> InputLoop["Input Loop"]
    
    InputLoop --> GetPrompt["Get user input via input() or dist.broadcast_object_list()"]
    GetPrompt --> CommandCheck{"Command check"}
    
    CommandCheck -->|"/exit"| ExitLoop["break"]
    CommandCheck -->|"/clear"| ClearMessages["messages.clear()"]
    CommandCheck -->|"regular input"| AddUserMsg["messages.append({'role': 'user', 'content': prompt})"]
    
    AddUserMsg --> ApplyTemplate["tokenizer.apply_chat_template(messages, add_generation_prompt=True)"]
    ApplyTemplate --> CallGenerate["generate(model, [prompt_tokens], ...)"]
    CallGenerate --> DecodeTokens["tokenizer.decode(completion_tokens[0])"]
    DecodeTokens --> PrintResponse["print(completion)"]
    PrintResponse --> AddAssistantMsg["messages.append({'role': 'assistant', 'content': completion})"]
    
    AddAssistantMsg --> InputLoop
    ClearMessages --> InputLoop
    
    style GetPrompt fill:#e8f5e8
    style CallGenerate fill:#fff3e0
    style DecodeTokens fill:#e3f2fd
```

Sources: [inference/generate.py:122-145]()

### Batch Mode

Batch mode processes multiple prompts from a file, supporting parallel inference:

| Configuration | Details |
|---------------|---------|
| Input Format | Double newline-separated prompts in text file |
| Batch Size Limit | `args.max_batch_size` from model configuration |
| Processing | Parallel tokenization and generation |
| Output Format | Prompt-completion pairs printed to stdout |

Sources: [inference/generate.py:146-156]()

## Distributed Execution Setup

The distributed execution system initializes multi-GPU inference using NCCL backend:

```mermaid
graph TD
    EnvVars["Environment Variables: WORLD_SIZE, RANK, LOCAL_RANK"] --> DistCheck{"world_size > 1?"}
    
    DistCheck -->|Yes| InitPG["dist.init_process_group('nccl')"]
    DistCheck -->|No| SingleGPU["Single GPU Mode"]
    
    InitPG --> RankCheck{"rank != 0?"}
    RankCheck -->|Yes| SuppressPrint["print = lambda *_, **__: None"]
    RankCheck -->|No| KeepPrint["Keep print functionality"]
    
    SuppressPrint --> DeviceSet["torch.cuda.set_device(local_rank)"]
    KeepPrint --> DeviceSet
    SingleGPU --> DeviceSet
    
    DeviceSet --> LoadModel["load_model(model, f'model{rank}-mp{world_size}.safetensors')"]
    LoadModel --> BroadcastSync["Synchronize input via dist.broadcast_object_list()"]
    
    style InitPG fill:#fff3e0
    style LoadModel fill:#e8f5e8
    style BroadcastSync fill:#e3f2fd
```

| Environment Variable | Purpose |
|---------------------|---------|
| `WORLD_SIZE` | Total number of processes |
| `RANK` | Global rank of current process |
| `LOCAL_RANK` | Local device rank for CUDA device assignment |

Sources: [inference/generate.py:100-119](), [inference/generate.py:125-134]()

## Command Line Interface

The CLI supports the following arguments for controlling generation behavior:

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--ckpt-path` | `str` | Required | Path to model checkpoint directory |
| `--config` | `str` | Required | Path to JSON model configuration |
| `--input-file` | `str` | `""` | File containing prompts for batch processing |
| `--interactive` | `bool` | `False` | Enable interactive chat mode |
| `--max-new-tokens` | `int` | `200` | Maximum tokens to generate per prompt |
| `--temperature` | `float` | `0.6` | Temperature for token sampling |

The system enforces that either `--input-file` or `--interactive` must be specified.

Sources: [inference/generate.py:177-186]()

---

