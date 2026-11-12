# Skeleton: vectara-agentic（26 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 8KB | 2 | ~3 | 7 |
| 2 | Architecture | L215 | 17KB | 8 | ~3 | 3 |
| 3 | Key Concepts | L706 | 9KB | 9 | ~4 | 6 |
| 4 | Core Components | L986 | 11KB | 7 | ~3 | 2 |
| 5 | Agent System | L1322 | 17KB | 11 | ~8 | 4 |
| 6 | Tool Factory System | L1860 | 10KB | 7 | ~5 | 4 |
| 7 | Workflow Engine | L2221 | 9KB | 3 | ~4 | 2 |
| 8 | Prompt System | L2491 | 9KB | 7 | ~8 | 2 |
| 9 | Installation and Configuration | L2764 | 7KB | 3 | ~2 | 5 |
| 10 | Dependencies and Setup | L3031 | 11KB | 6 | ~12 | 4 |
| 11 | Agent Configuration | L3419 | 9KB | 4 | ~6 | 2 |
| 12 | LLM Provider Setup | L3754 | 8KB | 4 | ~3 | 8 |
| 13 | Usage Guide | L4020 | 10KB | 3 | ~0 | 2 |
| 14 | Basic Usage | L4306 | 8KB | 7 | ~7 | 5 |
| 15 | Available Tools | L4591 | 10KB | 6 | ~10 | 6 |
| 16 | Advanced Features | L4957 | 11KB | 6 | ~3 | 6 |
| 17 | API and Endpoints | L5314 | 10KB | 2 | ~9 | 8 |
| 18 | REST API | L5682 | 8KB | 4 | ~10 | 6 |
| 19 | OpenAI-Compatible Endpoints | L5962 | 9KB | 4 | ~7 | 6 |
| 20 | Development and Testing | L6323 | 7KB | 4 | ~2 | 4 |
| 21 | Testing Framework | L6549 | 8KB | 5 | ~3 | 5 |
| 22 | Development Environment | L6819 | 6KB | 3 | ~1 | 4 |
| 23 | Release Process | L7058 | 7KB | 5 | ~9 | 4 |
| 24 | Deployment | L7271 | 7KB | 4 | ~4 | 4 |
| 25 | Docker Deployment | L7508 | 6KB | 3 | ~4 | 2 |
| 26 | Documentation Site | L7714 | 7KB | 5 | ~5 | 4 |


## · Overview  (L6)
  源文件: README.md, docs/index.md, requirements-dev.txt, setup.py, tests/test_agent_planning.py, tests/test_agent_type.py, vectara_agentic/__init__.py
  Purpose and Scope
  System Architecture Overview
  Core Framework Components
    · Agent System
    · Tool Factory Pattern
    · Configuration Management
  Integration with LlamaIndex
  Key Features and Capabilities
  Quick Start Example
  Related Documentation

## · Architecture  (L215)
  源文件: requirements.txt, vectara_agentic/agent.py, vectara_agentic/tools.py
  System Overview
    · High-Level Component Mapping
  Core Agent Architecture
    · Agent Types and Execution Flow
  Tool Factory System
    · VectaraToolFactory Architecture
    · ToolsFactory and External Integrations
  LLM Provider Layer
    · LLM Provider Integration
  Data Flow and Processing Pipeline
    · Query Processing Flow
  Technology Stack and Dependencies
    · Core Dependencies
    · LLM Provider Dependencies
  Configuration and Observability
    · Configuration Architecture

## · Key Concepts  (L706)
  源文件: README.md, docs/index.md, requirements-dev.txt, tests/test_agent_planning.py, tests/test_agent_type.py, vectara_agentic/_prompts.py
  Core Concepts
    · Agents
    · Tools
    · RAG vs Agentic RAG
    · Workflows
    · Agent Configuration
    · LLM Provider Abstraction
    · Tool Factory Pattern
    · Observability and Monitoring
    · Prompt System

## · Core Components  (L986)
  源文件: vectara_agentic/agent.py, vectara_agentic/tools.py
  Architecture Overview
  Agent as Central Orchestrator
  Tool Factory Pattern
    · VectaraToolFactory
    · ToolsFactory  
  Configuration Management
  LLM Provider Integration
  Data Flow and Tool Execution
  Error Handling and Fallbacks
  Serialization and Persistence

