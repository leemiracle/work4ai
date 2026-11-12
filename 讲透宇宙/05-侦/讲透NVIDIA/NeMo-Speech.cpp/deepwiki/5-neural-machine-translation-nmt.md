<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-Speech.cpp · page 5 Neural Machine Translation (NMT) · fetched 2026-10-26 -->

# Neural Machine Translation (NMT)

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [config/nmt.example.yaml](config/nmt.example.yaml)
- [docs/nmt/configuration.md](docs/nmt/configuration.md)
- [docs/nmt/models.md](docs/nmt/models.md)
- [src/asr/pnc/pnc_runner.cpp](src/asr/pnc/pnc_runner.cpp)
- [src/nmt/langpairs.cc](src/nmt/langpairs.cc)
- [src/nmt/langpairs.h](src/nmt/langpairs.h)
- [src/nmt/translator.cpp](src/nmt/translator.cpp)
- [src/nmt/translator.h](src/nmt/translator.h)
- [src/speech/speech_translator.cpp](src/speech/speech_translator.cpp)
- [src/speech/speech_translator.h](src/speech/speech_translator.h)
- [src/tts/magpietts/encoder.cpp](src/tts/magpietts/encoder.cpp)
- [tests/cpp/nmt/test_langpairs.cpp](tests/cpp/nmt/test_langpairs.cpp)
- [tests/cpp/nmt/test_nmt.cpp](tests/cpp/nmt/test_nmt.cpp)
- [tests/cpp/tts/test_tts_terminal_punctuation.cpp](tests/cpp/tts/test_tts_terminal_punctuation.cpp)

</details>



The Neural Machine Translation (NMT) subsystem in NeMo-Speech.cpp provides high-performance text translation using the **Riva-Translate** model family. It leverages a pinned version of `llama.cpp` as the execution engine, allowing it to share the underlying `ggml` runtime with the ASR and TTS subsystems. The NMT component is designed for both standalone text translation and integrated speech-to-speech translation pipelines.

## Riva-Translate and llama.cpp Integration

The NMT subsystem is built around the `nemo_speech::nmt::Translator` class, which acts as a wrapper for `llama.cpp` `[src/nmt/translator.h:74-91]()`. It supports the **Riva-Translate-4B-Instruct-v2** model, a Mistral/Llama-architecture transformer optimized for translation across dozens of language pairs `[docs/nmt/models.md:3-8]()`.

### Key Integration Features
*   **Shared Runtime:** NMT reuses the root `ggml` target, ensuring that ASR, TTS, and NMT share a single backend (CUDA, Metal, etc.) at runtime `[docs/nmt/models.md:29-30]()`.
*   **Prompt Engineering:** The system automatically wraps input text in a chat-style translation prompt (System/User turns) based on the requested language pair `[src/nmt/langpairs.cc:183-185]()`.
*   **Thread Safety:** The `Translator` manages a pool of decode contexts, allowing `translate()` to be called concurrently from multiple threads `[src/nmt/translator.h:79-84]()`.

### NMT System Architecture
The following diagram illustrates how the NMT library interacts with `llama.cpp` and the language pair resolution logic.

**NMT Logic Flow**
```mermaid
graph TD
    subgraph "Natural Language Space"
        Input["Source Text"]
        LangPair["Source/Target Codes (e.g., 'en', 'es')"]
    end

    subgraph "Code Entity Space: nemo_speech::nmt"
        direction TB
        [Translator] -- "uses" --> [Impl]
        [Impl] -- "calls" --> [langpairs::resolve_tag]
        [langpairs::resolve_tag] -- "returns" --> Tag["Pair Tag (en-es)"]
        Tag -- "passed to" --> [langpairs::build_prompt]
        [langpairs::build_prompt] -- "generates" --> Prompt["<s>System...<s>User..."]
        
        subgraph "Execution Layer"
            Prompt -- "tokenized by" --> [llama_tokenize]
            [llama_tokenize] -- "fed to" --> [llama_decode]
            [llama_decode] -- "samples" --> [llama_sampler_sample]
        end
    end

    Input --> [Translator]
    LangPair --> [Translator]
    [llama_sampler_sample] --> Output["Translated Text"]
```
Sources: `[src/nmt/translator.cpp:145-186]()`, `[src/nmt/langpairs.cc:145-186]()`

