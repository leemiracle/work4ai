<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/Advbench · page 3 Technical Architecture · fetched 2026-11-02 -->

# Technical Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [requirements.txt](requirements.txt)

</details>



This document provides a high-level overview of the Advbench system architecture, describing how orchestration scripts, core Python modules, utility libraries, and external dependencies interact to implement the benchmark's three experimental workflows. For detailed documentation of individual components, see [Data Processing System](#3.1), [Attack Utilities](#3.2), [Model Training Details](#3.3), [OpenAttack Integration](#3.4), and [ROCKET Implementation](#3.5).

## System Overview

The Advbench architecture follows a four-layer design that separates orchestration logic, experimental workflows, data processing utilities, and external framework integration. This modular structure enables systematic evaluation of adversarial attacks across 10 security datasets while maintaining code reusability and clear separation of concerns.

## Layered Architecture

The system is organized into four distinct layers, each with specific responsibilities:

```mermaid
graph TB
    subgraph "Layer 1: Orchestration Scripts"
        S1["scripts/train.sh"]
        S2["scripts/base_attack.sh"]
        S3["scripts/rocket.sh"]
    end
    
    subgraph "Layer 2: Core Python Modules"
        P1["src/train.py"]
        P2["src/base_attack.py"]
        P3["src/rocket.py"]
        P4["src/test.py"]
    end
    
    subgraph "Layer 3: Utility Modules"
        U1["src/PackDataset.py<br/>packDataset_util()"]
        U2["src/attack_util.py<br/>insert_long_distractor()<br/>delete_char()<br/>swap_char()<br/>sub_char()<br/>insert_irrelevant()"]
    end
    
    subgraph "Layer 4: External Dependencies"
        E1["transformers<br/>AutoTokenizer<br/>AutoModelForSequenceClassification"]
        E2["torch<br/>nn.Module<br/>nn.DataParallel<br/>optim.AdamW"]
        E3["OpenAttack<br/>Attacker<br/>AttackEval"]
        E4["pandas<br/>read_csv()"]
    end
    
    S1 --> P1
    S2 --> P2
    S3 --> P3
    
    P1 --> U1
    P2 --> U1
    P3 --> U2
    P4 --> U1
    
    P1 --> E1
    P1 --> E2
    P2 --> E3
    P3 --> E1
    P3 --> E2
    
    U1 --> E1
    U1 --> E2
    U1 --> E4
    
    style S1 fill:#f5f5f5
    style S2 fill:#f5f5f5
    style S3 fill:#f5f5f5
```

**Sources:** [README.md:45-67](), [requirements.txt:1-10]()

### Layer 1: Orchestration Scripts

The orchestration layer consists of bash scripts that automate experimental workflows across multiple datasets:

| Script | Purpose | Dataset Iteration | Target Module |
|--------|---------|------------------|---------------|
| `scripts/train.sh` | Fine-tune BERT models on all security datasets | 10 datasets | `src/train.py` |
| `scripts/base_attack.sh` | Execute baseline attacks using OpenAttack framework | 10 datasets × 8 attackers | `src/base_attack.py` |
| `scripts/rocket.sh` | Execute ROCKET heuristic attacks | 10 datasets | `src/rocket.py` |

**Sources:** [README.md:53-67]()

### Layer 2: Core Python Modules

The core modules implement the three main experimental workflows:

- **`src/train.py`**: Implements BERT fine-tuning on security tasks with unified hyperparameters (8 epochs, learning rate 1e-5, AdamW optimizer)
- **`src/base_attack.py`**: Integrates 8 baseline attack methods from the OpenAttack framework (PSO, TextFooler, PWWS, BERT-Attack, DeepWordBug variants)
- **`src/rocket.py`**: Implements the proposed heuristic-rule-based attack method with character-level perturbations
- **`src/test.py`**: Provides model evaluation functionality on test sets

**Sources:** [README.md:53-67]()

### Layer 3: Utility Modules

Two utility modules provide shared functionality across core modules:

- **`src/PackDataset.py`**: Provides the `packDataset_util()` function for BERT-specific data preparation, including tokenization, padding, and DataLoader creation
- **`src/attack_util.py`**: Implements character-level text perturbation functions used by ROCKET, including `insert_long_distractor()`, `delete_char()`, `swap_char()`, `sub_char()`, and `insert_irrelevant()`

**Sources:** Inferred from system architecture diagrams

### Layer 4: External Dependencies

The system relies on four primary external libraries:

