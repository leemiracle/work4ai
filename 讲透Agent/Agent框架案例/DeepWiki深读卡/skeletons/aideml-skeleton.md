# Skeleton: aideml（30 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 12KB | 4 | ~7 | 3 |
| 2 | Installation & Setup | L392 | 10KB | 4 | ~2 | 6 |
| 3 | Key Concepts | L761 | 7KB | 4 | ~5 | 4 |
| 4 | Example Tasks & Sample Results | L983 | 7KB | 2 | ~4 | 14 |
| 5 | System Architecture | L1139 | 14KB | 3 | ~4 | 6 |
| 6 | Experiment Execution Flow | L1518 | 14KB | 7 | ~8 | 8 |
| 7 | Configuration System | L1879 | 11KB | 3 | ~3 | 3 |
| 8 | User Interfaces | L2197 | 10KB | 3 | ~8 | 7 |
| 9 | Web UI | L2486 | 18KB | 8 | ~7 | 4 |
| 10 | Command Line Interface | L2869 | 5KB | 2 | ~5 | 3 |
| 11 | Python API | L3008 | 9KB | 4 | ~4 | 2 |
| 12 | Docker | L3337 | 7KB | 3 | ~5 | 3 |
| 13 | LLM Backend System | L3607 | 11KB | 4 | ~6 | 2 |
| 14 | Backend Architecture & Router | L3882 | 14KB | 4 | ~10 | 2 |
| 15 | OpenAI Integration | L4287 | 23KB | 10 | ~12 | 1 |
| 16 | Anthropic Integration | L4974 | 13KB | 9 | ~10 | 1 |
| 17 | Gemini Integration | L5384 | 9KB | 6 | ~7 | 1 |
| 18 | OpenRouter Integration | L5615 | 9KB | 2 | ~4 | 1 |
| 19 | Backend Utilities & Function Calling | L5864 | 13KB | 4 | ~5 | 2 |
| 20 | Core Subsystems | L6238 | 7KB | 3 | ~4 | 7 |
| 21 | Agent & Search System | L6425 | 11KB | 5 | ~5 | 5 |
| 22 | Code Interpreter | L6693 | 16KB | 4 | ~9 | 2 |
| 23 | Journal & Solution Tree | L7066 | 7KB | 2 | ~0 | 2 |
| 24 | Visualization & Reporting | L7250 | 8KB | 3 | ~7 | 4 |
| 25 | Metrics & Evaluation | L7431 | 9KB | 4 | ~6 | 3 |
| 26 | Developer Guide | L7701 | 7KB | 2 | ~2 | 3 |
| 27 | Project Structure | L7942 | 10KB | 7 | ~10 | 3 |
| 28 | Contributing Guidelines | L8266 | 9KB | 6 | ~7 | 7 |
| 29 | Dependencies & Requirements | L8486 | 9KB | 3 | ~19 | 4 |
| 30 | Glossary | L8736 | 7KB | 2 | ~2 | 13 |


## · Overview  (L6)
  源文件: README.md, aide/__init__.py, setup.py
  Purpose and Scope
  What is AIDE ML?
  Core Architecture
  Agentic Tree Search Workflow
  User Interaction Model
    · CLI Usage
    · Python API Usage
    · Web UI Usage
  Key Concepts
    · Task Specification
    · Solution Tree
    · Agentic Search
  Output Artifacts
  Configuration and Extensibility
  Multi-Provider LLM Support
  Research Context

## · Installation & Setup  (L392)
  源文件: .dockerignore, Dockerfile, README.md, aide/utils/metric.py, requirements.txt, setup.py
  Standard Installation
    · Basic Installation
  Dependency Structure
    · Installation Architecture
    · Dependency Categories
  API Key Configuration
    · Supported Providers
    · Setting API Keys
  Local LLM Setup
    · Configuration Flow
    · Ollama Example
  Docker Installation
    · Docker Build and Run
    · Docker Commands
  Verification

## · Key Concepts  (L761)
  源文件: README.md, aide/journal.py, aide/utils/metric.py, requirements.txt
  Overview: What AIDE Does
  Agentic Tree Search
    · How It Works
  Solution Tree Structure
    · Tree Components
  Nodes: Code Solutions and Their Context
    · Node Anatomy
    · Node Stages
  Metrics: Guiding the Search
    · Optimization Logic
  Task Specification: Goal and Eval
  The Journal: Recording the Search
    · Key Capabilities
  LLM-Driven Optimization Process

