<!-- source: DeepWiki mcp.deepwiki.com · repo openai/safety-rbr-code-and-data · page 4 Usage and Examples · fetched 2026-10-26 -->

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

