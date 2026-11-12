<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/satlas-super-resolution · page 3 Data Pipeline · fetched 2026-10-26 -->

# Data Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [ssr/data/s2-naip_dataset.py](ssr/data/s2-naip_dataset.py)
- [ssr/utils/data_utils.py](ssr/utils/data_utils.py)

</details>



This document explains how satellite imagery data flows through the system, from raw Sentinel-2 and NAIP inputs to processed training pairs ready for model consumption. The data pipeline handles the pairing, loading, validation, and augmentation of multi-temporal satellite imagery with high-resolution aerial imagery ground truth.

For information about model training using this processed data, see [Training](#5). For details on inference pipeline processing, see [Inference](#6).

## Data Flow Overview

The data pipeline transforms raw satellite and aerial imagery into paired training samples through a series of processing stages:

```mermaid
flowchart LR
    subgraph "Raw Data Sources"
        A["Sentinel-2 L1C\n32x32 chips\nMultiple bands\nTime series"]
        B["NAIP Imagery\n128x128 chips\nRGB ground truth\nHigh resolution"]
        C["OSM Objects\n(Optional)\nGeographic features\nObject masks"]
    end
    
    subgraph "S2NAIPDataset"
        D["Data Pairing\nChip coordination\nTemporal matching"]
        E["Band Selection\ns2_bands config\nTCI + optional"]
        F["Temporal Selection\nn_s2_images\nRandom sampling"]
    end
    
    subgraph "Data Processing"
        G["Validation\nhas_black_pixels\nQuality filtering"]
        H["Augmentation\nRandom cropping\nResize operations"]
        I["Tensor Formatting\nShape reshaping\nDevice preparation"]
    end
    
    subgraph "Sampling Strategy"
        J["CustomWeightedRandomSampler\nLarge dataset support\nOSM-based weighting"]
    end
    
    subgraph "Model Input"
        K["Training Batch\n{hr, lr, chip}\nReady for training"]
    end
    
    A --> D
    B --> D
    C --> D
    D --> E
    E --> F
    F --> G
    G --> H
    H --> I
    I --> J
    J --> K
```

**Data Pipeline Flow Diagram**

Sources: [ssr/data/s2-naip_dataset.py:35-249](), [ssr/utils/data_utils.py:3-10]()

## Core Dataset Implementation

The `S2NAIPDataset` class serves as the primary data loading mechanism, registered with BasicSR's dataset registry system:

```mermaid
graph TB
    subgraph "Dataset Registry"
        A["DATASET_REGISTRY.register()\nBasicSR integration"]
    end
    
    subgraph "S2NAIPDataset Class"
        B["__init__(opt)\nConfiguration parsing\nData path validation"]
        C["__getitem__(index)\nBatch loading\nData processing"]
        D["__len__()\nDataset size"]
        E["get_tile_weight_sampler()\nCustom sampling strategy"]
    end
    
    subgraph "Data Structures"
        F["self.datapoints\nList of data tuples\n[naip_path, s2_paths, chip]"]
        G["self.naip_chips\nNAIP file paths\nGlob-based discovery"]
        H["Configuration Options\nPhase, bands, scale, augmentation"]
    end
    
    subgraph "Processing Components"
        I["Band Loading\nMulti-band S2 imagery\nTCI + spectral bands"]
        J["Temporal Selection\nRandom time sampling\nGood/bad filtering"]
        K["Quality Validation\nBlack pixel detection\nError handling"]
    end
    
    A --> B
    B --> F
    B --> G
    B --> H
    C --> I
    C --> J
    C --> K
    E --> F
```

**S2NAIPDataset Class Architecture**

Sources: [ssr/data/s2-naip_dataset.py:34-50](), [ssr/data/s2-naip_dataset.py:152-246]()

## Data Loading and Pairing Process

The dataset pairs Sentinel-2 time series with corresponding NAIP imagery based on geographic chip coordinates:

| Component | Description | Configuration Key | File Reference |
|-----------|-------------|-------------------|----------------|
| **Chip Extraction** | Extract X,Y coordinates from file paths | N/A | [ssr/data/s2-naip_dataset.py:107-109]() |
| **S2 Band Loading** | Load multiple spectral bands per chip | `s2_bands` | [ssr/data/s2-naip_dataset.py:120-121]() |
| **Temporal Sampling** | Select N images from time series | `n_s2_images` | [ssr/data/s2-naip_dataset.py:216-225]() |
| **NAIP Loading** | Load high-resolution ground truth | N/A | [ssr/data/s2-naip_dataset.py:171-177]() |
| **Shape Formatting** | Reshape tensors for model input | `use_3d` | [ssr/data/s2-naip_dataset.py:237-239]() |

The pairing process handles several data scenarios:

- **Standard Pairing**: Current S2 time series with contemporary NAIP imagery
- **Historical Pairing**: Optional older NAIP imagery for temporal analysis via `old_naip_path` [ssr/data/s2-naip_dataset.py:65-67]()
- **OSM Filtering**: Geographic feature-based filtering using `osm_objs_path` [ssr/data/s2-naip_dataset.py:69-70]()

Sources: [ssr/data/s2-naip_dataset.py:105-127](), [ssr/data/s2-naip_dataset.py:181-196]()

## Data Processing and Augmentation

The pipeline includes several processing steps to prepare data for training:

### Temporal Selection Strategy

```mermaid
flowchart TD
    A["Load S2 Time Series\nAll available timestamps"] --> B["Extract TCI Chunks\ntci_chunks = s2_tensor[:, :3, :, :]"]
    B --> C["Quality Assessment\nhas_black_pixels() validation"]
    C --> D{"Sufficient Good Images?"}
    
    D -->|"len(goods) >= n_s2_images"| E["Random Sample from Good\nrandom.sample(goods, n_s2_images)"]
    D -->|"Insufficient Good Images"| F["Mixed Sample\ngoods + random.sample(bads, need)"]
    
    E --> G["Extract Selected Images\nimg_S2 = s2_tensor[rand_indices_tensor]"]
    F --> G
    
    G --> H["Shape Processing\nReshape for model input"]
```

**Temporal Selection Algorithm**

Sources: [ssr/data/s2-naip_dataset.py:208-225](), [ssr/data/s2-naip_dataset.py:237-239]()

### Augmentation Pipeline

The system supports training-time augmentation through random cropping:

- **Random Crop Size**: Selects crop size between 24-32 pixels for low-resolution input [ssr/data/s2-naip_dataset.py:230]()
- **Proportional HR Cropping**: Maintains 4x scale relationship with high-resolution crop [ssr/data/s2-naip_dataset.py:231]()
- **Resize Back**: Uses `F.interpolate` to restore original dimensions [ssr/data/s2-naip_dataset.py:234-235]()

Sources: [ssr/data/s2-naip_dataset.py:227-235]()

## Custom Sampling Strategy

The `CustomWeightedRandomSampler` addresses PyTorch's limitation for large datasets:

```mermaid
graph LR
    subgraph "Standard PyTorch"
        A["WeightedRandomSampler\nLimit: 2^24 samples\nInsufficient for large datasets"]
    end
    
    subgraph "Custom Implementation"
        B["CustomWeightedRandomSampler\nNumPy-based sampling\nNo size limitations"]
        C["get_tile_weight_sampler()\nOSM-based weighting\nGeographic feature emphasis"]
    end
    
    subgraph "Weighting Strategy"
        D["Default Weight: 1\nChips without OSM features"]
        E["Custom Weight: Variable\nChips with OSM features\nFrom tile_weights dict"]
    end
    
    A --> B
    B --> C
    C --> D
    C --> E
```

**Custom Sampling Architecture**

The weighting system enables emphasis on geographic features:

- **Base Weight**: Chips without OSM features receive weight of 1 [ssr/data/s2-naip_dataset.py:145]()
- **Enhanced Weight**: Chips with OSM features use `tile_weights` dictionary values [ssr/data/s2-naip_dataset.py:147]()
- **Weight Statistics**: System reports min/max/mean weights for monitoring [ssr/data/s2-naip_dataset.py:149]()

Sources: [ssr/data/s2-naip_dataset.py:18-32](), [ssr/data/s2-naip_dataset.py:132-150]()

## Data Validation and Quality Control

The pipeline implements robust quality control through several validation mechanisms:

### Black Pixel Detection

The `has_black_pixels` utility function identifies invalid imagery:

```python
# From ssr/utils/data_utils.py:3-10
def has_black_pixels(tensor):
    channel_sum = torch.sum(tensor, dim=0)
    black_pixels = (channel_sum.view(-1) == 0).any()
    return black_pixels
```

This validation applies at multiple stages:
- **NAIP Validation**: Skip chips with invalid ground truth [ssr/data/s2-naip_dataset.py:174-176]()
- **S2 Temporal Validation**: Classify time series images as good/bad [ssr/data/s2-naip_dataset.py:210-214]()

### Error Handling Strategy

The `__getitem__` method uses a retry loop to handle data loading failures:

- **Counter-based Retry**: Increment index when errors occur [ssr/data/s2-naip_dataset.py:157-161]()
- **Multiple Validation Points**: Check data quality at each processing stage
- **Graceful Fallback**: Continue to next sample on validation failure

Sources: [ssr/utils/data_utils.py:3-10](), [ssr/data/s2-naip_dataset.py:157-204]()

## Configuration Parameters

The dataset supports extensive configuration through the `opt` dictionary:

| Parameter | Type | Description | Default | Reference |
|-----------|------|-------------|---------|-----------|
| `sentinel2_path` | str | Path to S2 imagery directory | Required | [ssr/data/s2-naip_dataset.py:94]() |
| `naip_path` | str | Path to NAIP imagery directory | Required | [ssr/data/s2-naip_dataset.py:95]() |
| `n_s2_images` | int | Number of S2 timesteps to use | Required | [ssr/data/s2-naip_dataset.py:58]() |
| `scale` | int | Upsampling factor (4x supported) | 4 | [ssr/data/s2-naip_dataset.py:59]() |
| `phase` | str | Training phase ('train' or 'val') | Required | [ssr/data/s2-naip_dataset.py:52]() |
| `use_3d` | bool | Maintain temporal dimension | False | [ssr/data/s2-naip_dataset.py:63]() |
| `rand_crop` | bool | Enable random crop augmentation | False | [ssr/data/s2-naip_dataset.py:56]() |
| `s2_bands` | list | S2 spectral bands to load | ['tci'] | [ssr/data/s2-naip_dataset.py:73]() |
| `train_samples` | int | Limit training set size | None | [ssr/data/s2-naip_dataset.py:102-103]() |
| `old_naip_path` | str | Path to historical NAIP imagery | None | [ssr/data/s2-naip_dataset.py:67]() |
| `osm_objs_path` | str | Path to OSM object masks | None | [ssr/data/s2-naip_dataset.py:70]() |
| `n_osm_objs` | int | Minimum OSM objects per chip | None | [ssr/data/s2-naip_dataset.py:117]() |

### Band Configuration

The system supports multiple Sentinel-2 spectral bands with automatic TCI prioritization:

- **TCI Priority**: TCI band moved to front of band list [ssr/data/s2-naip_dataset.py:75]()
- **Multi-band Support**: Additional spectral bands concatenated as channels [ssr/data/s2-naip_dataset.py:196]()
- **Missing Band Handling**: Zero tensors used when bands unavailable [ssr/data/s2-naip_dataset.py:186-188]()

Sources: [ssr/data/s2-naip_dataset.py:48-103](), [ssr/data/s2-naip_dataset.py:183-196]()

---

