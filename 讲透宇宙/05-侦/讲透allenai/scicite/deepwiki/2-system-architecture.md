<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/scicite · page 2 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [experiment_configs/scicite-experiment.json](experiment_configs/scicite-experiment.json)

</details>



This document provides a comprehensive overview of the SciCite system architecture, explaining how various components interact to enable citation intent classification in scientific publications. It covers the high-level system structure, data flow, model components, and integration points. For details about specific implementations, see the dedicated pages for [Model Architecture](#2.1) and [Multi-Task Learning Framework](#2.2).

## System Overview

The SciCite system is designed to classify the intent behind citations in academic papers using a multi-task learning approach with auxiliary scaffolding tasks.

```mermaid
graph TD
    subgraph "Data Preparation"
        DataSources["Data Sources"] --> Readers["Dataset Readers"]
        Readers --> Vocabulary["Vocabulary Builder"]
    end
    
    subgraph "Model Components"
        Config["Configuration Files"] --> ModelDef["Model Definition"]
        Vocabulary --> ModelDef
        ModelDef --> ScaffoldModel["ScaffoldBilstmAttentionClassifier"]
    end
    
    subgraph "Training System"
        Readers --> TrainingPipeline["Training Pipeline"]
        ScaffoldModel --> TrainingPipeline
        Config --> TrainingPipeline
        TrainingPipeline --> SavedModel["Trained Model Artifact"]
    end
    
    subgraph "Inference System"
        SavedModel --> Predictors["Predictor Classes"]
        NewData["New Citation Data"] --> Predictors
        Predictors --> Output["Citation Intent Predictions"]
    end
    
    CLI["Command Line Interface"] --> TrainingPipeline
    CLI --> Predictors
```

Sources: [README.md:5-7](), [README.md:38-40](), [experiment_configs/scicite-experiment.json:17-36]()

## Core Components and Data Flow

The SciCite system integrates multiple specialized components for processing citation data through dataset readers, building vocabulary, training models, and making predictions.

### Dataset Readers

The system uses specialized dataset readers for different data types:

| Reader Type | Purpose | Configuration Path |
|-------------|---------|-------------------|
| `scicite_datasetreader` | Main citation intent classification data | [experiment_configs/scicite-experiment.json:17-22]() |
| `scicite_section_title_data_reader` | Section title prediction (auxiliary task) | [experiment_configs/scicite-experiment.json:23-26]() |
| `scicite_cite_worthiness_data_reader` | Citation worthiness prediction (auxiliary task) | [experiment_configs/scicite-experiment.json:27-30]() |

### Model Components

```mermaid
graph TD
    subgraph "ScaffoldBilstmAttentionClassifier"
        Input["Citation Text Input"] --> Embedder["TextFieldEmbedder"]
        
        subgraph "Embedding Components"
            Embedder --> GloVe["GloVe Embeddings"]
            Embedder --> ELMo["ELMo Embeddings (optional)"]
            Embedder --> Lexicon["Lexicon Embedder"]
        end
        
        GloVe --> Encoder["GRU Encoder (BiDirectional)"]
        ELMo --> Encoder
        Lexicon --> Encoder
        
        Encoder --> Attention["Attention Mechanism"]
        Attention --> EncodedRep["Encoded Representation"]
        
        subgraph "Classification Heads"
            EncodedRep --> MainClassifier["Citation Intent Classifier"]
            EncodedRep --> AuxClassifier1["Section Title Classifier"]
            EncodedRep --> AuxClassifier2["Citation Worthiness Classifier"]
        end
        
        MainClassifier --> Output1["Citation Intent (3 classes)"]
        AuxClassifier1 --> Output2["Section Title (5 classes)"]
        AuxClassifier2 --> Output3["Citation Worthiness (2 classes)"]
    end
```

Sources: [experiment_configs/scicite-experiment.json:38-104]()

### Data Flow

```mermaid
flowchart TD
    subgraph "Input Processing"
        SCData["SciCite Dataset"] --> SCReader["scicite_datasetreader"]
        SectionData["Section Title Data"] --> STReader["scicite_section_title_data_reader"]
        WorthinessData["Citation Worthiness Data"] --> CWReader["scicite_cite_worthiness_data_reader"]
        
        SCReader --> TrainData["Training Data"]
        SCReader --> DevData["Validation Data"]
        SCReader --> TestData["Test Data"]
        STReader --> AuxData1["Auxiliary Task 1 Data"]
        CWReader --> AuxData2["Auxiliary Task 2 Data"]
    end
    
    subgraph "Training Flow"
        TrainData --> VocabBuilder["VocabularyMultitask"]
        AuxData1 --> VocabBuilder
        AuxData2 --> VocabBuilder
        
        VocabBuilder --> ModelInit["Model Initialization"]
        
        ModelInit --> TrainLoop["MultiTaskTrainer"]
        TrainData --> TrainLoop
        DevData --> TrainLoop
        AuxData1 --> TrainLoop
        AuxData2 --> TrainLoop
        
        TrainLoop --> LossFn["Multi-Task Loss Function"]
        MixingRatio1["mixing_ratio (λ₂)"] --> LossFn
        MixingRatio2["mixing_ratio2 (λ₃)"] --> LossFn
        
        LossFn --> ModelUpdate["Model Parameter Update"]
        ModelUpdate --> ModelEval["Model Evaluation"]
        DevData --> ModelEval
        
        ModelEval --> SaveModel["Save Best Model"]
    end
    
    subgraph "Inference Flow"
        SaveModel --> ModelArtifact["Trained Model"]
        ModelArtifact --> Predictor["Predictor (scicite/aclarc)"]
        NewCitations["New Citation Data"] --> Predictor
        Predictor --> Predictions["Citation Intent Predictions"]
    end
```

Sources: [README.md:74-103](), [experiment_configs/scicite-experiment.json:17-36](), [experiment_configs/scicite-experiment.json:121-131]()

## Multi-Task Training System

The system employs a sophisticated multi-task training approach, using auxiliary tasks as scaffolds to improve the main citation intent classification task.

```mermaid
graph TD
    subgraph "MultiTaskTrainer Components"
        TrainFunc["train_local.py"] --> TrainArgs["train_model_from_args"]
        TrainArgs --> TrainFile["train_model_from_file"]
        TrainFile --> TrainModel["train_model"]
        
        TrainModel --> LoadDatasets["datasets_from_params"]
        TrainModel --> BuildVocab["VocabularyMultitask"]
        TrainModel --> CreateModel["Model.from_params"]
        TrainModel --> CreateIterator["DataIterator.from_params"]
        
        LoadDatasets --> MainData["Main Dataset (Citation Intent)"]
        LoadDatasets --> AuxData1["Auxiliary Dataset 1 (Section Title)"]
        LoadDatasets --> AuxData2["Auxiliary Dataset 2 (Citation Worthiness)"]
        
        CreateModel --> ScaffoldModel["ScaffoldBilstmAttentionClassifier"]
        
        MainData --> TrainerInstance["MultiTaskTrainer2"]
        AuxData1 --> TrainerInstance
        AuxData2 --> TrainerInstance
        ScaffoldModel --> TrainerInstance
        BuildVocab --> TrainerInstance
        CreateIterator --> TrainerInstance
        
        TrainerInstance --> TrainLoop["Training Loop"]
        
        TrainLoop --> MixRatio["Mixing Ratio Controls"]
        TrainLoop --> LossCalc["Loss Calculation"]
        LossCalc --> Update["Model Update"]
        Update --> Evaluate["Evaluate on Validation"]
        Evaluate --> SaveBest["Save Best Model"]
    end
```

Sources: [README.md:74-103](), [experiment_configs/scicite-experiment.json:13-16]()

## Command Line Interface

The system provides a command-line interface for training models and making predictions:

```mermaid
flowchart LR
    subgraph "Command Line Interface"
        User["User"] --> Commands["SciCite Commands"]
        
        Commands --> C1["train"]
        Commands --> C2["train_multitask"]
        Commands --> C3["train_multitask_2"]
        Commands --> C4["evaluate"]
        Commands --> C5["predict"]
        
        C1 --> T1["Standard Training"]
        C2 --> T2["Training with Section Title Task"]
        C3 --> T3["Training with Both Auxiliary Tasks"]
        C4 --> T4["Model Evaluation"]
        C5 --> T5["Citation Intent Prediction"]
        
        T5 --> P1["predictor_scicite"]
        T5 --> P2["predictor_aclarc"]
    end
```

Sources: [README.md:48-67](), [README.md:98-103]()

## Model Configuration

The model configuration is controlled via JSON configuration files, with key parameters:

| Parameter | Purpose | Example Value |
|-----------|---------|--------------|
| `train_data_path` | Path to main training data | `"data/train.jsonl"` |
| `validation_data_path` | Path to development data | `"data/dev.jsonl"` |
| `train_data_path_aux` | Path to section title auxiliary data | `"data/cite-sections.jsonl"` |
| `train_data_path_aux2` | Path to citation worthiness auxiliary data | `"data/cite-worthiness.jsonl"` |
| `mixing_ratio` | Control parameter (λ₂) for first auxiliary task | Variable |
| `mixing_ratio2` | Control parameter (λ₃) for second auxiliary task | Variable |
| `with_elmo` | Whether to use ELMo contextual embeddings | `true` or `false` |

Sources: [README.md:79-88](), [experiment_configs/scicite-experiment.json:6-16]()

## Integration with External Components

```mermaid
graph TD
    subgraph "SciCite System"
        Config["Configuration Files"] --> Model["ScaffoldBilstmAttentionClassifier"]
        Model --> TrainedModel["Trained Model (.tar.gz)"]
        TrainedModel --> Predictor["Predictors"]
        InputData["Input Citation Data (.jsonl)"] --> Predictor
        Predictor --> Output["Citation Intent Predictions"]
    end
    
    subgraph "External Components"
        AllenNLP["AllenNLP Framework"] --- Model
        GloVeEmbed["GloVe Embeddings (100d)"] --> Model
        ElmoEmbed["ELMo Embeddings"] --> Model
        Output --> SemScholarAPI["Semantic Scholar API"]
    end
```

Sources: [README.md:38-40](), [README.md:48-67](), [experiment_configs/scicite-experiment.json:47-74]()

## System Requirements and Dependencies

The SciCite system requires:

- Python 3.6
- AllenNLP library
- Dependencies specified in requirements.in and constraints.txt

The system can utilize GPU acceleration if available, configured through the `cuda_device` parameter in the trainer configuration.

Sources: [README.md:39-46](), [experiment_configs/scicite-experiment.json:127]()

---

