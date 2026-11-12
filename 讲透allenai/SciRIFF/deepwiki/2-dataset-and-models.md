<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/SciRIFF · page 2 Dataset and Models · fetched 2026-10-26 -->

# Dataset and Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This document describes the core SciRIFF dataset collection and the SciTulu model family. The SciRIFF dataset consists of 54 scientific tasks converted to instruction-following format, while SciTulu models are fine-tuned language models trained on this data. For information about evaluation procedures, see [Evaluation System](#3). For details on data processing workflows, see [Data Processing Pipeline](#4). For model training procedures, see [Model Training](#5).

## SciRIFF Dataset Collection

The SciRIFF dataset collection provides scientific instruction-following data in two primary configurations hosted on Hugging Face. The collection transforms existing scientific datasets into a unified instruction-following format using expert-written templates.

### Dataset Structure

**Full SciRIFF Dataset**
The complete `allenai/SciRIFF` dataset contains all 54 scientific tasks across multiple domain areas. Each task maintains separate train/validation/test splits where available from the source datasets.

**Training Mixture**
The `allenai/SciRIFF-train-mix` dataset provides the specific training configuration used for SciTulu models, combining 1000 instances per scientific task with matching data from the Tulu-V2 instruction dataset.

### Task Categories and Distribution

The 54 tasks span multiple scientific domains and task types:

| Domain | Task Types | Example Tasks |
|--------|------------|---------------|
| Biomedical | QA, NER, Text Classification | BioASQ, BioRED, SciERCNER |
| General Science | Summarization, QA, Entailment | Qasper, SciFact, MUP |
| Citation Analysis | Intent Classification, Evidence | Multicite, Evidence Inference |
| Domain-Specific | Relation Extraction, Classification | Discomat, ChemProt |

```mermaid
graph TB
    subgraph "SciRIFF Dataset Collection"
        FullDataset["allenai/SciRIFF<br/>Complete 54 Tasks"]
        TrainMix["allenai/SciRIFF-train-mix<br/>Training Configuration"]
    end
    
    subgraph "Task Categories"
        BioTasks["Biomedical Tasks<br/>BioASQ, BioRED, SciERCNER"]
        GenSciTasks["General Science<br/>Qasper, SciFact, MUP"]
        CiteTasks["Citation Tasks<br/>Multicite, Evidence"]
        DomainTasks["Domain-Specific<br/>ChemProt, Discomat"]
    end
    
    subgraph "Data Splits"
        TrainSplit["Train Split<br/>1000 instances/task"]
        ValSplit["Validation Split<br/>Variable sizes"]
        TestSplit["Test Split<br/>Held-out evaluation"]
    end
    
    subgraph "Training Components"
        SciInstances["Science Instructions<br/>54k instances"]
        TuluData["Tulu-V2 Data<br/>Matching amount"]
        FinalMix["Combined Training Mix<br/>~108k instances"]
    end
    
    FullDataset --> BioTasks
    FullDataset --> GenSciTasks
    FullDataset --> CiteTasks
    FullDataset --> DomainTasks
    
    TrainMix --> TrainSplit
    FullDataset --> ValSplit
    FullDataset --> TestSplit
    
    TrainSplit --> SciInstances
    SciInstances --> FinalMix
    TuluData --> FinalMix
    FinalMix --> TrainMix
```

Sources: [README.md:22-28]()

### Dataset Format and Structure

Each task in the SciRIFF collection follows a consistent instruction-following format with standardized fields:

```mermaid
graph LR
    subgraph "Source Datasets"
        RawData["Raw Scientific<br/>Datasets"]
    end
    
    subgraph "Template Processing"
        ExpertTemplates["Expert-written<br/>Templates"]
        InstrFormat["Instruction<br/>Formatting"]
    end
    
    subgraph "Standardized Format"
        TaskID["task_id"]
        Instruction["instruction"]
        Input["input"]
        Output["output"] 
        Context["context"]
    end
    
    subgraph "HF Dataset Structure"
        Train["train split"]
        Val["validation split"]
        Test["test split"]
    end
    
    RawData --> ExpertTemplates
    ExpertTemplates --> InstrFormat
    InstrFormat --> TaskID
    InstrFormat --> Instruction
    InstrFormat --> Input
    InstrFormat --> Output
    InstrFormat --> Context
    
    TaskID --> Train
    Instruction --> Train
    Input --> Train
    Output --> Train
    Context --> Train
    
    Train --> Val
    Train --> Test
```

Sources: [README.md:3](), [README.md:169-179]()

## SciTulu Model Family

The SciTulu models are instruction-tuned language models fine-tuned specifically on the SciRIFF training mixture to enhance performance on scientific instruction-following tasks.

