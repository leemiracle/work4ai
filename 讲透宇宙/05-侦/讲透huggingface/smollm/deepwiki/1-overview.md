<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/smollm · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [text/README.md](text/README.md)
- [text/finetuning/README.md](text/finetuning/README.md)
- [vision/README.md](vision/README.md)

</details>



This document provides a comprehensive overview of the SmolLM repository, a collection of efficient and lightweight AI models from Hugging Face. The repository contains the complete ecosystem for training, evaluating, and deploying small language models including SmolLM3 (3B parameters), SmolLM2 family (135M, 360M, 1.7B parameters), and SmolVLM (vision-language model).

For specific training procedures, see [SmolLM3 Pretraining](#2.2), [SmolLM3 Post-training](#2.3), and [SmolLM2 Fine-tuning](#3.2). For data curation details, see [Data and Datasets](#5). For deployment instructions, see [Tools and Deployment](#6).

## Model Family

The SmolLM ecosystem consists of three main model families designed for different use cases:

| Model Family | Parameters | Primary Use Case | Key Features |
|--------------|------------|------------------|--------------|
| SmolLM3 | 3B | High-performance assistant | Dual-mode reasoning, 128K context, multilingual |
| SmolLM2 | 135M, 360M, 1.7B | On-device applications | Lightweight, efficient inference |
| SmolVLM | 2B (1.7B language + vision) | Multimodal understanding | Image+text processing, video analysis |

**SmolLM3** represents the latest generation with advanced capabilities including dual-mode reasoning through `/think` and `/no_think` system prompts, support for 6 languages (English, French, Spanish, German, Italian, Portuguese), and extended context length up to 128K tokens using NoPE (No Position Embedding) and YaRN scaling.

**SmolLM2** provides a family of compact models optimized for on-device deployment, with the 1.7B variant serving as the language backbone for SmolVLM.

**SmolVLM** combines SmolLM2-1.7B with vision processing capabilities to handle arbitrary sequences of image and text inputs for multimodal tasks.

Sources: [README.md:1-118](), [text/README.md:15-40](), [vision/README.md:4-6]()

## Repository Structure

```mermaid
graph TB
    subgraph repo["smollm/"]
        subgraph text_dir["text/"]
            pretraining["pretraining/<br/>nanotron configs"]
            finetuning["finetuning/<br/>TRL + PEFT scripts"]
            evaluation["evaluation/<br/>LightEval framework"]
            data["data/<br/>FineMath, FineWeb-Edu<br/>SmolTalk pipelines"]
        end
        
        subgraph vision_dir["vision/"]
            m4["m4/<br/>M4 trainer"]
            experiments["experiments/<br/>Training configs"]
            vlm_finetuning["finetuning/<br/>SmolVLM fine-tuning"]
        end
        
        subgraph tools_dir["tools/"]
            smol_tools["smol_tools/<br/>AI-powered CLI tools"]
            smollm_inference["smollm_local_inference/<br/>Local inference scripts"]
            smolvlm_inference["smolvlm_local_inference/<br/>VLM inference + video"]
        end
    end
    
    subgraph external["External Frameworks"]
        nanotron["nanotron<br/>Distributed pretraining"]
        alignment_hb["Alignment Handbook<br/>Post-training"]
        trl["TRL<br/>Fine-tuning"]
        lighteval["LightEval<br/>Evaluation"]
    end
    
    pretraining -.-> nanotron
    finetuning -.-> trl
    finetuning -.-> alignment_hb
    evaluation -.-> lighteval
    m4 -.-> nanotron
```

The repository follows a modular structure with three main directories: `text/` contains all SmolLM3 and SmolLM2 related components, `vision/` houses SmolVLM training and evaluation code, and `tools/` provides inference and deployment utilities.

Sources: [README.md:30-39](), [text/README.md:130-142](), [vision/README.md:8-9]()

## Model Architecture and Training Pipeline

```mermaid
graph TD
    subgraph data_sources["Data Sources"]
        fineweb_edu["FineWeb-Edu<br/>Educational content"]
        finemath["FineMath<br/>Mathematical reasoning"]
        stack["The Stack v2<br/>Code data"]
        smoltalk["SmolTalk<br/>Instruction tuning"]
    end
    
    subgraph smollm3_pipeline["SmolLM3 Training Pipeline"]
        smollm3_pretrain["SmolLM3 Pretraining<br/>nanotron + 11T tokens"]
        smollm3_midtrain["Mid-training<br/>Domain adaptation"]
        smollm3_sft["SFT<br/>Instruction following"]
        smollm3_dpo["DPO<br/>Preference optimization"]
    end
    
    subgraph smollm2_pipeline["SmolLM2 Training Pipeline"]
        smollm2_pretrain["SmolLM2 Pretraining<br/>nanotron"]
        smollm2_sft["SmolLM2 Fine-tuning<br/>TRL + PEFT + LoRA"]
    end
    
    subgraph smolvlm_pipeline["SmolVLM Training Pipeline"]
        vision_data["Vision-Language Data"]
        smolvlm_train["SmolVLM Training<br/>M4 trainer"]
    end
    
    subgraph models["Trained Models"]
        smollm3_base["SmolLM3-3B-Base"]
        smollm3_instruct["SmolLM3-3B"]
        smollm2_models["SmolLM2-135M/360M/1.7B"]
        smolvlm_model["SmolVLM-Instruct"]
    end
    
    fineweb_edu --> smollm3_pretrain
    finemath --> smollm3_pretrain
    stack --> smollm3_pretrain
    
    smollm3_pretrain --> smollm3_base
    smollm3_pretrain --> smollm3_midtrain
    smollm3_midtrain --> smollm3_sft
    smollm3_sft --> smollm3_dpo
    smollm3_dpo --> smollm3_instruct
    
    fineweb_edu --> smollm2_pretrain
    smoltalk --> smollm2_sft
    smollm2_pretrain --> smollm2_sft
    smollm2_sft --> smollm2_models
    
    vision_data --> smolvlm_train
    smollm2_models --> smolvlm_train
    smolvlm_train --> smolvlm_model
    
    style smollm3_base fill:#e1f5fe
    style smollm3_instruct fill:#e1f5fe
    style smollm2_models fill:#f3e5f5
    style smolvlm_model fill:#e8f5e8
```

The training pipeline utilizes different frameworks for different stages: `nanotron` for distributed pretraining, `Alignment Handbook` for SmolLM3 post-training, `TRL` with `PEFT` for SmolLM2 fine-tuning, and `M4` for SmolVLM vision-language training.

Sources: [text/README.md:130-134](), [text/finetuning/README.md:3-10](), [vision/README.md:92-104]()

## Data Processing and Evaluation Framework

```mermaid
graph TB
    subgraph datasets["Key Datasets"]
        fineweb_edu_ds["HuggingFaceFW/fineweb-edu<br/>Educational web content"]
        finemath_ds["HuggingFaceTB/finemath<br/>Mathematical reasoning"]
        smoltalk_ds["HuggingFaceTB/smoltalk<br/>Instruction conversations"]
        magpie_ultra["MagPie Ultra v1.0<br/>Multi-turn dialogues"]
    end
    
    subgraph processing["Data Processing Pipeline"]
        resiliparse["Resiliparse<br/>Text extraction"]
        datatrove["datatrove<br/>Data pipeline framework"]
        decontamination["Decontamination<br/>13-gram overlap removal"]
        distilabel["distilabel<br/>SmolTalk generation"]
    end
    
    subgraph evaluation["Evaluation Framework"]
        lighteval_framework["LightEval<br/>Evaluation framework"]
        custom_tasks["Custom Tasks<br/>ARC, MMLU, GSM8K, HumanEval"]
        judge_models["Judge Models<br/>Flow-Judge for MixEval"]
        benchmarks["Benchmark Suites<br/>Base vs Instruct evaluation"]
    end
    
    subgraph models_eval["Model Evaluation"]
        smollm3_eval["SmolLM3 Evaluation<br/>Mathematical reasoning<br/>Dual-mode assessment"]
        smollm2_eval["SmolLM2 Evaluation<br/>Standard benchmarks"]
        smolvlm_eval["SmolVLM Evaluation<br/>Multimodal tasks"]
    end
    
    fineweb_edu_ds --> processing
    finemath_ds --> processing
    processing --> smoltalk_ds
    distilabel --> magpie_ultra
    
    lighteval_framework --> custom_tasks
    custom_tasks --> judge_models
    judge_models --> benchmarks
    
    benchmarks --> smollm3_eval
    benchmarks --> smollm2_eval
    benchmarks --> smolvlm_eval
```

The evaluation system is built around `LightEval` framework with custom task definitions for domain-specific benchmarks. SmolLM3 evaluation includes specialized assessment of dual-mode reasoning capabilities through both `/think` and `/no_think` modes.

Sources: [text/README.md:136-142](), [text/finetuning/README.md:1-11]()

## Inference and Deployment Ecosystem

```mermaid
graph TB
    subgraph models_deployed["Deployed Models"]
        smollm3_hf["HuggingFaceTB/SmolLM3-3B"]
        smollm2_hf["HuggingFaceTB/SmolLM2-1.7B-Instruct"]
        smolvlm_hf["HuggingFaceTB/SmolVLM-Instruct"]
    end
    
    subgraph inference_frameworks["Inference Frameworks"]
        transformers["transformers<br/>AutoModelForCausalLM<br/>AutoModelForVision2Seq"]
        llamacpp["llama.cpp<br/>Quantized inference"]
        mlx["MLX<br/>Apple Silicon optimization"]
        mlc["MLC<br/>Mobile deployment"]
        transformersjs["transformers.js<br/>Browser inference"]
        trl_chat["TRL CLI<br/>trl chat command"]
    end
    
    subgraph local_tools["Local Tools"]
        smol_tools_cli["smol-tools<br/>AI-powered CLI utilities"]
        smollm_local["smollm_local_inference/<br/>Local inference scripts"]
        smolvlm_local["smolvlm_local_inference/<br/>Video processing pipeline"]
        mlx_vlm["mlx-vlm<br/>Fast VLM inference"]
    end
    
    subgraph features["Key Features"]
        dual_mode["Dual-mode reasoning<br/>/think /no_think prompts<br/>enable_thinking kwarg"]
        long_context["Long context support<br/>Up to 128K tokens<br/>YaRN scaling"]
        multimodal["Multimodal processing<br/>Image + text input<br/>Video frame extraction"]
    end
    
    smollm3_hf --> transformers
    smollm3_hf --> llamacpp
    smollm3_hf --> mlx
    smollm3_hf --> mlc
    smollm3_hf --> transformersjs
    
    smollm2_hf --> transformers
    smollm2_hf --> trl_chat
    smollm2_hf --> smol_tools_cli
    
    smolvlm_hf --> transformers
    smolvlm_hf --> mlx_vlm
    smolvlm_hf --> smolvlm_local
    
    transformers --> dual_mode
    transformers --> long_context
    transformers --> multimodal
```

The deployment ecosystem supports multiple inference frameworks. SmolLM3 supports dual-mode reasoning through system prompts or the `enable_thinking` parameter in `apply_chat_template()`. SmolVLM includes specialized video processing capabilities with frame extraction pipelines.

Sources: [README.md:44-93](), [text/README.md:46-129](), [vision/README.md:22-91]()

## Code Integration Points

The repository integrates with several external frameworks through specific configuration files and scripts:

**Training Integration:**
- `nanotron` configs in [text/pretraining/](text/pretraining) for distributed pretraining
- `Alignment Handbook` recipes for SmolLM3 post-training stages
- `TRL` and `PEFT` integration in [text/finetuning/train.py](text/finetuning/train.py)
- `M4` trainer configuration in [vision/m4/](vision/m4)

**Model Loading:**
- `AutoModelForCausalLM` for text models [README.md:52-54]()
- `AutoModelForVision2Seq` for SmolVLM [vision/README.md:40-44]()
- `AutoTokenizer` and `AutoProcessor` for input processing

**Evaluation Framework:**
- `LightEval` framework integration in [text/evaluation/](text/evaluation)
- Custom task definitions for domain-specific benchmarks
- Judge model integration for preference evaluation

**Local Deployment:**
- CLI tools in [tools/smol_tools/](tools/smol_tools) using `llama.cpp` backend
- Inference scripts supporting multiple frameworks in [tools/smollm_local_inference/](tools/smollm_local_inference)
- Video processing pipeline in [tools/smolvlm_local_inference/SmolVLM_video_inference.py](tools/smolvlm_local_inference/SmolVLM_video_inference.py)

Sources: [text/README.md:130-142](), [text/finetuning/README.md:36-55](), [vision/README.md:78-91]()

---

