# Skeleton: pipecat（51 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 11KB | 3 | ~3 | 22 |
| 2 | Getting Started | L214 | 14KB | 3 | ~18 | 28 |
| 3 | Core Architecture | L508 | 13KB | 3 | ~3 | 16 |
| 4 | Frame System and Processing | L742 | 16KB | 6 | ~11 | 16 |
| 5 | Pipeline Architecture | L1091 | 11KB | 4 | ~1 | 16 |
| 6 | Frame Processors | L1341 | 11KB | 2 | ~3 | 23 |
| 7 | Pipeline Task and Execution | L1542 | 12KB | 3 | ~5 | 21 |
| 8 | Transport I/O Architecture | L1742 | 14KB | 3 | ~6 | 21 |
| 9 | Context System | L2026 | 13KB | 2 | ~5 | 20 |
| 10 | Context Aggregators | L2257 | 20KB | 6 | ~10 | 20 |
| 11 | Turn Detection and User Idle | L2638 | 15KB | 2 | ~6 | 26 |
| 12 | Interruption Handling | L2884 | 14KB | 3 | ~4 | 19 |
| 13 | Observer System and Monitoring | L3150 | 12KB | 3 | ~2 | 15 |
| 14 | RTVI Protocol | L3357 | 12KB | 3 | ~4 | 20 |
| 15 | AI Service Integrations | L3592 | 10KB | 2 | ~2 | 16 |
| 16 | Service Architecture and Adapters | L3777 | 11KB | 4 | ~2 | 19 |
| 17 | Large Language Models | L4022 | 15KB | 2 | ~2 | 35 |
| 18 | Text-to-Speech Services | L4287 | 12KB | 1 | ~2 | 34 |
| 19 | Speech-to-Text Services | L4494 | 15KB | 2 | ~3 | 33 |
| 20 | Speech-to-Speech Services | L4790 | 11KB | 2 | ~4 | 17 |
| 21 | OpenAI Realtime API | L4969 | 16KB | 2 | ~6 | 15 |
| 22 | Google Gemini Live | L5228 | 12KB | 2 | ~1 | 16 |
| 23 | AWS Nova Sonic | L5451 | 12KB | 2 | ~3 | 18 |
| 24 | xAI Grok Realtime, Ultravox, and Inworld Realtime | L5682 | 11KB | 3 | ~3 | 18 |
| 25 | Vision and Image Services | L5869 | 12KB | 3 | ~7 | 7 |
| 26 | Transport Layer | L6095 | 15KB | 2 | ~18 | 21 |
| 27 | Daily Transport | L6345 | 16KB | 4 | ~14 | 19 |
| 28 | LiveKit Transport | L6766 | 12KB | 3 | ~9 | 10 |
| 29 | WebSocket Transports | L7056 | 13KB | 2 | ~4 | 23 |
| 30 | Telephony and Serializers | L7293 | 13KB | 3 | ~4 | 22 |
| 31 | Local, Test, and MOQ Transports | L7532 | 8KB | 2 | ~2 | 25 |
| 32 | Audio and Video Processing | L7711 | 11KB | 3 | ~5 | 13 |
| 33 | Voice Activity Detection | L7932 | 11KB | 3 | ~2 | 27 |
| 34 | Audio Filters and Enhancement | L8150 | 12KB | 3 | ~9 | 20 |
| 35 | Video Processing | L8396 | 11KB | 3 | ~2 | 11 |
| 36 | Development Tools | L8604 | 11KB | 3 | ~2 | 28 |
| 37 | Pipeline Runner and Development Patterns | L8850 | 13KB | 3 | ~2 | 29 |
| 38 | Testing and Evaluation Framework | L9080 | 12KB | 2 | ~5 | 34 |
| 39 | Client SDKs and Tools | L9326 | 13KB | 3 | ~5 | 28 |
| 40 | Advanced Topics | L9532 | 12KB | 3 | ~3 | 21 |
| 41 | Function Calling and Tool Use | L9754 | 15KB | 2 | ~1 | 22 |
| 42 | Building Natural Conversations | L9965 | 14KB | 2 | ~1 | 24 |
| 43 | Multi-Worker Framework | L10198 | 10KB | 2 | ~2 | 31 |
| 44 | Worker Architecture and Bus | L10360 | 10KB | 2 | ~1 | 25 |
| 45 | Worker Types and Patterns | L10547 | 12KB | 2 | ~2 | 22 |
| 46 | Custom Processors and Extensions | L10721 | 13KB | 3 | ~3 | 18 |
| 47 | Observability, Metrics, and Tracing | L10944 | 16KB | 3 | ~3 | 19 |
| 48 | Memory and Persistent Context | L11264 | 11KB | 3 | ~4 | 8 |
| 49 | Conversation Flows | L11465 | 10KB | 2 | ~1 | 27 |
| 50 | Migration Guides and Deprecated APIs | L11643 | 13KB | 3 | ~6 | 28 |
| 51 | Glossary | L11892 | 17KB | 3 | ~0 | 38 |


## · Overview  (L6)
  源文件: CHANGELOG.md, README.md, env.example, examples/function-calling/function-calling-baseten.py, pyproject.toml, src/pipecat/cli/registry/_configs.py, src/pipecat/cli/registry/_imports.py, src/pipecat/cli/registry/service_metadata.py, src/pipecat/cli/templates/server/env.example.jinja2, src/pipecat/frames/frames.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_response.py
  Purpose and Scope
  What is Pipecat?
  Architecture Philosophy
    · Frame-Based Processing Pipeline
    · Multi-Worker Framework
    · Processor Linking and Frame Flow
  Key Capabilities
    · AI Service Integrations
    · Transport Layer Abstraction
    · Real-Time Conversational Features

## · Getting Started  (L214)
  源文件: MANIFEST.in, README.md, env.example, examples/function-calling/function-calling-baseten.py, pyproject.toml, src/pipecat/cli/__init__.py, src/pipecat/cli/agent_templates/AGENTS.md, src/pipecat/cli/agent_templates/CLAUDE.md, src/pipecat/cli/agent_templates/GETTING_STARTED.md, src/pipecat/cli/commands/__init__.py, src/pipecat/cli/commands/init.py, src/pipecat/cli/config_validator.py
  Installation
    · Core Dependencies
    · Optional Extras
  Environment Variable Configuration
  How Pipecat Pipelines Work
  Examples Directory Structure
  Anatomy of a Bot Entry Point
  The Pipecat CLI
    · Project Initialization (`pipecat init`)
    · Quickstart Scaffolding
    · Running Evaluations (`pipecat eval`)
  What to Read Next

## · Core Architecture  (L508)
  源文件: CHANGELOG.md, src/pipecat/frames/frames.py, src/pipecat/pipeline/base_pipeline.py, src/pipecat/pipeline/parallel_pipeline.py, src/pipecat/pipeline/pipeline.py, src/pipecat/pipeline/sync_parallel_pipeline.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py, src/pipecat/processors/frame_processor.py, src/pipecat/services/llm_service.py, src/pipecat/transports/base_input.py
  Architectural Principles
  Frame System Overview
    · Frame Type Hierarchy
  FrameProcessor and Pipeline Model
    · FrameProcessor Architecture
    · Pipeline Composition
  WorkerRunner and PipelineWorker
  Transport I/O Architecture
  Universal Context System
  Turn Detection and Interruption
  Observability and RTVI

