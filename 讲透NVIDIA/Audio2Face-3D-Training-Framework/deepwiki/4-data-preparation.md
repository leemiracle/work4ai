<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/Audio2Face-3D-Training-Framework · page 4 Data Preparation · fetched 2026-10-26 -->

# Data Preparation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [audio2face/geometry/anim_cache.py](audio2face/geometry/anim_cache.py)
- [audio2face/geometry/maya_cache.py](audio2face/geometry/maya_cache.py)
- [audio2face/geometry/point_cache.py](audio2face/geometry/point_cache.py)
- [audio2face/preproc/preproc.py](audio2face/preproc/preproc.py)
- [configs/example-diffusion-min/config_preproc.py](configs/example-diffusion-min/config_preproc.py)
- [configs/example-diffusion/config_preproc.py](configs/example-diffusion/config_preproc.py)
- [configs/example-regression-min/config_preproc.py](configs/example-regression-min/config_preproc.py)
- [configs/example-regression/config_preproc.py](configs/example-regression/config_preproc.py)
- [docs/preparing_animation_data.md](docs/preparing_animation_data.md)
- [run_preproc.py](run_preproc.py)
- [runners/run_preproc.py](runners/run_preproc.py)
- [runners/run_preproc_debug.py](runners/run_preproc_debug.py)

</details>



This page covers the data preparation phase of the Audio2Face-3D Training Framework, which transforms raw animation datasets into training-ready formats. Data preparation involves validating input data, organizing file structures, and preprocessing animation caches, audio files, and geometry information into the standardized formats required by the training pipeline.

