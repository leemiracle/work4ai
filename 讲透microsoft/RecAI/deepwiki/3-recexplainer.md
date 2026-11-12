<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/RecAI · page 3 RecExplainer · fetched 2026-10-26 -->

# RecExplainer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [RecExplainer/README.md](RecExplainer/README.md)
- [RecExplainer/shell/eval_explan.sh](RecExplainer/shell/eval_explan.sh)
- [RecExplainer/shell/infer_alignment.sh](RecExplainer/shell/infer_alignment.sh)

</details>



RecExplainer is a framework for aligning Large Language Models (LLMs) to understand and explain the behavior of black-box recommendation models. The system trains LLMs as surrogate models that can mimic target recommender models and generate natural language explanations for their predictions.

For information about other LLM-based recommendation approaches, see [RecLM-gen and RecLM-cgen](#5) for generative models and [InteRecAgent](#4) for conversational recommendation agents.

## System Overview

RecExplainer consists of two main components: a target recommender model (such as SASRec or Matrix Factorization) that generates recommendations, and an LLM that learns to mimic and explain the target model's behavior through specialized training tasks.

```mermaid
graph TB
    subgraph "RecExplainer Framework"
        subgraph "Target Models"
            SASRec["SASRec<br/>Sequential Recommender"]
            MF["MF<br/>Matrix Factorization"]
        end
        
        subgraph "LLM Surrogate Models"
            RecExpB["RecExplainer-B<br/>Behavior Alignment<br/>Language Space"]
            RecExpI["RecExplainer-I<br/>Intention Alignment<br/>Latent Space"]  
            RecExpH["RecExplainer-H<br/>Hybrid Alignment<br/>Both Spaces"]
        end
        
        subgraph "Training Tasks"
            Task1["uid2next<br/>Next Item Retrieval"]
            Task2["uidiid2rank<br/>Item Ranking"]
            Task3["uidiid2binary<br/>Interest Classification"]
            Task4["Item Discrimination"]
            Task6["uid2hist<br/>History Reconstruction"]
            TaskRec["iid2title<br/>Item Recovery"]
        end
        
        subgraph "Data Sources"
            Amazon["Amazon Video Games<br/>Reviews & Metadata"]
            ShareGPT["ShareGPT<br/>Conversation Data"]
        end
        
        subgraph "Evaluation"
            Alignment["Alignment Effect<br/>Task Performance"]
            Explanation["Explanation Quality<br/>GPT-4 & Human Rating"]
            Distinction["Distinction & Coherence<br/>Classifier & Score Predictor"]
        end
    end
    
    %% Data flow
    Amazon --> SASRec
    Amazon --> MF
    ShareGPT --> RecExpB
    ShareGPT --> RecExpI
    ShareGPT --> RecExpH
    
    %% Target model to LLM alignment
    SASRec --> RecExpB
    SASRec --> RecExpI
    SASRec --> RecExpH
    MF --> RecExpB
    MF --> RecExpI
    MF --> RecExpH
    
    %% Training tasks
    RecExpB --> Task1
    RecExpB --> Task2
    RecExpB --> Task3
    RecExpB --> Task4
    RecExpB --> Task6
    RecExpB --> TaskRec
    
    RecExpI --> Task1
    RecExpI --> Task2
    RecExpI --> Task3
    RecExpI --> Task4
    RecExpI --> Task6
    RecExpI --> TaskRec
    
    RecExpH --> Task1
    RecExpH --> Task2
    RecExpH --> Task3
    RecExpH --> Task4
    RecExpH --> Task6
    RecExpH --> TaskRec
    
    %% Evaluation
    RecExpB --> Alignment
    RecExpI --> Alignment
    RecExpH --> Alignment
    
    RecExpB --> Explanation
    RecExpI --> Explanation
    RecExpH --> Explanation
    
    RecExpB --> Distinction
    RecExpI --> Distinction
    RecExpH --> Distinction
```

Sources: [RecExplainer/README.md:1-20]()

## Alignment Approaches

RecExplainer implements three distinct alignment strategies to train LLMs as surrogate models for recommendation systems:

### Behavior Alignment (RecExplainer-B)
Operates entirely in the language space by representing user preferences and item information as text. The LLM learns to mimic the target model's behavior using textual representations of users and items.

### Intention Alignment (RecExplainer-I) 
Works in the latent space of the recommendation model, using user and item embeddings to understand the model's internal decision-making process.

### Hybrid Alignment (RecExplainer-H)
Combines both language and latent spaces to leverage the benefits of textual understanding and embedding-based reasoning.

```mermaid
graph TB
    subgraph "Alignment Approaches"
        subgraph "Behavior Alignment"
            B_Input["Text Representations<br/>User History + Item Descriptions"]
            B_LLM["LLM<br/>Language Space Processing"]
            B_Output["Text-based Predictions<br/>Mimicking Target Model"]
        end
        
        subgraph "Intention Alignment"
            I_Input["Embedding Vectors<br/>User & Item Representations"]
            I_LLM["LLM<br/>Latent Space Processing"]
            I_Output["Embedding-based Predictions<br/>Understanding Internal Logic"]
        end
        
        subgraph "Hybrid Alignment"
            H_Input_Text["Text Representations"]
            H_Input_Embed["Embedding Vectors"]
            H_LLM["LLM<br/>Combined Processing"]
            H_Output["Hybrid Predictions<br/>Best of Both Worlds"]
        end
        
        subgraph "Target Model Knowledge"
            TargetPreds["Target Model Predictions"]
            TargetEmbeds["Target Model Embeddings"]
        end
    end
    
    %% Behavior alignment flow
    B_Input --> B_LLM
    B_LLM --> B_Output
    TargetPreds --> B_Output
    
    %% Intention alignment flow
    I_Input --> I_LLM
    I_LLM --> I_Output
    TargetEmbeds --> I_Output
    
    %% Hybrid alignment flow
    H_Input_Text --> H_LLM
    H_Input_Embed --> H_LLM
    H_LLM --> H_Output
    TargetPreds --> H_Output
    TargetEmbeds --> H_Output
```

Sources: [RecExplainer/README.md:10-13]()

## Training Tasks and Data Pipeline

The system uses five core training tasks to align the LLM with the target recommender model's behavior patterns:

| Task | Task Type | Description | Inference Mode |
|------|-----------|-------------|----------------|
| Next Item Retrieval | `uid2next` | Predict next item in user sequence | `uid2next` |
| Item Ranking | `uidiid2rank` | Rank candidate items for user | `uidiid2rank` |
| Interest Classification | `uidiid2binary` | Binary classification of user interest | `uidiid2binary` |
| Item Discrimination | - | Distinguish between similar items | - |
| History Reconstruction | `uid2hist` | Reconstruct user interaction history | `uid2hist` |
| Item Recovery | `iid2title` | Recover item information from ID | `iid2title` |

```mermaid
graph LR
    subgraph "Data Preprocessing Pipeline"
        RawData["Raw Amazon Data<br/>meta_Video_Games.json<br/>Video_Games_5.json"]
        ShareGPT["ShareGPT Data<br/>ShareGPT_V3_unfiltered_cleaned_split.json"]
        
        Preprocess["preprocess_recmodel.sh<br/>Data Cleaning & Formatting"]
        UniRecPrep["unirec_prepare_data.sh<br/>UniRec Format Conversion"]
        
        TargetTrain["Target Model Training<br/>unirec_sasrec_train.sh<br/>unirec_mf_train.sh"]
        TargetInfer["Target Model Inference<br/>unirec_sasrec_infer.sh<br/>unirec_mf_infer.sh"]
        
        DataPipeline["recexplainer_data_pipeline.sh<br/>Generate Training Data"]
        
        TrainingFiles["Training Files<br/>behaviour_train.json<br/>intention_train.json<br/>both_train.json"]
        ValidationFiles["Validation Files<br/>behaviour_valid.json<br/>intention_valid.json<br/>both_valid.json"]
        ExplanationFiles["Explanation Files<br/>explan_behaviour_valid.json<br/>explan_intention_valid.json<br/>explan_both_valid.json"]
    end
    
    RawData --> Preprocess
    ShareGPT --> Preprocess
    Preprocess --> UniRecPrep
    UniRecPrep --> TargetTrain
    TargetTrain --> TargetInfer
    TargetInfer --> DataPipeline
    DataPipeline --> TrainingFiles
    DataPipeline --> ValidationFiles
    DataPipeline --> ExplanationFiles
```

Sources: [RecExplainer/README.md:51-117](), [RecExplainer/shell/infer_alignment.sh:1-142]()

## Training and Inference Configuration

The system supports multiple LLM templates and can be configured for different target recommendation models:

### Supported Models and Templates
- **Target Models**: SASRec, Matrix Factorization (MF)
- **LLM Templates**: mistral, vicuna, llama-2, llama-3, phi3
- **Task Types**: behaviour, intention, both, none

### Key Training Parameters

| Parameter | Description | Example Values |
|-----------|-------------|----------------|
| `rec_model_type` | Target recommender model type | `SASRec`, `MF` |
| `task_type` | Alignment method | `behaviour`, `intention`, `both` |
| `template_name` | LLM chat template | `llama-3`, `mistral` |
| `max_hist_len` | Maximum history length | `9` |
| `model_max_length` | Maximum sequence length | `1024` |

```mermaid
graph TB
    subgraph "Training Configuration Flow"
        BaseModel["Base LLM<br/>Llama-3, Mistral, etc."]
        LoRAConfig["LoRA Configuration<br/>Low-rank Adaptation"]
        
        TaskData["Task-specific Data<br/>behaviour_train.json<br/>intention_train.json<br/>both_train.json"]
        
        TrainScript["train.sh<br/>Supervised Fine-tuning"]
        MergeScript["merge.sh<br/>LoRA Adapter Merging"]
        
        AlignedModel["Aligned RecExplainer Model<br/>Merged Final Model"]
        
        InferenceScripts["Inference Scripts<br/>infer_alignment.sh<br/>infer_explan.sh"]
        
        Results["Model Outputs<br/>Alignment Performance<br/>Generated Explanations"]
    end
    
    BaseModel --> LoRAConfig
    TaskData --> TrainScript
    LoRAConfig --> TrainScript
    TrainScript --> MergeScript
    MergeScript --> AlignedModel
    AlignedModel --> InferenceScripts
    InferenceScripts --> Results
```

Sources: [RecExplainer/README.md:119-133](), [RecExplainer/shell/infer_alignment.sh:13-21]()

## Evaluation Framework

RecExplainer employs a comprehensive two-fold evaluation approach to assess both alignment effectiveness and explanation quality:

### Alignment Effect Evaluation
Measures how well the LLM understands the target model's predictive patterns through task-specific performance metrics across the six training tasks.

### Explanation Generation Evaluation

#### Overall Ratings
Uses GPT-4 and human experts to evaluate explanation quality through comparative analysis.

#### Distinction and Coherence
Employs trained classifiers and score predictors to verify that explanations are distinct from other LLMs and coherent with the model's own predictions.

```mermaid
graph TB
    subgraph "Evaluation Pipeline"
        subgraph "Alignment Evaluation"
            AlignInfer["infer_alignment.sh<br/>Task Performance Testing"]
            Tasks["Alignment Tasks<br/>iid2title, uid2hist<br/>uid2next, uidiid2rank<br/>uidiid2binary"]
            AlignResults["Alignment Scores<br/>Task Accuracy Metrics"]
        end
        
        subgraph "Explanation Evaluation"
            ExplanInfer["infer_explan.sh<br/>Generate Explanations"]
            ExplanData["Explanation Outputs<br/>recexplainer-B_response.csv<br/>recexplainer-I_response.csv<br/>recexplainer-H_response.csv"]
            
            GPTEval["eval_explan.sh<br/>GPT-4 Quality Assessment"]
            JudgeData["judge_query.csv<br/>judge_response.csv"]
            
            Discriminator["Discriminator Training<br/>data_gen.sh<br/>run_cls.sh, run_reg.sh"]
            ClassifierReg["Classifier & Regressor<br/>Distinction & Coherence"]
        end
        
        FinalScores["Final Evaluation Scores<br/>Alignment + Explanation Quality"]
    end
    
    %% Alignment evaluation flow
    AlignInfer --> Tasks
    Tasks --> AlignResults
    
    %% Explanation evaluation flow
    ExplanInfer --> ExplanData
    ExplanData --> GPTEval
    GPTEval --> JudgeData
    
    ExplanData --> Discriminator
    Discriminator --> ClassifierReg
    
    %% Final results
    AlignResults --> FinalScores
    JudgeData --> FinalScores
    ClassifierReg --> FinalScores
```

Sources: [RecExplainer/README.md:134-194](), [RecExplainer/shell/eval_explan.sh:1-18]()

## Implementation Architecture

The RecExplainer codebase follows a modular structure with distinct components for data processing, model training, and evaluation:

```mermaid
graph TB
    subgraph "RecExplainer Code Structure"
        subgraph "Shell Scripts"
            ShellPreprocess["shell/preprocess_recmodel.sh<br/>shell/unirec_prepare_data.sh"]
            ShellTrain["shell/unirec_sasrec_train.sh<br/>shell/unirec_mf_train.sh"]
            ShellPipeline["shell/recexplainer_data_pipeline.sh"]
            ShellTraining["shell/train.sh<br/>shell/merge.sh"]
            ShellInference["shell/infer_alignment.sh<br/>shell/infer_explan.sh"]
            ShellEval["shell/eval_explan.sh"]
        end
        
        subgraph "Source Code"
            SrcInference["src/inference.py<br/>Model Inference Engine"]
            SrcTraining["src/ (Training Components)"]
        end
        
        subgraph "Preprocessing"
            PrepUtils["preprocess/unirec_utils/<br/>Data Processing Utilities"]
            PrepEval["preprocess/eval_explan.py<br/>preprocess/gpt_api.py"]
        end
        
        subgraph "Discriminator"
            DiscGen["discriminator/data_gen.sh"]
            DiscTrain["discriminator/run_cls.sh<br/>discriminator/run_reg.sh"]
        end
        
        subgraph "Configuration"
            ConfigInfer["shell/config/infer_single_node.yaml<br/>Accelerate Configuration"]
        end
        
        subgraph "Data Directory Structure"
            DataAmazon["data/amazon_video_games_v3/<br/>datamaps.json, metadata.json<br/>SASRec.pth, sequential_data.txt"]
            DataMF["data/mf_amazon_video_games_v3/<br/>MF.pth, sim_item.txt"]
            DataOutput["output/amazon_video_games_v3/<br/>Inference Results"]
        end
    end
    
    %% Flow connections
    ShellPreprocess --> PrepUtils
    ShellTrain --> DataAmazon
    ShellTrain --> DataMF
    ShellPipeline --> DataAmazon
    ShellTraining --> SrcTraining
    ShellInference --> SrcInference
    ShellInference --> ConfigInfer
    ShellEval --> PrepEval
    
    SrcInference --> DataOutput
    DiscGen --> DiscTrain
```

Sources: [RecExplainer/README.md:76-98](), [RecExplainer/shell/infer_alignment.sh:23-46]()

---