## · Frame System and Processing  (L742)
  源文件: CHANGELOG.md, LICENSE, src/pipecat/frames/frames.proto, src/pipecat/frames/frames.py, src/pipecat/frames/protobufs/frames_pb2.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py, src/pipecat/processors/frame_processor.py, src/pipecat/services/llm_service.py, src/pipecat/transports/base_input.py, src/pipecat/transports/base_output.py
  Purpose and Scope
  Frame Type Hierarchy
    · Hierarchy Diagram
    · Frame Category Semantics
    · UninterruptibleFrame Mixin
  Frame Base Properties
  Frame Direction and Flow
    · FrameDirection Enum
    · Directional Flow Diagram
  Frame Processing Architecture
    · Priority Queue Implementation
  Multi-Worker Renames (Post-1.3.0)
  Pipeline Draining and Flushing
  Specialized Frame Types
    · Word-Level Progress and Highlighting (1.4.0)
    · Audio Buffer Control (1.5.0)
    · Audio Token Usage (1.6.0)
    · TTS Ordering Fixes (Post-1.6.0)
  Frame Processing Lifecycle
    · Event Handlers
    · Pause and Resume
  Common Frame Types
    · Media Frames
    · LLM and Text Frames
  Serialization and Network Transport
  Interruption and Flow Control

## · Pipeline Architecture  (L1091)
  源文件: CHANGELOG.md, src/pipecat/frames/frames.py, src/pipecat/pipeline/base_pipeline.py, src/pipecat/pipeline/parallel_pipeline.py, src/pipecat/pipeline/pipeline.py, src/pipecat/pipeline/sync_parallel_pipeline.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py, src/pipecat/processors/frame_processor.py, src/pipecat/services/llm_service.py, src/pipecat/transports/base_input.py
  Purpose and Scope
  Overview
    · Pipeline Types
  Basic Pipeline Structure
    · Pipeline Class
  PipelineSource and PipelineSink
    · PipelineSource
    · PipelineSink
  Frame Flow Direction
  ParallelPipeline
    · Architecture
    · Key Features
  SyncParallelPipeline
    · Architecture
    · Synchronization Mechanism
  Pipeline Integration
    · PipelineWorker Integration
    · Nesting Pipelines
  Setup and Cleanup
    · Setup Phase
    · Cleanup Phase

## · Frame Processors  (L1341)
  源文件: CHANGELOG.md, scripts/fix-ruff-and-typecheck.sh, src/pipecat/extensions/voicemail/voicemail_detector.py, src/pipecat/frames/frames.py, src/pipecat/pipeline/llm_switcher.py, src/pipecat/pipeline/service_switcher.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/dtmf_aggregator.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py, src/pipecat/processors/filters/frame_filter.py, src/pipecat/processors/filters/function_filter.py
  The FrameProcessor Base Class
  Frame Processing Architecture
    · Processor Internal Data Flow
  Frame Processor Queue: Priority Handling
  The process_frame Implementation
    · Implementation Pattern
  Bidirectional Flow and Pushing
    · Broadcasting
  Common Processor Patterns
    · 1. Filters
    · 2. Aggregators
    · 3. Transports as Processors
    · 4. Switchers
  Lifecycle: Setup and Cleanup

## · Pipeline Task and Execution  (L1542)
  源文件: examples/observability/observability-heartbeats.py, scripts/fix-ruff-and-typecheck.sh, src/pipecat/pipeline/llm_switcher.py, src/pipecat/pipeline/runner.py, src/pipecat/pipeline/service_switcher.py, src/pipecat/pipeline/worker.py, src/pipecat/processors/filters/frame_filter.py, src/pipecat/processors/filters/function_filter.py, src/pipecat/processors/filters/null_filter.py, src/pipecat/processors/filters/wake_check_filter.py, src/pipecat/tests/utils.py, src/pipecat/utils/startup.py
  Overview
    · Execution Architecture
  PipelineWorker
    · Internal Pipeline Structure
    · Constructor Parameters
    · Event Handlers
  Shared Application Resources (app_resources)
    · Accessing Resources
  WorkerRunner (formerly PipelineRunner)
    · Shared Task Management
  Service Switching
    · ServiceSwitcher and LLMSwitcher
  Pipeline Lifecycle and Event Handlers
    · Terminal Frames
  Heartbeats and Idle Detection
    · Heartbeats
    · Idle Detection

## · Transport I/O Architecture  (L1742)
  源文件: CHANGELOG.md, src/pipecat/frames/frames.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py, src/pipecat/processors/frame_processor.py, src/pipecat/services/llm_service.py, src/pipecat/transports/base_input.py, src/pipecat/transports/base_output.py, src/pipecat/transports/base_transport.py, src/pipecat/transports/daily/transport.py, src/pipecat/transports/livekit/transport.py
  Transport Abstraction Layer
    · Entity Relationship Diagram
    · BaseTransport
    · TransportParams
  Input Transport Architecture
    · Audio Processing Flow
    · Key Methods
  Output Transport Architecture
    · MediaSender Architecture
  WebSocket Server Reference Counting
  VAD Integration
  Media Serializers

## · Context System  (L2026)
  源文件: CHANGELOG.md, src/pipecat/adapters/base_llm_adapter.py, src/pipecat/adapters/services/anthropic_adapter.py, src/pipecat/adapters/services/bedrock_adapter.py, src/pipecat/adapters/services/gemini_adapter.py, src/pipecat/adapters/services/open_ai_adapter.py, src/pipecat/adapters/services/perplexity_adapter.py, src/pipecat/frames/frames.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_context.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py
  Overview
  LLMContext Architecture
    · Context Translation Flow
  Message Management
    · Message Types
    · Core Operations
  The Adapter Pattern (`BaseLLMAdapter`)
    · Key Adapter Functions
    · Implementation and Error Handling
  Safe Context Editing (`LLMMessagesTransformFrame`)
  Assistant Turn and STT Carryover
  Data Flow: Context to Provider
    · Code Entity Interaction
  Tool Integration and Serialization
  Migration from Provider-Specific Contexts
    · Migration Mapping

## · Context Aggregators  (L2257)
  源文件: CHANGELOG.md, src/pipecat/adapters/base_llm_adapter.py, src/pipecat/adapters/services/anthropic_adapter.py, src/pipecat/adapters/services/bedrock_adapter.py, src/pipecat/adapters/services/gemini_adapter.py, src/pipecat/adapters/services/open_ai_adapter.py, src/pipecat/adapters/services/perplexity_adapter.py, src/pipecat/frames/frames.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_context.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py
  Architecture Overview
  LLMContextAggregator Base Class
  LLMUserAggregator
    · Core Functionality
    · Frame Processing Flow
    · User Mute Strategies
    · Turn Completion Filtering
  LLMAssistantAggregator
    · Core Functionality
    · Function Call Handling
    · Thought Handling
    · Context Summarization
  Universal Aggregator Pair
    · Realtime Service Mode
    · Tool Change Messages
  Configuration Parameters
    · LLMUserAggregatorParams
    · LLMAssistantAggregatorParams
  Migration from Deprecated APIs

