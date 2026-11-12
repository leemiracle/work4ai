<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/speech-to-speech · extra page Realtime Event Handlers · fetched 2026-10-26 -->

# Realtime Event Handlers

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [scripts/synthetic_conversation_realtime_client.py](scripts/synthetic_conversation_realtime_client.py)
- [src/speech_to_speech/STT/transcription_notifier.py](src/speech_to_speech/STT/transcription_notifier.py)
- [src/speech_to_speech/api/openai_realtime/handlers/audio.py](src/speech_to_speech/api/openai_realtime/handlers/audio.py)
- [src/speech_to_speech/api/openai_realtime/handlers/base.py](src/speech_to_speech/api/openai_realtime/handlers/base.py)
- [src/speech_to_speech/api/openai_realtime/handlers/conversation.py](src/speech_to_speech/api/openai_realtime/handlers/conversation.py)
- [src/speech_to_speech/api/openai_realtime/handlers/response.py](src/speech_to_speech/api/openai_realtime/handlers/response.py)
- [src/speech_to_speech/api/openai_realtime/handlers/session.py](src/speech_to_speech/api/openai_realtime/handlers/session.py)
- [src/speech_to_speech/api/openai_realtime/llm_proxy.py](src/speech_to_speech/api/openai_realtime/llm_proxy.py)
- [src/speech_to_speech/api/openai_realtime/server.py](src/speech_to_speech/api/openai_realtime/server.py)
- [src/speech_to_speech/api/openai_realtime/webrtc_session.py](src/speech_to_speech/api/openai_realtime/webrtc_session.py)
- [src/speech_to_speech/pipeline/log_context.py](src/speech_to_speech/pipeline/log_context.py)
- [tests/openai_realtime/test_webrtc.py](tests/openai_realtime/test_webrtc.py)
- [tests/test_transcription_notifier.py](tests/test_transcription_notifier.py)

</details>



This page details the implementation of event handlers within the `speech_to_speech/api/openai_realtime/handlers/` package. These handlers are crucial for managing the real-time interaction lifecycle in the OpenAI Realtime API emulation, covering aspects from audio ingestion and response generation to conversation state management and session configuration updates. They act as the bridge between the incoming client events and the internal pipeline processing, as well as translating pipeline outputs back into client-facing events.

## RealtimeBaseHandler: Scaffolding for Event Handling

The `RealtimeBaseHandler` class [src/speech_to_speech/api/openai_realtime/handlers/base.py:18-58]() provides the foundational structure for all specific event handlers. It offers common utilities and accessors for connection-specific state, configuration, and queues. Each connection maintains its own `RuntimeConfig` via `ConnState`, which is managed by the `RealtimeService`.

Key methods include:
*   `_queue(self, conn_id: str) -> Queue | None`: Returns the `text_prompt_queue` for a given connection ID [src/speech_to_speech/api/openai_realtime/handlers/base.py:31-32]().
*   `_should_listen(self, conn_id: str) -> ThreadingEvent | None`: Returns the `should_listen` event for a given connection ID [src/speech_to_speech/api/openai_realtime/handlers/base.py:34-35]().
*   `_state(self, conn_id: str) -> ConnState`: Retrieves the `ConnState` object associated with a connection ID [src/speech_to_speech/api/openai_realtime/handlers/base.py:39-40]().
*   `_input_item_id(self, conn_id: str, turn_id: str | None = None, turn_revision: int | None = None) -> str | None`: Resolves the input item ID based on `turn_id` and `turn_revision`, or the current input item ID if not specified [src/speech_to_speech/api/openai_realtime/handlers/base.py:42-52]().
*   `_next_event_id() -> str`: Generates a unique ID for events [src/speech_to_speech/api/openai_realtime/handlers/base.py:54-55]().
*   `make_error(self, message: str, _type: str) -> RealtimeErrorEvent`: Creates a `RealtimeErrorEvent` [src/speech_to_speech/api/openai_realtime/handlers/base.py:57-58]().

