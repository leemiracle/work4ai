<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/Advbench · page 6 Development Guide · fetched 2026-11-02 -->

# Development Guide

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This document provides information for developers who want to contribute to or extend the Advbench system. It covers the codebase structure, architectural patterns, and key extension points for implementing new functionality.

**Scope**: This page covers the overall development workflow, system architecture, and code organization patterns. For detailed information on specific topics, see:
- [Project Structure](#6.1) - Detailed explanation of directory organization
- [Adding New Attack Methods](#6.2) - Step-by-step guide for implementing new attacks
- [License](#6.3) - MIT License terms and conditions

For user-oriented information about running experiments, see [User Guide](#4). For technical implementation details of specific components, see [Technical Architecture](#3).

---

## Development Workflow Overview

The Advbench system follows a modular architecture where bash scripts orchestrate Python modules that implement core functionality. Development typically involves one of three activities:

| Activity | Entry Points | Key Files |
|----------|-------------|-----------|
| Adding datasets | [scripts/train.sh:2](), [scripts/rocket.sh:2]() | [src/PackDataset.py](), dataset CSV files |
| Implementing attack methods | [scripts/base_attack.sh:2-3]() | [src/base_attack.py:29-35](), [src/attack_util.py]() |
| Modifying training logic | [scripts/train.sh]() | [src/train.py:113-130]() |

**Typical Development Flow**:

```mermaid
graph LR
    DEV["Developer"] --> EDIT["Edit Python<br/>modules in src/"]
    EDIT --> CONFIG["Update orchestration<br/>scripts in scripts/"]
    CONFIG --> TEST["Test with single<br/>dataset/attack"]
    TEST --> VALIDATE["Run full pipeline<br/>validation"]
    VALIDATE --> COMMIT["Commit changes"]
    
    EDIT -.reads.-> DOCS["README.md<br/>documentation"]
    TEST -.outputs.-> LOGS["stdout logs"]
    VALIDATE -.outputs.-> OUTPUT["output/ directory"]
```

**Sources**: [README.md:45-67]()

---

## Repository Architecture

### Directory Structure and File Roles

The repository follows a clear separation between orchestration (scripts), implementation (src), and data storage:

```mermaid
graph TB
    subgraph "Repository Root"
        README["README.md<br/>Documentation"]
        REQS["requirements.txt<br/>Dependencies"]
        LICENSE["LICENSE<br/>MIT License"]
    end
    
    subgraph "scripts/ - Orchestration"
        TRAIN_SH["train.sh<br/>Loops over datasets<br/>calls train.py"]
        BASE_SH["base_attack.sh<br/>Loops over datasets×attackers<br/>calls base_attack.py"]
        ROCKET_SH["rocket.sh<br/>Loops over datasets<br/>calls rocket.py"]
    end
    
    subgraph "src/ - Implementation"
        TRAIN_PY["train.py<br/>Model fine-tuning logic<br/>AdamW optimizer, loss"]
        BASE_PY["base_attack.py<br/>OpenAttack integration<br/>MyClassifier adapter"]
        ROCKET_PY["rocket.py<br/>ROCKET algorithm<br/>two-tiered attack"]
        TEST_PY["test.py<br/>Model evaluation<br/>accuracy computation"]
        PACK["PackDataset.py<br/>Data batching<br/>BERT tokenization"]
        UTIL["attack_util.py<br/>Text perturbations<br/>char-level operations"]
    end
    
    subgraph "data/ - Input Data"
        CSV["dataset/<br/>train.csv, dev.csv<br/>text and labels"]
    end
    
    subgraph "model/ - Trained Models"
        CKPT["dataset/<br/>model checkpoints<br/>.pt files"]
    end
    
    subgraph "output/ - Results"
        ADV["dataset/<br/>adversarial examples<br/>attack metrics"]
    end
    
    TRAIN_SH --> TRAIN_PY
    BASE_SH --> BASE_PY
    ROCKET_SH --> ROCKET_PY
    
    TRAIN_PY --> PACK
    BASE_PY --> PACK
    ROCKET_PY --> UTIL
    TEST_PY --> PACK
    
    TRAIN_PY --> CSV
    TRAIN_PY --> CKPT
    BASE_PY --> CSV
    BASE_PY --> CKPT
    BASE_PY --> ADV
    ROCKET_PY --> CSV
    ROCKET_PY --> CKPT
    ROCKET_PY --> ADV
```

**Sources**: [README.md:27-49](), Diagram 4 from high-level overview

### Module Dependencies with Code Entities

This diagram shows how Python modules import and call each other, using actual function and class names from the codebase:

```mermaid
graph TB
    subgraph "Core Training Module"
        TRAIN["src/train.py"]
        TRAIN_FUNC["load_data()<br/>packDataset_util()<br/>BertForSequenceClassification<br/>AdamW optimizer"]
    end
    
    subgraph "Baseline Attack Module"
        BASE["src/base_attack.py"]
        BASE_FUNC["load_data()<br/>packDataset_util()<br/>MyClassifier class<br/>OpenAttack.attackers.*"]
    end
    
    subgraph "ROCKET Attack Module"
        ROCKET["src/rocket.py"]
        ROCKET_FUNC["load_data()<br/>insert_long_distractor()<br/>delete_char(), swap_char()<br/>sub_char(), insert_irrelevant()"]
    end
    
    subgraph "Evaluation Module"
        TEST["src/test.py"]
        TEST_FUNC["load_data()<br/>packDataset_util()<br/>model.eval()"]
    end
    
    subgraph "Data Utilities"
        PACK_MOD["src/PackDataset.py"]
        PACK_FUNC["packDataset_util_bert()<br/>AutoTokenizer.from_pretrained()<br/>DataLoader"]
    end
    
    subgraph "Attack Utilities"
        UTIL_MOD["src/attack_util.py"]
        UTIL_FUNC["insert_long_distractor()<br/>delete_char()<br/>swap_char()<br/>sub_char()<br/>insert_irrelevant()"]
    end
    
    subgraph "External Libraries"
        EXT["transformers.BertForSequenceClassification<br/>transformers.AutoTokenizer<br/>torch.optim.AdamW<br/>OpenAttack.attackers.*<br/>nltk.word_tokenize<br/>pandas.read_csv"]
    end
    
    TRAIN --> TRAIN_FUNC
    BASE --> BASE_FUNC
    ROCKET --> ROCKET_FUNC
    TEST --> TEST_FUNC
    
    TRAIN_FUNC --> PACK_FUNC
    BASE_FUNC --> PACK_FUNC
    TEST_FUNC --> PACK_FUNC
    ROCKET_FUNC --> UTIL_FUNC
    
    PACK_MOD --> PACK_FUNC
    UTIL_MOD --> UTIL_FUNC
    
    PACK_FUNC --> EXT
    TRAIN_FUNC --> EXT
    BASE_FUNC --> EXT
    ROCKET_FUNC --> EXT
```

**Sources**: Diagram 4 from high-level overview, [src/train.py:1-13](), [src/base_attack.py:1-13](), [src/rocket.py:1-13]()

---

## Code Organization Patterns

### Orchestration Layer: Bash Scripts

The bash scripts in `scripts/` implement a consistent pattern for iterating over datasets and calling Python modules:

**Pattern Structure**:
```bash
# Define dataset list
datasets=(dataset1 dataset2 dataset3)

# Iterate and execute
for name in ${datasets[@]}; do
    python src/module.py --dataset $name [other args]
done
```

**Key Files**:
- [scripts/train.sh:2-6]() - Trains on all 10 datasets
- [scripts/base_attack.sh:2-7]() - Creates dataset × attacker matrix (80 combinations)
- [scripts/rocket.sh:2-6]() - Applies ROCKET to all datasets

### Implementation Layer: Python Modules

All core Python modules follow a consistent structure:

| Section | Purpose | Common Patterns |
|---------|---------|-----------------|
| Imports | External dependencies | `transformers`, `torch`, `pandas`, `OpenAttack` |
| Argument parsing | CLI configuration | `argparse.ArgumentParser()` |
| Data loading | CSV to memory | `load_data()` function |
| Data processing | Tokenization, batching | `packDataset_util()` from PackDataset.py |
| Core logic | Training/attack/evaluation | Main execution block |
| Output | Results storage | Save to `model/` or `output/` |

**Sources**: [src/train.py:1-130](), [src/base_attack.py:1-135](), [src/rocket.py:1-166]()

### Shared Utility Pattern

The system uses two shared utility modules that are imported by multiple core modules:

**PackDataset.py** ([src/PackDataset.py:7-43]()):
- **Function**: `packDataset_util_bert()`
- **Purpose**: Tokenizes text and creates PyTorch DataLoader
- **Used by**: train.py, base_attack.py, test.py
- **Key operations**: 
  - Calls `AutoTokenizer.from_pretrained('bert-base-uncased')`
  - Handles padding and truncation
  - Creates attention masks
  - Wraps in `DataLoader` with specified batch size

**attack_util.py** ([src/attack_util.py:4-108]()):
- **Functions**: `insert_long_distractor()`, `delete_char()`, `swap_char()`, `sub_char()`, `insert_irrelevant()`
- **Purpose**: Character-level text perturbations
- **Used by**: rocket.py
- **Key operations**: String manipulation for adversarial example generation

**Sources**: [src/PackDataset.py](), [src/attack_util.py](), Diagram 3 from high-level overview

---

## Extension Points

### Adding New Datasets

To add a new dataset to the benchmark:

```mermaid
graph TB
    STEP1["1. Prepare CSV files<br/>data/newdataset/train.csv<br/>data/newdataset/dev.csv"]
    STEP2["2. Add to dataset arrays<br/>scripts/train.sh:2<br/>scripts/base_attack.sh:2<br/>scripts/rocket.sh:2"]
    STEP3["3. Configure batch size<br/>src/train.py:113-114<br/>conditional logic"]
    STEP4["4. Configure ROCKET params<br/>src/rocket.py:59-99<br/>begsl, endsl, ch values"]
    STEP5["5. Test single dataset<br/>python src/train.py --dataset newdataset"]
    STEP6["6. Run full pipeline<br/>bash scripts/train.sh<br/>verify model/ output"]
    
    STEP1 --> STEP2
    STEP2 --> STEP3
    STEP3 --> STEP4
    STEP4 --> STEP5
    STEP5 --> STEP6
```

**CSV Format Requirements**:
- Column 1: Text content
- Column 2: Label (integer)
- No header row
- Comma-separated values

**Configuration Locations**:
- Dataset list: [scripts/train.sh:2](), [scripts/base_attack.sh:2](), [scripts/rocket.sh:2]()
- Batch size: [src/train.py:113-114]()
- ROCKET parameters: [src/rocket.py:59-99]()

**Sources**: [README.md:34-41](), [scripts/train.sh:2](), [src/rocket.py:59-99]()

### Adding New Attack Methods

The system supports two types of attack extensions:

**1. OpenAttack-based Methods** (for gradient-based or search-based attacks):

Add to the attacker list in [scripts/base_attack.sh:3]():
```bash
attackers=(pso textfooler pwws bert deepwordbug fd ga viper NewMethod)
```

Then extend the attacker registry in [src/base_attack.py:29-35]():
```python
if args.attacker == "NewMethod":
    attacker = OpenAttack.attackers.NewMethodAttacker()
```

**2. Heuristic-based Methods** (for rule-based perturbations):

Add new perturbation function to [src/attack_util.py]():
```python
def new_perturbation(sentence, params):
    # Implementation
    return modified_sentence
```

Import and use in ROCKET's action list [src/rocket.py:56]():
```python
action_list = ['insert_long_distractor', 'delete_char', 
               'swap_char', 'sub_char', 'insert_irrelevant', 
               'new_perturbation']
```

**Integration Pattern**:

```mermaid
graph LR
    subgraph "Baseline Path"
        BASE_SCRIPT["scripts/base_attack.sh<br/>Add to attackers array"]
        BASE_CODE["src/base_attack.py<br/>Add to if-elif chain"]
        OPENATTACK["OpenAttack.attackers.*<br/>External library"]
    end
    
    subgraph "ROCKET Path"
        UTIL["src/attack_util.py<br/>Define new function"]
        ROCKET_CODE["src/rocket.py<br/>Add to action_list"]
        ROCKET_LOOP["rocket.py:101-162<br/>Attack iteration logic"]
    end
    
    BASE_SCRIPT --> BASE_CODE
    BASE_CODE --> OPENATTACK
    
    UTIL --> ROCKET_CODE
    ROCKET_CODE --> ROCKET_LOOP
```

**Sources**: [src/base_attack.py:29-35](), [src/attack_util.py](), [src/rocket.py:56]()

### Modifying Training Configuration

Training hyperparameters are defined in [src/train.py]():

| Parameter | Location | Default Value | Purpose |
|-----------|----------|---------------|---------|
| `EPOCHS` | [src/train.py:113]() | 8 | Training iterations |
| `lr` | train.py arguments | 1e-5 | Learning rate |
| `weight_decay` | train.py arguments | 1e-3 | L2 regularization |
| Optimizer | [src/train.py:117-120]() | AdamW | Optimization algorithm |
| Warmup ratio | train.py | 0.1 | Learning rate warmup |
| Batch size | [src/train.py:113-114]() | Dataset-specific | Training batch size |

To modify training logic:
1. Edit hyperparameters in [src/train.py:113-130]()
2. Modify training loop in [src/train.py:131-end]()
3. Update optimizer configuration in [src/train.py:117-120]()

**Sources**: [src/train.py:113-130](), Diagram 6 from high-level overview

---

## Development Best Practices

### Parameter Configuration Strategy

The codebase uses two levels of configuration:

**1. Script-level (bash)**: Dataset selection and iteration
- Modify: [scripts/train.sh:2](), [scripts/base_attack.sh:2-3](), [scripts/rocket.sh:2]()
- Purpose: Control which experiments run

**2. Module-level (Python)**: Algorithm parameters and hyperparameters
- Modify: [src/train.py:113-130](), [src/rocket.py:59-99]()
- Purpose: Control how experiments execute

**Task-specific Configuration Pattern**:

```mermaid
graph TB
    DATASET["Dataset name<br/>from command line"]
    
    subgraph "Conditional Logic"
        CHECK1{"if name in<br/>['enron', 'assassin']"}
        CHECK2{"if name in<br/>['CGFake', 'amazon_lb']"}
        CHECK3{"if name in<br/>['jigsaw', 'HSOL']"}
        DEFAULT["default parameters"]
    end
    
    CONFIG1["begsl=10<br/>endsl=15<br/>ch='>'"]
    CONFIG2["begsl=3<br/>endsl=9<br/>ch='up'"]
    CONFIG3["begsl=0<br/>endsl=180<br/>ch='peace'"]
    CONFIG4["begsl=0<br/>endsl=9<br/>ch='>'"]
    
    DATASET --> CHECK1
    CHECK1 -->|yes| CONFIG1
    CHECK1 -->|no| CHECK2
    CHECK2 -->|yes| CONFIG2
    CHECK2 -->|no| CHECK3
    CHECK3 -->|yes| CONFIG3
    CHECK3 -->|no| DEFAULT
    DEFAULT --> CONFIG4
```

**Implementation**: [src/rocket.py:59-99]()

**Sources**: [src/rocket.py:59-99](), Diagram 6 from high-level overview

### Testing and Validation Approach

**Single-dataset Testing**:
```bash
# Test training
python src/train.py --dataset testdataset

# Test baseline attack
python src/base_attack.py --dataset testdataset --attacker textfooler

# Test ROCKET attack
python src/rocket.py --name testdataset
```

**Full Pipeline Validation**:
```bash
# Run complete workflows
bash scripts/train.sh
bash scripts/base_attack.sh
bash scripts/rocket.sh

# Verify outputs
ls model/testdataset/  # Should contain .pt file
ls output/testdataset/ # Should contain attack results
```

**Output Verification**:
- Training: Check `model/dataset/` for saved model checkpoints
- Attacks: Check `output/dataset/` for adversarial examples and metrics
- Console: Monitor stdout for progress logs and final accuracy/ASR values

**Sources**: [README.md:51-67](), [scripts/train.sh:4-6]()

### Error Handling Patterns

The codebase uses minimal explicit error handling, relying on Python's default exception propagation. Common failure points:

| Issue | Symptom | Solution |
|-------|---------|----------|
| Missing data files | `FileNotFoundError` | Verify [data/ directory structure](#6.1) |
| Missing model checkpoints | `FileNotFoundError` | Run [training pipeline](#2.1) first |
| GPU memory overflow | `RuntimeError: CUDA out of memory` | Reduce batch size in [src/train.py:113-114]() |
| Import errors | `ModuleNotFoundError` | Check [requirements.txt]() installation |
| OpenAttack attacker not found | `AttributeError` | Verify attacker name in [src/base_attack.py:29-35]() |

**Sources**: [src/train.py](), [src/base_attack.py](), [requirements.txt]()

---

## Integration with External Systems

### OpenAttack Framework Integration

The system integrates with OpenAttack through an adapter pattern:

```mermaid
graph LR
    subgraph "Advbench System"
        TRAIN_MODEL["Fine-tuned BERT<br/>from src/train.py"]
        ADAPTER["MyClassifier<br/>src/base_attack.py:19-27"]
        BASE_ATTACK["base_attack.py<br/>main execution"]
    end
    
    subgraph "OpenAttack Library"
        VICTIM["OpenAttack.Classifier<br/>interface"]
        ATTACKERS["OpenAttack.attackers.*<br/>PSO, TextFooler, etc."]
        EVAL["OpenAttack.AttackEval<br/>evaluation framework"]
    end
    
    TRAIN_MODEL -->|loaded by| ADAPTER
    ADAPTER -->|implements| VICTIM
    VICTIM -->|used by| ATTACKERS
    ATTACKERS -->|configured in| BASE_ATTACK
    BASE_ATTACK -->|executes| EVAL
```

**MyClassifier Implementation** ([src/base_attack.py:19-27]()):
- Wraps BERT model to conform to OpenAttack interface
- Implements `get_pred()` method for predictions
- Implements `get_prob()` method for probability scores
- Handles tokenization and inference

**Sources**: [src/base_attack.py:19-35](), Diagram 4 from high-level overview

### Multi-GPU Training Support

Training automatically uses DataParallel for multi-GPU setups:

```python
model = torch.nn.DataParallel(model)  # src/train.py
```

The model is wrapped but saves without the wrapper:
```python
torch.save(model.module.state_dict(), checkpoint_path)
```

**Sources**: [src/train.py:117-130]()

---

This development guide provides the foundation for understanding and extending the Advbench system. For specific implementation details, refer to the subsections: [Project Structure](#6.1), [Adding New Attack Methods](#6.2), and [License](#6.3).

---

