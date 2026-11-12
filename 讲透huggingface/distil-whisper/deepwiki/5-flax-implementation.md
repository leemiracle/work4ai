<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/distil-whisper · page 5 Flax Implementation · fetched 2026-10-26 -->

# Flax Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [training/flax/README.md](training/flax/README.md)
- [training/flax/create_student_model.py](training/flax/create_student_model.py)
- [training/flax/distil_whisper/modeling_flax_whisper.py](training/flax/distil_whisper/modeling_flax_whisper.py)
- [training/flax/distil_whisper/pipeline.py](training/flax/distil_whisper/pipeline.py)
- [training/flax/run_distillation.py](training/flax/run_distillation.py)
- [training/flax/run_pseudo_labelling_pt.py](training/flax/run_pseudo_labelling_pt.py)

</details>



This document provides technical details about the JAX/Flax implementation of Distil-Whisper, which enables efficient training and inference on TPU and GPU hardware. The Flax implementation is specifically designed for high-performance model training and deployment, leveraging JAX's just-in-time compilation, automatic differentiation, and device parallelism.

## Introduction to the Flax Backend

The Distil-Whisper project implements the model distillation pipeline in both PyTorch and JAX/Flax. This page focuses specifically on the Flax implementation, which offers several advantages for large-scale training:

```mermaid
flowchart LR
    subgraph "Distil-Whisper Project"
        direction TB
        PyTorch["PyTorch Implementation"]
        Flax["JAX/Flax Implementation"]
    end
    
    subgraph "JAX/Flax Advantages"
        direction TB
        TPU["TPU Optimization"]
        JIT["Just-in-Time Compilation"]
        SPMD["Single Program Multiple Data"]
        Scan["Scan for Layer Stacking"]
    end
    
    Flax --> TPU
    Flax --> JIT
    Flax --> SPMD
    Flax --> Scan
    
    PyTorch -.-> Multilingual["Supports Multilingual Training"]
    Flax -.-> EnglishOnly["Optimized for English ASR"]
```

The JAX/Flax implementation is primarily designed for English ASR, while the PyTorch implementation supports multilingual training. The JAX/Flax version has been optimized specifically for training on TPU v4 hardware, though it also works efficiently on GPUs without any code modifications.

Sources: [training/flax/README.md:1-18](training/flax/README.md:1-18)

## Architecture Overview

The Flax implementation consists of several key components that work together to implement the four-stage Distil-Whisper pipeline:

```mermaid
flowchart TD
    subgraph "Flax Implementation Components"
        direction TB
        FWM["FlaxWhisperModule"]
        FWFCG["FlaxWhisperForConditionalGeneration"]
        FWP["FlaxWhisperPipeline"]
        
        FWM --> FWFCG
        
        subgraph "Core Model Layers"
            FWE["FlaxWhisperEncoder"]
            FWD["FlaxWhisperDecoder"]
            FWA["FlaxWhisperAttention"]
            FWEL["FlaxWhisperEncoderLayer"]
            FWDL["FlaxWhisperDecoderLayer"]
        end
        
        FWM --> FWE
        FWM --> FWD
        FWE --> FWEL
        FWD --> FWDL
        FWEL --> FWA
        FWDL --> FWA
        
        FWFCG --> FWP
    end
    
    subgraph "Training Scripts"
        RunPseudoLabelling["run_pseudo_labelling.py"]
        CreateStudentModel["create_student_model.py"]
        RunDistillation["run_distillation.py"]
        RunEval["run_eval.py"]
    end
    
    FWFCG --> RunPseudoLabelling
    FWFCG --> CreateStudentModel
    FWFCG --> RunDistillation
    FWFCG --> RunEval
    FWP --> RunLongFormTranscription["run_long_form_transcription.py"]
```

The architecture follows a modular design where:

1. `FlaxWhisperModule` is the core model implementation with encoder and decoder components
2. `FlaxWhisperForConditionalGeneration` extends this module for generation tasks
3. `FlaxWhisperPipeline` provides an easy-to-use interface for audio transcription
4. Training scripts implement the four stages of the distillation process

Sources: [training/flax/distil_whisper/modeling_flax_whisper.py:107-1184](training/flax/distil_whisper/modeling_flax_whisper.py:107-1184)

## Optimizations in the Flax Implementation

The Flax implementation incorporates several JAX-specific optimizations to achieve high performance:

### Scan Optimization

One of the key optimizations is the `use_scan` parameter, which utilizes JAX's `scan_with_axes` for layer stacking:

```mermaid
flowchart LR
    subgraph "Traditional Approach"
        TL1["Layer 1"] --> TL2["Layer 2"] --> TL3["..."] --> TLN["Layer N"]
    end
    
    subgraph "Scan Approach"
        direction TB
        SLT["Stacked Layer Template"] --> Scan["scan_with_axes()"]
        Scan --> S1["Layer 1"]
        Scan --> S2["Layer 2"]
        Scan --> S3["..."]
        Scan --> SN["Layer N"]
    end
    
    Traditional["Traditional Loop\n(Separate Compilation)"] --> TL1
    Scan --> ScanAdvantages["Advantages:\n- Faster Compilation\n- Memory Efficient\n- Single Compiled Function"]
```

