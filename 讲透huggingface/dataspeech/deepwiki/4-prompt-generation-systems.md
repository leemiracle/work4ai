<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/dataspeech · page 4 Prompt Generation Systems · fetched 2026-10-26 -->

# Prompt Generation Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/prompt_creation/run_prompt_creation_dummy.sh](examples/prompt_creation/run_prompt_creation_dummy.sh)
- [examples/prompt_creation_llm_swarm/nginx.template.conf](examples/prompt_creation_llm_swarm/nginx.template.conf)
- [examples/prompt_creation_llm_swarm/run_prompt_creation_10k.sh](examples/prompt_creation_llm_swarm/run_prompt_creation_10k.sh)
- [scripts/run_prompt_creation.py](scripts/run_prompt_creation.py)
- [scripts/run_prompt_creation_llm_swarm.py](scripts/run_prompt_creation_llm_swarm.py)

</details>



This document covers the prompt generation systems that convert text bins (categorical audio feature descriptions) into natural language descriptions of speech characteristics. These systems represent the final stage of the dataspeech pipeline, transforming structured metadata like "slightly slowly" and "very monotone" into fluent descriptions such as "In a very expressive voice, Jenny speaks quite slowly with some background noise and echo."

For information about the preceding text binning stage, see [Metadata to Text Binning](#2.2). For details about the overall processing pipeline, see [Core Processing Pipeline](#2).

## Architecture Overview

The prompt generation system provides two distinct backends for large language model inference, each optimized for different deployment scenarios and scale requirements.

```mermaid
graph TB
    subgraph "Input Data"
        TAGGED_DS["Tagged Dataset<br/>with Text Bins"]
    end
    
    subgraph "Prompt Template System"
        PROMPT_TEMPLATES["Prompt Templates<br/>PROMPT<br/>NEW_PROMPT<br/>NEW_PROMPT_WITH_ACCENT<br/>SINGLE_SPEAKER_PROMPT<br/>NEW_SINGLE_SPEAKER_PROMPT"]
    end
    
    subgraph "Backend Selection"
        ACCEL_BACKEND["run_prompt_creation.py<br/>Accelerate Backend"]
        SWARM_BACKEND["run_prompt_creation_llm_swarm.py<br/>LLM Swarm Backend"]
    end
    
    subgraph "Model Infrastructure"
        subgraph "Accelerate Path"
            ACCEL_LIB["Accelerator"]
            LOCAL_MODEL["AutoModelForCausalLM<br/>Local Model Loading"]
            GPU_DIST["Multi-GPU Distribution"]
        end
        
        subgraph "Swarm Path"
            LLM_SWARM["LLMSwarm"]
            TGI_INSTANCES["TGI Inference Instances"]
            NGINX_LB["nginx Load Balancer"]
        end
    end
    
    subgraph "Processing Features"
        CHECKPOINTS["Checkpoint System<br/>save_checkpoint()<br/>load_checkpoint()"]
        DATA_COLLATOR["DataCollatorWithPadding"]
        ASYNC_PROC["AsyncInferenceClient"]
    end
    
    subgraph "Output"
        DESCRIPTIONS["text_description Column<br/>Natural Language Descriptions"]
        HUB_UPLOAD["HuggingFace Hub Upload"]
    end
    
    TAGGED_DS --> ACCEL_BACKEND
    TAGGED_DS --> SWARM_BACKEND
    
    PROMPT_TEMPLATES --> ACCEL_BACKEND
    PROMPT_TEMPLATES --> SWARM_BACKEND
    
    ACCEL_BACKEND --> ACCEL_LIB
    ACCEL_LIB --> LOCAL_MODEL
    LOCAL_MODEL --> GPU_DIST
    
    SWARM_BACKEND --> LLM_SWARM
    LLM_SWARM --> TGI_INSTANCES
    TGI_INSTANCES --> NGINX_LB
    
    CHECKPOINTS --> ACCEL_BACKEND
    CHECKPOINTS --> SWARM_BACKEND
    DATA_COLLATOR --> ACCEL_BACKEND
    ASYNC_PROC --> SWARM_BACKEND
    
    GPU_DIST --> DESCRIPTIONS
    NGINX_LB --> DESCRIPTIONS
    
    DESCRIPTIONS --> HUB_UPLOAD
    
    style ACCEL_BACKEND fill:#e8f5e8
    style SWARM_BACKEND fill:#fff3e0
    style DESCRIPTIONS fill:#f3e5f5
```

**Sources:** [scripts/run_prompt_creation.py:1-668](), [scripts/run_prompt_creation_llm_swarm.py:1-553]()

## Backend Comparison

The two prompt generation backends serve different deployment scenarios with distinct trade-offs in complexity, scalability, and resource requirements.

| Feature | Accelerate Backend | LLM Swarm Backend |
|---------|-------------------|-------------------|
| **Implementation** | `run_prompt_creation.py` | `run_prompt_creation_llm_swarm.py` |
| **Model Loading** | Local via `AutoModelForCausalLM` | Remote via TGI instances |
| **Distribution** | Accelerate library | LLM Swarm + nginx |
| **Processing** | Synchronous batching | Asynchronous requests |
| **Memory Model** | Direct GPU memory | Distributed inference |
| **Quantization** | BitsAndBytesConfig support | TGI-managed |
| **Checkpointing** | Per-batch with rotation | Per-chunk streaming |
| **Complexity** | Higher setup, simpler scaling | Lower setup, complex infrastructure |

**Sources:** [scripts/run_prompt_creation.py:31-108](), [scripts/run_prompt_creation_llm_swarm.py:27-91]()

## Prompt Template System

Both backends utilize a unified prompt template system that adapts to different speaker configurations and audio feature sets. The template selection logic determines the appropriate prompt based on dataset characteristics.

```mermaid
graph TB
    subgraph "Template Selection Logic"
        INPUT_SAMPLE["Input Sample<br/>prepare_dataset()"]
        
        SINGLE_CHECK{"is_single_speaker?"}
        SPEAKER_MAP_CHECK{"speaker_ids_to_name<br/>mapping exists?"}
        ACCENT_CHECK{"accent_column_name<br/>present?"}
        NEW_PROMPT_CHECK{"is_new_speaker_prompt?"}
        
        INPUT_SAMPLE --> SINGLE_CHECK
        SINGLE_CHECK -->|Yes| SINGLE_TEMPLATES
        SINGLE_CHECK -->|No| SPEAKER_MAP_CHECK
        
        SPEAKER_MAP_CHECK -->|Yes| SINGLE_TEMPLATES
        SPEAKER_MAP_CHECK -->|No| ACCENT_CHECK
        
        ACCENT_CHECK -->|Yes| NEW_PROMPT_CHECK
        ACCENT_CHECK -->|No| STANDARD_TEMPLATES
        
        NEW_PROMPT_CHECK -->|Yes| ACCENT_TEMPLATES
        NEW_PROMPT_CHECK -->|No| STANDARD_TEMPLATES
    end
    
    subgraph "Template Types"
        SINGLE_TEMPLATES["Single Speaker Templates<br/>SINGLE_SPEAKER_PROMPT<br/>NEW_SINGLE_SPEAKER_PROMPT"]
        
        ACCENT_TEMPLATES["Accent Templates<br/>NEW_PROMPT_WITH_ACCENT"]
        
        STANDARD_TEMPLATES["Standard Templates<br/>PROMPT<br/>NEW_PROMPT"]
    end
    
    subgraph "Template Processing"
        PLACEHOLDER_REPLACE["Placeholder Replacement<br/>sample_prompt.replace()"]
        CHAT_TEMPLATE["Chat Template Application<br/>tokenizer.apply_chat_template()"]
    end
    
    SINGLE_TEMPLATES --> PLACEHOLDER_REPLACE
    ACCENT_TEMPLATES --> PLACEHOLDER_REPLACE
    STANDARD_TEMPLATES --> PLACEHOLDER_REPLACE
    
    PLACEHOLDER_REPLACE --> CHAT_TEMPLATE
    
    style SINGLE_TEMPLATES fill:#e8f5e8
    style ACCENT_TEMPLATES fill:#fff3e0
    style STANDARD_TEMPLATES fill:#f3e5f5
```

**Sources:** [scripts/run_prompt_creation.py:552-573](), [scripts/run_prompt_creation_llm_swarm.py:408-427]()

### Template Variants

The system provides five core prompt templates, each optimized for specific dataset configurations:

**Legacy Templates:**
- `PROMPT`: Original 6-keyword template with traditional terminology [scripts/run_prompt_creation.py:320-330]()
- `SINGLE_SPEAKER_PROMPT`: 4-keyword version for mono-speaker datasets [scripts/run_prompt_creation.py:400-412]()

**Modern Templates:**
- `NEW_PROMPT`: Updated 6-keyword template with revised terminology [scripts/run_prompt_creation.py:332-353]()
- `NEW_PROMPT_WITH_ACCENT`: 7-keyword version including accent information [scripts/run_prompt_creation.py:355-377]()
- `NEW_SINGLE_SPEAKER_PROMPT`: Updated single-speaker template [scripts/run_prompt_creation.py:380-398]()

### Expected Columns

The prompt system validates input datasets against expected column sets that vary based on configuration:

```python
EXPECTED_COLUMNS = {"gender", "pitch", "noise", "reverberation", "speech_monotony", "speaking_rate"}

# Single speaker datasets exclude gender and pitch
if data_args.is_single_speaker:
    EXPECTED_COLUMNS = {"noise", "reverberation", "speech_monotony", "speaking_rate"}
    
# New prompt format uses sdr_noise instead of noise
if data_args.is_new_speaker_prompt:
    EXPECTED_COLUMNS.remove("noise")
    EXPECTED_COLUMNS.add("sdr_noise")
```

**Sources:** [scripts/run_prompt_creation.py:480-487](), [scripts/run_prompt_creation_llm_swarm.py:365-371]()

## Model Loading and Configuration

### Accelerate Backend Model Setup

The Accelerate backend provides comprehensive model configuration options including quantization, compilation, and distributed loading:

```mermaid
graph TB
    subgraph "Model Configuration"
        MODEL_ARGS["ModelArguments<br/>torch_dtype<br/>attn_implementation<br/>quantization options"]
        
        QUANT_CONFIG["get_quantization_config()<br/>BitsAndBytesConfig"]
        
        DEVICE_MAP["get_kbit_device_map()<br/>GPU device mapping"]
    end
    
    subgraph "Model Loading Pipeline"
        AUTO_MODEL["AutoModelForCausalLM.from_pretrained()"]
        TORCH_COMPILE_CHECK{"torch_compile enabled?"}
        STATIC_CACHE["Static k/v cache<br/>generation_config.cache_implementation"]
        COMPILED_MODEL["torch.compile(model)"]
        
        AUTO_MODEL --> TORCH_COMPILE_CHECK
        TORCH_COMPILE_CHECK -->|Yes| STATIC_CACHE
        STATIC_CACHE --> COMPILED_MODEL
        TORCH_COMPILE_CHECK -->|No| TOKENIZER_SETUP
        COMPILED_MODEL --> TOKENIZER_SETUP
    end
    
    subgraph "Tokenizer Configuration"
        TOKENIZER_SETUP["AutoTokenizer.from_pretrained()<br/>padding_side='left'"]
        PAD_TOKEN_CONFIG["pad_token_id = bos_token_id"]
    end
    
    MODEL_ARGS --> QUANT_CONFIG
    QUANT_CONFIG --> DEVICE_MAP
    DEVICE_MAP --> AUTO_MODEL
    
    TOKENIZER_SETUP --> PAD_TOKEN_CONFIG
    
    style AUTO_MODEL fill:#e8f5e8
    style COMPILED_MODEL fill:#fff3e0
```

**Sources:** [scripts/run_prompt_creation.py:199-545]()

### LLM Swarm Infrastructure Setup

The LLM Swarm backend orchestrates distributed inference through TGI instances and load balancing:

```python
with LLMSwarm(
    LLMSwarmConfig(
        instances=model_args.num_instances,
        inference_engine="tgi",
        slurm_template_path="./tgi_h100.template.slurm",
        load_balancer_template_path="./nginx.template.conf",
        model=model_args.model_name_or_path,
        per_instance_max_parallel_requests=model_args.per_instance_max_parallel_requests,
    )
) as llm_swarm:
```

**Sources:** [scripts/run_prompt_creation_llm_swarm.py:389-400](), [examples/prompt_creation_llm_swarm/nginx.template.conf:1-29]()

## Generation and Processing

### Accelerate Backend Processing

The Accelerate backend uses synchronous batch processing with DataLoader integration:

```mermaid
graph TB
    subgraph "Data Preparation"
        VECTORIZED_DS["vectorized_datasets<br/>with input_ids"]
        DATA_COLLATOR["DataCollatorWithPadding"]
        DATALOADER["DataLoader<br/>batch processing"]
    end
    
    subgraph "Generation Loop"
        GENERATE_STEP["generate_step()<br/>model.generate()"]
        PAD_ACROSS["accelerator.pad_across_processes()"]
        GATHER_METRICS["accelerator.gather_for_metrics()"]
    end
    
    subgraph "Checkpointing"
        SAVE_CHECKPOINT["save_checkpoint()<br/>every save_steps"]
        ROTATE_CHECKPOINTS["rotate_checkpoints()<br/>cleanup old checkpoints"]
    end
    
    subgraph "Postprocessing"
        POSTPROCESS["postprocess_dataset()<br/>tokenizer.batch_decode()"]
        TEXT_DESCRIPTION["text_description column<br/>extracted from generated_ids"]
    end
    
    VECTORIZED_DS --> DATA_COLLATOR
    DATA_COLLATOR --> DATALOADER
    DATALOADER --> GENERATE_STEP
    
    GENERATE_STEP --> PAD_ACROSS
    PAD_ACROSS --> GATHER_METRICS
    GATHER_METRICS --> SAVE_CHECKPOINT
    
    SAVE_CHECKPOINT --> ROTATE_CHECKPOINTS
    GATHER_METRICS --> POSTPROCESS
    POSTPROCESS --> TEXT_DESCRIPTION
    
    style GENERATE_STEP fill:#e8f5e8
    style POSTPROCESS fill:#f3e5f5
```

**Sources:** [scripts/run_prompt_creation.py:584-653]()

### LLM Swarm Async Processing

The LLM Swarm backend uses asynchronous processing with semaphore-controlled concurrency:

```python
async def process_text(sample):
    # Template selection and prompt preparation
    sample_prompt = tokenizer.apply_chat_template(sample_prompt, tokenize=False)
    
    attempt = 0
    while attempt < model_args.max_retries:
        try:
            async with semaphore:
                return await client.text_generation(
                    prompt=sample_prompt,
                    max_new_tokens=model_args.max_new_tokens,
                    temperature=model_args.temperature,
                    do_sample=model_args.do_sample,
                )
        except Exception as e:
            # Retry logic with exponential backoff
```

**Sources:** [scripts/run_prompt_creation_llm_swarm.py:408-448]()

## Checkpoint and Resume System

Both backends implement robust checkpointing to handle long-running generation tasks and enable resume functionality after interruptions.

### Checkpoint File Format

Checkpoints are stored as JSON files with numeric step identifiers:
- Filename pattern: `checkpoint-{step}.json`
- Content: List of generated text strings (Swarm) or token ID arrays (Accelerate)
- Regex pattern: `^checkpoint-(\d+).json$`

### Checkpoint Management Functions

| Function | Purpose | Backend |
|----------|---------|---------|
| `save_checkpoint()` | Save current progress | Both |
| `load_checkpoint()` | Restore from checkpoint | Both |
| `get_last_checkpoint()` | Find most recent checkpoint | Both |
| `rotate_checkpoints()` | Cleanup old checkpoints | Both |
| `sorted_checkpoints()` | Order checkpoints by step | Both |

**Sources:** [scripts/run_prompt_creation.py:235-302](), [scripts/run_prompt_creation_llm_swarm.py:190-250]()

## Usage Examples

### Accelerate Backend Example

```bash
python run_prompt_creation.py \
  --dataset_name "ylacombe/libritts_r_tags_and_text" \
  --dataset_config_name "clean" \
  --model_name_or_path "mistralai/Mistral-7B-Instruct-v0.2" \
  --per_device_eval_batch_size 8 \
  --output_dir "./descriptions" \
  --push_to_hub \
  --hub_dataset_id "user/dataset-descriptions"
```

### LLM Swarm Backend Example

```bash
python run_prompt_creation_llm_swarm.py \
  --dataset_name "ylacombe/mls-eng-10k-text-tags-v2" \
  --model_name_or_path "mistralai/Mistral-7B-Instruct-v0.2" \
  --num_instances 4 \
  --per_instance_max_parallel_requests 100 \
  --output_dir "./descriptions"
```

**Sources:** [examples/prompt_creation/run_prompt_creation_dummy.sh:1-18](), [examples/prompt_creation_llm_swarm/run_prompt_creation_10k.sh:1-10]()

---

