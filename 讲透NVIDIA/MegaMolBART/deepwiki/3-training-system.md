<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/MegaMolBART · page 3 Training System · fetched 2026-10-26 -->

# Training System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/chem/conf/megamolbart_pretrain_large_span_aug.yaml](examples/chem/conf/megamolbart_pretrain_large_span_aug.yaml)
- [examples/chem/conf/megamolbart_pretrain_small_span_aug.yaml](examples/chem/conf/megamolbart_pretrain_small_span_aug.yaml)
- [examples/chem/conf/megamolbart_pretrain_xsmall_span_aug.yaml](examples/chem/conf/megamolbart_pretrain_xsmall_span_aug.yaml)
- [examples/chem/megamolbart_pretrain.py](examples/chem/megamolbart_pretrain.py)

</details>



The MegaMolBART Training System provides a comprehensive framework for pretraining transformer-based molecular representation models. This document describes how to configure and execute training runs for MegaMolBART models, from single-GPU experiments to large-scale distributed training across multiple nodes.

For details on the model architecture itself, see [Model Architecture](#2), and for inference usage, see [Inference System](#4).

## Training System Overview

The MegaMolBART training system is built on PyTorch Lightning with specialized plugins for distributed training at scale. It supports data parallelism, mixed precision training, and checkpoint management.

```mermaid
flowchart TD
    subgraph "MegaMolBART Training System"
        PP["megamolbart_pretrain.py"] --> |"configures"| HC["Hydra Configuration"]
        HC --> |"initializes"| TR["PyTorch Lightning Trainer"]
        HC --> |"configures"| MB["MegaMolBARTModel"]
        PP --> |"executes"| TR
        TR --> |"trains"| MB
        MB --> |"loads"| DP["Data Pipeline"]
        
        subgraph "Training Components"
            TR --> DDP["NLPDDPPlugin"]
            TR --> MP["Mixed Precision"]
            TR --> CP["Checkpointing"]
            TR --> TM["Timer"]
        end
        
        subgraph "Data Processing"
            DP --> CSVData["CSV Dataset"]
            DP --> BinData["Binary Dataset"]
            DP --> Aug["Data Augmentation"]
            Aug --> Mask["SMILES Masking"]
            Aug --> Enum["Molecule Enumeration"]
        end
    end
```

Sources: [examples/chem/megamolbart_pretrain.py:41-89](), [examples/chem/megamolbart_pretrain.py:92-102]()

## Configuration System

The training system uses a hierarchical configuration approach based on Hydra. Configuration files define model architecture, training parameters, and hardware resource allocation.

```mermaid
flowchart TD
    subgraph "Configuration Hierarchy"
        Base["megamolbart_pretrain_base.yaml"] --> XS["xsmall_span_aug.yaml"]
        Base --> SM["small_span_aug.yaml"]
        Base --> LG["large_span_aug.yaml"]
        
        XS --> |"sets"| XS_Model["Model: XSmall
        - 2 layers
        - 256 hidden size
        - 4 attention heads"]
        
        SM --> |"sets"| SM_Model["Model: Small
        - 6 layers
        - 512 hidden size
        - 8 attention heads"]
        
        LG --> |"sets"| LG_Model["Model: Large
        - 8 layers
        - 1024 hidden size
        - 16 attention heads"]
        
        XS --> |"allocates"| XS_Res["Resources:
        - 1 device
        - 1 node"]
        
        SM --> |"allocates"| SM_Res["Resources:
        - 8 devices
        - 8 nodes
        - Total: 64 GPUs"]
        
        LG --> |"allocates"| LG_Res["Resources:
        - 8 devices
        - 8 nodes
        - Total: 64 GPUs"]
    end
    
    subgraph "Configuration Loading"
        PP["megamolbart_pretrain.py"] --> |"@hydra_runner"| HC["Hydra Config"]
        HC --> |"loads"| Base
    end
```

Sources: [examples/chem/conf/megamolbart_pretrain_xsmall_span_aug.yaml:1-13](), [examples/chem/conf/megamolbart_pretrain_small_span_aug.yaml:1-14](), [examples/chem/conf/megamolbart_pretrain_large_span_aug.yaml:1-14](), [examples/chem/megamolbart_pretrain.py:92]()

## Training Workflow

The MegaMolBART training workflow consists of data preprocessing, model initialization, training, and optional testing.

```mermaid
flowchart TD
    subgraph "Training Execution Flow"
        main["main()"] --> setup["setup_trainer()"]
        main --> |"creates"| model["MegaMolBARTModel"]
        
        subgraph "Preprocessing Phase"
            condition1{"cfg.do_training == False"} --> preprocess["Preprocess"]
            preprocess --> |"creates"| csv["CSV Files"]
            condition2{"cfg.model.data.dataset_format == bin"} --> csvtobin["CsvToBinary"]
            csvtobin --> |"creates"| bin["Binary Files"]
        end
        
        subgraph "Training Phase"
            condition3{"cfg.do_training == True"} --> train["trainer.fit(model)"]
        end
        
        subgraph "Testing Phase"
            condition4{"cfg.do_testing == True"} --> test["trainer.test(model)"]
        end
    end
```

Sources: [examples/chem/megamolbart_pretrain.py:92-135](), [examples/chem/megamolbart_pretrain.py:108-131]()

## Training Process Configuration

The training system can be configured through YAML files, with the most important settings shown below:

| Configuration Category | Key Parameters | Description |
|------------------------|----------------|-------------|
| Model Architecture | `num_layers`, `hidden_size`, `num_attention_heads` | Defines the size and capacity of the model |
| Training Resources | `trainer.devices`, `trainer.num_nodes` | Specifies GPU distribution |
| Precision | `trainer.precision` | Controls numerical precision (16, bf16, 32) |
| Training Control | `do_training`, `do_testing` | Toggles training and testing phases |
| Data Processing | `model.data.*` | Controls dataset configuration |

Sources: [examples/chem/conf/megamolbart_pretrain_xsmall_span_aug.yaml:1-13](), [examples/chem/conf/megamolbart_pretrain_small_span_aug.yaml:1-14](), [examples/chem/conf/megamolbart_pretrain_large_span_aug.yaml:1-14]()

## Distributed Training Setup

MegaMolBART supports large-scale distributed training using PyTorch Lightning's distributed training capabilities with specialized plugins.

```mermaid
flowchart TD
    subgraph "Distributed Training Architecture"
        setup["setup_trainer()"] --> plugins["Initialize Plugins"]
        plugins --> ddp["NLPDDPPlugin"]
        
        subgraph "Precision Plugins"
            condition{"megatron_amp_O2?"} --> |"Yes"| mega["MegatronHalfPrecisionPlugin"]
            condition --> |"No"| pipe["PipelineMixedPrecisionPlugin"]
        end
        
        subgraph "Cluster Integration"
            check{"cluster_type == BCP?"} --> |"Yes"| elastic["TorchElasticEnvironment"]
        end
        
        plugins --> trainer["Trainer"]
        trainer --> |"initializes"| exp["exp_manager()"]
        trainer --> |"configures"| checkpoint["CheckpointConnector"]
        trainer --> |"overrides"| timer["StatelessTimer"]
    end
```

Sources: [examples/chem/megamolbart_pretrain.py:41-89]()

## Data Processing During Training

During training, the data pipeline handles SMILES molecular data with several augmentation and preprocessing steps.

```mermaid
flowchart LR
    subgraph "Training Data Pipeline"
        data["model.data"] --> format{"dataset_format"}
        format --> |"csv"| csv["CSV Dataset"]
        format --> |"bin"| bin["Binary Dataset"]
        
        csv --> mol["MoleculeEnumeration"]
        bin --> mol
        
        mol --> |"processes"| aug["Data Augmentation"]
        aug --> mask["SMILES Masking"]
        aug --> rand["SMILES Randomization"]
        
        mask --> batch["Training Batch"]
        rand --> batch
        
        batch --> |"fed to"| model["MegaMolBARTModel"]
        model --> |"computes"| loss["Loss"]
    end
```

Sources: [examples/chem/megamolbart_pretrain.py:112-126]()

## Running Training

To launch a training job, use the `megamolbart_pretrain.py` script with the appropriate configuration file:

```bash
python examples/chem/megamolbart_pretrain.py --config-name=megamolbart_pretrain_xsmall_span_aug
```

The script supports the following operations based on configuration:

- **Data Preprocessing**: When `do_training=False`, the script prepares datasets from raw SMILES data
- **Model Training**: When `do_training=True`, the script trains the model using the prepared datasets
- **Model Testing**: When `do_testing=True`, the script evaluates the model on test data

Sources: [examples/chem/megamolbart_pretrain.py:108-131]()

## Checkpointing and Resuming

The training system includes robust checkpointing capabilities that allow training to be paused and resumed. Checkpoints are managed by PyTorch Lightning's CheckpointConnector with customizations for efficient distributed training.

```mermaid
flowchart TD
    subgraph "Checkpoint Management"
        trainer["Trainer"] --> connector["CheckpointConnector"]
        
        subgraph "Resuming Options"
            cfg["cfg.model.resume_from_checkpoint"] --> |"specified"| resume["Resume from specified path"]
            cfg --> |"not specified"| auto["Resume from automatically found checkpoint"]
        end
        
        connector --> |"handles"| save["Save Checkpoints"]
        connector --> |"handles"| load["Load Checkpoints"]
        
        exp["exp_manager()"] --> |"configures"| dir["Checkpoint Directory"]
        exp --> |"finds"| last["Last Checkpoint"]
    end
```

Sources: [examples/chem/megamolbart_pretrain.py:66-83]()

## Model Sizes and Resource Requirements

MegaMolBART provides several pre-configured model sizes with corresponding resource requirements:

| Model Size | Layers | Hidden Size | Attention Heads | GPU Requirements |
|------------|--------|-------------|----------------|------------------|
| XSmall     | 2      | 256         | 4              | 1 device, 1 node |
| Small      | 6      | 512         | 8              | 8 devices, 8 nodes (64 GPUs) |
| Large      | 8      | 1024        | 16             | 8 devices, 8 nodes (64 GPUs) |

For smaller experimental runs, the XSmall configuration can be used on a single GPU, while the larger models are designed for multi-node distributed training environments.

Sources: [examples/chem/conf/megamolbart_pretrain_xsmall_span_aug.yaml:1-13](), [examples/chem/conf/megamolbart_pretrain_small_span_aug.yaml:1-14](), [examples/chem/conf/megamolbart_pretrain_large_span_aug.yaml:1-14]()

---