Sources:
*   [src/speech_to_speech/api/openai_realtime/handlers/base.py:18-58]()

## ResponseHandler: Managing Response Lifecycle

The `ResponseHandler` [src/speech_to_speech/api/openai_realtime/handlers/response.py:62-154]() is responsible for the complete lifecycle of a response, including creation, cancellation, completion, and ID management. It handles provisional items, rollback mechanisms, prefetch transactions, and out-of-band responses.

### Response Lifecycle

The `_ensure_response` method [src/speech_to_speech/api/openai_realtime/handlers/response.py:67-85]() ensures that a response and an output item exist, creating them if necessary. It manages `current_response_id` and `current_response_key` within the connection state.

The `_end_response` method [src/speech_to_speech/api/openai_realtime/handlers/response.py:88-146]() marks a response as completed or cancelled, updates usage statistics, and clears all associated state variables. It also handles the persistence of successfully completed tool responses for potential late logical completion.

### Provisional Items and Rollback

The handler supports provisional items, which are parts of a response that might be rolled back. This is particularly relevant for speculative generation where parts of a response might be discarded if new input invalidates them. The `_end_response` method explicitly handles discarding tool follow-up prefetches if a response is cancelled [src/speech_to_speech/api/openai_realtime/handlers/response.py:123-125]().

### Prefetch Transactions and Out-of-Band Responses

The `ResponseHandler` interacts with `ResponsePrefetchTransaction` [src/speech_to_speech/pipeline/messages.py:52]() to manage speculative responses. It can determine if a standard `ResponseCreateEvent` can adopt generation from session defaults using `_prefetch_matches` [src/speech_to_speech/api/openai_realtime/handlers/response.py:148-154](). Out-of-band responses are identified by `is_out_of_band` [src/speech_to_speech/utils/utils.py:54](), allowing for responses that do not interrupt the current conversational flow.

### Diagram: Response Lifecycle

```mermaid
graph TD
    subgraph Client
        C[Client Event: response.create] --> RH_ER[_ensure_response]
        C_Cancel[Client Event: speech.started (interrupt)] --> RH_ER_Cancel[finish_response(cancelled)]
    end

    subgraph ResponseHandler
        RH_ER[_ensure_response] --> |"Creates response_id, item_id"| CS_CRID[ConnState.current_response_id]
        CS_CRID --> RH_SR[start_item]
        RH_SR --> CS_CII[ConnState.current_item_id]

        RH_ER_Cancel --> RH_ER_End[_end_response]
        RH_ER_End --> |"Updates usage, clears state"| CS_CRID_Clear[ConnState.current_response_id = None]
        RH_ER_End --> CS_CRK_Clear[ConnState.current_response_key = None]
        RH_ER_End --> CS_CII_Clear[ConnState.current_item_id = None]
    end

    subgraph Pipeline
        P_AOR[AssistantOutputEvent] --> RH_AOR[on_assistant_output_event]
        P_ARD[AssistantResponseDoneEvent] --> RH_ARD[on_assistant_response_done]
        P_RGD[ResponseGenerationDoneEvent] --> RH_RGD[on_response_generation_done]
    end

    subgraph ConnState
        CS_CRID
        CS_CRK[ConnState.current_response_key]
        CS_CII
        CS_CRID_Clear
        CS_CRK_Clear
        CS_CII_Clear
    end

    RH_AOR --> |"Generates ResponseTextDeltaEvent, ResponseAudioDeltaEvent"| Client_Output[Client Output]
    RH_ARD --> |"Generates ResponseAudioDoneEvent"| Client_Output
    RH_RGD --> |"Generates ResponseDoneEvent"| Client_Output
```
Sources:
*   [src/speech_to_speech/api/openai_realtime/handlers/response.py:62-154]()
*   [src/speech_to_speech/pipeline/messages.py:52]()
*   [src/speech_to_speech/utils/utils.py:54]()

## ConversationHandler: Conversation State and Transcript Stabilization