## · Example Tasks & Sample Results  (L983)
  源文件: LICENSE, aide/agent.py, aide/example_tasks/bitcoin_price.md, aide/example_tasks/bitcoin_price/BTC-USD.csv, aide/example_tasks/house_prices.md, aide/example_tasks/house_prices/data_description.txt, aide/example_tasks/house_prices/sample_submission.csv, aide/example_tasks/house_prices/test.csv, aide/example_tasks/house_prices/train.csv, sample_results/bike-sharing-demand.py, sample_results/digit-recognizer.py, sample_results/house-prices-advanced-regression-techniques.py
  Purpose and Scope
  Included Example Tasks
    · Task Specification Details
  Benchmark Solutions (sample_results/)
    · Key Benchmark Examples
    · Code Generation Patterns
  Custom Task Structure
    · Data Flow & Prompting
    · Implementation Guidelines
    · Review Mechanism
  Task Execution & Evaluation

## · System Architecture  (L1139)
  源文件: LICENSE, aide/__init__.py, aide/agent.py, aide/example_tasks/bitcoin_price/BTC-USD.csv, aide/example_tasks/house_prices/data_description.txt, aide/run.py
  Purpose and Scope
  Core Components Overview
  Component Relationships
  Module Structure
  Key Abstractions and Their Roles
    · Experiment Class
    · Agent Class
    · Interpreter Class
    · Journal and Node Classes
    · Backend Query Function
  Data Flow Architecture
  Layered Architecture
    · Layer 1: User Interface (Entry Points)
    · Layer 2: Orchestration
    · Layer 3: Core Execution
    · Layer 4: LLM Abstraction
  Execution Context and Isolation
  Component Initialization Sequence

## · Experiment Execution Flow  (L1518)
  源文件: .github/workflows/linter.yml, LICENSE, aide/__init__.py, aide/agent.py, aide/example_tasks/bitcoin_price/BTC-USD.csv, aide/example_tasks/house_prices/data_description.txt, aide/interpreter.py, aide/run.py
  Overview
  Initialization Phase
  Iterative Search Loop
  Node Types and Solution Tree
    · Solution Tree Hierarchy
    · Node Data Structure
  Search Policy: Node Selection Strategy
  Code Generation: Drafts, Debugs, and Improvements
    · Draft Generation: `Agent._draft()`
    · Debug Generation: `Agent._debug()`
    · Improvement Generation: `Agent._improve()`
  Execution and Evaluation Pipeline
    · Agent.step() Workflow
    · LLM-Based Evaluation: `review_func_spec`
    · Code Execution: `Interpreter.run()`
  Metric-Guided Selection and Pruning
    · Journal Tree Queries
    · Best Node Selection
  Output Phase
    · Best Solution Extraction
    · Optional Report Generation

## · Configuration System  (L1879)
  源文件: aide/utils/config.py, aide/utils/config.yaml, setup.py
  Purpose and Scope
  Configuration Architecture
    · Configuration Loading Flow
  Configuration Schema
    · Dataclass Hierarchy
    · Configuration Dataclass Definitions
  Default Configuration File
    · Core Parameters
    · Execution Configuration
    · Agent Configuration
  Configuration Loading and Merging
    · Load Process
    · CLI Override Mechanism
  Configuration Validation
    · Validation Rules
    · Path Resolution
    · Schema Validation
  Experiment Naming and Directory Structure
    · Automatic Naming
    · Workspace Preparation
  Task Description Loading
  Saving Experiment Results

## · User Interfaces  (L2197)
  源文件: README.md, aide/__init__.py, aide/run.py, Web UI, Command Line Interface, Python API, Docker
  Purpose and Scope
  Interface Options Summary
  Architecture: Convergence on Shared Core
    · Interface Integration Architecture
  Entry Points and Initialization
    · Entry Point Code Paths
  Data Flow Across Interfaces
    · Input → Processing → Output
  Interface Selection Guidance
    · Decision Matrix
  Common Interface Patterns
    · Configuration Override Hierarchy
  Output Artifacts (Universal)
  Interface Implementation Details
    · CLI Implementation
    · Python API Implementation
    · Web UI Implementation
    · Docker Implementation