For information about the training process that follows data preparation, see [Training Framework](#5). For details about the configuration system that controls data preparation parameters, see [Configuration System](#3).

## Purpose and Scope

The data preparation system serves as the critical bridge between raw animation data exported from Digital Content Creation (DCC) applications and the machine learning training pipeline. It handles format conversion, data validation, dimensionality reduction through PCA analysis, and audio feature extraction to create standardized training datasets.

The system supports multiple input formats and provides a unified preprocessing pipeline that can be configured for both regression and diffusion model training workflows.

## Data Requirements and File Organization

### Supported Input Formats

The framework supports multiple animation cache formats and follows a strict file organization structure:

```mermaid
graph TD
    subgraph "Raw Input Data"
        AudioFiles["Audio Files<br/>(.wav format)"]
        MayaCache["Maya Caches<br/>(.xml + .mc files)"]
        PointCache["Point Caches<br/>(.pc2 files)"] 
        NumpyCache["NumPy Arrays<br/>(.npy files)"]
        GeomData["Geometry Data<br/>(.npy, .json files)"]
        XformData["Transform Data<br/>(.npz files)"]
    end
    
    subgraph "File Organization Structure"
        AudioDir["audio/<br/>shot1.wav, shot2.wav"]
        CacheDir["cache/<br/>skin/, tongue/"]
        GeomDir["geom/<br/>skin/, tongue/"]  
        XformDir["xform/<br/>jaw, eye data"]
    end
    
    subgraph "Format Validation"
        Validator["Data Validation<br/>• Consistent topology<br/>• Matching framerates<br/>• Static head position"]
    end
    
    AudioFiles --> AudioDir
    MayaCache --> CacheDir
    PointCache --> CacheDir
    NumpyCache --> CacheDir
    GeomData --> GeomDir
    XformData --> XformDir
    
    AudioDir --> Validator
    CacheDir --> Validator
    GeomDir --> Validator
    XformDir --> Validator
```

Sources: [docs/preparing_animation_data.md:47-157](), [audio2face/geometry/anim_cache.py:22-32]()

### Technical Data Specifications

The framework enforces strict technical requirements for all input data:

| Data Type | Requirements | Format | Validation |
|-----------|--------------|---------|------------|
| Audio | WAV format, ≥16kHz, ≥16-bit | `.wav` | Duration matches animation |
| Skin Animation | Consistent topology, static head | `.xml+.mc`, `.pc2`, `.npy` | Vertex count consistency |
| Tongue Animation | Optional, same topology rules | `.xml+.mc`, `.pc2`, `.npy` | Matches skin framerate |
| Geometry Poses | Neutral, eye closed, lip open | `.npy` float32 | `[num_vertices, 3]` |
| Vertex Lists | Eye/lip distance, lip size | `.json` | Integer vertex indices |
| Transform Data | Jaw keypoints, eye rotations | `.npz` | `[num_frames, N, 3]` |

Sources: [docs/preparing_animation_data.md:47-113]()

## Preprocessing Pipeline Architecture

### Pipeline Orchestration

The preprocessing system follows a modular architecture with separate components for different data types:

```mermaid
graph LR
    subgraph "Entry Points"
        RunPreproc["run_preproc.py<br/>CONFIG_NAME + ACTOR_NAME"]
        RunnerPreproc["runners/run_preproc.py<br/>Docker container execution"]
    end
    
    subgraph "Core Preprocessing"
        PreprocMain["audio2face.preproc.preproc.run()"]
        PreprocSkin["preproc_skin.run()"]
        PreprocTongue["preproc_tongue.run()"]
        PreprocDeploy["preproc_deploy.run()"]
    end
    
    subgraph "Cache Format Handlers"  
        MayaCacheReader["maya_cache.MayaCacheReader"]
        PointCacheReader["point_cache.read_cache_pc2()"]
        AnimCacheUnified["anim_cache.read_cache()"]
    end
    
    subgraph "Configuration System"
        ConfigPreproc["config_preproc_base"]
        ConfigDataset["config_dataset_base"]
        ConfigMerger["utils.module_to_easy_dict()"]
    end
    
    RunPreproc --> RunnerPreproc
    RunnerPreproc --> PreprocMain
    PreprocMain --> PreprocSkin
    PreprocMain --> PreprocTongue
    PreprocMain --> PreprocDeploy
    
    PreprocSkin --> AnimCacheUnified
    PreprocTongue --> AnimCacheUnified
    AnimCacheUnified --> MayaCacheReader
    AnimCacheUnified --> PointCacheReader
    
    ConfigPreproc --> ConfigMerger
    ConfigDataset --> ConfigMerger
    ConfigMerger --> PreprocMain
```

Sources: [run_preproc.py:35-42](), [runners/run_preproc.py:45](), [audio2face/preproc/preproc.py:51-96]()

### Cache Format Support Matrix

The unified cache reading system provides format-agnostic access to animation data:

```mermaid
graph TD
    subgraph "Unified Interface"
        ReadCache["anim_cache.read_cache(fpath)"]
    end
    
    subgraph "Format Detection"
        ExtCheck{"File Extension<br/>Detection"}
    end
    
    subgraph "Format Handlers"
        NpyHandler["NumPy Loader<br/>np.load(fpath)"]
        MayaHandler["maya_cache.read_cache_mc()<br/>MayaCacheReader class"]
        PointHandler["point_cache.read_cache_pc2()<br/>struct-based parser"]
    end
    
    subgraph "Output Format"
        UnifiedArray["np.ndarray<br/>[frames, vertices, 3]<br/>dtype=float32"]
    end
    
    ReadCache --> ExtCheck
    ExtCheck -->|".npy"| NpyHandler
    ExtCheck -->|".xml"| MayaHandler  
    ExtCheck -->|".pc2"| PointHandler
    
    NpyHandler --> UnifiedArray
    MayaHandler --> UnifiedArray
    PointHandler --> UnifiedArray
```

Sources: [audio2face/geometry/anim_cache.py:22-32](), [audio2face/geometry/maya_cache.py:277-288](), [audio2face/geometry/point_cache.py:20-31]()

## Configuration System Integration

### Preprocessing Configuration Structure

The data preparation phase uses the two-tier configuration system with specialized preprocessing parameters:

| Configuration File | Purpose | Key Parameters |
|-------------------|---------|----------------|
| `config_preproc_base.py` | Base preprocessing settings | `PREPROC_OUTPUT_ROOT`, `RUN_NAME` |
| `config_dataset_base.py` | Dataset paths and structure | `AUDIO_ROOT`, `SKIN_CACHE_ROOT` |
| `configs/<name>/config_preproc.py` | User overrides | Custom `RUN_NAME`, `RUN_INFO` |
| `configs/<name>/config_dataset.py` | Dataset-specific paths | Actor-specific directory paths |

### Configuration Loading and Validation

```mermaid
graph LR
    subgraph "Configuration Loading"
        LoadConfig["utils.load_config()<br/>config_name, config_type"]
        ValidateConfig["utils.validate_cfg_mod()<br/>cfg_mod, base_module"]
        MergeConfig["utils.module_to_easy_dict()<br/>base_module, modifier"]
    end
    
    subgraph "Base Configurations"
        PreprocBase["config_preproc_base"]
        DatasetBase["config_dataset_base"]
    end
    
    subgraph "User Configurations"  
        PreprocUser["configs/<name>/config_preproc.py"]
        DatasetUser["configs/<name>/config_dataset.py"]
    end
    
    subgraph "Final Configuration"
        EasyDictPreproc["cfg_preproc: EasyDict"]
        EasyDictDataset["cfg_dataset: EasyDict"]
    end
    
    PreprocBase --> ValidateConfig
    DatasetBase --> ValidateConfig
    PreprocUser --> LoadConfig
    DatasetUser --> LoadConfig
    
    LoadConfig --> ValidateConfig
    ValidateConfig --> MergeConfig
    MergeConfig --> EasyDictPreproc
    MergeConfig --> EasyDictDataset
```

Sources: [audio2face/preproc/preproc.py:71-74](), [configs/example-diffusion/config_preproc.py:17-20]()

## Maya Cache Format Implementation

The Maya cache format handler provides comprehensive support for Autodesk Maya's native cache format:

### MayaCacheReader Architecture

```mermaid
graph TD
    subgraph "Maya Cache Components"
        XmlFile[".xml Metadata File<br/>• Cache type, time range<br/>• Channel definitions<br/>• Frame rate info"]
        McFile[".mc Binary Data File<br/>• FOR4 block structure<br/>• FVCA/DVCA vertex data<br/>• Frame-by-frame storage"]
    end
    
    subgraph "MayaCacheReader Class"
        Constructor["__init__(xml_path)<br/>• Parse XML metadata<br/>• Locate .mc binary file<br/>• Extract channel info"]
        XmlParser["_parse_xml()<br/>• Extract time range<br/>• Parse channel definitions<br/>• Get sampling rates"]
        BinaryReader["read_frames()<br/>• Parse FOR4/MYCH blocks<br/>• Handle FVCA/DVCA data<br/>• Yield np.ndarray per frame"]
        ByteSwap["_need_byte_swap()<br/>• Platform endianness<br/>• Windows/Linux support"]
    end
    
    subgraph "Data Output"
        FrameGenerator["Generator[np.ndarray]<br/>• Shape: [num_vertices, 3]<br/>• dtype: float32/float64<br/>• Memory efficient"]
    end
    
    XmlFile --> Constructor
    McFile --> BinaryReader
    Constructor --> XmlParser
    XmlParser --> BinaryReader
    BinaryReader --> ByteSwap
    BinaryReader --> FrameGenerator
```

Sources: [audio2face/geometry/maya_cache.py:24-180]()

### Binary Format Parsing

The Maya cache binary format uses a complex block structure that the reader parses sequentially:

| Block Type | Purpose | Structure |
|------------|---------|-----------|
| `FOR4` | File/Block Header | 4-byte tag + 32-bit size |
| `MYCH` | Maya Cache Header | Identifies cache block |
| `TIME` | Frame Timestamp | 32-bit frame time |
| `CHNM` | Channel Name | Variable-length string |
| `FVCA`/`DVCA` | Vertex Array Data | Float32/Float64 vertex positions |

Sources: [audio2face/geometry/maya_cache.py:86-180]()

## Metadata Export and Tracking

The preprocessing system maintains comprehensive metadata about each preprocessing run:

### Export Metadata Function

```mermaid
graph LR
    subgraph "Metadata Components"
        VersionInfo["VERSION.md<br/>Framework version"]
        RunInfo["info.txt<br/>RUN_INFO description"]  
        ConfigMods["*_modifier.json<br/>Configuration overrides"]
        ActorInfo["actor_info.json<br/>Actor name"]
    end
    
    subgraph "Full Exposure Mode"
        FullConfigs["*_full.json<br/>Complete configurations"]
        StateInfo["state.json<br/>Git state, environment"]
    end
    
    subgraph "export_meta_data() Function"
        CopyVersion["shutil.copy(VERSION.md)"]
        WriteInfo["Write RUN_INFO to file"]
        DumpJson["utils.json_dump_pretty()"]
        CheckExposure["utils.is_partial_exposure()"]
    end
    
    CopyVersion --> VersionInfo
    WriteInfo --> RunInfo
    DumpJson --> ConfigMods
    DumpJson --> ActorInfo
    CheckExposure --> FullConfigs
    CheckExposure --> StateInfo
```

Sources: [audio2face/preproc/preproc.py:28-49]()

This comprehensive data preparation system ensures that raw animation data from various DCC applications is properly validated, organized, and preprocessed into the standardized formats required by the Audio2Face-3D training pipeline, while maintaining full traceability through detailed metadata tracking.

---

