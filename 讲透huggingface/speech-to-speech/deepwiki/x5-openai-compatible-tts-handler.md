<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/speech-to-speech · extra page OpenAI-Compatible TTS Handler · fetched 2026-10-26 -->

# OpenAI-Compatible TTS Handler

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [docs/openai-compatible-tts.md](docs/openai-compatible-tts.md)
- [src/speech_to_speech/TTS/openai_compatible_handler.py](src/speech_to_speech/TTS/openai_compatible_handler.py)
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py](src/speech_to_speech/arguments_classes/openai_tts_arguments.py)
- [tests/test_openai_tts_handler.py](tests/test_openai_tts_handler.py)

</details>



This page details the `OpenAICompatibleTTSHandler` which provides an OpenAI-compatible HTTP Text-to-Speech (TTS) backend. It supports streaming audio responses, handles various audio formats and sample rates, and integrates with the system's cancellation mechanisms. The handler is designed to delegate speech synthesis to an external server while managing turns, sessions, conversation state, and response handling internally [docs/openai-compatible-tts.md:3-5]().

## Architecture and Data Flow

The `OpenAICompatibleTTSHandler` acts as a client to an external OpenAI-compatible TTS server. It receives text input from the Language Model (LLM) stage of the pipeline, sends it to the external server via an HTTP POST request, and then processes the streaming audio response. The audio is then resampled and chunked to match the pipeline's requirements before being sent to the audio output queue.

### Class: `OpenAICompatibleTTSHandler`

The `OpenAICompatibleTTSHandler` [src/speech_to_speech/TTS/openai_compatible_handler.py:600-744]() inherits from `BaseHandler` [src/speech_to_speech/baseHandler.py:24-24]() and implements the core logic for interacting with the OpenAI-compatible TTS API.

**Key responsibilities:**
*   **Initialization and Warmup:** During initialization, it performs a warmup request to the configured external TTS server to validate the connection and configuration [src/speech_to_speech/TTS/openai_compatible_handler.py:629-630](). This ensures that any issues with the endpoint, authentication, model, or voice are caught early [docs/openai-compatible-tts.md:120-122]().
*   **Request Construction:** It constructs the HTTP request payload based on the `TTSInput` message and the handler's configuration, including the model, voice, language, and response format [src/speech_to_speech/TTS/openai_compatible_handler.py:660-676]().
*   **Streaming Audio Processing:** It uses `HttpSpeechOperation` [src/speech_to_speech/TTS/openai_compatible_handler.py:52-52]() to stream audio bytes from the external server.
*   **Resampling and Chunking:** The handler resamples the incoming audio to the pipeline's standard 16 kHz sample rate and converts it to signed 16-bit PCM. It then chunks the audio into fixed-size blocks (default 512 samples) [src/speech_to_speech/TTS/openai_compatible_handler.py:680-700]().
*   **Cancellation Handling:** It integrates with the `CancelScope` [src/speech_to_speech/pipeline/cancel_scope.py:14-14]() to allow for best-effort cancellation of ongoing speech requests, preventing further audio publication locally upon barge-in or session teardown [src/speech_to_speech/TTS/openai_compatible_handler.py:678-679](), [docs/openai-compatible-tts.md:136-138]().
*   **Error Handling:** It catches and sanitizes errors from the HTTP requests, raising `SpeechRequestError` [src/speech_to_speech/TTS/openai_compatible_handler.py:37-38]() for issues like HTTP status errors or timeouts [src/speech_to_speech/TTS/openai_compatible_handler.py:99-99](), [src/speech_to_speech/TTS/openai_compatible_handler.py:162-163]().

### Class: `HttpSpeechOperation`

The `HttpSpeechOperation` class [src/speech_to_speech/TTS/openai_compatible_handler.py:52-52]() manages the lifecycle of a single HTTP speech request and its streaming transport.

