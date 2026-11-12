<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/OLMoE · page 6 Expert Routing Analysis · fetched 2026-10-26 -->

# Expert Routing Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/plot_routing_analysis.ipynb](scripts/plot_routing_analysis.ipynb)
- [scripts/routing_output.zip](scripts/routing_output.zip)
- [scripts/run_moe_analysis.py](scripts/run_moe_analysis.py)
- [scripts/run_routing_analysis.py](scripts/run_routing_analysis.py)
- [visuals/emojis/olmoe_checkmark.png](visuals/emojis/olmoe_checkmark.png)

</details>



## Overview

Expert Routing Analysis is a system for understanding how OLMoE (Open Language Model Mixture of Experts) models route tokens to different experts across various domains and model layers. This analysis helps researchers understand the specialization patterns that emerge during training and provides insights into how model architecture and training objectives impact expert utilization.

This documentation focuses on the tools and methodologies used to analyze expert routing behaviors. For information about the model architecture itself, see [Model Architecture](#2).

Sources: [scripts/run_routing_analysis.py](), [scripts/plot_routing_analysis.ipynb](), [scripts/run_moe_analysis.py]()

## Routing Analysis Pipeline

The routing analysis pipeline extracts and analyzes expert routing decisions made by the model during inference. It collects data across different domains, tracks which experts are activated for which tokens, and examines patterns both within and across layers.

```mermaid
flowchart TD
    subgraph InputSources["Input Sources"]
        GitHub["GitHub Code"]
        arXiv["arXiv Papers"]
        C4["C4 Dataset"]
        Books["Books3"]
        Wikipedia["Wikipedia"]
        Tulu["Tulu Dataset"]
    end

    subgraph ModelLoading["Model Loading Phase"]
        LoadModel["Load Model\n- Base OLMoE\n- OLMoE-SFT\n- OLMoE-Instruct\n- Mixtral"]
        EnableRouting["Enable Router Logits Output"]
    end

    subgraph DataCollection["Data Collection Phase"]
        RunInference["Run Inference"]
        CollectRouting["Collect Router Decisions"]
        ExtractExperts["Extract Expert IDs"]
        CountExperts["Count Expert Usage"]
        MapTokens["Map Tokens to Experts"]
    end

    subgraph Analysis["Analysis Phase"]
        LayerAnalysis["Layer-wise Analysis"]
        CrossLayerAnalysis["Cross-layer Analysis"]
        LoadBalancing["Load Balancing Loss"]
        TokenExpertRelation["Token-Expert Relationship"]
    end

    subgraph OutputAndVisualization["Output & Visualization"]
        SaveCounts["Save Expert Counts"]
        SaveCrosslayer["Save Cross-layer Data"]
        SaveTokenMappings["Save Token-Expert Mappings"]
        PlotDistributions["Plot Routing Distributions"]
    end

    InputSources --> RunInference
    LoadModel --> EnableRouting
    EnableRouting --> RunInference
    RunInference --> CollectRouting
    CollectRouting --> ExtractExperts
    ExtractExperts --> CountExperts
    ExtractExperts --> MapTokens
    CountExperts --> LayerAnalysis
    CountExperts --> CrossLayerAnalysis
    CountExperts --> LoadBalancing
    MapTokens --> TokenExpertRelation
    LayerAnalysis --> SaveCounts
    CrossLayerAnalysis --> SaveCrosslayer
    TokenExpertRelation --> SaveTokenMappings
    SaveCounts --> PlotDistributions
    SaveCrosslayer --> PlotDistributions
    SaveTokenMappings --> PlotDistributions
```

Sources: [scripts/run_routing_analysis.py:76-169](), [scripts/run_moe_analysis.py:76-112]()

## Key Components

### 1. Domain-Specific Text Loading

The system loads text from various domains to analyze how routing behavior differs across content types:

```mermaid
flowchart LR
    subgraph Domains["Analysis Domains"]
        GitHub["GitHub Code"]
        arXiv["arXiv Papers"]
        C4["C4 Dataset"]
        Books["Books3"]
        Wikipedia["Wikipedia"]
        Tulu["Tulu v3.1"]
    end

    subgraph TextLoading["Text Loading Functions"]
        LoadAnalysisData["load_analysis_data()"]
    end

    subgraph Processing["Text Processing"]
        Tokenization["Tokenize Text"]
        BatchCreation["Create Batches"]
    end

    Domains --> LoadAnalysisData
    LoadAnalysisData --> Tokenization
    Tokenization --> BatchCreation
```

The `load_analysis_data()` function handles loading text from different domains, tokenizing it, and creating batches for model inference.

Sources: [scripts/run_routing_analysis.py:45-67]()

### 2. Model Loading

The system supports loading different variants of OLMoE models:

```mermaid
flowchart TD
    subgraph ModelLoading["Model Loading Functions"]
        LoadModel["load_model()"]
        LoadSFTModel["load_sft_model()"]
        LoadDPOModel["load_dpo_model()"]
        LoadMistralModel["load_model_mistral()"]
    end

    subgraph Models["Supported Models"]
        BaseOLMoE["OLMoE-1B-7B-0924\nBase Model"]
        SFTOLMoE["OLMoE-1B-7B-0924-SFT\nSFT Model"]
        DPOOLMoE["OLMoE-1B-7B-0924-Instruct\nDPO Model"]
        Mixtral["Mixtral-8x7B-v0.1\nMixtral Model"]
    end

    LoadModel --> BaseOLMoE
    LoadSFTModel --> SFTOLMoE
    LoadDPOModel --> DPOOLMoE
    LoadMistralModel --> Mixtral
```

Sources: [scripts/run_routing_analysis.py:68-96]()

### 3. Router Analysis

The core analysis component collects and processes expert routing decisions:

```mermaid
flowchart TD
    subgraph RunAnalysis["run_analysis() Function"]
        InitCounters["Initialize Counters"]
        Inference["Run Model Inference"]
        CollectRouterLogits["Collect Router Logits"]
        CalculateLoadBalance["Calculate Load Balancing Loss"]
        ExtractExpertIDs["Extract Expert IDs"]
        UpdateCounters["Update Layer Counters"]
        UpdateCrosslayerCounters["Update Cross-layer Counters"]
        UpdateTokenMappings["Update Token-Expert Mappings"]
    end

    subgraph DataStructures["Key Data Structures"]
        LayerCounters["layer_counters\nDict of Counter objects"]
        CrosslayerCounters["crosslayer_counters\nDict of Counter objects"]
        TokenExpertMappings["eid2token_layer*\nDict of Counter objects"]
    end

    InitCounters --> Inference
    Inference --> CollectRouterLogits
    CollectRouterLogits --> CalculateLoadBalance
    CollectRouterLogits --> ExtractExpertIDs
    ExtractExpertIDs --> UpdateCounters
    ExtractExpertIDs --> UpdateCrosslayerCounters
    ExtractExpertIDs --> UpdateTokenMappings
    UpdateCounters --> LayerCounters
    UpdateCrosslayerCounters --> CrosslayerCounters
    UpdateTokenMappings --> TokenExpertMappings
```

The `run_analysis()` function processes input data through the model, extracts routing decisions, and organizes them into various counter data structures for further analysis.

Sources: [scripts/run_routing_analysis.py:105-169](), [scripts/run_moe_analysis.py:77-169]()

## Analysis Methods

### 1. Expert Usage Distribution

Expert usage distribution analysis examines how frequently each expert is activated across different input domains. This helps identify which experts are overutilized or underutilized.

```mermaid
flowchart LR
    subgraph InputData["Input Data"]
        ExpertCounts["Expert Count Data"]
    end

    subgraph Processing["Processing Steps"]
        LoadData["Load Count Data"]
        ConvertPercentage["Convert to Percentages"]
        SortExperts["Sort by Utilization"]
    end

    subgraph Visualization["Visualization"]
        BarCharts["Bar Charts\nper Domain"]
        HeatMaps["Heat Maps\nacross Domains"]
    end

    ExpertCounts --> LoadData
    LoadData --> ConvertPercentage
    ConvertPercentage --> SortExperts
    SortExperts --> BarCharts
    SortExperts --> HeatMaps
```

This analysis reveals whether the router is effectively distributing tokens across all available experts or if there's a bias toward certain experts.

Sources: [scripts/plot_routing_analysis.ipynb:112-169]()

### 2. Router Saturation Across Training

Router saturation analysis tracks how routing decisions evolve during model training. It compares expert assignments at different checkpoints to understand how routing patterns stabilize over time.

```mermaid
flowchart TD
    subgraph Checkpoints["Training Checkpoints"]
        CP1["5,000 Steps (1%)"]
        CP2["120,000 Steps (10%)"]
        CP3["245,000 Steps (20%)"]
        CP4["490,000 Steps (40%)"]
        CP5["Final Checkpoint (100%)"]
    end

    subgraph Analysis["Saturation Analysis"]
        RunInference["Run Inference on Same Data"]
        CompareRouting["Compare Routing Decisions"]
        CalculateMatch["Calculate Match Percentage"]
        PlotResults["Plot Results per Layer"]
    end

    CP1 --> RunInference
    CP2 --> RunInference
    CP3 --> RunInference
    CP4 --> RunInference
    CP5 --> RunInference
    RunInference --> CompareRouting
    CompareRouting --> CalculateMatch
    CalculateMatch --> PlotResults
```

This analysis shows at what point in training the router begins to make consistent decisions, indicating when expert specialization becomes stable.

Sources: [scripts/run_moe_analysis.py:114-245]()

### 3. Co-activation Patterns

Co-activation analysis examines which experts tend to be activated together for the same type of inputs:

```mermaid
flowchart TD
    subgraph DataCollection["Data Collection"]
        ExtractExperts["Extract Expert IDs per Token"]
        CountSingle["Count Single Expert Activations"]
        CountPairs["Count Expert Pair Co-activations"]
    end

    subgraph Analysis["Analysis Steps"]
        CalculateProbs["Calculate Conditional Probabilities"]
        SortPairs["Sort by Co-activation Strength"]
        CreateMatrix["Create Co-activation Matrix"]
    end

    subgraph Visualization["Visualization"]
        Heatmap["Generate Heatmap"]
        AnnotateMap["Annotate with Probabilities"]
    end

    ExtractExperts --> CountSingle
    ExtractExperts --> CountPairs
    CountSingle --> CalculateProbs
    CountPairs --> CalculateProbs
    CalculateProbs --> SortPairs
    SortPairs --> CreateMatrix
    CreateMatrix --> Heatmap
    Heatmap --> AnnotateMap
```

Co-activation analysis helps understand the relationships between experts and identify groups of experts that might have related specializations.

Sources: [scripts/run_moe_analysis.py:246-324]()

### 4. Vocabulary Specialization

Vocabulary specialization analysis maps tokens to the experts that process them most frequently, revealing whether experts have specialized in particular vocabulary subsets:

```mermaid
flowchart TD
    subgraph DataCollection["Data Collection"]
        MapTokensToExperts["Map Token IDs to Experts"]
        CountFrequencies["Count Token-Expert Frequencies"]
    end

    subgraph Analysis["Analysis Steps"]
        CalculateSpecialization["Calculate Specialization Scores"]
        SortBySpecialization["Sort Experts by Specialization"]
        IdentifyVocab["Identify Representative Vocabulary"]
    end

    subgraph Visualization["Visualization"]
        PlotLayerwise["Plot Layer-wise Specialization"]
        PlotExpertwise["Plot Expert-wise Specialization"]
        ListTokens["List Representative Tokens per Expert"]
    end

    MapTokensToExperts --> CountFrequencies
    CountFrequencies --> CalculateSpecialization
    CalculateSpecialization --> SortBySpecialization
    SortBySpecialization --> IdentifyVocab
    IdentifyVocab --> PlotLayerwise
    IdentifyVocab --> PlotExpertwise
    IdentifyVocab --> ListTokens
```

This analysis reveals how experts specialize in different parts of the vocabulary, such as code syntax, mathematical notation, or topic-specific terminology.

Sources: [scripts/run_moe_analysis.py:326-405](), [scripts/run_moe_analysis.py:546-718]()

## Running Routing Analysis

### Using `run_routing_analysis.py`

The main script for basic routing analysis is `run_routing_analysis.py`. Here's how to use it:

1. The script loads a specified model variant (base, SFT, DPO, or Mixtral)
2. It runs analysis on various domains (GitHub, arXiv, C4, books, Wikipedia, Tulu)
3. For each domain, it tracks expert usage and token-expert mappings
4. Results are saved as pickle files for later visualization

Example usage:

```
python scripts/run_routing_analysis.py
```

The script saves results to `routing_output/{model_name}/expert_counts/` and other directories.

Sources: [scripts/run_routing_analysis.py:171-196]()

### Using `run_moe_analysis.py`

For more advanced analysis, including router saturation, co-activation, and vocabulary specialization, use `run_moe_analysis.py`:

1. First, run inference to generate data:
   ```
   python scripts/run_moe_analysis.py --do_inference
   ```

2. For checkpoint analysis:
   ```
   python scripts/run_moe_analysis.py --do_ckpt_analysis --topk 1
   ```

3. For co-activation analysis:
   ```
   python scripts/run_moe_analysis.py --do_coactivation_analysis --layer_num 7
   ```

4. For vocabulary specialization analysis:
   ```
   python scripts/run_moe_analysis.py --do_token_analysis_layers_experts --topk 1
   ```

Sources: [scripts/run_moe_analysis.py:721-747]()

## Key Findings and Interpretations

### Expert Utilization Patterns

The routing analysis reveals several important patterns in expert utilization:

| Layer Position | Typical Pattern | Interpretation |
|----------------|-----------------|----------------|
| Early layers (0-3) | Rapidly stabilizing routing | Early layers specialize quickly in low-level features |
| Middle layers (4-11) | Gradual specialization | Develop more complex, contextual specializations |
| Late layers (12-15) | Most domain-specific routing | Specialize in high-level, domain-specific features |

### Router Saturation

Router saturation analysis shows how expert assignments stabilize during training:

1. At 1% of pretraining, routing decisions are largely random across all layers
2. By 10% of pretraining, early layers show significant stabilization (~60-80% match with final routing)
3. By 40% of pretraining, most layers have reached ~80-90% of their final routing patterns
4. Different layers saturate at different rates, with early layers generally stabilizing faster

### Expert Specialization

Vocabulary specialization analysis reveals that experts specialize in different types of content:

1. Some experts focus on specific domains (e.g., code syntax, mathematical notation)
2. Others specialize in specific parts of speech or linguistic constructs
3. The degree of specialization varies by layer, with later layers showing more pronounced specialization
4. Input token specialization is typically stronger than output token specialization

## Conclusion

Expert Routing Analysis provides crucial insights into how Mixture-of-Experts models like OLMoE distribute computation across experts. These insights can help guide architecture design, training strategies, and model interpretation.

For more detailed analysis of cross-layer routing patterns, see [Cross-Layer Routing Analysis](#6.1). For tools to visualize expert routing patterns, see [Routing Visualization Tools](#6.2). For domain-specific analysis, see [Domain-Specific Routing Analysis](#6.3).

---

