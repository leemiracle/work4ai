<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/smol2operator · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [assets/google.png](assets/google.png)
- [assets/screenspot-v2.png](assets/screenspot-v2.png)

</details>



## Purpose and Scope

The Smol2Operator system is a comprehensive pipeline for training GUI agents using vision-language models through post-training techniques. This wiki documents the complete system for transforming raw GUI interaction datasets into trained models capable of understanding and interacting with graphical user interfaces.

The system takes raw heterogeneous GUI datasets and applies a two-phase supervised fine-tuning approach to create models that can perceive GUI elements and perform agentic reasoning for computer interaction tasks. For specific implementation details of individual components, see [Data Processing Pipeline](#3), [Training System](#4), and [Utility Systems](#6).

## High-Level System Architecture

The Smol2Operator system follows a pipeline architecture that transforms raw datasets through processing, training, and evaluation stages:

```mermaid
graph TB
    subgraph "Data Sources"
        raw_aguvis["xlangai/aguvis-stage1<br/>xlangai/aguvis-stage2"]
    end
    
    subgraph "Data Processing Pipeline"
        processor["AguvisDatasetProcessor<br/>(aguvis_processor.py)"]
        models["Data Validation<br/>(aguvis_models.py)"]
        converter["Action Conversion<br/>(action_conversion.py)"]
        processed["smolagents/aguvis-stage-1<br/>smolagents/aguvis-stage-2"]
    end
    
    subgraph "Training Pipeline"
        recipe["Training Recipe<br/>(recipe.ipynb)"]
        phase1["Phase 1: Perception<br/>GUI Understanding"]
        phase2["Phase 2: Cognition<br/>Agentic Reasoning"]
        final_model["SmolVLM2-2.2B-Instruct-Agentic-GUI"]
    end
    
    subgraph "Evaluation System"
        eval_prompt["Evaluation Prompts<br/>(eval_prompt.py)"]
        screenspot["ScreenSpot-v2<br/>Benchmark"]
    end
    
    subgraph "Supporting Utilities"
        function_parser["Function Parser<br/>(function_parser.py)"]
        action_converter["Action Space Converter<br/>(action_space_converter.py)"]
        collator["Data Collator<br/>(collator.py)"]
        prompts["System Prompts<br/>(prompts.py)"]
    end
    
    raw_aguvis --> processor
    processor --> models
    models --> converter
    converter --> processed
    processed --> recipe
    recipe --> phase1
    phase1 --> phase2
    phase2 --> final_model
    final_model --> eval_prompt
    eval_prompt --> screenspot
    
    function_parser --> converter
    action_converter --> processed
    collator --> recipe
    prompts --> eval_prompt
```

Sources: [README.md:1-703]()

## Training Performance Results

The system demonstrates significant performance improvements through its two-phase approach:

| Stage | Model | ScreenSpot-v2 Performance | Improvement |
|-------|--------|--------------------------|-------------|
| Baseline | SmolVLM2-2.2B-Instruct | 0.47% | - |
| Phase 1 | After GUI Perception Training | 41.27% | +40.8% |
| Phase 2 | After Agentic Reasoning Training | 61.71% | +20.44% |

## Core Training Methodology

The system implements a progressive two-phase training strategy:

```mermaid
graph LR
    subgraph "Phase 1: Perception Training"
        base_model["SmolVLM2-2.2B-Instruct<br/>0.47% ScreenSpot-v2"]
        stage1_data["aguvis-stage-1<br/>Basic GUI Actions"]
        phase1_model["Phase 1 Model<br/>41.27% ScreenSpot-v2"]
        
        base_model --> stage1_data
        stage1_data --> phase1_model
    end
    
    subgraph "Phase 2: Cognition Training"
        stage2_data["aguvis-stage-2<br/>Agentic Reasoning"]
        final_model["Final Model<br/>61.71% ScreenSpot-v2"]
        
        phase1_model --> stage2_data
        stage2_data --> final_model
    end
```

Sources: [README.md:257-703]()

## Action Space Unification

A critical component of the system is the transformation of heterogeneous action formats into a unified API:

```mermaid
graph TB
    subgraph "Original Action Formats"
        mobile_actions["Mobile Actions<br/>mobile.swipe()<br/>mobile.home()<br/>mobile.long_press()"]
        desktop_actions["Desktop Actions<br/>pyautogui.click()<br/>pyautogui.scroll()<br/>pyautogui.hotkey()"]
    end
    
    subgraph "Action Conversion System"
        function_parser_comp["FunctionCall Parser<br/>(function_parser.py)"]
        action_conversion_comp["Action Converter<br/>(action_conversion.py)"]
    end
    
    subgraph "Unified Action Format"
        unified_actions["Unified Actions<br/>click(x, y)<br/>swipe(from_coord, to_coord)<br/>navigate_home()<br/>press(keys)"]
    end
    
    mobile_actions --> function_parser_comp
    desktop_actions --> function_parser_comp
    function_parser_comp --> action_conversion_comp
    action_conversion_comp --> unified_actions
```

Sources: [README.md:93-255]()

## Key System Components

The system consists of several interconnected modules:

### Data Processing Components
- **AguvisDatasetProcessor**: Main dataset processing orchestrator in [preprocessing/aguvis_processor.py]()
- **Action Conversion System**: Unifies heterogeneous action formats in [preprocessing/action_conversion.py]()
- **Data Models**: Pydantic validation models in [preprocessing/aguvis_models.py]()

### Training Infrastructure
- **Training Recipe**: Complete training pipeline in [recipe.ipynb]()
- **Data Collation**: VLM-specific data preparation in [utils/collator.py]()
- **TRL Integration**: Uses TRL library's `SFTTrainer` for supervised fine-tuning

### Evaluation System
- **ScreenSpot-v2 Evaluation**: Benchmark prompts in [eval/eval_prompt.py]()
- **Action Definitions**: System prompts and actions in [utils/prompts.py]()

### Utility Systems
- **Function Call Parser**: Extracts and reconstructs function calls in [utils/function_parser.py]()
- **Action Space Converter**: Adapts actions to custom vocabularies in [utils/action_space_converter.py]()

Sources: [README.md:674-684]()

## Dataset Transformation Pipeline

The system transforms raw AGUVIS datasets through a comprehensive processing pipeline:

```mermaid
graph TD
    subgraph "Input Processing"
        raw_json["Raw AGUVIS JSON<br/>Heterogeneous Actions"]
        validation["ConversationDataList<br/>Validation & Deduplication"]
    end
    
    subgraph "Action Processing"
        function_extraction["Function Call Extraction<br/>(FunctionCall objects)"]
        action_unification["Action Unification<br/>(Unified API format)"]
    end
    
    subgraph "Output Generation"
        data_rows["DataRow Objects<br/>(Images + Texts + Metadata)"]
        hf_datasets["HuggingFace Datasets<br/>(smolagents repositories)"]
    end
    
    raw_json --> validation
    validation --> function_extraction
    function_extraction --> action_unification
    action_unification --> data_rows
    data_rows --> hf_datasets
```

Sources: [README.md:93-255](), [preprocessing/aguvis_processor.py](), [preprocessing/action_conversion.py]()

## Technical Architecture Highlights

1. **Normalized Coordinates**: Uses 0-1 normalized coordinates instead of pixel coordinates for resolution independence
2. **Progressive Training**: Two-phase approach builds perception capabilities before adding agentic reasoning
3. **Modular Design**: Clear separation between data processing, training, evaluation, and utilities
4. **Open Source**: All components, datasets, and models are publicly available
5. **Reproducible**: Complete training recipes and data processing tools enable full reproducibility

The system demonstrates how careful data curation and progressive training can transform a base vision-language model with no GUI capabilities into an effective GUI agent through supervised fine-tuning alone.

Sources: [README.md:1-703]()

---