The `ConversationHandler` [src/speech_to_speech/api/openai_realtime/handlers/conversation.py:74-167]() is responsible for injecting conversation items into the LLM context and translating pipeline events into protocol-compliant conversation events. It also plays a key role in transcript stabilization.

### Conversation Item Injection

The `handle_conversation_item_create` method [src/speech_to_speech/api/openai_realtime/handlers/conversation.py:110-144]() processes incoming `ConversationItemCreateEvent`s. It adds text messages or function-call outputs to the LLM chat context. If a model generation is active, items are deferred to prevent fast tool results from overtaking later assistant items.

The `_apply_item` method [src/speech_to_speech/api/openai_realtime/handlers/conversation.py:146-167]() adds a single item to the chat and constructs its `conversation.item.created` event. It handles `ChatItemError` by generating an error event.

### Transcript Stabilization

A crucial function of the `ConversationHandler` is transcript stabilization. This is achieved through the `_stable_transcript_words` static method [src/speech_to_speech/api/openai_realtime/handlers/conversation.py:59-72](), which compares a previous transcription hypothesis with a current one to identify stable words. This prevents rapid, flickering updates to the client's displayed transcript by only committing words that are consistent across multiple hypotheses. The `_transcript_words` helper [src/speech_to_speech/api/openai_realtime/handlers/conversation.py:43-56]() extracts display and comparison forms of words from a transcript.

The `TranscriptionNotifier` [src/speech_to_speech/STT/transcription_notifier.py:26-106]() sits between the STT and LLM stages, emitting protocol-neutral transcription events (`PartialTranscriptionEvent`, `TranscriptionCompletedEvent`, `TranscriptionFailedEvent`) on the `text_output_queue`. The `RealtimeService` consumes these events to update conversation state and create LLM requests.

### Diagram: Conversation and Transcript Flow

```mermaid
graph TD
    subgraph Client
        C_CIC[Client Event: conversation.item.create] --> CH_HCIC[handle_conversation_item_create]
    end

    subgraph ConversationHandler
        CH_HCIC --> |"Adds to LLM context"| LLM_Context[LLM Chat Context]
        CH_HCIC --> |"If in_response, defers"| CS_DI[ConnState.deferred_items]
        CH_HCIC --> CH_AI[_apply_item]
        CH_AI --> |"Generates conversation.item.created"| Client_Output[Client Output]
    end

    subgraph STT Pipeline
        STT_Output[STT Output (PartialTranscription, Transcription, TranscriptionFailure)] --> TN[TranscriptionNotifier]
    end

    subgraph TranscriptionNotifier
        TN --> |"PartialTranscriptionEvent"| TQ_PTE[text_output_queue]
        TN --> |"TranscriptionCompletedEvent"| TQ_TCE[text_output_queue]
        TN --> |"TranscriptionFailedEvent"| TQ_TFE[text_output_queue]
    end

    subgraph RealtimeService
        RS_Consume[Consumes text_output_queue] --> CH_HPTE[handle_partial_transcription]
        RS_Consume --> CH_HTCE[handle_transcription_completed]
        RS_Consume --> CH_HTFE[handle_transcription_failed]
    end

    subgraph ConversationHandler (Internal)
        CH_HPTE --> |"Applies _stable_transcript_words"| CS_CT[ConnState.current_transcript]
        CH_HPTE --> |"Generates ConversationItemInputAudioTranscriptionDeltaEvent"| Client_Output
        CH_HTCE --> |"Generates ConversationItemInputAudioTranscriptionCompletedEvent"| Client_Output
        CH_HTFE --> |"Generates ConversationItemInputAudioTranscriptionFailedEvent"| Client_Output
    end
```
Sources:
*   [src/speech_to_speech/api/openai_realtime/handlers/conversation.py:74-167]()
*   [src/speech_to_speech/api/openai_realtime/handlers/conversation.py:59-72]()
*   [src/speech_to_speech/api/openai_realtime/handlers/conversation.py:43-56]()
*   [src/speech_to_speech/STT/transcription_notifier.py:26-106]()
*   [tests/test_transcription_notifier.py:27-43]()