## · Turn Detection and User Idle  (L2638)
  源文件: changelog/5007.fixed.2.md, changelog/5007.fixed.md, src/pipecat/audio/filters/koala_filter.py, src/pipecat/audio/turn/base_turn_analyzer.py, src/pipecat/audio/turn/smart_turn/__init__.py, src/pipecat/audio/turn/smart_turn/_whisper_features.py, src/pipecat/audio/turn/smart_turn/base_smart_turn.py, src/pipecat/audio/turn/smart_turn/http_smart_turn.py, src/pipecat/audio/turn/smart_turn/local_coreml_smart_turn.py, src/pipecat/audio/turn/smart_turn/local_smart_turn_v2.py, src/pipecat/audio/turn/smart_turn/local_smart_turn_v3.py, src/pipecat/turns/user_idle_controller.py
  Turn Detection Architecture
  Voice Activity Detection (VAD)
  User Turn Strategies
    · UserTurnController
    · Turn Start Strategies
    · Turn Stop Strategies
    · Decoupling Transcripts: `wait_for_transcript`
  Smart Turn Analyzers
    · LocalSmartTurnAnalyzerV3
    · BaseSmartTurn
  User Turn Completion Mixin
  STT Latency and Metadata
  User Idle Detection
  User Mute Strategies

## · Interruption Handling  (L2884)
  源文件: CHANGELOG.md, src/pipecat/frames/frames.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py, src/pipecat/processors/frame_processor.py, src/pipecat/services/llm_service.py, src/pipecat/services/stt_service.py, src/pipecat/services/tts_service.py, src/pipecat/transports/base_input.py, src/pipecat/transports/base_output.py, src/pipecat/transports/base_transport.py
  Purpose and Scope
  Core Interruption Concepts
    · InterruptionFrame
    · UninterruptibleFrame Mixin
    · Frame Priority System
  Interruption Propagation Flow
  Broadcasting Interruptions
    · The broadcast_interruption() Method
  Frame Processing During Interruptions
    · Queue Behavior
    · Task Cancellation
    · Pipeline Draining
  Service-Specific Interruption Handling
    · LLM and Aggregator Services
    · TTS Services and Deadlock Prevention
    · Transport Layer (BaseOutputTransport)
  Interruption Scenario: User Interrupts Bot
  Related Frame Types

## · Observer System and Monitoring  (L3150)
  源文件: src/pipecat/observers/__init__.py, src/pipecat/observers/base_observer.py, src/pipecat/observers/loggers/__init__.py, src/pipecat/observers/loggers/debug_log_observer.py, src/pipecat/observers/loggers/llm_log_observer.py, src/pipecat/observers/loggers/transcription_log_observer.py, src/pipecat/observers/startup_timing_observer.py, src/pipecat/observers/turn_tracking_observer.py, src/pipecat/observers/user_bot_latency_observer.py, src/pipecat/services/google/rtvi.py, src/pipecat/utils/tracing/tracing_context.py, src/pipecat/utils/tracing/turn_trace_observer.py
  Purpose and Scope
  Observer Pattern Architecture
    · Natural Language to Code Entity Mapping: Monitoring Infrastructure
    · Data Flow: Frame Event to Observers
  Core Observer Classes
    · BaseObserver
    · TurnTrackingObserver
    · UserBotLatencyObserver
    · StartupTimingObserver
    · TurnTraceObserver
    · Specialized Log Observers
  Metrics Collection
    · Latency Breakdown Models
    · Natural Language to Code Entity Mapping: Tracing Context
  Monitoring Lifecycle and Execution
    · Event Handlers

## · RTVI Protocol  (L3357)
  源文件: CHANGELOG.md, src/pipecat/frames/frames.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py, src/pipecat/processors/frame_processor.py, src/pipecat/processors/frameworks/rtvi/__init__.py, src/pipecat/processors/frameworks/rtvi/frames.py, src/pipecat/processors/frameworks/rtvi/models.py, src/pipecat/processors/frameworks/rtvi/observer.py, src/pipecat/processors/frameworks/rtvi/processor.py, src/pipecat/services/llm_service.py
  Purpose and Scope
  Protocol Overview
    · RTVI in the Pipeline Architecture
  Core Components
    · RTVIProcessor
    · RTVIObserver
    · RTVIObserverParams
  RTVI 2.0.0 & 2.1.0 Protocol Upgrades
    · Bot Output Message Enhancements (2.0.0)
    · Breaking Changes in 2.1.0 (Pipecat 1.6.0)
  UI Agent Protocol
  Lifecycle Management
    · Client Ready Flow
    · Bot Interruption
  Message Structure
    · Base Message Format

## · AI Service Integrations  (L3592)
  源文件: COMMUNITY_INTEGRATIONS.md, changelog/5103.fixed.md, src/pipecat/services/ai_service.py, src/pipecat/services/nvidia/__init__.py, src/pipecat/services/openai/_constants.py, src/pipecat/services/openai/realtime/events.py, src/pipecat/services/settings.py, src/pipecat/transports/daily/utils.py, tests/test_elevenlabs_tts.py, tests/test_settings.py, Service Architecture and Adapters, Large Language Models
  Module Organization
  Service Type Hierarchy
  The Adapter System
  WebSocket Service and Reconnection
  Supported Provider Landscape
    · Large Language Models
    · Speech and Vision

## · Service Architecture and Adapters  (L3777)
  源文件: changelog/5103.fixed.md, src/pipecat/adapters/schemas/direct_function.py, src/pipecat/adapters/schemas/function_schema.py, src/pipecat/adapters/schemas/tools_schema.py, src/pipecat/services/inworld/realtime/__init__.py, src/pipecat/services/inworld/realtime/events.py, src/pipecat/services/openai/_constants.py, src/pipecat/services/openai/realtime/events.py, src/pipecat/services/settings.py, src/pipecat/services/websocket_service.py, src/pipecat/transports/daily/utils.py, src/pipecat/utils/network.py
  Purpose and Scope
  Base Service Architecture
  Settings System and Deltas
    · Store vs. Delta Modes
    · The NOT_GIVEN Sentinel
  Universal LLM Context and Adapters
    · Tools and Function Calling
  Provider-Specific Adapters
    · BaseLLMAdapter Interface
    · Comparison of Adapter Transformations
  WebsocketService and Reconnection
    · Reconnection Behavior
  Assistant Turn Propagation
  Tools Schema and Custom Tools

## · Large Language Models  (L4022)
  源文件: README.md, env.example, examples/function-calling/function-calling-baseten.py, examples/thinking/thinking-functions-openai-responses.py, examples/thinking/thinking-openai-responses-http.py, examples/thinking/thinking-openai-responses.py, pyproject.toml, src/pipecat/adapters/services/open_ai_responses_adapter.py, src/pipecat/cli/registry/_configs.py, src/pipecat/cli/registry/_imports.py, src/pipecat/cli/registry/service_metadata.py, src/pipecat/cli/templates/server/env.example.jinja2
  LLMService Architecture
    · Class Hierarchy
    · Adapter System
  Available LLM Services
    · OpenAI and Compatible Services
    · Anthropic Claude
    · Google Gemini
    · AWS Bedrock
    · OpenAI Responses API
    · Other Standard Integrations
  Function Calling and Tool Use
    · Function Registration
    · MCP Integration
  Context Management
    · Universal LLMContext
  Summary of Recent Changes

