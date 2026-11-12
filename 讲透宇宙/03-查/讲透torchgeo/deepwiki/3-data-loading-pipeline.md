<!-- source: DeepWiki mcp.deepwiki.com · repo torchgeo/torchgeo · page 3 Data Loading Pipeline · fetched 2026-10-21 -->

# Data Loading Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/api/datamodules.rst](docs/api/datamodules.rst)
- [docs/api/datasets.rst](docs/api/datasets.rst)
- [tests/data/deepglobelandcover/data.py](tests/data/deepglobelandcover/data.py)
- [tests/data/deepglobelandcover/data.zip](tests/data/deepglobelandcover/data.zip)
- [tests/data/naip/data.py](tests/data/naip/data.py)
- [tests/data/naip/m_3807511_ne_18_060_20181104.tif](tests/data/naip/m_3807511_ne_18_060_20181104.tif)
- [tests/data/naip/m_3807511_ne_18_060_20190605.tif](tests/data/naip/m_3807511_ne_18_060_20190605.tif)
- [tests/data/vector/data.py](tests/data/vector/data.py)
- [tests/data/vector/vector_2024.geojson](tests/data/vector/vector_2024.geojson)
- [tests/data/vector/vector_2024.parquet](tests/data/vector/vector_2024.parquet)
- [tests/datasets/test_deepglobelandcover.py](tests/datasets/test_deepglobelandcover.py)
- [tests/datasets/test_geo.py](tests/datasets/test_geo.py)
- [tests/datasets/test_utils.py](tests/datasets/test_utils.py)
- [tests/trainers/test_segmentation.py](tests/trainers/test_segmentation.py)
- [torchgeo/datamodules/__init__.py](torchgeo/datamodules/__init__.py)
- [torchgeo/datasets/__init__.py](torchgeo/datasets/__init__.py)
- [torchgeo/datasets/cdl.py](torchgeo/datasets/cdl.py)
- [torchgeo/datasets/deepglobelandcover.py](torchgeo/datasets/deepglobelandcover.py)
- [torchgeo/datasets/geo.py](torchgeo/datasets/geo.py)
- [torchgeo/datasets/landsat.py](torchgeo/datasets/landsat.py)
- [torchgeo/datasets/naip.py](torchgeo/datasets/naip.py)
- [torchgeo/datasets/sentinel.py](torchgeo/datasets/sentinel.py)
- [torchgeo/datasets/utils.py](torchgeo/datasets/utils.py)

</details>



## Purpose and Scope

