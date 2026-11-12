<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/optimum-habana · page 4 Advanced Features · fetched 2026-10-26 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [conftest.py](conftest.py)
- [examples/image-to-text/run_image2text_lora_finetune.py](examples/image-to-text/run_image2text_lora_finetune.py)
- [examples/language-modeling/run_lora_clm.py](examples/language-modeling/run_lora_clm.py)
- [optimum/habana/quantizers/bitsandbytes.py](optimum/habana/quantizers/bitsandbytes.py)
- [tests/baselines/fixture/tests/test_bnb_inference.json](tests/baselines/fixture/tests/test_bnb_inference.json)
- [tests/baselines/fixture/tests/test_bnb_qlora.json](tests/baselines/fixture/tests/test_bnb_qlora.json)
- [tests/test_bnb_inference.py](tests/test_bnb_inference.py)
- [tests/test_bnb_qlora.py](tests/test_bnb_qlora.py)
- [tests/test_custom_file_input.py](tests/test_custom_file_input.py)
- [tests/test_examples.py](tests/test_examples.py)
- [tests/utils.py](tests/utils.py)

</details>



This document covers specialized functionality in optimum-habana for advanced users, including quantization techniques, parameter-efficient fine-tuning (PEFT), distributed training strategies, and comprehensive testing frameworks. These features enable sophisticated model optimization and deployment scenarios on Intel Habana Gaudi processors.

