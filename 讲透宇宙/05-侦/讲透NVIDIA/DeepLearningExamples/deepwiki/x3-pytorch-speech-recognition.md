<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/DeepLearningExamples · extra page PyTorch Speech Recognition · fetched 2026-10-26 -->

# PyTorch Speech Recognition

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PyTorch/SpeechRecognition/Jasper/Dockerfile](PyTorch/SpeechRecognition/Jasper/Dockerfile)
- [PyTorch/SpeechRecognition/Jasper/common/audio.py](PyTorch/SpeechRecognition/Jasper/common/audio.py)
- [PyTorch/SpeechRecognition/Jasper/common/features.py](PyTorch/SpeechRecognition/Jasper/common/features.py)
- [PyTorch/SpeechRecognition/Jasper/common/tb_dllogger.py](PyTorch/SpeechRecognition/Jasper/common/tb_dllogger.py)
- [PyTorch/SpeechRecognition/Jasper/requirements.txt](PyTorch/SpeechRecognition/Jasper/requirements.txt)
- [PyTorch/SpeechRecognition/Jasper/train.py](PyTorch/SpeechRecognition/Jasper/train.py)
- [PyTorch/SpeechRecognition/Jasper/utils/preprocessing_utils.py](PyTorch/SpeechRecognition/Jasper/utils/preprocessing_utils.py)
- [PyTorch/SpeechRecognition/QuartzNet/Dockerfile](PyTorch/SpeechRecognition/QuartzNet/Dockerfile)
- [PyTorch/SpeechRecognition/QuartzNet/common/tb_dllogger.py](PyTorch/SpeechRecognition/QuartzNet/common/tb_dllogger.py)
- [PyTorch/SpeechRecognition/QuartzNet/requirements.txt](PyTorch/SpeechRecognition/QuartzNet/requirements.txt)
- [PyTorch/SpeechRecognition/QuartzNet/train.py](PyTorch/SpeechRecognition/QuartzNet/train.py)
- [PyTorch/SpeechSynthesis/FastPitch/common/tb_dllogger.py](PyTorch/SpeechSynthesis/FastPitch/common/tb_dllogger.py)
- [PyTorch/SpeechSynthesis/FastPitch/requirements.txt](PyTorch/SpeechSynthesis/FastPitch/requirements.txt)

</details>



