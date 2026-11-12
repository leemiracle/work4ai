<!-- source: DeepWiki mcp.deepwiki.com · repo Lightning-AI/torchmetrics · page 7 Audio Metrics · fetched 2026-10-21 -->

# Audio Metrics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [docs/source/links.rst](docs/source/links.rst)
- [requirements/audio_test.txt](requirements/audio_test.txt)
- [src/torchmetrics/__init__.py](src/torchmetrics/__init__.py)
- [src/torchmetrics/classification/__init__.py](src/torchmetrics/classification/__init__.py)
- [src/torchmetrics/functional/__init__.py](src/torchmetrics/functional/__init__.py)
- [src/torchmetrics/functional/classification/__init__.py](src/torchmetrics/functional/classification/__init__.py)
- [src/torchmetrics/functional/pairwise/__init__.py](src/torchmetrics/functional/pairwise/__init__.py)
- [src/torchmetrics/functional/regression/__init__.py](src/torchmetrics/functional/regression/__init__.py)
- [src/torchmetrics/regression/__init__.py](src/torchmetrics/regression/__init__.py)

</details>



This document covers the audio quality assessment metrics available in TorchMetrics, which provide evaluation tools for speech and audio processing tasks. These metrics assess various aspects of audio quality including intelligibility, distortion, noise suppression effectiveness, and perceptual quality.