## · Web UI  (L2486)
  源文件: .streamlit/config.toml, aide/webui/__init__.py, aide/webui/app.py, aide/webui/style.css
  Purpose and Architecture
    · Component Overview
    · Key Class Structure
  User Interface Components
    · Input Section
    · Sidebar Configuration
  Experiment Execution Flow
    · File Handling Implementation
  Results Display System
    · Data Collection and Processing
  Styling and Customization
    · CSS Architecture
    · Streamlit Configuration
  Session State Management

## · Command Line Interface  (L2869)
  源文件: README.md, aide/run.py, setup.py
  CLI Entry Point and Implementation
    · CLI Data Flow and Code Entities
  Usage and Parameters
    · Core Parameters
    · Advanced Search & Model Options
  Execution Lifecycle
    · Internal Execution Flow
  Output and Artifacts
    · Output Locations
    · Terminal Visualization

## · Python API  (L3008)
  源文件: README.md, aide/__init__.py
  Purpose and Scope
  API Overview
  Experiment Class
    · Class Definition
  Constructor: `__init__`
    · Signature
    · Parameters
    · Initialization Flow
  Run Method: `run()`
    · Signature
    · Parameters
    · Return Value
    · Execution Flow
    · Implementation Details
  Solution Dataclass
    · Definition
    · Fields
  Internal Component Interaction
    · Data Flow Diagram
  Complete Usage Example
  Configuration System Integration

## · Docker  (L3337)
  源文件: .dockerignore, Dockerfile, README.md
  Overview
  Building the Docker Image
    · Basic Build
    · Build Process
  Running Containers
    · Volume Mount Architecture
  Standard Execution Pattern
    · Complete Run Command
  Environment Variables
    · API Credentials
  File System Layout Inside Container
    · Container Directory Structure
  Common Usage Patterns
    · Pattern 1: Using Claude Models
    · Pattern 2: Local LLM with Ollama
  Accessing Results
  Limitations and Considerations
    · Permissions
    · Network

## · LLM Backend System  (L3607)
  源文件: aide/backend/__init__.py, aide/backend/utils.py
  Purpose and Scope
  System Architecture
    · Backend System Component Structure
  Query Flow
    · LLM Query Processing Sequence
  Main Interface
  Provider Routing
    · Provider Determination Logic
  Function Specification
  Error Handling and Retries
  Prompt Handling
    · Prompt Formatting Pipeline
  Integration with AIDE Architecture
    · Backend System in AIDE Context
  Summary

## · Backend Architecture & Router  (L3882)
  源文件: aide/backend/__init__.py, aide/backend/utils.py
  Purpose & Scope
  Backend Router Architecture
  The Query Function Interface
  Provider Determination Logic
    · Provider Routing Rules
  Provider Registry & Adapter Pattern
    · Adapter Pattern Benefits
  Query Execution Flow
    · Query Return Values
  Prompt Compilation System
    · PromptType Definition
  Dataset
  Features
  Function Calling Abstraction
    · Provider-Specific Tool Formats
  Type System
  Backend Module Imports
  Error Handling & Logging

## · OpenAI Integration  (L4287)
  源文件: aide/backend/backend_openai.py
  Purpose and Scope
  Architecture Overview
  Supported Models and API Formats
    · Model Recognition Patterns
    · API Format Selection Logic
  Client Configuration and Initialization
    · Client Instances
    · Initialization Flow
  Query Function Interface
    · Function Signature
    · Parameters and Return Values
    · Parameter Processing
  Function Calling Support
    · Function Specification Format
    · Function Call Processing Flow
    · Graceful Degradation
  Error Handling and Retry Logic
    · Retryable Exceptions
    · Retry Mechanism
  Response Parsing and Token Tracking
    · Output Extraction by API Type
    · Metadata Collection
    · Logging
  Custom Endpoint Support
    · Configuration
    · Custom Endpoint Decision Logic
    · Example Usage Patterns
  Integration with AIDE System
    · Call Chain
    · Token Tracking
  Summary

## · Anthropic Integration  (L4974)
  源文件: aide/backend/backend_anthropic.py
  Purpose and Scope
  Module Overview
    · Key Components
  Client Initialization
  Model Aliases
  Query Function Interface
    · Return Values
  Message Format Requirements
    · System Message Handling
  Tool Use (Function Calling)
    · Tool Use Configuration
  Response Processing
    · Response Type Detection
    · Usage Tracking
  Error Handling & Retries
  Parameter Filtering & Defaults
  Code Entity Reference Map
  Integration with AIDE Components
  Logging and Observability