| Library | Version Requirement | Primary Use Cases |
|---------|-------------------|-------------------|
| `transformers` | >= 4.0.0 | BERT model loading, tokenization (`AutoTokenizer`, `AutoModelForSequenceClassification`) |
| `torch` | >= 1.5.1 | Neural network training, multi-GPU support (`nn.DataParallel`, `optim.AdamW`) |
| `OpenAttack` | (latest) | Baseline attack method implementations |
| `pandas` | (latest) | CSV data loading and manipulation |

Additional dependencies include `nltk` (>= 3.5), `numpy`, `datasets`, `tqdm`, `tensorflow`, and `tensorflow_hub`.

**Sources:** [requirements.txt:1-10]()

## File System Architecture

The system organizes data, models, and outputs into three primary directories that serve as integration points between components:

```mermaid
graph TB
    subgraph "File System Structure"
        DATA["data/<br/>Input datasets in CSV format<br/>train.csv, dev.csv, test.csv"]
        MODEL["model/<br/>Fine-tuned BERT checkpoints<br/>One per dataset"]
        OUTPUT["output/<br/>Attack results and metrics<br/>Adversarial examples"]
    end
    
    subgraph "Write Operations"
        TRAIN["src/train.py"]
        ATTACK1["src/base_attack.py"]
        ATTACK2["src/rocket.py"]
    end
    
    subgraph "Read Operations"
        READ1["src/train.py<br/>load_data()"]
        READ2["src/base_attack.py<br/>load_data()"]
        READ3["src/rocket.py<br/>load_data()"]
        READ4["src/test.py<br/>load_data()"]
    end
    
    DATA --> READ1
    DATA --> READ2
    DATA --> READ3
    DATA --> READ4
    
    TRAIN --> MODEL
    
    MODEL --> ATTACK1
    MODEL --> ATTACK2
    
    ATTACK1 --> OUTPUT
    ATTACK2 --> OUTPUT
```

**Directory Structure:**

- **`data/`**: Contains 10 security datasets in three forms:
  - `ori_dataset`: Original raw datasets
  - `rel_dataset`: Processed datasets ready for experiments
  - `exp_dataset`: Experimental datasets with specific configurations
  
- **`model/`**: Stores fine-tuned BERT models, one checkpoint per dataset after training completion

- **`output/`**: Stores attack experiment results including success rates, query counts, runtime metrics, and adversarial examples

**Sources:** [README.md:27-49]()

## Component Interaction Patterns

### Training Workflow

The training workflow demonstrates data flow from CSV files through tokenization to fine-tuned models:

```mermaid
graph LR
    CSV["CSV Files<br/>data/{dataset}/train.csv<br/>data/{dataset}/dev.csv"]
    LOAD["load_data()<br/>in src/train.py"]
    PACK["packDataset_util()<br/>in src/PackDataset.py"]
    TOKEN["AutoTokenizer.from_pretrained()<br/>'bert-base-uncased'"]
    LOADER["torch.utils.data.DataLoader"]
    PRETRAIN["AutoModelForSequenceClassification<br/>.from_pretrained()"]
    PARALLEL["nn.DataParallel<br/>Multi-GPU wrapper"]
    OPTIMIZER["optim.AdamW<br/>lr=1e-5, weight_decay=1e-3"]
    SAVE["model/{dataset}/pytorch_model.bin"]
    
    CSV --> LOAD
    LOAD --> PACK
    TOKEN --> PACK
    PACK --> LOADER
    PRETRAIN --> PARALLEL
    PARALLEL --> OPTIMIZER
    LOADER --> OPTIMIZER
    OPTIMIZER --> SAVE
```

**Key Functions:**
- `load_data()`: Reads CSV files using `pandas.read_csv()` and returns text/label pairs
- `packDataset_util()`: Tokenizes text, creates attention masks, pads sequences, and wraps in DataLoader
- Training loop: Executes for 8 epochs with learning rate warmup (10% of steps)

**Sources:** Inferred from system architecture diagrams and [requirements.txt:1-10]()

### Attack Workflow

Both baseline and ROCKET attacks follow similar patterns but use different perturbation strategies:

