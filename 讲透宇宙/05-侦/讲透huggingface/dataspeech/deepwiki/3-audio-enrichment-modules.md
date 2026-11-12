<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/dataspeech · page 3 Audio Enrichment Modules · fetched 2026-10-26 -->

# Audio Enrichment Modules

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dataspeech/__init__.py](dataspeech/__init__.py)
- [dataspeech/cpu_enrichments/rate.py](dataspeech/cpu_enrichments/rate.py)
- [dataspeech/gpu_enrichments/__init__.py](dataspeech/gpu_enrichments/__init__.py)

</details>



## Purpose and Scope

The Audio Enrichment Modules form the core feature extraction layer of the DataSpeech pipeline. These modules extract specific acoustic and linguistic characteristics from audio datasets, transforming raw audio into quantifiable metrics such as pitch variation, signal-to-noise ratio, speaking rate, and speech quality measures.

This page provides an architectural overview of the modular enrichment system. For detailed implementation of GPU-accelerated processing, see [GPU-Accelerated Processing](#3.1). For CPU-based processing details, see [CPU-Based Processing](#3.2). The integration of these modules into the main processing pipeline is covered in [Feature Extraction (main.py)](#2.1).

## Architecture Overview

The enrichment system follows a modular architecture where each module is responsible for extracting specific audio characteristics. The system automatically distributes processing across available hardware resources.

**Module Distribution Architecture**
```mermaid
graph TB
    subgraph "dataspeech Package Structure"
        MAIN_INIT["dataspeech/__init__.py"]
        
        subgraph "CPU Enrichments"
            CPU_INIT["cpu_enrichments/__init__.py"]
            RATE_MODULE["rate.py"]
        end
        
        subgraph "GPU Enrichments"
            GPU_INIT["gpu_enrichments/__init__.py"]
            PITCH_MODULE["pitch.py"]
            SNR_MODULE["snr_and_reverb.py"]
            SQUIM_MODULE["squim.py"]
        end
    end
    
    subgraph "Exported Functions"
        RATE_APPLY["rate_apply()"]
        PITCH_APPLY["pitch_apply()"]
        SNR_APPLY["snr_apply()"]
        SQUIM_APPLY["squim_apply()"]
    end
    
    MAIN_INIT --> RATE_APPLY
    MAIN_INIT --> PITCH_APPLY
    MAIN_INIT --> SNR_APPLY
    MAIN_INIT --> SQUIM_APPLY
    
    CPU_INIT --> RATE_APPLY
    GPU_INIT --> PITCH_APPLY
    GPU_INIT --> SNR_APPLY
    GPU_INIT --> SQUIM_APPLY
    
    RATE_MODULE --> RATE_APPLY
    PITCH_MODULE --> PITCH_APPLY
    SNR_MODULE --> SNR_APPLY
    SQUIM_MODULE --> SQUIM_APPLY
```

Sources: [dataspeech/__init__.py:1-2](), [dataspeech/gpu_enrichments/__init__.py:1-3]()

## Module Organization

The enrichment modules are organized into two categories based on their computational requirements and hardware optimization:

| Module Type | Location | Functions | Hardware Requirement |
|-------------|----------|-----------|---------------------|
| **CPU Enrichments** | `dataspeech/cpu_enrichments/` | `rate_apply` | CPU-optimized |
| **GPU Enrichments** | `dataspeech/gpu_enrichments/` | `pitch_apply`, `snr_apply`, `squim_apply` | GPU-accelerated |

### Module Interface Pattern

All enrichment modules follow a consistent interface pattern:

```python
def module_apply(batch, rank=None, audio_column_name="audio", text_column_name="text", **kwargs):
    # Process batch data
    # Return modified batch with new columns
    return batch
```

This standardized interface allows for seamless integration with the main processing pipeline and enables batch processing across different hardware configurations.

Sources: [dataspeech/cpu_enrichments/rate.py:5]()

## Integration with Main Pipeline

**Enrichment Module Processing Flow**
```mermaid
flowchart TD
    INPUT_BATCH["Input Audio Batch"]
    MAIN_ORCHESTRATOR["main.py Orchestrator"]
    
    subgraph "Hardware Detection"
        GPU_CHECK{"GPU Available?"}
        CPU_FALLBACK["CPU Processing"]
        GPU_PROCESSING["GPU Processing"]
    end
    
    subgraph "CPU Enrichments"
        RATE_APPLY_FUNC["rate_apply()"]
        G2P_TRANSDUCER["g2p transducer"]
        PHONEME_CALC["Phoneme Calculation"]
        SPEAKING_RATE_CALC["Speaking Rate Calculation"]
    end
    
    subgraph "GPU Enrichments"
        PITCH_APPLY_FUNC["pitch_apply()"]
        SNR_APPLY_FUNC["snr_apply()"]
        SQUIM_APPLY_FUNC["squim_apply()"]
        PENN_MODEL["Penn Pitch Model"]
        BROUHAHA_MODEL["Brouhaha SNR Model"]
        TORCHAUIDO_SQUIM["TorchAudio SQUIM"]
    end
    
    subgraph "Output Processing"
        COLUMN_MERGE["Column Merging"]
        ENRICHED_DATASET["Enriched Dataset"]
    end
    
    INPUT_BATCH --> MAIN_ORCHESTRATOR
    MAIN_ORCHESTRATOR --> GPU_CHECK
    
    GPU_CHECK -->|"No"| CPU_FALLBACK
    GPU_CHECK -->|"Yes"| GPU_PROCESSING
    
    CPU_FALLBACK --> RATE_APPLY_FUNC
    GPU_PROCESSING --> PITCH_APPLY_FUNC
    GPU_PROCESSING --> SNR_APPLY_FUNC
    GPU_PROCESSING --> SQUIM_APPLY_FUNC
    
    RATE_APPLY_FUNC --> G2P_TRANSDUCER
    G2P_TRANSDUCER --> PHONEME_CALC
    PHONEME_CALC --> SPEAKING_RATE_CALC
    
    PITCH_APPLY_FUNC --> PENN_MODEL
    SNR_APPLY_FUNC --> BROUHAHA_MODEL
    SQUIM_APPLY_FUNC --> TORCHAUIDO_SQUIM
    
    SPEAKING_RATE_CALC --> COLUMN_MERGE
    PENN_MODEL --> COLUMN_MERGE
    BROUHAHA_MODEL --> COLUMN_MERGE
    TORCHAUIDO_SQUIM --> COLUMN_MERGE
    
    COLUMN_MERGE --> ENRICHED_DATASET
```

Sources: [dataspeech/cpu_enrichments/rate.py:1-44](), [dataspeech/gpu_enrichments/__init__.py:1-3]()

## Available Enrichment Modules

### CPU-Based Modules

| Module | Function | Output Columns | Description |
|--------|----------|---------------|-------------|
| **Rate Analysis** | `rate_apply` | `speaking_rate`, `phonemes` | Calculates speaking rate and extracts phonemes using G2P conversion |

### GPU-Based Modules

| Module | Function | Output Columns | Description |
|--------|----------|---------------|-------------|
| **Pitch Analysis** | `pitch_apply` | `utterance_pitch_mean`, `utterance_pitch_std` | Extracts pitch statistics using Penn model |
| **SNR & Reverberation** | `snr_apply` | `snr`, `c50` | Measures signal-to-noise ratio and reverberation using Brouhaha |
| **Speech Quality** | `squim_apply` | `pesq`, `si_sdr` | Evaluates speech quality using TorchAudio SQUIM metrics |

## Rate Module Implementation Details

The `rate_apply` function demonstrates the typical enrichment module pattern:

**Rate Calculation Process**
```mermaid
flowchart TD
    TEXT_INPUT["Text Input"]
    BATCH_CHECK{"Batch Processing?"}
    
    subgraph "Single Item Processing"
        SINGLE_G2P["transducer(text)"]
        SINGLE_PHONEMES["Extract Phonemes"]
        SINGLE_DURATION["Calculate Duration"]
        SINGLE_RATE["speaking_rate = len(phonemes) / duration"]
    end
    
    subgraph "Batch Processing"
        BATCH_LOOP["For each text in batch"]
        BATCH_G2P["transducer(text)"]
        BATCH_PHONEMES["Extract Phonemes"]
        BATCH_DURATION{"speech_duration exists?"}
        BATCH_AUDIO_CALC["Calculate from audio array"]
        BATCH_RATE["speaking_rate = len(phonemes) / duration"]
    end
    
    subgraph "Output"
        RATE_COLUMN["batch['speaking_rate']"]
        PHONEMES_COLUMN["batch['phonemes']"]
    end
    
    TEXT_INPUT --> BATCH_CHECK
    BATCH_CHECK -->|"No"| SINGLE_G2P
    BATCH_CHECK -->|"Yes"| BATCH_LOOP
    
    SINGLE_G2P --> SINGLE_PHONEMES
    SINGLE_PHONEMES --> SINGLE_DURATION
    SINGLE_DURATION --> SINGLE_RATE
    
    BATCH_LOOP --> BATCH_G2P
    BATCH_G2P --> BATCH_PHONEMES
    BATCH_PHONEMES --> BATCH_DURATION
    BATCH_DURATION -->|"Yes"| BATCH_RATE
    BATCH_DURATION -->|"No"| BATCH_AUDIO_CALC
    BATCH_AUDIO_CALC --> BATCH_RATE
    
    SINGLE_RATE --> RATE_COLUMN
    BATCH_RATE --> RATE_COLUMN
    SINGLE_PHONEMES --> PHONEMES_COLUMN
    BATCH_PHONEMES --> PHONEMES_COLUMN
```

The module handles both single-item and batch processing, with flexible duration calculation that can use pre-computed `speech_duration` or calculate from raw audio arrays.

Sources: [dataspeech/cpu_enrichments/rate.py:5-44]()

## Resource Management

The enrichment system integrates with the main pipeline's resource management, supporting configurable parameters for optimal hardware utilization:

- `cpu_num_workers`: Controls CPU-based processing parallelism
- `num_workers_per_gpu`: Manages GPU worker allocation
- `batch_size`: Determines processing batch sizes
- Module-specific parameters (e.g., `penn_batch_size` for pitch processing)

The modular design allows for independent scaling of different enrichment types based on their computational requirements and available hardware resources.

---