## · Gemini Integration  (L5384)
  源文件: aide/backend/backend_gemini.py
  Architecture Overview
    · Gemini Backend Integration Flow
    · Backend System Integration
  Configuration and Setup
    · API Key Configuration
    · Client Initialization
  Query Interface and Function Calling
    · Main Query Function
    · Function Calling Support
  Error Handling and Retry Logic
    · Exception Handling Strategy
    · Retry Configuration
  Message Processing and Response Handling
    · Message Format Adaptation
    · Response Processing

## · OpenRouter Integration  (L5615)
  源文件: aide/backend/backend_openrouter.py
  Purpose and Role
  Client Initialization
    · Setup Function
  Query Function Execution
  Function Calling Limitation
  Message Format Handling
    · Message Construction
  Provider Routing Configuration
    · Provider Preferences
  API Call Execution and Response Processing
    · Retry Mechanism
    · Response Extraction
  Logging and Observability
    · Log Events
  Configuration Requirements
    · Environment Variables
    · Model Configuration

## · Backend Utilities & Function Calling  (L5864)
  源文件: aide/backend/__init__.py, aide/backend/utils.py
  Purpose and Scope
  Type Definitions
  FunctionSpec: Cross-Provider Tool Definition
    · Overview
    · Architecture
    · Conversion Methods
    · Schema Validation
  Retry Mechanism: backoff_create
    · Function Signature and Behavior
    · Backoff Strategy
    · Parameters
    · Backoff Configuration
    · Usage in Backends
  Message Formatting: opt_messages_to_list
    · Behavior
  Prompt Compilation: compile_prompt_to_md
    · Overview
    · Compilation Rules
    · Format Examples
  Unified Query Entry Point
    · Provider Determination Logic
    · Data Flow in `query()`
  Integration Summary

