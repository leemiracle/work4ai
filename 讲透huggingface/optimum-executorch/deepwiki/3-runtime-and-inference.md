<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-executorch · page 3 Runtime and Inference · fetched 2026-10-26 -->

# Runtime and Inference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [optimum/executorch/modeling.py](optimum/executorch/modeling.py)
- [optimum/exporters/executorch/utils.py](optimum/exporters/executorch/utils.py)

</details>



This document explains how to load and run ExecuTorch models for inference using the optimum-executorch runtime system. It covers the model loading process, inference execution, text generation capabilities, and performance monitoring features.

For information about exporting models to ExecuTorch format, see [Model Export System](#2). For details on optimization features like quantization and custom attention, see [Optimization Features](#4).

## Model Loading System

The runtime system provides task-specific model classes that wrap ExecuTorch's low-level runtime with a familiar HuggingFace-style API. All model classes inherit from `ExecuTorchModelBase` and provide a `from_pretrained()` method for loading models.

### Model Class Hierarchy

```mermaid
graph TD
    Base["ExecuTorchModelBase<br/>Abstract base class"]
    CausalLM["ExecuTorchModelForCausalLM<br/>AutoModelForCausalLM"]
    Seq2Seq["ExecuTorchModelForSeq2SeqLM<br/>AutoModelForSeq2SeqLM"] 
    Speech["ExecuTorchModelForSpeechSeq2Seq<br/>AutoModelForSpeechSeq2Seq"]
    Vision["ExecuTorchModelForImageClassification<br/>AutoModelForImageClassification"]
    MaskedLM["ExecuTorchModelForMaskedLM<br/>AutoModelForMaskedLM"]
    
    Base --> CausalLM
    Base --> Seq2Seq
    Base --> Speech
    Base --> Vision
    Base --> MaskedLM
    
    CausalLM --> CausalMethods["text_generation()<br/>generate()"]
    Seq2Seq --> Seq2SeqMethods["text_generation()<br/>generate()"]
    Speech --> SpeechMethods["transcribe()<br/>generate()"]
    Vision --> VisionMethods["forward()"]
    MaskedLM --> MaskedMethods["forward()"]
```

Sources: [optimum/executorch/modeling.py:56-370]()

### Loading Process

The model loading process supports multiple sources and automatically handles model export if needed:

```mermaid
graph LR
    subgraph Sources
        HubID["HuggingFace Hub ID<br/>meta-llama/Llama-3.2-1B"]
        LocalPTE["Local .pte file<br/>model.pte"]
        LocalDir["Local directory<br/>./my_model/"]
    end
    
    subgraph Loading
        FromPretrained["from_pretrained()"]
        CheckPTE["Check for .pte files<br/>find_files_matching_pattern()"]
        Export["Export if needed<br/>_export()"]
        LoadPTE["Load .pte file<br/>_load_for_executorch()"]
    end
    
    subgraph Runtime
        ETModule["ExecuTorchModule<br/>Low-level runtime"]
        Metadata["Extract metadata<br/>method_names()"]
        ModelInstance["ExecuTorchModelForXXX<br/>Ready for inference"]
    end
    
    HubID --> FromPretrained
    LocalPTE --> FromPretrained
    LocalDir --> FromPretrained
    
    FromPretrained --> CheckPTE
    CheckPTE --> Export
    CheckPTE --> LoadPTE
    Export --> LoadPTE
    LoadPTE --> ETModule
    ETModule --> Metadata
    Metadata --> ModelInstance
```

Sources: [optimum/executorch/modeling.py:278-371](), [optimum/executorch/modeling.py:134-193]()

### Model Metadata Extraction

During initialization, models extract configuration metadata from the `.pte` file using ExecuTorch's method introspection:

| Metadata Method | Purpose | Example Value |
|----------------|---------|---------------|
| `use_kv_cache` | KV cache enabled | `True` |
| `get_max_seq_len` | Maximum sequence length | `2048` |
| `get_max_batch_size` | Maximum batch size | `1` |
| `get_dtype` | Model data type | `5` (float16) |
| `get_bos_id` | Beginning-of-sequence token | `1` |
| `get_eos_ids` | End-of-sequence tokens | `[2, 32000]` |
| `get_vocab_size` | Vocabulary size | `32000` |
| `use_sdpa_with_kv_cache` | Custom SDPA enabled | `True` |

Sources: [optimum/executorch/modeling.py:606-625](), [optimum/exporters/executorch/utils.py:21-66]()

## Inference Runtime Core

The runtime system uses ExecuTorch's `ExecuTorchModule` as the underlying inference engine, wrapped by task-specific model classes that provide familiar APIs.

### Runtime Architecture

```mermaid
graph TD
    subgraph "Python API Layer"
        ModelAPI["ExecuTorchModelForXXX<br/>High-level API"]
        Forward["forward()<br/>Single inference call"]
        Generate["generate()<br/>Autoregressive generation"]
        TextGen["text_generation()<br/>End-to-end pipeline"]
    end
    
    subgraph "ExecuTorch Runtime"
        ETModule["ExecuTorchModule<br/>C++ runtime binding"]
        Methods["Available methods:<br/>• forward<br/>• method_names<br/>• run_method"]
        PTEFile[".pte file<br/>Portable executable"]
    end
    
    subgraph "Performance Tracking"
        Stats["Stats<br/>Performance monitoring"]
        Timing["Timing measurements:<br/>• Prompt evaluation<br/>• Token generation<br/>• First token latency"]
    end
    
    ModelAPI --> Forward
    ModelAPI --> Generate
    ModelAPI --> TextGen
    
    Forward --> ETModule
    Generate --> ETModule
    TextGen --> Generate
    
    ETModule --> Methods
    ETModule --> PTEFile
    
    Forward --> Stats
    Generate --> Stats
```

Sources: [optimum/executorch/modeling.py:39](), [optimum/executorch/modeling.py:627-652](), [optimum/executorch/stats.py]()

### Forward Pass Execution

The `forward()` method provides direct access to model inference with minimal overhead:

For causal language models, the forward pass signature is:
```python
forward(input_ids: torch.Tensor, cache_position: torch.Tensor) -> torch.Tensor
```

For sequence-to-sequence models:
```python
forward(input_ids: torch.Tensor, decoder_input_ids: torch.Tensor, 
        cache_position: torch.Tensor, encoder_outputs: Optional[torch.Tensor]) -> Tuple
```

Sources: [optimum/executorch/modeling.py:627-652](), [optimum/executorch/modeling.py:432-448]()

## Text Generation Capabilities

The runtime provides sophisticated text generation capabilities with support for both causal and sequence-to-sequence models.

### Generation Flow

```mermaid
graph TD
    subgraph "Input Processing"
        Prompt["Text prompt"]
        Tokenize["Tokenizer.encode()<br/>Convert to token IDs"]
        ValidateTokens["Verify EOS tokens<br/>verify_eos_tokens_in_tokenizer()"]
    end
    
    subgraph "Generation Loop"
        PrefillCheck["Check sequence length<br/>Parallel vs sequential prefill"]
        ParallelPrefill["Parallel prefill<br/>Process all prompt tokens at once"]
        SeqPrefill["Sequential prefill<br/>Process tokens one by one"]
        AutoRegressive["Autoregressive generation<br/>Generate one token at a time"]
        StopCheck["Check stopping criteria<br/>EOS token or max length"]
    end
    
    subgraph "Output Processing"
        TokenList["Generated token IDs"]
        Decode["Tokenizer.decode()<br/>Convert to text"]
        Result["Generated text"]
    end
    
    Prompt --> Tokenize
    Tokenize --> ValidateTokens
    ValidateTokens --> PrefillCheck
    
    PrefillCheck --> ParallelPrefill
    PrefillCheck --> SeqPrefill
    
    ParallelPrefill --> AutoRegressive
    SeqPrefill --> AutoRegressive
    
    AutoRegressive --> StopCheck
    StopCheck --> AutoRegressive
    StopCheck --> TokenList
    
    TokenList --> Decode
    Decode --> Result
```

Sources: [optimum/executorch/modeling.py:654-743](), [optimum/executorch/modeling.py:745-796]()

### Dynamic Shape Support

The generation system supports two modes based on the exported model's capabilities:

**Parallel Prefill** (dynamic shapes enabled):
- Processes entire prompt in a single forward pass
- Significantly faster for long prompts (up to 20x speedup)
- Determined by checking `model.method_meta("forward").input_tensor_meta(1).sizes()[0] > 1`

**Sequential Prefill** (static shapes):
- Processes prompt tokens one by one
- Maintained for backward compatibility
- Used when model was exported without dynamic shapes

Sources: [optimum/executorch/modeling.py:693-714]()

### Speech-to-Text Generation

The `ExecuTorchModelForSpeechSeq2Seq` class provides specialized generation for audio transcription:

```python
transcribe(tokenizer, input_features, echo=True, max_seq_len=None)
```

Where `input_features` is a log-mel spectrogram tensor of shape `[1, 80, 3000]` or `[1, 128, 3000]` for 30-second audio chunks.

Sources: [optimum/executorch/modeling.py:1066-1100]()

## Performance Monitoring

The runtime includes comprehensive performance tracking through the `Stats` class, which measures inference timing and throughput.

### Performance Metrics

```mermaid
graph LR
    subgraph "Timing Events"
        InferStart["on_inference_start()"]
        TokenEncode["on_token_encode_end()"]
        PromptEval["on_prompt_eval_end()"]
        FirstToken["on_first_token()"]
        SamplingLoop["on_sampling_begin()<br/>on_sampling_end()"]
        InferEnd["on_inference_end()"]
    end
    
    subgraph "Calculated Metrics"
        TTFT["Time to First Token<br/>(TTFT)"]
        Throughput["Token throughput<br/>(tokens/second)"]
        TotalTime["Total inference time"]
        PromptTok["Prompt tokens/second"]
    end
    
    subgraph "Reporting"
        PrintReport["print_report()<br/>Console output"]
        Benchmarks["Performance comparison<br/>Device-specific results"]
    end
    
    InferStart --> TokenEncode
    TokenEncode --> PromptEval
    PromptEval --> FirstToken
    FirstToken --> SamplingLoop
    SamplingLoop --> InferEnd
    
    PromptEval --> TTFT
    SamplingLoop --> Throughput
    InferEnd --> TotalTime
    PromptEval --> PromptTok
    
    TTFT --> PrintReport
    Throughput --> PrintReport
    TotalTime --> PrintReport
    PromptTok --> PrintReport
    
    PrintReport --> Benchmarks
```

### Device Performance Examples

Performance metrics from real-world deployments show significant improvements with optimizations:

| Device | Model | Throughput | Notes |
|--------|--------|------------|-------|
| Samsung Galaxy S22 | Llama-3.2-1B | 202 tok/s | With custom SDPA |
| iPhone 15 Pro | Llama-3.2-1B | 29.6 tok/s | XNNPACK backend |
| Standard setup | Llama-3.2-1B | ~67 tok/s | Without custom SDPA |

The custom SDPA optimization provides approximately 3x speedup over standard attention mechanisms.

Sources: [optimum/executorch/modeling.py:103](), [optimum/executorch/modeling.py:441-447](), [optimum/executorch/modeling.py:642]()

---