This document provides a comprehensive overview of the PyTorch-based automatic speech recognition (ASR) models available in the NVIDIA DeepLearningExamples repository. It focuses specifically on the Jasper and QuartzNet neural network architectures and their implementations. For information about text-to-speech models, see [PyTorch Text-to-Speech](#2.3.2).

## 1. Overview of Speech Recognition Models

The repository implements two state-of-the-art end-to-end speech recognition models:

1. **Jasper** - Joint Audio Speech and Encoder Recognition model
2. **QuartzNet** - A lightweight variant of Jasper with similar accuracy but fewer parameters

Both models are:
- End-to-end neural network architectures for ASR
- Based on convolutional neural networks (no recurrent layers)
- Trained with Connectionist Temporal Classification (CTC) loss
- Optimized for NVIDIA GPUs with mixed-precision training support

```mermaid
graph TD
    subgraph "PyTorch Speech Recognition Models"
        Jasper["Jasper\n(Joint Audio Speech and Encoder Recognition)"]
        QuartzNet["QuartzNet\n(Lightweight variant of Jasper)"]
    end
    
    Jasper --> Features["Common Feature Extraction\nFilterbankFeatures"]
    QuartzNet --> Features
    
    Features --> Training["Training Pipeline\n- CTC Loss\n- Novograd/AdamW\n- Mixed Precision"]
    
    Training --> Eval["Evaluation\n- GreedyCTCDecoder\n- WER Calculation"]
    
    subgraph "Optimizations"
        DALI["DALI Data Loading"]
        MultiGPU["Multi-GPU Training (DDP)"]
        AMP["Automatic Mixed Precision"]
        GA["Gradient Accumulation"]
    end
    
    DALI --> Training
    MultiGPU --> Training
    AMP --> Training
    GA --> Training
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:305-311](), [PyTorch/SpeechRecognition/QuartzNet/train.py:326-330]()

## 2. Model Architectures

### 2.1 Common Architecture Elements

Both Jasper and QuartzNet follow a similar architectural pattern:

```mermaid
flowchart LR
    subgraph "ASR Pipeline"
        direction LR
        Audio["Audio Input"] --> Features["FilterbankFeatures"]
        Features --> Encoder["Encoder\n(Jasper/QuartzNet)"]
        Encoder --> Decoder["CTC Decoder"]
        Decoder --> Text["Text Output"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:305-311](), [PyTorch/SpeechRecognition/QuartzNet/train.py:326-330]()

### 2.2 Jasper Architecture

Jasper is a deep convolutional neural network for end-to-end speech recognition. The model architecture consists of blocks of 1D convolutions, batch normalization, ReLU, and dropout.

```mermaid
graph TD
    subgraph "Jasper Model Architecture"
        Input["Input\nMel Spectrogram"] --> JasperEncoder
        
        subgraph "JasperEncoder"
            prologLayer["Prolog Layer\n1D Conv + BatchNorm + ReLU"]
            
            subgraph "JBlocks"
                B1["JBlock 1\n(R Subblocks)"]
                B2["JBlock 2\n(R Subblocks)"]
                BN["..."]
                BLast["JBlock N\n(R Subblocks)"]
                
                subgraph "JBlock Subblock"
                    Conv["1D Conv"]
                    BN["BatchNorm"]
                    ReLU["ReLU"]
                    Dropout["Dropout"]
                end
            end
            
            epilogLayer["Epilog Layer\n1D Conv + BatchNorm + ReLU"]
        end
        
        JasperEncoder --> CTCDecoder["CTCDecoder\n(Linear + LogSoftmax)"]
        CTCDecoder --> Output["Output\nProbabilities"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:305-308]()

### 2.3 QuartzNet Architecture

QuartzNet is an optimized variant of Jasper that uses depthwise separable convolutions to reduce the number of parameters while maintaining accuracy. This makes it more lightweight and efficient.

```mermaid
graph TD
    subgraph "QuartzNet Model Architecture"
        Input["Input\nMel Spectrogram"] --> QuartzNetEncoder
        
        subgraph "QuartzNetEncoder"
            prologLayer["Prolog Layer\n1D Conv + BatchNorm + ReLU"]
            
            subgraph "QBlocks"
                B1["QBlock 1\n(R Subblocks)"]
                B2["QBlock 2\n(R Subblocks)"]
                BN["..."]
                BLast["QBlock N\n(R Subblocks)"]
                
                subgraph "QBlock Subblock"
                    DWConv["1D Depthwise Conv"]
                    BN1["BatchNorm"]
                    ReLU1["ReLU"]
                    PWConv["1D Pointwise Conv"]
                    BN2["BatchNorm"]
                    ReLU2["ReLU"]
                    Dropout["Dropout"]
                end
            end
            
            epilogLayer["Epilog Layer\n1D Conv + BatchNorm + ReLU"]
        end
        
        QuartzNetEncoder --> CTCDecoder["CTCDecoder\n(Linear + LogSoftmax)"]
        CTCDecoder --> Output["Output\nProbabilities"]
    end
```

Sources: [PyTorch/SpeechRecognition/QuartzNet/train.py:326-330]()

## 3. Feature Extraction

Audio feature extraction is a critical pre-processing step for speech recognition models. Both models use the same feature extraction process.

### 3.1 Filterbank Features

The `FilterbankFeatures` class processes raw audio into mel-spectrogram features:

```mermaid
flowchart TD
    audio["Raw Audio"] --> dither["Apply Dither"]
    dither --> preemph["Pre-emphasis"]
    preemph --> stft["Short-Time Fourier Transform (STFT)"]
    stft --> powspec["Power Spectrum"]
    powspec --> melfilter["Apply Mel Filterbank"]
    melfilter --> log["Log Compression"]
    log --> norm["Normalization"]
    norm --> features["Mel Spectrogram Features"]
```

Key parameters for feature extraction:
- Sample rate (default: 16000 Hz)
- Window size (default: 20ms)
- Window stride (default: 10ms)
- Number of mel filters (default: 64)
- Optional augmentations: SpecAugment, Cutout

Sources: [PyTorch/SpeechRecognition/Jasper/common/features.py:196-298]()

## 4. Data Processing Pipeline

### 4.1 Dataset Structure

The data processing pipeline supports audio datasets in the following format:

```
dataset_dir/
├── file1.wav
├── file2.wav
└── ...
```

With a JSON manifest file containing:

```json
{"audio_filepath": "file1.wav", "duration": 3.45, "text": "transcript text"}
{"audio_filepath": "file2.wav", "duration": 2.18, "text": "another transcript"}
```

### 4.2 Data Processing Components

```mermaid
graph TD
    subgraph "Data Processing Pipeline"
        direction TB
        
        Manifest["JSON Manifest Files"] --> Dataset["AudioDataset"]
        
        Dataset --> DataLoader["DataLoader/DaliDataLoader"]
        
        RawAudio["Raw Audio"] --> AudioProcessing["Audio Preprocessing\n- Resampling\n- Speed Perturbation"]
        
        AudioProcessing --> FeatureExtraction["Feature Extraction\n(FilterbankFeatures)"]
        
        FeatureExtraction --> augment["Data Augmentation\n- SpecAugment\n- Cutout"]
        
        augment --> BatchProcessing["Batch Processing\n- Padding\n- Normalization"]
        
        BatchProcessing --> TrainingBatch["Training Batch"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:211-301](), [PyTorch/SpeechRecognition/QuartzNet/train.py:232-321]()

### 4.3 Data Loading Options

The implementation provides two main options for data loading:

1. **Standard PyTorch DataLoader**:
   - `AudioDataset` for data loading
   - `FilterbankFeatures` for feature extraction on GPU

2. **DALI DataLoader**:
   - GPU-accelerated data loading pipeline
   - Optimized for performance with NVIDIA GPUs
   - Supports feature extraction within the pipeline

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:215-290](), [PyTorch/SpeechRecognition/QuartzNet/train.py:236-310]()

