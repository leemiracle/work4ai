<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-speech-data-processor · page 9 Advanced Features · fetched 2026-10-26 -->

# Advanced Features

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [sdp/processors/inference/asr/nemo/utils/frame_vad_infer_postprocess.yaml](sdp/processors/inference/asr/nemo/utils/frame_vad_infer_postprocess.yaml)
- [sdp/processors/inference/asr/nemo/utils/speech_to_text_with_vad.py](sdp/processors/inference/asr/nemo/utils/speech_to_text_with_vad.py)
- [sdp/processors/inference/asr/nemo/utils/transcribe_speech.py](sdp/processors/inference/asr/nemo/utils/transcribe_speech.py)
- [sdp/processors/manage_files/convert_to_tarred_audio_dataset.py](sdp/processors/manage_files/convert_to_tarred_audio_dataset.py)
- [sdp/processors/manage_files/utils/convert_to_tarred_audio_dataset.py](sdp/processors/manage_files/utils/convert_to_tarred_audio_dataset.py)
- [sdp/processors/manage_files/utils/create_dali_tarred_dataset_index.py](sdp/processors/manage_files/utils/create_dali_tarred_dataset_index.py)

</details>



## Purpose and Scope

This page covers advanced features of the NeMo Speech Data Processor (SDP) that extend beyond basic dataset processing workflows. These features include sophisticated audio-text processing pipelines, optimized dataset packaging for large-scale training, and integration with external high-performance tools.

