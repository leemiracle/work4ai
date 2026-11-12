# Skeleton: joinly（29 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 15KB | 3 | ~6 | 6 |
| 2 | Getting Started | L457 | 13KB | 4 | ~8 | 6 |
| 3 | Installation and Dependencies | L821 | 11KB | 4 | ~10 | 5 |
| 4 | Quick Start Guide | L1211 | 8KB | 3 | ~4 | 6 |
| 5 | Configuration and Settings | L1510 | 9KB | 4 | ~9 | 4 |
| 6 | Architecture | L1794 | 21KB | 7 | ~14 | 13 |
| 7 | MCP Server and Client Communication | L2340 | 16KB | 8 | ~8 | 10 |
| 8 | Session Management and Dependency Injection | L2809 | 15KB | 8 | ~9 | 6 |
| 9 | Data Types and Models | L3203 | 9KB | 6 | ~2 | 5 |
| 10 | Core Server (joinly) | L3460 | 11KB | 5 | ~5 | 7 |
| 11 | FastMCP Server Interface | L3773 | 16KB | 6 | ~16 | 3 |
| 12 | Meeting Session Orchestration | L4274 | 14KB | 10 | ~7 | 6 |
| 13 | Browser Meeting Provider | L4663 | 20KB | 9 | ~9 | 2 |
| 14 | Platform Controllers | L5163 | 11KB | 6 | ~6 | 3 |
| 15 | Audio Processing Pipeline | L5430 | 12KB | 6 | ~7 | 10 |
| 16 | Transcription Controller | L5775 | 17KB | 4 | ~4 | 4 |
| 17 | Speech Controller | L6236 | 9KB | 7 | ~7 | 2 |
| 18 | Service Providers (VAD, STT, TTS) | L6539 | 20KB | 8 | ~13 | 8 |
| 19 | Client SDK (joinly-client) | L7113 | 21KB | 5 | ~18 | 8 |
| 20 | JoinlyClient API | L7699 | 23KB | 8 | ~9 | 9 |
| 21 | ConversationalToolAgent | L8315 | 20KB | 10 | ~17 | 7 |
| 22 | Usage Patterns and Examples | L8926 | 34KB | 7 | ~20 | 13 |
| 23 | LLM and External Service Integration | L10095 | 19KB | 4 | ~4 | 11 |
| 24 | Development | L10745 | 6KB | 3 | ~2 | 3 |
| 25 | Development Environment Setup | L10959 | 7KB | 3 | ~4 | 3 |
| 26 | Build System and Dependencies | L11140 | 17KB | 5 | ~6 | 4 |
| 27 | Deployment | L11798 | 13KB | 4 | ~7 | 5 |
| 28 | Docker Images and Variants | L12168 | 11KB | 2 | ~5 | 5 |
| 29 | Deployment Modes | L12547 | 21KB | 6 | ~11 | 6 |


## · Overview  (L6)
  源文件: .env.example, CHANGELOG.md, README.md, joinly/services/tts/resemble.py, pyproject.toml, uv.lock
  Purpose and Design Philosophy
  System Architecture
    · Package Structure
    · High-Level Component Diagram
    · Server-Client Communication via MCP
  Core Components
    · Server Package (`joinly`)
    · Client Package (`joinly-client`)
    · Common Package (`joinly-common`)
  Key Features
    · Real-Time Audio Processing
    · Service Provider Flexibility
    · MCP Tools and Resources
  Deployment Modes
    · Mode 1: Server + External Client
    · Mode 2: All-in-One Client
    · Mode 3: Custom Client
  Docker Image Variants
  Technology Stack
    · Core Technologies
    · Key Dependencies
    · Virtual Device Infrastructure
  Configuration System
  Development and Extension

## · Getting Started  (L457)
  源文件: .env.example, CHANGELOG.md, README.md, joinly/services/tts/resemble.py, pyproject.toml, uv.lock
  System Overview
    · Component Architecture
  Deployment Modes
    · Mode Comparison
  Basic Getting Started Workflow
  Prerequisites
  Configuration Overview
    · Essential Environment Variables
    · Speech Service Configuration
  Docker Image Variants
    · Choosing an Image
  First Steps After Installation
  MCP Server Interface
    · Available Tools
    · Available Resources
  Next Steps