**Key responsibilities:**
*   **Asynchronous HTTP Client:** It uses `httpx.AsyncClient` [src/speech_to_speech/TTS/openai_compatible_handler.py:153-153]() to make asynchronous HTTP requests to the TTS endpoint.
*   **Streaming Response Iteration:** The `iter_bytes` method [src/speech_to_speech/TTS/openai_compatible_handler.py:75-75]() provides an iterator over the incoming audio bytes from the HTTP response stream.
*   **Cancellation:** It supports cancellation via an `Event` [src/speech_to_speech/TTS/openai_compatible_handler.py:69-69]() and a `cancel_check` callable [src/speech_to_speech/TTS/openai_compatible_handler.py:75-75](), allowing the operation to be terminated prematurely.
*   **Timeout Management:** It enforces a timeout for the entire speech request [src/speech_to_speech/TTS/openai_compatible_handler.py:95-99]().
*   **Error Normalization:** It normalizes various exceptions into `SpeechRequestError` or `SpeechRequestCancelled` [src/speech_to_speech/TTS/openai_compatible_handler.py:136-137]().

### Diagram: OpenAI-Compatible TTS Handler Data Flow

```mermaid
graph TD
    subgraph "Speech-to-Speech Pipeline"
        LLMOutput[LLM Output (Text)] --> TTSInputMessage(TTSInput Message);
        TTSInputMessage --> OpenAICompatibleTTSHandler;
        OpenAICompatibleTTSHandler --> AudioOutputQueue[Audio Output Queue];
        AudioOutputQueue --> AudioPlayback[Audio Playback];
    end

    subgraph "OpenAICompatibleTTSHandler"
        OpenAICompatibleTTSHandler -- "1. Process TTSInput" --> ConstructPayload[Construct HTTP Payload];
        ConstructPayload -- "2. Create HttpSpeechOperation" --> HttpSpeechOperationInstance(HttpSpeechOperation);
        HttpSpeechOperationInstance -- "3. Stream Audio Bytes" --> AudioBytesStream[Audio Bytes Stream];
        AudioBytesStream -- "4. Resample & Chunk" --> ProcessedAudio[Processed Audio (PCM16, 16kHz, 512-sample chunks)];
        ProcessedAudio -- "5. Enqueue AudioOutput" --> AudioOutputQueue;
        OpenAICompatibleTTSHandler -- "Cancellation Signal" --> HttpSpeechOperationInstance;
    end

    subgraph "External TTS Server"
        HttpSpeechOperationInstance -- "HTTP POST /v1/audio/speech" --> ExternalTTSServer[External TTS Server];
        ExternalTTSServer -- "Streaming Audio Response" --> HttpSpeechOperationInstance;
    end

    style OpenAICompatibleTTSHandler fill:#f9f,stroke:#333,stroke-width:2px
    style HttpSpeechOperationInstance fill:#ccf,stroke:#333,stroke-width:2px
    style ExternalTTSServer fill:#cfc,stroke:#333,stroke-width:2px
```
Sources:
- [src/speech_to_speech/TTS/openai_compatible_handler.py:52-52]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:600-744]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:660-676]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:680-700]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:678-679]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:99-99]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:136-137]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:153-153]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:75-75]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:95-99]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:37-38]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:69-69]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:629-630]()
- [src/speech_to_speech/pipeline/cancel_scope.py:14-14]()
- [src/speech_to_speech/baseHandler.py:24-24]()
- [docs/openai-compatible-tts.md:3-5]()
- [docs/openai-compatible-tts.md:120-122]()
- [docs/openai-compatible-tts.md:136-138]()

## Configuration

The `OpenAICompatibleTTSHandler` is configured using the `OpenAICompatibleTTSHandlerArguments` dataclass [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:6-6](). These arguments are typically passed via CLI flags with the `openai_tts_` prefix.

### Class: `OpenAICompatibleTTSHandlerArguments`

