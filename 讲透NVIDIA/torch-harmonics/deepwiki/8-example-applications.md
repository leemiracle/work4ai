<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/torch-harmonics · page 8 Example Applications · fetched 2026-10-26 -->

# Example Applications

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/baseline_models/segformer.py](examples/baseline_models/segformer.py)
- [examples/baseline_models/transformer.py](examples/baseline_models/transformer.py)
- [examples/depth/train.py](examples/depth/train.py)
- [examples/segmentation/train.py](examples/segmentation/train.py)
- [torch_harmonics/examples/models/lsno.py](torch_harmonics/examples/models/lsno.py)
- [torch_harmonics/examples/models/sfno.py](torch_harmonics/examples/models/sfno.py)
- [torch_harmonics/examples/pde_dataset.py](torch_harmonics/examples/pde_dataset.py)

</details>



## Purpose and Scope

This page provides an overview of the complete example applications included with torch-harmonics, demonstrating practical usage of the library's capabilities across different problem domains. These examples serve as reference implementations showing how to combine the core components (spherical transforms, convolutions, attention mechanisms) into end-to-end machine learning pipelines.

For detailed documentation on the underlying model architectures, see [Neural Operator Architectures](#7). For information on the core mathematical operations used in these examples, see [Spherical Harmonic Transforms](#2), [DISCO Convolutions](#3), and [Spherical Attention Mechanisms](#4).

## Application Domains

torch-harmonics includes three primary application domains, each targeting different types of problems on spherical data:

| Domain | Task Type | Dataset | Input/Output | Primary Models |
|--------|-----------|---------|--------------|----------------|
| Depth Estimation | Regression | Stanford 2D3DS | RGB → Depth map | S2 Transformer, S2 Segformer, SFNO, LSNO |
| Semantic Segmentation | Multi-class Classification | Stanford 2D3DS | RGB → Class labels | S2 Segformer, S2 Transformer, SFNO, LSNO |
| PDE Solving | Operator Learning | Shallow Water Equations | Initial state → Future state | SFNO, LSNO |

**Vision Tasks** (Depth Estimation and Semantic Segmentation): These applications process spherical panoramic images from indoor environments. The Stanford 2D3DS dataset provides equirectangular projections with depth annotations and semantic labels for 13 object classes.

**PDE Tasks**: Neural operator learning for time-stepping partial differential equations on the sphere. The shallow water equations serve as a testbed for learning stable dynamics using purely data-driven approaches.

Sources: [examples/depth/train.py:48-53](), [examples/segmentation/train.py:53-58](), [torch_harmonics/examples/pde_dataset.py:39-71]()

## Example Directory Structure

```mermaid
graph TB
    subgraph "examples/"
        DEPTH["depth/<br/>train.py<br/>Depth estimation"]
        SEG["segmentation/<br/>train.py<br/>Semantic segmentation"]
        
        subgraph "baseline_models/"
            SEGFORMER["segformer.py<br/>Segformer class"]
            TRANSFORMER["transformer.py<br/>Transformer class"]
            S2_MODELS["s2_*.py<br/>Spherical variants"]
        end
        
        REGISTRY["model_registry.py<br/>get_baseline_models()"]
        DATA_DIR["data/<br/>Downloaded datasets"]
    end
    
    subgraph "torch_harmonics/examples/"
        MODELS_DIR["models/<br/>sfno.py, lsno.py"]
        DATASETS["Datasets<br/>StanfordDepthDataset<br/>StanfordSegmentationDataset<br/>PdeDataset"]
        LOSSES["losses.py<br/>W11LossS2<br/>CrossEntropyLossS2<br/>DiceLossS2"]
        METRICS["metrics.py<br/>IntersectionOverUnionS2<br/>AccuracyS2"]
        DOWNLOADER["Stanford2D3DSDownloader"]
    end
    
    DEPTH --> REGISTRY
    SEG --> REGISTRY
    REGISTRY --> SEGFORMER
    REGISTRY --> TRANSFORMER
    REGISTRY --> MODELS_DIR
    
    DEPTH --> DATASETS
    SEG --> DATASETS
    DEPTH --> LOSSES
    SEG --> LOSSES
    DEPTH --> METRICS
    SEG --> METRICS
    
    DATASETS --> DOWNLOADER
    DOWNLOADER --> DATA_DIR
```

**Directory Organization**:

- `examples/depth/` and `examples/segmentation/`: Task-specific training scripts for vision applications
- `examples/baseline_models/`: Model architectures not specific to torch-harmonics (standard transformers, segformers)
- `examples/model_registry.py`: Central registry providing factory functions for all available models
- `torch_harmonics/examples/models/`: Core neural operator implementations (SFNO, LSNO)
- `torch_harmonics/examples/`: Datasets, loss functions, metrics, and data utilities

Sources: [examples/depth/train.py:56-59](), [examples/segmentation/train.py:61-63](), [examples/baseline_models/segformer.py:1-30](), [torch_harmonics/examples/models/sfno.py:1-40]()

## Model Architectures by Application

### Depth Estimation Models

```mermaid
graph LR
    subgraph "Attention-based Models"
        S2TRANS["S2 Transformer<br/>AttentionS2<br/>Spherical positional encoding"]
        S2SEG["S2 Segformer<br/>NeighborhoodAttentionS2<br/>Multi-scale fusion"]
    end
    
    subgraph "Neural Operators"
        SFNO_DEPTH["SFNO<br/>SpectralConvS2<br/>Global spectral"]
        LSNO_DEPTH["LSNO<br/>DiscreteContinuousConvS2<br/>+ SpectralConvS2<br/>Mixed local+global"]
    end
    
    subgraph "Baseline Comparisons"
        TRANS["Standard Transformer<br/>No sphere awareness"]
        NSEG["Standard Segformer<br/>Neighborhood attention"]
    end
    
    INPUT["RGB Image<br/>B × 3 × nlat × nlon"]
    OUTPUT["Depth Map<br/>B × 1 × nlat × nlon"]
    
    INPUT --> S2TRANS --> OUTPUT
    INPUT --> S2SEG --> OUTPUT
    INPUT --> SFNO_DEPTH --> OUTPUT
    INPUT --> LSNO_DEPTH --> OUTPUT
    INPUT --> TRANS --> OUTPUT
    INPUT --> NSEG --> OUTPUT
```

All depth estimation models are configured through the `get_baseline_models()` function with variants differentiated by embedding dimensions (e.g., `e32`, `e128`, `e256`) and number of layers. Models prefixed with `s2` incorporate spherical geometry awareness through specialized components.

**Key Depth Models**:
- `s2transformer_sc2_layers4_e128`: Uses `AttentionS2` for global spherical attention
- `s2segformer_sc2_layers4_e128`: Uses `NeighborhoodAttentionS2` with geodesic distance-based neighborhoods
- `sfno_sc2_layers4_e32`: Pure spectral convolution approach via spherical harmonic transforms
- `lsno_sc2_layers4_e32`: Combines local DISCO convolutions with global spectral operations

Sources: [examples/depth/train.py:434-454](), [torch_harmonics/examples/models/sfno.py:175-240](), [torch_harmonics/examples/models/lsno.py:378-457]()

### Semantic Segmentation Models

The segmentation task uses the same model architectures as depth estimation but configured for multi-class output (13 semantic classes). The primary difference is in the loss functions and metrics used for training and evaluation.

```mermaid
graph TB
    subgraph "Model Output Processing"
        LOGITS["Model Output<br/>B × 13 × nlat × nlon<br/>Logits per class"]
        SOFTMAX["Softmax<br/>Convert to probabilities"]
        ARGMAX["Argmax<br/>Select highest probability"]
        PRED["Predicted Class Map<br/>B × nlat × nlon<br/>Integer class labels"]
    end
    
    LOGITS --> SOFTMAX --> ARGMAX --> PRED
    
    subgraph "Loss Computation"
        LOGITS2["Raw Logits"] --> CE["CrossEntropyLossS2<br/>Weighted by quadrature"]
        LOGITS2 --> DICE["DiceLossS2<br/>Overlap-based loss"]
        LOGITS2 --> FOCAL["FocalLossS2<br/>Hard example mining"]
    end
    
    subgraph "Metrics"
        PRED2["Predictions"] --> IOU["IntersectionOverUnionS2<br/>Per-class IoU averaged"]
        PRED2 --> ACC["AccuracyS2<br/>Weighted by spherical area"]
    end
```

Sources: [examples/segmentation/train.py:446-508](), [examples/segmentation/train.py:135-138]()

### PDE Solving Models

For operator learning on PDEs, the SFNO and LSNO architectures are specifically designed for this task:

```mermaid
graph LR
    subgraph "SFNO Pipeline"
        INPUT_SFNO["Initial Condition<br/>u₀, v₀, h₀<br/>3 × nlat × nlon"]
        ENC_SFNO["Encoder<br/>Conv2d layers<br/>3 → embed_dim"]
        BLOCKS_SFNO["Spectral Blocks<br/>RealSHT → Filter → InverseRealSHT<br/>Hard thresholding"]
        DEC_SFNO["Decoder<br/>Conv2d layers<br/>embed_dim → 3"]
        OUT_SFNO["Future State<br/>u₁, v₁, h₁"]
    end
    
    INPUT_SFNO --> ENC_SFNO --> BLOCKS_SFNO --> DEC_SFNO --> OUT_SFNO
    
    subgraph "LSNO Pipeline"
        INPUT_LSNO["Initial Condition<br/>3 × nlat × nlon"]
        ENC_LSNO["DiscreteContinuousEncoder<br/>Downsample with DISCO"]
        MIXED["Mixed Blocks<br/>Local: DiscreteContinuousConvS2<br/>Global: SpectralConvS2<br/>Alternating pattern"]
        DEC_LSNO["DiscreteContinuousDecoder<br/>Upsample with DISCO"]
        OUT_LSNO["Future State"]
    end
    
    INPUT_LSNO --> ENC_LSNO --> MIXED --> DEC_LSNO --> OUT_LSNO
```

The SFNO uses exclusively spectral operations with hard thresholding to retain only the most energetic modes, ensuring numerical stability for long-term rollouts. The LSNO adds local discrete-continuous convolutions to capture fine-scale features that may not be well-represented in spectral space.

Sources: [torch_harmonics/examples/models/sfno.py:313-346](), [torch_harmonics/examples/models/lsno.py:534-592]()

## Common Training Infrastructure

### Training Loop Architecture

```mermaid
graph TB
    subgraph "Main Training Function"
        INIT["Initialize<br/>- Model<br/>- Optimizer (AdamW)<br/>- Scheduler<br/>- GradScaler (AMP)"]
        EPOCH_LOOP["Epoch Loop<br/>for epoch in range(nepochs)"]
        TRAIN_PHASE["Training Phase<br/>- Load batch<br/>- Normalize input<br/>- Apply augmentation<br/>- Forward pass (AMP)<br/>- Compute loss<br/>- Backward pass<br/>- Optimizer step"]
        VAL_PHASE["Validation Phase<br/>- Disable gradients<br/>- Forward pass<br/>- Compute metrics<br/>- Log to wandb"]
        SAVE["Save Checkpoint<br/>torch.save(model.state_dict())"]
    end
    
    INIT --> EPOCH_LOOP
    EPOCH_LOOP --> TRAIN_PHASE
    TRAIN_PHASE --> VAL_PHASE
    VAL_PHASE --> EPOCH_LOOP
    EPOCH_LOOP --> SAVE
    
    subgraph "Distributed Training Support"
        DDP_INIT["dist.init_process_group()<br/>backend='nccl'"]
        DDP_WRAP["DDP(model, device_ids)"]
        SAMPLER["DistributedSampler<br/>Shard data across GPUs"]
        REDUCE["dist.all_reduce()<br/>Aggregate losses/metrics"]
    end
    
    DDP_INIT --> DDP_WRAP
    DDP_WRAP --> TRAIN_PHASE
    SAMPLER --> TRAIN_PHASE
    VAL_PHASE --> REDUCE
```

All example applications share a common training infrastructure pattern:

1. **Initialization**: Model creation, optimizer setup (AdamW with weight decay), learning rate scheduler (ReduceLROnPlateau for depth, CosineAnnealingLR for segmentation), and gradient scaler for automatic mixed precision
2. **Training Loop**: Forward pass with optional AMP, loss computation, backward pass, gradient clipping (optional), optimizer step
3. **Validation**: Periodic evaluation on held-out data with metrics computation
4. **Logging**: Integration with Weights & Biases for experiment tracking
5. **Checkpointing**: Save/load model state for resuming training

Sources: [examples/depth/train.py:168-328](), [examples/segmentation/train.py:158-319]()

### Data Pipeline

```mermaid
graph TB
    subgraph "Stanford 2D3DS Pipeline"
        URL["Base URL<br/>https://cvg-data.inf.ethz.ch/2d3ds/"]
        DOWNLOADER["Stanford2D3DSDownloader<br/>Download and extract"]
        HDF5["HDF5 File<br/>stanford_2d3ds_dataset_ds16.h5<br/>Preprocessed panoramas"]
        
        DEPTH_DS["StanfordDepthDataset<br/>Returns: (rgb, depth)"]
        SEG_DS["StanfordSegmentationDataset<br/>Returns: (rgb, semantic_mask)"]
        
        SPLIT["Random Split<br/>95% train, 2.5% test, 2.5% valid"]
        SAMPLER["DataLoader<br/>+ DistributedSampler (if DDP)"]
    end
    
    URL --> DOWNLOADER
    DOWNLOADER --> HDF5
    HDF5 --> DEPTH_DS
    HDF5 --> SEG_DS
    DEPTH_DS --> SPLIT
    SEG_DS --> SPLIT
    SPLIT --> SAMPLER
    
    subgraph "PDE Pipeline"
        SOLVER["ShallowWaterSolver<br/>Spectral solver"]
        IC["Initial Condition<br/>Random or Galewsky"]
        TIMESTEP["Timestep nsteps<br/>Generate target"]
        PDE_DS["PdeDataset<br/>__getitem__: solve on-the-fly"]
    end
    
    SOLVER --> IC
    IC --> TIMESTEP
    TIMESTEP --> PDE_DS
    
    subgraph "Preprocessing"
        STATS["compute_stats_s2()<br/>Channel-wise mean/std<br/>Weighted by spherical area"]
        NORM["v2.Normalize<br/>mean, std normalization"]
        AUG["Data Augmentation<br/>ColorJitter, GaussianNoise<br/>Horizontal flip"]
    end
    
    SAMPLER --> STATS
    STATS --> NORM
    NORM --> AUG
```

**Stanford 2D3DS Dataset**:
- Automatic download and preprocessing via `Stanford2D3DSDownloader`
- Configurable downsampling factor (default: 16x to reduce resolution)
- Stored in HDF5 format for efficient random access
- Supports both depth and segmentation annotations

**PDE Dataset**:
- Generated on-the-fly using `ShallowWaterSolver`
- Each sample: run spectral solver for `nsteps` to create input/target pair
- Supports multiple initial conditions (random, Galewsky jet)
- Optional normalization based on first sample statistics

Sources: [examples/depth/train.py:371-389](), [examples/segmentation/train.py:363-384](), [torch_harmonics/examples/pde_dataset.py:39-160]()

## Loss Functions and Metrics

### Spherical-Aware Loss Functions

All loss functions in torch-harmonics incorporate quadrature weights to account for varying grid cell areas on the sphere:

```mermaid
graph TB
    subgraph "Depth Estimation Losses"
        W11["W11LossS2<br/>Sobolev H¹ norm<br/>Penalizes L2 + gradient"]
        L1_DEPTH["L1LossS2<br/>Absolute error<br/>Robust to outliers"]
        L2_DEPTH["L2LossS2<br/>Mean squared error"]
        NORMAL["NormalLossS2<br/>Surface normal error<br/>Geometric consistency"]
        
        COMBINED["Combined Loss<br/>0.1 × W11 + L1"]
    end
    
    W11 --> COMBINED
    L1_DEPTH --> COMBINED
    
    subgraph "Segmentation Losses"
        CE["CrossEntropyLossS2<br/>Per-pixel classification<br/>Optional label smoothing"]
        DICE["DiceLossS2<br/>Overlap-based<br/>Class imbalance handling"]
        FOCAL["FocalLossS2<br/>Focus on hard examples<br/>γ parameter"]
    end
    
    subgraph "Core Computation"
        QUAD["Quadrature Weights<br/>clenshaw_curtiss_weights()<br/>Spherical integration"]
        WEIGHT["Element-wise multiply<br/>loss × quadrature_weights"]
        SUM["Sum and normalize<br/>Σ(weighted_loss) / Σ(weights)"]
    end
    
    W11 --> QUAD
    CE --> QUAD
    QUAD --> WEIGHT
    WEIGHT --> SUM
```

**Key Loss Functions**:

| Loss Class | Equation | Use Case |
|------------|----------|----------|
| `W11LossS2` | `∫_S² (‖u - v‖² + ‖∇u - ∇v‖²) dA` | Depth regression with smoothness |
| `L1LossS2` | `∫_S² ‖u - v‖ dA` | Robust depth regression |
| `CrossEntropyLossS2` | `∫_S² -Σ_c y_c log(p_c) dA` | Multi-class segmentation |
| `DiceLossS2` | `1 - (2∫_S² p·y dA)/(∫_S² p dA + ∫_S² y dA)` | Segmentation with class imbalance |
| `NormalLossS2` | `∫_S² ‖n_pred - n_gt‖ dA` | Geometric consistency for depth |

All losses integrate over the sphere using quadrature weights that account for the varying area of grid cells (smaller near poles, larger near equator).

Sources: [examples/depth/train.py:459-471](), [examples/segmentation/train.py:488-507]()

### Metrics

Evaluation metrics also incorporate spherical geometry:

```mermaid
graph LR
    subgraph "Segmentation Metrics"
        IOU["IntersectionOverUnionS2<br/>Per-class IoU<br/>Weighted average"]
        ACC["AccuracyS2<br/>Correct pixels<br/>Weighted by area"]
    end
    
    subgraph "Depth Metrics"
        L2_METRIC["L2 error<br/>RMS difference"]
        L1_METRIC["L1 error<br/>Mean absolute difference"]
        W11_METRIC["W11 error<br/>Sobolev norm"]
        NORMAL_METRIC["Normal error<br/>Surface normal difference"]
    end
    
    subgraph "Computation"
        PRED["Predictions"]
        TARGET["Ground Truth"]
        MASK["Valid Mask<br/>Exclude invalid regions"]
        QUAD_METRIC["Quadrature Weights"]
        
        PRED --> COMPUTE["Compute Metric"]
        TARGET --> COMPUTE
        MASK --> COMPUTE
        QUAD_METRIC --> COMPUTE
    end
```

**Metrics by Task**:
- **Depth**: L1, L2, W11 (Sobolev), Normal error
- **Segmentation**: Mean Intersection over Union (mIoU), Mean Accuracy
- **PDE**: L2 relative error, energy conservation

All metrics are weighted by spherical area to provide accurate global statistics.

Sources: [examples/depth/train.py:464-471](), [examples/segmentation/train.py:494-507]()

## Running the Examples

### Depth Estimation

```bash
# Basic training
python examples/depth/train.py \
    --models s2transformer_sc2_layers4_e128 \
    --num_epochs 100 \
    --batch_size 8 \
    --learning_rate 1e-3

# Multi-GPU distributed training
python -m torch.distributed.run --nproc_per_node=4 \
    examples/depth/train.py \
    --models sfno_sc2_layers4_e32 \
    --enable_ddp \
    --amp_mode bf16

# Multiple models comparison
python examples/depth/train.py \
    --models s2transformer_sc2_layers4_e128 \
           sfno_sc2_layers4_e32 \
           lsno_sc2_layers4_e32 \
    --num_epochs 100
```

**Command-line Arguments**:
- `--models`: Space-separated list of model names from registry
- `--num_epochs`: Training epochs (0 for evaluation only)
- `--batch_size`: Batch size per GPU
- `--learning_rate`: Initial learning rate
- `--data_downsampling_factor`: Spatial downsampling (default: 16)
- `--amp_mode`: Mixed precision mode (`none`, `fp16`, `bf16`)
- `--enable_ddp`: Enable distributed data parallel
- `--resume`: Load checkpoint and resume training
- `--output_path`: Directory for checkpoints and outputs
- `--data_path`: Dataset location

Sources: [examples/depth/train.py:592-636]()

### Semantic Segmentation

```bash
# Training with data augmentation
python examples/segmentation/train.py \
    --models s2segformer_sc2_layers4_e128 \
    --num_epochs 200 \
    --learning_rate 5e-4 \
    --enable_data_augmentation

# With gradient clipping and label smoothing
python examples/segmentation/train.py \
    --models s2segformer_sc2_layers4_e128 \
    --max_grad_norm 4.0 \
    --label_smoothing_factor 0.1
```

**Additional Segmentation Arguments**:
- `--max_grad_norm`: Gradient clipping threshold (default: 4.0)
- `--label_smoothing_factor`: Label smoothing [0, 1] (default: 0.0)
- `--enable_data_augmentation`: Apply color jitter, noise, autocontrast

Sources: [examples/segmentation/train.py:621-669]()

### Training Output Structure

```
output_path/
├── model_name/
│   ├── checkpoint.pt              # Model state dict
│   ├── figures/
│   │   ├── input_0.png           # Input visualization
│   │   ├── pred_0.png            # Prediction visualization
│   │   └── truth_0.png           # Ground truth visualization
│   └── output_data/
│       └── metrics.pkl            # Performance metrics DataFrame
└── ...
```

Each model creates a subdirectory containing:
- **checkpoint.pt**: Saved model parameters for resumption
- **figures/**: Visualizations of validation set predictions
- **output_data/metrics.pkl**: Pandas DataFrame with statistics (mean/std of losses and metrics)

Sources: [examples/depth/train.py:492-586](), [examples/segmentation/train.py:528-616]()

## Integration with Weights & Biases

All examples support experiment tracking via Weights & Biases:

```python
# Automatic initialization when training
wandb.init(
    project="depth estimation 2d3ds",  # or "spherical segmentation 2d3ds"
    group=model_name,
    name=f"{model_name}_{timestamp}",
    config=model_config
)

# Logged metrics per epoch
wandb.log({
    "loss": train_loss,
    "validation loss": val_loss,
    "learning rate": current_lr,
    "L2 error": l2_metric,
    "mean IoU": miou_metric,
    # ... task-specific metrics
})
```

This enables:
- Hyperparameter tracking
- Real-time training curves
- Cross-model comparison
- Reproducibility via saved configs

Sources: [examples/depth/train.py:502-541](), [examples/segmentation/train.py:538-578]()

## Model Registry System

The `get_baseline_models()` function provides a centralized registry of all available models with pre-configured hyperparameters:

```mermaid
graph TB
    subgraph "Model Registry Pattern"
        REGISTRY["get_baseline_models(img_size, in_chans, out_chans)<br/>Returns: Dict[str, partial]"]
        
        SFNO_FACTORY["'sfno_sc2_layers4_e32'<br/>partial(SphericalFourierNeuralOperator,<br/>img_size=img_size, embed_dim=32, ...)"]
        
        LSNO_FACTORY["'lsno_sc2_layers4_e32'<br/>partial(LocalSphericalNeuralOperator,<br/>img_size=img_size, embed_dim=32, ...)"]
        
        S2SEG_FACTORY["'s2segformer_sc2_layers4_e128'<br/>partial(S2Segformer,<br/>img_size=img_size, embed_dims=[32,64,128,256], ...)"]
        
        INSTANTIATE["model_factory()<br/>→ nn.Module instance"]
    end
    
    REGISTRY --> SFNO_FACTORY
    REGISTRY --> LSNO_FACTORY
    REGISTRY --> S2SEG_FACTORY
    
    SFNO_FACTORY --> INSTANTIATE
    LSNO_FACTORY --> INSTANTIATE
    S2SEG_FACTORY --> INSTANTIATE
    
    subgraph "Configuration Storage"
        PARTIAL["functools.partial<br/>Stores keyword arguments"]
        KEYWORDS["partial.keywords<br/>Access configuration"]
    end
    
    SFNO_FACTORY -.-> PARTIAL
    PARTIAL -.-> KEYWORDS
```

This pattern allows:
1. **Easy model selection**: Select models by string name
2. **Hyperparameter storage**: Configuration accessible via `factory.keywords`
3. **Lazy instantiation**: Models created only when needed
4. **Type safety**: All returned objects are callable factories

Example usage:
```python
models = get_baseline_models(img_size=(128, 256), in_chans=3, out_chans=13)
model = models["s2segformer_sc2_layers4_e128"]()  # Instantiate
config = models["s2segformer_sc2_layers4_e128"].keywords  # Access config
```

Sources: [examples/depth/train.py:433-454](), [examples/segmentation/train.py:446-482]()

---

