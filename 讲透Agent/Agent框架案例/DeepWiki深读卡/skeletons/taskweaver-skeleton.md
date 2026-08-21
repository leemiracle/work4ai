# Skeleton: taskweaver（19 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 10KB | 4 | ~4 | 11 |
| 2 | System Architecture | L278 | 17KB | 9 | ~4 | 12 |
| 3 | Core Components | L805 | 11KB | 7 | ~4 | 7 |
| 4 | Planner | L1109 | 11KB | 5 | ~4 | 15 |
| 5 | Session Management | L1467 | 12KB | 9 | ~4 | 9 |
| 6 | Memory and Communication System | L1843 | 17KB | 13 | ~3 | 11 |
| 7 | Code Interpreter | L2354 | 12KB | 7 | ~5 | 11 |
| 8 | LLM Integration | L2685 | 13KB | 5 | ~4 | 17 |
| 9 | Code Execution Service | L3080 | 17KB | 12 | ~10 | 18 |
| 10 | Plugin System | L3616 | 18KB | 6 | ~12 | 17 |
| 11 | External Roles | L4174 | 10KB | 6 | ~2 | 18 |
| 12 | User Interfaces | L4494 | 15KB | 6 | ~10 | 9 |
| 13 | Console Interface | L4931 | 12KB | 8 | ~5 | 9 |
| 14 | Web UI | L5323 | 9KB | 5 | ~2 | 10 |
| 15 | JSON Processing and Utilities | L5616 | 11KB | 6 | ~10 | 5 |
| 16 | Configuration and Verification | L5976 | 13KB | 5 | ~10 | 8 |
| 17 | Evaluation and Testing | L6363 | 14KB | 7 | ~7 | 11 |
| 18 | Observability and Tracing | L6848 | 12KB | 5 | ~6 | 9 |
| 19 | Deployment and Infrastructure | L7242 | 12KB | 5 | ~5 | 12 |


## · Overview  (L6)
  源文件: README.md, taskweaver/memory/attachment.py, taskweaver/planner/planner_prompt.yaml, website/blog/authors.yml, website/blog/evaluation.md, website/blog/experience.md, website/blog/local_llm.md, website/blog/plugin.md, website/blog/reasoning.md, website/blog/role.md, website/docusaurus.config.js
  Purpose and Scope
  What is TaskWeaver
  Core Architecture
  Key Concepts
    · Code-First Approach
    · Roles and Multi-Agent System
    · Plugin System
    · Memory and Communication
  How It Works Together
  Key Features
  Getting Started

## · System Architecture  (L278)
  源文件: README.md, taskweaver/chat/console/chat.py, taskweaver/memory/attachment.py, taskweaver/module/event_emitter.py, taskweaver/planner/planner.py, taskweaver/planner/planner_prompt.yaml, taskweaver/session/session.py, website/docs/FAQ.md, website/docs/advanced/observability.md, website/docs/code_execution.md, website/docs/llms/Keywords-AI.md, website/sidebars.js
  Purpose and Scope
  Architectural Overview
    · High-Level System Architecture
    · Core Data Flow Architecture
  Component Architecture Details
    · Session Management Core
    · Role-Based Orchestration System
    · Memory and Communication Architecture
    · LLM Integration Layer
    · Code Execution Architecture
    · Plugin and Extension System
  Event-Driven Architecture
    · Event System Structure
  Security and Isolation

## · Core Components  (L805)
  源文件: README.md, taskweaver/chat/console/chat.py, taskweaver/memory/attachment.py, taskweaver/module/event_emitter.py, taskweaver/planner/planner.py, taskweaver/planner/planner_prompt.yaml, taskweaver/session/session.py
  Component Architecture Overview
  Session Management
    · Session Components
    · Session Initialization
  Communication System
    · Communication Architecture
    · Attachment Types
  Event-Driven Architecture
    · Event Hierarchy
    · Event Flow Implementation
  Role System Integration
    · Role Integration Pattern
  Memory Integration
    · Memory Structure

## · Planner  (L1109)
  源文件: taskweaver/chat/console/chat.py, taskweaver/module/event_emitter.py, taskweaver/planner/planner.py, taskweaver/role/translator.py, taskweaver/session/session.py, tests/unit_tests/test_planner.py, tests/unit_tests/test_translator.py, website/blog/authors.yml, website/blog/evaluation.md, website/blog/experience.md, website/blog/local_llm.md, website/blog/plugin.md
  Architecture Overview
    · Core Planner Architecture
  Planning Process Flow
    · Task Processing Workflow
  Core Components
    · Planner Class Structure
    · Planning State Management
  Prompt Engineering and LLM Integration
    · System Prompt Construction
    · Response Validation and Error Handling
  Integration with Core Systems
    · Session Management Integration
    · Memory and Experience Integration  
  Configuration and Customization
    · PlannerConfig Options
    · Prompt Template Structure