## Language Pair Support

The system supports a wide array of language pairs, typically involving English as either the source or target. The `nemo_speech::nmt::langpairs` namespace handles the normalization of BCP-47 codes and the resolution of supported tags `[src/nmt/langpairs.h:13-40]()`.

| Feature | Description |
|---|---|
| **Normalization** | Converts codes like `EN-US` to `en` or `es-ES` to `es-es` to match model tags `[src/nmt/langpairs.cc:102-125]()`. |
| **Tag Resolution** | Resolves ambiguous inputs (e.g., source="en", target="de") into a unified tag `en-de` `[src/nmt/langpairs.cc:145-173]()`. |
| **Prompt Template** | Matches the `Riva-Translate` v1.1 chat template for high-quality instruction following `[src/nmt/langpairs.cc:183-185]()`. |

For a complete list of supported pairs and configuration details, see **[NMT Configuration and Models](#5.1)**.

## Speech Translation Pipeline

The `nemo_speech::speech::SpeechTranslator` class provides a composite interface that links ASR, NMT, and TTS into a single streaming pipeline `[src/speech/speech_translator.h:65-85]()`.

1.  **ASR:** Captures audio and produces a transcript via `asr::RecognitionStream` `[src/speech/speech_translator.cpp:155]()`.
2.  **NMT:** Once a "final" ASR result is received, it is sent to `nmt::Translator` for translation `[src/speech/speech_translator.cpp:83-86]()`.
3.  **TTS:** The translated text is optionally passed to `tts::Synthesizer` to generate spoken audio in the target language `[src/speech/speech_translator.cpp:100-109]()`.

**Speech Translation Pipeline Entities**
```mermaid
graph LR
    subgraph "nemo_speech::speech"
        [SpeechTranslator] -- "creates" --> [SpeechTranslationStream]
        [SpeechTranslationStream] -- "manages" --> [SpeechTranslationStream::Impl]
    end

    subgraph "Subsystem Integration"
        [SpeechTranslationStream::Impl] -- "pushes audio to" --> [asr::RecognitionStream]
        [asr::RecognitionStream] -- "emits final to" --> [nmt::Translator]
        [nmt::Translator] -- "sends text to" --> [tts::Synthesizer]
    end

    [tts::Synthesizer] -- "yields" --> Audio["Target Audio"]
```
Sources: `[src/speech/speech_translator.cpp:67-142]()`, `[src/speech/speech_translator.h:18-44]()`

For details on the end-to-end flow and callbacks, see **[Speech Translation Pipeline](#5.2)**.

## Serving and RPCs

NMT capabilities are exposed through two primary server interfaces:
*   **HTTP/REST:** The `nemo-speech serve` command provides a `/v1/translations` endpoint for text-to-text translation `[docs/nmt/configuration.md:13-23]()`.
*   **Riva gRPC:** The `riva_server` binary implements `RivaTranslation.TranslateText`, `StreamingTranslateSpeechToText`, and `StreamingTranslateSpeechToSpeech` `[docs/nmt/configuration.md:61-80]()`.

For service enablement and gRPC details, see the **[Riva gRPC Server](#6.2)** documentation.

## Related Pages
*   **[NMT Configuration and Models](#5.1)** — Detailed model conversion steps, `nmt.*` config keys, and concurrency pooling.
*   **[Speech Translation Pipeline](#5.2)** — Deep dive into `src/speech/speech_translator.cpp` and the ASR → NMT → TTS coordination logic.

---

