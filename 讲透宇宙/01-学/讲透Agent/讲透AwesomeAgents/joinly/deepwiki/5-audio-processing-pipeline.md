<!-- source: DeepWiki mcp.deepwiki.com · repo joinly-ai/joinly · page 5 Audio Processing Pipeline · fetched 2026-10-26 -->

# Audio Processing Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [joinly/controllers/speech/default.py](joinly/controllers/speech/default.py)
- [joinly/controllers/transcription/default.py](joinly/controllers/transcription/default.py)
- [joinly/core.py](joinly/core.py)
- [joinly/services/stt/deepgram.py](joinly/services/stt/deepgram.py)
- [joinly/services/stt/whisper.py](joinly/services/stt/whisper.py)
- [joinly/services/tts/deepgram.py](joinly/services/tts/deepgram.py)
- [joinly/services/tts/elevenlabs.py](joinly/services/tts/elevenlabs.py)
- [joinly/session.py](joinly/session.py)
- [joinly/types.py](joinly/types.py)
- [joinly/utils/clock.py](joinly/utils/clock.py)

</details>



The Audio Processing Pipeline is joinly's real-time audio processing system that handles bidirectional audio flow during meeting participation. It manages the complete lifecycle of audio data from meeting capture through transcription to synthetic speech output, coordinating Voice Activity Detection (VAD), Speech-to-Text (STT), and Text-to-Speech (TTS) services.