For basic training and inference workflows, see [Core Systems](#2). For specific application examples, see [Applications and Examples](#3).

## Quantization Support

Optimum-habana provides comprehensive quantization support through integration with the BitsAndBytes library, enabling efficient model compression while maintaining performance on Gaudi devices.

### BitsAndBytes Integration

The library supports NF4 (Normal Float 4-bit) quantization through a custom HPU-compatible implementation:

```mermaid
graph TB
    subgraph "Quantization Stack"
        BNB_CONFIG["BitsAndBytesConfig"]
        GAUDI_VALIDATOR["gaudi_validate_environment"]
        QUANTIZED_PARAM["gaudi_create_quantized_param"]
        HPU_BACKEND["HPU Backend Validation"]
    end
    
    subgraph "Model Loading"
        AUTO_MODEL["AutoModelForCausalLM"]
        DEVICE_MAP["device_map={'': 'hpu'}"]
        TORCH_DTYPE["torch_dtype=torch.bfloat16"]
    end
    
    subgraph "Training Integration"
        PEFT_MODEL["get_peft_model"]
        GAUDI_TRAINER["GaudiTrainer"]
        LORA_CONFIG["LoraConfig"]
    end
    
    BNB_CONFIG --> GAUDI_VALIDATOR
    GAUDI_VALIDATOR --> HPU_BACKEND
    BNB_CONFIG --> AUTO_MODEL
    AUTO_MODEL --> DEVICE_MAP
    AUTO_MODEL --> TORCH_DTYPE
    AUTO_MODEL --> PEFT_MODEL
    PEFT_MODEL --> LORA_CONFIG
    PEFT_MODEL --> GAUDI_TRAINER
    QUANTIZED_PARAM --> AUTO_MODEL
```

**Sources:** [tests/test_bnb_qlora.py:68-78](), [tests/test_bnb_inference.py:29-41](), [optimum/habana/quantizers/bitsandbytes.py:26-58]()

### Quantization Configuration

The quantization system supports multiple precision formats and backend validation:

| Feature | Implementation | Purpose |
|---------|----------------|---------|
| NF4 Quantization | `bnb_4bit_quant_type="nf4"` | 4-bit normal float quantization |
| Compute Dtype | `bnb_4bit_compute_dtype=torch.bfloat16` | Computation precision control |
| HPU Device Mapping | `device_map={"": "hpu"}` | Direct HPU placement |
| Backend Validation | `gaudi_validate_bnb_backend_availability` | HPU compatibility checking |

**Sources:** [tests/test_bnb_qlora.py:68-78](), [optimum/habana/quantizers/bitsandbytes.py:72-127]()

## Parameter-Efficient Fine-Tuning (PEFT)

Optimum-habana supports multiple PEFT techniques for efficient model adaptation with minimal parameter updates.

### PEFT Method Support

```mermaid
graph LR
    subgraph "PEFT Methods"
        LORA["LoRA"]
        ADALORA["AdaLoRA"]
        IA3["IA3"]
        LLAMA_ADAPTER["LLama-Adapter"]
        VERA["VERA"]
        LN_TUNING["LN-Tuning"]
    end
    
    subgraph "Configuration"
        PEFT_CONFIG["PeftConfig"]
        TARGET_MODULES["target_modules"]
        RANK_PARAMS["rank/alpha parameters"]
        DROPOUT_PARAMS["dropout parameters"]
    end
    
    subgraph "Model Integration"
        BASE_MODEL["Base Model"]
        PEFT_MODEL["get_peft_model"]
        GAUDI_TRAINER["GaudiTrainer"]
    end
    
    LORA --> PEFT_CONFIG
    ADALORA --> PEFT_CONFIG
    IA3 --> PEFT_CONFIG
    LLAMA_ADAPTER --> PEFT_CONFIG
    VERA --> PEFT_CONFIG
    LN_TUNING --> PEFT_CONFIG
    
    PEFT_CONFIG --> TARGET_MODULES
    PEFT_CONFIG --> RANK_PARAMS
    PEFT_CONFIG --> DROPOUT_PARAMS
    
    BASE_MODEL --> PEFT_MODEL
    PEFT_CONFIG --> PEFT_MODEL
    PEFT_MODEL --> GAUDI_TRAINER
```

**Sources:** [examples/language-modeling/run_lora_clm.py:33-43](), [examples/language-modeling/run_lora_clm.py:362-393]()

### LoRA Implementation

The LoRA (Low-Rank Adaptation) implementation provides comprehensive parameter control:

```python
# Configuration from FinetuneArguments
lora_rank: int = 8                    # Rank parameter
lora_alpha: int = 16                  # Alpha scaling parameter  
lora_dropout: float = 0.05            # Dropout rate
lora_target_modules: List[str]        # Target module specification
```

**Sources:** [examples/language-modeling/run_lora_clm.py:316-331]()

### Advanced PEFT Features

The system supports sophisticated PEFT configurations:

| Method | Key Parameters | Use Case |
|--------|----------------|----------|
| AdaLoRA | `init_r`, `target_r`, `tinit`, `tfinal` | Dynamic rank adaptation |
| IA3 | `target_modules`, `feedforward_modules` | Infused adapter by inhibiting and amplifying |
| LLama-Adapter | `adapter_layers`, `adapter_len` | Prompt-based adaptation |
| VERA | `vera_target_modules` | Vector-based rare-expert adaptation |

**Sources:** [examples/language-modeling/run_lora_clm.py:336-393]()

### Multimodal PEFT

For vision-language models, specialized PEFT implementations handle multimodal architectures:

```mermaid
graph TB
    subgraph "Vision-Language Models"
        IDEFICS2["idefics2"]
        MLLAMA["mllama"] 
        LLAVA["llava"]
    end
    
    subgraph "PEFT Configuration"
        FIND_LINEAR["find_all_linear_names"]
        MULTIMODAL_FILTER["multimodal_keywords filter"]
        TARGET_MODULES["target_modules"]
    end
    
    subgraph "Data Processing"
        CUSTOM_COLLATOR["MyDataCollator/LLavaDataCollator"]
        CHAT_TEMPLATE["apply_chat_template"]
        IMAGE_PROCESSING["Image preprocessing"]
    end
    
    IDEFICS2 --> FIND_LINEAR
    MLLAMA --> FIND_LINEAR
    LLAVA --> FIND_LINEAR
    
    FIND_LINEAR --> MULTIMODAL_FILTER
    MULTIMODAL_FILTER --> TARGET_MODULES
    TARGET_MODULES --> CUSTOM_COLLATOR
    
    CUSTOM_COLLATOR --> CHAT_TEMPLATE
    CUSTOM_COLLATOR --> IMAGE_PROCESSING
```

**Sources:** [examples/image-to-text/run_image2text_lora_finetune.py:416-430](), [examples/image-to-text/run_image2text_lora_finetune.py:253-350]()

## Distributed Training

Optimum-habana provides comprehensive distributed training support through multiple parallelization strategies.

### Distribution Strategies

```mermaid
graph TB
    subgraph "Distribution Methods"
        SINGLE_CARD["Single Card"]
        MULTI_CARD["Multi-Card"]
        DEEPSPEED["DeepSpeed"]
        FSDP["FSDP"]
    end
    
    subgraph "Launch Mechanisms"
        GAUDI_SPAWN["gaudi_spawn.py"]
        DEEPSPEED_LAUNCHER["deepspeed launcher"]
        MPI_SUPPORT["MPI support"]
    end
    
    subgraph "Configuration"
        WORLD_SIZE["--world_size 8"]
        NUM_GPUS["--num_gpus 8"]
        USE_MPI["--use_mpi"]
        NO_LOCAL_RANK["--no_local_rank"]
    end
    
    MULTI_CARD --> GAUDI_SPAWN
    DEEPSPEED --> DEEPSPEED_LAUNCHER
    GAUDI_SPAWN --> WORLD_SIZE
    GAUDI_SPAWN --> USE_MPI
    DEEPSPEED_LAUNCHER --> NUM_GPUS
    DEEPSPEED_LAUNCHER --> NO_LOCAL_RANK
    MPI_SUPPORT --> GAUDI_SPAWN
```

**Sources:** [tests/test_examples.py:665-675](), [tests/test_examples.py:484-487]()

### Environment Configuration

Distributed training requires specific environment variable management:

| Variable | Purpose | Models |
|----------|---------|---------|
| `PT_HPU_AUTOCAST_LOWER_PRECISION_OPS_LIST` | BF16 operations control | Falcon, LLama |
| `PT_HPU_MAX_COMPOUND_OP_SIZE` | Compound operation sizing | Flan-T5 |
| `DEEPSPEED_HPU_ZERO3_SYNC_MARK_STEP_REQUIRED` | ZeRO-3 synchronization | Bloom, Qwen2-72B |
| `PT_HPU_LAZY_MODE` | Execution mode control | FSDP configurations |

**Sources:** [tests/test_examples.py:490-508]()

## Testing and Validation Framework

The advanced testing framework provides comprehensive validation across different hardware configurations and model types.

### Test Generation System

```mermaid
graph LR
    subgraph "Test Metaclass System"
        EXAMPLE_TEST_META["ExampleTestMeta"]
        SCRIPT_MODEL_MAPPING["_SCRIPT_TO_MODEL_MAPPING"]
        CREATE_TEST["_create_test"]
    end
    
    subgraph "Test Configuration"
        DEVICE_CONTEXT["OH_DEVICE_CONTEXT"]
        BASELINE_SYSTEM["Baseline"]
        CONFIG_DIRECTORY["CONFIG_DIRECTORY"]
    end
    
    subgraph "Test Execution"
        COMMAND_GENERATION["_create_command_line"]
        SUBPROCESS_EXECUTION["subprocess.Popen"]
        PERFORMANCE_VALIDATION["assert_no_regression"]
    end
    
    EXAMPLE_TEST_META --> SCRIPT_MODEL_MAPPING
    SCRIPT_MODEL_MAPPING --> CREATE_TEST
    CREATE_TEST --> COMMAND_GENERATION
    DEVICE_CONTEXT --> BASELINE_SYSTEM
    BASELINE_SYSTEM --> CONFIG_DIRECTORY
    COMMAND_GENERATION --> SUBPROCESS_EXECUTION
    SUBPROCESS_EXECUTION --> PERFORMANCE_VALIDATION
```

**Sources:** [tests/test_examples.py:217-223](), [tests/test_examples.py:103-214](), [tests/test_examples.py:644-724]()

### Baseline Management

The baseline system tracks performance metrics across different device contexts:

```mermaid
graph TB
    subgraph "Baseline System"
        BASELINE_CLASS["Baseline"]
        BASELINE_REQUEST["BaselineRequest"]
        REFERENCE_STORAGE["references dictionary"]
    end
    
    subgraph "Metrics Tracking"
        REGRESSION_METRICS["REGRESSION_METRICS"]
        ACCURACY_FACTOR["ACCURACY_PERF_FACTOR = 0.99"]
        TIME_FACTOR["TIME_PERF_FACTOR = 1.05"]
    end
    
    subgraph "Validation"
        ASSERT_REF["assertRef"]
        COMPARE_FUNCTION["compare function"]
        CONTEXT_ARRAY["context array"]
    end
    
    BASELINE_CLASS --> REFERENCE_STORAGE
    BASELINE_REQUEST --> ASSERT_REF
    REGRESSION_METRICS --> ACCURACY_FACTOR
    REGRESSION_METRICS --> TIME_FACTOR
    ASSERT_REF --> COMPARE_FUNCTION
    ASSERT_REF --> CONTEXT_ARRAY
```

**Sources:** [conftest.py:27-58](), [conftest.py:60-78](), [tests/test_examples.py:625-634]()

### Device-Specific Testing

The testing framework adapts test execution based on device capabilities:

| Device Context | Supported Features | Excluded Tests |
|----------------|-------------------|----------------|
| `gaudi1` | Basic training, inference | FSDP, FP8, Advanced PEFT methods |
| `gaudi2` | All features | None |
| `gaudi3` | All features + FP8 | None |

The `to_test` method in `ExampleTestMeta` implements device-specific logic:

**Sources:** [tests/test_examples.py:224-340](), [tests/test_examples.py:264-270]()

### Performance Regression Testing

The framework validates multiple performance dimensions:

```python
REGRESSION_METRICS = {
    "eval_f1": (operator.ge, ACCURACY_PERF_FACTOR),
    "eval_accuracy": (operator.ge, ACCURACY_PERF_FACTOR), 
    "perplexity": (operator.le, 2 - ACCURACY_PERF_FACTOR),
    "train_runtime": (operator.le, TIME_PERF_FACTOR),
    "train_samples_per_second": (operator.ge, 2 - TIME_PERF_FACTOR),
    "eval_samples_per_second": (operator.ge, 2 - TIME_PERF_FACTOR),
}
```

**Sources:** [tests/test_examples.py:625-634](), [tests/test_examples.py:738-788]()

## Advanced Configuration

### Custom Arguments and Environment

The system provides specialized training arguments and environment management for advanced scenarios:

```mermaid
graph LR
    subgraph "Training Arguments"
        GAUDI_TRAINING_ARGS["GaudiTrainingArguments"]
        MODEL_ARGS["ModelArguments"]
        DATA_ARGS["DataArguments"]
        FINETUNE_ARGS["FinetuneArguments"]
    end
    
    subgraph "Model Configuration"
        FLASH_ATTENTION["flash_attention_*"]
        FUSED_ROPE["use_fused_rope"]
        ATTENTION_SOFTMAX["attn_softmax_bf16"]
        LOW_CPU_MEM["low_cpu_mem_usage"]
    end
    
    subgraph "Environment Variables"
        LAZY_MODE["PT_HPU_LAZY_MODE"]
        AUTOCAST_LIST["PT_HPU_AUTOCAST_LOWER_PRECISION_OPS_LIST"]
        COMPOUND_OP["PT_HPU_MAX_COMPOUND_OP_SIZE"]
    end
    
    GAUDI_TRAINING_ARGS --> MODEL_ARGS
    MODEL_ARGS --> FLASH_ATTENTION
    MODEL_ARGS --> FUSED_ROPE
    MODEL_ARGS --> ATTENTION_SOFTMAX
    MODEL_ARGS --> LOW_CPU_MEM
    
    FLASH_ATTENTION --> LAZY_MODE
    FUSED_ROPE --> AUTOCAST_LIST
    ATTENTION_SOFTMAX --> COMPOUND_OP
```

**Sources:** [examples/language-modeling/run_lora_clm.py:76-194](), [examples/language-modeling/run_lora_clm.py:708-721]()

### Custom Dataset Processing

Advanced dataset processing supports multiple prompt formats and concatenation strategies:

| Feature | Implementation | Purpose |
|---------|----------------|---------|
| SQL Prompts | `create_sql_prompts` | Text-to-SQL training |
| Chat Prompts | `create_chat_prompts` | Conversational fine-tuning | 
| Dataset Concatenation | `dataset_concatenation` | Efficient sequence packing |
| Custom File Input | JSON/JSONL/TXT support | Flexible data ingestion |

**Sources:** [examples/language-modeling/run_lora_clm.py:395-458](), [tests/test_custom_file_input.py:19-119]()

---