## · Text-to-Speech Services  (L4287)
  源文件: changelog/4791.fixed.md, examples/features/features-text-transforms.py, examples/features/features-voice-formatter.py, src/pipecat/services/asyncai/tts.py, src/pipecat/services/aws/tts.py, src/pipecat/services/azure/tts.py, src/pipecat/services/cartesia/tts.py, src/pipecat/services/cartesia/turns/__init__.py, src/pipecat/services/cartesia/turns/stt.py, src/pipecat/services/deepgram/flux/base.py, src/pipecat/services/deepgram/flux/sagemaker/__init__.py, src/pipecat/services/deepgram/flux/sagemaker/stt.py
  Purpose and Scope
  Base Service Architecture
    · Class Hierarchy
    · TTSService Base Class
    · WordTTSService and Ordering
  Text Processing and Transforms
    · VoiceFormatter and Transforms
  Provider Implementations
    · DeepgramFluxTTSService (New in 1.6.0)
    · ElevenLabsTTSService
    · GeminiTTSService
    · NvidiaTTSService
    · XAITTSService
    · SarvamTTSService
    · SmallestTTSService

## · Speech-to-Text Services  (L4494)
  源文件: changelog/4791.fixed.md, changelog/5055.added.md, src/pipecat/metrics/metrics.py, src/pipecat/observers/loggers/metrics_log_observer.py, src/pipecat/processors/metrics/frame_processor_metrics.py, src/pipecat/processors/metrics/sentry.py, src/pipecat/services/assemblyai/stt.py, src/pipecat/services/aws/stt.py, src/pipecat/services/azure/stt.py, src/pipecat/services/cartesia/stt.py, src/pipecat/services/cartesia/turns/__init__.py, src/pipecat/services/cartesia/turns/stt.py
  STT Service Architecture
    · Base STTService Class
    · WebsocketSTTService
    · SegmentedSTTService
  Audio Frame Flow
  Provider Implementations
    · AssemblyAI
    · Deepgram
    · Deepgram Flux
    · Together AI
    · Soniox
    · Nvidia STT
    · Azure STT
    · Moonshine
  STT Usage Metrics
  Server-Side Turn Detection
  Context Carryover

## · Speech-to-Speech Services  (L4790)
  源文件: examples/realtime/realtime-azure.py, examples/realtime/realtime-gemini-live-locally-driven-turns.py, examples/realtime/realtime-grok-locally-driven-turns.py, examples/realtime/realtime-inworld-locally-driven-turns.py, examples/realtime/realtime-openai-locally-driven-turns.py, examples/realtime/realtime-openai-text.py, examples/realtime/realtime-openai.py, src/pipecat/services/aws/nova_sonic/llm.py, src/pipecat/services/google/gemini_live/llm.py, src/pipecat/services/inworld/realtime/llm.py, src/pipecat/services/openai/realtime/llm.py, src/pipecat/services/ultravox/llm.py
  Architecture Overview
    · Traditional vs. Speech-to-Speech Pipeline
    · Core Components
  Available Services
    · Service Entity Relationship
  Common Features
    · Bidirectional Audio Handling
    · Audio Token Usage (1.6.0)
    · Locally-Driven Turns
    · Tool Handling and Double-Encoding Fix (1.6.0)
  Context and Aggregation
    · Universal Context
    · Context Aggregator Pairs
  Namespace Migrations (Legacy Support)

## · OpenAI Realtime API  (L4969)
  源文件: examples/realtime/realtime-azure.py, examples/realtime/realtime-gemini-live-locally-driven-turns.py, examples/realtime/realtime-grok-locally-driven-turns.py, examples/realtime/realtime-inworld-locally-driven-turns.py, examples/realtime/realtime-openai-locally-driven-turns.py, examples/realtime/realtime-openai-text.py, examples/realtime/realtime-openai.py, src/pipecat/services/aws/nova_sonic/llm.py, src/pipecat/services/google/gemini_live/llm.py, src/pipecat/services/inworld/realtime/llm.py, src/pipecat/services/openai/realtime/llm.py, src/pipecat/services/ultravox/llm.py
  Service Architecture
  WebSocket Communication Architecture
  Session Configuration
  Event System and Truncation
  Legacy and Deprecated Shims

## · Google Gemini Live  (L5228)
  源文件: src/pipecat/runner/daily.py, src/pipecat/services/aws/nova_sonic/llm.py, src/pipecat/services/google/gemini_live/llm.py, src/pipecat/services/google/gemini_live/vertex/__init__.py, src/pipecat/services/google/gemini_live/vertex/llm.py, src/pipecat/services/inworld/realtime/llm.py, src/pipecat/services/openai/realtime/llm.py, src/pipecat/services/ultravox/llm.py, src/pipecat/services/xai/realtime/llm.py, src/pipecat/transports/smallwebrtc/connection.py, src/pipecat/transports/smallwebrtc/request_handler.py, src/pipecat/transports/whatsapp/__init__.py
  Overview
  Namespace Migration and Deprecation
  Service Architecture
    · System Data Flow
  Key Implementation Details
    · Audio and Video Handling
    · Token Usage and Metrics (1.6.0)
    · Context Window Compression
    · Affective Dialog and Thinking
    · Function Calling and Search
    · Function Call Execution Flow
  Vertex AI Integration
  VAD and Sensitivity
  Example Usage
    · Basic Conversation
    · Vertex AI Example

## · AWS Nova Sonic  (L5451)
  源文件: src/pipecat/services/aws/__init__.py, src/pipecat/services/aws/agent_core.py, src/pipecat/services/aws/nova_sonic/__init__.py, src/pipecat/services/aws/nova_sonic/llm.py, src/pipecat/services/aws/nova_sonic/ready.wav, src/pipecat/services/aws/sagemaker/__init__.py, src/pipecat/services/aws/sagemaker/bidi_client.py, src/pipecat/services/aws/utils.py, src/pipecat/services/google/gemini_live/llm.py, src/pipecat/services/inworld/realtime/llm.py, src/pipecat/services/nvidia/sagemaker/__init__.py, src/pipecat/services/nvidia/sagemaker/stt.py
  Purpose and Scope
  Overview
    · Key Capabilities
  Service Architecture
    · Data Flow Diagram
  Service Configuration
    · Settings and Parameters
    · Audio Configuration
  Credential Resolution
  Dependency Changes
  Context Management
  Bidirectional Audio Streaming
    · Content Stage Tracking
  Function Calling and Interruption
    · Async Function Calls
    · Server-Side Interruption Fix
    · Endpointing Sensitivity
  Namespace Migration