## · Session Management  (L1467)
  源文件: .gitignore, playground/UI/.chainlit/config.toml, playground/UI/app.py, playground/UI/public/style_v1.css, taskweaver/chat/console/chat.py, taskweaver/module/event_emitter.py, taskweaver/planner/planner.py, taskweaver/session/session.py, website/docs/usage/webui.md
  Purpose and Scope
  Session Architecture
    · Core Session Components
  Session Lifecycle
    · Session Initialization
    · Session Termination
  Message Routing and Round Management
    · Round-Based Communication
    · Message Routing Logic
  Event System Integration
    · Event-Driven Communication
    · PostEventProxy for Streaming Updates
  Session State Management
    · Session Variables and Context
    · File Upload and Management
  User Interface Integration
    · Web UI Session Management
    · Console Interface Session Management
  Session Configuration
    · AppSessionConfig Options
    · Session Metadata

## · Memory and Communication System  (L1843)
  源文件: taskweaver/chat/console/chat.py, taskweaver/memory/compression.py, taskweaver/memory/experience.py, taskweaver/module/event_emitter.py, taskweaver/module/tracing.py, taskweaver/planner/planner.py, taskweaver/role/translator.py, taskweaver/session/session.py, tests/unit_tests/test_planner.py, tests/unit_tests/test_tracing.py, tests/unit_tests/test_translator.py
  Purpose and Scope
  Core Architecture
  Memory Subsystem
    · Memory and Round Management
    · Post and Attachment System
    · Shared Memory System
  Communication Subsystem
    · PostTranslator System
    · Real-time Communication Flow
  Event Subsystem
    · Event Architecture
    · PostEventProxy Pattern
  Advanced Memory Features
    · Round Compression
    · Experience System
  Integration with Core Components
    · Session Integration
    · Planner Integration

## · Code Interpreter  (L2354)
  源文件: taskweaver/code_interpreter/__init__.py, taskweaver/code_interpreter/code_executor.py, taskweaver/code_interpreter/code_interpreter/code_generator.py, taskweaver/code_interpreter/code_interpreter/code_interpreter.py, taskweaver/code_interpreter/code_interpreter_cli_only/code_interpreter_cli_only.py, taskweaver/code_interpreter/code_interpreter_plugin_only/code_interpreter_plugin_only.py, taskweaver/code_interpreter/code_verification.py, taskweaver/logging/__init__.py, taskweaver/memory/post.py, tests/unit_tests/test_code_generator.py, tests/unit_tests/test_code_verification.py
  Architecture Overview
    · Core Components Diagram
    · Component Responsibilities
  Code Generation Process
    · Generation Pipeline
    · Prompt Engineering Features
    · Auto Plugin Selection
  Code Execution Process
    · Execution Flow
    · Artifact Management
  Code Verification System
    · Verification Components
    · Security Controls
  Code Interpreter Variants
    · Variant Comparison
    · Plugin-Only Variant
  Configuration Options
    · Core Configuration
    · Code Generator Configuration
  Error Handling and Recovery
    · Retry Logic Flow

## · LLM Integration  (L2685)
  源文件: requirements.txt, taskweaver/code_interpreter/code_interpreter/code_generator_prompt.yaml, taskweaver/llm/__init__.py, taskweaver/llm/azure_ml.py, taskweaver/llm/base.py, taskweaver/llm/google_genai.py, taskweaver/llm/mock.py, taskweaver/llm/ollama.py, taskweaver/llm/openai.py, taskweaver/llm/placeholder.py, taskweaver/llm/qwen.py, taskweaver/llm/sentence_transformer.py
  Purpose and Scope
  Architecture Overview
    · LLM Integration Architecture
  LLM API Facade
    · Provider Mapping and Initialization
  Service Abstractions
    · CompletionService Interface
    · EmbeddingService Interface
  Provider Implementations
    · Provider Implementation Matrix
    · OpenAI Service Implementation
    · Local LLM Support
  Configuration System
    · Configuration Hierarchy
    · Configuration Parameters
  Advanced Features
    · Stream Smoothing
    · Mock and Testing Infrastructure
    · Function Calling and Tools Support
  Error Handling and Resilience
    · Provider-Specific Error Handling
    · Fallback Mechanisms

