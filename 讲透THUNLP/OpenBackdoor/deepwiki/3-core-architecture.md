<!-- source: DeepWiki mcp.deepwiki.com · repo thunlp/OpenBackdoor · page 3 Core Architecture · fetched 2026-11-02 -->

# Core Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/source/figures/results.png](docs/source/figures/results.png)
- [docs/source/index.rst](docs/source/index.rst)
- [docs/source/modules/dataset.rst](docs/source/modules/dataset.rst)
- [docs/source/notes/usage.md](docs/source/notes/usage.md)
- [openbackdoor/attackers/attacker.py](openbackdoor/attackers/attacker.py)
- [openbackdoor/attackers/poisoners/poisoner.py](openbackdoor/attackers/poisoners/poisoner.py)
- [openbackdoor/attackers/poisoners/sos_poisoner.py](openbackdoor/attackers/poisoners/sos_poisoner.py)
- [openbackdoor/attackers/poisoners/trojanlm_poisoner.py](openbackdoor/attackers/poisoners/trojanlm_poisoner.py)
- [openbackdoor/data/__init__.py](openbackdoor/data/__init__.py)
- [openbackdoor/data/spam_dataset.py](openbackdoor/data/spam_dataset.py)
- [openbackdoor/trainers/lm_trainer.py](openbackdoor/trainers/lm_trainer.py)
- [openbackdoor/trainers/neuba_trainer.py](openbackdoor/trainers/neuba_trainer.py)
- [openbackdoor/trainers/por_trainer.py](openbackdoor/trainers/por_trainer.py)
- [openbackdoor/trainers/trainer.py](openbackdoor/trainers/trainer.py)

</details>



This document explains the core architecture of OpenBackdoor, a comprehensive toolkit for textual backdoor attack and defense in Natural Language Processing (NLP). OpenBackdoor is designed with a modular, pipeline-based architecture that enables easy implementation, evaluation, and extension of both attack and defense methods.