For basic processor usage and pipeline configuration, see [Core Architecture](#2). For standard dataset processing workflows, see [Data Processing and Transformation](#5).

## Advanced ASR and VAD Integration

The SDP system provides sophisticated inference pipelines that combine Automatic Speech Recognition (ASR) with Voice Activity Detection (VAD) for robust audio processing workflows.

### Combined ASR+VAD Pipeline Architecture

```mermaid
graph TB
    subgraph "Input Processing"
        MANIFEST["Input Manifest<br/>audio_filepath, duration, text"]
        AUDIO_DIR["Audio Directory<br/>*.wav files"]
    end
    
    subgraph "Feature Extraction"
        FEAT_EXTRACT["extract_audio_features()<br/>Preprocessor"]
        FEAT_STORE["Feature Storage<br/>*.pt files"]
    end
    
    subgraph "VAD Processing"
        VAD_MODEL["VAD Model<br/>vad_multilingual_frame_marblenet"]
        FRAME_PRED["generate_vad_frame_pred()<br/>Frame-level predictions"]
        OVERLAP_SMOOTH["generate_overlap_vad_seq()<br/>Overlap smoothing"]
        SEGMENT_TABLE["generate_vad_segment_table()<br/>RTTM generation"]
    end
    
    subgraph "ASR Processing"
        ASR_MODEL["ASR Model<br/>stt_en_conformer_ctc_large"]
        DECODE["Decoding Strategy<br/>CTC/RNNT/MultiTask"]
        ASR_INFER["run_asr_inference()<br/>Transcription"]
    end
    
    subgraph "Output"
        PRED_MANIFEST["Prediction Manifest<br/>pred_text, feature_file, rttm_file"]
        METRICS["Performance Metrics<br/>WER, CER, RTFx"]
    end
    
    MANIFEST --> FEAT_EXTRACT
    AUDIO_DIR --> FEAT_EXTRACT
    FEAT_EXTRACT --> FEAT_STORE
    FEAT_STORE --> VAD_MODEL
    VAD_MODEL --> FRAME_PRED
    FRAME_PRED --> OVERLAP_SMOOTH
    OVERLAP_SMOOTH --> SEGMENT_TABLE
    SEGMENT_TABLE --> ASR_MODEL
    FEAT_STORE --> ASR_MODEL
    ASR_MODEL --> DECODE
    DECODE --> ASR_INFER
    ASR_INFER --> PRED_MANIFEST
    ASR_INFER --> METRICS
```

**VAD+ASR Pipeline Integration**

Sources: [sdp/processors/inference/asr/nemo/utils/speech_to_text_with_vad.py:1-648]()

The system supports three operational modes through the `speech_to_text_with_vad.py` script:

| Mode | VAD Model | ASR Model | Use Case |
|------|-----------|-----------|----------|
| ASR Only | `None` | Specified | Pure transcription without VAD filtering |
| VAD Only | Specified | `None` | Speech activity detection and segmentation |
| Combined | Specified | Specified | VAD-filtered transcription with RTTM masking |

### Frame-Level VAD Processing

The system implements sophisticated frame-level VAD with configurable post-processing parameters:

```mermaid
graph LR
    subgraph "VAD Configuration"
        VAD_YAML["frame_vad_infer_postprocess.yaml<br/>onset: 0.3, offset: 0.3<br/>pad_onset: 0.2, pad_offset: 0.2"]
    end
    
    subgraph "Frame Processing"
        AUDIO_IN["Audio Input<br/>16kHz sampling"]
        FRAME_VAD["Frame VAD Model<br/>shift_length_in_sec: 0.02"]
        FRAME_PRED["Frame Predictions<br/>*.frame files"]
    end
    
    subgraph "Post-Processing"
        SMOOTHING["Overlap Smoothing<br/>median/mean filtering"]
        THRESHOLD["Threshold Application<br/>onset/offset thresholds"]
        PADDING["Segment Padding<br/>pad_onset/pad_offset"]
        MIN_DURATION["Duration Filtering<br/>min_duration_on/off"]
    end
    
    subgraph "Output"
        RTTM["RTTM Files<br/>Speaker segments"]
        SEGMENTS["Speech Segments<br/>start/end times"]
    end
    
    VAD_YAML --> FRAME_VAD
    AUDIO_IN --> FRAME_VAD
    FRAME_VAD --> FRAME_PRED
    FRAME_PRED --> SMOOTHING
    SMOOTHING --> THRESHOLD
    THRESHOLD --> PADDING
    PADDING --> MIN_DURATION
    MIN_DURATION --> RTTM
    MIN_DURATION --> SEGMENTS
```

**VAD Post-Processing Parameters**

Sources: [sdp/processors/inference/asr/nemo/utils/frame_vad_infer_postprocess.yaml:22-29]()

### Advanced Transcription Features

The `transcribe_speech.py` script provides comprehensive transcription capabilities with extensive configuration options:

```mermaid
graph TB
    subgraph "Model Support"
        CTC["EncDecCTCModel<br/>CTC Decoding"]
        RNNT["EncDecRNNTModel<br/>RNNT Decoding"]
        HYBRID["EncDecHybridRNNTCTCModel<br/>Dual Decoding"]
        AED["AED Models<br/>MultiTask Decoding"]
    end
    
    subgraph "Advanced Features"
        TIMESTAMPS["Timestamp Extraction<br/>word/char/segment level"]
        LANG_ID["Language Detection<br/>compute_langs=True"]
        NBEST["N-Best Hypotheses<br/>extract_nbest=True"]
        PROMPTS["Multi-Task Prompts<br/>Canary-1B support"]
    end
    
    subgraph "Performance Measurement"
        RTFX["Real-Time Factor<br/>calculate_rtfx=True"]
        WARMUP["Warmup Steps<br/>warmup_steps"]
        BATCH_TIME["Batch Timing<br/>SimpleTimer"]
    end
    
    subgraph "Output Options"
        WER_CALC["WER/CER Calculation<br/>calculate_wer=True"]
        MANIFEST_OUT["Manifest Output<br/>JSON lines format"]
        HYPO_OUT["Hypotheses Output<br/>return_hypotheses=True"]
    end
    
    CTC --> TIMESTAMPS
    RNNT --> TIMESTAMPS
    HYBRID --> TIMESTAMPS
    AED --> PROMPTS
    
    TIMESTAMPS --> RTFX
    LANG_ID --> RTFX
    NBEST --> RTFX
    PROMPTS --> RTFX
    
    RTFX --> WER_CALC
    BATCH_TIME --> WER_CALC
    WER_CALC --> MANIFEST_OUT
    WER_CALC --> HYPO_OUT
```

**Advanced Transcription Configuration**

Sources: [sdp/processors/inference/asr/nemo/utils/transcribe_speech.py:118-215]()

Key advanced features include:

- **Multi-Model Support**: CTC, RNNT, Hybrid RNNT/CTC, and AED models through the `TranscriptionConfig` dataclass
- **Timestamp Extraction**: Configurable timestamp types (`all`, `char`, `word`, `segment`) via `ctc_timestamp_type` and `rnnt_timestamp_type`
- **Language Detection**: Multi-lingual model support with `compute_langs` parameter
- **Performance Profiling**: Real-time factor (RTFx) calculation with warmup and timing measurements

## Tarred Audio Dataset Conversion

The SDP system provides sophisticated dataset packaging capabilities for large-scale training through the tarred audio dataset conversion pipeline.

### Tarred Dataset Architecture

```mermaid
graph TB
    subgraph "Input Processing"
        MANIFEST["Input Manifest<br/>audio_filepath, duration, text"]
        CONFIG["ASRTarredDatasetConfig<br/>num_shards, shuffle, bucketing"]
    end
    
    subgraph "Processing Pipeline"
        FILTER["Duration Filtering<br/>min_duration, max_duration"]
        SHUFFLE["Optional Shuffling<br/>shuffle_seed"]
        BUCKET["Optional Bucketing<br/>buckets_num, duration bins"]
        SHARD["Shard Distribution<br/>entries per shard calculation"]
    end
    
    subgraph "Parallel Tar Creation"
        WORKER1["Worker 1<br/>_create_shard()"]
        WORKER2["Worker 2<br/>_create_shard()"]
        WORKERN["Worker N<br/>_create_shard()"]
        TAR_WRITE["Audio File Writing<br/>_write_to_tar()"]
    end
    
    subgraph "Output Generation"
        TAR_FILES["Tar Archives<br/>audio_0.tar, audio_1.tar, ..."]
        MAIN_MANIFEST["Main Manifest<br/>tarred_audio_manifest.json"]
        SHARD_MANIFESTS["Shard Manifests<br/>manifest_0.json, manifest_1.json"]
        METADATA["Metadata<br/>metadata.yaml"]
        DALI_INDEX["DALI Index<br/>*.index files"]
    end
    
    MANIFEST --> FILTER
    CONFIG --> FILTER
    FILTER --> SHUFFLE
    SHUFFLE --> BUCKET
    BUCKET --> SHARD
    
    SHARD --> WORKER1
    SHARD --> WORKER2
    SHARD --> WORKERN
    
    WORKER1 --> TAR_WRITE
    WORKER2 --> TAR_WRITE
    WORKERN --> TAR_WRITE
    
    TAR_WRITE --> TAR_FILES
    TAR_WRITE --> MAIN_MANIFEST
    TAR_WRITE --> SHARD_MANIFESTS
    TAR_WRITE --> METADATA
    TAR_FILES --> DALI_INDEX
```

**Tarred Dataset Creation Pipeline**

Sources: [sdp/processors/manage_files/utils/convert_to_tarred_audio_dataset.py:159-890](), [sdp/processors/manage_files/convert_to_tarred_audio_dataset.py:73-162]()

### Advanced Dataset Features

The `ASRTarredDatasetBuilder` class provides sophisticated dataset management capabilities:

| Feature | Description | Configuration |
|---------|-------------|---------------|
| **Duration Bucketing** | Split datasets by duration ranges | `buckets_num`, `bucket_duration_bins` |
| **Dynamic Bucketing** | Automatic bucket estimation | `dynamic_buckets_num=30` |
| **Audio Transcoding** | On-the-fly codec conversion | `force_codec='flac'` |
| **Offset Slicing** | Extract audio segments | `slice_with_offset=True` |
| **File Grouping** | Keep file segments together | `keep_files_together=True` |
| **Parallel Processing** | Multi-worker tar creation | `workers=-1` |

### DALI Integration

The system provides GPU-accelerated data loading through NVIDIA DALI integration:

```mermaid
graph LR
    subgraph "Tar Dataset"
        TAR_FILES["Tar Archives<br/>audio_*.tar"]
        MANIFEST["Tarred Manifest<br/>tarred_audio_manifest.json"]
    end
    
    subgraph "DALI Index Creation"
        INDEX_CREATOR["IndexCreator<br/>wds2idx library"]
        PARALLEL_BUILD["Parallel Index Building<br/>build_index()"]
        INDEX_FILES["Index Files<br/>*.index in dali_index/"]
    end
    
    subgraph "Training Integration"
        WEBDATASET["WebDataset<br/>Efficient streaming"]
        GPU_LOADING["GPU Data Loading<br/>DALI pipeline"]
        BATCH_PREP["Batch Preparation<br/>Minimized CPU overhead"]
    end
    
    TAR_FILES --> INDEX_CREATOR
    MANIFEST --> INDEX_CREATOR
    INDEX_CREATOR --> PARALLEL_BUILD
    PARALLEL_BUILD --> INDEX_FILES
    
    INDEX_FILES --> WEBDATASET
    TAR_FILES --> WEBDATASET
    WEBDATASET --> GPU_LOADING
    GPU_LOADING --> BATCH_PREP
```

**DALI Index Generation**

Sources: [sdp/processors/manage_files/utils/create_dali_tarred_dataset_index.py:68-91]()

The DALI integration requires the `wds2idx` library and creates index files that enable:

- **Random Access**: Direct access to samples within tar archives
- **GPU Acceleration**: Elimination of CPU bottlenecks during data loading
- **Memory Efficiency**: Streaming data access without full dataset loading

### Metadata and Versioning

The system maintains comprehensive metadata through the `ASRTarredDatasetMetadata` class:

```mermaid
graph TB
    subgraph "Metadata Structure"
        BASE_META["ASRTarredDatasetMetadata<br/>version, created_datetime"]
        DATASET_CONFIG["ASRTarredDatasetConfig<br/>processing parameters"]
        HISTORY["History<br/>previous versions"]
    end
    
    subgraph "Versioning Workflow"
        INITIAL["Initial Dataset<br/>metadata.yaml"]
        CONCAT1["Concatenated v1<br/>metadata_version_1.yaml"]
        CONCAT2["Concatenated v2<br/>metadata_version_2.yaml"]
    end
    
    subgraph "Configuration Tracking"
        NUM_SHARDS["num_shards<br/>shard count"]
        SAMPLES_PER_SHARD["num_samples_per_shard<br/>distribution"]
        BUCKETING_PARAMS["Bucketing Parameters<br/>duration bins, bucket count"]
    end
    
    BASE_META --> DATASET_CONFIG
    BASE_META --> HISTORY
    
    INITIAL --> CONCAT1
    CONCAT1 --> CONCAT2
    
    DATASET_CONFIG --> NUM_SHARDS
    DATASET_CONFIG --> SAMPLES_PER_SHARD
    DATASET_CONFIG --> BUCKETING_PARAMS
```

**Dataset Metadata Management**

Sources: [sdp/processors/manage_files/utils/convert_to_tarred_audio_dataset.py:132-157](), [sdp/processors/manage_files/utils/convert_to_tarred_audio_dataset.py:377-570]()

## Performance Optimization Features

### Audio Processing Optimization

The tarred dataset system includes several performance optimizations:

- **Codec Selection**: Automatic format detection with optional transcoding via `force_codec`
- **Parallel Tar Creation**: Multi-worker processing using joblib's `Parallel` backend
- **Memory Management**: Streaming audio processing to minimize memory footprint
- **Shard Sorting**: Duration-based sorting within shards to reduce training padding

### Inference Performance Measurement

The ASR/VAD pipeline provides comprehensive performance profiling:

```mermaid
graph LR
    subgraph "Performance Metrics"
        RTFX["Real-Time Factor<br/>audio_duration / processing_time"]
        WARMUP["Warmup Measurement<br/>GPU initialization overhead"]
        BATCH_TIMING["Batch Processing Time<br/>per-iteration measurement"]
        MEMORY_PROF["Memory Profiling<br/>CUDA memory tracking"]
    end
    
    subgraph "Profiling Tools"
        PYTORCH_PROF["PyTorch Profiler<br/>CPU/GPU activity tracking"]
        SIMPLE_TIMER["SimpleTimer<br/>high-precision timing"]
        TORCH_PROF["torch.profiler<br/>detailed performance analysis"]
    end
    
    RTFX --> PYTORCH_PROF
    WARMUP --> SIMPLE_TIMER
    BATCH_TIMING --> SIMPLE_TIMER
    MEMORY_PROF --> TORCH_PROF
```

**Performance Profiling Integration**

Sources: [sdp/processors/inference/asr/nemo/utils/speech_to_text_with_vad.py:149-188](), [sdp/processors/inference/asr/nemo/utils/transcribe_speech.py:386-501]()

The performance measurement features enable:

- **RTFx Calculation**: Real-time factor measurement for production deployment planning
- **Memory Profiling**: CUDA memory usage tracking for optimization
- **Detailed Timing**: Per-component timing analysis for bottleneck identification