## · Installation and Dependencies  (L821)
  源文件: CHANGELOG.md, client/README.md, client/joinly_client/__init__.py, pyproject.toml, uv.lock
  System Requirements
    · Python Version
    · Platform Support
    · System Dependencies
  Installation Methods
    · Docker Installation (Recommended)
    · uv Installation (Development/Local)
    · pip Installation
  Dependency Overview
    · Workspace Structure
    · Core Server Dependencies
    · Client Dependencies
    · Development Dependencies
  Dependency Resolution
    · Platform-Specific Resolution
    · Workspace Dependencies
  Version Management
    · Package Versions
    · Dependency Updates
  CLI Entry Points
  Next Steps

## · Quick Start Guide  (L1211)
  源文件: .env.example, README.md, client/README.md, client/joinly_client/__init__.py, joinly/main.py, joinly/services/tts/resemble.py
  Prerequisites and Setup
    · Environment Configuration
  Basic Deployment
    · Pull Docker Image
    · Direct Client Mode
  MCP Server Deployment
    · Start Server Mode
    · Quick Start Architecture
  External Client Connection
    · Using joinly-client
    · MCP Tools and Resources Flow
  Multi-MCP Server Integration
    · Configuration File
    · Run with Multiple Servers
  Meeting Session Lifecycle
    · Session Management Flow
  Common Configuration Options
    · Basic Settings
    · Provider Settings
    · Debug Options
  Next Steps

## · Configuration and Settings  (L1510)
  源文件: .env.example, README.md, joinly/main.py, joinly/services/tts/resemble.py
  Configuration Architecture
    · Configuration Flow
    · Settings Management Pattern
  Configuration Sources
    · Environment File Loading
  Core Settings
    · Basic Configuration
    · Server Configuration
    · Service Selection
  Service-Specific Configuration
    · Service Arguments Structure
    · CLI Argument Parsing
  Environment Variable Configuration
    · Naming Convention
    · Pydantic Settings Configuration
  Logging Configuration
    · Logging Levels and Options
    · Verbosity Levels
  Client-Specific Configuration
  Configuration Examples
    · Development Configuration
    · Production Configuration
    · CLI Override Example

## · Architecture  (L1794)
  源文件: CHANGELOG.md, client/joinly_client/agent.py, client/joinly_client/client.py, client/joinly_client/main.py, client/joinly_client/prompts.py, client/joinly_client/types.py, client/joinly_client/utils.py, common/joinly_common/types.py, joinly/server.py, joinly/utils/events.py, joinly/utils/usage.py, pyproject.toml
  System Overview
    · Server-Client Separation
  Core Components
    · Server Components
    · Client Components
  Communication Protocol
    · MCP Resources
    · MCP Tools
  Data Flow Architecture
    · Event-Driven Transcript Updates
    · Bidirectional Speech Pipeline
  Shared Data Types
    · Core Types
    · Transcript Model
    · Usage Tracking
  Configuration and Settings
    · Server Configuration
    · Client Configuration
  Deployment Architecture
    · Docker Image Variants
  Summary

## · MCP Server and Client Communication  (L2340)
  源文件: client/joinly_client/agent.py, client/joinly_client/client.py, client/joinly_client/main.py, client/joinly_client/prompts.py, client/joinly_client/types.py, client/joinly_client/utils.py, common/joinly_common/types.py, joinly/server.py, joinly/utils/events.py, joinly/utils/usage.py
  Architecture Overview
  Server Implementation
    · Core Server Setup
    · Settings Injection
    · Resource Providers
    · Tool Implementations
  Client Implementation
    · Client Connection Architecture
    · Resource Subscription Model
    · Message Handling Pipeline
  Communication Protocols
    · Transport Layer Configuration
    · Resource Update Flow
  Session Management
    · Session Lifecycle
    · Context Variable Management
  Code Entity Mapping

## · Session Management and Dependency Injection  (L2809)
  源文件: joinly/container.py, joinly/controllers/transcription/default.py, joinly/core.py, joinly/providers/browser/meeting_provider.py, joinly/session.py, joinly/utils/clock.py
  Dependency Injection Overview
    · High-Level Component Relationships
  Service Resolution: The `_resolve()` Function
    · `_resolve()` Token Mapping Algorithm
  `SessionContainer`: Dependency Injection Implementation
    · `SessionContainer.__aenter__()` Execution Flow
    · Dependency Wiring Code
    · Async Context Management with `AsyncExitStack`
    · Configuration-to-Service Mapping
  `MeetingSession`: Component Orchestration
    · `MeetingSession.join_meeting()` Initialization
    · Shared Resource Architecture
  MeetingSession Orchestration
    · Session State Management
    · Component Coordination
  Service Configuration Examples

