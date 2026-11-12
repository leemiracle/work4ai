<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/semantic-segmentation · page 3 System Architecture · fetched 2026-10-26 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [config.py](config.py)

</details>



This document provides a detailed overview of the system architecture for NVIDIA's semantic segmentation implementation. It covers the core components, their interactions, and the overall data flow through the system. For installation instructions, see [Installation and Environment Setup](#2.1), and for dataset preparation information, see [Dataset Preparation](#2.2).

## Overall Architecture

The semantic segmentation system implements the "Hierarchical Multi-Scale Attention for Semantic Segmentation" approach described in the repository's associated paper. The architecture consists of several key components that work together to enable efficient training and inference for semantic segmentation tasks.

```mermaid
flowchart TD
    subgraph "Configuration System"
        config["config.py<br>Configuration Manager"]
    end

    subgraph "Dataset Pipeline"
        dataset_init["datasets/__init__.py<br>setup_loaders()"]
        base_loader["BaseLoader<br>Common Dataset Functionality"]
        cityscapes["Cityscapes Dataset"]
        mapillary["Mapillary Dataset"]
        transforms["Data Transforms<br>Joint/Image/Label"]
    end

    subgraph "Model Architecture"
        hrnet["HRNet<br>Backbone Network"]
        ocr["OCR Module<br>Object Context Representation"]
        mscale["Multi-scale Attention<br>Hierarchical Attention"]
    end

    subgraph "Training Pipeline"
        train["train.py<br>Training Loop"]
        loss["Loss Functions<br>OCR+Segmentation"]
        optimizer["Optimizer"]
    end

    subgraph "Evaluation"
        eval["Evaluation Scripts<br>eval_*.yml"]
        dump["Visualization<br>dump_*.yml"]
    end

    subgraph "Experiment Management"
        runx["runx<br>Experiment Runner"]
        yml["YAML Configuration<br>*.yml files"]
    end

    config --> dataset_init
    config --> hrnet
    config --> ocr
    config --> mscale
    config --> train
    config --> loss

    dataset_init --> base_loader
    base_loader --> cityscapes
    base_loader --> mapillary
    cityscapes --> train
    mapillary --> train
    transforms --> cityscapes
    transforms --> mapillary

    hrnet --> ocr
    ocr --> mscale
    mscale --> train

    train --> loss
    train --> optimizer

    yml --> runx
    runx --> train
    runx --> eval
    runx --> dump

    train --> eval
    train --> dump
```

Sources: [README.md:1-107](), [config.py:32-68]()

## Configuration System

The configuration system serves as the central manager for all parameters and settings in the semantic segmentation framework, allowing for consistent configuration across all components.

```mermaid
flowchart LR
    subgraph "Configuration Definition"
        config_file["config.py<br>__C AttrDict"]
        defaults["Default Parameters"]
        cmd_args["Command Line Arguments"]
    end

    subgraph "Configuration Categories"
        dataset_cfg["DATASET<br>Data Parameters"]
        model_cfg["MODEL<br>Architecture Parameters"]
        train_cfg["TRAIN<br>Training Parameters"]
        loss_cfg["LOSS<br>Loss Parameters"]
        ocr_cfg["MODEL.OCR<br>OCR Module Parameters"]
    end

    subgraph "Configuration Users"
        dataset_loader["Dataset Loader"]
        model_builder["Model Builder"]
        train_loop["Training Loop"]
        eval_script["Evaluation Script"]
    end

    config_file --> defaults
    cmd_args --> assert_infer["assert_and_infer_cfg()<br>Parameter Processing"]
    defaults --> assert_infer
    
    assert_infer --> dataset_cfg
    assert_infer --> model_cfg
    assert_infer --> train_cfg
    assert_infer --> loss_cfg
    assert_infer --> ocr_cfg
    
    dataset_cfg --> dataset_loader
    model_cfg --> model_builder
    ocr_cfg --> model_builder
    train_cfg --> train_loop
    loss_cfg --> train_loop
    
    dataset_loader --> train_loop
    model_builder --> train_loop
    train_loop --> eval_script
```

The configuration system is defined in `config.py` and uses an `AttrDict` class to create a hierarchical parameter structure. Key configuration categories include:

| Configuration Category | Purpose | Example Parameters |
|-----------------------|---------|-------------------|
| `DATASET` | Dataset paths and loading parameters | `CITYSCAPES_DIR`, `MAPILLARY_DIR`, `CLASS_UNIFORM_PCT` |
| `MODEL` | Model architecture configuration | `MSCALE`, `ALIGN_CORNERS`, `OCR` settings |
| `TRAIN` | Training process parameters | `FP16`, `RANDOM_BRIGHTNESS_SHIFT_VALUE` |
| `LOSS` | Loss function configuration | `OCR_ALPHA`, `OCR_AUX_RMI` |

The function `assert_and_infer_cfg()` processes command-line arguments to update the default configuration, ensuring consistency across the entire system.

Sources: [config.py:32-383]()

## Dataset Pipeline

The dataset pipeline manages the loading, processing, and batching of image data for training and evaluation.

```mermaid
flowchart TD
    subgraph "Dataset Configuration"
        dataset_cfg["config.DATASET<br>Dataset Parameters"]
        paths["Dataset Paths<br>CITYSCAPES_DIR, MAPILLARY_DIR"]
    end

    subgraph "Dataset Initialization"
        setup_loaders["setup_loaders()<br>datasets/__init__.py"]
        base_loader["BaseLoader<br>Common Functionality"]
    end

    subgraph "Dataset Implementations"
        cityscapes["Cityscapes<br>cityscapes.py"]
        mapillary["Mapillary<br>mapillary.py"]
    end

    subgraph "Data Processing"
        joint_transforms["Joint Transforms<br>Image+Label"]
        img_transforms["Image Transforms"]
        label_transforms["Label Transforms"]
        class_uniform["Class Uniform Sampling<br>For Balanced Training"]
    end

    subgraph "DataLoader Creation"
        train_loader["Training DataLoader"]
        val_loader["Validation DataLoader"]
    end

    dataset_cfg --> paths
    paths --> setup_loaders
    dataset_cfg --> setup_loaders
    
    setup_loaders --> base_loader
    base_loader --> cityscapes
    base_loader --> mapillary
    
    cityscapes --> joint_transforms
    cityscapes --> img_transforms
    cityscapes --> label_transforms
    mapillary --> joint_transforms
    mapillary --> img_transforms
    mapillary --> label_transforms
    
    cityscapes --> class_uniform
    mapillary --> class_uniform
    
    cityscapes --> train_loader
    mapillary --> train_loader
    cityscapes --> val_loader
    mapillary --> val_loader
```

The dataset pipeline consists of:

1. **Dataset Configuration**: Parameters in `config.py` define dataset paths and loading settings
2. **Dataset Initialization**: The `setup_loaders()` function in `datasets/__init__.py` creates appropriate dataset instances
3. **BaseLoader**: Provides common functionality for all dataset implementations
4. **Dataset Implementations**: Specific implementations for Cityscapes and Mapillary
5. **Data Processing**: Transforms for augmentation and normalization
6. **Class Uniform Sampling**: Ensures balanced class representation during training
7. **DataLoader Creation**: Batching and shuffling data for training and validation

The system supports multiple datasets with cross-validation splits, class-uniform sampling for handling imbalanced classes, and various data augmentation techniques.

Sources: [README.md:26-42](), [config.py:75-117]()

## Model Architecture

The model architecture implements the "Hierarchical Multi-Scale Attention for Semantic Segmentation" approach with three main components: HRNet backbone, OCR module, and multi-scale attention.

```mermaid
flowchart TD
    subgraph "Input"
        input["Input Image"]
    end

    subgraph "HRNet Backbone"
        hrnet["HRNetV2<br>Multi-Resolution Features"]
        stage1["Stage 1<br>Single Resolution"]
        stage2["Stage 2<br>Two Resolutions"]
        stage3["Stage 3<br>Three Resolutions"]
        stage4["Stage 4<br>Four Resolutions"]
    end

    subgraph "OCR Module"
        feat["Feature Maps"]
        soft_regions["Soft Object Regions"]
        context["Object Context"]
        ocr_output["OCR Enhanced Features"]
    end

    subgraph "Multi-scale Attention"
        main_scale["Main Scale<br>(1.0x)"]
        lo_scale["Low Scale<br>(config.MODEL.MSCALE_LO_SCALE)"]
        extra_scales["Extra Scales<br>(config.MODEL.EXTRA_SCALES)"]
        attn_weights["Attention Weights"]
        fused_pred["Scale-Fused Prediction"]
    end

    subgraph "Output"
        output["Semantic Segmentation<br>Class Predictions"]
    end

    input --> hrnet
    hrnet --> stage1
    stage1 --> stage2
    stage2 --> stage3
    stage3 --> stage4
    stage4 --> feat
    
    feat --> soft_regions
    feat --> context
    soft_regions --> context
    context --> ocr_output
    
    ocr_output --> main_scale
    ocr_output --> lo_scale
    ocr_output --> extra_scales
    
    main_scale --> attn_weights
    lo_scale --> attn_weights
    extra_scales --> attn_weights
    
    main_scale --> fused_pred
    lo_scale --> fused_pred
    extra_scales --> fused_pred
    attn_weights --> fused_pred
    
    fused_pred --> output
```

