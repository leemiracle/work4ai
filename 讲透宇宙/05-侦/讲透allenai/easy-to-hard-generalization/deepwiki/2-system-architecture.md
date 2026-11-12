<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/easy-to-hard-generalization · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [main.py](main.py)
- [run_jobs.py](run_jobs.py)

</details>



This page provides a high-level overview of the system architecture for the "Easy-to-Hard Generalization" framework. It describes the main system components, how they interact, and the overall data and control flow. For detailed information about the experiment workflow, see [Experiment Workflow](#2.1), and for configuration details, see [Configuration System](#2.2).

## System Components Overview

The codebase is organized into several core components that work together to test the hypothesis that language models can generalize from easy to hard examples:

```mermaid
graph TD
    subgraph "Experiment Orchestration"
        runJobs["run_jobs.py"]
    end

    subgraph "Core Execution"
        main["main.py"]
    end

    subgraph "Data Management"
        dataUtils["data_utils.py"]
        prompt["prompt.py"]
    end

    subgraph "Model Handling"
        probes["models/probes.py"]
        LMutils["utils/LM_utils.py"]
    end

    subgraph "Evaluation"
        metrics["utils/metrics.py"]
    end

    subgraph "Configuration"
        globals["globals.py"]
    end

    runJobs -->|"Launches experiments with\nspecific configurations"| main
    globals -->|"Provides config\nparameters"| runJobs
    globals -->|"Provides config\nparameters"| main
    
    main -->|"Loads & processes\ndatasets"| dataUtils
    main -->|"Formats prompts"| prompt
    main -->|"Creates probes"| probes
    main -->|"Processes LM batches"| LMutils
    main -->|"Evaluates results"| metrics

    dataUtils -->|"Feeds data to"| probes
    LMutils -->|"Supports"| probes
    probes -->|"Outputs evaluated by"| metrics
```

Sources: [main.py:963-1114](), [run_jobs.py:193-251](), [run_jobs.py:677-795]()

## Component Roles and Responsibilities

The system consists of these primary components:

1. **Experiment Orchestration (`run_jobs.py`)**: Manages experiment configuration and launches experiments
2. **Core Execution (`main.py`)**: Implements experiment logic including training, evaluation, and hardness estimation
3. **Data Management**: Handles dataset loading, processing, and formatting
4. **Model Handling**: Manages model interaction, probing methods, and batch processing
5. **Evaluation**: Computes metrics and analyzes results
6. **Configuration (`globals.py`)**: Defines dataset and model configurations

### Component Details

```mermaid
classDiagram
    class runJobs {
        +write_hidden_states()
        +estimate_hardness()
        +all_to_all_table()
        +get_population_table()
        +noisy_labels_table()
        +third_grade_to_college()
    }
    
    class main {
        +write_hidden_states()
        +load_hidden_states()
        +write_MDL_scores()
        +write_text_prob_scores()
        +postprocess_hardness_scores()
        +run_modeling_experiment()
    }
    
    class Probe {
        +fit()
        +repeated_fit()
        +finetune()
        +forward()
        +save_probe()
        +load_probe()
    }
    
    class Prompt {
        +get_prompt_kwargs_from_id()
        +get_str_prompt_templates()
        +format_prompt()
    }
    
    class data_utils {
        +load_datasets()
        +split_datasets()
        +prepare_dataset_for_dataloader()
        +get_dataloader()
    }
    
    runJobs --> main : launches
    main --> Probe : creates/uses
    main --> Prompt : uses
    main --> data_utils : uses
```

Sources: [main.py:26-98](), [main.py:99-196](), [main.py:500-963](), [run_jobs.py:255-318]()

## Data Flow Architecture

The system processes data through several stages, from raw datasets to evaluation results:

```mermaid
flowchart TD
    subgraph "Input Data"
        rawData["Raw Datasets\n(MMLU, ARC, StrategyQA, GSM8k)"]
    end

    subgraph "Data Processing"
        writeDatasets["write_datasets_with_known_hardness\nStandardizes and splits datasets"]
        loadDatasets["load_datasets\nLoads datasets from disk"]
        splitDatasets["split_datasets\nSplits into train/dev/test"]
        prepareData["prepare_dataset_for_dataloader\nFormats data for models"]
    end

    subgraph "Prompt Formatting"
        promptObj["Prompt Object\nManages prompt templates"]
        formatPrompt["format_prompt\nCreates formatted prompts"]
    end

    subgraph "Model Interaction"
        hiddenStates["write_hidden_states\nExtracts model representations"]
        probeTraining["Probe Training\n(Linear/MLP/Transformer)"]
        evaluation["evaluate_model\nRuns predictions"]
    end

    subgraph "Results"
        metrics["Calculate metrics\n(accuracy, confidence intervals)"]
        storage["Save results to CSV"]
    end

    rawData --> writeDatasets
    writeDatasets --> loadDatasets
    loadDatasets --> splitDatasets
    splitDatasets --> prepareData
    
    prepareData --> promptObj
    promptObj --> formatPrompt
    
    prepareData --> hiddenStates
    hiddenStates --> probeTraining
    formatPrompt --> evaluation
    probeTraining --> evaluation
    
    evaluation --> metrics
    metrics --> storage
```

Sources: [main.py:1171-1207](), [main.py:1247-1266](), [main.py:1500-1580]()

## Experimental Methods Architecture

The system supports multiple approaches to evaluate model generalization:

| Method | Description | Implementation | Key Components |
|--------|-------------|----------------|----------------|
| **Decoding** | Direct use of language model probabilities | Uses model's native token prediction | LM_utils.py for scoring |
| **Learned Probes** | Trains a classifier on extracted representations | Linear, MLP, or Transformer on hidden states | models/probes.py |
| **Finetuning** | Updates model weights (QLoRA) | PEFT-based finetuning | PEFT library integration |

### Probing and Evaluation System

```mermaid
graph TD
    subgraph "Hidden State Extraction"
        extractHidden["write_hidden_states()"]
        loadHidden["load_hidden_states()"]
    end

    subgraph "Probe Methods"
        decoding["decoding\nDirect LM scoring"]
        learned["learned\nClassifier on hidden states"]
        finetuned["finetuned\nModel weight updates"]
    end

    subgraph "Probe Models"
        linear["Linear Classifier"]
        mlp["MLP"]
        transformer["Transformer"]
    end

    subgraph "Evaluation"
        decodingEval["Score answer choices"]
        learnedEval["Train + evaluate probe"]
        finetunedEval["Finetune + evaluate model"]
    end

    extractHidden --> loadHidden
    loadHidden --> learned
    
    decoding --> decodingEval
    learned --> learnedEval
    finetuned --> finetunedEval
    
    learned --> linear
    learned --> mlp
    learned --> transformer
```

Sources: [main.py:26-98](), [main.py:500-596](), [main.py:660-699]()

## Hardness Evaluation System

A key component of the framework is measuring the "hardness" of examples:

```mermaid
flowchart LR
    subgraph "Hardness Methods"
        humanHardness["Human-Defined Hardness\n(Bloom, Grade, Difficulty)"]
        modelHardness["Model-Based Hardness\n(MDL, Answer Probability)"]
        textHardness["Text-Based Metrics\n(Question/Answer Length)"]
    end

    subgraph "Hardness Calculation"
        mdlScores["write_MDL_scores()\nFits models to data subsets"]
        textProbs["write_text_prob_scores()\nComputes text probabilities"]
        postprocess["postprocess_hardness_scores()\nProcesses and normalizes scores"]
    end

    subgraph "Application"
        stratify["Stratify datasets by hardness"]
        evaluate["Evaluate by hardness levels"]
    end

    humanHardness --> stratify
    
    modelHardness --> mdlScores
    mdlScores --> postprocess
    
    textHardness --> textProbs
    textProbs --> postprocess
    
    postprocess --> stratify
    stratify --> evaluate
```

Sources: [main.py:99-317](), [main.py:336-368](), [main.py:369-498]()

## Integration with External Libraries

The system integrates with several key external libraries:

```mermaid
graph TD
    subgraph "Core Framework"
        main["main.py"]
    end

    subgraph "HuggingFace Libraries"
        transformers["transformers\nModel loading & tokenization"]
        peft["PEFT\nParameter-efficient finetuning"]
    end

    subgraph "Data Processing"
        pandas["pandas\nData manipulation"]
        torch["PyTorch\nTensor operations"]
    end

    subgraph "Evaluation"
        numpy["NumPy\nNumerical operations"]
        scipy["SciPy\nStatistical functions"]
    end

    main -->|"Loads models"| transformers
    main -->|"Finetuning"| peft
    main -->|"Data handling"| pandas
    main -->|"Model operations"| torch
    main -->|"Numerical processing"| numpy
    main -->|"Statistics"| scipy
```

Sources: [main.py:1-24](), [main.py:1242-1266]()

## Control Flow between Components

The high-level control flow across the system:

```mermaid
sequenceDiagram
    participant RunJobs as run_jobs.py
    participant Main as main.py
    participant Data as data_utils.py
    participant Probe as models/probes.py
    participant Metrics as utils/metrics.py
    
    RunJobs->>RunJobs: Configure experiment
    RunJobs->>Main: Launch experiment with configuration
    
    Main->>Data: Load and process dataset
    Data-->>Main: Return prepared dataset
    
    Main->>Main: Load model
    
    alt write_hidden_states
        Main->>Main: Extract and save hidden states
    else estimate_hardness
        Main->>Probe: Create hardness probe
        Main->>Main: Calculate hardness scores
        Main->>Main: Write scores to dataset
    else do_eval
        Main->>Probe: Create evaluation probe
        Main->>Main: Run modeling experiment
        Main->>Metrics: Evaluate results
        Metrics-->>Main: Return metrics
        Main->>Main: Save results
    end
    
    Main-->>RunJobs: Return results
    RunJobs->>RunJobs: Aggregate results
```

Sources: [run_jobs.py:255-318](), [run_jobs.py:394-496](), [main.py:963-1303]()

## Storage Architecture

The system organizes its data across several key directories:

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `data/` | Dataset storage | Raw and processed datasets, hidden representations |
| `outputs/` | Results storage | Experiment results CSV files |
| `result_sheets/` | Aggregated results | Combined results for analysis |
| Model directory | Model storage | Saved models and probes |
| Cache directory | HuggingFace cache | Downloaded models |

Sources: [main.py:1091-1116](), [main.py:1147-1151](), [main.py:863-894]()

---

