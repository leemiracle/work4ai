<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Audio2Face-3D-Training-Framework · page 3 Configuration System · fetched 2026-10-26 -->

# Configuration System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [audio2face/config_base/config_train_diffusion_base.py](audio2face/config_base/config_train_diffusion_base.py)
- [audio2face/config_base/config_train_regression_base.py](audio2face/config_base/config_train_regression_base.py)
- [audio2face/dataset.py](audio2face/dataset.py)
- [audio2face/networks/diffusion_rnn.py](audio2face/networks/diffusion_rnn.py)
- [configs/example-diffusion-min/config_train.py](configs/example-diffusion-min/config_train.py)
- [configs/example-diffusion/config_train.py](configs/example-diffusion/config_train.py)
- [configs/example-regression-min/config_train.py](configs/example-regression-min/config_train.py)
- [docs/config_details.md](docs/config_details.md)

</details>



The Configuration System is the core orchestration mechanism for the Audio2Face-3D Training Framework, implementing a two-tier architecture that separates base defaults from user customizations. This system manages all parameters across the entire pipeline, from dataset preparation through model deployment, providing a unified interface for controlling training workflows, model architectures, and inference settings.

For information about specific training configuration parameters, see [Training Configuration](#3.3). For dataset-specific configuration details, see [Dataset Configuration](#3.2).

## Two-Tier Configuration Architecture

The framework implements a hierarchical configuration system with two distinct layers that merge at runtime to produce the final configuration used by the training pipeline.

### Configuration Merger System

```mermaid
graph TB
    subgraph "Base Configuration Layer"
        CDB["config_dataset_base.py"]
        CPB["config_preproc_base.py"]
        CTRB["config_train_regression_base.py"]
        CTDB["config_train_diffusion_base.py"]
        CIRB["config_inference_regression_base.py"]
        CIDB["config_inference_diffusion_base.py"]
    end
    
    subgraph "User Configuration Layer"
        CD["config_dataset.py"]
        CP["config_preproc.py"]
        CT["config_train.py"]
        CI["config_inference.py"]
    end
    
    subgraph "Runtime System"
        CM["Configuration Merger"]
        FC["Final Configuration Object"]
        TP["Training Pipeline"]
    end
    
    CDB -.->|"default values"| CM
    CPB -.->|"default values"| CM
    CTRB -.->|"default values"| CM
    CTDB -.->|"default values"| CM
    
    CD -->|"overrides"| CM
    CP -->|"overrides"| CM
    CT -->|"overrides"| CM
    CI -->|"overrides"| CM
    
    CM --> FC
    FC --> TP
    
    FC --> AudioProvider["AudioProvider"]
    FC --> PhonemeProvider["PhonemeProvider"] 
    FC --> TargetProviderFullFace["TargetProviderFullFace"]
```

**Sources:** [audio2face/config_base/config_train_regression_base.py:1-215](), [audio2face/config_base/config_train_diffusion_base.py:1-224](), [audio2face/dataset.py:38-44]()

The base configuration layer provides comprehensive defaults for all framework components, while the user layer allows selective overrides for specific deployment scenarios. This architecture ensures that users only need to specify parameters that differ from sensible defaults.

### Configuration Type Selection

```mermaid
graph TD
    subgraph "Configuration Selection Logic"
        NT["NETWORK_TYPE Parameter"]
        NT -->|"regression"| RegBase["config_train_regression_base.py"]
        NT -->|"diffusion"| DiffBase["config_train_diffusion_base.py"]
        
        RegBase --> RegParams["Regression Parameters"]
        DiffBase --> DiffParams["Diffusion Parameters"]
        
        RegParams --> SEQ_LEN["SEQ_LEN = 2"]
        RegParams --> BATCH_SIZE_R["BATCH_SIZE = 32"]
        RegParams --> TARGET_CHANNELS_R["TARGET_CHANNELS = [skin_coeffs, tongue_coeffs, jaw, eye]"]
        
        DiffParams --> TRAIN_ON_RANDOM["TRAIN_ON_RANDOM_SUBSEGMENT = True"]
        DiffParams --> BATCH_SIZE_D["BATCH_SIZE = 1"]
        DiffParams --> TARGET_CHANNELS_D["TARGET_CHANNELS = [skin_pose, tongue_pose, jaw, eye]"]
        DiffParams --> DIFFUSION_STEPS["DIFFUSION_STEPS = 1000"]
    end
```

**Sources:** [audio2face/config_base/config_train_regression_base.py:25](), [audio2face/config_base/config_train_diffusion_base.py:25](), [audio2face/config_base/config_train_regression_base.py:153](), [audio2face/config_base/config_train_diffusion_base.py:173]()

## Configuration File Structure

The configuration system organizes parameters into four primary categories, each handled by dedicated configuration files with specific responsibilities.

### Core Configuration Components

| Configuration Type | Base File | Purpose | Key Parameters |
|-------------------|-----------|---------|----------------|
| Dataset | `config_dataset_base.py` | Data paths and actor properties | `AUDIO_ROOT`, `SKIN_CACHE_ROOT`, `ACTOR_NAMES` |
| Preprocessing | `config_preproc_base.py` | PCA and data preparation | `SKIN_PCA_VARIANCE_THRESHOLD`, `RUN_NAME` |
| Training | `config_train_*_base.py` | Model training parameters | `NETWORK_TYPE`, `BATCH_SIZE`, `LOSS_*_ALPHA` |
| Inference | `config_inference_*_base.py` | Post-processing and deployment | `TEMPORAL_SMOOTHING`, `LIP_SYNC_OFFSET` |

**Sources:** [docs/config_details.md:14-926]()

### Dataset Configuration Structure

```mermaid
graph LR
    subgraph "Dataset Configuration Parameters"
        AUDIO_ROOT["AUDIO_ROOT<br/>{actor_name: path}"]
        SKIN_CACHE_ROOT["SKIN_CACHE_ROOT<br/>{actor_name: path}"]
        SKIN_NEUTRAL_FPATH["SKIN_NEUTRAL_FPATH<br/>{actor_name: path}"]
        
        TONGUE_CACHE_ROOT["TONGUE_CACHE_ROOT<br/>{actor_name: path}"]
        JAW_ANIM_DATA_FPATH["JAW_ANIM_DATA_FPATH<br/>{actor_name: path}"]
        EYE_ANIM_DATA_FPATH["EYE_ANIM_DATA_FPATH<br/>{actor_name: path}"]
        
        ACTOR_NAMES["ACTOR_NAMES<br/>List[str]"]
        CACHE_FPS["CACHE_FPS<br/>{actor_name: float}"]
        SHOT_EMOTION_NAMES["SHOT_EMOTION_NAMES<br/>List[str]"]
    end
    
    subgraph "Data Validation Files"
        SKIN_LIP_DIST_VERTEX_LIST["SKIN_LIP_DIST_VERTEX_LIST_FPATH"]
        SKIN_EYE_DIST_VERTEX_LIST["SKIN_EYE_DIST_VERTEX_LIST_FPATH"]
    end
    
    AUDIO_ROOT --> AudioProvider
    SKIN_CACHE_ROOT --> TargetProviderFullFace
    ACTOR_NAMES --> AudioProvider
    ACTOR_NAMES --> TargetProviderFullFace
```

**Sources:** [docs/config_details.md:27-202](), [audio2face/dataset.py:38-61](), [audio2face/dataset.py:381-409]()

## Configuration Merging and Resolution

The framework employs a runtime configuration resolution system that combines base and user configurations through parameter-level overrides.

### Parameter Resolution Process

```mermaid
sequenceDiagram
    participant UC as "User Config"
    participant BC as "Base Config"
    participant CM as "Configuration Merger"
    participant EasyDict as "utils.EasyDict"
    participant Pipeline as "Training Pipeline"
    
    UC->>CM: Load user parameters
    BC->>CM: Load base parameters
    CM->>CM: Override base with user values
    CM->>EasyDict: Create unified config object
    EasyDict->>Pipeline: Pass to AudioProvider.__init__()
    EasyDict->>Pipeline: Pass to TargetProviderFullFace.__init__()
    EasyDict->>Pipeline: Pass to PhonemeProvider.__init__()
```

**Sources:** [audio2face/dataset.py:39-41](), [audio2face/dataset.py:165-167](), [audio2face/dataset.py:117-120]()

The merging process ensures that user-specified parameters take precedence over base defaults, while maintaining type safety and parameter validation. The `utils.EasyDict` class provides the runtime configuration object used throughout the training pipeline.

### Actor-Specific Parameter Structure

Many configuration parameters use dictionary structures keyed by actor names to support multi-actor training scenarios:

```python
# Example from config files
PREPROC_RUN_NAME_FULL = {
    "claire": "XXXXXX_XXXXXX_example"
}

AUDIO_ROOT = {
    "actor_name": "path/to/audio/directory"
}
```

**Sources:** [configs/example-regression-min/config_train.py:38-40](), [docs/config_details.md:27-31]()

## Training Configuration Integration

The configuration system directly integrates with the training pipeline through provider classes that consume configuration parameters during initialization.

### Configuration Consumer Classes

```mermaid
graph TB
    subgraph "Configuration Consumers"
        AP["AudioProvider"]
        PP["PhonemeProvider"]
        TPF["TargetProviderFullFace"]
    end
    
    subgraph "Configuration Parameters"
        AUDIO_PARAMS["AUDIO_PARAMS"]
        AUDIO_DATA_CACHING["AUDIO_DATA_CACHING"]
        PHONEME_FORCING_LANGS["PHONEME_FORCING_LANGS"]
        TARGET_CHANNELS["TARGET_CHANNELS"]
        TARGET_DATA_CACHING["TARGET_DATA_CACHING"]
        PREPROC_RUN_NAME_FULL["PREPROC_RUN_NAME_FULL"]
    end
    
    AUDIO_PARAMS --> AP
    AUDIO_DATA_CACHING --> AP
    PHONEME_FORCING_LANGS --> PP
    TARGET_CHANNELS --> TPF
    TARGET_DATA_CACHING --> TPF
    PREPROC_RUN_NAME_FULL --> TPF
    
    AP --> cfg_train["cfg_train: utils.EasyDict"]
    PP --> cfg_train
    TPF --> cfg_train
    
    cfg_train --> cfg_dataset["cfg_dataset: utils.EasyDict"]
```

**Sources:** [audio2face/dataset.py:39-44](), [audio2face/dataset.py:118-124](), [audio2face/dataset.py:165-169]()

### Network Architecture Configuration

The configuration system supports different network architectures through the `NETWORK_TYPE` parameter and associated hyperparameters:

```mermaid
graph TD
    subgraph "Network Configuration"
        NETWORK_TYPE["NETWORK_TYPE"]
        NETWORK_NAME["NETWORK_NAME"]
        NETWORK_HYPER_PARAMS["NETWORK_HYPER_PARAMS"]
        
        NETWORK_TYPE -->|"regression"| conv_w2v_autocorr["conv_w2v_autocorr"]
        NETWORK_TYPE -->|"diffusion"| diffusion_rnn["diffusion_rnn"]
        
        conv_w2v_autocorr --> RegHyperParams["use_w2v_features: True<br/>implicit_emotion_len: 16<br/>explicit_emo_emb_len: 8"]
        diffusion_rnn --> DiffHyperParams["feature_dim: 256<br/>gru_feature_dim: 256<br/>num_gru_layers: 2"]
    end
```

**Sources:** [audio2face/config_base/config_train_regression_base.py:128-145](), [audio2face/config_base/config_train_diffusion_base.py:132-143](), [audio2face/networks/diffusion_rnn.py:201-227]()

The `NETWORK_HYPER_PARAMS` dictionary contains architecture-specific parameters that are passed directly to network constructors, enabling flexible model configuration without code changes.

## Example Configuration Hierarchy

The framework provides several example configurations demonstrating different use cases and complexity levels.

### Example Configuration Structure

```mermaid
graph TB
    subgraph "Example Configurations"
        ExampleRegMin["example-regression-min/"]
        ExampleDiffMin["example-diffusion-min/"]
        ExampleDiff["example-diffusion/"]
        
        ExampleRegMin --> ConfigTrainRegMin["config_train.py<br/>RUN_NAME = example-regression-min<br/>NUM_EPOCHS = 50<br/>LOSS_LIP_DIST_ALPHA = 1e2"]
        
        ExampleDiffMin --> ConfigTrainDiffMin["config_train.py<br/>RUN_NAME = example-diffusion-min<br/>NUM_EPOCHS = 400<br/>LOSS_LIP_DIST_ALPHA = 1e-5"]
        
        ExampleDiff --> ConfigTrainDiff["config_train.py<br/>RUN_NAME = example-diffusion<br/>NUM_EPOCHS = 400<br/>LOSS_LIP_DIST_ALPHA = 1e-5"]
    end
    
    subgraph "Common Elements"
        CLIPS["CLIPS = [(actor, shot, range, speaker, lang, audio, offset)]"]
        AUG_MUTED_SHOTS["AUG_MUTED_SHOTS = [(actor, source, length, emotion)]"]
        PREPROC_RUN_NAME["PREPROC_RUN_NAME_FULL = {claire: XXXXXX_XXXXXX_example}"]
    end
    
    ConfigTrainRegMin --> CLIPS
    ConfigTrainDiffMin --> CLIPS
    ConfigTrainDiff --> CLIPS
    
    ConfigTrainRegMin --> AUG_MUTED_SHOTS
    ConfigTrainDiffMin --> AUG_MUTED_SHOTS
    ConfigTrainDiff --> AUG_MUTED_SHOTS
```

**Sources:** [configs/example-regression-min/config_train.py:17](), [configs/example-diffusion-min/config_train.py:17](), [configs/example-diffusion/config_train.py:17](), [configs/example-regression-min/config_train.py:52-107](), [configs/example-regression-min/config_train.py:120-132]()

All example configurations share common structural elements like the `CLIPS` list for defining training data segments and `AUG_MUTED_SHOTS` for data augmentation, while differing in model-specific parameters like loss function weights and training epochs.

---