Key components of the model architecture include:

1. **HRNet Backbone**: Maintains high-resolution representations throughout the network, generating multi-scale feature maps.
   - Configured through parameters in `config.MODEL.OCR_EXTRA`
   - Uses a pre-trained HRNet model from `__C.MODEL.HRNET_CHECKPOINT`

2. **OCR (Object Context Representation)**: Enhances features with object context information.
   - Takes feature maps from HRNet as input
   - Generates soft object regions
   - Aggregates object context
   - Parameters controlled by `config.MODEL.OCR.MID_CHANNELS` and `config.MODEL.OCR.KEY_CHANNELS`

3. **Multi-scale Attention**: Fuses predictions from multiple scales using attention mechanisms.
   - Processes features at multiple scales (main, low, and extra scales)
   - Generates attention weights for each scale
   - Combines predictions using attention weights
   - Controlled by parameters like `config.MODEL.MSCALE_LO_SCALE` and `config.MODEL.EXTRA_SCALES`

The entire architecture is highly configurable through parameters in `config.py`, allowing for experimentation with different model configurations.

Sources: [README.md:3-3](), [config.py:119-190]()

## Training and Evaluation Pipeline

The training and evaluation pipeline manages the model training process, evaluation, and result visualization.

```mermaid
flowchart TD
    subgraph "Configuration"
        config["config.py<br>System Configuration"]
        args["Command Line Arguments"]
        yml["YAML Configuration<br>train_*.yml, eval_*.yml"]
    end

    subgraph "Data Preparation"
        setup_loaders["setup_loaders()<br>datasets/__init__.py"]
        train_loader["Training DataLoader"]
        val_loader["Validation DataLoader"]
    end

    subgraph "Model Setup"
        model_builder["Model Builder"]
        model["Segmentation Model<br>HRNet+OCR+MScale"]
        optimizer["Optimizer"]
        scheduler["Learning Rate Scheduler"]
    end

    subgraph "Training Loop"
        epoch_loop["Epoch Loop<br>train.py"]
        batch_loop["Batch Iteration"]
        forward["Forward Pass"]
        losses["Loss Calculation<br>Main + OCR Aux Loss"]
        backward["Backward Pass"]
        update["Parameter Update"]
        validation["Periodic Validation"]
    end

    subgraph "Evaluation"
        eval_script["Evaluation Script<br>eval_*.yml"]
        metrics["Metric Calculation<br>IOU, Accuracy"]
        visualization["Result Visualization<br>dump_*.yml"]
    end

    config --> setup_loaders
    args --> config
    yml --> runx["runx<br>Experiment Runner"]
    runx --> args

    setup_loaders --> train_loader
    setup_loaders --> val_loader

    config --> model_builder
    model_builder --> model
    model --> optimizer
    model --> scheduler

    train_loader --> epoch_loop
    model --> epoch_loop
    optimizer --> epoch_loop
    scheduler --> epoch_loop

    epoch_loop --> batch_loop
    batch_loop --> forward
    forward --> losses
    losses --> backward
    backward --> update
    epoch_loop --> validation
    val_loader --> validation

    model --> eval_script
    val_loader --> eval_script
    eval_script --> metrics
    eval_script --> visualization
```

The training and evaluation pipeline consists of:

1. **Configuration**: Parameters from `config.py`, command-line arguments, and YAML configuration files
2. **Data Preparation**: Dataset loaders for training and validation
3. **Model Setup**: Initializing the segmentation model, optimizer, and learning rate scheduler
4. **Training Loop**: Iterating through epochs and batches, updating model parameters
   - Forward pass through the model
   - Loss calculation (main segmentation loss + OCR auxiliary loss)
   - Backward pass for gradient calculation
   - Parameter updates
   - Periodic validation