## · Data Types and Models  (L3203)
  源文件: common/joinly_common/types.py, joinly/controllers/speech/default.py, joinly/server.py, joinly/types.py, joinly/utils/usage.py
  Core Data Structures Overview
  Audio Processing Types
    · AudioFormat
    · Audio Data Flow Types
  Meeting-Related Types
    · Meeting Participants and Chat
  Exception Types
    · Custom Exception Hierarchy
  Shared Types from joinly-common
    · Transcription and Usage Types
  Type Relationships and Data Flow

## · Core Server (joinly)  (L3460)
  源文件: CHANGELOG.md, common/joinly_common/types.py, joinly/main.py, joinly/server.py, joinly/utils/usage.py, pyproject.toml, uv.lock
  Application Architecture
  CLI Interface and Application Modes
    · Server Mode
    · Client Mode  
  MCP Server Implementation
    · Core Tools
    · MCP Resources
  Session Management
  Settings Management
  Usage Tracking System
  Health Check and HTTP Endpoints

## · FastMCP Server Interface  (L3773)
  源文件: common/joinly_common/types.py, joinly/server.py, joinly/utils/usage.py
  Purpose and Scope
  Server Instance and Transport
  Session Lifecycle and Context Management
    · Per-Connection Session Architecture
    · Settings Extraction from HTTP Headers
    · SessionContext Structure
  Resources
    · Resource Definitions
    · transcript://live
    · transcript://live/segments
    · usage://current
  Tools
    · Tool Catalog
    · join_meeting
    · leave_meeting
    · speak_text
    · send_chat_message
    · get_chat_history
    · get_transcript
    · get_participants
    · get_video_snapshot
    · mute_yourself / unmute_yourself
  Resource Subscriptions
    · Subscription Flow
    · Subscription Handler Implementation
  Custom HTTP Endpoints
    · Health Check
  Usage Tracking
    · Usage Context Variables
  Server Execution

## · Meeting Session Orchestration  (L4274)
  源文件: joinly/controllers/speech/default.py, joinly/controllers/transcription/default.py, joinly/core.py, joinly/session.py, joinly/types.py, joinly/utils/clock.py
  Purpose and Scope
  Architecture Overview
    · Component Structure
  Core Responsibilities
  Shared Resources
    · Clock
    · Transcript
    · EventBus
  Component Coordination
    · Controller Initialization
    · Cross-Controller Coordination
  Lifecycle Management
    · Join Meeting Sequence
    · Leave Meeting Sequence
  Event Subscription System
    · Subscription API
    · Event Flow
  API Surface
    · Properties
  Implementation Details
    · Method Delegation Pattern
    · Error Handling

## · Browser Meeting Provider  (L4663)
  源文件: joinly/container.py, joinly/providers/browser/meeting_provider.py
  Purpose and Scope
  Architecture Overview
  Architecture Overview
  Core Components
    · BrowserMeetingProvider Class
    · Platform Controller Selection and Integration
  Virtual Audio Device Architecture
    · Audio Reader and Writer Properties
    · Speaker Attribution Wrapper
    · Virtual Microphone and Speaker Configuration
  Meeting Action Implementation
    · Action Guard Context Manager
    · Join and Leave Methods
    · Meeting Control Methods
  Video Snapshot Support
  Audio Format Integration
    · Audio Format Conversion
    · Timing and Duration Calculations

## · Platform Controllers  (L5163)
  源文件: joinly/providers/browser/platforms/google_meet.py, joinly/providers/browser/platforms/teams.py, joinly/providers/browser/platforms/zoom.py
  Architecture Overview
  Common Interface
  Platform-Specific Implementations
    · Google Meet Controller
    · Zoom Controller
    · Teams Controller
  Core Functionality
    · Meeting Lifecycle Management
    · Chat Message Handling
    · Participant Management
  Active Speaker Detection
  URL Pattern Matching

## · Audio Processing Pipeline  (L5430)
  源文件: joinly/controllers/speech/default.py, joinly/controllers/transcription/default.py, joinly/core.py, joinly/services/stt/deepgram.py, joinly/services/stt/whisper.py, joinly/services/tts/deepgram.py, joinly/services/tts/elevenlabs.py, joinly/session.py, joinly/types.py, joinly/utils/clock.py
  Architecture Overview
    · Audio Processing Flow
    · Component Integration
  Audio Format Management
    · AudioFormat Type
    · Format Conversion
  Transcription Flow
    · Transcription Controller Lifecycle
    · Speech Window Processing
  Speech Synthesis Flow
    · Speech Controller Architecture
    · Interruption Handling
  Turn-Taking Coordination
    · Event Coordination Flow
  Error Handling and Resource Management
    · Resource Lifecycle Management
    · Exception Types
  Performance Characteristics
    · Latency Management
    · Memory Management