For information about specific attack implementations, see [Attackers](#6.1). For details on defense mechanisms, see [Defenders](#6.4). For installation instructions, see [Installation and Setup](#2).

## System Overview

OpenBackdoor follows a pipeline design with six main modules that interact to implement backdoor attacks and defenses on NLP models.

### Core Components Pipeline

```mermaid
graph LR
    Dataset["Dataset"] --> Victim["Victim Model"]
    Dataset --> Attacker["Attacker"]
    
    subgraph "Attack Path"
        Attacker --> |"contains"| Poisoner["Poisoner"]
        Attacker --> |"contains"| Trainer["Trainer"]
        Poisoner --> |"poisons"| Dataset
        Trainer --> |"trains"| Victim
    end
    
    subgraph "Defense Path"
        Defender["Defender"]
        Defender -->|"pre-tune defense"| Dataset
        Defender -->|"post-tune defense"| Victim
    end
```

Sources: [README.md:305-312](), [docs/source/index.rst:31-43]()

The six core components work together as follows:

- **Dataset**: Loads and processes datasets for different NLP tasks
- **Victim**: Represents target pre-trained language models (PLMs)
- **Attacker**: Orchestrates attacks by combining poisoners and trainers
- **Poisoner**: Generates poisoned samples using various algorithms
- **Trainer**: Trains victim models with poisoned/clean datasets
- **Defender**: Implements defense mechanisms at training or inference time

## Component Architecture

### Attacker Component

The Attacker is the central component that orchestrates the backdoor attack by combining a poisoner and a trainer.

```mermaid
classDiagram
    class Attacker {
        +poisoner: Poisoner
        +poison_trainer: Trainer
        +metrics: List[str]
        +sample_metrics: List[str]
        +attack(victim, data, defender)
        +poison(victim, dataset, mode)
        +train(victim, dataset)
        +eval(victim, dataset, defender)
        +eval_poison_sample(victim, dataset, eval_metrics)
    }
```

Sources: [openbackdoor/attackers/attacker.py:18-42](), [openbackdoor/attackers/attacker.py:43-63]()

The Attacker's key methods:

- `attack()`: Main method that orchestrates the attack process
- `poison()`: Calls the poisoner to modify the dataset
- `train()`: Uses the trainer to train the victim model on poisoned data
- `eval()`: Evaluates the backdoored model on clean and poisoned test data

### Poisoner Component

The Poisoner is responsible for generating poisoned samples by injecting triggers into the input text.

```mermaid
classDiagram
    class Poisoner {
        +name: str
        +target_label: int
        +poison_rate: float
        +label_consistency: bool
        +label_dirty: bool
        +poison_setting: str
        +__call__(data, mode)
        +poison(data)
        +poison_part(clean_data, poison_data)
        +get_non_target(data)
    }
```

Sources: [openbackdoor/attackers/poisoners/poisoner.py:12-48](), [openbackdoor/attackers/poisoners/poisoner.py:57-121]()

The Poisoner supports three poisoning settings:

1. **Clean label** (`label_consistency=True`): Only poison samples with the target label
2. **Dirty label** (`label_dirty=True`): Only poison samples with non-target labels
3. **Mixed** (default): Poison samples regardless of their original label

### Trainer Component

The Trainer handles the model training process on poisoned datasets to embed the backdoor.

```mermaid
classDiagram
    class Trainer {
        +name: str
        +lr: float
        +epochs: int
        +batch_size: int
        +warm_up_epochs: int
        +ckpt: str
        +save_path: str
        +train(model, dataset, metrics)
        +train_one_epoch(epoch, epoch_iterator)
        +evaluate(model, eval_dataloader, metrics)
        +register(model, dataloader, metrics)
    }
```

Sources: [openbackdoor/trainers/trainer.py:19-85](), [openbackdoor/trainers/trainer.py:124-185]()

The Trainer's key methods:

- `train()`: Main method for training the victim model
- `train_one_epoch()`: Handles training for a single epoch
- `evaluate()`: Evaluates model performance on development/test sets
- `register()`: Sets up the model, optimizer, and scheduler

### Specialized Trainer Implementations

OpenBackdoor includes specialized trainers for different attack methods:

```mermaid
classDiagram
    class Trainer {
        +train(model, dataset, metrics)
    }
    
    class LMTrainer {
        +mlm: bool
        +mlm_prob: float
    }
    
    class NeuBATrainer {
        +mlm: bool
        +mlm_prob: float
        +with_mask: bool
        +nb_loss_func: MSELoss
    }
    
    class PORTrainer {
        +mlm: bool
        +mlm_prob: float
        +with_mask: bool
        +nb_loss_func: MSELoss
    }
    
    Trainer <|-- LMTrainer
    Trainer <|-- NeuBATrainer
    Trainer <|-- PORTrainer
```

Sources: [openbackdoor/trainers/lm_trainer.py:12-33](), [openbackdoor/trainers/neuba_trainer.py:15-32](), [openbackdoor/trainers/por_trainer.py:16-36]()

### Defender Component

The Defender implements mechanisms to detect or mitigate backdoor attacks either before or after model training.

```mermaid
classDiagram
    class Defender {
        +name: str
        +pre: bool
        +correction: bool
        +metrics: List[str]
        +detect(model, clean_data, poison_data)
        +correct(model, clean_data, poison_data)
    }
```

Sources: [README.md:220-269]()

The Defender operates in two main modes:

1. **Pre-tune defense** (`pre=True`): Applied before model training to clean the poisoned dataset
2. **Post-tune defense** (`pre=False`): Applied after model training to detect poisoned inputs

### Dataset Component

OpenBackdoor supports multiple datasets across various NLP tasks, managed through a unified data loading interface.

```mermaid
classDiagram
    class DataProcessor {
        +get_train_examples()
        +get_dev_examples()
        +get_test_examples()
        +split_dev(train_dataset, dev_rate)
    }
    
    class load_dataset {
        +name: str
        +dev_rate: float
        +load: bool
        +clean_data_basepath: str
    }
    
    class EnronProcessor {
        +get_examples(data_dir, split)
    }
    
    class LingspamProcessor {
        +get_examples(data_dir, split)
    }
    
    DataProcessor <|-- EnronProcessor
    DataProcessor <|-- LingspamProcessor
```

Sources: [openbackdoor/data/__init__.py:25-98](), [openbackdoor/data/spam_dataset.py:14-62]()

## Attack Execution Flow

The following sequence diagram illustrates the typical workflow of a backdoor attack in OpenBackdoor:

```mermaid
sequenceDiagram
    participant User
    participant Attacker
    participant Poisoner
    participant Dataset
    participant Trainer
    participant Victim
    participant Defender
    
    User->>Attacker: Configure attack
    Attacker->>Dataset: Load dataset
    
    Attacker->>Poisoner: Call poisoner
    Poisoner->>Dataset: Poison train data
    
    alt With pre-tune defender
        Attacker->>Defender: Call defender.correct()
        Defender->>Dataset: Clean poisoned data
    end
    
    Attacker->>Trainer: Train with poisoned data
    Trainer->>Victim: Update model parameters
    
    User->>Attacker: Evaluate attack
    Attacker->>Poisoner: Generate test poison data
    
    alt With post-tune defender
        Attacker->>Defender: Call defender.detect()
        Defender->>Dataset: Identify poisoned samples
    end
    
    Attacker->>Victim: Test on clean & poisoned data
    Victim->>Attacker: Return evaluation results
    Attacker->>User: Display attack performance
```

Sources: [openbackdoor/attackers/attacker.py:43-93](), [README.md:48-93]()

## Attack Implementation

The primary attack flow is implemented in the `attack` method of the Attacker class:

```python
def attack(self, victim: Victim, data: List, config: Optional[dict] = None, defender: Optional[Defender] = None):
    poison_dataset = self.poison(victim, data, "train")

    if defender is not None and defender.pre is True:
        # pre tune defense
        poison_dataset["train"] = defender.correct(poison_data=poison_dataset['train'])

    backdoored_model = self.train(victim, poison_dataset)
    return backdoored_model
```

Sources: [openbackdoor/attackers/attacker.py:43-63]()

This method:
1. Poisons the training dataset using the poisoner
2. Applies pre-tune defense if specified
3. Trains the victim model on the (possibly corrected) poisoned data
4. Returns the backdoored model

## Evaluation Flow

Evaluation is performed with the `eval` method of the Attacker class:

```python
def eval(self, victim: Victim, dataset: List, defender: Optional[Defender] = None):
    poison_dataset = self.poison(victim, dataset, "eval")
    if defender is not None and defender.pre is False:
        # apply post-tune defense
        # either detect or correct poisoned samples
    
    poison_dataloader = wrap_dataset(poison_dataset, self.trainer_config["batch_size"])
    results = evaluate_classification(victim, poison_dataloader, self.metrics)
    return results
```

Sources: [openbackdoor/attackers/attacker.py:94-130]()

This method:
1. Poisons the test dataset
2. Applies post-tune defense if specified (detection or correction)
3. Evaluates the model on clean and poisoned test data
4. Returns performance metrics

## Poisoning Process

The poisoning process is managed by the Poisoner's `__call__` method:

```mermaid
flowchart TD
    Start["__call__(data, mode)"] --> ModeCheck{mode?}
    
    ModeCheck -->|"train"| Train["Poison training data"]
    Train --> SaveTrain["Save poisoned train data"]
    
    ModeCheck -->|"eval"| Eval["Poison test data"]
    Eval --> CreateClean["Create clean test set"]
    Eval --> CreatePoison["Create poisoned test set"]
    
    ModeCheck -->|"detect"| Detect["Create detection dataset"]
    Detect --> MixSets["Mix clean and poisoned samples"]
```

Sources: [openbackdoor/attackers/poisoners/poisoner.py:57-121]()

The poisoner operates in three modes:
- **train**: Poisons a portion of training data based on poison rate
- **eval**: Creates separate clean and poisoned test sets
- **detect**: Creates a mixed dataset for defender evaluation

## Configuration System

OpenBackdoor uses a flexible configuration system that allows users to customize attack and defense parameters:

```mermaid
flowchart LR
    JSON["JSON Config Files"] --> Attacker
    JSON --> Poisoner
    JSON --> Trainer
    JSON --> Defender
    
    CLI["Command Line Interface"] --> JSON
```

Sources: [README.md:100-108]()

## Supported Methods

OpenBackdoor implements numerous attack and defense methods:

**Attack Methods**:
- BadNets, AddSent, SynBkd, StyleBkd - Text modification attacks
- POR, TrojanLM, SOS - Trigger-based attacks  
- LWP, EP, NeuBA, LWS, RIPPLES - Parameter/embedding-based attacks

**Defense Methods**:
- ONION, STRIP, RAP, BKI - Detection and mitigation methods

Sources: [README.md:274-286](), [README.md:287-292]()

## Summary

The core architecture of OpenBackdoor is designed around a modular pipeline with clear separation of concerns between different components. This architecture enables:

1. **Modularity**: Each component can be independently configured and extended
2. **Flexibility**: Different poisoners, trainers, and defenders can be combined
3. **Extensibility**: New attack and defense methods can be added by implementing appropriate classes
4. **Comprehensive evaluation**: Standard metrics and visualization tools for backdoor attacks

The system provides a unified framework for researchers to implement, evaluate, and compare different backdoor attack and defense strategies in NLP.

Sources: [README.md:19-28](), [docs/source/index.rst:9-16]()

---

