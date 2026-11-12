<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/VLAb · page 10 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [LICENSE](LICENSE)
- [README.md](README.md)
- [src/lerobot/datasets/lerobot_dataset.py](src/lerobot/datasets/lerobot_dataset.py)
- [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py](src/lerobot/policies/smolvla2/smolvlm_with_expert2.py)

</details>



This page covers advanced usage patterns and implementation details for VLAb that go beyond basic training workflows. These topics are intended for users who need to customize dataset handling, optimize performance, or understand the internal mechanisms of the system.

**Related pages:**
- For temporal querying and history-aware policies, see [Temporal Context with Delta Timestamps](#10.1)
- For recording new datasets, see [Custom Dataset Creation](#10.2)
- For debugging common errors, see [Troubleshooting](#10.3)

---

## Feature Mapping and Heterogeneous Datasets

VLAb supports training on datasets with different feature schemas through a sophisticated feature mapping and padding system. This enables pretraining on diverse robotics datasets that may have different observation spaces, action dimensions, or camera configurations.

### Feature Key Mapping

The `feature_keys_mapping` system allows remapping dataset-specific feature names to standardized keys. This is configured per-dataset and applied during dataset initialization.

```mermaid
graph TB
    subgraph "Dataset A (Custom Keys)"
        A1["observation.images.camera_1"]
        A2["observation.images.camera_2"]
        A3["action (dim=5)"]
    end
    
    subgraph "Feature Mapping Layer"
        Map["feature_keys_mapping dict<br/>per repo_id"]
    end
    
    subgraph "Standardized Schema"
        B1["observation.images.image"]
        B2["observation.images.image2"]
        B3["action (padded to max_dim)"]
    end
    
    subgraph "Training Features"
        C1["Selected features for training"]
        C2["Excluded features"]
    end
    
    A1 --> Map
    A2 --> Map
    A3 --> Map
    
    Map --> B1
    Map --> B2
    Map --> B3
    
    B1 --> C1
    B2 --> C1
    B3 --> C1
```

**Sources:** [src/lerobot/datasets/lerobot_dataset.py:124-151](), [src/lerobot/datasets/lerobot_dataset.py:543-546]()

### Feature Padding and Alignment

When training on multiple datasets with different feature dimensions, VLAb pads features to a maximum dimension specified in the configuration. This ensures all batches have uniform shapes.

| Feature Type | Configuration Parameter | Padding Strategy |
|-------------|------------------------|------------------|
| Action | `max_action_dim` | Pad to maximum action dimension across datasets |
| State | `max_state_dim` | Pad to maximum state dimension |
| Environment State | `max_state_dim` | Same as state padding |
| Images | `max_image_dim` | Resize or pad to uniform dimensions |
| Number of Images | `max_num_images` | Pad with dummy camera streams |

The padding is applied in [src/lerobot/datasets/lerobot_dataset.py:643-653]() and uses the `reshape_features_to_max_dim` function to transform feature schemas. Statistics are also padded accordingly to ensure proper normalization of padded dimensions.

**Implementation:**

```mermaid
flowchart LR
    DS1["Dataset 1<br/>action: 7-dim<br/>state: 14-dim"]
    DS2["Dataset 2<br/>action: 5-dim<br/>state: 10-dim"]
    DS3["Dataset 3<br/>action: 6-dim<br/>state: 12-dim"]
    
    Config["Configuration<br/>max_action_dim: 7<br/>max_state_dim: 14"]
    
    Pad["Feature Padding<br/>reshape_features_to_max_dim"]
    
    Uniform["Uniform Batches<br/>All actions: 7-dim<br/>All states: 14-dim"]
    
    DS1 --> Pad
    DS2 --> Pad
    DS3 --> Pad
    Config --> Pad
    Pad --> Uniform
```

**Sources:** [src/lerobot/datasets/lerobot_dataset.py:643-653](), [src/lerobot/datasets/utils_must.py]()

---

## Motion Detection and Idle Frame Filtering

VLAb provides two mechanisms to filter out idle or stationary frames at the beginning of episodes, which can improve training efficiency by focusing on actionable demonstrations.

### Configuration Options

The frame filtering is controlled by three dataset configuration parameters:

- `discard_first_n_frames` (int): Remove the first N frames from each episode
- `discard_first_idle_frames` (bool): Automatically detect and remove idle frames
- `motion_threshold` (float): Velocity threshold for motion detection (default: 0.05)
- `motion_window_size` (int): Sliding window size for motion detection (default: 10)
- `motion_buffer` (int): Number of frames to include before detected motion (default: 3)

### Motion Detection Algorithm

When `discard_first_idle_frames=True`, the system analyzes robot state velocities to find the start of motion:

```mermaid
flowchart TB
    Episode["Episode Robot States<br/>[T, D] tensor"]
    
    Velocity["Compute Velocities<br/>np.linalg.norm(np.diff(states, axis=0), axis=1)"]
    
    Window["Sliding Window Analysis<br/>window_size frames"]
    
    Threshold["Check Mean Velocity<br/>window_mean > motion_threshold"]
    
    Buffer["Add Motion Buffer<br/>max(0, t - motion_buffer)"]
    
    Start["Motion Start Index"]
    
    Subset["Filtered Frame IDs<br/>from motion_start to episode_end"]
    
    Episode --> Velocity
    Velocity --> Window
    Window --> Threshold
    Threshold -->|"Found"| Buffer
    Threshold -->|"Not found"| Start
    Buffer --> Start
    Start --> Subset
```

The implementation in [src/lerobot/datasets/lerobot_dataset.py:610-623]() computes velocities from consecutive state differences, applies a sliding window to smooth the signal, and identifies when the mean velocity exceeds the threshold. A buffer is added to include context before the motion starts.

**Sources:** [src/lerobot/datasets/lerobot_dataset.py:410-423](), [src/lerobot/datasets/lerobot_dataset.py:610-623](), [src/lerobot/datasets/lerobot_dataset.py:110-116]()

---

## Multi-Dataset Aggregation and Cleaning

The `MultiLeRobotDataset` class handles training on multiple heterogeneous datasets simultaneously, with built-in validation and cleaning mechanisms.

### Dataset Validation Pipeline

```mermaid
flowchart TB
    Input["Input Datasets<br/>repo_ids, sampling_weights"]
    
    FPS["FPS Validation<br/>keep_datasets_with_valid_fps<br/>min_fps ≤ fps ≤ max_fps"]
    
    Features["Feature Consistency Check<br/>keep_datasets_with_the_same_features_per_robot_type"]
    
    RobotType["Group by Robot Type<br/>ROBOT_TYPE_KEYS_MAPPING"]
    
    Stats["Aggregate Statistics<br/>aggregate_stats_per_robot_type"]
    
    Union["Union Feature Schema<br/>Exclude disabled features"]
    
    Pad["Pad Features<br/>reshape_features_to_max_dim"]
    
    Final["MultiLeRobotDatasetMeta<br/>features, stats, episodes"]
    
    Input --> FPS
    FPS --> Features
    Features --> RobotType
    RobotType --> Stats
    Features --> Union
    Union --> Pad
    Pad --> Final
    Stats --> Final
```

The `MultiLeRobotDatasetCleaner` class [src/lerobot/datasets/lerobot_dataset.py:1279-1314]() implements a two-stage filtering process:

1. **FPS Validation**: Removes datasets with invalid frame rates outside the `[min_fps, max_fps]` range
2. **Feature Consistency**: Groups datasets by robot type and ensures all datasets for a given robot type have compatible features

After cleaning, sampling weights are adjusted and cumulative dataset sizes are computed for efficient indexing during training.

**Sources:** [src/lerobot/datasets/lerobot_dataset.py:1279-1314](), [src/lerobot/datasets/lerobot_dataset.py:1216-1277]()

### Robot Type Aggregation

Statistics aggregation respects robot types to enable proper normalization across different robot platforms:

```mermaid
graph TB
    subgraph "Datasets by Robot Type"
        R1["so_arm datasets"]
        R2["franka datasets"]
        R3["xarm datasets"]
    end
    
    subgraph "Per-Robot Statistics"
        S1["so_arm stats<br/>action min/max/mean/std<br/>state min/max/mean/std"]
        S2["franka stats<br/>action min/max/mean/std<br/>state min/max/mean/std"]
        S3["xarm stats<br/>action min/max/mean/std<br/>state min/max/mean/std"]
    end
    
    subgraph "Padded Statistics"
        PS["Padded to max_dims<br/>pad_tensor for each stat"]
    end
    
    R1 --> S1
    R2 --> S2
    R3 --> S3
    
    S1 --> PS
    S2 --> PS
    S3 --> PS
```

The `aggregate_stats_per_robot_type` function groups datasets by robot type and computes separate statistics for each group. This allows the policy to normalize actions and states appropriately for different robot platforms during training.

**Sources:** [src/lerobot/datasets/lerobot_dataset.py:1260-1271](), [src/lerobot/datasets/utils_must.py:aggregate_stats_per_robot_type]()

---

## Cache Management and Optimization

VLAb relies on HuggingFace's caching mechanisms for datasets and models. Understanding cache behavior is crucial for managing disk space and debugging download issues.

### Cache Structure

The default cache locations are:

| Component | Default Path | Environment Variable |
|-----------|-------------|---------------------|
| Datasets | `~/.cache/huggingface/datasets` | `HF_DATASETS_CACHE` |
| Models | `~/.cache/huggingface/hub` | `HF_HOME` |
| Transformers | `~/.cache/huggingface/transformers` | `TRANSFORMERS_CACHE` |
| LeRobot Datasets | `~/.cache/huggingface/lerobot` | `LEROBOT_HOME` |

### Cache Synchronization

The `force_cache_sync` parameter in `LeRobotDataset` [src/lerobot/datasets/lerobot_dataset.py:126]() controls whether to refresh cached metadata:

```python
meta = LeRobotDatasetMetadata(
    repo_id,
    root,
    force_cache_sync=True  # Forces re-download of metadata
)
```

When `force_cache_sync=True`, the system will re-download metadata files from the hub even if they exist locally, ensuring you have the latest dataset version.

### Manual Cache Cleanup

For corrupted or outdated cache entries, manual cleanup may be required:

```bash
# Remove all cached datasets
rm -rf ~/.cache/huggingface/datasets

# Remove all cached models
rm -rf ~/.cache/huggingface/hub

# Remove all cached transformers
rm -rf ~/.cache/huggingface/transformers
```

In SLURM environments, the cache cleanup can be automated by setting `CLEAN_CACHE=true` in the job script. This is particularly useful when encountering persistent cache corruption issues across cluster nodes.

**Sources:** [README.md:228-245](), [src/lerobot/datasets/lerobot_dataset.py:126](), [src/lerobot/datasets/lerobot_dataset.py:133-143]()

---

## Video Backend Selection and Configuration

VLAb supports multiple video decoding backends, each with different performance characteristics and compatibility requirements.

### Available Backends

| Backend | Description | Requirements | Performance |
|---------|-------------|--------------|-------------|
| `pyav` | FFmpeg-based decoder via PyAV | `av` package | Good compatibility, moderate speed |
| `video_reader` | Torchvision video_reader | Torchvision ≥0.9 | Fast, platform-dependent |
| `torchcodec` | Modern Torch codec (default when available) | Platform-specific | Best performance |

The backend is selected in [src/lerobot/datasets/lerobot_dataset.py:527]():

```python
self.video_backend = video_backend if video_backend else get_safe_default_codec()
```

The `get_safe_default_codec()` function attempts to use `torchcodec` if available, falling back to `pyav` for broader compatibility.

### Video Decoding Flow

```mermaid
flowchart LR
    Request["Frame Request<br/>episode_idx, video_key, timestamps"]
    
    Path["Video File Path<br/>meta.get_video_file_path"]
    
    Decode["decode_video_frames<br/>video_backend parameter"]
    
    subgraph "Backend Selection"
        PyAV["PyAV Decoder<br/>av.open()"]
        VR["video_reader Decoder<br/>torchvision"]
        TC["torchcodec Decoder<br/>torch.ops"]
    end
    
    Frames["Decoded Frames<br/>[T, C, H, W] tensor"]
    
    Request --> Path
    Path --> Decode
    Decode --> PyAV
    Decode --> VR
    Decode --> TC
    PyAV --> Frames
    VR --> Frames
    TC --> Frames
```

Video decoding happens on-demand during `__getitem__` calls [src/lerobot/datasets/lerobot_dataset.py:873-884](), using the configured backend to extract frames at specific timestamps. The decoder ensures frame timestamps match the requested timestamps within the specified `tolerance_s`.

**Sources:** [src/lerobot/datasets/lerobot_dataset.py:527](), [src/lerobot/datasets/lerobot_dataset.py:873-884](), [src/lerobot/datasets/video_utils.py:get_safe_default_codec]()

---

## Training Strategy Optimization

The SmolVLA2 architecture supports multiple training strategies with different compute and memory requirements.

### Training Mode Comparison

```mermaid
graph TB
    subgraph "train_expert_only=True"
        TE1["VLM Frozen<br/>requires_grad=False"]
        TE2["Expert Trainable<br/>requires_grad=True"]
        TE3["Low Memory<br/>~30% of full model"]
    end
    
    subgraph "freeze_vision_encoder=True"
        FV1["Vision Encoder Frozen"]
        FV2["Text Model Trainable"]
        FV3["Expert Trainable"]
        FV4["Medium Memory"]
    end
    
    subgraph "Full Fine-tuning"
        FF1["All Parameters Trainable"]
        FF2["Highest Memory"]
        FF3["Best Performance"]
    end
    
    subgraph "PEFT/LoRA"
        LR1["LoRA Adapters Added<br/>target_modules"]
        LR2["Low-rank Updates<br/>r, lora_alpha"]
        LR3["Very Low Memory"]
        LR4["90% of full performance"]
    end
```

The training mode is controlled by configuration parameters and implemented in [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:202-233]():

- `train_expert_only`: Freezes the entire VLM, trains only the expert model
- `freeze_vision_encoder`: Freezes vision encoder only, trains text model and expert
- `peft_method`: Applies parameter-efficient fine-tuning (LoRA) to specified modules

### PEFT Configuration

When using LoRA, the configuration specifies which modules to adapt:

```python
lora_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=peft_config.r,  # Rank of low-rank adaptation
    lora_alpha=peft_config.lora_alpha,  # Scaling factor
    lora_dropout=peft_config.lora_dropout,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    exclude_modules=["lm_expert"]  # Expert is always trained fully
)
```

The expert model is always excluded from LoRA adaptation and trained with full-rank updates, regardless of the PEFT configuration.

**Sources:** [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:151-184](), [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:202-233]()

---

## Attention Mode Configuration

The SmolVLA2 architecture supports two attention mechanisms that affect how the expert model interacts with the VLM.

### Self-Attention Mode

In self-attention mode (`attention_mode="self_attn"`), the VLM and expert process inputs independently and their outputs are concatenated:

```mermaid
graph TB
    Input["Input Embeddings"]
    
    subgraph "VLM Processing"
        V1["VLM Layers"]
        V2["Self-Attention"]
        V3["MLP"]
        VOut["VLM Output"]
    end
    
    subgraph "Expert Processing"
        E1["Expert Layers"]
        E2["Self-Attention"]
        E3["MLP"]
        EOut["Expert Output"]
    end
    
    Concat["Concatenate Outputs"]
    Final["Final Output"]
    
    Input --> V1
    V1 --> V2
    V2 --> V3
    V3 --> VOut
    
    Input --> E1
    E1 --> E2
    E2 --> E3
    E3 --> EOut
    
    VOut --> Concat
    EOut --> Concat
    Concat --> Final
```

### Cross-Attention Mode

In cross-attention mode (`attention_mode="cross_attn"`), the expert attends to VLM outputs, enabling richer information flow:

```mermaid
graph TB
    Input["Input Embeddings"]
    
    subgraph "VLM Processing"
        V1["VLM Layers"]
        V2["Self-Attention"]
        V3["MLP"]
        VOut["VLM Output<br/>(Keys & Values)"]
    end
    
    subgraph "Expert Processing"
        E1["Expert Layers"]
        E2["Cross-Attention<br/>Q from expert<br/>K,V from VLM"]
        E3["MLP"]
        EOut["Expert Output"]
    end
    
    Concat["Concatenate Outputs"]
    Final["Final Output"]
    
    Input --> V1
    V1 --> V2
    V2 --> V3
    V3 --> VOut
    
    Input --> E1
    E1 --> E2
    VOut --> E2
    E2 --> E3
    E3 --> EOut
    
    VOut --> Concat
    EOut --> Concat
    Concat --> Final
```

The cross-attention implementation [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:334-443]() reshapes the K and V projections to accept VLM hidden states as input, while Q comes from the expert's own hidden states. This allows the expert to selectively attend to relevant VLM features.

**Sources:** [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:70](), [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:124-138](), [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:334-443](), [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:479-508]()

---

## Expert Model Architecture Configuration

The expert model's architecture can be customized to balance performance and efficiency.

### Architecture Parameters

| Parameter | Description | Default | Impact |
|-----------|-------------|---------|--------|
| `num_expert_layers` | Number of transformer layers in expert | All VLM layers | Memory usage scales linearly |
| `expert_width_multiplier` | Hidden dimension multiplier | 0.5 | Quadratic memory impact |
| `num_vlm_layers` | Number of VLM layers to use | All layers | Affects KV cache size |
| `self_attn_every_n_layers` | Frequency of self-attention in cross-attn mode | -1 (disabled) | Reduces cross-attn computation |

### Layer Configuration Example

```mermaid
graph LR
    subgraph "VLM: 24 Layers"
        V0["Layer 0"]
        V1["Layer 1"]
        V2["..."]
        V23["Layer 23"]
    end
    
    subgraph "Expert: 6 Layers (num_expert_layers=6)"
        E0["Expert 0<br/>matches VLM 0"]
        E1["Expert 1<br/>matches VLM 4"]
        E2["Expert 2<br/>matches VLM 8"]
        E3["Expert 3<br/>matches VLM 12"]
        E4["Expert 4<br/>matches VLM 16"]
        E5["Expert 5<br/>matches VLM 20"]
    end
    
    V0 -.->|"cross-attn"| E0
    V1 --> V2
    V2 -.->|"cross-attn"| E1
    V23 -.->|"cross-attn"| E5
```

When `num_expert_layers` is less than `num_vlm_layers`, the expert layers are distributed evenly across the VLM depth. The implementation in [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:445-457]() computes the mapping:

```python
multiple_of = self.num_vlm_layers // self.num_expert_layers
for i in range(self.num_vlm_layers):
    if multiple_of > 0 and i > 0 and i % multiple_of != 0:
        expert_layer = None  # Skip this VLM layer
    else:
        expert_layer_index = i // multiple_of
        expert_layer = models[1].layers[expert_layer_index]
```

**Sources:** [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:64-75](), [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:104-122](), [src/lerobot/policies/smolvla2/smolvlm_with_expert2.py:445-457]()

---