## · xAI Grok Realtime, Ultravox, and Inworld Realtime  (L5682)
  源文件: examples/realtime/realtime-aws-nova-sonic.py, examples/realtime/realtime-gemini-live.py, examples/realtime/realtime-grok-async-tool.py, examples/realtime/realtime-grok.py, examples/realtime/realtime-inworld.py, examples/realtime/realtime-ultravox-async-tool.py, examples/realtime/realtime-ultravox-text.py, examples/realtime/realtime-ultravox.py, examples/update-settings/llm/llm-azure-realtime.py, examples/update-settings/llm/llm-grok-realtime.py, examples/update-settings/llm/llm-openai-realtime.py, src/pipecat/adapters/services/aws_nova_sonic_adapter.py
  xAI Grok Realtime
    · Namespace and Adapter
    · Implementation Details
    · Built-in Tools
    · Tool Result Encoding Fix (1.6.0)
    · Locally Driven Turns
  Ultravox Realtime
    · Integration Patterns
    · Async Tool Result Fix
    · Service Teardown
  Inworld Realtime
    · Core Components
    · Tool Result Encoding Fix (1.6.0)
    · Locally Driven Turns
  Comparison of Real-time Capabilities

## · Vision and Image Services  (L5869)
  源文件: src/pipecat/services/azure/image.py, src/pipecat/services/fal/image.py, src/pipecat/services/google/image.py, src/pipecat/services/image_service.py, src/pipecat/services/moondream/vision.py, src/pipecat/services/openai/image.py, src/pipecat/services/vision_service.py
  Overview
  Image Frame Type Hierarchy
    · Code Entity Association: Image Frames
  Vision Analysis Services
    · Moondream (Local Vision)
    · Vision Service Base Class
  Image Generation Services
    · Supported Providers
    · Data Flow: Text to Image
  Implementation Details: Service Settings
    · Code Entity Association: Service Settings
  Summary of Vision Capabilities

## · Transport Layer  (L6095)
  源文件: CHANGELOG.md, src/pipecat/frames/frames.py, src/pipecat/pipeline/task.py, src/pipecat/processors/aggregators/llm_response.py, src/pipecat/processors/aggregators/llm_response_universal.py, src/pipecat/processors/frame_processor.py, src/pipecat/services/llm_service.py, src/pipecat/transports/base_input.py, src/pipecat/transports/base_output.py, src/pipecat/transports/base_transport.py, src/pipecat/transports/daily/transport.py, src/pipecat/transports/livekit/transport.py
  Role of the Transport Layer
  Class Hierarchy
  How Transports Plug Into the Pipeline
  `TransportParams` Reference
  Frame Contract at Transport Boundaries
  Transport Catalog
  Subsection Pages

## · Daily Transport  (L6345)
  源文件: src/pipecat/runner/daily.py, src/pipecat/services/google/gemini_live/vertex/__init__.py, src/pipecat/services/google/gemini_live/vertex/llm.py, src/pipecat/transports/daily/transport.py, src/pipecat/transports/livekit/transport.py, src/pipecat/transports/smallwebrtc/connection.py, src/pipecat/transports/smallwebrtc/request_handler.py, src/pipecat/transports/smallwebrtc/transport.py, src/pipecat/transports/tavus/transport.py, src/pipecat/transports/websocket/client.py, src/pipecat/transports/websocket/fastapi.py, src/pipecat/transports/websocket/server.py
  Installation
  Architecture
  DailyTransport
    · New in 1.6.0: STT Latency Metadata
  DailyParams
  DailyCallbacks
  DailyTransportClient
  WebRTCVADAnalyzer
  Daily-Specific Frame Types
    · DTMF Frames
    · Message Frames
  SIP Call Control
    · DailySIPTransferFrame and DailySIPReferFrame
    · DailyUpdateRemoteParticipantsFrame
  Daily REST Utilities
  TavusTransport
    · TavusApi
  Module Reference

## · LiveKit Transport  (L6766)
  源文件: src/pipecat/transports/daily/transport.py, src/pipecat/transports/livekit/transport.py, src/pipecat/transports/smallwebrtc/transport.py, src/pipecat/transports/tavus/transport.py, src/pipecat/transports/websocket/client.py, src/pipecat/transports/websocket/fastapi.py, src/pipecat/transports/websocket/server.py, tests/test_fastapi_websocket.py, tests/test_livekit_transport.py, tests/test_websocket_server_transport.py
  Overview
  Class Hierarchy
  Configuration: `LiveKitParams`
  Callbacks: `LiveKitCallbacks`
  `LiveKitTransport`
  `LiveKitTransportClient`
  Audio and Video I/O
  Data Channel Messaging
    · Sending Messages
    · Receiving Messages
  DTMF Support
    · Sending DTMF
    · Inbound SIP DTMF
  LiveKit Runner Helper

## · WebSocket Transports  (L7056)
  源文件: .gitignore, examples/transports/transports-moq.py, src/pipecat/runner/moq.py, src/pipecat/runner/run.py, src/pipecat/runner/types.py, src/pipecat/runner/utils.py, src/pipecat/transports/daily/transport.py, src/pipecat/transports/livekit/transport.py, src/pipecat/transports/moq/__init__.py, src/pipecat/transports/moq/transport.py, src/pipecat/transports/smallwebrtc/transport.py, src/pipecat/transports/tavus/transport.py
  Transport Overview
  FastAPI WebSocket Transport
    · Key Components
    · Development Runner Integration
  WebSocket Server Transport (Deprecated)
    · Drain Fix (1.6.0)
    · Security and Origins
  WebSocket Client Transport
  SmallWebRTC Transport
    · SmallWebRTCConnection
    · SmallWebRTCRequestHandler
    · Media and OpenCV (1.6.0)
    · Raw Media Tracks
  WhatsApp Transport
    · Key Components
  Installation

## · Telephony and Serializers  (L7293)
  源文件: examples/transports/transports-vonage.py, examples/video-avatar/video-avatar-lemonslice-transport.py, src/pipecat/runner/vonage.py, src/pipecat/serializers/base_serializer.py, src/pipecat/serializers/exotel.py, src/pipecat/serializers/genesys.py, src/pipecat/serializers/plivo.py, src/pipecat/serializers/protobuf.py, src/pipecat/serializers/telnyx.py, src/pipecat/serializers/twilio.py, src/pipecat/serializers/vonage.py, src/pipecat/transports/lemonslice/api.py
  FrameSerializer Base Class
    · Configuration Parameters
  Telephony Serializers
    · Provider Comparison
    · Validation and Auto Hang-up
  Genesys AudioHook Serializer
  Vonage Video Connector
  ProtobufFrameSerializer
  LemonSlice Transport
  Audio Resampling and DTMF
    · Resampling
    · DTMF Handling
    · 422 Validation Error Logging

## · Local, Test, and MOQ Transports  (L7532)
  源文件: .gitignore, examples/transports/transports-moq.py, src/pipecat/processors/consumer_processor.py, src/pipecat/processors/gstreamer/pipeline_source.py, src/pipecat/processors/idle_frame_processor.py, src/pipecat/processors/producer_processor.py, src/pipecat/runner/moq.py, src/pipecat/runner/run.py, src/pipecat/runner/types.py, src/pipecat/runner/utils.py, src/pipecat/services/heygen/api_interactive_avatar.py, src/pipecat/services/heygen/client.py
  Media over QUIC (MOQ) Transport
    · Key Architecture
    · Development Runner Integration
  Local Audio Transport
  Tkinter Transport
  GStreamer Pipeline Source
  Avatar Services
    · Tavus Integration
    · HeyGen Integration
  Comparison Summary