### Model Variants

| Model | Parameters | Base Model | Training Data | HF Repository |
|-------|------------|------------|---------------|---------------|
| SciTulu-7B | 7 billion | Llama 2 7B | SciRIFF-train-mix | `allenai/scitulu-7b` |
| SciTulu-70B | 70 billion | Llama 2 70B | SciRIFF-train-mix | `allenai/scitulu-70b` |

### Model Architecture and Training

```mermaid
graph TB
    subgraph "Base Models"
        Llama7B["meta-llama/Llama-2-7b-hf<br/>Base Model"]
        Llama70B["meta-llama/Llama-2-70b-hf<br/>Base Model"]
    end
    
    subgraph "Training Data"
        TrainingMix["allenai/SciRIFF-train-mix<br/>108k instances"]
        SciData["Science Tasks<br/>54k instances<br/>1000 per task"]
        TuluData["Tulu-V2 Mix<br/>54k instances<br/>General instruction data"]
    end
    
    subgraph "Training Process"
        OpenInstruct["Open-Instruct<br/>Framework"]
        FineTuning["Instruction<br/>Fine-tuning"]
        TrainingConfig["Training Config<br/>2 epochs<br/>2e-5 LR<br/>4096 seq length"]
    end
    
    subgraph "SciTulu Models"
        SciTulu7B["allenai/scitulu-7b<br/>Scientific Instruction Model"]
        SciTulu70B["allenai/scitulu-70b<br/>Scientific Instruction Model"]
    end
    
    SciData --> TrainingMix
    TuluData --> TrainingMix
    TrainingMix --> OpenInstruct
    
    Llama7B --> FineTuning
    Llama70B --> FineTuning
    OpenInstruct --> FineTuning
    FineTuning --> TrainingConfig
    
    TrainingConfig --> SciTulu7B
    TrainingConfig --> SciTulu70B
```

Sources: [README.md:26-27](), [README.md:128-159]()

### Model Capabilities and Performance

The SciTulu models demonstrate enhanced performance on scientific instruction-following tasks compared to their base models and general instruction-following models. Key capabilities include:

**Scientific Task Proficiency:**
- Biomedical question answering and information extraction
- Scientific literature summarization and analysis  
- Citation intent classification and evidence assessment
- Domain-specific named entity recognition and relation extraction

**Technical Specifications:**
- Maximum sequence length: 4096 tokens
- Chat template compatibility: Tulu format
- Inference backend support: VLLM, transformers, OpenAI-compatible APIs
- Hardware requirements: 7B model runs on single A6000, 70B model requires 4x A100 80GB

```mermaid
graph TB
    subgraph "Model Usage Patterns"
        Inference["Model Inference"]
        ChatTemplate["Chat Template<br/>Tulu Format"]
        VLLMBackend["VLLM Backend<br/>GPU Inference"]
        APIBackend["API Backend<br/>OpenAI Compatible"]
    end
    
    subgraph "Evaluation Tasks"
        HeldOut["9 Held-out Tasks<br/>BioASQ, Qasper, MUP"]
        StandardMetrics["Standard Metrics<br/>BLEU, ROUGE, F1"]
        LMJudge["LM Judge<br/>GPT-4 Evaluation"]
    end
    
    subgraph "Performance Areas"
        QATask["Question Answering<br/>Attributable responses"]
        SummTask["Summarization<br/>Scientific abstracts"]
        NERTask["Named Entity Recognition<br/>Biomedical entities"]
        ClassTask["Text Classification<br/>Citation intents"]
    end
    
    Inference --> ChatTemplate
    ChatTemplate --> VLLMBackend
    ChatTemplate --> APIBackend
    
    VLLMBackend --> HeldOut
    APIBackend --> HeldOut
    HeldOut --> StandardMetrics
    HeldOut --> LMJudge
    
    StandardMetrics --> QATask
    StandardMetrics --> SummTask
    StandardMetrics --> NERTask
    StandardMetrics --> ClassTask
    
    LMJudge --> QATask
    LMJudge --> SummTask
```

Sources: [README.md:81-106](), [README.md:141-142]()

### Model Access and Integration

Both SciTulu models are available through the Hugging Face Hub and can be integrated into evaluation and inference workflows using standard tooling:

**Direct Model Loading:**
- Compatible with `transformers` library
- Supports VLLM for high-throughput inference
- Available through OpenAI-compatible API servers

**Evaluation Integration:**
- Compatible with Eleuther AI evaluation harness
- Integrated with SciRIFF evaluation pipeline via `predict_eleuther.py`
- Supports both chat template and completion-style inference

Sources: [README.md:86-94](), [README.md:99-106]()

---

