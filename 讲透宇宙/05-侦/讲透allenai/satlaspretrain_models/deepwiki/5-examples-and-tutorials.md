<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/satlaspretrain_models · page 5 Examples and Tutorials · fetched 2026-10-26 -->

# Examples and Tutorials

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [demo.ipynb](demo.ipynb)
- [torchgeo_demo.ipynb](torchgeo_demo.ipynb)

</details>



This page provides practical examples and step-by-step tutorials for using the satlaspretrain_models library. The examples demonstrate common workflows from basic model loading to complete fine-tuning pipelines for satellite imagery analysis tasks.

For installation and initial setup instructions, see [Installation](#2.1). For detailed API documentation, see [Core API Reference](#3).

## Overview of Available Examples

The library includes several demonstration notebooks and tutorials that showcase different usage patterns:

| Example Type | Purpose | Complexity | Key Components |
|--------------|---------|------------|----------------|
| Basic Usage | Model loading and inference | Beginner | `get_pretrained_model`, backbone extraction |
| TorchGeo Integration | Fine-tuning with geospatial datasets | Intermediate | TorchGeo datamodules, PyTorch Lightning |
| Custom Fine-tuning | Task-specific model adaptation | Advanced | Custom heads, training loops |

## Common Usage Workflows

The following diagram illustrates the typical workflows for using pre-trained models from this library:

```mermaid
flowchart TD
    A["User Starts"] --> B{"Usage Goal?"}
    
    B -->|"Feature Extraction"| C["Load Backbone Only"]
    B -->|"Fine-tuning"| D["Load Backbone + Task Head"]
    B -->|"Transfer Learning"| E["Load Full Model"]
    
    C --> F["get_pretrained_model()"]
    D --> F
    E --> F
    
    F --> G["Model Configuration"]
    G --> H{"Integration Type?"}
    
    H -->|"Standalone"| I["Direct PyTorch Usage"]
    H -->|"TorchGeo"| J["TorchGeo Datamodules"]
    H -->|"Custom Pipeline"| K["Custom Training Loop"]
    
    I --> L["Inference/Feature Extraction"]
    J --> M["Lightning Trainer"]
    K --> N["Manual Training"]
    
    M --> O["Fine-tuned Model"]
    N --> O
    
    L --> P["Results"]
    O --> P
```

Sources: [torchgeo_demo.ipynb:1-246]()

## TorchGeo Integration Example

The library provides seamless integration with TorchGeo for geospatial deep learning workflows. The primary example demonstrates fine-tuning on the UCMerced land use classification dataset:

```mermaid
flowchart LR
    A["UCMercedDataModule"] --> B["SatlasClassificationTask"]
    B --> C["configure_models()"]
    
    C --> D["Swin_V2_B_Weights.SENTINEL2_RGB_SI_SATLAS"]
    D --> E["swin_v2_b(weights)"]
    
    E --> F["Model Architecture Adaptation"]
    F --> G["Input Layer: Conv2d(3, ...)"]
    F --> H["Output Layer: Linear(..., 21)"]
    
    G --> I["Lightning Trainer"]
    H --> I
    
    I --> J["trainer.fit()"]
    J --> K["Fine-tuned Classification Model"]
    
    subgraph "Key Code Entities"
        L["ClassificationTask"]
        M["torch.nn.Conv2d"]
        N["torch.nn.Linear"]
    end
```

The implementation follows this pattern in the notebook:

- **Data Setup**: Uses `UCMercedDataModule` for automatic dataset management [torchgeo_demo.ipynb:68-72]()
- **Model Configuration**: Extends `ClassificationTask` to load Satlas weights [torchgeo_demo.ipynb:83-111]()
- **Architecture Adaptation**: Modifies input channels and output classes [torchgeo_demo.ipynb:88-98]()
- **Training Setup**: Configures `Trainer` with appropriate settings [torchgeo_demo.ipynb:146-153]()

Sources: [torchgeo_demo.ipynb:35-44](), [torchgeo_demo.ipynb:83-111](), [torchgeo_demo.ipynb:146-153]()

## Model Loading and Adaptation Patterns

The following diagram shows the key code entities involved in adapting pre-trained models for downstream tasks:

```mermaid
flowchart TD
    A["Swin_V2_B_Weights.SENTINEL2_RGB_SI_SATLAS"] --> B["swin_v2_b()"]
    
    B --> C["SwinTransformer Model"]
    
    C --> D{"Layer Adaptation"}
    D --> E["model.features[0][0]"]
    D --> F["model.head"]
    
    E --> G["torch.nn.Conv2d replacement"]
    F --> H["torch.nn.Linear replacement"]
    
    G --> I["Input Channel Matching"]
    H --> J["Output Class Matching"]
    
    I --> K["Adapted Model"]
    J --> K
    
    K --> L["trainer.fit(model=task)"]
    
    subgraph "Configuration Parameters"
        M["in_channels=3"]
        N["out_features=21"]
        O["num_classes=21"]
    end
```

Key adaptation steps include:
- **Input Layer Modification**: Replacing `model.features[0][0]` to match input channels [torchgeo_demo.ipynb:89-95]()
- **Output Layer Modification**: Replacing `model.head` for task-specific classes [torchgeo_demo.ipynb:98]()
- **Parameter Preservation**: Maintaining kernel sizes and architectural properties [torchgeo_demo.ipynb:92-94]()

Sources: [torchgeo_demo.ipynb:84-98]()

## Training Configuration Examples

The library examples demonstrate various training configurations optimized for satellite imagery tasks:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| `batch_size` | 8 | Memory-efficient processing |
| `max_epochs` | 10 | Quick demonstration training |
| `num_workers` | 2 | Parallel data loading |
| `accelerator` | "gpu" or "cpu" | Hardware adaptation |

The training setup pattern follows:

```mermaid
flowchart LR
    A["Trainer Configuration"] --> B["accelerator selection"]
    A --> C["default_root_dir"]
    A --> D["max_epochs"]
    A --> E["log_every_n_steps"]
    
    B --> F["torch.cuda.is_available()"]
    C --> G["tempfile.gettempdir()"]
    
    F --> H["Trainer()"]
    G --> H
    D --> H
    E --> H
    
    H --> I["trainer.fit()"]
    I --> J["model=task"]
    I --> K["datamodule=datamodule"]
```

Sources: [torchgeo_demo.ipynb:54-58](), [torchgeo_demo.ipynb:143-153]()

## Environment Setup Requirements

The examples require specific environment configurations depending on the integration type:

- **TorchGeo Integration**: Requires separate conda environment with TorchGeo from git [torchgeo_demo.ipynb:13-17]()
- **Dependencies**: PyTorch Lightning, TorchGeo, and standard PyTorch stack [torchgeo_demo.ipynb:36-44]()
- **Hardware**: Supports both GPU and CPU execution with automatic detection [torchgeo_demo.ipynb:143]()

For detailed tutorials on specific use cases, see [Basic Usage Examples](#5.1) and [Fine-tuning Tutorial](#5.2).

Sources: [torchgeo_demo.ipynb:13-17](), [torchgeo_demo.ipynb:36-44](), [torchgeo_demo.ipynb:143-153]()

---