## · Code Execution Service  (L3080)
  源文件: .gitattributes, docker/ces_container/Dockerfile, docker/ces_container/entrypoint.sh, project/examples/planner_examples/example-planner-echo.yaml, project/examples/planner_examples/example-planner-recepta.yaml, scripts/build_executor.ps1, taskweaver/ces/__init__.py, taskweaver/ces/environment.py, taskweaver/ces/kernel/ctx_magic.py, taskweaver/ces/kernel/ext.py, taskweaver/ces/kernel/launcher.py, taskweaver/ces/manager/sub_proc.py
  Architecture Overview
  Service Factory and Configuration
  Environment Management
    · Environment Class
    · Session Lifecycle
  Execution Modes
    · Local Mode
    · Container Mode
  Kernel Integration
    · Kernel Launcher
    · Magic Commands
  Runtime Execution
    · Executor Class
    · Code Execution Flow
  Container Infrastructure
    · Docker Image Build
    · Container Security
  Client Interface
    · SubProcessClient
  Testing and Validation

## · Plugin System  (L3616)
  源文件: project/plugins/README.md, taskweaver/ext_role/web_explorer/README.md, taskweaver/ext_role/web_search/README.md, taskweaver/memory/plugin.py, taskweaver/misc/component_registry.py, taskweaver/plugin/base.py, tests/unit_tests/test_embedding.py, tests/unit_tests/test_plugin.py, tests/unit_tests/test_plugin_selector.py, website/blog/authors.yml, website/blog/evaluation.md, website/blog/experience.md
  Plugin Architecture Overview
    · Core Plugin Architecture
    · Plugin Data Flow
  Plugin Components
    · PluginEntry
    · PluginSpec
    · PluginParameter
  Plugin Registry and Management
    · PluginRegistry
    · Plugin Module Configuration
  Plugin Selection and Embeddings
    · Plugin Selection Architecture
    · PluginMetaData Structure
  Plugin Base Class and Context
    · Plugin Base Implementation
  Plugin Examples and Structure
    · Available Plugin Types
    · Plugin Development Structure
  Plugin Integration with Code Execution
    · Code Generation and Plugin Integration
    · Plugin Lifecycle in Code Execution

## · External Roles  (L4174)
  源文件: project/examples/planner_examples/example-planner-echo.yaml, project/examples/planner_examples/example-planner-recepta.yaml, taskweaver/ces/runtime/executor.py, taskweaver/ext_role/image_reader/__init__.py, taskweaver/ext_role/image_reader/image_reader.py, taskweaver/ext_role/image_reader/image_reader.role.yaml, taskweaver/ext_role/recepta/__init__.py, taskweaver/ext_role/recepta/recepta.py, taskweaver/ext_role/recepta/recepta.role.yaml, taskweaver/llm/util.py, website/blog/authors.yml, website/blog/evaluation.md
  Role System Overview
  Built-in External Roles
    · ImageReader Role
    · Recepta Role
  External Role Development
    · Base Role Architecture
    · Role Configuration Files
  Role Lifecycle and Integration
    · Role Loading and Registration
    · Communication Protocol
  Configuration and Deployment
    · Session Role Configuration
    · Role-Specific Configuration

## · User Interfaces  (L4494)
  源文件: .gitignore, playground/UI/.chainlit/config.toml, playground/UI/app.py, playground/UI/public/style_v1.css, taskweaver/chat/console/chat.py, taskweaver/module/event_emitter.py, taskweaver/planner/planner.py, taskweaver/session/session.py, website/docs/usage/webui.md
  Overview of Available Interfaces
  Interface Architecture
  Console CLI
    · Features
    · Core Components
    · Usage 
  Web UI
    · Implementation
    · Key Components
    · Configuration
    · Usage
  Library API
    · Core Usage Pattern
    · Key Components for Integration
    · Basic Usage Example
    · Custom Event Handler Implementation
  File Upload and Attachment Support
    · File Upload Flow
    · File Handling Implementation
  Interface Feature Comparison
  Integration with TaskWeaver Architecture

## · Console Interface  (L4931)
  源文件: taskweaver/chat/console/chat.py, taskweaver/module/event_emitter.py, taskweaver/planner/planner.py, taskweaver/session/session.py, website/docs/FAQ.md, website/docs/advanced/observability.md, website/docs/code_execution.md, website/docs/llms/Keywords-AI.md, website/sidebars.js
  Architecture Overview
  Main Console Application
    · Core Application Structure
    · Command System Implementation
  Real-Time Update Handler
    · Event Processing Architecture
    · Animation and Display System
  User Input Management
    · Input Processing Flow
  Session Integration
    · Session Interaction Pattern
  File Upload and Management
    · File Handling Architecture
  Error Handling and User Feedback
    · Error Management System