## · Core Subsystems  (L6238)
  源文件: .github/workflows/linter.yml, LICENSE, aide/agent.py, aide/example_tasks/bitcoin_price/BTC-USD.csv, aide/example_tasks/house_prices/data_description.txt, aide/interpreter.py, aide/journal.py
  Overview
  System Architecture
  Subsystem Details
    · Agent & Search System (#5.1)
    · Code Interpreter (#5.2)
    · Journal & Solution Tree (#5.3)
    · Visualization & Reporting (#5.4)
    · Metrics & Evaluation (#5.5)
  Agent-Driven Execution Flow
  Key Data Relationships
  Integration Points

## · Agent & Search System  (L6425)
  源文件: LICENSE, aide/agent.py, aide/example_tasks/bitcoin_price/BTC-USD.csv, aide/example_tasks/house_prices/data_description.txt, aide/utils/config.py
  Agent Architecture Overview
  Core Agent Class and Initialization
  Search Hyperparameters
  Search Policy and Node Selection
  Code Generation Modes and LLM Interaction
    · Draft Mode (`_draft`)
    · Improve Mode (`_improve`) 
    · Debug Mode (`_debug`)
  Result Analysis and Feedback Loop
  Step Execution and Integration
  Prompt Engineering Components

## · Code Interpreter  (L6693)
  源文件: .github/workflows/linter.yml, aide/interpreter.py
  Purpose and Scope
  Architecture Overview
    · Class Structure
  Multiprocessing Isolation Model
  Execution Flow
    · Sequence Diagram
  Queue-Based Communication System
    · Queue Purposes
    · RedirectQueue Implementation
    · State Signals
  Timeout Enforcement Mechanism
    · Timeout Strategy
  Output Capture and Exception Handling
    · Output Collection
    · Exception Handling
  Session Management
    · Process Lifecycle
    · Cleanup Procedure
  Configuration Options
    · Working Directory Behavior
    · Warning Suppression
  Integration with AIDE System

## · Journal & Solution Tree  (L7066)
  源文件: aide/journal.py, aide/utils/serialize.py
  Purpose and Scope
  Overview
    · Data Flow & System Mapping
  Node Data Structure
    · Key Attributes
    · Node Stages
  Journal Class Interface
    · Best Node Selection
    · Filtering Properties
  Serialization and Persistence
    · Serialization Logic (`dumps_json`)
    · Deserialization Logic (`loads_json`)
  Interactive Sessions
  Summary of Data Flow

## · Visualization & Reporting  (L7250)
  源文件: aide/journal2report.py, aide/utils/tree_export.py, aide/utils/viz_templates/template.html, aide/utils/viz_templates/template.js
  Tree Visualization System
    · Tree Export Pipeline
    · Graph Layout Generation
    · Interactive HTML Generation
  Report Generation
    · Report Generation Process
    · Report Structure and Content
  UI Implementation Details (template.js)
    · Key JavaScript Components
    · Data Structure for Visualization

## · Metrics & Evaluation  (L7431)
  源文件: aide/utils/metric.py, aide/utils/response.py, requirements.txt
  Purpose & Scope
  MetricValue Class
    · Data Structure
    · Key Properties
    · Comparison Semantics
    · String Representation
  WorstMetricValue for Error Handling
    · Characteristics
  Metric Computation & Integration
    · Metric Flow Through System
    · Metric Computation Context
  MetricValue in Journal Operations
    · Best Node Selection
    · Node Pruning
  Serialization & Persistence
  Type Safety & Validation

## · Developer Guide  (L7701)
  源文件: .github/ISSUE_TEMPLATE/bug_report.yml, Makefile, setup.py
  Development Environment Setup
    · Installing for Development
    · Setting Up API Keys
    · Running the System
  Repository Structure
    · Package Layout
  Entry Points and Core Classes
    · Command Line Entry Point
    · Python API Entry Point
    · Web UI Entry Point
  Development Workflow
    · Code Organization Principles
    · Dependency Management
  Extension Points
    · Adding a New LLM Backend
    · Customizing Search Strategy
    · Adding Configuration Options
  Contributing Guidelines

## · Project Structure  (L7942)
  源文件: aide/utils/__init__.py, aide/utils/data_preview.py, setup.py
  Package Overview
    · High-Level Directory Structure
  Core Module Organization
    · Entry Points and Interfaces
    · Backend Integration Layer
  Data Structures and Utilities
    · Metrics System
    · Data Preview and Processing
  Configuration and Templates
  Dependencies and Requirements
    · Core Dependencies
    · Package Metadata
  Example Tasks and Workspaces
    · Example Task Structure
    · Runtime Workspaces

## · Contributing Guidelines  (L8266)
  源文件: .github/ISSUE_TEMPLATE/bug_report.yml, .github/ISSUE_TEMPLATE/feature_request.md, .github/ISSUE_TEMPLATE/technical_proposal.md, .github/pull_request_template.md, .github/workflows/linter.yml, Makefile, aide/interpreter.py
  Getting Started
    · Development Setup for AIDE ML
  Types of Contributions
    · Bug Reports
    · Feature Requests
    · Technical Proposals
  Code Standards for AIDE ML
    · Linting and Formatting Pipeline
  Pull Request Requirements
  AIDE ML Repository Architecture
  Best Practices for Contributors

## · Dependencies & Requirements  (L8486)
  源文件: .github/workflows/python-publish.yml, aide/utils/metric.py, requirements.txt, setup.py
  Overview
  Core AIDE Requirements (Tier 1)
    · LLM Backend Integration
    · Configuration & Data Management
    · Data Science Stack
    · User Interface & Logging
    · Utilities
  Agent Requirements (Tier 2)
    · Deep Learning & NLP
    · Classical ML & Optimization
    · Computer Vision & Processing
    · Domain-Specific & Utilities
  Dependency Management
    · Installation via setup.py
    · Dependency Strategy
    · Rationale for Two-Tier Structure

## · Glossary  (L8736)
  源文件: .github/workflows/linter.yml, LICENSE, README.md, aide/agent.py, aide/backend/__init__.py, aide/backend/utils.py, aide/example_tasks/bitcoin_price/BTC-USD.csv, aide/example_tasks/house_prices/data_description.txt, aide/interpreter.py, aide/journal.py, aide/utils/config.py, aide/utils/metric.py
  Core Concepts
    · Agentic Tree Search
    · Journal
    · Node
    · Stage Name
  Technical Definitions & Code Pointers
    · Interpreter
    · MetricValue
    · FunctionSpec
  Architecture Visualizations
    · Natural Language to Code Entity Mapping
    · Code Execution & Feedback Flow
  Summary Table of Key Terms