## 5. Training Process

### 5.1 Training Pipeline

```mermaid
flowchart TD
    subgraph "Training Pipeline"
        direction TB
        
        config["Load Configuration\nand Setup"] --> dataload["Setup Dataloaders"]
        dataload --> model["Initialize Model"]
        model --> optimizer["Setup Optimizer\n(Novograd/AdamW)"]
        
        optimizer --> train["Training Loop"]
        
        train --> forward["Forward Pass\n- Feature Extraction\n- Model Forward\n- CTC Loss"]
        forward --> backward["Backward Pass\n- Gradient Computation\n- Gradient Accumulation"]
        backward --> optimize["Optimizer Step"]
        optimize --> lrschedule["LR Scheduling"]
        
        lrschedule --> ema["EMA Update\n(if enabled)"]
        
        ema --> log["Logging\n- Loss\n- WER\n- Throughput"]
        
        log --> eval["Periodic Evaluation"]
        
        eval --> checkpoint["Checkpointing"]
        
        checkpoint --> train
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:354-494](), [PyTorch/SpeechRecognition/QuartzNet/train.py:383-531]()

### 5.2 Loss Function

Both models use the CTC (Connectionist Temporal Classification) loss, implemented as `CTCLossNM`:

```mermaid
graph LR
    subgraph "CTCLoss Calculation"
        logprobs["Log Probabilities\nfrom Model"] --> ctcloss["CTCLossNM"]
        targets["Target Transcripts"] --> ctcloss
        enclens["Encoder Output Lengths"] --> ctcloss
        txtlens["Target Transcript Lengths"] --> ctcloss
        ctcloss --> loss["Loss Value"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:308-417](), [PyTorch/SpeechRecognition/QuartzNet/train.py:329-448]()

### 5.3 Optimizers and Learning Rate Scheduling