## AudioHandler: Audio Ingestion and Resampling

The `AudioHandler` [src/speech_to_speech/api/openai_realtime/handlers/audio.py:32-174]() manages the decoding, resampling, and chunking of inbound audio, as well as the encoding of outbound audio.

### Inbound Audio Processing

The `handle_audio_append` method [src/speech_to_speech/api/openai_realtime/handlers/audio.py:105-120]() decodes base64-encoded audio from `InputAudioBufferAppendEvent`s. It then calls `append_pcm` [src/speech_to_speech/api/openai_realtime/handlers/audio.py:122-149]() to resample the raw PCM16 audio to the pipeline's sample rate (16kHz) and split it into 512-sample chunks. This method is shared by both WebSocket and WebRTC transports. The `PcmResampler` class [src/speech_to_speech/api/openai_realtime/webrtc_session.py:72-98]() handles stateful resampling and downmixing of multi-channel audio to mono.

The `handle_audio_commit` method [src/speech_to_speech/api/openai_realtime/handlers/audio.py:151-162]() commits the audio buffer, returning an error if the buffer is empty.

### Outbound Audio Handling

The `PipelineAudioTrack` [src/speech_to_speech/api/openai_realtime/webrtc_session.py:101-155]() is used for outbound audio in WebRTC. It paces the delivery of 20ms, 48kHz frames from a PCM buffer, emitting silence if the buffer is empty to maintain a continuous RTP stream. The `clear()` method allows dropping unplayed audio, which is essential for barge-in scenarios.

### Speech Events

The `on_speech_started` method [src/speech_to_speech/api/openai_realtime/handlers/audio.py:165-174]() handles `SpeechStartedEvent`s from the VAD. If interrupt response is enabled, it cancels any active response and starts a new input item.

Sources:
*   [src/speech_to_speech/api/openai_realtime/handlers/audio.py:32-174]()
*   [src/speech_to_speech/api/openai_realtime/webrtc_session.py:72-98]()
*   [src/speech_to_speech/api/openai_realtime/webrtc_session.py:101-155]()
*   [tests/openai_realtime/test_webrtc.py:122-144]()

## SessionHandler: Session Configuration and RuntimeConfig Updates

The `SessionHandler` [src/speech_to_speech/api/openai_realtime/handlers/session.py:21-80]() manages the session lifecycle, including applying configuration updates and generating session-related events.

### Session Updates

The `handle_session_update` method [src/speech_to_speech/api/openai_realtime/handlers/session.py:24-53]() applies configuration changes specified in a `SessionUpdateEvent`. It currently only supports the 'realtime' session type and deep-merges incoming fields into the existing session configuration to preserve previously set values.

### RuntimeConfig Updates

The `ConnState` object for each connection holds a `runtime_config` attribute, which is an instance of `RuntimeConfig`. The `handle_session_update` method directly modifies this `runtime_config` by applying the session update [src/speech_to_speech/api/openai_realtime/handlers/session.py:47-51](). This ensures that session-specific settings, such as the model to use, are dynamically updated during the conversation.

### Session Events

The `build_session_created` [src/speech_to_speech/api/openai_realtime/handlers/session.py:55-66]() and `build_session_updated` [src/speech_to_speech/api/openai_realtime/handlers/session.py:68-80]() methods construct `SessionCreatedEvent` and `SessionUpdatedEvent` respectively, populating them with the current session configuration. These events are sent to the client to acknowledge session state changes.

Sources:
*   [src/speech_to_speech/api/openai_realtime/handlers/session.py:21-80]()
*   [src/speech_to_speech/api/openai_realtime/handlers/session.py:24-53]()
*   [src/speech_to_speech/api/openai_realtime/handlers/session.py:47-51]()
*   [src/speech_to_speech/api/openai_realtime/handlers/session.py:55-66]()
*   [src/speech_to_speech/api/openai_realtime/handlers/session.py:68-80]()

---