## · Transcription Controller  (L5775)
  源文件: joinly/controllers/transcription/default.py, joinly/core.py, joinly/session.py, joinly/utils/clock.py
  Purpose and Scope
  Overview
  Architecture and Data Flow
    · Component Interaction Diagram
    · Pipeline Sequence Diagram
  DefaultTranscriptionController Implementation
    · Configuration Parameters
    · Protocol Requirements
    · Lifecycle Management
  VAD Worker Pipeline
    · VAD Worker State Diagram
    · Audio Chunk Processing
    · Utterance Boundary Detection
  STT Utterance Processing
    · Window Iterator
    · STT Streaming and Segment Creation
    · Latency Tracking
  Concurrency and Task Management
    · Task Lifecycle
    · Concurrent STT Processing
    · Queue Management
  Audio Format Conversion
    · Conversion Points
  Event System Integration
    · Event Types
    · No Speech Event
  Clock Synchronization
  Integration with MeetingSession

## · Speech Controller  (L6236)
  源文件: joinly/controllers/speech/default.py, joinly/types.py
  Architecture Overview
    · Speech Controller Architecture
  DefaultSpeechController Implementation
    · Core Components
    · Lifecycle Management
  Text Processing and Chunking
    · Text Chunking Strategy
  Audio Streaming and Interruption Handling
    · Producer-Consumer Pattern
    · Speech Interruption System
  Error Handling and Types
    · Speech-Specific Exceptions
    · Audio Data Types
  Integration with Audio Pipeline
    · Transcript Integration
    · Audio Format Conversion

## · Service Providers (VAD, STT, TTS)  (L6539)
  源文件: joinly/controllers/transcription/default.py, joinly/core.py, joinly/services/stt/deepgram.py, joinly/services/stt/whisper.py, joinly/services/tts/deepgram.py, joinly/services/tts/elevenlabs.py, joinly/session.py, joinly/utils/clock.py
  Purpose and Scope
  Protocol Interfaces
    · Core Service Protocols
    · Protocol Requirements
  Voice Activity Detection (VAD)
    · Available VAD Implementations
    · VAD Configuration
  Speech-to-Text (STT)
    · STT Implementation Architecture
    · WhisperSTT Implementation
    · DeepgramSTT Implementation
    · STT Configuration Comparison
  Text-to-Speech (TTS)
    · TTS Implementation Landscape
    · TTS Provider Comparison
    · KokoroTTS (Local)
    · DeepgramTTS (Cloud)
    · ElevenlabsTTS (Cloud)
  Service Resolution and Configuration
    · Resolution Architecture
    · Configuration Token Format
    · Resolution Process
  Audio Format Handling
    · Audio Format Specifications
    · Format Conversion Points
    · Common Audio Formats by Service
  Usage Tracking
    · Usage Recording Pattern
    · Tracked Metrics
  Integration with Controllers
    · Service Flow in Transcription Pipeline
    · Service Flow in Speech Pipeline
  Summary

## · Client SDK (joinly-client)  (L7113)
  源文件: client/joinly_client/agent.py, client/joinly_client/client.py, client/joinly_client/main.py, client/joinly_client/prompts.py, client/joinly_client/types.py, client/joinly_client/utils.py, client/pyproject.toml, joinly/utils/events.py
  Purpose and Scope
  Package Structure
  Core Architecture
    · Component Interaction Diagram
  JoinlyClient Component
    · Key Responsibilities
    · Resource Subscriptions
  ConversationalToolAgent Component
    · Agent Loop
    · Message History Management
    · Tool Call Handling
  Tool System
    · Tool Loading and Execution
    · Tool Schema Sanitization
    · McpClientConfig
  LLM Integration
    · Model Initialization
    · Model Request Flow
  Prompt System
    · Prompt Components
    · Prompt Structure
  Subscription and Callback System
    · Callback Registration and Flow
    · Callback Types
  Configuration and Settings
    · Settings Propagation
  Entry Points and Usage Modes
    · 1. CLI Mode
    · 2. High-Level `run()` Function
    · 3. Low-Level `JoinlyClient` API
  Dependencies