## · Agent System  (L1322)
  源文件: tests/test_agent.py, vectara_agentic/agent.py, vectara_agentic/agent_config.py, vectara_agentic/types.py
  Purpose and Architecture
    · Core Agent Architecture
  Agent Class Overview
    · Agent Initialization
    · Key Initialization Parameters
  Agent Types and Implementation
    · Agent Type Implementation Matrix
    · Agent Creation Logic
  Configuration System
    · Configuration Structure
    · Fallback Configuration System
  Chat Interface and Lifecycle
    · Chat Method Flow
    · Streaming Chat Interface
  Memory Management
    · Memory Initialization and Operations
  Tool Integration and Validation
    · Tool Processing Pipeline
    · Gemini Tool Sanitization
  Factory Methods
    · Factory Method Comparison
    · from_corpus Implementation
  Workflow Integration
    · Workflow Execution Flow
  Error Handling and Observability
    · Token Counting and Callbacks

## · Tool Factory System  (L1860)
  源文件: tests/test_tools.py, vectara_agentic/llm_utils.py, vectara_agentic/tool_utils.py, vectara_agentic/tools.py
  Purpose and Scope
  Factory Pattern Architecture
  VectaraToolFactory
    · Initialization and Configuration
    · RAG Tool Creation
    · Search Tool Creation
  ToolsFactory
    · Standard Tool Categories
    · LlamaIndex Integration
  VectaraTool Implementation
    · Tool Metadata Enhancement
    · Enhanced Error Handling
  Dynamic Tool Creation Process
    · Filter String Construction
  Tool Type Classification

## · Workflow Engine  (L2221)
  源文件: tests/test_workflow.py, vectara_agentic/sub_query_workflow.py
  Architecture Overview
  Sub-Question Query Workflow
    · Workflow Components
    · Processing Flow
    · Sub-Question Generation
  Sequential Sub-Questions Workflow
    · Sequential Processing Model
    · Context Passing Mechanism
  Integration with Agent System
    · Agent-Workflow Integration
    · Required Workflow Attributes
  Error Handling and Timeouts
    · Timeout Management
    · Failure Recovery
    · JSON Parsing Resilience

## · Prompt System  (L2491)
  源文件: vectara_agentic/_prompts.py, vectara_agentic/agent.py
  Core Prompt Templates
    · General Instructions Framework
    · Agent-Specific Templates
  Prompt Processing and Injection
    · Template Variable Substitution
    · LLM Compiler Specialized Processing
  Agent Type Integration
    · Prompt Assignment by Agent Type
    · ReAct Agent Format Specification
  Structured Planning Prompts
    · Initial Planning Template
    · Plan Refinement Template
  Prompt Customization Mechanisms
    · Multi-Level Instruction Hierarchy
    · Validation and Tool Integration

## · Installation and Configuration  (L2764)
  源文件: docs/endpoint.md, docs/installation.md, requirements.txt, setup.py, vectara_agentic/__init__.py
  Package Installation
  Dependencies Overview
    · Core Framework Dependencies
    · Tool Ecosystem Dependencies
    · Observability and Monitoring Dependencies
  Environment Configuration
    · Required Environment Variables
    · Configuration Loading
  Configuration Architecture
  Verification Steps
    · 1. Package Import Verification
    · 2. Dependency Verification
    · 3. Environment Configuration Check
    · 4. Basic Agent Creation

## · Dependencies and Setup  (L3031)
  源文件: Makefile, requirements.txt, setup.py, vectara_agentic/__init__.py
  Core Dependency Architecture
    · Dependency Layer Structure
  LlamaIndex Ecosystem Integration
    · Core LlamaIndex Components
    · Agent Type Dependencies
  LLM Provider Dependencies
    · Provider Package Mapping
    · LLM Provider Architecture
  Tool Ecosystem Dependencies
    · Built-in Tool Dependencies
    · External API Libraries
  Observability and Monitoring Stack
    · Observability Component Architecture
    · Observability Dependencies
  Installation Process
    · Package Installation
    · Development Installation
    · Package Configuration
  Development Setup
    · Development Tools
    · Core Dependencies

## · Agent Configuration  (L3419)
  源文件: docs/usage.md, vectara_agentic/agent_config.py
  Configuration Architecture
    · AgentConfig Class Structure
    · Configuration Data Flow
  Configuration Fields
    · Agent Type Configuration
    · LLM Provider Configuration
    · Private LLM Configuration
    · Observability and Runtime Configuration
  Environment Variable Configuration
    · Setting Environment Variables
    · Private LLM Configuration
  Creating AgentConfig Objects
    · Using Environment Variable Defaults
    · Explicit Configuration
    · Mixed Configuration Example
  Serialization and Persistence
    · Dictionary Conversion
    · Dictionary Structure
  Integration with Agent System
    · Agent Constructor Usage
    · Fallback Agent Configuration
  Type Safety and Validation
    · Frozen Dataclass
    · Automatic Type Conversion