```python
@dataclass
class OpenAICompatibleTTSHandlerArguments:
    """Connection and audio settings for an OpenAI-compatible TTS server."""

    openai_tts_base_url: str = field(
        default="http://localhost:8091/v1",
        metadata={"help": "Base URL of the OpenAI-compatible server, including /v1."},
    )
    openai_tts_api_key: Optional[str] = field(
        default=None,
        metadata={"help": "Optional bearer token. If unset, OPENAI_API_KEY is used when available."},
    )
    openai_tts_model: str = field(
        default="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice",
        metadata={"help": "Model identifier sent to POST /audio/speech."},
    )
    openai_tts_voice: str = field(
        default="aiden",
        metadata={"help": "Voice name sent with speech requests."},
    )
    openai_tts_language: Optional[str] = field(
        default=None,
        metadata={"help": "Optional fixed language value forwarded unchanged with every speech request."},
    )
    openai_tts_task_type: Optional[str] = field(
        default=None,
        metadata={"help": "Optional vLLM-Omni task type such as CustomVoice, VoiceDesign, or Base."},
    )
    openai_tts_instructions: Optional[str] = field(
        default=None,
        metadata={"help": "Optional voice style instructions for compatible servers."},
    )
    openai_tts_response_format: str = field(
        default="pcm",
        metadata={"help": "Audio response format. The adapter currently supports pcm and wav."},
    )
    openai_tts_sample_rate: int = field(
        default=24000,
        metadata={"help": "Sample rate of raw PCM returned by the server. Qwen3-TTS uses 24000."},
    )
    openai_tts_speed: float = field(
        default=1.0,
        metadata={"help": "Speech speed for compatible non-streaming endpoints."},
    )
    openai_tts_stream: bool = field(
        default=False,
        metadata={"help": "Opt in to the vLLM-Omni stream=true extension."},
    )
    openai_tts_timeout: float = field(
        default=300.0,
        metadata={"help": "HTTP request timeout in seconds."},
    )
    openai_tts_blocksize: int = field(
        default=512,
        metadata={"help": "Pipeline output chunk size in 16 kHz samples."},
    )
```
Sources:
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:6-60]()

**Key Configuration Parameters:**
*   `openai_tts_base_url`: The base URL of the OpenAI-compatible TTS server [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:9-12]().
*   `openai_tts_api_key`: An optional bearer token for authentication. If not set, the `OPENAI_API_KEY` environment variable is used [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:13-16]().
*   `openai_tts_model`: The model identifier to be sent to the `/v1/audio/speech` endpoint [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:17-20]().
*   `openai_tts_voice`: The voice name to be used for synthesis [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:21-24]().
*   `openai_tts_language`: An optional fixed language value. The handler does not infer language from the pipeline [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:25-28](), [docs/openai-compatible-tts.md:43-45]().
*   `openai_tts_response_format`: The audio response format (e.g., "pcm", "wav") [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:37-40]().
*   `openai_tts_sample_rate`: The sample rate of the raw PCM returned by the server [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:41-44]().
*   `openai_tts_stream`: A boolean to opt into the vLLM-Omni `stream=true` extension [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:49-52](), [docs/openai-compatible-tts.md:70-71]().
*   `openai_tts_timeout`: HTTP request timeout in seconds [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:53-56]().
*   `openai_tts_blocksize`: The desired output chunk size in 16 kHz samples for the pipeline [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:57-60]().

### Diagram: Configuration Flow

```mermaid
graph TD
    subgraph "User Input"
        CLIArgs[CLI Arguments]
        EnvVars[Environment Variables (e.g., OPENAI_API_KEY)]
    end

    subgraph "Configuration System"
        CLIArgs --> HfArgumentParser[HfArgumentParser];
        EnvVars --> HfArgumentParser;
        HfArgumentParser --> OpenAICompatibleTTSHandlerArguments[OpenAICompatibleTTSHandlerArguments];
    end

    subgraph "TTS Handler Initialization"
        OpenAICompatibleTTSHandlerArguments --> OpenAICompatibleTTSHandler[OpenAICompatibleTTSHandler];
        OpenAICompatibleTTSHandler -- "Warmup Request" --> ExternalTTSServer[External TTS Server];
    end

    style OpenAICompatibleTTSHandlerArguments fill:#ccf,stroke:#333,stroke-width:2px
    style OpenAICompatibleTTSHandler fill:#f9f,stroke:#333,stroke-width:2px
    style ExternalTTSServer fill:#cfc,stroke:#333,stroke-width:2px
```
Sources:
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:9-12]()
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:13-16]()
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:17-20]()
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:21-24]()
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:25-28]()
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:37-40]()
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:41-44]()
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:49-52]()
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:53-56]()
- [src/speech_to_speech/arguments_classes/openai_tts_arguments.py:57-60]()
- [docs/openai-compatible-tts.md:43-45]()
- [docs/openai-compatible-tts.md:70-71]()

