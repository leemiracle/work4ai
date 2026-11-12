<!-- source: DeepWiki mcp.deepwiki.com · repo yoshitomo-matsubara/torchdistill · page 5 Performance and Benchmarks · fetched 2026-10-21 -->

# Performance and Benchmarks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [configs/official/README.md](configs/official/README.md)
- [configs/official/ilsvrc2012/roymiles/aaai2024/README.md](configs/official/ilsvrc2012/roymiles/aaai2024/README.md)
- [configs/official/ilsvrc2012/roymiles/aaai2024/srd-resnet18_from_resnet34.log](configs/official/ilsvrc2012/roymiles/aaai2024/srd-resnet18_from_resnet34.log)
- [configs/official/ilsvrc2012/roymiles/aaai2024/srd-resnet18_from_resnet34.yaml](configs/official/ilsvrc2012/roymiles/aaai2024/srd-resnet18_from_resnet34.yaml)
- [configs/official/ilsvrc2012/yoshitomo-matsubara/nlp-oss2023/kr-resnet18_from_resnet34.yaml](configs/official/ilsvrc2012/yoshitomo-matsubara/nlp-oss2023/kr-resnet18_from_resnet34.yaml)
- [docs/source/_static/benchmarks/imagenet-resnet18_kd.tsv](docs/source/_static/benchmarks/imagenet-resnet18_kd.tsv)
- [docs/source/benchmarks.rst](docs/source/benchmarks.rst)

</details>



This page documents torchdistill's performance benchmarking system, reproducible experimental results, and official configuration repository. It covers benchmark result formats, reproducibility infrastructure, and the relationship between published research and torchdistill implementations.