## · LLM Provider Setup  (L3754)
  源文件: tests/test_api_endpoint.py, tests/test_fallback.py, tests/test_gemini.py, tests/test_groq.py, tests/test_private_llm.py, vectara_agentic/agent_endpoint.py, vectara_agentic/llm_utils.py, vectara_agentic/tool_utils.py
  Overview
  Provider Architecture
  Supported Providers
  Configuration Through AgentConfig
  Provider-Specific Setup
    · OpenAI Configuration
    · Anthropic Configuration
    · Google Gemini Configuration
    · Groq Configuration
    · Private/Custom LLM Configuration
  LLM Role Configuration
  Fallback Configuration
  Environment Variables
  Agent Type Compatibility
  Tokenization Support

## · Usage Guide  (L4020)
  源文件: README.md, docs/usage.md
  Core Usage Patterns
  Tool Creation Workflow
    · Vectara RAG Tool Creation
    · Custom Tool Creation
  Agent Configuration and Lifecycle
    · Agent Instructions
    · Configuration Options
  Interaction Methods
    · Chat Interface
    · Workflow Execution
  Common Usage Patterns
    · Financial Analysis Agent
    · Multi-Corpus RAG System
    · Observability Integration

## · Basic Usage  (L4306)
  源文件: docker/simple-agent.py, docs/usage.md, tests/endpoint.py, tests/test_agent.py, vectara_agentic/types.py
  Core System Overview
  Quick Start Example
  Agent Creation Patterns
    · From Corpus (Simplest)
    · Manual Construction
  Essential Agent Parameters
  Basic Chat Interactions
    · Synchronous Chat
    · Multi-turn Conversations
  Configuration Basics
    · Agent Types
    · LLM Provider Configuration
    · Basic Configuration Example

## · Available Tools  (L4591)
  源文件: .pylintrc, docs/tools.md, vectara_agentic/_callback.py, vectara_agentic/_observability.py, vectara_agentic/db_tools.py, vectara_agentic/tools_catalog.py
  Tool Architecture Overview
  Standard Text Processing Tools
    · Text Manipulation Tools
    · Utility Tools
  Guardrail Tools
    · Content Safety
  Database Tools
    · Database Tool Catalog
    · Database Tool Functions
  Vectara-Specific Tools  
    · RAG and Search Tools
  External Integration Tools
    · Research and Information Tools
    · Financial Analysis Tools
    · Legal Domain Tools
  Tool Management and Lifecycle
    · Tool Creation Patterns
    · Observability Integration

## · Advanced Features  (L4957)
  源文件: .pylintrc, vectara_agentic/_callback.py, vectara_agentic/_observability.py, vectara_agentic/db_tools.py, vectara_agentic/tools_catalog.py, vectara_agentic/utils.py
  Observability and Monitoring
    · Phoenix Integration Architecture
    · Observer Setup Process
    · Factual Consistency Score Evaluation
  Callback System
    · Callback Handler Architecture
    · Callback Event Types
  Utility Functions
    · Document Summarization Utilities
    · Function Introspection Utilities
    · Type Checking Utilities
  Advanced Tool Features
    · Text Processing Tools
    · Database Tools Advanced Features
    · Guardrails Integration

## · API and Endpoints  (L5314)
  源文件: docker/simple-agent.py, docs/endpoint.md, docs/installation.md, tests/endpoint.py, tests/test_api_endpoint.py, tests/test_gemini.py, tests/test_groq.py, vectara_agentic/agent_endpoint.py
  Endpoint Architecture
    · API System Overview
    · Request Flow Architecture
  Native Vectara-Agentic Endpoints
    · GET /chat
  OpenAI-Compatible Endpoints
    · POST /v1/completions
    · POST /v1/chat
  Authentication and Security
    · API Key Authentication
  Deployment and Configuration
    · Application Factory
    · Server Startup
    · Simple Deployment Example
  Request/Response Models
    · Core Model Definitions
    · Token Counting

## · REST API  (L5682)
  源文件: docs/endpoint.md, docs/installation.md, tests/test_api_endpoint.py, tests/test_gemini.py, tests/test_groq.py, vectara_agentic/agent_endpoint.py
  Overview
  API Endpoint Architecture
  Request/Response Flow
  Core Endpoint Types
    · Chat Endpoint (`/chat`)
    · Completion Endpoint (`/v1/completions`)
    · Chat Completion Endpoint (`/v1/chat`)
  Authentication System
    · API Key Verification
  Token Usage Calculation
  Application Lifecycle
    · Application Creation
    · Application Startup
  Error Handling
    · HTTP Status Codes
    · Error Response Format
  Integration Testing
    · Test Coverage Areas