## · JoinlyClient API  (L7699)
  源文件: client/README.md, client/joinly_client/__init__.py, client/joinly_client/agent.py, client/joinly_client/client.py, client/joinly_client/main.py, client/joinly_client/prompts.py, client/joinly_client/types.py, client/joinly_client/utils.py, joinly/utils/events.py
  Purpose and Scope
  Overview
  Class Architecture
  Connection and Lifecycle Management
    · Initialization
    · Context Manager Pattern
    · Connection Process
  Resource Subscription System
    · MCP Resource URIs
    · Subscription Mechanism
  Callback System
    · Callback Types
    · Callback Registration
    · Callback Filtering
  API Methods
    · Meeting Control Methods
    · Audio and Chat Methods
    · Data Retrieval Methods
  Integration with FastMCP
    · Client Wrapper Pattern
    · Message Handler
    · Task Tracking
  Usage Example

## · ConversationalToolAgent  (L8315)
  源文件: client/joinly_client/agent.py, client/joinly_client/client.py, client/joinly_client/main.py, client/joinly_client/prompts.py, client/joinly_client/types.py, client/joinly_client/utils.py, joinly/utils/events.py
  Purpose and Scope
  Overview
  Architecture
    · Component Diagram
    · Agent Loop State Machine
  Initialization and Configuration
    · Constructor Parameters
    · System Prompt Structure
  Message Processing Loop
    · Utterance Event Flow
    · End Turn Conditions
  Tool Execution
    · Tool Call Processing
    · Binary Content Handling
    · Error Handling
  Message History Management
    · Message Limiting
    · Tool Result Truncation
    · Binary Content Filtering
  LLM Integration
    · Model Request Construction
    · Usage Tracking
  Async Context Management
  Integration Example
    · Complete Setup Flow
    · Typical Usage Pattern
  Configuration Reference
    · Complete Parameter Matrix
  Key Methods Reference

## · Usage Patterns and Examples  (L8926)
  源文件: client/README.md, client/joinly_client/__init__.py, client/joinly_client/agent.py, client/joinly_client/client.py, client/joinly_client/main.py, client/joinly_client/prompts.py, client/joinly_client/types.py, client/joinly_client/utils.py, examples/client_example.py, examples/client_example.py.lock, examples/config_notion.json, examples/config_tavily.json
  Purpose and Scope
  Overview of Usage Patterns
  Pattern 1: Command-Line Interface
    · Basic CLI Usage
    · CLI Configuration Flow
    · Advanced CLI Configuration
  Pattern 2: High-Level `run` Function
    · Direct Function Usage
    · Run Function Configuration
    · Run Function Parameters
    · Advanced Configuration Examples
  Pattern 3: Custom Agent with JoinlyClient
    · Low-Level Client API
    · Callback System Architecture
    · Callback Registration and Lifecycle
    · JoinlyClient Methods Reference
    · Advanced Custom Agent Examples
  Pattern 4: Integration with Other Frameworks
    · LangChain/LangGraph Integration
    · Integration with Other MCP Servers
  Comparison of Usage Patterns
    · Decision Matrix
    · Use Case Recommendations
  Common Configuration Patterns
    · Prompt Customization
    · LLM Provider Configuration
    · Settings Propagation
  Error Handling and Best Practices
    · Connection Management
    · Callback Exception Handling
    · Tool Execution Error Handling
    · Best Practices Summary

## · LLM and External Service Integration  (L10095)
  源文件: client/joinly_client/agent.py, client/joinly_client/client.py, client/joinly_client/main.py, client/joinly_client/prompts.py, client/joinly_client/types.py, client/joinly_client/utils.py, examples/client_example.py, examples/client_example.py.lock, examples/config_notion.json, examples/config_tavily.json, joinly/utils/events.py
  Purpose and Scope
  Supported LLM Providers
    · Provider Support Matrix
    · LLM Configuration Function
  ConversationalToolAgent Integration
    · Agent-LLM Interaction Architecture
    · Agent Initialization
    · LLM Request Construction
    · Message History Management
    · Usage Tracking
  External MCP Server Integration
    · MCP Configuration Format
    · Example: Tavily Web Search Integration
    · Example: Notion Integration
    · Tool Loading and Namespacing
    · Schema Sanitization
  Complete Integration Flow
  Configuration Examples
    · CLI Configuration
    · Programmatic Configuration
    · Alternative: LangChain Integration
  HTTP Header Configuration
  Best Practices
    · LLM Provider Selection
    · Tool Configuration
    · Message History Management
    · Usage Tracking