5. **Evaluation**: Assessing model performance and visualizing results
   - IOU (Intersection over Union) calculation
   - Visualization of segmentation outputs

The system uses the `runx` tool for experiment management, which provides a convenient way to configure and run training and evaluation jobs.

Sources: [README.md:46-108](), [config.py:204-383]()

## Experiment Management

The experiment management system uses `runx` to configure, run, and track experiments.

```mermaid
flowchart LR
    subgraph "Configuration Files"
        train_yml["Training Scripts<br>train_*.yml"]
        eval_yml["Evaluation Scripts<br>eval_*.yml"]
        dump_yml["Visualization Scripts<br>dump_*.yml"]
    end

    subgraph "runx System"
        runx_cli["runx CLI<br>Experiment Runner"]
        args_parser["Arguments Parser"]
        job_manager["Job Manager"]
    end

    subgraph "Execution"
        train_script["train.py<br>Training Script"]
        eval_script["Evaluation Script"]
        dump_script["Visualization Script"]
    end

    subgraph "Outputs"
        logs["Log Files<br>Training Progress"]
        checkpoints["Model Checkpoints"]
        metrics["Evaluation Metrics"]
        visualizations["Output Visualizations"]
    end

    train_yml --> runx_cli
    eval_yml --> runx_cli
    dump_yml --> runx_cli
    
    runx_cli --> args_parser
    args_parser --> job_manager
    
    job_manager --> train_script
    job_manager --> eval_script
    job_manager --> dump_script
    
    train_script --> logs
    train_script --> checkpoints
    eval_script --> metrics
    dump_script --> visualizations
```

The experiment management system handles:

1. **Configuration Files**: YAML files for different experiment types
   - `train_*.yml`: Training configurations
   - `eval_*.yml`: Evaluation configurations 
   - `dump_*.yml`: Visualization configurations

2. **runx CLI**: Command-line interface for running experiments
   - Parses experiment configuration
   - Manages job execution
   - Example: `python -m runx.runx scripts/train_cityscapes.yml -i`

3. **Execution**: Running the appropriate scripts with the specified parameters
   - Training script (`train.py`)
   - Evaluation scripts
   - Visualization scripts

4. **Outputs**: Storing experiment results
   - Log files with training progress
   - Model checkpoints
   - Evaluation metrics
   - Output visualizations

This system enables efficient experimentation by simplifying the process of configuring and running different training and evaluation scenarios.

Sources: [README.md:46-108]()

## System Integration

This diagram shows how all components integrate to form the complete semantic segmentation system:

```mermaid
flowchart TD
    subgraph "Input"
        raw_data["Raw Images<br>Cityscapes/Mapillary"]
        config_files["Configuration Files<br>config.py, *.yml"]
    end

    subgraph "Core System"
        config_system["Configuration System<br>config.py"]
        dataset_system["Dataset System<br>BaseLoader, Dataset Implementations"]
        model_system["Model System<br>HRNet+OCR+MScale"]
        training_system["Training System<br>train.py"]
        eval_system["Evaluation System<br>eval_*.yml scripts"]
    end

    subgraph "Experiment Management"
        runx_system["runx<br>Experiment Runner"]
    end

    subgraph "Output"
        checkpoints["Model Checkpoints<br>Trained Models"]
        eval_results["Evaluation Results<br>IOU Metrics"]
        visualizations["Visualizations<br>Segmentation Maps"]
    end

    raw_data --> dataset_system
    config_files --> config_system
    config_files --> runx_system
    
    config_system --> dataset_system
    config_system --> model_system
    config_system --> training_system
    config_system --> eval_system
    
    dataset_system --> training_system
    model_system --> training_system
    
    runx_system --> training_system
    runx_system --> eval_system
    
    training_system --> checkpoints
    eval_system --> eval_results
    eval_system --> visualizations
    
    checkpoints --> eval_system
```

The complete system integrates all components through:

1. **Configuration Flow**: Configuration parameters from `config.py` and YAML files flow through to all components
2. **Data Flow**: Raw image data flows through the dataset pipeline to the training and evaluation systems
3. **Model Flow**: The model architecture receives processed data and produces segmentation outputs
4. **Result Flow**: Model outputs flow through evaluation to produce metrics and visualizations

This integration ensures all components work together efficiently to train and evaluate semantic segmentation models.

Sources: [README.md:1-108](), [config.py:1-383]()

---