## · Audio and Video Processing  (L7711)
  源文件: src/pipecat/audio/filters/aic_filter.py, src/pipecat/audio/utils.py, src/pipecat/audio/vad/aic_vad.py, src/pipecat/audio/vad/vad_analyzer.py, src/pipecat/audio/vad/vad_controller.py, src/pipecat/processors/audio/vad_processor.py, tests/test_aic_filter.py, tests/test_aic_filter_vad_factory_deprecation.py, tests/test_aic_vad.py, tests/test_aic_vad_deprecation.py, tests/test_resampy_resampler.py, tests/test_vad_controller.py
  Overview
  Audio and Video Frame Types
    · Frame Mixins
  Voice Activity Detection (VAD)
    · VAD Components
  Audio Filters and Enhancement
    · AI-Coustics (AIC) Filter and VAD
    · Recording and Buffering
  Video Processing
    · Multimodal Capabilities
  Audio Utilities

## · Voice Activity Detection  (L7932)
  源文件: examples/voice/voice-krisp-viva.py, scripts/krisp/audio_file_utils.py, scripts/krisp/test_krisp_viva_filter_audiofile.py, scripts/krisp/test_krisp_viva_turn_audiofile.py, src/pipecat/audio/filters/aic_filter.py, src/pipecat/audio/filters/krisp_viva_filter.py, src/pipecat/audio/krisp_instance.py, src/pipecat/audio/turn/krisp_viva_turn.py, src/pipecat/audio/utils.py, src/pipecat/audio/vad/aic_vad.py, src/pipecat/audio/vad/krisp_viva_vad.py, src/pipecat/audio/vad/vad_analyzer.py
  Overview
  VAD State Machine
  VADAnalyzer Interface
    · Key Method Contracts
  Supported VAD Analyzers
    · AIC Quail VAD (`AICQuailVADAnalyzer`)
    · Krisp VIVA VAD (`KrispVivaVadAnalyzer`)
    · Silero VAD (`SileroVADAnalyzer`)
  VADController and Processor
  Integration with Transports and Aggregators

## · Audio Filters and Enhancement  (L8150)
  源文件: examples/audio/audio-recording.py, examples/voice/voice-aicoustics.py, src/pipecat/audio/dtmf/utils.py, src/pipecat/audio/filters/aic_filter.py, src/pipecat/audio/filters/rnnoise_filter.py, src/pipecat/audio/utils.py, src/pipecat/audio/vad/aic_vad.py, src/pipecat/processors/audio/audio_buffer_processor.py, src/pipecat/processors/frameworks/strands_agents.py, tests/test_aic_filter.py, tests/test_aic_filter_vad_factory_deprecation.py, tests/test_aic_vad.py
  Overview
  Filter Interface
  AICFilter
    · Authentication and Environment
    · Key constructor parameters
  AICModelManager
  Voice Activity Detection (AIC)
    · AICQuailVADAnalyzer (Recommended)
    · AICVADAnalyzer (Deprecated)
  RNNoiseFilter
  AudioBufferProcessor
    · Configuration
    · Events
    · Control Frames
  Audio Utility Functions
    · Resamplers and Factories
    · Metrics and Onset Detection
    · Mixing and channel functions

## · Video Processing  (L8396)
  源文件: src/pipecat/processors/consumer_processor.py, src/pipecat/processors/gstreamer/pipeline_source.py, src/pipecat/processors/idle_frame_processor.py, src/pipecat/processors/producer_processor.py, src/pipecat/services/heygen/api_interactive_avatar.py, src/pipecat/services/heygen/client.py, src/pipecat/services/heygen/video.py, src/pipecat/services/simli/video.py, src/pipecat/services/tavus/video.py, src/pipecat/transports/heygen/transport.py, tests/test_producer_consumer.py
  Purpose and Scope
  Video Frame Hierarchy
  Avatar Video Services
    · Tavus Integration
    · HeyGen Integration
    · Simli Integration
  GStreamer Integration
  Frame Distribution Patterns
    · Producer and Consumer Processors
    · Idle Monitoring
  Video Input and Output Processing

## · Development Tools  (L8604)
  源文件: .gitignore, examples/transports/transports-moq.py, src/pipecat/cli/__init__.py, src/pipecat/cli/commands/__init__.py, src/pipecat/cli/commands/init.py, src/pipecat/cli/config_validator.py, src/pipecat/cli/generators/project.py, src/pipecat/cli/main.py, src/pipecat/cli/prompts/questions.py, src/pipecat/cli/registry/__init__.py, src/pipecat/cli/registry/service_loader.py, src/pipecat/runner/moq.py
  Overview
  Bot Entry Point Convention
  Runner Arguments Type Hierarchy
  Pipecat CLI
    · Project Scaffolding
    · Evaluation CLI
  Telephony Detection and Handshake
  MOQ Transport (v1.6.0)
  Testing and Eval Framework
  Client SDKs and Tools

## · Pipeline Runner and Development Patterns  (L8850)
  源文件: .gitignore, examples/transports/transports-moq.py, src/pipecat/pipeline/runner.py, src/pipecat/runner/daily.py, src/pipecat/runner/moq.py, src/pipecat/runner/run.py, src/pipecat/runner/types.py, src/pipecat/runner/utils.py, src/pipecat/services/google/gemini_live/vertex/__init__.py, src/pipecat/services/google/gemini_live/vertex/llm.py, src/pipecat/tests/utils.py, src/pipecat/transports/moq/__init__.py
  Purpose and Scope
  Pipeline Runner and Development Infrastructure
    · Multi-Transport Development Server
    · Media over QUIC (MoQ) Support
    · Security and Authentication
    · Runner Architecture
    · RunnerArguments and Session Tracing
  Transport Helpers and Utilities
    · Daily Room Configuration
    · Telephony Detection
  Foundational Development Patterns
    · The WorkerRunner Lifecycle
    · MoQ Transport Architecture
    · WebRTC Connection Management
  Development Workflow Summary

## · Testing and Evaluation Framework  (L9080)
  源文件: .github/workflows/build.yaml, .github/workflows/coverage.yaml, .github/workflows/format.yaml, .github/workflows/publish.yaml, .github/workflows/publish_test.yaml, .github/workflows/tests.yaml, AGENTS.md, CLAUDE.md, scripts/release-evals/README.md, scripts/release-evals/manifest.yaml, scripts/release-evals/run.sh, scripts/release-evals/scenarios/capital_question.yaml
  Purpose and Scope
  Evaluation Architecture
    · System Topology
  Core Evaluation Components
    · EvalSession and Harness
    · Scenario Definition
  Evaluation Logic and Data Flow
    · Judge and Transcriber Bridge
  Release Evaluation Process
    · EvalSuite and Manifest
  CI/CD and Static Analysis
    · CI/CD Workflows
    · Static Analysis
  CLI and Scaffolding

