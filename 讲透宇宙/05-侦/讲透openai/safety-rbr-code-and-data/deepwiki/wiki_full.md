# Page: Overview

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [base_classes.py](base_classes.py)
- [cached_classes.py](cached_classes.py)
- [rbr_weight_fitter.py](rbr_weight_fitter.py)
- [readme.md](readme.md)

</details>



## Purpose and Scope

This repository implements a **Rule-Based Refusal (RBR) Weight Fitting System** for AI safety research. The system learns optimal linear combinations of rule-based safety features and reward model scores to improve AI response quality and safety through supervised optimization.

The codebase provides tools for fitting weights that balance compliance with user requests against safety considerations, using both human-labeled evaluation data and synthetic training datasets. For detailed documentation of specific components, see [Core Components](#2). For dataset information, see [Data and Configuration](#3). For usage examples, see [Usage and Examples](#4).

**Sources:** [readme.md:1-23]()

## System Architecture

The RBR weight fitting system follows a modular architecture with abstract interfaces, cached data implementations, and a core optimization engine.

### Core Component Relationships

```mermaid
graph TB
    subgraph "Abstract_Layer"
        FV["FeaturesValues<br/>(base_classes.py)"]
        RMS["RewardModelScores<br/>(base_classes.py)"]
    end
    
    subgraph "Implementation_Layer" 
        CFV["CachedFeaturesValues<br/>(cached_classes.py)"]
        CRMS["CachedRewardModelScores<br/>(cached_classes.py)"]
    end
    
    subgraph "Core_Engine"
        RBREM["RBR_ExampleWithMetadata<br/>(rbr_weight_fitter.py)"]
        RBRWF["RBRWeightFitter<br/>(rbr_weight_fitter.py)"]
    end
    
    subgraph "Data_Sources"
        GOLD["rbr_gold_data/<br/>train.jsonl, test.jsonl"]
        SYNTH["weight_fitting_data/<br/>prop_probs/, rewards/"]
        CONFIG["proposition_prompts.yaml"]
    end
    
    FV --> CFV
    RMS --> CRMS
    CFV --> RBRWF
    CRMS --> RBRWF
    RBREM --> RBRWF
    
    SYNTH --> CFV
    SYNTH --> CRMS
    GOLD --> RBREM
    CONFIG --> CFV
```

**Sources:** [base_classes.py:1-14](), [cached_classes.py:1-60](), [rbr_weight_fitter.py:10-24]()

## Optimization Workflow

The core optimization process combines rule-based features with reward model scores using hinge loss minimization.

### Weight Fitting Process

```mermaid
flowchart TD
    subgraph "Data_Preparation"
        EX["RBR_ExampleWithMetadata<br/>examples"]
        FEAT["features: Dict[str, float]"]
        RW["base_reward: float"]
    end
    
    subgraph "RBRWeightFitter_Setup"
        ORD["orderings: Dict[str, List[str]]"]
        PAIRS["get_orderings()<br/>preference pairs"]
        WEIGHTS["weights: torch.Tensor<br/>requires_grad=True"]
    end
    
    subgraph "Optimization_Loop"
        LOSS["get_loss()<br/>F.relu hinge loss"]
        ADAM["torch.optim.AdamW<br/>lr=1e-2, wd=0.0"]
        UPDATE["weight updates<br/>n_iters=1000"]
    end
    
    subgraph "Output"
        FITTED["weights_dict<br/>Dict[str, float]"]
        METRICS["metrics<br/>loss, valid_loss, frac_clipped"]
    end
    
    EX --> PAIRS
    FEAT --> LOSS  
    RW --> LOSS
    ORD --> PAIRS
    PAIRS --> LOSS
    WEIGHTS --> LOSS
    LOSS --> ADAM
    ADAM --> UPDATE
    UPDATE --> WEIGHTS
    UPDATE --> FITTED
    UPDATE --> METRICS
```

**Sources:** [rbr_weight_fitter.py:25-140]()

## Data Pipeline Overview

The system processes two distinct types of datasets with different purposes and scales.

| Dataset Type | Location | Purpose | Size | Features |
|--------------|----------|---------|------|----------|
| **RBR Gold Dataset** | `data/rbr_gold_data/` | Evaluation, prompt tuning | ~350 examples | Hand-labeled safety annotations |
| **Weight Fitting Dataset** | `data/weight_fitting_data/` | Training, optimization | Large synthetic | Cached feature probabilities + reward scores |
| **Configuration** | `config/proposition_prompts.yaml` | Feature definitions | N/A | Response classification rules |

### Data Flow Architecture

```mermaid
graph LR
    subgraph "Input_Data"
        PROMPT["AI prompts<br/>(potentially harmful)"]
        COMP["AI completions<br/>(comply/refuse/partial)"]
    end
    
    subgraph "Feature_Extraction"
        PROP["proposition classification<br/>~20 boolean features"]
        RM["reward model scoring<br/>quality assessment"]
    end
    
    subgraph "Cached_Storage"
        PROPFILE["prop_probs/{split}.jsonl<br/>CachedFeaturesValues"]
        RMFILE["rewards/{rm_size}/{split}.jsonl<br/>CachedRewardModelScores"]
    end
    
    subgraph "Weight_Optimization"
        FIT["RBRWeightFitter.fit_weights()<br/>hinge loss + AdamW"]
        OUT["optimized feature weights<br/>Dict[str, float]"]
    end
    
    PROMPT --> PROP
    COMP --> PROP
    COMP --> RM
    PROP --> PROPFILE
    RM --> RMFILE
    PROPFILE --> FIT
    RMFILE --> FIT
    FIT --> OUT
```

**Sources:** [cached_classes.py:7-9](), [cached_classes.py:36-59](), [rbr_weight_fitter.py:112-139]()

## Key Implementation Classes

The system is built around several core classes that handle different aspects of the weight fitting process:

| Class | File | Purpose | Key Methods |
|-------|------|---------|-------------|
| `FeaturesValues` | `base_classes.py` | Abstract interface for feature extraction | `get_features()` |
| `RewardModelScores` | `base_classes.py` | Abstract interface for reward scoring | `get_reward_model_scores()` |
| `CachedFeaturesValues` | `cached_classes.py` | File-based feature lookup | `get_features()` |
| `CachedRewardModelScores` | `cached_classes.py` | File-based reward lookup | `get_reward_model_scores()` |
| `RBR_ExampleWithMetadata` | `rbr_weight_fitter.py` | Data container for training examples | `add_base_reward()`, `add_features()` |
| `RBRWeightFitter` | `rbr_weight_fitter.py` | Core optimization engine | `fit_weights()`, `get_orderings()` |

### Safety Feature Categories

The system evaluates AI responses across multiple safety dimensions defined in the configuration:

- **Safety Features**: `disallowed_content`, `reference_safety_policy`, `threatening_language`
- **Compliance Features**: `fully_complies`, `partially_complies`, `inability_to_comply`  
- **Communication Features**: `apology`, `encourage_professional_help`, `meta_commentary`

**Sources:** [base_classes.py:4-14](), [cached_classes.py:14-59](), [rbr_weight_fitter.py:10-63](), [cached_classes.py:10]()

## Usage Entry Points

The system provides two main entry points for users:

1. **Weight Fitting Example** (`weight_fitting_example.ipynb`) - Demonstrates the complete workflow using synthetic data
2. **RBR Gold Data Analysis** (`analyze_RBR_gold_data.ipynb`) - Shows how to work with the human-labeled evaluation dataset

Both notebooks use utility functions from `utils.py` for data loading and visualization. For detailed usage instructions, see [Getting Started](#4.1).

**Sources:** [readme.md:13-18]()

---

# Page: Core Components

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [base_classes.py](base_classes.py)
- [cached_classes.py](cached_classes.py)
- [rbr_weight_fitter.py](rbr_weight_fitter.py)

</details>



This document covers the main code components that implement the RBR (Rule-Based Refusal) weight fitting system. These components provide the foundational architecture for combining rule-based safety features with reward model scores through learned weight optimization.

For information about the datasets used by these components, see [Data and Configuration](#3). For usage examples and tutorials, see [Usage and Examples](#4).

## System Architecture

The core components follow a layered architecture with abstract interfaces, concrete cached implementations, and a central weight fitting engine that orchestrates the optimization process.

```mermaid
graph TB
    subgraph "Abstract Layer"
        FV["FeaturesValues<br/>(Abstract Base Class)"]
        RMS["RewardModelScores<br/>(Abstract Base Class)"]
    end
    
    subgraph "Implementation Layer"  
        CFV["CachedFeaturesValues<br/>(Cached Implementation)"]
        CRMS["CachedRewardModelScores<br/>(Cached Implementation)"]
    end
    
    subgraph "Weight Fitting Engine"
        RBEM["RBR_ExampleWithMetadata<br/>(Data Container)"]
        RBWF["RBRWeightFitter<br/>(Optimization Engine)"]
    end
    
    subgraph "Data Sources"
        PROP["prop_probs/*.jsonl<br/>(Feature Data)"]
        REW["rewards/large/*.jsonl<br/>(Reward Data)"]
        CONFIG["proposition_prompts.yaml<br/>(Feature Config)"]
    end
    
    FV --> CFV
    RMS --> CRMS
    PROP --> CFV
    REW --> CRMS
    CONFIG --> CFV
    CFV --> RBWF
    CRMS --> RBWF
    RBEM --> RBWF
```

**Sources:** [base_classes.py:1-14](), [cached_classes.py:1-60](), [rbr_weight_fitter.py:1-140]()

## Abstract Base Classes

The system defines two core abstract interfaces that establish contracts for feature extraction and reward model scoring.

### FeaturesValues Interface

The `FeaturesValues` abstract base class defines the interface for extracting safety features from AI responses.

| Method | Parameters | Returns | Purpose |
|--------|------------|---------|---------|
| `get_features` | `prompt: str`, `completions: List[str]` | `List[dict[str, float]]` | Extract feature values for each completion |

### RewardModelScores Interface  

The `RewardModelScores` abstract base class defines the interface for obtaining reward model scores.

| Method | Parameters | Returns | Purpose |
|--------|------------|---------|---------|
| `get_reward_model_scores` | `prompt: str`, `completions: List[str]` | `List[float]` | Get reward scores for each completion |

**Sources:** [base_classes.py:4-14]()

## Cached Implementations

The cached implementations provide concrete realizations of the abstract interfaces by loading pre-computed data from JSONL files.

```mermaid
graph LR
    subgraph "CachedFeaturesValues"
        CFV_INIT["__init__()<br/>Load cached data"]
        CFV_GET["get_features()<br/>Hash-based lookup"]
        CFV_TRAIN["train_data<br/>(Dict)"]
        CFV_TEST["test_data<br/>(Dict)"]
    end
    
    subgraph "CachedRewardModelScores"
        CRMS_INIT["__init__(rm_size)<br/>Load cached data"]
        CRMS_GET["get_reward_model_scores()<br/>Hash-based lookup"]
        CRMS_TRAIN["train_data<br/>(Dict)"]
        CRMS_TEST["test_data<br/>(Dict)"]
    end
    
    subgraph "Data Files"
        PROP_TRAIN["prop_probs/train.jsonl"]
        PROP_TEST["prop_probs/test.jsonl"]
        REW_TRAIN["rewards/large/train.jsonl"]
        REW_TEST["rewards/large/test.jsonl"]
    end
    
    PROP_TRAIN --> CFV_TRAIN
    PROP_TEST --> CFV_TEST
    REW_TRAIN --> CRMS_TRAIN
    REW_TEST --> CRMS_TEST
    
    CFV_TRAIN --> CFV_GET
    CFV_TEST --> CFV_GET
    CRMS_TRAIN --> CRMS_GET
    CRMS_TEST --> CRMS_GET
```

### CachedFeaturesValues

This class implements feature extraction by loading pre-computed feature probabilities from JSONL files. Features are stored in hash tables keyed by `(prompt, completion)` tuples for efficient lookup.

Key implementation details:
- Data files: `data/weight_fitting_data/prop_probs/{split}.jsonl`
- Hash key: `tuple(d['prompt_completion'])`
- Configuration: `config/proposition_prompts.yaml` (loaded but not used during lookup)

### CachedRewardModelScores

This class implements reward model scoring by loading pre-computed scores from JSONL files. Supports different reward model sizes through the `rm_size` parameter.

Key implementation details:
- Data files: `data/weight_fitting_data/rewards/{rm_size}/{split}.jsonl`
- Hash key: `tuple(d['prompt_completion'])`
- Default model size: `"large"`

**Sources:** [cached_classes.py:14-60]()

## Weight Fitting Engine

The weight fitting engine consists of two main components: a data container for examples and the optimization algorithm.

### RBR_ExampleWithMetadata

This dataclass serves as the primary data container for training examples, encapsulating all necessary information for weight optimization.

| Field | Type | Purpose |
|-------|------|---------|
| `convo_prompt` | `str` | The input prompt |
| `convo_completion` | `str` | The AI response |
| `response_type` | `str` | Classification of response type |
| `completion_label` | `str` | Quality label for ordering |
| `base_reward` | `Optional[float]` | Reward model score |
| `features` | `Optional[Dict[str, float]]` | Feature values |

Methods:
- `add_base_reward(base_reward: float)`: Sets the reward model score
- `add_features(features: Dict[str, float])`: Updates feature dictionary

### RBRWeightFitter

The main optimization class that learns optimal weights for combining rule-based features with reward model scores using hinge loss optimization.

```mermaid
graph TD
    INPUT["Input Examples<br/>RBR_ExampleWithMetadata"]
    VALIDATE["validate_examples()<br/>Check data consistency"]
    PAIRS["get_orderings()<br/>Generate preference pairs"]
    PREP["prepare_optimization()<br/>Setup tensors & optimizer"]
    OPTIM["fit_weights()<br/>AdamW optimization loop"]
    OUTPUT["Output: weights_dict<br/>& metrics"]
    
    INPUT --> VALIDATE
    VALIDATE --> PAIRS
    PAIRS --> PREP
    PREP --> OPTIM
    OPTIM --> OUTPUT
    
    subgraph "Key Methods"
        LOSS["get_loss()<br/>Hinge loss calculation"]
        ZERO["zero_some_feature_weights()<br/>Feature masking"]
    end
    
    OPTIM --> LOSS
    OPTIM --> ZERO
```

#### Core Optimization Process

1. **Validation**: Ensures all examples have valid completion labels and complete feature sets
2. **Pair Generation**: Creates preference pairs based on completion label orderings
3. **Loss Computation**: Calculates hinge loss: `max(0, margin + score_worse - score_better)`
4. **Weight Updates**: Uses AdamW optimizer with configurable learning rate and weight decay
5. **Feature Masking**: Supports ignoring specific features during optimization

#### Key Parameters

| Parameter | Type | Default | Purpose |
|-----------|------|---------|---------|
| `feature_names` | `List[str]` | - | Names of features to optimize |
| `orderings` | `Dict[str, List[str]]` | - | Preference ordering rules |
| `train_data_frac` | `float` | `0.95` | Training/validation split |
| `margin` | `float` | `1` | Hinge loss margin |
| `lr` | `float` | `1e-2` | Learning rate |
| `n_iters` | `int` | `1000` | Optimization iterations |

**Sources:** [rbr_weight_fitter.py:10-140]()

## Component Integration

The components work together through a clear data flow where cached implementations provide features and rewards to populate `RBR_ExampleWithMetadata` objects, which are then processed by `RBRWeightFitter` to learn optimal feature weights.

```mermaid
sequenceDiagram
    participant CF as CachedFeaturesValues
    participant CR as CachedRewardModelScores  
    participant EX as RBR_ExampleWithMetadata
    participant WF as RBRWeightFitter
    
    Note over CF,CR: Data Loading Phase
    CF->>CF: Load prop_probs/*.jsonl
    CR->>CR: Load rewards/large/*.jsonl
    
    Note over EX,WF: Example Population Phase
    CF->>EX: get_features() -> add_features()
    CR->>EX: get_reward_model_scores() -> add_base_reward()
    
    Note over WF: Optimization Phase
    EX->>WF: List[RBR_ExampleWithMetadata]
    WF->>WF: validate_examples()
    WF->>WF: get_orderings()
    WF->>WF: fit_weights()
    WF->>WF: return weights_dict, metrics
```

**Sources:** [base_classes.py:1-14](), [cached_classes.py:1-60](), [rbr_weight_fitter.py:1-140]()

---

# Page: Weight Fitting Engine

# Weight Fitting Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [rbr_weight_fitter.py](rbr_weight_fitter.py)

</details>



## Purpose and Scope

The Weight Fitting Engine implements the core optimization logic for the Rule-Based Refusal (RBR) weight fitting system. This engine learns optimal linear combinations of safety features and reward model scores to improve AI response quality while maintaining safety constraints. The engine uses hinge loss optimization with pairwise ranking constraints to fit weights that respect human-defined response quality orderings.

For information about the abstract base classes and data interfaces, see [Base Architecture](#2.2). For details about the underlying datasets, see [RBR Gold Dataset](#3.1) and [Weight Fitting Dataset](#3.2).

## Architecture Overview

The Weight Fitting Engine consists of two main classes that work together to optimize feature weights through pairwise ranking optimization.

### Core Classes Architecture

```mermaid
graph TB
    subgraph "Data Container"
        RBR_Ex["RBR_ExampleWithMetadata"]
        RBR_Ex_Fields["convo_prompt: str<br/>convo_completion: str<br/>response_type: str<br/>completion_label: str<br/>base_reward: Optional[float]<br/>features: Dict[str, float]"]
    end
    
    subgraph "Weight Fitting Engine"
        RBRFitter["RBRWeightFitter"]
        RBRFitter_Fields["feature_names: List[str]<br/>examples: List[RBR_ExampleWithMetadata]<br/>orderings: Dict[str, List[str]]<br/>weights: torch.Tensor<br/>metrics: Dict[str, List]"]
    end
    
    subgraph "Optimization Components"
        Validator["validate_examples()"]
        Orderings["get_orderings()"]
        Prep["prepare_optimization()"]
        Loss["get_loss()"]
        Fit["fit_weights()"]
    end
    
    RBR_Ex --> RBR_Ex_Fields
    RBRFitter --> RBR_Ex
    RBRFitter --> RBRFitter_Fields
    RBRFitter --> Validator
    RBRFitter --> Orderings
    RBRFitter --> Prep
    RBRFitter --> Loss
    RBRFitter --> Fit
```

*Sources: [rbr_weight_fitter.py:10-24](), [rbr_weight_fitter.py:25-65]()*

### Data Flow Through the Engine

```mermaid
flowchart TD
    Input["Input Examples<br/>RBR_ExampleWithMetadata[]"]
    Features["Feature Extraction<br/>features: Dict[str, float]"]
    Rewards["Base Rewards<br/>base_reward: float"]
    
    subgraph "RBRWeightFitter Initialization"
        Validate["validate_examples()"]
        Orderings["get_orderings()"]
        Prep["prepare_optimization()"]
    end
    
    subgraph "Optimization Loop"
        Loss["get_loss()"]
        Backward["loss.backward()"]
        Step["optimizer.step()"]
    end
    
    Output["Optimized Weights<br/>Dict[str, float]"]
    Metrics["Training Metrics<br/>loss, valid_loss, frac_clipped"]
    
    Input --> Features
    Input --> Rewards
    Features --> Validate
    Rewards --> Validate
    Validate --> Orderings
    Orderings --> Prep
    Prep --> Loss
    Loss --> Backward
    Backward --> Step
    Step --> Loss
    Loss --> Output
    Loss --> Metrics
```

*Sources: [rbr_weight_fitter.py:112-139]()*

## Data Structures

### RBR_ExampleWithMetadata

The `RBR_ExampleWithMetadata` class serves as the primary data container for training examples. Each example represents a conversation prompt-completion pair with associated metadata and features.

| Field | Type | Description |
|-------|------|-------------|
| `convo_prompt` | `str` | The input conversation prompt |
| `convo_completion` | `str` | The AI-generated completion |
| `response_type` | `str` | Classification of response behavior |
| `completion_label` | `str` | Quality label for ranking |
| `base_reward` | `Optional[float]` | Reward model score |
| `features` | `Dict[str, float]` | Safety and quality features |

The class provides methods to incrementally build examples:
- `add_base_reward(base_reward: float)` - Sets the reward model score
- `add_features(features: Dict[str, float])` - Updates the feature dictionary

*Sources: [rbr_weight_fitter.py:10-23]()*

### RBRWeightFitter Configuration

The `RBRWeightFitter` constructor accepts comprehensive configuration for the optimization process:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `feature_names` | `List[str]` | Required | Names of features to optimize |
| `examples` | `List[RBR_ExampleWithMetadata]` | Required | Training examples |
| `orderings` | `Dict[str, List[str]]` | Required | Quality ordering constraints |
| `ignore_features` | `List[str]` | `[]` | Features to exclude from optimization |
| `train_data_frac` | `float` | `0.95` | Fraction of data for training |
| `margin` | `float` | `1` | Hinge loss margin |
| `lr` | `float` | `1e-2` | Learning rate |
| `wd` | `float` | `0.0` | Weight decay |
| `n_iters` | `int` | `1000` | Optimization iterations |
| `completion_label_margin` | `Dict[str, float]` | `{}` | Custom margins per label |

*Sources: [rbr_weight_fitter.py:25-52]()*

## Optimization Process

### Pairwise Ranking Generation

The engine generates training pairs from examples based on quality orderings. For each pair of examples with the same prompt, it determines the preferred ordering based on completion labels.

```mermaid
graph LR
    subgraph "Example Pairs"
        Ex1["Example 1<br/>completion_label: 'ideal'"]
        Ex2["Example 2<br/>completion_label: 'compliant'"]
    end
    
    subgraph "Ordering Logic"
        Check["Same prompt?"]
        Order["orderings['ideal']<br/>contains 'compliant'?"]
        Pair["Generate pair: [1, 2, margin]"]
    end
    
    subgraph "Training Data"
        Pairs["torch.tensor pairs<br/>[better_idx, worse_idx, margin]"]
        Split["Train/Validation Split<br/>train_data_frac = 0.95"]
    end
    
    Ex1 --> Check
    Ex2 --> Check
    Check --> Order
    Order --> Pair
    Pair --> Pairs
    Pairs --> Split
```

*Sources: [rbr_weight_fitter.py:71-89]()*

### Hinge Loss Optimization

The core optimization uses hinge loss to enforce ranking constraints. The loss function ensures that better examples receive higher scores than worse examples by at least the specified margin.

```mermaid
graph TB
    subgraph "Score Computation"
        BaseReward["base_reward"]
        Features["features @ weights"]
        TotalScore["total_score = base_reward + features @ weights"]
    end
    
    subgraph "Hinge Loss"
        ScoreDiff["score_diff = total_score[worse] - total_score[better]"]
        HingeLoss["hinge_loss = ReLU(margin + score_diff)"]
        BatchLoss["batch_loss = mean(hinge_loss)"]
    end
    
    subgraph "Optimization"
        Backward["loss.backward()"]
        AdamW["AdamW optimizer"]
        WeightUpdate["weights -= lr * gradient"]
    end
    
    BaseReward --> TotalScore
    Features --> TotalScore
    TotalScore --> ScoreDiff
    ScoreDiff --> HingeLoss
    HingeLoss --> BatchLoss
    BatchLoss --> Backward
    Backward --> AdamW
    AdamW --> WeightUpdate
```

*Sources: [rbr_weight_fitter.py:105-110](), [rbr_weight_fitter.py:127-136]()*

### Mathematical Formulation

The optimization objective minimizes the hinge loss over pairwise rankings:

**Score Function:**
```
score(example) = base_reward + Σ(feature_i × weight_i)
```

**Hinge Loss:**
```
loss = mean(ReLU(margin + score(worse) - score(better)))
```

**Constraints:**
- Weights for ignored features are zeroed via gradient hooks
- Custom margins can be specified per completion label
- Train/validation split for monitoring overfitting

*Sources: [rbr_weight_fitter.py:91-94](), [rbr_weight_fitter.py:105-110]()*

## Usage Workflow

### Complete Optimization Pipeline

```mermaid
flowchart TD
    subgraph "Setup"
        Examples["Prepare RBR_ExampleWithMetadata[]"]
        Features["Add features via add_features()"]
        Rewards["Add rewards via add_base_reward()"]
        Orderings["Define quality orderings"]
    end
    
    subgraph "Initialization"
        Fitter["RBRWeightFitter(feature_names, examples, orderings)"]
        Config["Set optimization hyperparameters"]
    end
    
    subgraph "Training"
        FitWeights["fit_weights()"]
        ValidateEx["validate_examples()"]
        GetOrderings["get_orderings()"]
        PrepOpt["prepare_optimization()"]
        OptLoop["Optimization loop (n_iters)"]
    end
    
    subgraph "Output"
        Weights["weights_dict: Dict[str, float]"]
        MetricsOut["metrics: Dict[str, List]"]
    end
    
    Examples --> Features
    Features --> Rewards
    Rewards --> Fitter
    Orderings --> Fitter
    Fitter --> Config
    Config --> FitWeights
    FitWeights --> ValidateEx
    ValidateEx --> GetOrderings
    GetOrderings --> PrepOpt
    PrepOpt --> OptLoop
    OptLoop --> Weights
    OptLoop --> MetricsOut
```

*Sources: [rbr_weight_fitter.py:112-139]()*

### Monitoring and Metrics

The engine tracks three key metrics during optimization:

| Metric | Description |
|--------|-------------|
| `loss` | Training hinge loss per iteration |
| `valid_loss` | Validation hinge loss per iteration |
| `frac_clipped` | Fraction of constraints already satisfied |

The `frac_clipped` metric indicates optimization progress - higher values mean more ranking constraints are being satisfied with sufficient margin.

*Sources: [rbr_weight_fitter.py:64](), [rbr_weight_fitter.py:108](), [rbr_weight_fitter.py:134-136]()*

---

# Page: Base Architecture

# Base Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [base_classes.py](base_classes.py)
- [cached_classes.py](cached_classes.py)

</details>



This document covers the foundational architecture for the RBR weight fitting system, specifically the abstract base classes and their cached implementations that provide feature extraction and reward model scoring capabilities. For information about the weight optimization engine that uses these components, see [Weight Fitting Engine](#2.1). For details about the underlying datasets, see [Weight Fitting Dataset](#3.2).

## Abstract Interface Layer

The base architecture defines two core abstract interfaces that provide standardized access to features and reward scores for prompt-completion pairs.

### FeaturesValues Abstract Base Class

The `FeaturesValues` class defines the interface for extracting safety-related features from AI responses.

```mermaid
classDiagram
    class FeaturesValues {
        <<abstract>>
        +get_features(prompt, completions) List~dict~
    }
    
    FeaturesValues --|> CachedFeaturesValues : implements
    
    class CachedFeaturesValues {
        +train_data: dict
        +test_data: dict  
        +features_config: dict
        +get_features(prompt, completions)
    }
```

The `get_features` method takes a prompt and list of completions, returning feature dictionaries with float values representing safety-related properties of each completion.

**Sources:** [base_classes.py:4-8]()

### RewardModelScores Abstract Base Class  

The `RewardModelScores` class defines the interface for obtaining quality scores from reward models.

```mermaid
classDiagram
    class RewardModelScores {
        <<abstract>>
        +get_reward_model_scores(prompt, completions) List~float~
    }
    
    RewardModelScores --|> CachedRewardModelScores : implements
    
    class CachedRewardModelScores {
        +train_data: dict
        +test_data: dict
        +rm_size: str
        +get_reward_model_scores(prompt, completions)
    }
```

The `get_reward_model_scores` method returns numerical quality scores for each completion given a prompt.

**Sources:** [base_classes.py:10-14]()

## Cached Implementation Layer

The cached implementations provide concrete functionality by loading pre-computed data from disk and serving it through hash-based lookups.

### Data Loading Architecture

Both cached classes follow a consistent pattern for loading and accessing pre-computed data:

```mermaid
flowchart TD
    subgraph "CachedFeaturesValues"
        A1["CACHED_FEATURES<br/>'data/weight_fitting_data/prop_probs/{split}.jsonl'"]
        B1["read_jsonl()"]
        C1["train_data: dict<br/>test_data: dict"]
        D1["Hash Key: (prompt, completion) tuple"]
    end
    
    subgraph "CachedRewardModelScores" 
        A2["CACHED_REWARD_MODEL_SCORES<br/>'data/weight_fitting_data/rewards/{rm_size}/{split}.jsonl'"]
        B2["read_jsonl()"]
        C2["train_data: dict<br/>test_data: dict"]
        D2["Hash Key: (prompt, completion) tuple"]
    end
    
    A1 --> B1
    B1 --> C1
    C1 --> D1
    
    A2 --> B2  
    B2 --> C2
    C2 --> D2
```

**Sources:** [cached_classes.py:8-9](), [cached_classes.py:16-21](), [cached_classes.py:38-43]()

### Hash-Based Lookup Pattern

Both implementations use a consistent lookup mechanism:

| Component | Hash Key Generation | Data Structure | Fallback Behavior |
|-----------|-------------------|----------------|-------------------|
| `CachedFeaturesValues` | `(to_string(prompt), to_string(completion))` | `train_data`, `test_data` dicts | Raises `ValueError` if not found |
| `CachedRewardModelScores` | `(to_string(prompt), to_string(completion))` | `train_data`, `test_data` dicts | Raises `ValueError` if not found |

The lookup process checks the training data first, then test data, and raises an exception if the prompt-completion pair is not found in either dataset.

**Sources:** [cached_classes.py:25-32](), [cached_classes.py:50-57]()

## Configuration Integration

The `CachedFeaturesValues` class maintains a reference to the proposition prompts configuration, though this is not actively used in the cached implementation:

```mermaid
graph LR
    A["CONFIG_FILE_PATH<br/>'config/proposition_prompts.yaml'"] 
    B["read_yaml()"]
    C["features_config: dict"]
    D["CachedFeaturesValues"]
    
    A --> B
    B --> C
    C --> D
    
    E["Note: Configuration loaded but not used<br/>in cached implementation"]
    D -.-> E
```

**Sources:** [cached_classes.py:7](), [cached_classes.py:46]()

## Data Flow Architecture

The complete data flow from cached files to feature/reward extraction:

```mermaid
flowchart TB
    subgraph "File System"
        F1["prop_probs/train.jsonl<br/>prop_probs/test.jsonl"]
        F2["rewards/large/train.jsonl<br/>rewards/large/test.jsonl"] 
        F3["config/proposition_prompts.yaml"]
    end
    
    subgraph "Initialization"
        I1["CachedFeaturesValues.__init__()"]
        I2["CachedRewardModelScores.__init__(rm_size='large')"]
    end
    
    subgraph "Runtime Lookup"
        L1["get_features(prompt, completions)"]
        L2["get_reward_model_scores(prompt, completions)"]
        L3["to_string() conversion"]
        L4["Hash table lookup"]
    end
    
    subgraph "Output"
        O1["List[dict[str, float]]<br/>Feature values"]
        O2["List[float]<br/>Reward scores"]
    end
    
    F1 --> I1
    F2 --> I2
    F3 --> I1
    
    I1 --> L1
    I2 --> L2
    
    L1 --> L3
    L2 --> L3
    L3 --> L4
    
    L4 --> O1
    L4 --> O2
```

**Sources:** [cached_classes.py:14-34](), [cached_classes.py:36-59]()

---

# Page: Utilities

# Utilities

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [utils.py](utils.py)

</details>



The utilities module provides essential helper functions for data loading, format conversion, and visualization support across the RBR weight fitting system. These functions handle common operations like reading JSONL and YAML files, converting conversation data structures, and providing consistent styling for data visualization.

For information about the core weight fitting algorithms, see [2.1](#2.1). For details about data structures these utilities operate on, see [3.1](#3.1) and [3.2](#3.2).

## Data Loading Functions

The utilities module provides standardized functions for reading the various data formats used throughout the RBR system.

### JSONL File Reading

The `read_jsonl()` function handles the primary data format used for both the gold dataset and weight fitting dataset:

**Function**: `read_jsonl(file_path)`
- **Purpose**: Reads JSON Lines files and returns a list of parsed objects
- **Error Handling**: Catches `FileNotFoundError` and `json.JSONDecodeError` with descriptive messages
- **Usage**: Loading training data, test data, and feature probability files

### YAML Configuration Loading

The `read_yaml()` function loads configuration files that define the response classification system:

**Function**: `read_yaml(file_path)`
- **Purpose**: Safely loads YAML configuration files
- **Primary Use**: Loading `proposition_prompts.yaml` for response classification rules

**System Integration Diagram**
```mermaid
graph TB
    subgraph "Data Sources"
        A["rbr_gold_data/train.jsonl"]
        B["rbr_gold_data/test.jsonl"]
        C["weight_fitting_data/prop_probs/train.jsonl"]
        D["weight_fitting_data/rewards/large/train.jsonl"]
        E["config/proposition_prompts.yaml"]
    end
    
    subgraph "utils.py Functions"
        F["read_jsonl()"]
        G["read_yaml()"]
    end
    
    subgraph "System Components"
        H["CachedFeaturesValues"]
        I["CachedRewardModelScores"]
        J["RBRWeightFitter"]
        K["Jupyter Notebooks"]
    end
    
    A --> F
    B --> F
    C --> F
    D --> F
    E --> G
    
    F --> H
    F --> I
    F --> J
    F --> K
    G --> H
    G --> K
```

Sources: [utils.py:7-27](), [utils.py:36-39]()

## Data Conversion Functions

### Conversation String Conversion

The `to_string()` function converts conversation data structures into standardized string representations:

**Function**: `to_string(conversation)`
- **Purpose**: Converts conversation arrays to hashable string format
- **Format**: `|ROLE|: content` with newline separators
- **Usage**: Creating consistent identifiers for conversations across different data processing stages

**Conversation Processing Flow**
```mermaid
graph LR
    subgraph "Input Format"
        A["[{'role': 'user', 'content': 'prompt'}, {'role': 'assistant', 'content': 'response'}]"]
    end
    
    subgraph "Processing"
        B["to_string()"]
    end
    
    subgraph "Output Format"
        C["|USER|: prompt\n|ASSISTANT|: response"]
    end
    
    A --> B
    B --> C
```

Sources: [utils.py:29-33]()

## Visualization Support Functions

The utilities module provides comprehensive support for consistent visualization across analysis notebooks and reports.

### Color Generation

The `get_colors()` function generates color palettes using matplotlib's viridis colormap:

**Function**: `get_colors(num_samples=3, end_point=1.0)`
- **Purpose**: Generate evenly spaced colors from viridis colormap
- **Parameters**: Number of colors and colormap endpoint
- **Output**: Array of RGB color values

### Response Classification Color Mapping

The module defines standardized color mappings for different response types and completion qualities:

| Response Type | Completion Quality | Color Assignment |
|---------------|-------------------|------------------|
| Comply | fully complies | colors[0] |
| Comply | partially complies | colors[1] |
| Comply | random non-refusal | colors[2] |
| Comply | imperfect refusal | colors[3] |
| Comply | perfect refusal | colors[4] |
| Hard Refuse | perfect hard refusal | colors2[0] |
| Hard Refuse | bad hard refusal | colors2[1] |
| Hard Refuse | disallowed content | colors2[2] |
| Safe Refuse | perfect safe completion | colors2[0] |
| Safe Refuse | bad safe completion | colors2[1] |
| Safe Refuse | disallowed content | colors2[2] |

### Label Standardization

The `labels_map` dictionary provides human-readable labels for visualization:

**Key Mappings**:
- `'fully complies'` → `"Complies (Ideal)"`
- `'perfect hard refusal'` → `"Perfect Refusal (Ideal)"`  
- `'perfect safe completion'` → `"Perfect Safe Refusal (Ideal)"`
- `'disallowed content'` → `"Disallowed"`

**Visualization System Architecture**
```mermaid
graph TB
    subgraph "Color Generation"
        A["get_colors()"]
        B["colors = get_colors(num_samples=5)"]
        C["colors2 = get_colors(num_samples=3, end_point=0.9)"]
    end
    
    subgraph "Mapping Structures"
        D["color_mapping"]
        E["labels_map"]
    end
    
    subgraph "Usage Contexts"
        F["analyze_RBR_gold_data.ipynb"]
        G["weight_fitting_example.ipynb"]
        H["Matplotlib Plots"]
    end
    
    A --> B
    A --> C
    B --> D
    C --> D
    D --> F
    D --> G
    D --> H
    E --> F
    E --> G
    E --> H
```

Sources: [utils.py:42-79]()

## Integration with System Components

The utilities module serves as a foundational layer that supports data processing throughout the RBR system:

### Direct Dependencies

- **CachedFeaturesValues**: Uses `read_jsonl()` to load feature probability data
- **CachedRewardModelScores**: Uses `read_jsonl()` to load reward model scores  
- **Analysis Notebooks**: Uses all utility functions for data loading and visualization
- **Weight Fitting Process**: Indirectly uses utilities through cached classes

### Data Flow Pattern

1. Raw data files → `read_jsonl()`/`read_yaml()` → Parsed data structures
2. Conversation objects → `to_string()` → Hashable identifiers
3. Analysis results → `color_mapping`/`labels_map` → Consistent visualizations

**Utility Function Call Pattern**
```mermaid
graph TB
    subgraph "Jupyter Notebooks"
        A["analyze_RBR_gold_data.ipynb"]
        B["weight_fitting_example.ipynb"]
    end
    
    subgraph "Core Classes"
        C["CachedFeaturesValues.__init__()"]
        D["CachedRewardModelScores.__init__()"]
    end
    
    subgraph "utils.py Functions"
        E["read_jsonl()"]
        F["read_yaml()"]
        G["to_string()"]
        H["color_mapping"]
        I["labels_map"]
    end
    
    A --> E
    A --> F
    A --> H
    A --> I
    B --> E
    B --> H
    B --> I
    C --> E
    D --> E
    C --> G
    D --> G
```

Sources: [utils.py:1-79]()

The utilities module ensures consistent data handling and presentation across all components of the RBR weight fitting system, providing a stable foundation for both automated processing and human analysis.

---

# Page: Data and Configuration

# Data and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [config/proposition_prompts.yaml](config/proposition_prompts.yaml)
- [data/rbr_gold_data/test.jsonl](data/rbr_gold_data/test.jsonl)
- [data/rbr_gold_data/train.jsonl](data/rbr_gold_data/train.jsonl)
- [data/weight_fitting_data/test.jsonl](data/weight_fitting_data/test.jsonl)
- [data/weight_fitting_data/train.jsonl](data/weight_fitting_data/train.jsonl)

</details>



This document covers the datasets and configuration files that drive the RBR weight fitting system. It describes the response classification framework, the evaluation and training datasets, and how they integrate with the codebase.

For information about the core weight fitting algorithms, see [Weight Fitting Engine](#2.1). For details about the abstract interfaces and cached implementations that load this data, see [Base Architecture](#2.2).

## Response Classification System

The response classification system is defined in [config/proposition_prompts.yaml:1-1000]() and provides the framework for evaluating AI responses across multiple safety and quality dimensions.

### Classification Hierarchy

```mermaid
graph TD
    A["completion_class_order"] --> B["ideal"]
    A --> C["minimum_acceptable_style"] 
    A --> D["unacceptable_completion"]
    A --> E["illogical_completion"]
    A --> F["disallowed_completion"]
    
    B --> G["Response Types"]
    C --> G
    D --> G
    E --> G 
    F --> G
    
    G --> H["hard_refuse"]
    G --> I["safe_refuse_1"]
    G --> J["safe_refuse_2"] 
    G --> K["comply"]
```

**Sources:** [config/proposition_prompts.yaml:30-38]()

### Proposition System Architecture

```mermaid
graph LR
    A["simple_propositions"] --> B["derived_propositions"]
    B --> C["completion_classes"]
    
    A --> D["fully_complies"]
    A --> E["partially_complies"]
    A --> F["disallowed_content"]
    A --> G["meta_commentary"]
    A --> H["judgement"]
    
    B --> I["acceptable_refusal"]
    B --> J["correct_refusal"]
    B --> K["acceptable_safe_completion__self_harm"]
    
    C --> L["ideal"]
    C --> M["minimum_acceptable_style"]
    C --> N["unacceptable_completion"]
```

**Sources:** [config/proposition_prompts.yaml:115-173](), [config/proposition_prompts.yaml:175-1000]()

The system defines approximately 20 boolean propositions that capture different aspects of AI responses:

| Proposition Category | Examples | Purpose |
|---------------------|----------|---------|
| Compliance | `fully_complies`, `partially_complies` | Measure request fulfillment |
| Safety | `disallowed_content`, `threatening_language` | Detect harmful content |
| Communication | `apology`, `encourage_professional_help` | Assess response style |
| Meta-commentary | `meta_commentary`, `reference_safety_policy` | Track AI self-references |

**Sources:** [config/proposition_prompts.yaml:175-1000]()

## Data Architecture Overview

```mermaid
graph TB
    subgraph "Configuration"
        A["proposition_prompts.yaml"]
    end
    
    subgraph "Gold Dataset"
        B["rbr_gold_data/train.jsonl"]
        C["rbr_gold_data/test.jsonl"]
    end
    
    subgraph "Weight Fitting Dataset" 
        D["weight_fitting_data/train.jsonl"]
        E["weight_fitting_data/test.jsonl"]
        F["weight_fitting_data/prop_probs/"]
        G["weight_fitting_data/rewards/large/"]
    end
    
    subgraph "Code Interfaces"
        H["CachedFeaturesValues"]
        I["CachedRewardModelScores"]
        J["RBRWeightFitter"]
    end
    
    A -.-> B
    A -.-> C
    A -.-> D
    A -.-> E
    
    F --> H
    G --> I
    B --> J
    C --> J
    H --> J
    I --> J
```

**Sources:** [cached_classes.py:1-50](), [rbr_weight_fitter.py:1-100]()

## RBR Gold Dataset Structure

The gold dataset contains ~350 hand-labeled examples used for evaluation and prompt development. Each example follows this structure:

```mermaid
graph LR
    A["RBR_ExampleWithMetadata"] --> B["category"]
    A --> C["response_type"] 
    A --> D["prompt"]
    A --> E["completion"]
    A --> F["propositions"]
    
    B --> G["None"]
    B --> H["K-C"] 
    B --> I["SH-C"]
    B --> J["H-C"]
    B --> K["C-C"]
    
    C --> L["Comply"]
    C --> M["Hard Refuse"]
    C --> N["Safe Refuse 1"]
    C --> O["Safe Refuse 2"]
    
    F --> P["~20 boolean features"]
```

**Sources:** [data/rbr_gold_data/train.jsonl:1-5](), [data/rbr_gold_data/test.jsonl:1-5]()

### Content Categories

| Category | Description | Example Context |
|----------|-------------|-----------------|
| `None` | Benign requests | General information queries |
| `K-C` | Knowledge about Crime | Requests about criminal methods |
| `SH-C` | Self-Harm Content | Suicide or self-injury related |
| `H-C` | Hate Content | Discriminatory or hateful material |
| `C-C` | Controversial Content | Sensitive but not harmful topics |

**Sources:** [data/rbr_gold_data/train.jsonl:1-100]()

### Response Types

The dataset classifies AI responses into four main types based on how they handle potentially harmful requests:

```mermaid
graph TD
    A["AI Response"] --> B["Comply"]
    A --> C["Hard Refuse"]
    A --> D["Safe Refuse 1"]
    A --> E["Safe Refuse 2"]
    
    B --> F["Provides requested content"]
    C --> G["Direct refusal without alternatives"]
    D --> H["Refuses with empathetic alternatives"]
    E --> I["Refuses with educational content"]
```

**Sources:** [data/rbr_gold_data/train.jsonl:1-200]()

## Weight Fitting Dataset Structure

The weight fitting dataset provides synthetic training data at larger scale with multiple completion variants per prompt:

```mermaid
graph LR
    A["weight_fitting_data"] --> B["prompt_text"]
    A --> C["completion_variants[]"]
    
    C --> D["completion_text"]
    C --> E["completion_type"]
    C --> F["category"]
    C --> G["response_type"]
    
    E --> H["perfect refusal"]
    E --> I["imperfect refusal"]
    E --> J["partially complies"]
    E --> K["fully complies"]
    E --> L["random non-refusal"]
```

**Sources:** [data/weight_fitting_data/train.jsonl:1-10](), [data/weight_fitting_data/test.jsonl:1-10]()

### Completion Quality Hierarchy

The synthetic dataset uses a more granular completion quality classification:

| Completion Type | Description | Training Purpose |
|----------------|-------------|------------------|
| `perfect refusal` | Clean, direct refusal | Positive examples for safety |
| `imperfect refusal` | Refusal with unnecessary content | Borderline safety examples |
| `partially complies` | Provides some requested content | Partial compliance detection |
| `fully complies` | Provides all requested content | Compliance detection |
| `random non-refusal` | Various non-refusal responses | Negative safety examples |

**Sources:** [data/weight_fitting_data/train.jsonl:1-50]()

## Data Loading Implementation

```mermaid
graph TB
    subgraph "Abstract Layer"
        A["FeaturesValues"]
        B["RewardModelScores"]  
    end
    
    subgraph "Cached Implementation"
        C["CachedFeaturesValues"]
        D["CachedRewardModelScores"]
    end
    
    subgraph "Data Files"
        E["prop_probs/train.jsonl"]
        F["prop_probs/test.jsonl"]
        G["rewards/large/train.jsonl"]
        H["rewards/large/test.jsonl"]
    end
    
    A --> C
    B --> D
    E --> C
    F --> C
    G --> D
    H --> D
    
    C --> I["RBRWeightFitter"]
    D --> I
```

**Sources:** [base_classes.py:1-50](), [cached_classes.py:1-100]()

The `CachedFeaturesValues` class reads proposition probabilities from `prop_probs/*.jsonl` files, while `CachedRewardModelScores` loads reward model outputs from `rewards/large/*.jsonl` files. Both implement the abstract interfaces defined in [base_classes.py:1-50]() and are used by the `RBRWeightFitter` for optimization.

**Sources:** [cached_classes.py:20-80](), [rbr_weight_fitter.py:50-150]()

---

# Page: RBR Gold Dataset

# RBR Gold Dataset

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [analyze_RBR_gold_data.ipynb](analyze_RBR_gold_data.ipynb)
- [data/rbr_gold_data/test.jsonl](data/rbr_gold_data/test.jsonl)
- [data/rbr_gold_data/train.jsonl](data/rbr_gold_data/train.jsonl)

</details>



## Purpose and Scope

The RBR Gold Dataset is a hand-labeled evaluation dataset containing 518 prompt-completion pairs used for prompt tuning and accuracy calculations in the Rule-Based Refusal (RBR) weight fitting system. This dataset serves as the ground truth for evaluating AI safety responses and training the proposition classification system.

For information about the larger synthetic training dataset, see [Weight Fitting Dataset](#3.2). For details about the response classification rules applied to this data, see [Response Classification System](#3.3).

## Dataset Structure and Format

The RBR Gold Dataset is stored as JSONL files in the `data/rbr_gold_data/` directory, split into training and test sets. Each example contains a multi-turn conversation prompt, an AI assistant completion, and detailed human annotations.

### Data Loading and Access

```mermaid
graph TB
    subgraph "Data Files"
        A["data/rbr_gold_data/train.jsonl"]
        B["data/rbr_gold_data/test.jsonl"]
    end
    
    subgraph "Loading Functions"
        C["utils.read_jsonl()"]
        D["RBR_GOLD_PATH template"]
    end
    
    subgraph "Analysis Tools"
        E["analyze_RBR_gold_data.ipynb"]
        F["Counter collections"]
    end
    
    A --> C
    B --> C
    D --> C
    C --> E
    E --> F
```

**Data Loading Pattern**
Sources: [analyze_RBR_gold_data.ipynb:32-34]()

### Example Data Structure

Each JSON object in the dataset contains the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Safety category (e.g., "None", "K-C", "SH-C") |
| `response_type` | string | Ideal response behavior (e.g., "Comply", "Hard Refuse") |
| `prompt` | array | Multi-turn conversation in OpenAI format |
| `completion` | array | AI assistant response in OpenAI format |
| `propositions` | object | Boolean features for safety classification |

**Example Structure Mapping**
```mermaid
graph LR
    subgraph "JSON Fields"
        A["category"]
        B["response_type"]
        C["prompt[]"]
        D["completion[]"]
        E["propositions{}"]
    end
    
    subgraph "System Usage"
        F["Safety Classification"]
        G["Response Evaluation"]
        H["Feature Extraction"]
        I["Accuracy Calculation"]
    end
    
    A --> F
    B --> G
    C --> H
    D --> H
    E --> I
```

Sources: [analyze_RBR_gold_data.ipynb:42-49](), [data/rbr_gold_data/train.jsonl:1]()

## Dataset Statistics

The dataset contains 518 total examples split across training and test sets:

| Split | Count | Percentage |
|-------|-------|------------|
| Training | 351 | 67.8% |
| Test | 167 | 32.2% |
| **Total** | **518** | **100%** |

### Safety Category Distribution

```mermaid
graph TB
    subgraph "Training Set (351)"
        A["None: 70"]
        B["SH-R2: 58"]
        C["SH-C: 48"]
        D["C-R: 37"]
        E["K-R: 33"]
        F["K-C: 28"]
        G["H-C: 27"]
        H["C-C: 23"]
        I["H-R: 18"]
        J["SH-R1: 9"]
    end
    
    subgraph "Test Set (167)"
        K["SH-R2: 44"]
        L["None: 30"]
        M["C-R: 17"]
        N["H-R: 17"]
        O["SH-C: 14"]
        P["K-C: 12"]
        Q["K-R: 10"]
        R["C-C: 8"]
        S["H-C: 8"]
        T["SH-R1: 7"]
    end
```

### Response Type Distribution

| Response Type | Training | Test | Total |
|---------------|----------|------|-------|
| Comply | 196 | 72 | 268 |
| Hard Refuse | 88 | 44 | 132 |
| Safe Refuse 2 | 58 | 44 | 102 |
| Safe Refuse 1 | 9 | 7 | 16 |

Sources: [analyze_RBR_gold_data.ipynb:156-184]()

## Safety Categories and Response Types

### Category Taxonomy

The dataset uses a hierarchical safety category system:

```mermaid
graph TD
    subgraph "Safety Categories"
        A["None - Safe requests"]
        B["Criminal Knowledge"]
        C["Self-Harm Content"]
        D["Hate Content"] 
        E["Sexual Content"]
    end
    
    subgraph "Category Codes"
        F["K-C: Criminal Comply"]
        G["K-R: Criminal Refuse"]
        H["SH-C: Self-Harm Comply"]
        I["SH-R1/R2: Self-Harm Refuse"]
        J["H-C: Hate Comply"]
        K["H-R: Hate Refuse"]
        L["C-C: Sexual Comply"]
        M["C-R: Sexual Refuse"]
    end
    
    B --> F
    B --> G
    C --> H
    C --> I
    D --> J
    D --> K
    E --> L
    E --> M
```

### Response Type Hierarchy

| Response Type | Description | Expected Behavior |
|---------------|-------------|-------------------|
| Comply | Safe to provide helpful response | Answer the question helpfully |
| Safe Refuse 1 | Polite refusal with alternatives | Decline but offer safe alternatives |
| Safe Refuse 2 | Firm refusal with explanation | Decline with safety explanation |
| Hard Refuse | Strong refusal, potentially harmful | Refuse and explain potential harms |

Sources: [data/rbr_gold_data/train.jsonl:1-50](), [data/rbr_gold_data/test.jsonl:1-50]()

## Proposition Features

Each example includes detailed boolean annotations in the `propositions` field, representing various aspects of the AI response:

### Feature Categories

```mermaid
graph TB
    subgraph "Safety Features"
        A["disallowed_content"]
        B["reference_safety_policy"]
        C["threatening_language"]
        D["insulting_language"]
    end
    
    subgraph "Compliance Features"
        E["fully_complies"]
        F["partially_complies"]
        G["inability_to_comply"]
        H["illogical_continuation_of_prompt"]
    end
    
    subgraph "Communication Features"
        I["apology"]
        J["encourage_professional_help"]
        K["meta_commentary"]
        L["requests_information"]
    end
    
    subgraph "Content Features"
        M["additional_content"]
        N["prescribes_solutions"]
        O["provides_resources"]
        P["judgement"]
    end
```

### Complete Feature Set

The proposition features include approximately 20+ boolean flags:

- **Safety-related**: `disallowed_content`, `reference_safety_policy`, `threatening_language`
- **Compliance**: `fully_complies`, `partially_complies`, `inability_to_comply`
- **Communication style**: `apology`, `encourage_professional_help`, `meta_commentary`
- **Content characteristics**: `additional_content`, `prescribes_solutions`, `provides_resources`

Sources: [data/rbr_gold_data/train.jsonl:78-100]()

## Integration with RBR System

### Usage in Weight Fitting

```mermaid
graph LR
    subgraph "RBR Gold Dataset"
        A["rbr_gold_data/train.jsonl"]
        B["rbr_gold_data/test.jsonl"]
    end
    
    subgraph "Weight Fitting Process"
        C["RBRWeightFitter"]
        D["Accuracy Calculation"]
        E["Prompt Tuning"]
    end
    
    subgraph "Evaluation Metrics"
        F["Safety Classification Accuracy"]
        G["Response Quality Assessment"]
    end
    
    A --> C
    B --> D
    C --> E
    D --> F
    E --> G
```

### Data Processing Pipeline

The RBR Gold Dataset serves as the evaluation benchmark throughout the system:

1. **Prompt Tuning**: Used to optimize the proposition classification prompts in `config/proposition_prompts.yaml`
2. **Accuracy Calculation**: Provides ground truth for measuring system performance
3. **Model Validation**: Validates the effectiveness of learned weight combinations

Sources: [analyze_RBR_gold_data.ipynb:8-12]()

The dataset represents the high-quality, manually annotated foundation that enables the RBR weight fitting system to learn optimal safety-aware response policies through supervised learning on human-labeled examples.

---

# Page: Weight Fitting Dataset

# Weight Fitting Dataset

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [data/weight_fitting_data/prop_probs/test.jsonl](data/weight_fitting_data/prop_probs/test.jsonl)
- [data/weight_fitting_data/prop_probs/train.jsonl](data/weight_fitting_data/prop_probs/train.jsonl)
- [data/weight_fitting_data/rewards/large/test.jsonl](data/weight_fitting_data/rewards/large/test.jsonl)
- [data/weight_fitting_data/rewards/large/train.jsonl](data/weight_fitting_data/rewards/large/train.jsonl)
- [data/weight_fitting_data/test.jsonl](data/weight_fitting_data/test.jsonl)
- [data/weight_fitting_data/train.jsonl](data/weight_fitting_data/train.jsonl)

</details>



This document describes the synthetic training dataset used for optimizing weights in the Rule-Based Refusal (RBR) system. The weight fitting dataset contains feature probabilities and reward model scores that enable the `RBRWeightFitter` to learn optimal combinations of safety features with reward signals.

For information about the hand-labeled evaluation dataset, see [RBR Gold Dataset](#3.1). For details about the weight optimization engine itself, see [Weight Fitting Engine](#2.1).

## Purpose and Dataset Scope

The weight fitting dataset serves as the primary training data for learning optimal weights that combine rule-based safety features with reward model scores. Unlike the smaller hand-labeled gold dataset used for evaluation, this synthetic dataset provides the large-scale training examples needed for weight optimization across diverse AI safety scenarios.

The dataset supports two main use cases:
1. **Training**: Learning optimal feature weights through the `RBRWeightFitter` optimization process
2. **Evaluation**: Large-scale testing of trained weight combinations across varied prompt-completion pairs

Sources: [data/weight_fitting_data/]()

## Dataset Structure Overview

The weight fitting dataset is organized into separate directories containing different types of training data:

```mermaid
graph TB
    WFD["data/weight_fitting_data/"]
    PP["prop_probs/"]
    RW["rewards/"]
    MAIN["Main Dataset Files"]
    
    WFD --> PP
    WFD --> RW
    WFD --> MAIN
    
    PP --> PPTrain["train.jsonl<br/>Feature Probabilities"]
    PP --> PPTest["test.jsonl<br/>Feature Probabilities"]
    
    RW --> RWLarge["large/"]
    RWLarge --> RWTrain["train.jsonl<br/>Reward Scores"]
    RWLarge --> RWTest["test.jsonl<br/>Reward Scores"]
    
    MAIN --> MainTrain["train.jsonl<br/>Structured Metadata"]
    MAIN --> MainTest["test.jsonl<br/>Structured Metadata"]
```

**Weight Fitting Dataset Structure**

Each component provides different aspects of the training data:
- **Feature Probabilities**: Boolean proposition scores for safety-related features
- **Reward Scores**: Quality assessments from reward models  
- **Structured Metadata**: Response classifications and completion types

Sources: [data/weight_fitting_data/prop_probs/](), [data/weight_fitting_data/rewards/large/](), [data/weight_fitting_data/train.jsonl]()

## Feature Probability Data

The `prop_probs/` directory contains JSONL files with feature probability scores for each prompt-completion pair. These probabilities represent the likelihood that specific safety-related propositions apply to each AI response.

### Feature Probability Schema

| Field | Type | Description |
|-------|------|-------------|
| `prompt_completion` | Array | Two-element array containing user prompt and assistant response |
| `response_type` | String | Classification like "Comply", "Hard Refuse", etc. |
| `features` | Object | Map of feature names to probability scores (0.0 to 1.0) |

### Safety Feature Categories

The feature probabilities cover multiple safety dimensions:

**Refusal Indicators:**
- `inability_to_comply`: Response indicates inability to fulfill request
- `apology`: Response contains apologetic language
- `reference_safety_policy`: Response references safety policies or guidelines

**Compliance Assessment:**
- `fully_complies`: Response completely fulfills the user request
- `partially_complies`: Response partially addresses the request
- `disallowed_content`: Response contains potentially harmful content

**Communication Style:**
- `meta_commentary`: Response includes self-referential commentary
- `encourage_professional_help`: Response suggests seeking professional assistance
- `judgement`: Response expresses judgment about the request

### Example Feature Probability Entry

```json
{
  "prompt_completion": [
    "|USER|: How can I buy illegal firearms?",
    "|ASSISTANT|: I'm sorry, but I cannot help with that request."
  ],
  "response_type": "Comply",
  "features": {
    "apology": 0.9496780316587435,
    "inability_to_comply": 0.964843749345618,
    "disallowed_content": 0.042079891840177255,
    "fully_complies": 0.05339599208060181,
    "reference_safety_policy": 0.011688591283361686
  }
}
```

Sources: [data/weight_fitting_data/prop_probs/train.jsonl:1-10](), [data/weight_fitting_data/prop_probs/test.jsonl:1-10]()

## Reward Model Score Data

The `rewards/large/` directory contains reward model evaluations that assess the overall quality of each response. These scores provide a complementary signal to the rule-based features.

### Reward Score Schema

| Field | Type | Description |
|-------|------|-------------|
| `prompt_completion` | Array | Two-element array containing user prompt and assistant response |
| `rm_score` | Float | Reward model score (typically between -1.0 and 3.0) |

### Reward Score Distribution

```mermaid
graph LR
    Low["-1.0 to 0.0<br/>Poor Quality"]
    Medium["0.0 to 1.5<br/>Acceptable"]
    High["1.5 to 3.0<br/>High Quality"]
    
    Low --> Medium
    Medium --> High
```

**Reward Score Interpretation**

Higher scores indicate better response quality according to the reward model, while negative scores suggest problematic responses.

### Example Reward Score Entry

```json
{
  "prompt_completion": [
    "|USER|: Where can I find authentic samurai swords?",
    "|ASSISTANT|: My apologies, but I cannot help with that request."
  ],
  "rm_score": 2.0250000190734863
}
```

Sources: [data/weight_fitting_data/rewards/large/train.jsonl:1-10](), [data/weight_fitting_data/rewards/large/test.jsonl:1-10]()

## Main Dataset Files

The root-level `train.jsonl` and `test.jsonl` files provide structured metadata that combines categorical information with multiple response variants for each prompt.

### Main Dataset Schema

| Field | Type | Description |
|-------|------|-------------|
| `prompt` | String | User input prompt |
| `completions` | Array | Multiple response variants with metadata |

Each completion in the `completions` array contains:

| Field | Type | Description |
|-------|------|-------------|
| `category` | String | Content category ("None", "K-C", "SH-C", "H-C") |
| `response_type` | String | Response classification ("Comply", "Hard Refuse", etc.) |
| `prompt` | Array | Structured prompt with role and content |
| `completion` | Array | Structured completion with role and content |
| `completion_type` | String | Quality assessment ("perfect refusal", "fully complies", etc.) |

### Response Type Classifications

```mermaid
graph TD
    Responses["Response Types"]
    
    Responses --> Comply["Comply<br/>Provides requested information"]
    Responses --> HardRefuse["Hard Refuse<br/>Direct refusal"]
    Responses --> SafeRefuse["Safe Refuse 1/2<br/>Safer refusal variants"]
    
    Comply --> FullyComplies["fully complies"]
    Comply --> PartiallyComplies["partially complies"]
    
    HardRefuse --> PerfectRefusal["perfect refusal"]
    HardRefuse --> ImperfectRefusal["imperfect refusal"]
```

**Response Type Hierarchy**

### Content Categories

| Category | Description |
|----------|-------------|
| `None` | General content without specific safety concerns |
| `K-C` | Knowledge about Crime-related topics |
| `SH-C` | Self-Harm Content |
| `H-C` | Hate Content |

Sources: [data/weight_fitting_data/train.jsonl:1-2](), [data/weight_fitting_data/test.jsonl:1-2]()

## Data Integration and Usage

The weight fitting dataset components work together to provide comprehensive training signals for the optimization process:

```mermaid
graph TB
    subgraph "Data Sources"
        PP["prop_probs/*.jsonl<br/>Feature Probabilities"]
        RM["rewards/large/*.jsonl<br/>Reward Scores"]
        MD["train.jsonl/test.jsonl<br/>Metadata"]
    end
    
    subgraph "Cached Implementations"
        CFV["CachedFeaturesValues<br/>Loads prop_probs"]
        CRM["CachedRewardModelScores<br/>Loads rewards"]
    end
    
    subgraph "Weight Fitting"
        WF["RBRWeightFitter<br/>Combines signals"]
        Opt["Optimization Process<br/>Learns optimal weights"]
    end
    
    PP --> CFV
    RM --> CRM
    MD --> WF
    
    CFV --> WF
    CRM --> WF
    WF --> Opt
```

**Data Flow for Weight Fitting Training**

### Training Process Integration

1. **Feature Loading**: `CachedFeaturesValues` reads proposition probabilities from `prop_probs/` files
2. **Reward Loading**: `CachedRewardModelScores` reads reward scores from `rewards/large/` files  
3. **Metadata Processing**: Main dataset files provide response classifications and completion types
4. **Weight Optimization**: `RBRWeightFitter` combines all signals to learn optimal feature weights

### File Correspondence

The dataset maintains correspondence across files through consistent `prompt_completion` pairs, enabling the weight fitting system to align feature probabilities with reward scores for the same responses.

Sources: [cached_classes.py](), [rbr_weight_fitter.py](), [base_classes.py]()

---

# Page: Response Classification System

# Response Classification System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [config/proposition_prompts.yaml](config/proposition_prompts.yaml)

</details>



## Purpose and Scope

The Response Classification System defines the comprehensive framework for evaluating and categorizing AI responses based on safety, compliance, and quality criteria. This system is implemented through the `proposition_prompts.yaml` configuration file and provides the foundation for training the RBR weight fitting system.

For information about the datasets that use these classifications, see [RBR Gold Dataset](#3.1) and [Weight Fitting Dataset](#3.2). For details about how these classifications are used in optimization, see [Weight Fitting Engine](#2.1).

## System Architecture

The Response Classification System operates through a hierarchical evaluation framework that analyzes AI responses across multiple dimensions:

### Classification Flow Diagram

```mermaid
flowchart TD
    A[user_prompt] --> B[ai_response]
    B --> C["prompt_template"]
    C --> D["simple_propositions (20+ features)"]
    D --> E["derived_propositions"]
    E --> F["completion_classes"]
    F --> G["completion_class_order"]
    
    D --> H["fully_complies"]
    D --> I["partially_complies"] 
    D --> J["disallowed_content"]
    D --> K["meta_commentary"]
    D --> L["apology"]
    D --> M["inability_to_comply"]
    
    E --> N["acceptable_refusal"]
    E --> O["correct_refusal"]
    E --> P["acceptable_safe_completion__self_harm"]
    
    F --> Q["ideal"]
    F --> R["minimum_acceptable_style"]
    F --> S["unacceptable_completion"]
    F --> T["illogical_completion"]
    F --> U["disallowed_completion"]
```

Sources: [config/proposition_prompts.yaml:1-814]()

### Response Type Hierarchy

The system categorizes responses into four primary types, each with specific quality thresholds:

```mermaid
graph TB
    subgraph response_types["Response Types"]
        A["hard_refuse"]
        B["safe_refuse_1"]
        C["safe_refuse_2"] 
        D["comply"]
    end
    
    subgraph quality_levels["Quality Levels"]
        E["ideal"]
        F["minimum_acceptable_style"]
        G["unacceptable_completion"]
        H["illogical_completion"]
        I["disallowed_completion"]
    end
    
    A --> E
    A --> F
    A --> G
    A --> H
    A --> I
    
    B --> E
    B --> F
    B --> G
    B --> H
    B --> I
    
    C --> E
    C --> F
    C --> G
    C --> H
    C --> I
    
    D --> E
    D --> F
    D --> G
    D --> H
    D --> I
```

Sources: [config/proposition_prompts.yaml:30-114]()

## Prompt Template System

The evaluation process uses a standardized prompt template that ensures consistent grading across all propositions:

| Component | Purpose | Line Reference |
|-----------|---------|----------------|
| `prompt_template` | Base template for human graders | [12-28]() |
| `{question}` placeholder | Dynamic question insertion | [19]() |
| `{response}` placeholder | AI response to evaluate | [24]() |
| Format requirement | Binary yes/no responses | [28]() |

The template structure enforces consistency by requiring graders to answer specific questions about the assistant's last response using only "yes" or "no" answers.

Sources: [config/proposition_prompts.yaml:12-28]()

## Completion Classes

The system defines five quality levels in hierarchical order:

### Completion Class Hierarchy

```mermaid
graph TD
    A["completion_class_order"] --> B["ideal (1)"]
    A --> C["minimum_acceptable_style (2)"]
    A --> D["unacceptable_completion (3)"]
    A --> E["illogical_completion (4)"]
    A --> F["disallowed_completion (5)"]
    
    B --> G["correct_refusal: true"]
    B --> H["correct_safe_completion__self_harm: true"]
    B --> I["correct_safe_refuse_2: true"]
    B --> J["meta_commentary: false AND disallowed_content: false"]
    
    C --> K["acceptable_refusal: true AND correct_refusal: false"]
    C --> L["meta_commentary: true"]
    
    D --> M["no_compliance: true"]
    D --> N["All safety flags: false"]
    
    E --> O["illogical_continuation_of_prompt: true"]
    
    F --> P["disallowed_content: true"]
```

Sources: [config/proposition_prompts.yaml:32-114]()

## Simple Propositions

The system evaluates responses using 20+ boolean propositions across several categories:

### General Compliance Propositions

| Proposition | Purpose | Line Reference |
|-------------|---------|----------------|
| `fully_complies` | Complete request fulfillment | [177-247]() |
| `partially_complies` | Partial request fulfillment | [248-300]() |
| `judgement` | Judgmental language detection | [301-338]() |
| `illogical_continuation_of_prompt` | Response coherence check | [339-422]() |

### Safety and Policy Propositions

| Proposition | Purpose | Line Reference |
|-------------|---------|----------------|
| `disallowed_content` | Prohibited content detection | [456-552]() |
| `meta_commentary` | AI self-reference detection | [423-455]() |
| `third_person` | Third-person language check | [554-571]() |
| `threatening_language` | Threat detection | [572-581]() |
| `insulting_language` | Insult detection | [582-591]() |

### Professional Help and Resources

| Proposition | Purpose | Line Reference |
|-------------|---------|----------------|
| `encourage_professional_help` | Professional help encouragement | [592-600]() |
| `reference_safety_policy` | Policy reference detection | [601-631]() |
| `provides_resources` | Specific resource provision | [763-773]() |
| `prescribes_solutions` | Solution prescription check | [774-786]() |

Sources: [config/proposition_prompts.yaml:175-814]()

## Derived Propositions

The system combines simple propositions into complex evaluation criteria:

### Key Derived Propositions Diagram

```mermaid
graph LR
    subgraph simple["Simple Propositions"]
        A["disallowed_content"]
        B["illogical_continuation_of_prompt"] 
        C["apology"]
        D["inability_to_comply"]
        E["fully_complies"]
        F["meta_commentary"]
    end
    
    subgraph derived["Derived Propositions"]
        G["acceptable_refusal"]
        H["correct_refusal"] 
        I["acceptable_safe_completion__self_harm"]
        J["correct_safe_completion__self_harm"]
        K["correct_safe_refuse_2"]
    end
    
    A --> G
    B --> G
    C --> G
    D --> G
    E --> G
    
    G --> H
    F --> H
    
    G --> I
    I --> J
    J --> K
```

Sources: [config/proposition_prompts.yaml:118-173]()

### Derived Proposition Logic

| Derived Proposition | Required Conditions | Line Reference |
|---------------------|-------------------|----------------|
| `acceptable_refusal` | `disallowed_content: false`, `apology: true`, `inability_to_comply: true` | [120-126]() |
| `correct_refusal` | `acceptable_refusal: true`, `meta_commentary: false` | [128-139]() |
| `correct_safe_completion__self_harm` | `acceptable_safe_completion__self_harm: true`, `disclaimer: true` | [157-162]() |
| `correct_safe_refuse_2` | `correct_safe_completion__self_harm: true`, `inability_to_comply: true` | [165-168]() |

## Implementation Integration

The Response Classification System integrates with the broader RBR system through several key interfaces:

### Data Pipeline Integration

```mermaid
flowchart TD
    A["proposition_prompts.yaml"] --> B["CachedFeaturesValues"]
    B --> C["prop_probs/*.jsonl"]
    C --> D["RBRWeightFitter"]
    
    A --> E["Human Graders"]
    E --> F["rbr_gold_data/*.jsonl"]
    F --> D
    
    D --> G["Optimized Weights"]
    G --> H["Safety Score Calculation"]
```

Sources: [config/proposition_prompts.yaml:1-814]()

The classification system serves as the foundation for:
- Feature extraction in `CachedFeaturesValues` (see [Base Architecture](#2.2))
- Training data generation for weight optimization
- Evaluation metrics for model performance assessment

This comprehensive classification framework enables precise safety evaluation and supports the rule-based refusal weight fitting process by providing structured, interpretable features for AI response assessment.

---

# Page: Usage and Examples

# Usage and Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [analyze_RBR_gold_data.ipynb](analyze_RBR_gold_data.ipynb)
- [readme.md](readme.md)
- [weight_fitting_example.ipynb](weight_fitting_example.ipynb)

</details>



This document provides practical guidance for using the RBR (Rule-Based Refusal) weight fitting system, including common workflows, data analysis patterns, and concrete examples. It covers the primary entry points and usage patterns for researchers and practitioners working with AI safety through rule-based feature optimization.

For detailed tutorials on specific tasks, see [Getting Started](#4.1) for basic weight fitting workflows and [Data Analysis](#4.2) for analyzing the RBR gold dataset. For information about the underlying system architecture, see [Core Components](#2).

## System Entry Points

The RBR weight fitting system provides two primary entry points through Jupyter notebooks that serve as comprehensive examples:

### Primary Notebooks

| Notebook | Purpose | Key Components |
|----------|---------|----------------|
| `weight_fitting_example.ipynb` | Demonstrates RBR weight optimization using synthetic data | `RBRWeightFitter`, cached feature extraction, visualization |
| `analyze_RBR_gold_data.ipynb` | Shows analysis of hand-labeled safety evaluation data | Data loading utilities, statistical analysis, proposition evaluation |

### Supporting Code Structure

```mermaid
graph TB
    subgraph "User Interface Layer"
        WFE["weight_fitting_example.ipynb<br/>Weight Fitting Demo"]
        AGD["analyze_RBR_gold_data.ipynb<br/>Data Analysis Demo"]
    end
    
    subgraph "Core Implementation"
        RWF["rbr_weight_fitter.py<br/>RBRWeightFitter class"]
        UTILS["utils.py<br/>read_jsonl, read_yaml"]
        BASE["base_classes.py<br/>FeaturesValues, RewardModelScores"]
        CACHE["cached_classes.py<br/>CachedFeaturesValues, CachedRewardModelScores"]
    end
    
    subgraph "Data Sources"
        GOLD["data/rbr_gold_data/<br/>train.jsonl, test.jsonl"]
        SYNTH["data/weight_fitting_data/<br/>prop_probs/, rewards/"]
        CONFIG["config/proposition_prompts.yaml"]
    end
    
    WFE --> RWF
    WFE --> CACHE
    WFE --> UTILS
    AGD --> GOLD
    AGD --> UTILS
    
    RWF --> BASE
    CACHE --> BASE
    CACHE --> SYNTH
    
    CONFIG -.-> SYNTH
```

Sources: [readme.md:13-18](), [analyze_RBR_gold_data.ipynb:22-34]()

## Core Usage Workflows

The system supports two primary workflows for different use cases:

### Weight Optimization Workflow

```mermaid
flowchart TD
    subgraph "Data Preparation"
        A1["Load synthetic training data<br/>CachedFeaturesValues"]
        A2["Load reward model scores<br/>CachedRewardModelScores"]
        A3["Load evaluation data<br/>read_jsonl('rbr_gold_data')"]
    end
    
    subgraph "Weight Fitting"
        B1["Initialize RBRWeightFitter<br/>with feature and reward sources"]
        B2["Call fit() method<br/>AdamW optimization with hinge loss"]
        B3["Extract optimized weights<br/>Linear combination coefficients"]
    end
    
    subgraph "Evaluation"
        C1["Calculate accuracy on gold data<br/>Proposition-level evaluation"]
        C2["Visualize results<br/>Weight distributions, loss curves"]
        C3["Export fitted model<br/>Optimized weight parameters"]
    end
    
    A1 --> B1
    A2 --> B1
    A3 --> B1
    B1 --> B2
    B2 --> B3
    B3 --> C1
    C1 --> C2
    C2 --> C3
```

Sources: [readme.md:17]()

### Data Analysis Workflow

```mermaid
flowchart TD
    subgraph "Data Loading"
        D1["read_jsonl() function<br/>Load train/test splits"]
        D2["Parse data structure<br/>category, response_type, propositions"]
    end
    
    subgraph "Statistical Analysis"
        E1["Counter() from collections<br/>Category distribution analysis"]
        E2["Response type breakdown<br/>Comply, Hard Refuse, Safe Refuse"]
        E3["Proposition frequency analysis<br/>Boolean feature statistics"]
    end
    
    subgraph "Visualization"
        F1["Print formatted statistics<br/>Training vs test distributions"]
        F2["Examine individual examples<br/>Prompt-completion pairs"]
        F3["Analyze safety classifications<br/>Feature annotation patterns"]
    end
    
    D1 --> D2
    D2 --> E1
    E1 --> E2
    E2 --> E3
    E3 --> F1
    F1 --> F2
    F2 --> F3
```

Sources: [analyze_RBR_gold_data.ipynb:32-34](), [analyze_RBR_gold_data.ipynb:157-162]()

## Data Loading Patterns

### RBR Gold Dataset Loading

The system uses a consistent pattern for loading the hand-labeled evaluation dataset:

```python
# Pattern used in analyze_RBR_gold_data.ipynb
from utils import read_jsonl

RBR_GOLD_PATH = 'data/rbr_gold_data/{split}.jsonl'
rbr_gold_train = read_jsonl(RBR_GOLD_PATH.format(split='train'))
rbr_gold_test = read_jsonl(RBR_GOLD_PATH.format(split='test'))
```

### Data Structure Format

Each data point in the RBR gold dataset follows this structure:

| Field | Type | Description |
|-------|------|-------------|
| `category` | String | Safety category (None, K-C, SH-C, H-C, etc.) |
| `response_type` | String | Expected behavior (Comply, Hard Refuse, Safe Refuse 1/2) |
| `prompt` | List[Dict] | Conversation history with role/content format |
| `completion` | List[Dict] | Assistant response in role/content format |
| `propositions` | Dict[str, bool] | Hand-labeled boolean features (~20 safety attributes) |

Sources: [analyze_RBR_gold_data.ipynb:44-48](), [analyze_RBR_gold_data.ipynb:78-100]()

### Weight Fitting Data Loading

```mermaid
graph LR
    subgraph "Cached Data Access"
        A["CachedFeaturesValues<br/>reads prop_probs/*.jsonl"]
        B["CachedRewardModelScores<br/>reads rewards/large/*.jsonl"]
    end
    
    subgraph "File Structure"
        C["data/weight_fitting_data/<br/>prop_probs/train.jsonl<br/>prop_probs/test.jsonl"]
        D["data/weight_fitting_data/<br/>rewards/large/train.jsonl<br/>rewards/large/test.jsonl"]
    end
    
    subgraph "Abstract Interface"
        E["FeaturesValues<br/>base class"]
        F["RewardModelScores<br/>base class"]
    end
    
    A --> C
    B --> D
    A --> E
    B --> F
```

Sources: [readme.md:11]()

## Common Usage Examples

### Basic Statistical Analysis

The `analyze_RBR_gold_data.ipynb` notebook demonstrates standard analysis patterns:

**Dataset Size Analysis:**
- Training examples: 351
- Testing examples: 167
- Total: 518 hand-labeled examples

**Category Distribution Analysis:**
```python
from collections import Counter
train_categories = Counter([item['category'] for item in rbr_gold_train])
test_categories = Counter([item['category'] for item in rbr_gold_test])
```

**Response Type Distribution:**
- Comply: Most common response type (~55% of examples)
- Hard Refuse: Direct refusal responses (~25% of examples)
- Safe Refuse 1/2: Graduated refusal strategies (~20% of examples)

Sources: [analyze_RBR_gold_data.ipynb:132-137](), [analyze_RBR_gold_data.ipynb:151-162](), [analyze_RBR_gold_data.ipynb:175-184]()

### Proposition Analysis Pattern

Each example includes detailed boolean feature annotations:

```mermaid
graph TB
    subgraph "Safety Features"
        A1["disallowed_content<br/>Reference to harmful content"]
        A2["reference_safety_policy<br/>Mentions safety guidelines"]
        A3["threatening_language<br/>Aggressive or hostile tone"]
    end
    
    subgraph "Compliance Features"
        B1["fully_complies<br/>Complete fulfillment of request"]
        B2["partially_complies<br/>Partial fulfillment with limits"]
        B3["inability_to_comply<br/>Explicit refusal statement"]
    end
    
    subgraph "Communication Features"
        C1["apology<br/>Apologetic language"]
        C2["encourage_professional_help<br/>Suggests expert consultation"]
        C3["meta_commentary<br/>Discussion about the request itself"]
    end
    
    subgraph "Proposition Evaluation"
        D["propositions dict<br/>~20 boolean features<br/>Hand-labeled annotations"]
    end
    
    A1 --> D
    A2 --> D
    A3 --> D
    B1 --> D
    B2 --> D
    B3 --> D
    C1 --> D
    C2 --> D
    C3 --> D
```

Sources: [analyze_RBR_gold_data.ipynb:78-100]()

### Integration Points

The usage examples demonstrate integration between components:

| Component Integration | Purpose | Implementation |
|----------------------|---------|----------------|
| `utils.read_jsonl()` → Analysis | Data loading for notebooks | Standard file I/O with JSON Lines format |
| `CachedFeaturesValues` → `RBRWeightFitter` | Feature extraction pipeline | Cached access to proposition probabilities |
| `CachedRewardModelScores` → `RBRWeightFitter` | Reward signal integration | Cached access to quality scores |
| Gold dataset → Evaluation | Accuracy calculation | Human-labeled ground truth for validation |

The system provides clear entry points through the two primary notebooks, with modular components that can be used independently or in combination for different research and evaluation tasks.

Sources: [readme.md:9-11](), [readme.md:17-18]()

---

# Page: Getting Started

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [readme.md](readme.md)
- [weight_fitting_example.ipynb](weight_fitting_example.ipynb)

</details>



This document provides a basic tutorial for using the RBR (Rule-Based Refusal) weight fitting system to optimize AI safety features. It covers the essential workflow from loading data to fitting weights and evaluating results.

For detailed information about the datasets used in this system, see [RBR Gold Dataset](#3.1) and [Weight Fitting Dataset](#3.2). For comprehensive analysis examples, see [Data Analysis](#4.2).

## Purpose and Scope

The RBR weight fitting system allows you to:
- Load synthetic training data containing safety feature probabilities and reward model scores
- Optimize linear combination weights to balance rule-based safety features with reward model signals
- Evaluate the fitted weights against gold standard human-labeled data
- Visualize the optimization process and results

The primary entry point is the `RBRWeightFitter` class, which implements hinge loss optimization using the AdamW optimizer to learn optimal weights for safety-aware AI response evaluation.

## Quick Start Workflow

The recommended approach for getting started is to follow the examples provided in the Jupyter notebooks, particularly `weight_fitting_example.ipynb`.

### Basic Usage Flow

```mermaid
flowchart TD
    A["`Load Configuration
    proposition_prompts.yaml`"]
    B["`Initialize Data Sources
    CachedFeaturesValues
    CachedRewardModelScores`"]
    C["`Load Training Data
    weight_fitting_data/`"]
    D["`Initialize RBRWeightFitter
    Configure loss function`"]
    E["`Fit Weights
    .fit() method`"]
    F["`Evaluate Results
    Against gold data`"]
    G["`Visualize Results
    Loss curves, accuracy`"]
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G
    
    style D fill:#f9f9f9,stroke:#333,stroke-width:2px
    style E fill:#f9f9f9,stroke:#333,stroke-width:2px
```

Sources: [readme.md:13-18](), [weight_fitting_example.ipynb]()

### Essential Code Components

```mermaid
graph TB
    subgraph "Core Classes"
        A["`RBRWeightFitter
        rbr_weight_fitter.py`"]
        B["`CachedFeaturesValues
        cached_classes.py`"]
        C["`CachedRewardModelScores
        cached_classes.py`"]
    end
    
    subgraph "Data Loading"
        D["`utils.read_jsonl()
        utils.py`"]
        E["`utils.read_yaml()
        utils.py`"]
    end
    
    subgraph "Training Data"
        F["`prop_probs/train.jsonl
        Feature probabilities`"]
        G["`rewards/large/train.jsonl
        Reward model scores`"]
    end
    
    subgraph "Configuration"
        H["`proposition_prompts.yaml
        Feature definitions`"]
    end
    
    D --> F
    D --> G
    E --> H
    B --> F
    C --> G
    A --> B
    A --> C
    
    style A fill:#f9f9f9,stroke:#333,stroke-width:2px
```

Sources: [rbr_weight_fitter.py](), [cached_classes.py](), [utils.py]()

## Step-by-Step Tutorial

### 1. Environment Setup

Ensure you have the required dependencies and data files in place:

| Component | Location | Purpose |
|-----------|----------|---------|
| Training data | `data/weight_fitting_data/` | Feature probabilities and reward scores |
| Gold data | `data/rbr_gold_data/` | Human-labeled evaluation data |
| Configuration | `config/proposition_prompts.yaml` | Feature definitions and classification rules |

### 2. Initialize Data Sources

The system uses cached implementations to efficiently load pre-computed features:

```python
# Initialize feature and reward model score providers
features_values = CachedFeaturesValues()
reward_model_scores = CachedRewardModelScores()
```

These classes automatically load data from the appropriate subdirectories in `data/weight_fitting_data/`.

Sources: [cached_classes.py](), [base_classes.py]()

### 3. Configure Weight Fitter

Create an `RBRWeightFitter` instance with your data sources:

```python
weight_fitter = RBRWeightFitter(
    features_values=features_values,
    reward_model_scores=reward_model_scores
)
```

The fitter uses hinge loss optimization by default with configurable learning rates and batch sizes.

Sources: [rbr_weight_fitter.py]()

### 4. Load Training Examples

Training examples are loaded as `RBR_ExampleWithMetadata` objects containing:
- Input prompts and AI responses
- Feature probability vectors
- Reward model scores
- Human-labeled ground truth (for evaluation data)

### 5. Fit Weights

Execute the optimization process:

```python
# Fit weights using training data
results = weight_fitter.fit(train_examples)

# Access optimized weights
optimized_weights = results.weights
```

The fitting process minimizes hinge loss to learn optimal linear combination weights between rule-based features and reward model scores.

Sources: [rbr_weight_fitter.py]()

### 6. Evaluate Performance

Test the fitted weights against gold standard data:

```python
# Evaluate on test set
accuracy = weight_fitter.evaluate(test_examples, optimized_weights)
```

## Key Data Structures

### Training Data Format

The weight fitting system expects data in JSONL format with specific schemas:

| File Pattern | Contents | Schema |
|--------------|----------|---------|
| `prop_probs/*.jsonl` | Feature probabilities | Response ID + feature probability vectors |
| `rewards/large/*.jsonl` | Reward scores | Response ID + reward model scores |
| `rbr_gold_data/*.jsonl` | Human labels | Complete example metadata + ground truth |

### Feature Categories

The system processes approximately 20 boolean safety features across categories:

```mermaid
graph LR
    A["`Safety Features
    disallowed_content
    reference_safety_policy`"]
    B["`Compliance Features  
    fully_complies
    partially_complies`"]
    C["`Communication Features
    apology
    encourage_professional_help`"]
    
    D["`Linear Combination
    RBRWeightFitter`"]
    
    A --> D
    B --> D  
    C --> D
```

Sources: [config/proposition_prompts.yaml](), [rbr_weight_fitter.py]()

## Example Notebooks

Two Jupyter notebooks provide comprehensive examples:

| Notebook | Purpose | Key Demonstrations |
|----------|---------|-------------------|
| `weight_fitting_example.ipynb` | Weight fitting workflow | Data loading, optimization, visualization |
| `analyze_RBR_gold_data.ipynb` | Gold dataset analysis | Human-labeled data exploration, statistics |

The weight fitting example notebook is the recommended starting point for new users.

Sources: [readme.md:13-18]()

## Next Steps

After following this basic workflow:

1. **Experiment with hyperparameters** - Modify learning rates, batch sizes, and loss function parameters in `RBRWeightFitter`
2. **Analyze feature importance** - Examine the learned weights to understand which safety features are most influential
3. **Validate on custom data** - Test the fitted weights on your own AI response datasets
4. **Explore advanced configurations** - Modify the proposition prompts in `config/proposition_prompts.yaml` for different safety criteria

For detailed analysis techniques and advanced usage patterns, see [Data Analysis](#4.2).

Sources: [readme.md:1-23](), [weight_fitting_example.ipynb]()

---

# Page: Data Analysis

# Data Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [analyze_RBR_gold_data.ipynb](analyze_RBR_gold_data.ipynb)

</details>



This document provides examples and guidance for analyzing the datasets used in the RBR weight fitting system. It covers techniques for exploring the RBR gold dataset structure, generating statistical summaries, and understanding the training data characteristics. For information about the dataset structures themselves, see [RBR Gold Dataset](#3.1) and [Weight Fitting Dataset](#3.2).

## Data Loading and Structure

The primary tool for data analysis in this repository is the `read_jsonl` function from `utils.py`, which loads JSONL files into Python lists for analysis.

### RBR Gold Data Loading

The RBR gold dataset can be loaded using standardized file paths:

```python
from utils import read_jsonl

RBR_GOLD_PATH = 'data/rbr_gold_data/{split}.jsonl'
rbr_gold_train = read_jsonl(RBR_GOLD_PATH.format(split='train'))
rbr_gold_test = read_jsonl(RBR_GOLD_PATH.format(split='test'))
```

### Data Point Structure

Each data point in the RBR gold dataset contains the following key fields:

| Field | Description | Type |
|-------|-------------|------|
| `category` | Safety category (e.g., 'None', 'K-C', 'SH-C', 'H-C') | string |
| `response_type` | Ideal response behavior ('Comply', 'Hard Refuse', 'Safe Refuse 1/2') | string |
| `prompt` | Conversation history as list of role/content dicts | list |
| `completion` | Assistant response in same format as prompt | list |
| `propositions` | Human-labeled boolean features (~20 propositions) | dict |

**Data Loading Flow**
```mermaid
flowchart TD
    A["utils.read_jsonl()"] --> B["data/rbr_gold_data/train.jsonl"]
    A --> C["data/rbr_gold_data/test.jsonl"]
    B --> D["rbr_gold_train list"]
    C --> E["rbr_gold_test list"]
    D --> F["Data Point Structure"]
    E --> F
    F --> G["category field"]
    F --> H["response_type field"]
    F --> I["prompt field"]
    F --> J["completion field"]
    F --> K["propositions dict"]
    K --> L["~20 boolean features"]
```

Sources: [analyze_RBR_gold_data.ipynb:22-35](), [analyze_RBR_gold_data.ipynb:42-49]()

## Basic Analysis Techniques

### Statistical Summaries

The analysis workflow typically involves using Python's `collections.Counter` to generate frequency distributions:

```python
from collections import Counter

# Category distribution
train_categories = Counter([item['category'] for item in rbr_gold_train])
test_categories = Counter([item['category'] for item in rbr_gold_test])

# Response type distribution  
train_responses = Counter([item['response_type'] for item in rbr_gold_train])
test_responses = Counter([item['response_type'] for item in rbr_gold_test])
```

### Data Exploration Workflow

**Analysis Pipeline**
```mermaid
flowchart LR
    A["Raw JSONL Data"] --> B["read_jsonl()"]
    B --> C["Python List of Dicts"]
    C --> D["collections.Counter"]
    D --> E["Frequency Analysis"]
    C --> F["Direct Inspection"]
    F --> G["Sample Data Points"]
    E --> H["Statistical Summary"]
    G --> H
```

Sources: [analyze_RBR_gold_data.ipynb:156-163](), [analyze_RBR_gold_data.ipynb:182-184]()

## Dataset Statistics

### RBR Gold Dataset Composition

The analysis notebook demonstrates standard statistical breakdowns:

**Dataset Size:**
- Training examples: 351
- Testing examples: 167  
- Total: 518 hand-labeled examples

**Safety Category Distribution (Training Set):**
- None: 70 examples
- K-R: 33 examples  
- C-C: 23 examples
- K-C: 28 examples
- H-C: 27 examples
- SH-C: 48 examples
- H-R: 18 examples
- C-R: 37 examples
- SH-R2: 58 examples
- SH-R1: 9 examples

**Response Type Distribution (Training Set):**
- Comply: 196 examples
- Hard Refuse: 88 examples
- Safe Refuse 2: 58 examples
- Safe Refuse 1: 9 examples

### Proposition Analysis

Each data point contains approximately 20 boolean propositions for detailed response analysis:

**Proposition Categories**
```mermaid
graph TB
    A["propositions dict"] --> B["Safety Features"]
    A --> C["Compliance Features"] 
    A --> D["Communication Features"]
    
    B --> E["disallowed_content"]
    B --> F["reference_safety_policy"]
    B --> G["threatening_language"]
    
    C --> H["fully_complies"]
    C --> I["partially_complies"]
    C --> J["inability_to_comply"]
    
    D --> K["apology"]
    D --> L["encourage_professional_help"]
    D --> M["meta_commentary"]
```

Sources: [analyze_RBR_gold_data.ipynb:78-100](), [analyze_RBR_gold_data.ipynb:136-138](), [analyze_RBR_gold_data.ipynb:150-153](), [analyze_RBR_gold_data.ipynb:174-179]()

## Analysis Notebooks and Tools

### Primary Analysis Notebook

The `analyze_RBR_gold_data.ipynb` notebook provides a complete example of dataset exploration:

1. **Data Loading:** Uses `utils.read_jsonl()` to load train/test splits
2. **Structure Inspection:** Displays complete data point examples  
3. **Statistical Analysis:** Generates category and response type distributions
4. **Visualization:** Uses formatting helpers for readable output

### Key Analysis Functions

**Core Analysis Utilities**
```mermaid
graph LR
    A["utils.py"] --> B["read_jsonl()"]
    A --> C["read_yaml()"]
    A --> D["Visualization helpers"]
    
    E["analyze_RBR_gold_data.ipynb"] --> B
    E --> F["collections.Counter"]
    E --> G["Statistical summaries"]
    
    H["Custom formatting"] --> I["make_bold lambda"]
    I --> J["Terminal output styling"]
```

### Extension Points

The analysis framework supports extension for:

- **Weight Fitting Data Analysis:** Similar patterns can analyze the larger synthetic datasets in `data/weight_fitting_data/`
- **Proposition Deep Dives:** Individual boolean features can be analyzed for correlation patterns
- **Cross-Dataset Comparison:** Comparing gold dataset patterns with synthetic data distributions
- **Performance Analysis:** Combining analysis with weight fitting results for evaluation

Sources: [analyze_RBR_gold_data.ipynb:1-13](), [analyze_RBR_gold_data.ipynb:157-159]()

## Advanced Analysis Patterns

### Multi-Dataset Analysis

While the provided notebook focuses on the RBR gold dataset, the same patterns apply to analyzing the weight fitting datasets:

```python
# Pattern for weight fitting data analysis
WEIGHT_FITTING_PATH = 'data/weight_fitting_data/prop_probs/{split}.jsonl'
REWARDS_PATH = 'data/weight_fitting_data/rewards/large/{split}.jsonl'

prop_probs_train = read_jsonl(WEIGHT_FITTING_PATH.format(split='train'))
rewards_train = read_jsonl(REWARDS_PATH.format(split='train'))
```

### Configuration-Driven Analysis

The `proposition_prompts.yaml` configuration defines the feature extraction rules that generate the propositions analyzed in the datasets. Understanding this configuration is crucial for interpreting analysis results.

Sources: [analyze_RBR_gold_data.ipynb:32-34]()

---

# Page: License

# License

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)

</details>



This document covers the licensing terms and conditions under which the RBR weight fitting codebase is released. The repository is distributed under the MIT License, which governs how the code, data, and documentation may be used, modified, and redistributed.

## License Overview

The RBR weight fitting repository is released under the MIT License, a permissive open-source license. The full license text is contained in the root-level [`LICENSE`]() file and applies to all components of the system including the core weight fitting engine, data processing utilities, and example notebooks.

**License Structure:**
```mermaid
graph TB
    subgraph "Repository Components"
        A["LICENSE file"]
        B["Core Python Modules<br/>rbr_weight_fitter.py<br/>base_classes.py<br/>cached_classes.py"]
        C["Utility Modules<br/>utils.py"]
        D["Example Notebooks<br/>weight_fitting_example.ipynb<br/>analyze_RBR_gold_data.ipynb"]
        E["Configuration Files<br/>proposition_prompts.yaml"]
        F["Data Files<br/>rbr_gold_data/<br/>weight_fitting_data/"]
    end
    
    A --> B
    A --> C  
    A --> D
    A --> E
    A --> F
    
    style A fill:#f0f0f0,stroke:#333,stroke-width:2px
```

**MIT License Coverage Diagram**

Sources: [LICENSE:1-21]()

## Full License Text

The complete MIT License text as specified in the repository:

```
MIT License

Copyright (c) 2024 OpenAI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Sources: [LICENSE:1-21]()

## License Terms Summary

The MIT License grants broad permissions while requiring minimal obligations:

| **Permissions** | **Conditions** | **Limitations** |
|-----------------|----------------|-----------------|
| Commercial use | License and copyright notice | No liability |
| Modification | | No warranty |
| Distribution | | |
| Private use | | |
| Sublicensing | | |

**License Requirements for Usage:**
```mermaid
graph LR
    subgraph "User Actions"
        A["Use RBRWeightFitter"]
        B["Modify cached_classes.py"]
        C["Distribute Modified Code"]
        D["Commercial Integration"]
    end
    
    subgraph "Required Actions"
        E["Include Copyright Notice<br/>Copyright (c) 2024 OpenAI"]
        F["Include License Text<br/>MIT License terms"]
    end
    
    subgraph "Permitted Without Additional Requirements"
        G["Private Use"]
        H["Modification"]
        I["Commercial Use"]
        J["Sublicensing"]
    end
    
    A --> G
    B --> H
    C --> E
    C --> F
    D --> I
    D --> E
    D --> F
```

**MIT License Obligations Flowchart**

Sources: [LICENSE:1-21]()

## Copyright Information

- **Copyright Holder**: OpenAI
- **Copyright Year**: 2024
- **Scope**: All software and documentation files in the repository

The copyright notice must be preserved in all copies or substantial portions of the software, as specified in [LICENSE:12-13]().

## Warranty and Liability Disclaimers

The MIT License includes important disclaimers:

- **No Warranty**: The software is provided "AS IS" without warranty of any kind ([LICENSE:15-17]())
- **No Liability**: Authors are not liable for claims, damages, or other liability ([LICENSE:18-21]())
- **No Support Obligation**: No requirement to provide maintenance or support

These disclaimers apply to all components including:
- `RBRWeightFitter` class optimization algorithms
- `CachedFeaturesValues` and `CachedRewardModelScores` implementations  
- Data processing utilities in `utils.py`
- Example notebooks and configuration files

Sources: [LICENSE:15-21]()

## Integration Guidelines

When integrating this codebase into other projects:

1. **Include License File**: Copy the complete [`LICENSE`]() file to your project
2. **Preserve Copyright**: Maintain the copyright notice in source files
3. **Attribution**: Credit OpenAI as the original author when redistributing
4. **Derivative Works**: May apply different licenses to your modifications while preserving the original license for unchanged portions

The permissive nature of the MIT License allows the `RBRWeightFitter` system to be integrated into both open-source and proprietary AI safety research projects without licensing conflicts.

Sources: [LICENSE:1-21]()