For information about configuring individual experiments, see [Configuration Examples](#4.3). For research-specific configurations, see [Research Configurations](#4.4).

## Benchmark Results Infrastructure

The torchdistill framework maintains a comprehensive benchmarking system that compares knowledge distillation methods against their original implementations and provides reproducible configurations.

### Result Storage Format

Benchmark results are stored in tab-separated value (TSV) format within the documentation system:

```mermaid
graph TB
    subgraph "Benchmark Data Pipeline"
        TSV["TSV Files<br/>docs/source/_static/benchmarks/"]
        RST["RST Documentation<br/>docs/source/benchmarks.rst"]
        TABLE["Rendered Tables<br/>HTML Documentation"]
    end
    
    subgraph "Result Categories"
        IMAGENET["ImageNet Results<br/>imagenet-resnet18_kd.tsv"]
        GLUE["GLUE Results<br/>(Future datasets)"]
        CUSTOM["Custom Benchmarks<br/>(Domain-specific)"]
    end
    
    subgraph "Configuration Links"
        OFFICIAL["Official Configs<br/>configs/official/"]
        SAMPLE["Sample Configs<br/>configs/sample/"]
        CHECKPOINTS["Model Checkpoints<br/>Release artifacts"]
    end
    
    TSV --> RST
    RST --> TABLE
    
    IMAGENET --> TSV
    GLUE --> TSV
    CUSTOM --> TSV
    
    TABLE --> OFFICIAL
    TABLE --> SAMPLE
    OFFICIAL --> CHECKPOINTS
```

**TSV Result Format**
The benchmark files follow a standardized format with columns for method name, original work results, torchdistill reproduced results, and configuration links:

| Column | Description | Example |
|--------|-------------|---------|
| Method | Knowledge distillation method name | `KD`, `AT`, `FT`, `CRD` |
| Original work | Results from original paper | `70.70`, `71.43*` |
| torchdistill | Reproduced results using torchdistill | `70.90`, `71.56` |
| Config | Link to configuration files | `torchdistill/configs/official/...` |

Sources: [docs/source/_static/benchmarks/imagenet-resnet18_kd.tsv:1-16](), [docs/source/benchmarks.rst:22-27]()

### ImageNet ILSVRC 2012 Results

The primary benchmark dataset is ImageNet ILSVRC 2012, using ResNet-18 as the student model with ResNet-34 as the teacher:

```mermaid
graph LR
    subgraph "Teacher Model"
        T_MODEL["ResNet-34<br/>torchvision pretrained"]
        T_ACC["Teacher Accuracy<br/>~73.3% top-1"]
    end
    
    subgraph "Student Model"
        S_MODEL["ResNet-18<br/>num_classes: 1000"]
        S_BASE["Baseline Accuracy<br/>69.76% top-1"]
    end
    
    subgraph "Knowledge Distillation Methods"
        KD["Knowledge Distillation<br/>71.37%"]
        AT["Attention Transfer<br/>70.90%"]
        FT["Factor Transfer<br/>71.56%"]
        CRD["Contrastive Representation Distillation<br/>70.93%"]
        SSKD["Self-Supervised Knowledge Distillation<br/>70.09%"]
        PAD["Prime-Aware Distillation<br/>71.71%"]
        KR["Knowledge Review<br/>71.64%"]
        SRD["Simple Recipe Distillation<br/>71.92%"]
    end
    
    T_MODEL --> KD
    T_MODEL --> AT
    T_MODEL --> FT
    T_MODEL --> CRD
    T_MODEL --> SSKD
    T_MODEL --> PAD
    T_MODEL --> KR
    T_MODEL --> SRD
    
    S_MODEL --> KD
    S_MODEL --> AT
    S_MODEL --> FT
    S_MODEL --> CRD
    S_MODEL --> SSKD
    S_MODEL --> PAD
    S_MODEL --> KR
    S_MODEL --> SRD
```

**Performance Comparison**
The benchmark results demonstrate torchdistill's ability to reproduce and sometimes exceed original paper results:

- **Knowledge Distillation (KD)**: 71.37% (no original baseline for comparison)
- **Attention Transfer (AT)**: 70.90% vs 70.70% original
- **Factor Transfer (FT)**: 71.56% vs 71.43% original
- **Knowledge Review (KR)**: 71.64% vs 71.61% original
- **Simple Recipe Distillation (SRD)**: 71.92% vs 71.63% original

Sources: [docs/source/_static/benchmarks/imagenet-resnet18_kd.tsv:3-14](), [docs/source/benchmarks.rst:35-46]()

## Reproducibility Framework

The torchdistill reproducibility framework ensures that benchmark results can be independently verified and extended by providing complete experimental configurations and trained model checkpoints.

### Official Configuration Repository

```mermaid
graph TB
    subgraph "configs/official/"
        ROOT["configs/official/README.md<br/>Contribution guidelines"]
        
        subgraph "Dataset Organization"
            ILSVRC["ilsvrc2012/<br/>ImageNet experiments"]
            GLUE_DIR["glue/<br/>NLP benchmarks"]
        end
        
        subgraph "Author Organization"
            MATSUBARA["yoshitomo-matsubara/<br/>Framework author configs"]
            MILES["roymiles/<br/>AAAI 2024 paper"]
            CONTRIBUTORS["Other contributors<br/>Research reproductions"]
        end
        
        subgraph "Publication Organization"
            RRPR2020["rrpr2020/<br/>ICPR workshop paper"]
            NLP_OSS2023["nlp-oss2023/<br/>EMNLP workshop paper"]
            AAAI2024["aaai2024/<br/>AAAI conference paper"]
        end
    end
    
    subgraph "Configuration Components"
        YAML["YAML Config Files<br/>complete experiment definition"]
        LOG["Log Files<br/>training progress and metrics"]
        README["README Files<br/>citations and commands"]
        CKPT["Checkpoint Links<br/>trained model weights"]
    end
    
    ROOT --> ILSVRC
    ROOT --> GLUE_DIR
    
    ILSVRC --> MATSUBARA
    ILSVRC --> MILES
    
    MATSUBARA --> RRPR2020
    MATSUBARA --> NLP_OSS2023
    MILES --> AAAI2024
    
    RRPR2020 --> YAML
    NLP_OSS2023 --> YAML
    AAAI2024 --> YAML
    
    YAML --> LOG
    YAML --> README
    YAML --> CKPT
```

**Configuration Structure**
Each official configuration includes:

1. **Complete YAML Configuration**: Dataset, model, training, and evaluation settings
2. **Training Logs**: Full training output with metrics and timing information
3. **Documentation**: Citation information, reproduction commands, and results
4. **Model Checkpoints**: Pre-trained weights available for download

Sources: [configs/official/README.md:1-8](), [configs/official/ilsvrc2012/roymiles/aaai2024/README.md:1-53]()

### Experimental Configuration Format

The YAML configuration files provide complete experiment definitions that ensure reproducibility:

```mermaid
graph LR
    subgraph "Configuration Sections"
        DATASETS["datasets:<br/>Data loading and transforms"]
        MODELS["models:<br/>Teacher and student definitions"]
        TRAIN["train:<br/>Optimization and loss functions"]
        TEST["test:<br/>Evaluation settings"]
    end
    
    subgraph "Reproducibility Elements"
        SEEDS["Random seeds<br/>Deterministic results"]
        HYPERPARAMS["Hyperparameters<br/>Learning rates, batch sizes"]
        TRANSFORMS["Data transforms<br/>Augmentation settings"]
        SCHEDULES["Learning schedules<br/>Epoch milestones"]
    end
    
    subgraph "Model Specifications"
        TEACHER_WEIGHTS["Teacher weights<br/>torchvision.models.ResNet34_Weights"]
        STUDENT_ARCH["Student architecture<br/>resnet18, num_classes: 1000"]
        CHECKPOINT_PATHS["Checkpoint paths<br/>./resource/ckpt/ilsvrc2012/"]
    end
    
    DATASETS --> SEEDS
    MODELS --> HYPERPARAMS
    TRAIN --> TRANSFORMS
    TEST --> SCHEDULES
    
    HYPERPARAMS --> TEACHER_WEIGHTS
    TRANSFORMS --> STUDENT_ARCH
    SCHEDULES --> CHECKPOINT_PATHS
```

**Example: SRD Configuration Structure**
The Simple Recipe Distillation configuration demonstrates the comprehensive nature of torchdistill configurations:

- **Dataset Configuration**: ImageNet with specific transforms and normalization
- **Model Configuration**: ResNet-34 teacher with pre-trained weights, ResNet-18 student
- **Training Configuration**: SGD optimizer, MultiStepLR scheduler, 100 epochs
- **Loss Configuration**: Weighted combination of CrossEntropy and SRD-specific losses
- **Auxiliary Models**: SRDModelWrapper for feature normalization and projection

Sources: [configs/official/ilsvrc2012/roymiles/aaai2024/srd-resnet18_from_resnet34.yaml:1-201]()

## Performance Analysis and Validation

The benchmark system includes comprehensive validation mechanisms to ensure result reliability and enable performance analysis across different knowledge distillation methods.

### Training Progress Monitoring

```mermaid
graph TB
    subgraph "Logging System"
        LOG_FREQ["log_freq: 50<br/>Progress reporting interval"]
        METRICS["Metrics Collection<br/>Loss, accuracy, timing"]
        VALIDATION["Validation Runs<br/>Per-epoch evaluation"]
    end
    
    subgraph "Performance Metrics"
        TRAIN_LOSS["Training Loss<br/>Combined KD + task loss"]
        VAL_ACC["Validation Accuracy<br/>Top-1 and Top-5"]
        THROUGHPUT["Training Throughput<br/>Images per second"]
        MEMORY["Memory Usage<br/>Peak GPU memory"]
    end
    
    subgraph "Checkpointing"
        BEST_MODEL["Best Model Checkpoints<br/>Highest validation accuracy"]
        CHECKPOINT_PATH["Checkpoint Paths<br/>Organized by experiment"]
        RESUME["Resume Training<br/>From saved states"]
    end
    
    LOG_FREQ --> METRICS
    METRICS --> VALIDATION
    
    VALIDATION --> TRAIN_LOSS
    VALIDATION --> VAL_ACC
    VALIDATION --> THROUGHPUT
    VALIDATION --> MEMORY
    
    VAL_ACC --> BEST_MODEL
    BEST_MODEL --> CHECKPOINT_PATH
    CHECKPOINT_PATH --> RESUME
```

**Training Log Analysis**
The training logs provide detailed insights into the knowledge distillation process:

- **Epoch-by-epoch progress**: Loss convergence and accuracy improvement
- **Performance metrics**: Training throughput (960+ images/second), memory usage (9397 MB peak)
- **Validation tracking**: Regular evaluation with top-1 and top-5 accuracy
- **Best model selection**: Automatic checkpoint saving based on validation performance

The SRD training log shows progression from 30.7% accuracy at epoch 0 to 71.92% final accuracy, demonstrating effective knowledge transfer.

Sources: [configs/official/ilsvrc2012/roymiles/aaai2024/srd-resnet18_from_resnet34.log:1-500]()

### Method Comparison Framework

```mermaid
graph LR
    subgraph "Baseline Methods"
        PRETRAINED["Pretrained Teacher<br/>ResNet-34: torchvision"]
        STUDENT_ONLY["Student Only<br/>ResNet-18: 69.76%"]
    end
    
    subgraph "Feature-based Methods"
        AT_METHOD["Attention Transfer<br/>70.90% (+1.14%)"]
        FT_METHOD["Factor Transfer<br/>71.56% (+1.80%)"]
        CRD_METHOD["Contrastive Distillation<br/>70.93% (+1.17%)"]
    end
    
    subgraph "Response-based Methods"
        KD_METHOD["Knowledge Distillation<br/>71.37% (+1.61%)"]
        TFKD_METHOD["Label Smoothing KD<br/>70.52% (+0.76%)"]
    end
    
    subgraph "Advanced Methods"
        SSKD_METHOD["Self-Supervised KD<br/>70.09% (+0.33%)"]
        PAD_METHOD["Prime-Aware Distillation<br/>71.71% (+1.95%)"]
        KR_METHOD["Knowledge Review<br/>71.64% (+1.88%)"]
        SRD_METHOD["Simple Recipe Distillation<br/>71.92% (+2.16%)"]
    end
    
    STUDENT_ONLY --> AT_METHOD
    STUDENT_ONLY --> FT_METHOD
    STUDENT_ONLY --> CRD_METHOD
    STUDENT_ONLY --> KD_METHOD
    STUDENT_ONLY --> TFKD_METHOD
    STUDENT_ONLY --> SSKD_METHOD
    STUDENT_ONLY --> PAD_METHOD
    STUDENT_ONLY --> KR_METHOD
    STUDENT_ONLY --> SRD_METHOD
```

**Performance Analysis**
The benchmark results reveal several key insights:

1. **Consistent Improvements**: All methods show positive gains over the baseline student model
2. **Method Effectiveness**: Feature-based methods (AT, FT) and advanced methods (PAD, KR, SRD) achieve the highest improvements
3. **Reproducibility**: torchdistill results closely match or exceed original paper results
4. **Method Range**: Performance improvements range from 0.33% (SSKD) to 2.16% (SRD)

### Testing and Evaluation Commands

The framework provides standardized commands for testing and reproducing results:

```bash
# Test with pre-trained checkpoints
python3 examples/torchvision/image_classification.py \
    --config configs/official/ilsvrc2012/roymiles/aaai2024/srd-resnet18_from_resnet34.yaml \
    -test_only

# Train from scratch
python3 examples/torchvision/image_classification.py \
    --config configs/official/ilsvrc2012/roymiles/aaai2024/srd-resnet18_from_resnet34.yaml \
    --run_log log/ilsvrc2012/srd-resnet18_from_resnet34.log
```

**Checkpoint Management**
- Checkpoint files available via GitHub releases and Google Drive
- Organized by dataset, method, and experiment configuration
- Includes both intermediate and final model states
- Enables quick validation without full retraining

Sources: [configs/official/ilsvrc2012/roymiles/aaai2024/README.md:31-52](), [docs/source/benchmarks.rst:48-51]()

---