The implementation supports multiple optimizers:
- **Novograd** (default): A variant of Adam with layer-wise normalization
- **AdamW**: Adam with decoupled weight decay
- **LAMB** (QuartzNet only): Layer-wise Adaptive Moments for Batch optimization
- **Fused Novograd** (QuartzNet only): Optimized implementation of Novograd

Learning rate scheduling options:
- **Exponential decay**: Learning rate decays exponentially
- **Legacy**: Custom learning rate schedule with warmup and hold phases

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:313-328](), [PyTorch/SpeechRecognition/QuartzNet/train.py:334-356]()

## 6. Performance Optimization

### 6.1 Mixed Precision Training

Both models support mixed precision training using PyTorch's Automatic Mixed Precision (AMP):

```mermaid
flowchart TD
    subgraph "Mixed Precision Training"
        direction TB
        
        input["Input Batch"] --> autocasting["torch.cuda.amp.autocast\n(FP16 Operations)"]
        autocasting --> forward["Model Forward Pass"]
        forward --> loss["Loss Calculation"]
        
        loss --> scaler["GradScaler.scale(loss)"]
        scaler --> backward["Backward Pass"]
        backward --> optimize["scaler.step(optimizer)"]
        optimize --> update["scaler.update()"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:322-446](), [PyTorch/SpeechRecognition/QuartzNet/train.py:350-470]()

### 6.2 Multi-GPU Training

Distributed training is implemented using PyTorch's DistributedDataParallel (DDP):

```mermaid
flowchart LR
    subgraph "Multi-GPU Training"
        direction TB
        
        init["Initialize Process Group\n(NCCL Backend)"] --> wrap["Wrap Model in DDP"]
        
        subgraph "GPU 0"
            model0["Model Replica"]
            opt0["Optimizer"]
        end
        
        subgraph "GPU 1"
            model1["Model Replica"] 
            opt1["Optimizer"]
        end
        
        subgraph "GPU N"
            modelN["Model Replica"]
            optN["Optimizer"]
        end
        
        wrap --> sync["Synchronized Forward/Backward"]
        sync --> allreduce["All-Reduce Gradients"]
        allreduce --> update["Update Parameters"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:335-337](), [PyTorch/SpeechRecognition/QuartzNet/train.py:363-365]()

### 6.3 DALI Data Loading

NVIDIA Data Loading Library (DALI) provides GPU-accelerated data loading:

```mermaid
flowchart TD
    subgraph "DALI Pipeline"
        direction TB
        
        readers["FileReaders"] --> decode["Audio Decoder"]
        decode --> preprocess["Preprocessing\n(Resampling, Normalization)"]
        preprocess --> feat["Feature Extraction"]
        feat --> augment["Data Augmentation"]
        augment --> batch["Batch Assembly"]
        batch --> gpu["GPU Transfer"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:236-265](), [PyTorch/SpeechRecognition/QuartzNet/train.py:266-285]()

### 6.4 Gradient Accumulation

Both implementations support gradient accumulation to simulate larger batch sizes:

```mermaid
flowchart TD
    subgraph "Gradient Accumulation"
        direction TB
        
        batch1["Mini-batch 1"] --> forward1["Forward Pass"]
        forward1 --> loss1["Loss/N"]
        loss1 --> backward1["Backward (Accumulate Gradients)"]
        
        batch2["Mini-batch 2"] --> forward2["Forward Pass"]
        forward2 --> loss2["Loss/N"]
        loss2 --> backward2["Backward (Accumulate Gradients)"]
        
        dots["..."]
        
        batchN["Mini-batch N"] --> forwardN["Forward Pass"]
        forwardN --> lossN["Loss/N"]
        lossN --> backwardN["Backward (Accumulate Gradients)"]
        
        backward1 --> dots
        dots --> backwardN
        
        backwardN --> optimize["Optimizer Step"]
        optimize --> zero["Zero Gradients"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:436-442](), [PyTorch/SpeechRecognition/QuartzNet/train.py:467-473]()

## 7. Inference and Evaluation

### 7.1 Greedy CTC Decoding

