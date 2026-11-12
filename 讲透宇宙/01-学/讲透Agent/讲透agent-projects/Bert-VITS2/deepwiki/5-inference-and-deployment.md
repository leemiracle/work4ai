<!-- source: DeepWiki mcp.deepwiki.com · repo fishaudio/Bert-VITS2 · page 5 Inference and Deployment · fetched 2026-10-29 -->

# Inference and Deployment

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [for_deploy/infer.py](for_deploy/infer.py)
- [infer.py](infer.py)
- [oldVersion/V210/__init__.py](oldVersion/V210/__init__.py)
- [oldVersion/V210/text/tone_sandhi.py](oldVersion/V210/text/tone_sandhi.py)
- [oldVersion/V220/__init__.py](oldVersion/V220/__init__.py)
- [oldVersion/V220/text/tone_sandhi.py](oldVersion/V220/text/tone_sandhi.py)
- [slm/wavlm-base-plus/.gitattributes](slm/wavlm-base-plus/.gitattributes)
- [slm/wavlm-base-plus/README.md](slm/wavlm-base-plus/README.md)
- [webui.py](webui.py)

</details>



This document provides a detailed guide on how to perform inference with trained Bert-VITS2 models and deploy them for production use. It covers the inference pipeline architecture, model loading process, version compatibility, and various deployment options. For information about training the models, see [Training Pipeline](#3).

## 1. Inference Architecture

The inference pipeline in Bert-VITS2 transforms input text into synthesized speech through several processing stages. The core pipeline handles multi-language support, speaker management, and various customization parameters.

### Inference Pipeline Overview

```mermaid
flowchart LR
    subgraph "Input Processing"
        Text["Input Text"] --> TextProcessing["Text Processing"]
        TextProcessing --> Phonemes["Phoneme Conversion"]
        TextProcessing --> Tones["Tone Extraction"]
        TextProcessing --> LangIDs["Language ID Assignment"]
        Phonemes & Tones & LangIDs --> BertFeatures["BERT Feature Extraction"]
    end

    subgraph "Model Inference"
        BertFeatures --> ModelInput["Model Input Preparation"]
        SpeakerID["Speaker ID"] --> SpeakerEmb["Speaker Embedding"]
        EmotionRef["Emotion/Reference"] --> EmotionEmb["Emotion Embedding"]
        ModelInput & SpeakerEmb & EmotionEmb --> NetG["SynthesizerTrn Model"]
        NetG --> AudioOut["Raw Audio Output"]
    end

    subgraph "Post-Processing"
        AudioOut --> Normalization["Audio Normalization"]
        Normalization --> FinalAudio["Final Audio"]
    end
```

Sources: [infer.py:151-332](), [webui.py:44-88]()

### Multi-Language Inference Process

The system supports inferring text that contains multiple languages, automatically handling the appropriate processing for each language segment.

```mermaid
flowchart TD
    Input["Input Text"] --> LangDetect{"Language \nDetection"}
    
    LangDetect -->|"Single Language"| SingleProc["Single Language Processing"]
    LangDetect -->|"Mix Format"| MixProc["Mixed Language Processing"]
    LangDetect -->|"Auto Detect"| AutoProc["Auto Language Detection"]
    
    SingleProc --> GetText["get_text() Function"]
    MixProc --> TextSplit["Split Text by Language"]
    TextSplit --> GetTextMulti["Multiple get_text() Calls"]
    AutoProc --> LangSplit["split_by_language()"]
    LangSplit --> GetTextMulti
    
    GetText --> BertEmb["BERT Embeddings"]
    GetTextMulti --> BertEmb
    
    BertEmb --> Infer["Model Inference"]
    Infer --> Audio["Generated Audio"]
```

Sources: [infer.py:335-437](), [webui.py:225-316]()

## 2. Model Loading and Version Compatibility

Bert-VITS2 includes a sophisticated version compatibility system that enables models trained with different versions to be used with the current codebase.

```mermaid
flowchart TD
    ModelPath["Model Path"] --> LoadModel["Load Model\nget_net_g()"]
    Config["Config.json"] --> LoadModel
    
    LoadModel --> VersionCheck{"Check Version"}
    
    VersionCheck -->|"Latest Version"| CurrentModel["Current Model\nSynthesizerTrn"]
    VersionCheck -->|"Older Version"| VersionMap["Version Mapping\nSynthesizerTrnMap"]
    
    VersionMap --> V220["V220SynthesizerTrn"]
    VersionMap --> V210["V210SynthesizerTrn"]
    VersionMap --> V200["V200SynthesizerTrn"]
    VersionMap --> V111["V111SynthesizerTrn"]
    VersionMap --> V110["V110SynthesizerTrn"]
    VersionMap --> V101["V101SynthesizerTrn"]
    
    V220 & V210 & V200 & V111 & V110 & V101 --> LoadCheckpoint["Load Checkpoint\nutils.load_checkpoint()"]
    CurrentModel --> LoadCheckpoint
    
    LoadCheckpoint --> ModelReady["Model Ready for Inference"]
```

Sources: [infer.py:84-104](), [infer.py:39-55]()

During inference, the system selects the appropriate inference function based on the model version:

```mermaid
flowchart TD
    TextInput["Text Input"] --> InferFunction["infer() Function"]
    ModelVersion["Model Version"] --> InferFunction
    
    InferFunction --> VersionCheck{"Check Version"}
    
    VersionCheck -->|"2.3 (Latest)"| CurrentInfer["Current Version Inference"]
    VersionCheck -->|"2.2"| V220Infer["V220.infer()"]
    VersionCheck -->|"2.1"| V210Infer["V210.infer()"]
    VersionCheck -->|"2.0.x"| V200Infer["V200.infer()"]
    VersionCheck -->|"1.1.x"| V11xInfer["V11x.infer()"]
    VersionCheck -->|"1.0.x"| V10xInfer["V10x.infer()"]
    
    CurrentInfer & V220Infer & V210Infer & V200Infer & V11xInfer & V10xInfer --> AudioOutput["Audio Output"]
```

Sources: [infer.py:151-259](), [infer.py:170-193]()

## 3. Text Processing for Inference

When converting text to speech, Bert-VITS2 processes the input through multiple stages to prepare it for the model:

```mermaid
flowchart LR
    Text["Input Text"] --> CleanText["Clean Text\nclean_text()"]
    CleanText --> Sequence["Text to Sequence\ncleaned_text_to_sequence()"]
    
    Sequence --> Phone["Phoneme Sequence"]
    Sequence --> Tone["Tone Sequence"]
    Sequence --> Lang["Language ID Sequence"]
    
    Phone & Tone & Lang --> AddBlank["Add Blank Tokens\ncommons.intersperse()"]
    
    AddBlank --> GetBert["Get BERT Features\nget_bert()"]
    
    GetBert --> BertFeatures["BERT Features"]
    AddBlank --> Tensors["Convert to Tensors"]
    
    BertFeatures & Tensors --> ModelInput["Model Input"]
```

Sources: [infer.py:107-148]()

## 4. Deployment Options

Bert-VITS2 provides multiple deployment options to suit different use cases.

### Web UI

The Web UI offers an interactive interface for text-to-speech synthesis with various customization options:

```mermaid
flowchart TD
    WebUI["webui.py\nGradio Interface"] --> TextInput["Text Input Area"]
    WebUI --> SpeakerSelection["Speaker Selection"]
    WebUI --> Parameters["Parameter Controls\n(SDP, Noise, Length)"]
    WebUI --> LanguageSelection["Language Selection"]
    WebUI --> PromptMode["Prompt Mode\n(Text/Audio)"]
    
    TextInput & SpeakerSelection & Parameters & LanguageSelection & PromptMode --> GenerateButton["Generate Audio Button"]
    
    GenerateButton --> TTS["tts_fn() Function"]
    TTS --> ProcessText["process_text() Function"]
    ProcessText --> GenerateAudio["generate_audio() Function"]
    GenerateAudio --> Infer["infer() Function"]
    
    Infer --> AudioOutput["Audio Output"]
    AudioOutput --> Display["Display in Web UI"]
```

Sources: [webui.py:403-569](), [webui.py:319-356]()

### Language Handling in Web UI

The Web UI supports several language modes:

1. **Single Language Mode**: Process text in a single language (ZH, JP, EN)
2. **Mix Mode**: Process text with explicit language tags
3. **Auto Mode**: Automatically detect languages in text

```mermaid
flowchart TD
    Text["Text Input"] --> Language{"Language\nSelection"}
    
    Language -->|"ZH/JP/EN"| SingleLang["Single Language Processing"]
    Language -->|"mix"| MixLang["Mixed Language Format\n[speaker]<lang>text"]
    Language -->|"auto"| AutoLang["Auto Language Detection"]
    
    SingleLang --> GenerateAudio["generate_audio()"]
    MixLang --> ProcessMix["process_mix()"]
    ProcessMix --> GenerateAudioMultilang["generate_audio_multilang()"]
    AutoLang --> ProcessAuto["process_auto()"]
    ProcessAuto --> GenerateAudioMultilang
    
    GenerateAudio & GenerateAudioMultilang --> FinalAudio["Final Audio"]
```

Sources: [webui.py:206-242](), [webui.py:245-316]()

### API Server

For programmatic access, Bert-VITS2 includes a FastAPI server for integration with other applications.

## 5. Inference Parameters

Bert-VITS2 provides several parameters to customize the generated speech:

| Parameter | Description | Default Value | Range |
|-----------|-------------|---------------|-------|
| SDP Ratio | Controls stochastic duration predictor influence | 0.5 | 0.0-1.0 |
| Noise Scale | Controls variation in the output | 0.6 | 0.1-2.0 |
| Noise Scale W | Controls variation in the phoneme duration | 0.9 | 0.1-2.0 |
| Length Scale | Controls the speed of speech | 1.0 | 0.1-2.0 |

Sources: [webui.py:443-454](), [infer.py:151-173]()

### Text Style and Emotion Control

Bert-VITS2 supports two methods for controlling the speaking style and emotion:

1. **Text Prompt**: Using text descriptions to guide the speaking style
2. **Audio Prompt**: Using a reference audio to guide the speaking style

```mermaid
flowchart TD
    Input["Input"] --> PromptMode{"Prompt\nMode"}
    
    PromptMode -->|"Text Prompt"| TextPrompt["Text Description\n(e.g., 'Happy')"]
    PromptMode -->|"Audio Prompt"| AudioPrompt["Reference Audio"]
    
    TextPrompt --> StyleEmb["Style Embedding"]
    AudioPrompt --> LoadAudio["Load Audio\nload_audio()"]
    LoadAudio --> AudioEmb["Audio Embedding"]
    
    StyleEmb & AudioEmb --> Inference["Model Inference"]
    Inference --> Output["Generated Audio"]
```

Sources: [webui.py:428-442](), [webui.py:332-339]()

## 6. Version Compatibility Details

Bert-VITS2 supports multiple versions with different features. The current architecture allows seamless use of models trained with previous versions.

| Version | Features | Added Components |
|---------|----------|------------------|
| 2.3 | Latest version | Current inference pipeline |
| 2.2 | CLAP-Enhanced audio generation | Audio and text prompt feature |
| 2.1 | Emotion and multi-language optimization | Emotion embedding support |
| 2.0.x | Multi-language support | Chinese, Japanese, English support |
| 1.1.x | Improved Chinese support | Japanese fixes in 1.1.1-fix |
| 1.0.x | Basic Chinese TTS | Initial VITS implementation |

Sources: [infer.py:1-9](), [infer.py:39-55](), [infer.py:170-193]()

## 7. ONNX Export and Inference

For production deployments requiring faster inference, models can be exported to ONNX format. For detailed information on ONNX export, see [ONNX Export and Inference](#6).

## 8. Performance Considerations

When deploying Bert-VITS2 for inference, consider the following:

1. **Memory Usage**: The model requires significant GPU memory, especially for larger models
2. **Batch Processing**: For processing long texts, use the splitting functionality in the Web UI
3. **GPU vs. CPU**: GPU provides significantly faster inference; CPU mode is available but much slower
4. **Version Compatibility**: Newer versions may include optimizations for faster inference

Sources: [webui.py:36-42](), [infer.py:290-332]()

---

