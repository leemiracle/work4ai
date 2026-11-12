<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-executorch · page 5 Supported Models · fetched 2026-10-26 -->

# Supported Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [tests/models/test_modeling_gemma2.py](tests/models/test_modeling_gemma2.py)

</details>



This document provides a comprehensive overview of the transformer models supported by optimum-executorch, including their specific architectures, implementation details, and usage patterns. The supported models span multiple domains including text generation, vision tasks, and audio processing, all optimized for deployment through the ExecuTorch runtime.

For detailed information about model export processes, see [Model Export System](#2). For runtime inference capabilities, see [Runtime and Inference](#3). For optimization features available for these models, see [Optimization Features](#4).

## Model Architecture Categories

The optimum-executorch library supports three primary categories of transformer architectures, each with specific implementation patterns and use cases:

```mermaid
graph TB
    subgraph "Encoder-Only Models"
        BERT["bert-base-uncased<br/>AutoModel"]
        ALBERT["albert-base-v2<br/>AutoModel"]
        DISTILBERT["distilbert-base-uncased<br/>AutoModel"]
        ROBERTA["xlm-roberta-base<br/>AutoModel"]
        EUROBERT["EuroBERT-210m<br/>AutoModel"]
    end
    
    subgraph "Decoder-Only Models"
        LLAMA["Llama-3.2-1B<br/>LlamaForCausalLM"]
        GEMMA["gemma-2-2b<br/>GemmaForCausalLM"]
        QWEN["Qwen2.5-0.5B<br/>Qwen2ForCausalLM"]
        PHI["Phi-4-mini-instruct<br/>PhiForCausalLM"]
        SMOLLM["SmolLM2-135M<br/>LlamaForCausalLM"]
        GPT2["gpt-sw3-126m<br/>GPT2LMHeadModel"]
    end
    
    subgraph "Encoder-Decoder Models"
        T5["t5-small<br/>T5ForConditionalGeneration"]
        WHISPER["whisper-tiny<br/>WhisperForConditionalGeneration"]
    end
    
    subgraph "Vision Models"
        VIT["deit-base-distilled-patch16-224<br/>DeiTForImageClassification"]
        EFFICIENTNET["efficientnet-b0<br/>EfficientNetForImageClassification"]
        SWIN["swin-tiny-patch4-window7-224<br/>SwinForImageClassification"]
        MOBILEVIT["mobilevit-xx-small<br/>MobileViTForImageClassification"]
    end
    
    subgraph "Task Implementations"
        CAUSAL_LM[ExecuTorchModelForCausalLM]
        MASKED_LM[ExecuTorchModelForMaskedLM]
        SEQ2SEQ_LM[ExecuTorchModelForSeq2SeqLM]
        SPEECH_SEQ2SEQ[ExecuTorchModelForSpeechSeq2Seq]
        IMAGE_CLASSIFICATION[ExecuTorchModelForImageClassification]
    end
    
    LLAMA --> CAUSAL_LM
    GEMMA --> CAUSAL_LM
    QWEN --> CAUSAL_LM
    PHI --> CAUSAL_LM
    SMOLLM --> CAUSAL_LM
    GPT2 --> CAUSAL_LM
    
    BERT --> MASKED_LM
    ALBERT --> MASKED_LM
    DISTILBERT --> MASKED_LM
    ROBERTA --> MASKED_LM
    EUROBERT --> MASKED_LM
    
    T5 --> SEQ2SEQ_LM
    WHISPER --> SPEECH_SEQ2SEQ
    
    VIT --> IMAGE_CLASSIFICATION
    EFFICIENTNET --> IMAGE_CLASSIFICATION
    SWIN --> IMAGE_CLASSIFICATION
    MOBILEVIT --> IMAGE_CLASSIFICATION
```

Sources: [README.md:141-193](), [tests/models/test_modeling_gemma2.py:1-137]()

## Implementation Framework

The model support in optimum-executorch is implemented through a structured framework that maps HuggingFace model architectures to ExecuTorch-compatible implementations:

```mermaid
graph LR
    subgraph "HuggingFace Models"
        HF_MODEL_ID["model_id<br/>(e.g. 'meta-llama/Llama-3.2-1B')"]
        AUTO_MODEL["AutoModel.from_pretrained()"]
        AUTO_TOKENIZER["AutoTokenizer.from_pretrained()"]
    end
    
    subgraph "Task Registry System"
        TASK_REGISTRY["@register_task decorators"]
        LOAD_CAUSAL_LM["load_causal_lm_model()"]
        LOAD_MASKED_LM["load_masked_lm_model()"]
        LOAD_SEQ2SEQ["load_seq2seq_lm_model()"]
        LOAD_VISION["load_vision_model()"]
        LOAD_SPEECH["load_seq2seq_speech_model()"]
    end
    
    subgraph "ExportableModule Wrappers"
        CAUSAL_WRAPPER["CausalLMExportableModule"]
        MASKED_WRAPPER["MaskedLMExportableModule"]
        SEQ2SEQ_WRAPPER["Seq2SeqLMExportableModule"]
        VISION_WRAPPER["VisionEncoderExportableModule"]
    end
    
    subgraph "ExecuTorch Runtime Models"
        ET_CAUSAL["ExecuTorchModelForCausalLM"]
        ET_MASKED["ExecuTorchModelForMaskedLM"]
        ET_SEQ2SEQ["ExecuTorchModelForSeq2SeqLM"]
        ET_SPEECH["ExecuTorchModelForSpeechSeq2Seq"]
        ET_VISION["ExecuTorchModelForImageClassification"]
    end
    
    subgraph "Model Testing"
        TEST_FILES["test_modeling_*.py"]
        QUALITY_CHECK["check_causal_lm_output_quality()"]
        CLI_EXPORT["optimum-cli export executorch"]
    end
    
    HF_MODEL_ID --> AUTO_MODEL
    HF_MODEL_ID --> AUTO_TOKENIZER
    
    AUTO_MODEL --> LOAD_CAUSAL_LM
    AUTO_MODEL --> LOAD_MASKED_LM
    AUTO_MODEL --> LOAD_SEQ2SEQ
    AUTO_MODEL --> LOAD_VISION
    AUTO_MODEL --> LOAD_SPEECH
    
    LOAD_CAUSAL_LM --> CAUSAL_WRAPPER
    LOAD_MASKED_LM --> MASKED_WRAPPER
    LOAD_SEQ2SEQ --> SEQ2SEQ_WRAPPER
    LOAD_VISION --> VISION_WRAPPER
    
    CAUSAL_WRAPPER --> ET_CAUSAL
    MASKED_WRAPPER --> ET_MASKED
    SEQ2SEQ_WRAPPER --> ET_SEQ2SEQ
    SEQ2SEQ_WRAPPER --> ET_SPEECH
    VISION_WRAPPER --> ET_VISION
    
    ET_CAUSAL --> TEST_FILES
    ET_MASKED --> TEST_FILES
    ET_SEQ2SEQ --> TEST_FILES
    ET_SPEECH --> TEST_FILES
    ET_VISION --> TEST_FILES
    
    TEST_FILES --> QUALITY_CHECK
    TEST_FILES --> CLI_EXPORT
```

Sources: [README.md:141-193](), [tests/models/test_modeling_gemma2.py:31-137]()

## Text Generation Models

### Large Language Models

The library supports major LLM families optimized for causal language modeling tasks:

| Model Family | Example Models | HuggingFace Class | Key Features |
|--------------|----------------|-------------------|--------------|
| **Llama** | `meta-llama/Llama-3.2-1B` | `LlamaForCausalLM` | RoPE, SiLU activation, RMSNorm |
| **Gemma** | `google/gemma-2-2b` | `GemmaForCausalLM` | RoPE, GeGLU, RMSNorm |
| **Qwen** | `Qwen/Qwen2.5-0.5B` | `Qwen2ForCausalLM` | Sliding window attention |
| **Phi** | `microsoft/Phi-4-mini-instruct` | `PhiForCausalLM` | Rotary embeddings |
| **SmolLM** | `HuggingFaceTB/SmolLM2-135M` | `LlamaForCausalLM` | Optimized for mobile deployment |

### Specialized Language Models

Additional specialized models for specific domains:

| Model Family | Example Models | Domain | Special Features |
|--------------|----------------|---------|------------------|
| **CodeGen** | `Salesforce/codegen-350M-mono` | Code Generation | Optimized for programming tasks |
| **StarCoder** | `bigcode/starcoder2-3b` | Code Generation | Multi-language code support |
| **Granite** | `ibm-granite/granite-3.3-2b-instruct` | Enterprise | IBM's enterprise-focused model |
| **OLMo** | `allenai/OLMo-1B-hf` | Research | Open Language Model from Allen AI |

Sources: [README.md:153-173]()

## Masked Language Models

Encoder-only models designed for fill-mask and classification tasks:

| Model Family | Example Models | Architecture | Use Cases |
|--------------|----------------|-------------|-----------|
| **BERT** | `google-bert/bert-base-uncased` | Bidirectional encoder | Text classification, NER |
| **Albert** | `albert/albert-base-v2` | Parameter sharing | Memory-efficient BERT variant |
| **DistilBERT** | `distilbert/distilbert-base-uncased` | Knowledge distillation | Faster inference |
| **RoBERTa** | `FacebookAI/xlm-roberta-base` | Optimized BERT | Multilingual support |
| **EuroBERT** | `EuroBERT/EuroBERT-210m` | European languages | Specialized for EU languages |

Sources: [README.md:147-152]()

## Sequence-to-Sequence Models

Encoder-decoder architectures for conditional generation tasks:

### Text-to-Text Models

| Model Family | Example Models | Architecture | Primary Tasks |
|--------------|----------------|-------------|---------------|
| **T5** | `google-t5/t5-small` | Encoder-decoder transformer | Text summarization, translation |

### Speech-to-Text Models

| Model Family | Example Models | Architecture | Primary Tasks |
|--------------|----------------|-------------|---------------|
| **Whisper** | `openai/whisper-tiny` | Encoder-decoder with audio preprocessing | Speech recognition, translation |

Sources: [README.md:174-191]()

## Vision Models

Computer vision models optimized for image classification and processing:

| Model Family | Example Models | Architecture | Key Features |
|--------------|----------------|-------------|--------------|
| **DeiT** | `facebook/deit-base-distilled-patch16-224` | Vision Transformer | Distilled ViT for efficiency |
| **EfficientNet** | `google/efficientnet-b0` | Convolutional | Scalable CNN architecture |
| **Swin** | `microsoft/swin-tiny-patch4-window7-224` | Hierarchical ViT | Shifted window attention |
| **MobileViT** | `apple/mobilevit-xx-small` | Hybrid CNN-ViT | Mobile-optimized vision |
| **CVT** | `microsoft/cvt-13` | Convolutional ViT | Combines convolution with attention |
| **FocalNet** | `microsoft/focalnet-tiny` | Focal attention | Alternative to self-attention |

Sources: [README.md:177-187]()

## Model Testing Framework

Each supported model is validated through a comprehensive testing framework:

```mermaid
graph TD
    subgraph "Test Discovery"
        SCAN_TESTS["Scan test_modeling_*.py files"]
        EXTRACT_MODELS["Extract model_id from test methods"]
        GENERATE_MATRIX["Generate CI test matrix"]
    end
    
    subgraph "Export Testing"
        CLI_SUBPROCESS["subprocess.run(optimum-cli export)"]
        PTE_VALIDATION["Validate .pte file creation"]
        MEMORY_CLEANUP["Memory cleanup and gc.collect()"]
    end
    
    subgraph "Inference Testing"
        LOAD_MODEL["ExecuTorchModelForXXX.from_pretrained()"]
        TEXT_GENERATION["model.text_generation()"]
        QUALITY_VALIDATION["check_causal_lm_output_quality()"]
    end
    
    subgraph "Performance Testing"
        CUSTOM_SDPA["attn_implementation='custom_sdpa'"]
        QUANTIZATION["qlinear='8da4w', qembedding='8w'"]
        BENCHMARK_RESULTS["Tokens/sec measurements"]
    end
    
    SCAN_TESTS --> EXTRACT_MODELS
    EXTRACT_MODELS --> GENERATE_MATRIX
    GENERATE_MATRIX --> CLI_SUBPROCESS
    
    CLI_SUBPROCESS --> PTE_VALIDATION
    PTE_VALIDATION --> MEMORY_CLEANUP
    MEMORY_CLEANUP --> LOAD_MODEL
    
    LOAD_MODEL --> TEXT_GENERATION
    TEXT_GENERATION --> QUALITY_VALIDATION
    
    LOAD_MODEL --> CUSTOM_SDPA
    LOAD_MODEL --> QUANTIZATION
    CUSTOM_SDPA --> BENCHMARK_RESULTS
    QUANTIZATION --> BENCHMARK_RESULTS
```

Sources: [tests/models/test_modeling_gemma2.py:51-136]()

## Model Performance Benchmarks

The library maintains performance benchmarks across mobile devices for key models:

| Model | Samsung Galaxy S22 5G | iPhone 15 Pro | Key Optimizations |
|-------|:-------------------:|:-------------:|-------------------|
| **SmolLM2-135M** | 202.28 tok/s | 29.64 tok/s | Custom SDPA, 8da4w quantization |
| **Qwen3-0.6B** | 59.16 tok/s | 17.99 tok/s | Custom KV cache, quantization |
| **Gemma-3-1B** | 25.07 tok/s | 17.8 tok/s | XNNPACK backend delegation |
| **Llama-3.2-1B** | 44.91 tok/s | 25.78 tok/s | Batch prefill optimization |
| **OLMo-1B** | 44.98 tok/s | 20.24 tok/s | Custom SDPA implementation |

Sources: [README.md:195-209]()

## Model Registry and Task Mapping

The supported models are organized through a task registry system that maps model architectures to appropriate task implementations. Each model family is tested and validated for specific optimization patterns including custom attention mechanisms, quantization schemes, and backend delegation strategies.

For implementation details of specific model families, see [Large Language Models](#5.1), [Specialized Models](#5.2), and [Vision and Multimodal Models](#5.3).

Sources: [README.md:141-193](), [tests/models/test_modeling_gemma2.py:1-137]()

---

