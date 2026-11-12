<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/molmo · page 3 Training · fetched 2026-10-26 -->

# Training

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [launch_scripts/train_captioner.py](launch_scripts/train_captioner.py)
- [launch_scripts/train_multitask_model.py](launch_scripts/train_multitask_model.py)

</details>



This page provides an overview of the training process for Molmo multimodal language models. It covers the general training architecture, workflow, and key components involved in training Molmo models. For detailed information about specific training approaches, see [Captioner Training](#3.1) and [Multitask Training](#3.2). For a comprehensive guide to training configuration options, see [Training Configuration](#3.3).

## Training Architecture

The Molmo training system is built to efficiently train multimodal models that integrate vision encoders with language models. The training architecture is designed to support both pre-training on captioning data and fine-tuning on multitask data.

### High-Level Training Architecture

```mermaid
flowchart TD
    subgraph "Training Initialization"
        TC["TrainConfig"] --> M["ModelConfig"]
        TC --> DC["DataConfig"]
        TC --> OC["OptimizerConfig"]
        TC --> SC["SchedulerConfig"]
        TC --> FC["FSDPConfig"]
        
        PT["Pre-trained Models"] --> VE["Vision Encoder<br>(CLIP, SigLIP, etc.)"]
        PT --> LM["Language Model<br>(OLMo, Qwen2, etc.)"]
    end
    
    subgraph "Training Pipeline"
        M --> |"initialize_model()"| Model["Molmo Model"]
        DC --> |"build_data_loader()"| DL["Data Loader"]
        OC --> |"build_optimizer()"| Opt["Optimizer"]
        SC --> |"build_scheduler()"| Sched["Scheduler"]
        FC --> |"setup_fsdp()"| FSDP["FSDP Wrapper"]
        
        DL --> Batch["Training Batch"]
        Batch --> FP["Forward Pass"]
        FP --> Loss["Loss Calculation"]
        Loss --> BP["Backward Pass"]
        BP --> Opt
        Opt --> Sched
        
        Checkpoint["Checkpointing<br>save_interval"] --> |"save_model()"| SavedModel["Model Checkpoint"]
    end
    
    subgraph "Evaluation"
        SavedModel --> Eval["Evaluation<br>eval_interval"]
        Eval --> Metrics["Training Metrics"]
    end
```

Sources: [launch_scripts/train_captioner.py:110-203](), [launch_scripts/train_multitask_model.py:209-295]()

## Training Types

Molmo supports two primary training workflows:

### Captioner Training

Captioner training focuses on teaching the model to generate text descriptions for images. This is typically the first stage of training, where the model learns to understand and describe visual content.

```mermaid
flowchart LR
    subgraph "Captioner Training Flow"
        pixmo["PixMo-Cap Dataset"] --> |"train_captioner.py"| model["Molmo Model"]
        model --> caption["Image Captions"]
    end
```

Sources: [launch_scripts/train_captioner.py:1-212](), [README.md:258-276]()

### Multitask Training

Multitask training builds on top of captioner training by incorporating various multimodal tasks such as visual question answering, pointing, counting, and more. This is typically the second stage of training, where a previously trained captioner model is fine-tuned on multiple tasks.

```mermaid
flowchart LR
    subgraph "Multitask Training Flow"
        mixtures["Dataset Mixtures"] --> |"train_multitask_model.py"| model["Pre-trained Captioner"]
        model --> mmodel["Multitask Molmo"]
    end
    
    subgraph "Dataset Mixtures"
        demo["Demo Tasks<br>- pixmo_ask_model_anything<br>- pixmo_cap<br>- pixmo_cap_qa<br>- pixmo_pointing_explanations"]
        aux["Auxiliary Tasks<br>- chart_qa<br>- doc_qa<br>- vqa_tasks<br>- many others"]
        pointing["Pointing Tasks<br>- pixmo_points<br>- pixmo_count<br>- pointing_tasks"]
    end
```

Sources: [launch_scripts/train_multitask_model.py:1-304](), [README.md:278-295]()

## Key Components

### Configuration System

The Molmo training system uses a hierarchical configuration system to define all aspects of training. The `TrainConfig` class is the root configuration that contains nested configurations for model, data, optimizer, scheduler, and FSDP.

```mermaid
classDiagram
    class TrainConfig {
        +model: ModelConfig
        +data: DataConfig
        +optimizer: OptimizerConfig
        +scheduler: SchedulerConfig
        +fsdp: FSDPConfig
        +wandb: WandbConfig
        +max_duration: int
        +global_train_batch_size: int
        +device_train_microbatch_size: int
        +save_interval: int
        +eval_interval: int
    }
    
    class ModelConfig {
        +vision_backbone: VisionBackboneConfig
        +tokenizer: TokenizerConfig
        +crop_mode: str
        +max_crops: int
        +vit_layers: List[int]
    }
    
    class DataConfig {
        +dataset: str
        +sequence_length: int
        +split: str
        +shuffle: bool
    }
    
    class OptimizerConfig {
        +name: OptimizerType
        +connector_learning_rate: float
        +vit_learning_rate: float
        +llm_learning_rate: float
    }
    
    class SchedulerConfig {
        +name: SchedulerType
        +connector_t_warmup: int
        +vit_t_warmup: int
        +llm_t_warmup: int
    }
    
    TrainConfig --> ModelConfig
    TrainConfig --> DataConfig
    TrainConfig --> OptimizerConfig
    TrainConfig --> SchedulerConfig
```

Sources: [launch_scripts/train_captioner.py:110-203](), [launch_scripts/train_multitask_model.py:209-295]()

### Model Components

During training, different components of the model can be selectively fine-tuned:

| Component       | Control Flag   | Learning Rate Parameter     | Description                                      |
|-----------------|----------------|----------------------------|--------------------------------------------------|
| Vision Encoder  | `ft_vit`       | `vit_learning_rate`        | The vision component (CLIP, SigLIP, etc.)        |
| Connector       | `ft_connector` | `connector_learning_rate`  | Module connecting vision and language components |
| Language Model  | `ft_llm`       | `llm_learning_rate`        | The text generation component (OLMo, Qwen2)      |

Sources: [launch_scripts/train_captioner.py:137-139](), [launch_scripts/train_multitask_model.py:239-241]()

## Distributed Training

Molmo uses PyTorch's Fully Sharded Data Parallel (FSDP) for efficient distributed training across multiple GPUs and potentially multiple nodes.

```mermaid
flowchart TD
    subgraph "Distributed Training"
        torchrun["torchrun<br>--nproc-per-node=N"] --> FSDP["FSDP Wrapper"]
        
        subgraph "Model Sharding"
            FSDP --> GPU1["GPU 1<br>Model Shard"]
            FSDP --> GPU2["GPU 2<br>Model Shard"]
            FSDP --> GPUN["GPU N<br>Model Shard"]
        end
        
        subgraph "Data Parallelism"
            B1["Batch 1"] --> GPU1
            B2["Batch 2"] --> GPU2
            BN["Batch N"] --> GPUN
        end
        
        subgraph "Gradient Synchronization"
            GPU1 --> AllReduce["All-Reduce"]
            GPU2 --> AllReduce
            GPUN --> AllReduce
        end
    end
```

Sources: [README.md:303-310](), [launch_scripts/train_captioner.py:164-169](), [launch_scripts/train_multitask_model.py:266-270]()

## Training Workflow

The typical workflow for training a Molmo model involves:

1. **Initialization Phase**:
   - Download pre-trained models for initialization
   - Configure training parameters
   - Set up distributed training environment

2. **Captioner Training**:
   - Train on the PixMo-Cap dataset to learn basic image-text alignment
   - Example command:
     ```
     torchrun --nproc-per-node=8 launch_scripts/train_captioner.py qwen2_7b --save_folder=/path/to/save/folder
     ```

3. **Multitask Training**:
   - Fine-tune the captioner model on a mixture of tasks
   - Example command:
     ```
     torchrun --nproc-per-node=8 launch_scripts/train_multitask_model.py 3.2-synthetic /path/to/captioner/checkpoint --save_folder=/path/to/save/folder
     ```

4. **Evaluation**:
   - Periodic evaluation during training at intervals specified by `eval_interval`
   - Comprehensive evaluation after training

Sources: [README.md:242-295](), [launch_scripts/train_captioner.py:29-212](), [launch_scripts/train_multitask_model.py:72-304]()

## Common Training Parameters

Below are some important training parameters that can be configured:

| Parameter                    | Description                                                |
|------------------------------|------------------------------------------------------------|
| `global_batch_size`          | Total batch size across all GPUs                           |
| `device_train_microbatch_size` | Batch size per GPU                                       |
| `seq_len`                    | Maximum sequence length for training                       |
| `max_duration`               | Maximum number of training steps                           |
| `save_interval`              | Number of steps between checkpoints                        |
| `eval_interval`              | Number of steps between evaluations                        |
| `learning_rates`             | Separate learning rates for vision, connector, and LLM components |
| `warmup_steps`               | Steps for learning rate warmup                             |

For a complete list of configuration options, see [Training Configuration](#3.3).

Sources: [launch_scripts/train_captioner.py:110-203](), [launch_scripts/train_multitask_model.py:209-295]()

## Data Mixtures for Training

For multitask training, Molmo uses a mixture of datasets with configurable proportions:

```mermaid
flowchart TD
    subgraph "Data Mixture Example"
        MM["RootSizeMixture"] --> |"15%"| Demo["Demo Tasks"]
        MM --> |"50%"| Aux["Auxiliary Tasks"]
        MM --> |"35%"| Pointing["Pointing Tasks"]
        
        Demo --> AMA["pixmo_ask_model_anything"]
        Demo --> Cap["pixmo_cap"]
        Demo --> CapQA["pixmo_cap_qa"]
        Demo --> PE["pixmo_pointing_explanations"]
        
        Aux --> ChartQA["chart_qa"]
        Aux --> DocQA["doc_qa"]
        Aux --> VQA["coco_2014_vqa_multi"]
        Aux --> Others["...other auxiliary tasks"]
        
        Pointing --> Points["pixmo_points"]
        Pointing --> Count["pixmo_count"]
        Pointing --> HC["pixmo_points_high_freq_counting"]
    end
```

Sources: [launch_scripts/train_multitask_model.py:28-143](), [launch_scripts/train_multitask_model.py:192-195]()

## Further Reading

For more detailed information about specific aspects of training, refer to:
- [Captioner Training](#3.1) for details on training image captioning models
- [Multitask Training](#3.2) for information on training models across various tasks
- [Training Configuration](#3.3) for comprehensive documentation on configuration options
- [Datasets](#2) for information about the data used for training
- [Evaluation](#4) for understanding how models are evaluated during and after training

---