The `scan` optimization results in:
- Faster compile times: JAX only needs to compile the layer function once
- More efficient memory use during training
- Slower inference due to the overhead of stacking layers

The `use_scan` parameter is set to `True` by default for training and automatically disabled for inference.

Sources: [training/flax/README.md:380-389](training/flax/README.md:380-389), [training/flax/distil_whisper/modeling_flax_whisper.py:543-614](training/flax/distil_whisper/modeling_flax_whisper.py:543-614)

### Mixed Precision Training

The implementation supports different precision modes:

```mermaid
flowchart LR
    subgraph "Precision Modes"
        direction TB
        Full["Full precision\nfp32 all operations"]
        HalfMixed["Half mixed precision\nforward pass: bf16\nbackward pass: fp32\noptimizer: fp32"]
        FullMixed["Full mixed precision\nforward pass: bf16\nbackward & optimizer update: bf16\nintermediate calcs: fp32"]
    end
    
    PrecisionParam["precision parameter"] --> Full
    PrecisionParam --> HalfMixed
    PrecisionParam --> FullMixed
    
    DtypeParam["dtype parameter"] --> DataType["Controls computation dtype\nnot parameter storage"]
```

The precision mode can be configured through the `precision` parameter in the training arguments, while the `dtype` parameter controls the data type of the computation (not the model parameters).

Sources: [training/flax/run_distillation.py:422-441](training/flax/run_distillation.py:422-441)

## Four-Stage Pipeline Implementation

The Flax implementation follows the same four-stage pipeline as the PyTorch version:

```mermaid
flowchart LR
    subgraph "Flax Distil-Whisper Pipeline"
        direction LR
        PL["1. Pseudo-Labelling\nrun_pseudo_labelling.py"] --> 
        Init["2. Initialization\ncreate_student_model.py"] --> 
        Train["3. Training\nrun_distillation.py"] --> 
        Eval["4. Evaluation\nrun_eval.py"]
    end
    
    PL -->|"Creates pseudo-labels\nfrom teacher model"| PLOutput["Labeled Dataset"] 
    Init --> |"Initializes student model\nfrom teacher layers"| InitOutput["Student Model"]
    PLOutput --> Train
    InitOutput --> Train
    Train --> |"Knowledge Distillation"| TrainOutput["Trained Student Model"]
    TrainOutput --> Eval
    Eval --> |"WER Metrics"| EvalOutput["Evaluation Results"]
```

### 1. Pseudo-Labelling

The pseudo-labelling process generates target text predictions using the teacher model, which replace ground truth labels during distillation.

Key components in the Flax implementation:
- `run_pseudo_labelling.py`: Flexible inference script for generating pseudo-labels
- Supports streaming mode via HuggingFace Datasets
- Supports greedy decoding or beam-search
- Can generate timestamp information in audio data

Sources: [training/flax/README.md:33-78](training/flax/README.md:33-78), [training/flax/run_pseudo_labelling_pt.py:17-113](training/flax/run_pseudo_labelling_pt.py:17-113)

### 2. Student Model Initialization

The student model initialization process creates a smaller model from the teacher model:

```mermaid
flowchart LR
    subgraph "Student Initialization"
        direction TB
        TeacherModel["Teacher Model\n(e.g., whisper-large-v2)"] --> 
        LayerSelection["Layer Selection\n(maximize spacing)"] --> 
        StudentInit["Student Model\n(e.g., large-32-2)"]
    end
    
    TeacherConfig["Teacher Config\nencoder_layers: 32\ndecoder_layers: 32"] -->
    StudentConfig["Student Config\nencoder_layers: 32\ndecoder_layers: 2"]
    
    EncoderMap["Encoder Layer Mapping\nCopy all encoder layers or\nspaced selection"] --> StudentInit
    DecoderMap["Decoder Layer Mapping\nCopy maximally spaced layers\n(e.g., layers 1 and 32)"] --> StudentInit
```

The `create_student_model.py` script handles:
- Copying maximally spaced layers from the teacher model
- Supporting different encoder/decoder configurations
- Preserving the model weights in the layers that are kept
- Ensuring the processor and feature extractor are updated accordingly

Sources: [training/flax/README.md:80-102](training/flax/README.md:80-102), [training/flax/create_student_model.py:97-226](training/flax/create_student_model.py:97-226)

### 3. Distillation Training

The distillation training process uses the `run_distillation.py` script, which implements the knowledge distillation framework:

```mermaid
flowchart TD
    subgraph "Distillation Training Process"
        direction TB
        InputData["Input: Audio + Pseudo-labels"] --> 
        Filter["Filter by WER threshold"] --> 
        Training["Training Loop"]
        
        subgraph "Training Loop Components"
            direction TB
            StudentFwd["Student Forward Pass"] --> 
            TeacherFwd["Teacher Forward Pass"] --> 
            LossComp["Loss Computation"] --> 
            Optimize["Optimizer Update"]
        end
        
        subgraph "Loss Components"
            direction LR
            CE["Cross-Entropy Loss\nvs Ground Truth"]
            KL["KL-Divergence Loss\nvs Teacher Probabilities"]
            MSE["MSE Loss\nvs Teacher Representations"]
        end
        
        LossComp --> CE
        LossComp --> KL
        LossComp --> MSE
        
        CE --> CombinedLoss["Combined Loss"]
        KL --> CombinedLoss
        MSE --> CombinedLoss
        
        CombinedLoss --> Optimize
    end
    
    Training --> Metrics["Training Metrics"]
    Training --> SavedModel["Trained Student Model"]
```

Key components of the distillation training:
- Multi-dataset support with custom sampling probabilities
- Mixed-precision training options
- Teacher-student knowledge transfer via combined loss functions
- Encoder freezing option for memory efficiency
- WER threshold filtering to avoid training on poor pseudo-labels

Sources: [training/flax/README.md:103-168](training/flax/README.md:103-168), [training/flax/run_distillation.py:724-781](training/flax/run_distillation.py:724-781)

### 4. Evaluation

The Flax implementation provides two types of evaluation:

1. **Short-form evaluation**: For audio samples less than 30 seconds using `run_eval.py`
2. **Long-form evaluation**: For longer audio samples using `run_long_form_transcription.py` and the `FlaxWhisperPipeline`

```mermaid
flowchart LR
    subgraph "Evaluation Methods"
        direction TB
        ShortForm["Short-form Evaluation\n(<30s audio)"] --> StandardDecoding["Standard Decoding"]
        LongForm["Long-form Evaluation\n(>30s audio)"] --> ChunkedInference["Chunked Inference"]
    end
    
    ChunkedInference --> |"Process"| CI1["1. Divide audio into chunks"]
    CI1 --> CI2["2. Process chunks in parallel"]
    CI2 --> CI3["3. Join transcriptions"]
    
    StandardDecoding --> Metrics["WER Metrics"]
    CI3 --> Metrics
```

The `FlaxWhisperPipeline` class enables chunked inference for long-form audio, dividing it into smaller segments with overlap and processing them in parallel.

Sources: [training/flax/README.md:176-242](training/flax/README.md:176-242), [training/flax/distil_whisper/pipeline.py:61-527](training/flax/distil_whisper/pipeline.py:61-527)

## Key Differences from PyTorch Implementation

The Flax implementation has some important differences compared to the PyTorch version:

| Feature | Flax Implementation | PyTorch Implementation |
|---------|---------------------|------------------------|
| Language Support | English ASR only | Multilingual support |
| Hardware Optimization | Optimized for TPU v4 | Optimized for GPU |
| Layer Optimization | `scan_with_axes` for compilation speed | Traditional layer stacking |
| Mixed Precision | Advanced options with fp32/bf16 | Standard mixed precision |
| Encoder Freezing | Memory-efficient encoder sharing | Standard freezing approach |
| Long-form Inference | Optimized chunked transcription | Standard chunked transcription |

Sources: [training/flax/README.md:16-18](training/flax/README.md:16-18)

## Practical Usage

### Requirements and Installation

To use the Flax implementation of Distil-Whisper:

1. Install JAX following the [official instructions](https://github.com/google/jax#installation)
2. Install the `distil_whisper` package:

```bash
git clone https://github.com/huggingface/distil-whisper.git
cd distil-whisper/training/flax
pip install -e .
```

### Running the Four-Stage Pipeline

Here's how to execute each stage of the pipeline:

1. **Pseudo-labelling**: Generate transcriptions using the teacher model
2. **Initialization**: Create a student model from the teacher
3. **Training**: Perform distillation training
4. **Evaluation**: Measure the performance on test sets

Each of these stages can be executed using the corresponding scripts in the repository, with examples provided in the README.

Sources: [training/flax/README.md:20-32](training/flax/README.md:20-32)

## Performance Considerations

When using the Flax implementation, consider these performance factors:

- **use_scan**: Enable for training (faster compilation, more memory efficient), disable for inference
- **freeze_encoder**: Enable when student encoder is identical to teacher (significant memory savings)
- **dtype**: Use `bfloat16` on TPUs and modern GPUs for best performance
- **chunk_length_s**: For long-form audio, tune this parameter to match the student model's training context length

For long-form transcription, the `chunk_length_s` parameter should be tuned to the specific model. The repository provides a sweep script to find the optimal value.

Sources: [training/flax/README.md:163-167](training/flax/README.md:163-167), [training/flax/README.md:236-242](training/flax/README.md:236-242)

## Conclusion

The Flax implementation of Distil-Whisper provides an efficient, high-performance framework for training and deploying distilled speech recognition models. It leverages JAX's advanced features for parallelism and compilation optimization, making it particularly well-suited for large-scale training on TPUs. While currently focused on English ASR, the architecture and approach provide a solid foundation for future multilingual extensions.

---