## · Web UI  (L5323)
  源文件: .gitignore, playground/UI/.chainlit/config.toml, playground/UI/app.py, playground/UI/public/style_v1.css, website/docs/FAQ.md, website/docs/advanced/observability.md, website/docs/code_execution.md, website/docs/llms/Keywords-AI.md, website/docs/usage/webui.md, website/sidebars.js
  Overview
  Architecture
  Key Components
    · ChainLitMessageUpdater
    · Session Management
    · Message Processing
    · File and Image Handling
  Content Formatting
    · Plan Display
    · Code Blocks
    · Execution Results
  Usage Instructions
  Security Considerations
  Configuration Options
  Integration with TaskWeaver Core

## · JSON Processing and Utilities  (L5616)
  源文件: taskweaver/role/translator.py, taskweaver/utils/json_parser.py, tests/unit_tests/test_json_parser.py, tests/unit_tests/test_planner.py, tests/unit_tests/test_translator.py
  Architecture Overview
    · JSON Processing Data Flow
  Streaming JSON Parser
    · Parser Event System
    · Parser State Management
    · Key Parser Functions
  Post Translator
    · Translation Architecture
    · Parser Version Comparison
    · Post Structure Translation
  Usage Patterns
    · Early Stop Processing
    · Streaming Response Handling
    · Error Handling
  Integration with TaskWeaver Components
    · Memory System Integration
    · Event System Integration
  Testing and Validation
    · Test Categories

## · Configuration and Verification  (L5976)
  源文件: taskweaver/code_interpreter/__init__.py, taskweaver/code_interpreter/code_verification.py, tests/unit_tests/test_code_verification.py, website/docs/FAQ.md, website/docs/advanced/observability.md, website/docs/code_execution.md, website/docs/llms/Keywords-AI.md, website/sidebars.js
  Configuration System Overview
  Code Verification System
  Security Configuration Options
  Execution Environment Configuration
  Magic Command Handling
  Configuration File Structure
  Error Handling and Validation Messages
  Troubleshooting Configuration Issues

## · Evaluation and Testing  (L6363)
  源文件: auto_eval/evaluator.py, auto_eval/taskweaver_eval.py, taskweaver/code_interpreter/code_interpreter_cli_only/code_generator_cli_only.py, website/blog/authors.yml, website/blog/evaluation.md, website/blog/experience.md, website/blog/local_llm.md, website/blog/plugin.md, website/blog/reasoning.md, website/blog/role.md, website/docusaurus.config.js
  Evaluation Philosophy
  Core Components
    · VirtualUser Class
    · Evaluator Class
    · ScoringPoint Configuration
  Evaluation Workflow
    · Single Case Evaluation
    · Batch Evaluation
  Test Case Configuration
    · Evaluation Case Structure
    · Configuration Fields
  LLM Integration for Evaluation
    · Supported LLM Providers
    · Prompt Templates
  Running Evaluations
    · Command Line Interface
    · CLI Arguments
    · Working Directory Management
  Extending the Evaluation Framework
    · Adapting for Other Agents
    · Custom Scoring Mechanisms

## · Observability and Tracing  (L6848)
  源文件: taskweaver/memory/compression.py, taskweaver/memory/experience.py, taskweaver/module/tracing.py, tests/unit_tests/test_tracing.py, website/docs/FAQ.md, website/docs/advanced/observability.md, website/docs/code_execution.md, website/docs/llms/Keywords-AI.md, website/sidebars.js
  Overview
  OpenTelemetry Integration
    · Core Tracing Components
    · Span and Metrics Management
    · Configuration Options
  Tracing Implementation Patterns
    · Automatic Tracing with Decorators
    · LLM Interaction Tracing
  AgentOps Integration
    · Integration Setup
    · Event Tracking Capabilities
    · Usage Modes and Limitations
  Exporter Configuration
  Testing and Validation

## · Deployment and Infrastructure  (L7242)
  源文件: .gitattributes, .github/workflows/deploy-website.yaml, .github/workflows/pytest.yml, docker/ces_container/Dockerfile, docker/ces_container/entrypoint.sh, scripts/build_executor.ps1, taskweaver/ces/kernel/ctx_magic.py, taskweaver/ces/kernel/ext.py, taskweaver/ces/kernel/launcher.py, tests/unit_tests/test_environment.py, website/package-lock.json, website/package.json
  Purpose and Scope
  Deployment Modes
    · Local Mode
    · Container Mode
  Container Infrastructure
    · Docker Image Components
    · Container Runtime Configuration
  CI/CD Pipelines
    · Testing Pipeline
    · Website Deployment Pipeline
  Environment Configuration
    · Kernel Configuration Variables
    · Magic Command Integration
  Infrastructure Requirements
    · System Dependencies
    · Security Considerations
    · Testing Infrastructure