## · Development  (L10745)
  源文件: CHANGELOG.md, pyproject.toml, uv.lock
  Development Approach
  Development Environment Overview
    · Development Environment Diagram
  Development Workflow
    · Development Workflow Diagram
  Code Quality and Tooling
  System Dependencies
    · System Dependencies Diagram
  Package Management

## · Development Environment Setup  (L10959)
  源文件: CHANGELOG.md, pyproject.toml, uv.lock
  Development Container Architecture
    · Development Container Configuration
  VS Code Extensions and Configuration
  System Dependencies and Runtime Environment
    · System Package Installation
    · Runtime Directory Configuration
  Environment Variables
  Development Workflow Setup
    · Container Lifecycle Commands
    · Package Manager Integration

## · Build System and Dependencies  (L11140)
  源文件: CHANGELOG.md, client/pyproject.toml, pyproject.toml, uv.lock
  Purpose and Scope
  Workspace Structure
    · Package Organization
  UV Lock File System
    · Lock File Structure
  Project Configuration
    · Main Package (joinly)
    · Client Package (joinly-client)
  Dependency Management
    · Dependency Resolution Flow
    · Optional Dependencies
    · Cross-Package Dependency Graph
  Build System Configuration
    · Hatchling Build Backend
    · Entry Points and CLI Commands
  Code Quality Configuration
    · Ruff Linter and Formatter
    · Pyright Type Checker
    · Pytest Configuration
  Dependency Version Strategy
    · Version Constraints
    · Upgrade Strategy
  Summary

## · Deployment  (L11798)
  源文件: .env.example, README.md, client/README.md, client/joinly_client/__init__.py, joinly/services/tts/resemble.py
  Deployment Patterns
    · Pattern 1: Server + External Client
    · Pattern 2: All-in-One
    · Pattern 3: Custom Client
  Docker Image Variants
  Configuration Management
    · Environment Variables
    · CLI Arguments
    · HTTP Headers for Dynamic Configuration
  Runtime Architecture
  Environment Configuration
    · Default Environment Variables
    · CUDA-Specific Variables
  System Dependencies
    · Browser Dependencies
    · Audio/Video Dependencies  
    · Runtime Dependencies
  Asset Management
  Security Considerations
    · Non-Root Execution
    · Multi-Stage Builds
    · Minimal Base Images

## · Docker Images and Variants  (L12168)
  源文件: CHANGELOG.md, client/README.md, client/joinly_client/__init__.py, pyproject.toml, uv.lock
  Overview of Image Variants
  When to Use Each Variant
    · Base Image (`latest`)
    · CUDA Image (`cuda`)
    · Lite Image (`lite`)
  Dependency Comparison
  Build Architecture
    · Multi-Stage Build Process
    · Asset Management
  System Dependencies
    · Required System Packages
  Default Configuration
    · Environment Variables
    · Image Metadata
  Runtime Configuration
    · Port Exposure
    · Security Model
    · Entrypoint
  Docker Build Exclusions
  Deployment Examples
    · Basic Deployment
    · CUDA Deployment
    · Resource-Constrained Deployment

## · Deployment Modes  (L12547)
  源文件: .env.example, README.md, client/README.md, client/joinly_client/__init__.py, joinly/main.py, joinly/services/tts/resemble.py
  Overview of Deployment Patterns
  Mode 1: Server Mode (Separated Architecture)
    · Architecture
    · Starting the Server
    · Connecting External Client
    · Adding Additional MCP Servers
    · Advantages and Use Cases
  Mode 2: All-in-One Client Mode
    · Architecture
    · Starting All-in-One Mode
    · Configuration in All-in-One Mode
    · Advantages and Limitations
  Mode 3: Custom Client (Developer Mode)
    · Architecture
    · Using the JoinlyClient API
    · Client Settings Propagation
    · Using ConversationalToolAgent
    · Available Client Methods
    · Advantages and Use Cases
  Configuration Methods and Precedence
    · Configuration Sources
    · Environment Variables (.env file)
    · CLI Arguments
    · HTTP Headers (Client → Server)
    · Settings Resolution Flow
  Deployment Comparison
    · Feature Matrix
    · Resource Requirements
    · Selection Guidelines
  Common Deployment Scenarios
    · Scenario 1: Local Development
    · Scenario 2: Cloud Production
    · Scenario 3: Demo Presentation
    · Scenario 4: Research Experiment
    · Scenario 5: Multi-Meeting Server
  Debugging and Monitoring
    · VNC Server for Visual Debugging
    · Logging Levels