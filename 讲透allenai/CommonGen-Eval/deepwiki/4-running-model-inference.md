<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/CommonGen-Eval · page 4 Running Model Inference · fetched 2026-10-26 -->

# Running Model Inference

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [data_utils.py](data_utils.py)
- [instruct_template.md](instruct_template.md)
- [scripts/Pallas-0.5.sh](scripts/Pallas-0.5.sh)

</details>



This page describes how to run model inference to generate sentences from concept sets using the CommonGen-lite dataset. It covers the command-line interface, configuration options, and the overall inference pipeline that produces model outputs for later evaluation.

For details about the data loading and formatting functions, see [Data Utilities](#4.1). For information about conversation templates for different models, see [Conversation Templates](#4.2). For running evaluation on generated outputs, see [Running Evaluation](#5).

## Purpose and Scope

The model inference system takes concept sets from the CommonGen-lite dataset and generates natural language sentences using various large language models (LLMs). The system supports 50+ model architectures through model-specific conversation templates and uses vLLM for efficient batch inference.

**Sources:** [README.md:55-69]()

## Inference Pipeline Overview

The inference process follows a structured pipeline from data loading through model output generation:

```mermaid
flowchart TD
    subgraph "Input Stage"
        DS["CommonGen-lite Dataset<br/>allenai/commongen_lite"]
        IT["instruct_template.md<br/>2-shot prompt template"]
    end
    
    subgraph "Data Loading"
        LDE["load_eval_data()<br/>data_utils.py"]
        CH["chat_history list<br/>raw instructions"]
        META["metadata dict<br/>id, concept_set"]
    end
    
    subgraph "Template Application"
        AT["apply_template()<br/>data_utils.py"]
        GCT["get_conv_template()<br/>fastchat_conversation.py"]
        MI["model_inputs list<br/>formatted prompts"]
    end
    
    subgraph "Model Inference"
        VLLM["vllm_infer.py<br/>LLM class from vllm"]
        BATCH["Batch processing<br/>batch_size=8"]
        GEN["generate() method<br/>temp=0, top_p=1"]
    end
    
    subgraph "Output Stage"
        CO["clear_output()<br/>post-processing"]
        SO["save_outputs()<br/>JSON serialization"]
        OUT["model_outputs/*.json<br/>400 examples"]
    end
    
    DS --> LDE
    IT --> LDE
    LDE --> CH
    LDE --> META
    CH --> AT
    AT --> GCT
    GCT --> MI
    MI --> VLLM
    VLLM --> BATCH
    BATCH --> GEN
    GEN --> CO
    CO --> SO
    META --> SO
    SO --> OUT
```

**Sources:** [data_utils.py:34-57](), [data_utils.py:6-32](), [README.md:55-96]()

## Command-Line Interface

The primary entry point for model inference is `vllm_infer.py`, which is invoked through shell scripts with model-specific parameters.

### Basic Command Structure

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 \
python vllm_infer.py \
    --data_name "commongen" \
    --model_name 01-ai/Yi-34b-chat \
    --tensor_parallel_size 4 \
    --dtype bfloat16 \
    --output_folder "model_outputs/" \
    --top_p 1 \
    --temperature 0 \
    --batch_size 8 \
    --max_tokens 128
```

### Key Command-Line Arguments

| Argument | Purpose | Example Values |
|----------|---------|----------------|
| `--data_name` | Dataset identifier | `"commongen"` |
| `--model_name` | HuggingFace model path or name | `"01-ai/Yi-34b-chat"`, `"meta-llama/Llama-2-7b-chat-hf"` |
| `--tensor_parallel_size` | Number of GPUs for model parallelism | `1`, `2`, `4` |
| `--dtype` | Model precision format | `"bfloat16"`, `"float16"` |
| `--output_folder` | Directory for output JSON files | `"model_outputs/"` |
| `--top_p` | Nucleus sampling parameter | `1` |
| `--temperature` | Sampling temperature (0=greedy) | `0` |
| `--batch_size` | Number of examples per batch | `8` |
| `--max_tokens` | Maximum tokens per generation | `128` |
| `--download_dir` | Optional model cache directory | `"/path/to/cache/"` |

**Sources:** [README.md:62-69](), [scripts/Pallas-0.5.sh:1-7]()

## Model-Specific Shell Scripts

Each evaluated model has a corresponding shell script in the `scripts/` directory that configures model-specific parameters:

```mermaid
flowchart LR
    subgraph "Shell Scripts Directory"
        S1["scripts/Yi-34b-chat.sh<br/>tensor_parallel=4"]
        S2["scripts/Llama-2-7b-chat-hf.sh<br/>tensor_parallel=1"]
        S3["scripts/Pallas-0.5.sh<br/>tensor_parallel=4"]
        S4["scripts/Mixtral-8x7B-Instruct.sh<br/>tensor_parallel=4"]
    end
    
    subgraph "vllm_infer.py"
        VI["vllm_infer.py<br/>Main inference script"]
    end
    
    subgraph "Output Files"
        O1["Yi-34b-chat.json"]
        O2["Llama-2-7b-chat-hf.json"]
        O3["Pallas-0.5.json"]
        O4["Mixtral-8x7B-Instruct-v0.1.json"]
    end
    
    S1 --> VI
    S2 --> VI
    S3 --> VI
    S4 --> VI
    
    VI --> O1
    VI --> O2
    VI --> O3
    VI --> O4
```

**Example script structure** (Pallas-0.5):

```bash
CUDA_VISIBLE_DEVICES=0,1,2,3 \
python vllm_infer.py \
    --download_dir /net/nfs/s2-research/llama2/ \
    --data_name "commongen" \
    --model_name Mihaiii/Pallas-0.5 \
    --tensor_parallel_size 4 \
    --dtype bfloat16 \
    --output_folder "model_outputs/" \
    --top_p 1 --temperature 0 --batch_size 8 --max_tokens 128
```

**Sources:** [scripts/Pallas-0.5.sh:1-7]()

## Data Loading and Formatting

The inference system loads data through `load_eval_data()` in `data_utils.py`, which performs the following transformations:

```mermaid
flowchart TD
    subgraph "load_eval_data() Function"
        direction TB
        LD["load_dataset()<br/>datasets library"]
        DS["CommonGen-lite split=train<br/>400 examples"]
        
        LOOP["for item in dataset:<br/>extract instruction"]
        
        META["Build metadata dict:<br/>id, concept_set"]
        CH["Build chat_history:<br/>list of instructions"]
        
        AT["apply_template()<br/>model_name based routing"]
        
        RET["Return:<br/>id_strs, chat_history,<br/>model_inputs, metadata"]
    end
    
    LD --> DS
    DS --> LOOP
    LOOP --> META
    LOOP --> CH
    CH --> AT
    META --> RET
    AT --> RET
```

The `apply_template()` function routes to the appropriate conversation template based on model name pattern matching:

| Model Pattern | Template Name | Matching Logic |
|---------------|---------------|----------------|
| `"tulu"` | `"tulu"` | `if "tulu" in model_name.lower()` |
| `"zephyr"` | `"zephyr"` | `if "zephyr" in model_name.lower()` |
| `"llama-2"` | `"llama-2"` | `if "llama-2" in model_name.lower()` |
| `"mixtral"` or `"mistral"` | `"mistral"` | `if "mixtral" or "mistral" in model_name.lower()` |
| `"yi"` + `"chat"` | `"Yi-34b-chat"` | `if "yi" and "chat" in model_name.lower()` |
| `"vicuna"` | `"vicuna_v1.1"` | `if "vicuna" in model_name.lower()` |
| `"pallas"` | `"vicuna_v1.1"` | `if "pallas" in model_name.lower()` |
| `"gpt-"` | No template (direct use) | `if "gpt-" in model_name.lower()` |

**Sources:** [data_utils.py:34-57](), [data_utils.py:6-32]()

## Instruction Template

All models receive the same task instruction formatted using `instruct_template.md`, which provides a 2-shot prompt:

### Template Structure

```markdown
# Instruction

Given several concepts (i.e., nouns or verbs), write a short and simple sentence 
that contains *all* the required words. The sentence should describe a common 
scene in daily life, and the concepts should be used in a natural way.

# Examples

## Example 1
- Concepts: "dog(noun), frisbee(noun), catch(verb), throw(verb)"
- Sentence: The dog catches the frisbee when the boy throws it into the air.

## Example 2
- Concepts: "apple(noun), place(verb), tree(noun), pick(verb)"
- Sentence: A girl picks some apples from a tree and places them into her basket.

# Your Task 

- Concepts: "{$concept_list}"
- Sentence: 
```

The `{$concept_list}` placeholder is replaced with the actual concepts for each example, formatted by `concept_list_str()` which converts tags like `_N` to `(noun)` and `_V` to `(verb)`.

**Sources:** [instruct_template.md:1-19](), [data_utils.py:90-94]()

## Output Format and Storage

Model outputs are saved to `model_outputs/{model_name}.json` through the `save_outputs()` function:

```mermaid
flowchart LR
    subgraph "Raw Outputs"
        RO["outputs list<br/>from vLLM generate()"]
    end
    
    subgraph "save_outputs() Processing"
        direction TB
        LOOP["for ind in range(len(outputs))"]
        BUILD["Build output_item dict:<br/>instruction, output, generator"]
        CLEAR["clear_output()<br/>post-process text"]
        ADD["Add metadata:<br/>id, concept_set"]
    end
    
    subgraph "JSON Structure"
        direction TB
        ITEM1["Item 0:<br/>{instruction, output,<br/>generator, id, concept_set}"]
        ITEM2["Item 1:<br/>{instruction, output,<br/>generator, id, concept_set}"]
        ITEM3["..."]
        ITEM400["Item 399:<br/>{instruction, output,<br/>generator, id, concept_set}"]
    end
    
    subgraph "File Output"
        JSON["model_outputs/<br/>model_name.json"]
    end
    
    RO --> LOOP
    LOOP --> BUILD
    BUILD --> CLEAR
    CLEAR --> ADD
    ADD --> ITEM1
    ADD --> ITEM2
    ADD --> ITEM3
    ADD --> ITEM400
    
    ITEM1 --> JSON
    ITEM2 --> JSON
    ITEM3 --> JSON
    ITEM400 --> JSON
```

### Output JSON Schema

Each output file contains a JSON array of objects with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `instruction` | string | The full prompt sent to the model |
| `output` | string or list | Generated sentence(s) from the model |
| `generator` | string | The model name that generated the output |
| `id` | string | Unique identifier for the example |
| `concept_set` | list | Array of concept strings with POS tags (e.g., `["dog_N", "catch_V"]`) |

**Sources:** [data_utils.py:72-88]()

## Post-Processing

The `clear_output()` function applies model-specific post-processing to clean up generated text:

```python
# Llama-2-7b specific cleaning
if "llama-2-7b" in model_name.lower():
    if "\n\n" in output:
        output = output[output.index("\n\n"):].strip()
```

This function handles model-specific artifacts and formatting issues. Additional post-processing can be added for new models as needed.

**Sources:** [data_utils.py:62-69]()

## Adding a New Model

To add inference support for a new model:

1. **Create a shell script** in `scripts/{model_name}.sh` with appropriate parameters:
   ```bash
   CUDA_VISIBLE_DEVICES=0 \
   python vllm_infer.py \
       --data_name "commongen" \
       --model_name your/model-name \
       --tensor_parallel_size 1 \
       --dtype bfloat16 \
       --output_folder "model_outputs/" \
       --top_p 1 --temperature 0 --batch_size 8 --max_tokens 128
   ```

2. **Add template routing** in `apply_template()` if the model requires a specific conversation format (see [Conversation Templates](#4.2))

3. **Add post-processing** in `clear_output()` if the model produces artifacts that need cleaning

4. **Run inference** using the shell script:
   ```bash
   bash scripts/{model_name}.sh
   ```

5. **Verify output** in `model_outputs/{model_name}.json`

**Sources:** [data_utils.py:6-32](), [data_utils.py:62-69](), [scripts/Pallas-0.5.sh:1-7]()

## Inference Parameters

The system uses conservative inference parameters to ensure deterministic, high-quality outputs:

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| `temperature` | `0` | Greedy decoding for deterministic outputs |
| `top_p` | `1` | No nucleus sampling (greedy mode) |
| `max_tokens` | `128` | Sufficient for single sentences (avg ~15 words) |
| `batch_size` | `8` | Balances throughput and memory usage |

These parameters ensure that model outputs are reproducible and comparable across different runs.

**Sources:** [README.md:68](), [scripts/Pallas-0.5.sh:7]()

---

