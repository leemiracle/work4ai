<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/speech-to-speech · extra page Whisper-Family STT Handlers · fetched 2026-10-26 -->

# Whisper-Family STT Handlers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/speech_to_speech/STT/faster_whisper_handler.py](src/speech_to_speech/STT/faster_whisper_handler.py)
- [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py](src/speech_to_speech/STT/lightning_whisper_mlx_handler.py)
- [src/speech_to_speech/STT/mlx_audio_whisper_handler.py](src/speech_to_speech/STT/mlx_audio_whisper_handler.py)
- [src/speech_to_speech/STT/whisper_stt_handler.py](src/speech_to_speech/STT/whisper_stt_handler.py)
- [tests/test_faster_whisper_language_code.py](tests/test_faster_whisper_language_code.py)
- [tests/test_mlx_audio_whisper_handler.py](tests/test_mlx_audio_whisper_handler.py)
- [tests/test_whisper_language_detection.py](tests/test_whisper_language_detection.py)
- [tests/test_whisper_progressive_transcription.py](tests/test_whisper_progressive_transcription.py)

</details>



## Purpose and Scope
This page details the Whisper-family Speech-to-Text (STT) handlers in the speech-to-speech codebase. These handlers convert speech input into text using various implementations of OpenAI's Whisper model, catering to different hardware targets (CUDA, CPU, and Apple Silicon MLX). Specifically, this covers:
- Transformers Whisper (`WhisperSTTHandler`) with `torch.compile` and static cache support [src/speech_to_speech/STT/whisper_stt_handler.py:46-81]()
- Faster Whisper (`FasterWhisperSTTHandler`) using CTranslate2 [src/speech_to_speech/STT/faster_whisper_handler.py:36-63]()
- Lightning Whisper MLX (`LightningWhisperSTTHandler`) for Apple Silicon [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:36-54]()
- MLX Audio Whisper (`MLXAudioWhisperSTTHandler`) using MLX Audio [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:36-61]()

Sources: [src/speech_to_speech/STT/whisper_stt_handler.py:46-81](), [src/speech_to_speech/STT/faster_whisper_handler.py:36-63](), [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:36-54](), [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:36-61]()

---

## Handler Ecosystem and Backend Mapping
To bridge natural language STT processing to code entities, the following diagram maps the logical Whisper execution paths to their respective handler classes across backends.

```mermaid
graph TB
    subgraph "Natural Language Space"
        ["Speech Audio Stream"]
        ["Language Detection / Auto"]
        ["Progressive & Final Transcription"]
    end

    subgraph "Code Entity Space (speech_to_speech/STT)"
        ["BaseSTTHandler"]
        ["WhisperSTTHandler"]
        ["FasterWhisperSTTHandler"]
        ["LightningWhisperSTTHandler"]
        ["MLXAudioWhisperSTTHandler"]

        ["WhisperSTTHandler"] -- "inherits" --> ["BaseSTTHandler"]
        ["FasterWhisperSTTHandler"] -- "inherits" --> ["BaseSTTHandler"]
        ["LightningWhisperSTTHandler"] -- "inherits" --> ["BaseSTTHandler"]
        ["MLXAudioWhisperSTTHandler"] -- "inherits" --> ["BaseSTTHandler"]
    end

    ["Speech Audio Stream"] --> ["WhisperSTTHandler"]
    ["Speech Audio Stream"] --> ["FasterWhisperSTTHandler"]
    ["Speech Audio Stream"] --> ["LightningWhisperSTTHandler"]
    ["Speech Audio Stream"] --> ["MLXAudioWhisperSTTHandler"]
```

Sources: [src/speech_to_speech/STT/base_stt_handler.py:1-20](), [src/speech_to_speech/STT/whisper_stt_handler.py:46-51](), [src/speech_to_speech/STT/faster_whisper_handler.py:36-40](), [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:36-40](), [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:36-41]()

---

## 1. Transformers Whisper Handler (`WhisperSTTHandler`)
The standard Hugging Face Transformers implementation uses `AutoModelForSpeechSeq2Seq` and `AutoProcessor` [src/speech_to_speech/STT/whisper_stt_handler.py:10-11]().

### Setup and Compilation
The `setup` method configures device, dtype, and optional `torch.compile` optimization [src/speech_to_speech/STT/whisper_stt_handler.py:53-81](). When `compile_mode` is provided, it configures a static cache and compiles `model.forward` with `fullgraph=True` [src/speech_to_speech/STT/whisper_stt_handler.py:78-80]().

