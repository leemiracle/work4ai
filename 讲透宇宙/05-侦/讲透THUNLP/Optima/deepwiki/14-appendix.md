<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/Optima · page 14 Appendix · fetched 2026-11-02 -->

# Appendix

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [alignment-handbook/LICENSE](alignment-handbook/LICENSE)

</details>



This section provides supplementary reference materials, licensing information, and acknowledgments for the Optima project. It covers project dependencies, directory structure reference, license details, and credits to the open-source projects that Optima builds upon.

For the Apache License 2.0 full text and usage terms, see [License](#14.1). For acknowledgments and credits to key dependencies, see [Acknowledgments](#14.2).

---

## Project Dependencies

Optima integrates with several key open-source projects to provide its training and inference capabilities. The system has a modular dependency structure with clear separation between training and inference environments.

### Dependency Architecture

```mermaid
graph TB
    subgraph "Optima Core"
        OptimaScripts["Optima Scripts<br/>sft_script.py<br/>dpo_script.py<br/>inference_script.py"]
        AgentClasses["Agent Classes<br/>BaseAgent<br/>Agent<br/>VllmAgent"]
    end
    
    subgraph "Training Dependencies"
        AlignmentHandbook["alignment-handbook<br/>Custom fork with Mask collator"]
        Transformers["transformers<br/>Model loading and training"]
        TRL["trl<br/>RLHF utilities"]
        Datasets["datasets<br/>HuggingFace datasets"]
        Accelerate["accelerate<br/>Distributed training"]
        PEFT["peft<br/>Parameter-efficient fine-tuning"]
    end
    
    subgraph "Inference Dependencies"
        VLLM["vllm==0.5.3<br/>Model serving"]
        OpenAI["openai<br/>Client library"]
        FastAPI["fastapi/uvicorn<br/>HTTP server"]
    end
    
    subgraph "Common Dependencies"
        PyTorch["torch<br/>Deep learning framework"]
        FlashAttn["flash-attn<br/>Optimized attention"]
        NumPy["numpy/pandas<br/>Data manipulation"]
    end
    
    OptimaScripts --> AlignmentHandbook
    OptimaScripts --> VLLM
    AgentClasses --> VLLM
    AgentClasses --> OpenAI
    
    AlignmentHandbook --> Transformers
    AlignmentHandbook --> TRL
    AlignmentHandbook --> Datasets
    AlignmentHandbook --> Accelerate
    AlignmentHandbook --> PEFT
    
    VLLM --> FastAPI
    
    AlignmentHandbook --> PyTorch
    VLLM --> PyTorch
    
    Transformers --> FlashAttn
    PyTorch --> NumPy
```

**Sources:** [alignment-handbook/LICENSE:1-202]()

### Key Dependencies Table

| Dependency | Version | Environment | Purpose |
|------------|---------|-------------|---------|
| `vllm` | 0.5.3 | optima-vllm | High-performance model serving with PagedAttention |
| `alignment-handbook` | Custom fork | optima-train | Training framework with custom Mask collator |
| `transformers` | Latest | optima-train | Model loading, tokenization, and training |
| `torch` | Latest | Both | Core deep learning framework |
| `openai` | Latest | optima-vllm | HTTP client for vLLM API communication |
| `flash-attn` | Latest | optima-train | Flash Attention 2 for memory-efficient training |
| `accelerate` | Latest | optima-train | Multi-GPU distributed training |
| `trl` | Latest | optima-train | Trainer classes for RLHF methods |
| `peft` | Latest | optima-train | LoRA and other efficient fine-tuning methods |
| `datasets` | Latest | optima-train | Dataset loading and preprocessing |

**Sources:** Environment setup files referenced in system architecture

---

## Directory Structure Reference

The Optima repository follows a modular organization with clear separation between code, configuration, data, and outputs.

### Root Directory Layout

```mermaid
graph TB
    subgraph "Optima Repository Root"
        ScriptsDir["Scripts<br/>*.py training and inference"]
        RecipesDir["recipes/<br/>YAML configurations"]
        AlignmentDir["alignment-handbook/<br/>Custom fork"]
        DatasetsDir["my_datasets/<br/>Training data"]
        CheckpointsDir["checkpoints/<br/>Model iterations"]
        ResultsDir["results/<br/>Evaluation outputs"]
        InferenceResultsDir["inference_results/<br/>Inference outputs"]
        EnvironmentDir["Environment files<br/>environment_train.yaml<br/>environment_vllm.yaml"]
    end
    
    ScriptsDir -->|"Reads configs from"| RecipesDir
    ScriptsDir -->|"Uses utilities from"| AlignmentDir
    ScriptsDir -->|"Loads data from"| DatasetsDir
    ScriptsDir -->|"Saves models to"| CheckpointsDir
    ScriptsDir -->|"Writes results to"| ResultsDir
    ScriptsDir -->|"Writes inference to"| InferenceResultsDir
```

### File Path Reference

| Path | Type | Purpose |
|------|------|---------|
| `sft_script.py` | Script | Supervised fine-tuning main script |
| `dpo_script.py` | Script | Direct preference optimization script |
| `sft_dpo_script.py` | Script | Combined SFT+DPO training script |
| `inference_script.py` | Script | Batch inference and evaluation |
| `multi_sc_data_generate_script.py` | Script | Multi-agent self-consistency data generation |
| `recipes/arc_sft/` | Directory | ARC dataset SFT configurations |
| `recipes/arc_dpo/` | Directory | ARC dataset DPO configurations |
| `recipes/cbt_sft/` | Directory | CBT dataset SFT configurations |
| `recipes/cbt_dpo/` | Directory | CBT dataset DPO configurations |
| `alignment-handbook/src/alignment/` | Directory | Training utilities and data collators |
| `alignment-handbook/src/alignment/data.py` | Module | Mask data collator implementation |
| `my_datasets/arc/` | Directory | ARC-Challenge dataset files |
| `my_datasets/hotpot_qa/` | Directory | HotpotQA dataset files |
| `my_datasets/cbt/` | Directory | Children's Book Test dataset |
| `checkpoints/iteration_0/` | Directory | Iteration 0 model checkpoints |
| `checkpoints/iteration_1/` | Directory | Iteration 1 model checkpoints |
| `inference_results/` | Directory | Inference output JSON files |
| `results/` | Directory | Evaluation metrics and analysis |

**Sources:** Project structure as referenced throughout documentation

---

## Code Entity Reference Map

This diagram maps high-level system concepts to their concrete implementations in the codebase.

### Training System Entity Map

```mermaid
graph LR
    subgraph "Concept Layer"
        C1["Iterative SFT"]
        C2["Iterative DPO"]
        C3["Completion-only Masking"]
        C4["Recipe Configuration"]
        C5["Multi-Agent Data Gen"]
    end
    
    subgraph "Implementation Layer"
        I1["sft_script.py<br/>main function"]
        I2["dpo_script.py<br/>main function"]
        I3["alignment/data.py<br/>Mask class"]
        I4["recipes/*.yaml<br/>YAML files"]
        I5["multi_sc_data_generate_script.py<br/>VllmAgent instances"]
    end
    
    subgraph "Class/Function Layer"
        F1["SFTTrainer<br/>from trl"]
        F2["DPOTrainer<br/>from trl"]
        F3["DataCollatorForCompletionOnlyLM<br/>Mask inherits"]
        F4["H4ArgumentParser<br/>parse_yaml_file"]
        F5["VllmAgent.chat<br/>generate_response"]
    end
    
    C1 --> I1
    C2 --> I2
    C3 --> I3
    C4 --> I4
    C5 --> I5
    
    I1 --> F1
    I2 --> F2
    I3 --> F3
    I4 --> F4
    I5 --> F5
```

### Inference System Entity Map

```mermaid
graph LR
    subgraph "Concept Layer"
        C1["Batch Inference"]
        C2["Agent Communication"]
        C3["vLLM Model Serving"]
        C4["Conversation Memory"]
    end
    
    subgraph "Implementation Layer"
        I1["inference_script.py<br/>batch_inference"]
        I2["VllmAgent<br/>class definition"]
        I3["vllm server<br/>--host --port --model"]
        I4["llmMessage<br/>list storage"]
    end
    
    subgraph "Method/Function Layer"
        F1["agent.chat<br/>agent.alice_chat"]
        F2["requests.post<br/>HTTP communication"]
        F3["completions.create<br/>OpenAI client API"]
        F4["append_message<br/>history.append"]
    end
    
    C1 --> I1
    C2 --> I2
    C3 --> I3
    C4 --> I4
    
    I1 --> F1
    I2 --> F2
    I3 --> F3
    I4 --> F4
```

**Sources:** Code structure as referenced in system architecture and implementation files

---

## Environment Configuration

Optima requires two separate conda environments for training and inference operations.

### Environment Comparison

| Feature | optima-vllm | optima-train |
|---------|-------------|--------------|
| **Primary Purpose** | Model serving and inference | Model training and optimization |
| **Python Version** | 3.10+ | 3.10+ |
| **Key Package** | vllm==0.5.3 | alignment-handbook |
| **GPU Requirements** | 1+ GPUs for serving | 2+ GPUs recommended |
| **Port Usage** | 8000-8007 (vLLM servers) | N/A |
| **Memory Profile** | High VRAM for model weights | High for training activations |
| **Configuration File** | `environment_vllm.yaml` | `environment_train.yaml` |

### Environment Installation Commands

```bash
# optima-vllm environment
conda env create -f environment_vllm.yaml
conda activate optima-vllm
pip install vllm==0.5.3

# optima-train environment
conda env create -f environment_train.yaml
conda activate optima-train
cd alignment-handbook && pip install -e .
```

**Sources:** Environment setup files and installation procedures from system architecture

---

## Common Configuration Patterns

### Recipe File Structure

All recipe YAML files follow a consistent structure with these top-level keys:

| Key | Type | Purpose |
|-----|------|---------|
| `model_name_or_path` | String | Path to base model or checkpoint |
| `tokenizer_name_or_path` | String | Path to tokenizer (usually same as model) |
| `dataset_mixer` | Dict | Dataset paths and sampling weights |
| `output_dir` | String | Directory for saving checkpoints |
| `num_train_epochs` | Integer | Number of training epochs |
| `per_device_train_batch_size` | Integer | Batch size per GPU |
| `gradient_accumulation_steps` | Integer | Steps to accumulate gradients |
| `learning_rate` | Float | Optimizer learning rate |
| `lr_scheduler_type` | String | Learning rate schedule (e.g., "cosine") |
| `warmup_ratio` | Float | Fraction of steps for warmup |
| `torch_dtype` | String | Precision (typically "bfloat16") |
| `use_flash_attention_2` | Boolean | Enable Flash Attention optimization |

### Port Management Scheme

When running multiple vLLM instances:

```
Port 8000: Model A (e.g., iteration_0)
Port 8001: Model B (e.g., iteration_1)
Port 8002: Model C (e.g., iteration_2)
...
Port 8007: Maximum recommended concurrent instances
```

**Sources:** Recipe configurations and vLLM deployment patterns from training system

---

## License Summary

Optima is distributed under the **Apache License 2.0**, which provides:

- ✅ Commercial use permitted
- ✅ Modification permitted
- ✅ Distribution permitted
- ✅ Patent use granted
- ✅ Private use permitted

**Requirements:**
- Include license and copyright notice
- State changes made to the code
- Include NOTICE file if provided

**Limitations:**
- No trademark use without permission
- No warranty provided
- No liability assumed by contributors

For the complete license text, see [License](#14.1).

**Sources:** [alignment-handbook/LICENSE:1-202]()

---

## Contributing and Development

For information on contributing to Optima:
- Project structure and organization: see [Project Structure](#12.1)
- Code quality standards: see [Code Quality and Testing](#12.2)
- Contribution guidelines: see [Contributing Guidelines](#12.3)

For development setup:
- Environment installation: see [Installation and Environment Setup](#2.1)
- Running tests and quality checks: see [Code Quality and Testing](#12.2)

---

## Additional Resources

### Related Documentation Pages

- **Overview and introduction**: [Overview](#1)
- **Quick start guide**: [Quick Start Tutorial](#2.2)
- **Complete CLI reference**: [Command-Line Interface Reference](#13.1)
- **API documentation**: [API Reference](#13.2)
- **Key terminology**: [Glossary](#13.4)

### External Resources

- Optima repository: `https://github.com/thunlp/Optima`
- alignment-handbook: Integrated as a custom fork with Mask collator
- vLLM documentation: For model serving details
- Hugging Face transformers: For model and tokenizer APIs

**Sources:** Repository structure and external dependencies

---