## Audio Processing Details

The handler supports raw signed PCM16 and WAV response formats [docs/openai-compatible-tts.md:126-128](). Regardless of the incoming format, the audio is decoded, resampled, and forwarded incrementally.

### Resampling

The `_resample_and_chunk` method [src/speech_to_speech/TTS/openai_compatible_handler.py:400-400]() handles the conversion of the incoming audio stream to the pipeline's required format (16 kHz, signed 16-bit PCM, 512-sample chunks).

**Steps involved:**
1.  **Input Buffer:** Audio chunks from the HTTP stream are accumulated in an input buffer [src/speech_to_speech/TTS/openai_compatible_handler.py:409-410]().
2.  **Resampling:** If the server's sample rate (`self.sample_rate`) differs from the pipeline's `PIPELINE_SAMPLE_RATE` (16 kHz), the audio is resampled using a polyphase FIR filter [src/speech_to_speech/TTS/openai_compatible_handler.py:416-420]().
3.  **Chunking:** The resampled audio is then chunked into `self.blocksize` (default 512) samples [src/speech_to_speech/TTS/openai_compatible_handler.py:422-427]().
4.  **Output:** Each chunk is yielded as a `numpy.ndarray` of `int16` [src/speech_to_speech/TTS/openai_compatible_handler.py:426-427]().

### WAV File Handling

If `openai_tts_response_format` is set to "wav" and `openai_tts_stream` is `False` [docs/openai-compatible-tts.md:127-128](), the handler expects a complete WAV file as the response. The `_decode_wav_stream` method [src/speech_to_speech/TTS/openai_compatible_handler.py:350-350]() is used to parse the WAV header and extract the audio data.

### Playback Buffering

For `speech-to-speech local --tts openai`, a default playback buffer of 196 ms is applied. This buffer helps absorb initial delivery jitter from the external HTTP endpoint, providing smoother playback by holding a small amount of audio before playback begins [docs/openai-compatible-tts.md:80-85](). This is distinct from the TTS handler's internal processing and is managed downstream. The buffer size can be overridden with `--playback-buffer-ms` [docs/openai-compatible-tts.md:98-98]().

Sources:
- [src/speech_to_speech/TTS/openai_compatible_handler.py:400-400]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:409-410]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:416-420]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:422-427]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:426-427]()
- [src/speech_to_speech/TTS/openai_compatible_handler.py:350-350]()
- [docs/openai-compatible-tts.md:80-85]()
- [docs/openai-compatible-tts.md:98-98]()
- [docs/openai-compatible-tts.md:126-128]()
- [docs/openai-compatible-tts.md:127-128]()

## Testing

The `test_openai_tts_handler.py` [tests/test_openai_tts_handler.py:1-1110]() file contains unit tests for the `OpenAICompatibleTTSHandler`. It uses a `_FakeSpeechOperation` [tests/test_openai_tts_handler.py:37-70]() to mock the external HTTP server, allowing for controlled testing of various scenarios, including:
*   Warmup request configuration [tests/test_openai_tts_handler.py:114-148]()
*   HTTP failures during warmup [tests/test_openai_tts_handler.py:150-163]()
*   Streaming and resampling of audio [tests/test_openai_tts_handler.py:165-183]()
*   Cancellation behavior [tests/test_openai_tts_handler.py:209-220]()
*   Error handling [tests/test_openai_tts_handler.py:222-233]()

Sources:
- [tests/test_openai_tts_handler.py:1-1110]()
- [tests/test_openai_tts_handler.py:37-70]()
- [tests/test_openai_tts_handler.py:114-148]()
- [tests/test_openai_tts_handler.py:150-163]()
- [tests/test_openai_tts_handler.py:165-183]()
- [tests/test_openai_tts_handler.py:209-220]()
- [tests/test_openai_tts_handler.py:222-233]()

---