## · Client SDKs and Tools  (L9326)
  源文件: MANIFEST.in, scripts/cli/check_registry.py, scripts/cli/configs/config_generator.py, scripts/cli/configs/update_configs.py, scripts/cli/imports/import_generator.py, scripts/cli/imports/update_imports.py, scripts/cli/update_registry.py, src/pipecat/cli/__init__.py, src/pipecat/cli/agent_templates/AGENTS.md, src/pipecat/cli/agent_templates/CLAUDE.md, src/pipecat/cli/agent_templates/GETTING_STARTED.md, src/pipecat/cli/commands/__init__.py
  Client SDKs
    · Supported Platforms
    · Client-Bot Data Flow
  Pipecat CLI
    · Project Initialization (`pipecat init`)
    · Project Scaffolding
    · Plugin Isolation (Post-1.6.0)
    · Project Generation Logic
  Development Tools
    · Whisker Debugger
    · Testing and Evaluation Framework
  Example Applications
    · Pipeline Modes
    · Integration Examples
  Dependency Management

## · Advanced Topics  (L9532)
  源文件: CHANGELOG.md, examples/README.md, examples/flows/assets/hold_music/README.md, examples/flows/assets/hold_music/hold_music.py, examples/flows/assets/hold_music/hold_music.wav, examples/flows/food_ordering.py, examples/flows/food_ordering_advanced_functionschema.py, examples/flows/hello_world.py, examples/flows/insurance_quote.py, examples/flows/llm_switching.py, examples/flows/multi_worker_handoff.py, src/pipecat/frames/frames.py
  What Makes These Topics "Advanced"
  Advanced Systems Integration with Code Entities
  Multi-Worker Communication Architecture
  Advanced Frame Types
  Overview of Subsections
    · 8.1 Function Calling and Tool Use
    · 8.2 Building Natural Conversations
    · 8.3 Multi-Worker Framework
    · 8.4 Custom Processors and Extensions
    · 8.5 Observability, Metrics, and Tracing
    · 8.6 Memory and Persistent Context
    · 8.7 Conversation Flows
    · 8.8 Migration Guides and Deprecated APIs
  Common Advanced Patterns
    · Programmatic Context Transformation
    · Service Auto-Configuration
    · Shared Application Resources

## · Function Calling and Tool Use  (L9754)
  源文件: examples/function-calling/function-calling-anthropic-async-stream.py, examples/function-calling/function-calling-anthropic-async.py, examples/function-calling/function-calling-anthropic.py, examples/function-calling/function-calling-azure.py, examples/function-calling/function-calling-cerebras.py, examples/function-calling/function-calling-deepseek.py, examples/function-calling/function-calling-google-async-stream.py, examples/function-calling/function-calling-google-async.py, examples/function-calling/function-calling-google.py, examples/function-calling/function-calling-groq.py, examples/function-calling/function-calling-mistral.py, examples/function-calling/function-calling-novita.py
  Overview
    · Natural Language to Code Entity Mapping
  Function Registration and Auto-Registration
    · LLMContext Auto-Registration
    · Direct Function Registration
  Tool Options and Decorators
  Execution Flow and Modes
  Framework Integrations
    · Model Context Protocol (MCP)
    · LangChain and Strands
    · App Resources Pattern
  Tool Schemas and Adapters

## · Building Natural Conversations  (L9965)
  源文件: changelog/5007.fixed.2.md, changelog/5007.fixed.md, changelog/5063.fixed.md, examples/turn-management/turn-management-filter-incomplete-turns.py, src/pipecat/turns/user_start/base_user_turn_start_strategy.py, src/pipecat/turns/user_start/min_words_user_turn_start_strategy.py, src/pipecat/turns/user_start/wake_phrase_user_turn_start_strategy.py, src/pipecat/turns/user_stop/__init__.py, src/pipecat/turns/user_stop/base_user_turn_stop_strategy.py, src/pipecat/turns/user_stop/deferred_user_turn_stop_strategy.py, src/pipecat/turns/user_stop/external_user_turn_completion_stop_strategy.py, src/pipecat/turns/user_stop/external_user_turn_stop_strategy.py
  Purpose and Scope
  Turn Management Architecture
    · Core Components
  Turn Detection and Analysis
    · Smart Turn Analysis
    · Timeout Strategies
  Incomplete Turn Filtering (Markers)
    · Turn Completion Markers
    · Implementation: UserTurnCompletionLLMServiceMixin
  Turn Completion Strategies
    · Key Classes and Wrappers
    · Events
  User Idle Detection
  Natural Conversation Examples
    · Example Configuration

## · Multi-Worker Framework  (L10198)
  源文件: examples/observability/observability-heartbeats.py, src/pipecat/bus/__init__.py, src/pipecat/bus/bridge_processor.py, src/pipecat/bus/bus.py, src/pipecat/bus/local/async_queue.py, src/pipecat/bus/messages.py, src/pipecat/bus/network/__init__.py, src/pipecat/bus/network/pgmq.py, src/pipecat/bus/network/pgmq_backends.py, src/pipecat/bus/network/redis.py, src/pipecat/bus/queue.py, src/pipecat/pipeline/job_context.py
  High-Level Architecture
    · Framework Components
    · Code-to-System Mapping: The Multi-Worker Ecosystem
  Worker Architecture and Bus
  Worker Types and Patterns
    · Core Worker Types and Decorators
    · Multi-Worker Topologies
  WorkerRunner and Deployment
    · Distributed Deployments
    · Task Management (1.5.0+)
  Example Patterns

## · Worker Architecture and Bus  (L10360)
  源文件: src/pipecat/bus/__init__.py, src/pipecat/bus/bridge_processor.py, src/pipecat/bus/bus.py, src/pipecat/bus/local/async_queue.py, src/pipecat/bus/messages.py, src/pipecat/bus/network/__init__.py, src/pipecat/bus/network/pgmq.py, src/pipecat/bus/network/pgmq_backends.py, src/pipecat/bus/network/redis.py, src/pipecat/bus/queue.py, src/pipecat/pipeline/job_context.py, src/pipecat/pipeline/job_decorator.py
  WorkerBus System
    · Message Priority and Queuing
    · Bus Message Hierarchy
    · Message Data Flow
  Concrete Bus Implementations
    · Local: AsyncQueueBus
    · Distributed: RedisBus
    · Distributed: PgmqBus
  BridgeProcessor: Transporting Frames
    · Serialization Adapters
    · BusBridgeProcessor
    · _BusEdgeProcessor
  WorkerRegistry and Discovery
  Distributed Proxying

## · Worker Types and Patterns  (L10547)
  源文件: examples/observability/observability-heartbeats.py, src/pipecat/bus/__init__.py, src/pipecat/bus/bridge_processor.py, src/pipecat/bus/bus.py, src/pipecat/bus/local/async_queue.py, src/pipecat/bus/messages.py, src/pipecat/bus/network/__init__.py, src/pipecat/bus/network/pgmq.py, src/pipecat/bus/network/pgmq_backends.py, src/pipecat/bus/network/redis.py, src/pipecat/bus/queue.py, src/pipecat/pipeline/job_context.py
  Core Worker Classes
    · BaseWorker
    · PipelineWorker
    · LLMWorker and LLMContextWorker
    · UIWorker
  Implementation Data Flow
    · Worker Communication Architecture
  Job Coordination and Lifecycle (1.5.0+)
  Distributed Patterns
    · Distributed Buses
    · WebSocketProxyServer/Client
    · Remote Worker Topology
  Multi-Worker Example Patterns
    · Pattern: LLM Tool Handoff
    · Pattern: Multi-Worker Handoff with Flows