For image quality metrics, see [Image Metrics](#5). For text similarity metrics, see [Text Metrics](#6).

## Overview

TorchMetrics provides a comprehensive suite of audio quality assessment metrics designed for evaluating speech enhancement, noise suppression, source separation, and general audio processing algorithms. The audio metrics domain includes both reference-based metrics (requiring clean target audio) and no-reference metrics (requiring only the processed audio).

```mermaid
graph TB
    subgraph "Audio Metrics Domain"
        subgraph "Reference-Based Metrics"
            PESQ["perceptual_evaluation_speech_quality"]
            STOI["short_time_objective_intelligibility"] 
            SDR["signal_distortion_ratio"]
            SISDR["scale_invariant_signal_distortion_ratio"]
            SASDR["source_aggregated_signal_distortion_ratio"]
        end
        
        subgraph "No-Reference Metrics"
            DNSMOS["deep_noise_suppression_mean_opinion_score"]
            NISQA["non_intrusive_speech_quality_assessment"]
        end
        
        subgraph "Implementation Types"
            Functional["Functional API<br/>torchmetrics.functional.audio.*"]
            Module["Module API<br/>torchmetrics.audio.*"]
        end
    end
    
    PESQ --> Functional
    STOI --> Functional
    SDR --> Functional
    SISDR --> Functional
    SASDR --> Functional
    DNSMOS --> Functional
    DNSMOS --> Module
    NISQA --> Functional
    NISQA --> Module
    
    Functional --> Module
```

Sources: [src/torchmetrics/functional/audio/pesq.py](), [src/torchmetrics/functional/audio/stoi.py](), [src/torchmetrics/functional/audio/sdr.py](), [src/torchmetrics/functional/audio/dnsmos.py](), [src/torchmetrics/functional/audio/nisqa.py](), [src/torchmetrics/audio/dnsmos.py](), [src/torchmetrics/audio/nisqa.py]()

## Architecture

The audio metrics follow the standard TorchMetrics dual API pattern with functional (stateless) and module (stateful) implementations. Unlike some domains where all metrics have both implementations, only certain audio metrics provide module classes due to their computational complexity and external dependencies.

```mermaid
graph LR
    subgraph "Functional Implementation"
        FPESQ["perceptual_evaluation_speech_quality"]
        FSTOI["short_time_objective_intelligibility"]
        FSDR["signal_distortion_ratio"]
        FDNSMOS["deep_noise_suppression_mean_opinion_score"]
        FNISQA["non_intrusive_speech_quality_assessment"]
    end
    
    subgraph "Module Implementation"
        MDNSMOS["DeepNoiseSuppressionMeanOpinionScore"]
        MNISQA["NonIntrusiveSpeechQualityAssessment"]
        BaseMetric["Metric"]
    end
    
    subgraph "External Dependencies"
        PESQ_PKG["pesq package"]
        PYSTOI_PKG["pystoi package"]
        FASTBSS_PKG["fast-bss-eval package"]
        LIBROSA_PKG["librosa package"]
        ONNX_PKG["onnxruntime package"]
        REQUESTS_PKG["requests package"]
    end
    
    FPESQ --> PESQ_PKG
    FSTOI --> PYSTOI_PKG
    FSDR --> FASTBSS_PKG
    FDNSMOS --> LIBROSA_PKG
    FDNSMOS --> ONNX_PKG
    FDNSMOS --> REQUESTS_PKG
    FNISQA --> LIBROSA_PKG
    FNISQA --> REQUESTS_PKG
    
    FDNSMOS --> MDNSMOS
    FNISQA --> MNISQA
    MDNSMOS --> BaseMetric
    MNISQA --> BaseMetric
```

Sources: [src/torchmetrics/functional/audio/](), [src/torchmetrics/audio/](), [requirements/audio_test.txt]()

## Signal Distortion Ratio (SDR) Metrics

The SDR family of metrics measures the quality of source separation and signal reconstruction by comparing predicted signals to reference targets.

### Core SDR Functions

The SDR implementation provides three main variants:

| Function | Purpose | Key Parameters |
|----------|---------|----------------|
| `signal_distortion_ratio` | Standard SDR computation with distortion filter | `use_cg_iter`, `filter_length`, `zero_mean` |
| `scale_invariant_signal_distortion_ratio` | Scale-invariant variant (SI-SDR) | `zero_mean` |
| `source_aggregated_signal_distortion_ratio` | Source-aggregated variant (SA-SDR) | `scale_invariant`, `zero_mean` |

```mermaid
graph TB
    subgraph "SDR Computation Pipeline"
        Input["preds, target<br/>(..., time)"]
        Normalize["Normalize signals<br/>norm(signal, dim=-1)"]
        AutoCorr["Compute autocorrelation<br/>_compute_autocorr_crosscorr"]
        FilterSolve["Solve filter coefficients<br/>torch.linalg.solve or CGD"]
        Coherence["Compute coherence<br/>torch.einsum"]
        ToDecibel["Convert to dB<br/>10 * log10(ratio)"]
        Output["SDR values<br/>(...,)"]
    end
    
    Input --> Normalize
    Normalize --> AutoCorr
    AutoCorr --> FilterSolve
    FilterSolve --> Coherence
    Coherence --> ToDecibel
    ToDecibel --> Output
    
    subgraph "Helper Functions"
        SymToeplitz["_symmetric_toeplitz<br/>Construct Toeplitz matrix"]
        FFTCorr["FFT-based correlation<br/>torch.fft.rfft/irfft"]
    end
    
    AutoCorr --> FFTCorr
    FilterSolve --> SymToeplitz
```

Sources: [src/torchmetrics/functional/audio/sdr.py:88-198](), [src/torchmetrics/functional/audio/sdr.py:200-239](), [src/torchmetrics/functional/audio/sdr.py:241-304]()

## PESQ (Perceptual Evaluation of Speech Quality)

PESQ provides industry-standard perceptual quality assessment for speech signals, returning scores between -0.5 and 4.5.

```mermaid
graph LR
    subgraph "PESQ Implementation"
        CheckInputs["_check_same_shape<br/>Validate inputs"]
        MoveToCPU["Move to CPU<br/>pesq backend requirement"]
        CallPESQ["pesq_backend.pesq<br/>External pesq package"]
        ProcessBatch["Handle batch processing<br/>multiprocessing support"]
        ReturnResult["Return tensor result<br/>keep_same_device option"]
    end
    
    CheckInputs --> MoveToCPU
    MoveToCPU --> CallPESQ
    CallPESQ --> ProcessBatch
    ProcessBatch --> ReturnResult
    
    subgraph "External Requirements"
        PESQPackage["pesq package<br/>_PESQ_AVAILABLE"]
        MultiProc["multiprocessing<br/>_MULTIPROCESSING_AVAILABLE"]
    end
    
    CallPESQ --> PESQPackage
    ProcessBatch --> MultiProc
```

Sources: [src/torchmetrics/functional/audio/pesq.py:26-121]()

## STOI (Short-Time Objective Intelligibility)

STOI measures speech intelligibility correlation, particularly useful for evaluating the impact of noise reduction and other processing on speech comprehension.

```mermaid
graph LR
    subgraph "STOI Implementation"
        ValidateShape["_check_same_shape<br/>Input validation"]
        MoveToCPU["Move to CPU<br/>pystoi backend requirement"]
        CallSTOI["stoi_backend<br/>pystoi.stoi function"]
        HandleBatch["Process batch dimension<br/>individual processing"]
        ReshapeOutput["Reshape to input shape<br/>preserve batch dimensions"]
    end
    
    ValidateShape --> MoveToCPU
    MoveToCPU --> CallSTOI
    CallSTOI --> HandleBatch
    HandleBatch --> ReshapeOutput
    
    subgraph "Parameters"
        Extended["extended: bool<br/>Use extended STOI"]
        KeepDevice["keep_same_device: bool<br/>Return to original device"]
    end
    
    CallSTOI --> Extended
    ReshapeOutput --> KeepDevice
```

Sources: [src/torchmetrics/functional/audio/stoi.py:25-96]()

## DNSMOS (Deep Noise Suppression Mean Opinion Score)

DNSMOS provides no-reference speech quality assessment using deep neural networks, particularly designed for evaluating noise suppression algorithms.

### DNSMOS Architecture

```mermaid
graph TB
    subgraph "DNSMOS Pipeline"
        AudioInput["Audio input<br/>(..., time)"]
        Resample["Resample to 16kHz<br/>librosa.resample"]
        Segment["Segment audio<br/>9.01s windows"]
        MelSpec["Mel spectrogram<br/>_audio_melspec"]
        ModelInference["ONNX model inference<br/>sig_bak_ovr.onnx + model_v8.onnx"]
        Polyfit["Polynomial fitting<br/>_polyfit_val"]
        Output["DNSMOS scores<br/>[p808_mos, mos_sig, mos_bak, mos_ovr]"]
    end
    
    AudioInput --> Resample
    Resample --> Segment
    Segment --> MelSpec
    MelSpec --> ModelInference
    ModelInference --> Polyfit
    Polyfit --> Output
    
    subgraph "Model Management"
        PrepareModels["_prepare_dnsmos<br/>Download ONNX models"]
        LoadSession["_load_session<br/>Create inference session"]
        CacheSession["_cached_load_session<br/>LRU cache for sessions"]
    end
    
    ModelInference --> LoadSession
    LoadSession --> PrepareModels
    LoadSession --> CacheSession
```

### DNSMOS Module Class

The `DeepNoiseSuppressionMeanOpinionScore` class provides stateful metric tracking:

```mermaid
graph LR
    subgraph "DNSMOS Module"
        Init["__init__<br/>fs, personalized, device"]
        AddState["add_state<br/>sum_dnsmos, total"]
        Update["update<br/>Accumulate batch scores"]
        Compute["compute<br/>Return averaged scores"]
        Plot["plot<br/>Visualization support"]
    end
    
    subgraph "State Management"
        SumDNSMOS["sum_dnsmos<br/>tensor([0,0,0,0])"]
        Total["total<br/>tensor(0)"]
    end
    
    Init --> AddState
    AddState --> SumDNSMOS
    AddState --> Total
    Update --> SumDNSMOS
    Update --> Total
    Compute --> SumDNSMOS
    Compute --> Total
```

Sources: [src/torchmetrics/functional/audio/dnsmos.py:184-292](), [src/torchmetrics/audio/dnsmos.py:36-187]()

## NISQA (Non-Intrusive Speech Quality Assessment)

NISQA provides multidimensional speech quality prediction using a deep CNN-self-attention model, outputting scores for overall MOS, noisiness, discontinuity, coloration, and loudness.

### NISQA Model Architecture

```mermaid
graph TB
    subgraph "NISQA Neural Network"
        MelSpec["Mel Spectrogram Input<br/>(..., n_mels, n_frames)"]
        Segment["Segment into windows<br/>_segment_specs"]
        CNN["CNN Feature Extraction<br/>_AdaptCNN"]
        SelfAttn["Self-Attention<br/>_SelfAttention"]
        Pooling["Attention Pooling<br/>_PoolAttFF x5"]
        Output["Quality Scores<br/>[mos, noi, dis, col, loud]"]
    end
    
    MelSpec --> Segment
    Segment --> CNN
    CNN --> SelfAttn
    SelfAttn --> Pooling
    Pooling --> Output
    
    subgraph "CNN Components"
        Conv["6 Conv2D layers<br/>BatchNorm + ReLU"]
        AdaptPool["Adaptive pooling<br/>adaptive_max_pool2d"]
        Dropout["Dropout2d<br/>Regularization"]
    end
    
    CNN --> Conv
    CNN --> AdaptPool
    CNN --> Dropout
    
    subgraph "Self-Attention Components"
        MultiHead["MultiheadAttention<br/>td_sa_nhead heads"]
        LayerNorm["LayerNorm<br/>Normalization"]
        FeedForward["Feed-forward<br/>Linear layers"]
    end
    
    SelfAttn --> MultiHead
    SelfAttn --> LayerNorm
    SelfAttn --> FeedForward
```

### NISQA Processing Pipeline

```mermaid
graph LR
    subgraph "NISQA Functional"
        AudioIn["Audio input<br/>(..., time)"]
        LoadModel["_load_nisqa_model<br/>Download and load"]
        LibrosaMel["_get_librosa_melspec<br/>Mel spectrogram"]
        SegmentSpec["_segment_specs<br/>Window segmentation"]
        ModelForward["Model inference<br/>_NISQADIM"]
        Reshape["Reshape output<br/>(..., 5)"]
    end
    
    AudioIn --> LoadModel
    LoadModel --> LibrosaMel
    LibrosaMel --> SegmentSpec
    SegmentSpec --> ModelForward
    ModelForward --> Reshape
    
    subgraph "Model Components"
        Framewise["_Framewise<br/>CNN processing"]
        TimeDep["_TimeDependency<br/>Self-attention"]
        PoolLayers["pool_layers<br/>5 pooling modules"]
    end
    
    ModelForward --> Framewise
    ModelForward --> TimeDep
    ModelForward --> PoolLayers
```

Sources: [src/torchmetrics/functional/audio/nisqa.py:66-121](), [src/torchmetrics/functional/audio/nisqa.py:155-398](), [src/torchmetrics/audio/nisqa.py:35-156]()

## Dependencies and Installation

Audio metrics have specific external dependencies that must be installed separately:

| Metric | Required Packages | Installation Notes |
|--------|-------------------|-------------------|
| PESQ | `pesq` | Compiles with current numpy version |
| STOI | `pystoi` | CPU-only implementation |
| SDR | `fast-bss-eval` (optional), `torch_complex` | Conjugate gradient optimization |
| DNSMOS | `librosa`, `onnxruntime`, `requests` | Downloads ONNX models |
| NISQA | `librosa`, `requests` | Downloads PyTorch model weights |

```mermaid
graph LR
    subgraph "Installation Options"
        AudioExtra["pip install torchmetrics[audio]<br/>All audio dependencies"]
        Individual["pip install pesq pystoi librosa<br/>Individual packages"]
        GPU["pip install onnxruntime-gpu<br/>GPU acceleration for DNSMOS"]
    end
    
    subgraph "Import Checks"
        PESQCheck["_PESQ_AVAILABLE"]
        STOICheck["_PYSTOI_AVAILABLE"]
        LibrosaCheck["_LIBROSA_AVAILABLE"]
        ONNXCheck["_ONNXRUNTIME_AVAILABLE"]
        RequestsCheck["_REQUESTS_AVAILABLE"]
        FastBSSCheck["_FAST_BSS_EVAL_AVAILABLE"]
    end
    
    AudioExtra --> PESQCheck
    AudioExtra --> STOICheck
    AudioExtra --> LibrosaCheck
    Individual --> PESQCheck
    GPU --> ONNXCheck
```

Sources: [requirements/audio_test.txt](), [src/torchmetrics/functional/audio/pesq.py:21](), [src/torchmetrics/functional/audio/stoi.py:19](), [src/torchmetrics/functional/audio/dnsmos.py:23-31](), [src/torchmetrics/functional/audio/nisqa.py:53-59]()

## Usage Patterns

### Reference-Based Metrics Usage

```python
# PESQ, STOI, SDR require both predictions and targets
from torchmetrics.functional.audio import (
    perceptual_evaluation_speech_quality,
    short_time_objective_intelligibility,
    signal_distortion_ratio
)

# Example usage with 8kHz audio
pesq_score = perceptual_evaluation_speech_quality(preds, target, fs=8000, mode='nb')
stoi_score = short_time_objective_intelligibility(preds, target, fs=8000)
sdr_score = signal_distortion_ratio(preds, target)
```

### No-Reference Metrics Usage

```python
# DNSMOS and NISQA only require predictions
from torchmetrics.functional.audio import (
    deep_noise_suppression_mean_opinion_score,
    non_intrusive_speech_quality_assessment
)
from torchmetrics.audio import (
    DeepNoiseSuppressionMeanOpinionScore,
    NonIntrusiveSpeechQualityAssessment
)

# Functional usage
dnsmos_scores = deep_noise_suppression_mean_opinion_score(preds, fs=16000, personalized=False)
nisqa_scores = non_intrusive_speech_quality_assessment(preds, fs=16000)

# Module usage for accumulation across batches
dnsmos_metric = DeepNoiseSuppressionMeanOpinionScore(fs=16000, personalized=False)
dnsmos_metric.update(preds)
final_scores = dnsmos_metric.compute()
```

Sources: [src/torchmetrics/functional/audio/pesq.py:72-80](), [src/torchmetrics/functional/audio/dnsmos.py:227-233](), [src/torchmetrics/audio/dnsmos.py:83-88]()

---