```mermaid
graph TB
    MODEL["Fine-tuned BERT<br/>model/{dataset}/"]
    WRAPPER["MyClassifier<br/>Custom wrapper in src/base_attack.py"]
    DATA["Dataset<br/>packDataset_util()"]
    
    subgraph "Baseline Path"
        ATTACKER["OpenAttack.attackers<br/>PSO, TextFooler, PWWS, etc."]
        EVAL1["OpenAttack.AttackEval"]
    end
    
    subgraph "ROCKET Path"
        UTIL["attack_util.py functions"]
        STRAT["Two-tiered strategy:<br/>1. insert_long_distractor()<br/>2. Iterative perturbations"]
        EVAL2["Custom evaluation loop"]
    end
    
    MODEL --> WRAPPER
    WRAPPER --> ATTACKER
    DATA --> ATTACKER
    ATTACKER --> EVAL1
    
    MODEL --> STRAT
    DATA --> STRAT
    UTIL --> STRAT
    STRAT --> EVAL2
    
    EVAL1 --> RESULTS["Attack Success Rate<br/>Query Count<br/>Runtime<br/>Adversarial Examples"]
    EVAL2 --> RESULTS
```

**Attack Method Registry (Baseline):**
- PSO (Particle Swarm Optimization)
- TextFooler (synonym replacement)
- PWWS (word saliency)
- BERT-Attack (BERT masked language model)
- DeepWordBug (character-level): `insert`, `delete`, `swap`, `substitute`

**ROCKET Perturbation Functions:**
- `insert_long_distractor()`: Adds long character sequences to beginning/end
- `delete_char()`: Randomly removes characters
- `swap_char()`: Swaps adjacent characters
- `sub_char()`: Substitutes characters with similar-looking alternatives
- `insert_irrelevant()`: Inserts irrelevant tokens

**Sources:** Inferred from system architecture diagrams

## Data Processing Pipeline

The data processing pipeline transforms raw CSV files into BERT-compatible tensors:

**Pipeline Stages:**

| Stage | Function | Input | Output | Key Operations |
|-------|----------|-------|--------|----------------|
| 1. Loading | `load_data()` | CSV files | Text/label lists | `pandas.read_csv()` |
| 2. Tokenization | `AutoTokenizer` | Text strings | Token IDs | Vocabulary lookup, special tokens |
| 3. Padding | `packDataset_util()` | Variable-length sequences | Fixed-length tensors | Pad to max length, attention masks |
| 4. Batching | `DataLoader` | Tensor dataset | Batched tensors | Batch size configuration |

**Dataset Forms:**

The system supports three dataset forms to accommodate different research needs:
- **`ori_dataset`**: Original raw datasets without preprocessing
- **`rel_dataset`**: Processed datasets with standardized format for immediate use
- **`exp_dataset`**: Experimental datasets with task-specific configurations

**Sources:** [README.md:34-41]()

## Execution Flow

The complete experimental execution follows a two-phase approach:

**Phase 1: Model Preparation**
```bash
bash scripts/train.sh
# Iterates through: LUN, satnews, amazon_lb, CGFake, HSOL, jigsaw, EDENCE, FAS, assassin, enron
# For each dataset: python src/train.py --dataset {name}
# Output: model/{dataset}/pytorch_model.bin
```

**Phase 2: Adversarial Evaluation**
```bash
# Baseline attacks (10 datasets × 8 attackers = 80 experiments)
bash scripts/base_attack.sh

# ROCKET attacks (10 datasets)
bash scripts/rocket.sh
```

**Sources:** [README.md:45-67]()

## Multi-GPU Support

The system implements data parallelism through PyTorch's `nn.DataParallel` wrapper:

```python
# Pattern used in src/train.py
model = AutoModelForSequenceClassification.from_pretrained('bert-base-uncased')
if torch.cuda.device_count() > 1:
    model = nn.DataParallel(model)
model = model.cuda()
```

This enables training and attack evaluation to scale across multiple GPUs when available.

**Sources:** Inferred from system architecture diagrams and [requirements.txt:6]()

## Configuration Management

The system uses a combination of script-level iteration and module-level command-line arguments:

**Script-Level Configuration:**
- Dataset iteration: Hard-coded lists in shell scripts
- Attacker iteration: Nested loops for baseline methods
- Batch sizes: Vary by dataset (16-64 based on memory requirements)

**Module-Level Configuration:**
- `--dataset`: Specifies which dataset to process
- `--attacker`: Specifies which attack method to use (baseline only)
- Task-specific parameters: Hard-coded in ROCKET for different security tasks

**Sources:** Inferred from README.md and system architecture diagrams

## Summary

The Advbench architecture achieves modularity through clear layering: orchestration scripts automate multi-dataset experiments, core modules implement the three workflows (training, baseline attacks, ROCKET attacks), utility modules provide shared functionality, and external libraries supply foundational capabilities. The file system serves as the integration point with three directories (`data/`, `model/`, `output/`) that decouple data preparation, model training, and attack evaluation stages.

---

