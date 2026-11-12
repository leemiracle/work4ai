<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/dataspeech · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [examples/tagging/run_main_1k.sh](examples/tagging/run_main_1k.sh)
- [requirements.txt](requirements.txt)

</details>



Data-Speech is a comprehensive suite of utility scripts designed for automated annotation and tagging of speech datasets. The system transforms raw audio datasets into richly annotated datasets with natural language descriptions of speech characteristics, enabling advanced conditioning for text-to-speech models and dataset filtering applications.

This document provides an architectural overview of the Data-Speech system and its core processing pipeline. For detailed information about specific components, see [Core Processing Pipeline](#2), [Audio Enrichment Modules](#3), and [Prompt Generation Systems](#4).

## Purpose and Architecture

Data-Speech implements a three-stage pipeline that converts raw audio datasets into annotated datasets with natural language descriptions:

1. **Feature Extraction**: Extract continuous audio characteristics (pitch, SNR, speaking rate, quality metrics)
2. **Text Binning**: Map continuous variables to discrete categorical text bins using statistical distributions
3. **Natural Language Generation**: Convert text bins into coherent natural language descriptions using LLMs

## System Architecture Overview

```mermaid
graph TB
    subgraph "Input_Data" ["Input Data Sources"]
        HF_DS["HuggingFace Hub Datasets<br/>LibriTTS-R, MLS, Jenny TTS"]
        LOCAL_DS["Local Audio Datasets<br/>CSV + Audio Files"]
    end
    
    subgraph "Stage_1" ["Stage 1: Feature Extraction"]
        MAIN_PY["main.py<br/>Orchestrator"]
        
        subgraph "Enrichment_Modules" ["Enrichment Modules"]
            PITCH_MOD["pitch_apply<br/>Penn Model"]
            SNR_MOD["snr_apply<br/>Brouhaha Model"] 
            SQUIM_MOD["squim_apply<br/>TorchAudio SQUIM"]
            RATE_MOD["rate_apply<br/>G2P + Phoneme Analysis"]
        end
    end
    
    subgraph "Stage_2" ["Stage 2: Text Binning"]
        META_SCRIPT["scripts/metadata_to_text.py"]
        BIN_CONFIG["examples/tags_to_annotations/<br/>v02_bin_edges.json<br/>v02_text_bins.json"]
    end
    
    subgraph "Stage_3" ["Stage 3: Natural Language Generation"]
        ACCEL_SCRIPT["scripts/run_prompt_creation.py<br/>Accelerate Backend"]
        SWARM_SCRIPT["scripts/run_prompt_creation_llm_swarm.py<br/>LLM Swarm Backend"]
    end
    
    subgraph "Output_Data" ["Output Datasets"]
        TAGGED_DS["Tagged Datasets<br/>with Text Bins"]
        DESC_DS["Description Datasets<br/>with Natural Language"]
    end
    
    HF_DS --> MAIN_PY
    LOCAL_DS --> MAIN_PY
    
    MAIN_PY --> PITCH_MOD
    MAIN_PY --> SNR_MOD
    MAIN_PY --> SQUIM_MOD
    MAIN_PY --> RATE_MOD
    
    PITCH_MOD --> META_SCRIPT
    SNR_MOD --> META_SCRIPT
    SQUIM_MOD --> META_SCRIPT
    RATE_MOD --> META_SCRIPT
    
    BIN_CONFIG --> META_SCRIPT
    META_SCRIPT --> TAGGED_DS
    
    TAGGED_DS --> ACCEL_SCRIPT
    TAGGED_DS --> SWARM_SCRIPT
    
    ACCEL_SCRIPT --> DESC_DS
    SWARM_SCRIPT --> DESC_DS
```

**Sources:** [README.md:1-50](), [README.md:144-152](), [README.md:233-240]()

## Core Pipeline Components

The system consists of modular components that can be executed independently or as part of the complete pipeline:

```mermaid
graph LR
    subgraph "Continuous_Variables" ["Continuous Variables"]
        PITCH_VARS["utterance_pitch_std<br/>utterance_pitch_mean"]
        QUALITY_VARS["snr, c50<br/>pesq, si-sdr"]
        RATE_VARS["speaking_rate<br/>phonemes<br/>speech_duration"]
    end
    
    subgraph "Text_Bins" ["Categorical Text Bins"]
        PITCH_BINS["very high-pitched<br/>quite high-pitched<br/>moderate pitch<br/>quite low-pitched<br/>very low-pitched"]
        QUALITY_BINS["very clear<br/>quite clear<br/>slightly clear<br/>moderate<br/>slightly noisy<br/>quite noisy<br/>very noisy"]
        RATE_BINS["very slowly<br/>quite slowly<br/>slightly slowly<br/>moderate speed<br/>slightly fast<br/>quite fast<br/>very fast"]
    end
    
    subgraph "Natural_Language" ["Natural Language Descriptions"]
        SAMPLE_DESC["In a very expressive voice, Jenny<br/>speaks quite slowly with some<br/>background noise and echo."]
    end
    
    PITCH_VARS --> PITCH_BINS
    QUALITY_VARS --> QUALITY_BINS  
    RATE_VARS --> RATE_BINS
    
    PITCH_BINS --> SAMPLE_DESC
    QUALITY_BINS --> SAMPLE_DESC
    RATE_BINS --> SAMPLE_DESC
```

**Sources:** [README.md:183-192](), [README.md:198-202](), [README.md:103-104]()

## Key Features and Capabilities

| Feature Category | Components | Description |
|------------------|------------|-------------|
| **Audio Analysis** | `pitch_apply`, `snr_apply`, `squim_apply`, `rate_apply` | Extract pitch statistics, SNR, reverberation, quality metrics, speaking rate |
| **Statistical Binning** | `scripts/metadata_to_text.py` | Map continuous variables to discrete bins using histogram analysis |
| **LLM Integration** | `scripts/run_prompt_creation.py`, `scripts/run_prompt_creation_llm_swarm.py` | Generate natural language descriptions using Accelerate or TGI backends |
| **GPU Acceleration** | Multi-GPU support in `main.py` | Automatically scale processing across available GPUs |
| **Hub Integration** | Dataset upload/download via `datasets` library | Seamless integration with HuggingFace Hub |
| **Configuration Management** | JSON configuration files | Reproducible binning with pre-computed statistical thresholds |

**Sources:** [README.md:54-59](), [README.md:156-170](), [README.md:233-302]()

## Data Flow and Processing Model

```mermaid
flowchart TD
    RAW_AUDIO["Raw Audio Dataset<br/>Audio files + Text transcripts"]
    
    CONTINUOUS["Dataset with Continuous Variables<br/>speaking_rate: 3.2 phonemes/sec<br/>utterance_pitch_mean: 180.5 Hz<br/>snr: 15.3 dB<br/>c50: 42.1 dB"]
    
    BINNED["Dataset with Text Bins<br/>speaking_rate_text: 'slightly slowly'<br/>pitch_text: 'moderate pitch'<br/>snr_text: 'quite clear'<br/>c50_text: 'quite reverberant'"]
    
    NATURAL_DESC["Dataset with Natural Language<br/>description: 'In a moderate pitch voice,<br/>the speaker talks slightly slowly<br/>with quite clear audio quality<br/>and some reverberation.'"]
    
    RAW_AUDIO -->|"main.py"| CONTINUOUS
    CONTINUOUS -->|"scripts/metadata_to_text.py"| BINNED  
    BINNED -->|"scripts/run_prompt_creation.py"| NATURAL_DESC
```

**Sources:** [README.md:47-50](), [README.md:196-202](), [README.md:228-232]()

The Data-Speech system is designed for scalability and modularity, supporting both small-scale experimentation and large-scale dataset processing. Each stage can be run independently, enabling flexible workflows for different use cases ranging from dataset filtering to comprehensive annotation for TTS model training.

---