The data loading pipeline in TorchGeo is responsible for transforming raw geospatial data from datasets into batched tensors ready for model training. This pipeline bridges the dataset layer (see [Dataset System](#2)) with the training system (see [Training System](#5)) by handling spatial/temporal sampling, data augmentation, and batch preparation.

This page covers the overall architecture and flow of data through the pipeline. For implementation details on specific components, see:
- [Samplers](#3.1) for spatial/temporal query generation
- [Transforms and Augmentation](#3.2) for preprocessing and augmentation
- [DataModules](#3.3) for train/val/test splitting and DataLoader configuration

---

## Pipeline Architecture

The data loading pipeline consists of three main stages that operate sequentially to prepare data for training:

```mermaid
graph TB
    subgraph "Stage 1: Query Generation"
        DS["Dataset<br/>(GeoDataset or NonGeoDataset)"]
        Sampler["Sampler<br/>(RandomGeoSampler, GridGeoSampler)"]
        Query["Query/Index<br/>(GeoSlice or int)"]
    end
    
    subgraph "Stage 2: Data Retrieval & Transform"
        GetItem["Dataset.__getitem__()"]
        RawSample["Raw Sample<br/>{image, mask, crs, bounds}"]
        Transform["Transform Pipeline<br/>(augmentation, indices)"]
        ProcessedSample["Transformed Sample"]
    end
    
    subgraph "Stage 3: Batching & Loading"
        DataLoader["PyTorch DataLoader"]
        CollateFn["Collate Function<br/>(stack_samples, concat_samples)"]
        Batch["Batched Tensors<br/>Ready for Training"]
    end
    
    DS --> Sampler
    Sampler --> Query
    Query --> GetItem
    GetItem --> RawSample
    RawSample --> Transform
    Transform --> ProcessedSample
    ProcessedSample --> DataLoader
    DataLoader --> CollateFn
    CollateFn --> Batch
```

**Sources:** [torchgeo/datasets/geo.py:50-309](), [torchgeo/datasets/utils.py:474-559]()

---

## Pipeline Components

### Query Generation and Sampling

The pipeline begins with query generation, which differs fundamentally between geospatial and non-geospatial datasets:

| Component | GeoDataset Pipeline | NonGeoDataset Pipeline |
|-----------|---------------------|------------------------|
| **Input** | Spatiotemporal bounds | Integer index |
| **Sampler** | `RandomGeoSampler`, `GridGeoSampler` | Standard PyTorch sampler |
| **Query Format** | `GeoSlice` (slice objects for x, y, t) | `int` |
| **Index Structure** | `GeoDataFrame` with geometry + time | List-based integer indexing |

```mermaid
graph LR
    subgraph "GeoDataset Path"
        GB["GeoDataset.bounds<br/>(xmin:xmax, ymin:ymax, tmin:tmax)"]
        RGS["RandomGeoSampler<br/>generates random patches"]
        GS["GeoSlice<br/>(slice(x), slice(y), slice(t))"]
        GDI["GeoDataset.__getitem__(query)"]
    end
    
    subgraph "NonGeoDataset Path"
        NL["NonGeoDataset.__len__()"]
        RS["RandomSampler<br/>generates indices"]
        IDX["int index"]
        NDI["NonGeoDataset.__getitem__(index)"]
    end
    
    GB --> RGS --> GS --> GDI
    NL --> RS --> IDX --> NDI
```

**GeoSlice Format:**  The `GeoSlice` type alias represents spatiotemporal queries as a tuple of 1-3 slice objects: `(slice(xmin, xmax, xres), slice(ymin, ymax, yres), slice(tmin, tmax, tres))`. Partial slices are disambiguated using the dataset's full bounds.

**Sources:** [torchgeo/datasets/utils.py:48-50](), [torchgeo/datasets/geo.py:116-142]()

---

### Data Retrieval with `__getitem__`

When a dataset's `__getitem__` method is called with a query, it performs the following operations:

```mermaid
graph TB
    Query["Query<br/>(GeoSlice or index)"]
    
    subgraph "RasterDataset.__getitem__()"
        Disambig["_disambiguate_slice()<br/>Resolve partial queries"]
        IndexLookup["Index Lookup<br/>Find overlapping files"]
        MergeFiles["_merge_files()<br/>Load & merge rasters"]
        CastDtype["Cast to dtype<br/>(float32 for images, long for masks)"]
        ApplyTransform["Apply transforms<br/>if provided"]
    end
    
    Sample["Sample dict<br/>{image/mask, crs, bounds}"]
    
    Query --> Disambig
    Disambig --> IndexLookup
    IndexLookup --> MergeFiles
    MergeFiles --> CastDtype
    CastDtype --> ApplyTransform
    ApplyTransform --> Sample
```

**Key Implementation Details:**

1. **Spatial Index Query:** The GeoDataFrame index is queried using `.cx[xmin:xmax, ymin:ymax]` for spatial filtering and `.index.overlaps(interval)` for temporal filtering [torchgeo/datasets/geo.py:518-522]()

2. **File Merging:** For datasets with multiple overlapping files, `rasterio.merge.merge()` combines them into a single array [torchgeo/datasets/geo.py:587-589]()

3. **Transform Application:** If transforms are provided in the dataset constructor, they are applied after data loading but before returning [torchgeo/datasets/geo.py:558-559]()

4. **Caching:** The `cache` parameter enables LRU caching of file handles via `_cached_load_warp_file()` to speed up repeated sampling [torchgeo/datasets/geo.py:594-604]()

**Sources:** [torchgeo/datasets/geo.py:506-561]()

---

### Transform Pipeline

Transforms are applied to samples after data loading but before batching. TorchGeo supports standard PyTorch/Kornia transforms plus custom geospatial transforms:

```mermaid
graph LR
    Sample["Raw Sample<br/>{image: Tensor, mask: Tensor}"]
    
    subgraph "Transform Pipeline"
        Aug1["Augmentation<br/>(RandomFlip, RandomRotation)"]
        Aug2["Color Jittering<br/>(RandomGamma, Normalize)"]
        Indices["Spectral Indices<br/>(AppendNDVI, AppendNDWI)"]
    end
    
    Transformed["Transformed Sample<br/>{image: Tensor, mask: Tensor}"]
    
    Sample --> Aug1 --> Aug2 --> Indices --> Transformed
```

**Transform Categories:**

- **Augmentation:** Spatial (flip, rotation, crop) and radiometric (brightness, contrast) augmentations
- **Spectral Indices:** Compute NDVI, NDWI, and other vegetation/water indices from multispectral bands
- **Normalization:** Per-channel mean/std normalization for pretrained models

Transforms are passed to the dataset constructor and stored as `self.transforms`, then applied in `__getitem__()` immediately before returning the sample.

**Sources:** [torchgeo/datasets/geo.py:404-405](), [torchgeo/datasets/geo.py:558-559]()

---

## DataModules and Batching

The final stage wraps datasets, samplers, and transforms into PyTorch Lightning DataModules that handle train/val/test splitting and DataLoader configuration:

```mermaid
graph TB
    subgraph "DataModule Structure"
        DM["BaseDataModule"]
        GeoDM["GeoDataModule"]
        NonGeoDM["NonGeoDataModule"]
        
        DM --> GeoDM
        DM --> NonGeoDM
    end
    
    subgraph "Components Created by setup()"
        TrainDS["train_dataset"]
        ValDS["val_dataset"]
        TestDS["test_dataset"]
        TrainSampler["train_sampler<br/>(RandomGeoSampler)"]
        ValSampler["val_sampler<br/>(GridGeoSampler)"]
    end
    
    subgraph "DataLoaders Created by *_dataloader()"
        TrainDL["train_dataloader<br/>(shuffle=True)"]
        ValDL["val_dataloader<br/>(shuffle=False)"]
        TestDL["test_dataloader<br/>(shuffle=False)"]
    end
    
    GeoDM -.->|creates| TrainDS
    GeoDM -.->|creates| ValDS
    GeoDM -.->|creates| TestDS
    GeoDM -.->|creates| TrainSampler
    GeoDM -.->|creates| ValSampler
    
    TrainDS --> TrainDL
    ValDS --> ValDL
    TestDS --> TestDL
    TrainSampler --> TrainDL
    ValSampler --> ValDL
```

**Collation Functions:**

DataLoaders use custom collation functions to combine individual samples into batches:

| Function | Purpose | Use Case |
|----------|---------|----------|
| `stack_samples()` | Stack samples along new batch dimension | Standard minibatch creation |
| `concat_samples()` | Concatenate samples along channel dimension | Multi-modal fusion (IntersectionDataset) |
| `merge_samples()` | Merge overlapping samples by taking maximum | Union of datasets |
| `pad_across_batches()` | Pad variable-length sequences | Time series with different lengths |

**Sources:** [torchgeo/datasets/utils.py:474-560](), [torchgeo/datamodules/geo.py:1-200]()

---

## Pipeline Variants

TorchGeo implements two distinct pipeline variants optimized for different dataset types:

### GeoDataset Pipeline

For spatially-indexed datasets like Landsat, Sentinel, or NAIP:

```mermaid
graph LR
    RasterDS["RasterDataset<br/>(Landsat, Sentinel, NAIP)"]
    Index["GeoDataFrame Index<br/>(geometry + time)"]
    Sampler["RandomGeoSampler<br/>(size, length)"]
    Query["GeoSlice Query<br/>(x:x+size, y:y+size, t)"]
    GetItem["__getitem__(query)"]
    Load["Load & Merge Files<br/>rasterio.merge"]
    Sample["Sample<br/>{image, crs, bounds}"]
    
    RasterDS --> Index
    Index --> Sampler
    Sampler --> Query
    Query --> GetItem
    GetItem --> Load
    Load --> Sample
```

**Key Characteristics:**
- Queries are spatiotemporal bounding boxes (GeoSlice)
- Multiple files may overlap a single query and must be merged
- CRS and resolution can be specified to automatically warp data
- Supports both single-file and separate-file-per-band datasets

**Sources:** [torchgeo/datasets/geo.py:311-624]()

---

### NonGeoDataset Pipeline

For pre-curated datasets like EuroSAT, RESISC45, or BigEarthNet:

```mermaid
graph LR
    NonGeoDS["NonGeoClassificationDataset<br/>(EuroSAT, RESISC45)"]
    FileList["List of image files"]
    Sampler["RandomSampler<br/>(standard PyTorch)"]
    Index["Integer index"]
    GetItem["__getitem__(index)"]
    Load["Load Single File<br/>PIL or rasterio"]
    Sample["Sample<br/>{image, label}"]
    
    NonGeoDS --> FileList
    FileList --> Sampler
    Sampler --> Index
    Index --> GetItem
    GetItem --> Load
    Load --> Sample
```

**Key Characteristics:**
- Queries are simple integer indices
- Each index maps to exactly one file (no merging required)
- No CRS or spatial information in returned samples
- Uses standard PyTorch samplers and data loaders

**Sources:** [torchgeo/datasets/geo.py:1048-1178]()

---

## Integration with Training

The data loading pipeline integrates with the training system through PyTorch Lightning's DataModule interface:

```mermaid
graph TB
    subgraph "Data Pipeline Output"
        Batch["Mini-batch<br/>{image: (B,C,H,W), mask: (B,H,W)}"]
    end
    
    subgraph "Training System Input"
        Task["LightningModule<br/>(SemanticSegmentationTask)"]
        TrainStep["training_step(batch, batch_idx)"]
        Forward["model(batch['image'])"]
        Loss["loss_fn(pred, batch['mask'])"]
    end
    
    Batch --> TrainStep
    TrainStep --> Forward
    Forward --> Loss
```

The DataModule provides three methods that the Trainer calls automatically:
- `train_dataloader()`: Returns DataLoader for training with shuffling enabled
- `val_dataloader()`: Returns DataLoader for validation with shuffling disabled
- `test_dataloader()`: Returns DataLoader for testing with shuffling disabled

Each DataLoader is configured with:
- `batch_size`: Number of samples per batch
- `num_workers`: Number of parallel data loading processes
- `collate_fn`: Function to combine samples into batches (e.g., `stack_samples`)
- `sampler`: Strategy for generating queries/indices (e.g., `RandomGeoSampler`)

**Sources:** [torchgeo/datamodules/geo.py:1-200](), [tests/trainers/test_segmentation.py:1-289]()

---

## Common Pipeline Patterns

### Multi-Modal Fusion

When combining multiple data sources (e.g., imagery + labels), use `IntersectionDataset` with `concat_samples`:

```mermaid
graph LR
    Landsat["Landsat Dataset<br/>(images)"]
    CDL["CDL Dataset<br/>(labels)"]
    Intersection["IntersectionDataset<br/>(landsat & cdl)"]
    Query["Same GeoSlice<br/>for both datasets"]
    Concat["concat_samples()<br/>combine channels"]
    Batch["Batch<br/>{image: (B,13,H,W), mask: (B,H,W)}"]
    
    Landsat --> Intersection
    CDL --> Intersection
    Intersection --> Query
    Query --> Concat
    Concat --> Batch
```

**Sources:** [torchgeo/datasets/geo.py:158-172](), [torchgeo/datasets/utils.py:495-514]()

---

### Time Series Data

For temporal sequences with variable lengths, use `pad_across_batches` as the collate function:

```mermaid
graph LR
    PASTIS["PASTIS Dataset<br/>(time series)"]
    Sample1["Sample 1<br/>(T1, C, H, W)"]
    Sample2["Sample 2<br/>(T2, C, H, W)"]
    Pad["pad_across_batches()<br/>(padding_length=50)"]
    Batch["Padded Batch<br/>(B, 50, C, H, W)"]
    
    PASTIS --> Sample1
    PASTIS --> Sample2
    Sample1 --> Pad
    Sample2 --> Pad
    Pad --> Batch
```

The function pads shorter sequences to a fixed length and truncates longer sequences, issuing a warning if truncation occurs.

**Sources:** [torchgeo/datasets/utils.py:425-471](), [torchgeo/datamodules/pastis.py:1-90]()

---

## Performance Optimization

The pipeline includes several optimization strategies:

| Strategy | Implementation | Benefit |
|----------|----------------|---------|
| **File Handle Caching** | `@functools.lru_cache` on `_cached_load_warp_file()` | Avoid repeated file opens for overlapping queries |
| **Parallel Loading** | `num_workers > 0` in DataLoader | Load data in parallel processes |
| **Pin Memory** | `pin_memory=True` in DataLoader | Faster GPU transfer |
| **WarpedVRT** | `rasterio.vrt.WarpedVRT` for CRS/resolution changes | Lazy reprojection without copying data |

**Sources:** [torchgeo/datasets/geo.py:594-624](), [torchgeo/datasets/geo.py:606-623]()

---

## Summary

The TorchGeo data loading pipeline provides a flexible architecture for transforming raw geospatial data into training-ready batches. Key design decisions include:

1. **Dual Pathways**: Separate optimized pipelines for geospatial (query-based) and non-geospatial (index-based) datasets
2. **Composability**: Datasets, samplers, transforms, and collation functions can be mixed and matched
3. **Lazy Evaluation**: Data is only loaded when needed, and CRS/resolution transformations are performed lazily
4. **Standard Interfaces**: Builds on PyTorch's Dataset/DataLoader and Lightning's DataModule abstractions

For implementation details on each component, see the child pages: [Samplers](#3.1), [Transforms and Augmentation](#3.2), and [DataModules](#3.3).

---