## · Custom Processors and Extensions  (L10721)
  源文件: src/pipecat/extensions/voicemail/voicemail_detector.py, src/pipecat/processors/aggregators/dtmf_aggregator.py, src/pipecat/processors/aggregators/llm_text_processor.py, src/pipecat/utils/string.py, src/pipecat/utils/text/__init__.py, src/pipecat/utils/text/base_text_aggregator.py, src/pipecat/utils/text/base_text_filter.py, src/pipecat/utils/text/markdown_text_filter.py, src/pipecat/utils/text/pattern_pair_aggregator.py, src/pipecat/utils/text/simple_text_aggregator.py, src/pipecat/utils/text/skip_tags_aggregator.py, tests/test_dtmf_aggregator.py
  Custom Frame Processors
    · Implementation Patterns
    · Event Handlers and Interruption
  Text Aggregation and Filtering
    · LLM Text Processor
    · Simple and Pattern Aggregators
    · Markdown Text Filter
  Voicemail Detection
    · Classification and Gating
  DTMF Aggregator
  IVR Navigator
    · IVR Status and Actions
  Managed Tasks and Idle Processing
    · Managed Tasks
    · Idle Frame Processor
  GStreamer Pipeline Source
  Word Completion and Timestamps

## · Observability, Metrics, and Tracing  (L10944)
  源文件: src/pipecat/metrics/metrics.py, src/pipecat/observers/__init__.py, src/pipecat/observers/base_observer.py, src/pipecat/observers/loggers/debug_log_observer.py, src/pipecat/observers/loggers/metrics_log_observer.py, src/pipecat/observers/startup_timing_observer.py, src/pipecat/observers/turn_tracking_observer.py, src/pipecat/observers/user_bot_latency_observer.py, src/pipecat/processors/metrics/frame_processor_metrics.py, src/pipecat/processors/metrics/sentry.py, src/pipecat/utils/tracing/service_attributes.py, src/pipecat/utils/tracing/service_decorators.py
  Purpose and Scope
  System Architecture
  Observer Pattern
    · BaseObserver
  Built-in Observers
    · TurnTrackingObserver
    · UserBotLatencyObserver
    · StartupTimingObserver
    · MetricsLogObserver
  Metrics Collection
    · FrameProcessorMetrics
    · TTFAMetricsData
  OpenTelemetry Tracing
    · Service Decorators
    · OTel GenAI Semantic Conventions (1.6.0 Updates)
    · TurnTraceObserver
  Sentry Integration

## · Memory and Persistent Context  (L11264)
  源文件: examples/rag/rag-mem0.py, src/pipecat/processors/aggregators/llm_context_summarizer.py, src/pipecat/services/mem0/memory.py, src/pipecat/utils/context/llm_context_summarization.py, src/pipecat/utils/frame_queue.py, tests/test_context_summarization.py, tests/test_llm_context_summarizer.py, tests/test_mem0.py
  Purpose and Scope
  Context Summarization
    · Summarization Architecture
    · Configuration Parameters
    · Token Estimation
  Mem0 Memory Service
    · Data Flow for Memory Retrieval
    · Key Features and 2.0.0 Changes
  Persistent Context Patterns
    · Entity Mapping: Persistence Logic
  Context in Pipecat Flows
  Multi-turn History Management

## · Conversation Flows  (L11465)
  源文件: .github/workflows/generate-changelog.yml, .pre-commit-config.yaml, examples/README.md, examples/flows/assets/hold_music/README.md, examples/flows/assets/hold_music/hold_music.py, examples/flows/assets/hold_music/hold_music.wav, examples/flows/food_ordering.py, examples/flows/food_ordering_advanced_functionschema.py, examples/flows/hello_world.py, examples/flows/insurance_quote.py, examples/flows/llm_switching.py, examples/flows/multi_worker_handoff.py
  Architecture and Core Components
    · FlowManager
    · NodeConfig
    · Data Flow and Transitions
  Context Management Strategies
  Function and Tool Handling
    · Global Functions
    · Function Handlers
    · NO_RESPONSE (v1.6.0)
    · Action Handling
  LLMSwitcher Integration
  Migration and Best Practices
    · 1.5.0 Migration Guide
    · Examples

## · Migration Guides and Deprecated APIs  (L11643)
  源文件: .github/workflows/generate-changelog.yml, .pre-commit-config.yaml, CHANGELOG.md, scripts/deprecations/__init__.py, scripts/deprecations/deprecations.json, scripts/deprecations/generate.py, scripts/deprecations/generate_removals.py, scripts/deprecations/removals.json, scripts/deprecations/scan.py, src/pipecat/__init__.py, src/pipecat/flows/__init__.py, src/pipecat/flows/actions.py
  Overview of Deprecation Strategy
  Major Migration: Multi-Worker Framework (1.3.0)
    · PipelineTask → PipelineWorker
    · PipelineRunner → WorkerRunner
    · TaskFrame Renames
  Module Path and Namespace Migrations
  Resource Management: tool_resources to app_resources
  Service and Transport Updates (1.4.0 - 1.6.0)
    · VAD and Audio Filtering
    · Function Calling and Tools
    · Text-to-Speech Updates
    · Transports and Connectivity
    · Memory and Persistence
    · Flow Management (1.5.0 - 1.6.0)
  Turn Detection and Lifecycle Callbacks (1.6.0)
  Observability and OTel Semantic Conventions (1.6.0)
  Migration Checklist

## · Glossary  (L11892)
  源文件: CHANGELOG.md, README.md, env.example, examples/function-calling/function-calling-baseten.py, pyproject.toml, src/pipecat/bus/__init__.py, src/pipecat/bus/bridge_processor.py, src/pipecat/bus/bus.py, src/pipecat/bus/local/async_queue.py, src/pipecat/bus/messages.py, src/pipecat/bus/network/__init__.py, src/pipecat/bus/network/pgmq.py
  Core Pipeline Concepts
    · Frame
    · FrameProcessor
    · PipelineWorker
    · WorkerRunner
    · TaskManager
    · Mapping Code Entities to Pipeline Concepts
  Multi-Worker Framework (pipecat.workers)
    · WorkerBus
    · BaseWorker
    · Job & Event Decorators
    · Worker Lifecycle Types
  Conversation & Context Terms
    · LLMContext
    · Aggregator Pair
    · User Turn Strategies
    · Conversation Flows
  Audio & AI Service Terminology
    · Large Language Models (LLM)
    · Speech-to-Text (STT)
    · Text-to-Speech (TTS)
  Transport & Protocol
    · MOQTransport (Media over QUIC)
    · RTVI Protocol
    · Telephony & WebRTC
  Development & Operations