```mermaid
graph TD
    subgraph "WhisperSTTHandler Setup"
        ["setup()"] --> ["Load AutoProcessor & AutoModelForSpeechSeq2Seq"]
        ["Load AutoProcessor & AutoModelForSpeechSeq2Seq"] --> CHECK{"compile_mode set?"}
        CHECK -- "Yes" --> ["Set cache_implementation = 'static'"]
        ["Set cache_implementation = 'static'"] --> ["torch.compile(model.forward, mode=compile_mode, fullgraph=True)"]
        CHECK -- "No" --> WARM["warmup()"]
        ["torch.compile(...)"] --> WARM
    end
```

Sources: [src/speech_to_speech/STT/whisper_stt_handler.py:53-81]()

### Language Detection and Warmup
Language detection uses `detect_language()` via encoder outputs when available [src/speech_to_speech/STT/whisper_stt_handler.py:166-177](). Warmup adapts the number of steps based on compilation mode and runs dummy forward/generate passes to prevent cold-start latency [src/speech_to_speech/STT/whisper_stt_handler.py:89-127]().

Sources: [src/speech_to_speech/STT/whisper_stt_handler.py:89-127](), [src/speech_to_speech/STT/whisper_stt_handler.py:166-177]()

---

## 2. Faster Whisper Handler (`FasterWhisperSTTHandler`)
The `FasterWhisperSTTHandler` integrates `faster_whisper.WhisperModel` backed by CTranslate2 [src/speech_to_speech/STT/faster_whisper_handler.py:7-62]().

### Configuration and Language Normalization
`setup()` normalizes `gen_kwargs` and language requests, mapping `"auto"` or `None` to auto-detection while passing through explicit ISO language codes [src/speech_to_speech/STT/faster_whisper_handler.py:45-74]().

### Processing Flow
During `process()`, audio chunks are transcribed via `self.model.transcribe()`, returning segments and an `info` object containing detected language metadata [src/speech_to_speech/STT/faster_whisper_handler.py:107-115](). Detected language fallback is resolved using `_resolve_language(info)` [src/speech_to_speech/STT/faster_whisper_handler.py:76-105]().

Sources: [src/speech_to_speech/STT/faster_whisper_handler.py:36-115]()

---

## 3. Lightning Whisper MLX Handler (`LightningWhisperSTTHandler`)
Optimized for Apple Silicon via `lightning_whisper_mlx` [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:8-53]().

### Execution and MLX Locking
`setup()` initializes `LightningWhisperMLX` with a batch size of 6 [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:53](). `process()` and `warmup()` utilize `MLXLockContext` to prevent concurrent Metal queue violations across pipeline threads [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:67](), [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:75](). MPS cache is cleared using `torch.mps.empty_cache()` when running on MPS [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:89-90]().

Sources: [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:36-94]()

---

## 4. MLX Audio Whisper Handler (`MLXAudioWhisperSTTHandler`)
`MLXAudioWhisperSTTHandler` integrates MLX Audio's Whisper generation pipeline [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:36-60]().

### Model and Processor Fallback
If the loaded MLX model lacks a built-in processor (`self.model._processor is None`), the handler maps model names to their original OpenAI Whisper counterparts and loads `WhisperProcessor` from pretrained weights [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:63-80]().

### Thread Safety and Language Resolution
Inference is serialized using `MLXLockContext` [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:149](). `_resolve_language()` checks forced languages, detected language codes against `SUPPORTED_LANGUAGES`, and sticky fallbacks [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:110-128]().

Sources: [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:36-128]()

---

## 5. Progressive Transcription Support
All Whisper handlers support progressive transcription modes (`vad_audio.mode == "progressive"`), yielding `PartialTranscription` messages during active speech rather than prematurely closing turns with final `Transcription` outputs [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:99-105](), [src/speech_to_speech/STT/faster_whisper_handler.py:123-129](), [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:168-174](), [tests/test_whisper_progressive_transcription.py:1-16]().

Sources: [src/speech_to_speech/STT/lightning_whisper_mlx_handler.py:99-105](), [src/speech_to_speech/STT/faster_whisper_handler.py:123-129](), [src/speech_to_speech/STT/mlx_audio_whisper_handler.py:168-174](), [tests/test_whisper_progressive_transcription.py:1-16]()

---