## · OpenAI-Compatible Endpoints  (L5962)
  源文件: docker/simple-agent.py, tests/endpoint.py, tests/test_api_endpoint.py, tests/test_gemini.py, tests/test_groq.py, vectara_agentic/agent_endpoint.py
  Overview
  Request Flow Architecture
  Available Endpoints
    · Chat Completions Endpoint
    · Text Completions Endpoint  
    · Legacy Chat Endpoint
  Request and Response Schemas
    · Chat Completion Schemas
    · Text Completion Schemas
  Authentication
  Usage Examples
    · Using OpenAI Python Client
    · Direct HTTP Requests
  Deployment
    · Basic Deployment
    · Custom FastAPI Integration
  Implementation Details
    · Token Counting
    · Response ID Generation
    · Message Processing

## · Development and Testing  (L6323)
  源文件: Makefile, tests/test_agent.py, tests/test_tools.py, vectara_agentic/types.py
  Testing Framework Overview
    · Test Architecture
    · Test Categories
  Development Environment
    · Development Workflow
    · Quality Assurance Tools
  Testing Strategies
    · Mock Testing for External Services
    · Tool Validation Testing
    · Agent Configuration Testing
    · Integration Testing
    · Test Execution

## · Testing Framework  (L6549)
  源文件: tests/test_agent.py, tests/test_return_direct.py, tests/test_tools.py, tests/test_vectara_llms.py, vectara_agentic/types.py
  Test Suite Structure
  Tool System Testing
    · VectaraToolFactory Testing
    · Generic Tool Testing
  Agent System Testing
    · Agent Configuration Testing
    · Multi-turn Conversation Testing
  LLM Integration Testing
    · Provider-Specific Testing
  Specialized Feature Testing
    · Return Direct Functionality
  Test Execution Patterns
    · Mock Integration Testing
    · Test Credentials Management
  Running Tests

## · Development Environment  (L6819)
  源文件: .flake8, .github/assets/Vectara-logo.png, Makefile, publish.sh
  Development Tools Overview
  Code Quality and Linting
    · Linting Configuration
    · Running Linting Tools
  Type Checking with MyPy
  Testing Framework
  Build and Publishing Process
  Development Workflow
    · Complete Development Command

## · Release Process  (L7058)
  源文件: .github/assets/Vectara-logo.png, .github/workflows/publish_release.yml, publish.sh, vectara_agentic/_version.py
  Release Workflow Overview
    · GitHub Actions Release Workflow
  Version Management
    · Version Definition and Extraction
  Build and Publish Process
    · Package Build Steps
    · Dependencies and Tools
  Documentation Deployment
    · Documentation Workflow
  Manual Release Alternative
    · Manual Release Script
  Release Triggers and Permissions
    · Workflow Configuration
    · Required Secrets

## · Deployment  (L7271)
  源文件: docker/simple-agent.py, docs/endpoint.md, docs/installation.md, tests/endpoint.py
  Deployment Overview
    · Deployment Architecture
  API Endpoint Deployment
    · Basic Endpoint Setup
    · Endpoint Configuration
  Production Configuration
    · Environment Variables
    · Security Considerations
    · Scaling Considerations
  API Compatibility
    · Native REST API
    · OpenAI-Compatible API
  Monitoring and Observability

## · Docker Deployment  (L7508)
  源文件: docker/simple-agent.py, tests/endpoint.py
  Container Architecture
    · Deployment Architecture
    · Code Entity Flow
  Basic Deployment Process
    · Agent Creation Pattern
  Configuration Management
    · Environment Variables
    · Corpus Configuration
    · Network Configuration
  Production Deployment Considerations
    · Container Structure
    · Security Considerations
    · Health Checks and Monitoring
  Testing Deployed Containers

## · Documentation Site  (L7714)
  源文件: docs/api.md, docs/endpoint.md, docs/installation.md, mkdocs.yml
  Purpose and Scope
  Documentation Architecture
    · Documentation Build Pipeline
    · File Structure and Organization
  MkDocs Configuration
    · Site Configuration
    · Navigation Structure
    · Plugin Configuration
  API Documentation Generation
    · Automatic Documentation Extraction
  Documentation Content Structure
    · Core Documentation Pages
    · Installation Documentation
    · Endpoint Documentation
  Deployment Process
    · Versioning Strategy
    · Build and Deployment Pipeline