For detailed implementation of individual audio processing components, see [Transcription Controller](#5.1), [Speech Controller](#5.2), and [Service Providers](#5.3). For browser-based audio device management, see [Browser Meeting Provider](#4.3).

## Architecture Overview

The audio processing pipeline operates as a bidirectional system with separate input and output flows, coordinated by controller components that manage turn-taking and interruption handling.

### Audio Processing Flow

```mermaid
graph TD
    subgraph "Audio Input Flow"
        READER["AudioReader<br/>(audio_reader)"]
        TC["DefaultTranscriptionController"]
        VAD["VAD<br/>(vad)"]
        STT["STT<br/>(stt)"]
        TRANSCRIPT["Transcript"]
    end
    
    subgraph "Audio Output Flow"
        TEXT["Text Input"]
        SC["DefaultSpeechController"]
        TTS["TTS<br/>(tts)"]
        WRITER["AudioWriter<br/>(audio_writer)"]
    end
    
    subgraph "Coordination"
        NSE["no_speech_event<br/>(asyncio.Event)"]
        CLOCK["Clock"]
        EVENTBUS["EventBus"]
    end
    
    READER -->|"read() -> AudioChunk"| TC
    TC -->|"AudioChunk iterator"| VAD
    VAD -->|"stream() -> SpeechWindow"| STT
    STT -->|"stream() -> TranscriptSegment"| TRANSCRIPT
    
    TEXT -->|"speak_text()"| SC
    SC -->|"text chunks"| TTS
    TTS -->|"stream() -> bytes"| WRITER
    
    TC -->|"no speech detected"| NSE
    NSE -->|"is_set() check"| SC
    
    CLOCK -->|"timing"| TC
    CLOCK -->|"timing"| SC
    EVENTBUS -->|"segment/utterance events"| TC
    EVENTBUS -->|"segment events"| SC
```

Sources: [joinly/controllers/transcription/default.py:17-265](), [joinly/controllers/speech/default.py:26-279](), [joinly/core.py:18-297]()

### Component Integration

```mermaid
graph TB
    subgraph "Controller Layer"
        TC["DefaultTranscriptionController<br/>- utterance_tail_seconds: float<br/>- max_stt_tasks: int<br/>- window_queue_size: int"]
        SC["DefaultSpeechController<br/>- prefetch_chunks: int"]
    end
    
    subgraph "Protocol Interfaces"
        AR["AudioReader<br/>- read() -> AudioChunk<br/>- audio_format: AudioFormat"]
        AW["AudioWriter<br/>- write(data: bytes)<br/>- audio_format: AudioFormat<br/>- chunk_size: int"]
        VAD_IF["VAD<br/>- stream(chunks) -> SpeechWindow<br/>- audio_format: AudioFormat"]
        STT_IF["STT<br/>- stream(windows) -> TranscriptSegment<br/>- audio_format: AudioFormat"]
        TTS_IF["TTS<br/>- stream(text) -> bytes<br/>- audio_format: AudioFormat"]
    end
    
    subgraph "Data Types"
        AC["AudioChunk<br/>- data: bytes<br/>- time_ns: int<br/>- speaker: str | None"]
        AF["AudioFormat<br/>- sample_rate: int<br/>- byte_depth: int"]
        SW["SpeechWindow<br/>- data: bytes<br/>- time_ns: int<br/>- is_speech: bool<br/>- speaker: str | None"]
        TS["TranscriptSegment<br/>- text: str<br/>- start: float<br/>- end: float<br/>- speaker: str | None"]
    end
    
    TC --> AR
    TC --> VAD_IF
    TC --> STT_IF
    SC --> AW
    SC --> TTS_IF
    
    AR --> AC
    AC --> AF
    VAD_IF --> SW
    STT_IF --> TS
    AW --> AF
```

Sources: [joinly/controllers/transcription/default.py:24-44](), [joinly/controllers/speech/default.py:33-44](), [joinly/core.py:18-297](), [joinly/types.py:44-87]()

## Audio Format Management

The pipeline handles audio format conversion transparently between components that may operate with different sample rates and bit depths. All audio processing uses PCM format with configurable parameters.

### AudioFormat Type

The `AudioFormat` dataclass standardizes audio properties across the pipeline:

| Property | Type | Description |
|----------|------|-------------|
| `sample_rate` | `int` | Sample rate in Hz (commonly 16000) |
| `byte_depth` | `int` | Bytes per sample (2 for int16, 4 for float32) |

### Format Conversion

Audio format conversion occurs automatically at component boundaries using the utilities in [joinly/utils/audio.py:9-57](). The system supports conversion between 16-bit integer and 32-bit float PCM formats while maintaining the same sample rate.

```mermaid
graph LR
    subgraph "Audio Format Conversion"
        INPUT["Input Audio<br/>AudioFormat A"]
        CONVERT["convert_audio_format()<br/>- numpy conversion<br/>- clip/scale values"]
        OUTPUT["Output Audio<br/>AudioFormat B"]
    end
    
    INPUT -->|"bytes, source_format, target_format"| CONVERT
    CONVERT -->|"converted bytes"| OUTPUT
    
    subgraph "Supported Conversions"
        INT16["16-bit PCM<br/>(byte_depth=2)"]
        FLOAT32["32-bit float PCM<br/>(byte_depth=4)"]
    end
    
    INT16 <-->|"bidirectional"| FLOAT32
```

Sources: [joinly/utils/audio.py:9-71](), [joinly/types.py:19-30]()

## Transcription Flow

The transcription flow processes incoming meeting audio through VAD and STT services, coordinated by the `DefaultTranscriptionController`.

### Transcription Controller Lifecycle

```mermaid
sequenceDiagram
    participant Session as "MeetingSession"
    participant TC as "DefaultTranscriptionController"
    participant VAD as "VAD"
    participant STT as "STT"
    participant Reader as "AudioReader"
    
    Session->>TC: start(clock, transcript, event_bus)
    TC->>TC: create _vad_task = _vad_worker()
    TC->>TC: set _no_speech_event
    
    loop "_vad_worker Loop"
        TC->>Reader: read()
        Reader->>TC: AudioChunk
        TC->>TC: convert_audio_format()
        TC->>VAD: stream(_chunk_iterator())
        VAD->>TC: SpeechWindow
        
        alt "window.is_speech and _window_queue is None"
            TC->>TC: create asyncio.Queue (window_queue_size)
            TC->>TC: create _stt_utterance task
            TC->>TC: clear _no_speech_event
        end
        
        alt "not window.is_speech and tail elapsed"
            TC->>TC: set _no_speech_event
            TC->>TC: put None in window_queue (end marker)
        end
        
        TC->>TC: put window in queue
    end
    
    loop "_stt_utterance Task"
        TC->>STT: stream(_window_iterator())
        STT->>TC: TranscriptSegment
        TC->>TC: transcript.add_segment()
        TC->>TC: _notify("segment")
    end
```

Sources: [joinly/controllers/transcription/default.py:66-265]()

### Speech Window Processing

The transcription controller manages speech detection using configurable timing parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `utterance_tail_seconds` | 0.6 | Silence duration before ending utterance |
| `max_stt_tasks` | 5 | Maximum concurrent STT operations |
| `window_queue_size` | 100 | Buffer size for speech windows |

Sources: [joinly/controllers/transcription/default.py:22-48]()

## Speech Synthesis Flow

The speech synthesis flow converts text to audio output through TTS services, managed by the `DefaultSpeechController` using a producer-consumer pattern with interruption handling.

### Speech Controller Architecture

```mermaid
graph TD
    subgraph "speak_text() Method"
        LOCK["async with self._lock"]
        TG["asyncio.TaskGroup"]
        CHUNK["_chunk_text()<br/>- semchunk.chunkerify<br/>- dynamic chunk size"]
    end
    
    subgraph "Producer-Consumer Pattern"
        QUEUE["asyncio.Queue[bytes | object]<br/>- audio segments<br/>- _CHUNK_END<br/>- _TEXT_END"]
        SEM["asyncio.Semaphore<br/>- prefetch_chunks limit"]
        PROD["_speech_producer()<br/>- TTS.stream() per chunk<br/>- release semaphore"]
        CONS["_speech_consumer()<br/>- write to AudioWriter<br/>- interruption check"]
    end
    
    subgraph "Audio Output"
        BUF["Audio Buffer<br/>- accumulate segments<br/>- format conversion"]
        INT["Interruption Check<br/>- no_speech_event.is_set()<br/>- estimate spoken text"]
        WRITE["AudioWriter.write()<br/>- chunk_size aligned"]
    end
    
    LOCK --> TG
    TG --> CHUNK
    TG --> PROD
    TG --> CONS
    
    CHUNK --> SEM
    PROD --> QUEUE
    QUEUE --> CONS
    SEM --> PROD
    
    CONS --> BUF
    BUF --> INT
    INT --> WRITE
```

Sources: [joinly/controllers/speech/default.py:93-279]()

### Interruption Handling

The speech controller implements interruption logic during audio output to handle natural conversation flow:

| Feature | Implementation |
|---------|----------------|
| **Speech Detection** | Checks `no_speech_event.is_set()` during audio writing |
| **Interrupt Timing** | Checks between `chunk_size` audio writes |
| **Interrupt Behavior** | Raises `SpeechInterruptedError` when speech detected |
| **Recovery** | Estimates spoken text using duration and words-per-second |
| **Transcript Update** | Adds partial segment with "..." suffix on interruption |

Sources: [joinly/controllers/speech/default.py:230-253](), [joinly/controllers/speech/default.py:261-278]()

## Turn-Taking Coordination

The pipeline coordinates turn-taking between transcription and speech synthesis using the `no_speech_event` mechanism.

### Event Coordination Flow

```mermaid
stateDiagram-v2
    [*] --> NoSpeech: "Initial state"
    NoSpeech --> SpeechDetected: "VAD detects speech"
    SpeechDetected --> UtteranceActive: "Create STT task"
    UtteranceActive --> NoSpeech: "Silence > utterance_tail_seconds"
    
    state "NoSpeech" as NS {
        [*] --> EventSet: "no_speech_event.set()"
        EventSet --> SpeechReady: "Speech controller can proceed"
    }
    
    state "SpeechDetected" as SD {
        [*] --> EventClear: "no_speech_event.clear()"
        EventClear --> SpeechBlocked: "Speech controller waits"
    }
    
    note right of NS: "Speech synthesis allowed"
    note right of SD: "Speech synthesis blocked"
```

Sources: [joinly/controllers/transcription/default.py:47-57](), [joinly/controllers/transcription/default.py:134-156](), [joinly/controllers/speech/default.py:252-253]()

## Error Handling and Resource Management

The audio processing pipeline implements comprehensive error handling and resource cleanup through async context managers.

### Resource Lifecycle Management

Both controllers implement proper async context management:

- **Transcription Controller**: Manages VAD worker task, STT task pool, and event state
- **Speech Controller**: Manages worker task, job queue, and TTS resources
- **Audio Devices**: Virtual speaker/microphone lifecycle tied to browser session

### Exception Types

| Exception | Usage |
|-----------|-------|
| `SpeechInterruptedError` | Raised when speech is interrupted by detected speech |
| `IncompatibleAudioFormatError` | Raised for unsupported audio format conversions |
| `RuntimeError` | General pipeline state errors (already started, not initialized) |

Sources: [joinly/types.py:11-17](), [joinly/controllers/speech/default.py:286-293]()

## Performance Characteristics

The audio processing pipeline is designed for real-time operation with configurable performance parameters:

### Latency Management

- **STT Latency**: Tracked and logged with warnings for >1 second delays
- **TTS Streaming**: Chunked text processing to reduce initial latency  
- **Buffer Management**: Queue size limits prevent memory exhaustion
- **Concurrent Processing**: Multiple STT tasks can run simultaneously

### Memory Management

- **Frame Dropping**: Graceful degradation when queues are full
- **Buffer Cleanup**: Proper cleanup of audio buffers and tasks
- **Resource Limits**: Bounded queues and semaphores prevent resource exhaustion

Sources: [joinly/controllers/transcription/default.py:174-183](), [joinly/controllers/transcription/default.py:216-220](), [joinly/controllers/speech/default.py:220-227]()

---