For inference, both models use a simple greedy CTC decoder:

```mermaid
flowchart LR
    subgraph "Greedy CTC Decoding"
        direction LR
        
        logprobs["Model Log Probabilities"] --> argmax["Argmax over Classes"]
        argmax --> collapse["Collapse Repeated Symbols"]
        collapse --> remove["Remove Blank Symbols"]
        remove --> text["Decoded Text"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:308-447](), [PyTorch/SpeechRecognition/QuartzNet/train.py:330-479]()

### 7.2 Word Error Rate Calculation

Model performance is evaluated using Word Error Rate (WER):

```mermaid
flowchart TD
    subgraph "WER Calculation"
        direction TB
        
        pred["Model Predictions"] --> decode["Greedy Decoding"]
        decode --> normalize["Text Normalization"]
        
        ref["Reference Transcripts"] --> refnorm["Text Normalization"]
        
        normalize --> compare["Compare Sequences"]
        refnorm --> compare
        
        compare --> calculate["Calculate WER\n(Levenshtein Distance / Reference Length)"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:137-175](), [PyTorch/SpeechRecognition/QuartzNet/train.py:157-196]()

## 8. Getting Started

### 8.1 Requirements

Both models have similar requirements:

| Requirement | Version |
|-------------|---------|
| Python      | 3.8+    |
| PyTorch     | 1.13+   |
| CUDA        | 11.0+   |
| NVIDIA Container | NGC PyTorch Container |
| Libraries   | inflect, librosa, pandas, pyyaml, soundfile, sox, tqdm, dllogger |

Sources: [PyTorch/SpeechRecognition/Jasper/requirements.txt:1-9](), [PyTorch/SpeechRecognition/QuartzNet/requirements.txt:1-9]()

### 8.2 Example Usage

To train Jasper on a dataset:

```bash
python train.py \
  --model_config=configs/jasper10x5dr.yaml \
  --train_manifests=/path/to/train_manifest.json \
  --val_manifests=/path/to/val_manifest.json \
  --dataset_dir=/path/to/dataset \
  --output_dir=/path/to/output \
  --amp \
  --batch_size=64 \
  --lr=0.015 \
  --epochs=400 \
  --weight_decay=0.001 \
  --optimizer=novograd \
  --ema=0.999 \
  --dali_device=gpu
```

For QuartzNet:

```bash
python train.py \
  --model_config=configs/quartznet15x5.yaml \
  --train_manifests=/path/to/train_manifest.json \
  --val_manifests=/path/to/val_manifest.json \
  --dataset_dir=/path/to/dataset \
  --output_dir=/path/to/output \
  --amp \
  --gpu_batch_size=16 \
  --grad_accumulation=8 \
  --lr=0.01 \
  --epochs=400 \
  --weight_decay=0.001 \
  --optimizer=novograd \
  --ema=0.999 \
  --dali_device=gpu
```

Sources: [PyTorch/SpeechRecognition/Jasper/train.py:39-117](), [PyTorch/SpeechRecognition/QuartzNet/train.py:41-125]()

### 8.3 Pre-processing Audio Data

The repository includes utilities for preprocessing audio data:

```mermaid
flowchart LR
    subgraph "Audio Preprocessing"
        direction LR
        
        audio["Raw Audio Files"] --> convert["Convert to WAV Format"]
        convert --> resample["Resample to Target SR"]
        resample --> perturb["Optional Speed Perturbation"]
        perturb --> manifest["Generate JSON Manifest"]
    end
```

Sources: [PyTorch/SpeechRecognition/Jasper/utils/preprocessing_utils.py:25-74]()

## 9. Conclusion

The PyTorch Speech Recognition implementations in the NVIDIA DeepLearningExamples repository provide optimized and efficient end-to-end ASR models. Both Jasper and QuartzNet offer state-of-the-art performance with various optimizations for NVIDIA GPUs, including mixed precision training, multi-GPU support, and DALI data loading. The modular architecture allows for experimentation with different configurations and hyperparameters to achieve optimal performance on specific datasets.

---

