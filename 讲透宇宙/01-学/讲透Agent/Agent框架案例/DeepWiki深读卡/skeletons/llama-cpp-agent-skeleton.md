# Skeleton: llama-cpp-agent（25 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 9KB | 3 | ~4 | 2 |
| 2 | Getting Started | L277 | 11KB | 3 | ~2 | 8 |
| 3 | Core Framework | L677 | 14KB | 8 | ~4 | 5 |
| 4 | LlamaCppAgent | L1107 | 19KB | 18 | ~10 | 5 |
| 5 | FunctionCallingAgent | L1840 | 8KB | 4 | ~2 | 10 |
| 6 | StructuredOutputAgent | L2056 | 9KB | 5 | ~4 | 5 |
| 7 | Output Processing | L2387 | 14KB | 8 | ~4 | 5 |
| 8 | Provider System | L2752 | 8KB | 5 | ~6 | 3 |
| 9 | Provider Architecture | L3032 | 10KB | 5 | ~5 | 3 |
| 10 | Provider Implementations | L3329 | 10KB | 6 | ~7 | 12 |
| 11 | Memory System | L3664 | 10KB | 4 | ~3 | 5 |
| 12 | Memory Architecture | L3991 | 12KB | 5 | ~4 | 11 |
| 13 | Memory Tools Integration | L4341 | 11KB | 7 | ~6 | 11 |
| 14 | Tools and Function Calling | L4642 | 10KB | 4 | ~4 | 5 |
| 15 | Function Tools Framework | L4961 | 11KB | 4 | ~1 | 9 |
| 16 | Web Search Tools | L5349 | 12KB | 3 | ~8 | 11 |
| 17 | Prompt Templates | L5727 | 9KB | 5 | ~2 | 5 |
| 18 | Examples and Applications | L6019 | 9KB | 4 | ~1 | 6 |
| 19 | Basic Examples | L6299 | 12KB | 6 | ~4 | 8 |
| 20 | Virtual Game Master | L6581 | 12KB | 8 | ~6 | 6 |
| 21 | Memory Assistant | L6987 | 9KB | 4 | ~3 | 6 |
| 22 | Advanced Applications | L7270 | 11KB | 6 | ~6 | 7 |
| 23 | Development and Deployment | L7655 | 8KB | 4 | ~5 | 2 |
| 24 | Project Configuration | L7928 | 8KB | 5 | ~7 | 5 |
| 25 | CI/CD Pipeline | L8201 | 6KB | 3 | ~2 | 1 |


## · Overview  (L6)
  源文件: ReadMe.md, pyproject.toml
  Framework Purpose and Scope
  High-Level System Architecture
    · Core System Architecture
  Core Framework Flow
    · Agent Processing Pipeline
  Key Components
    · Agent Classes
    · Provider System
    · Memory Architecture
  Optional Dependencies and Features
  Application Examples
    · Example Applications
  Framework Benefits

## · Getting Started  (L277)
  源文件: docs/chat_history-api-reference.md, docs/get-started.md, examples/01_Basics/chatbot_using_llama_cpp_server.py, examples/02_Structured_Output/book_dataset_creation.py, examples/02_Structured_Output/dataframe_creation.py, examples/03_Tools_And_Function_Calling/duck_duck_go_websearch_agent.py, examples/03_Tools_And_Function_Calling/experimental_code_interpreter.py, tests/providers.py
  Installation
  Framework Overview
    · Core Components Architecture
  Provider Setup
    · Provider Configuration Examples
    · llama-cpp-python Provider
    · llama.cpp Server Provider
    · TGI Server Provider
    · vLLM Server Provider
  Basic Agent Creation
    · Simple Agent Setup
    · Customized Agent Configuration
  Core Usage Workflows
    · Basic Chat Interaction Flow
    · Simple Chat Example
    · Function Calling Workflow
    · Function Calling Example
    · Structured Output Generation
  Specialized Agent Classes
    · FunctionCallingAgent
    · StructuredOutputAgent
  Next Steps
    · Advanced Features
    · Configuration Options
    · Provider-Specific Features

## · Core Framework  (L677)
  源文件: src/llama_cpp_agent/function_calling.py, src/llama_cpp_agent/function_calling_agent.py, src/llama_cpp_agent/gbnf_grammar_generator/gbnf_grammar_from_pydantic_models.py, src/llama_cpp_agent/llm_agent.py, src/llama_cpp_agent/messages_formatter.py
  Core Architecture Overview
    · Framework Components Diagram
  LlamaCppAgent - Central Orchestrator
    · Core Agent Architecture
    · Key Methods and Responsibilities
  Specialized Agent Types
    · FunctionCallingAgent
    · StructuredOutputAgent
  Message Processing Pipeline
    · Message Formatter Architecture
    · System Prompt Modules
  Output Processing System
    · GBNF Grammar Generation Pipeline
    · Function Tool Integration
  Integration and Data Flow
    · Complete Framework Data Flow
    · Framework Configuration Options

## · LlamaCppAgent  (L1107)
  源文件: src/llama_cpp_agent/function_calling.py, src/llama_cpp_agent/function_calling_agent.py, src/llama_cpp_agent/gbnf_grammar_generator/gbnf_grammar_from_pydantic_models.py, src/llama_cpp_agent/llm_agent.py, src/llama_cpp_agent/messages_formatter.py
  Purpose and Scope
  Core Architecture
  Key Components and Configuration
    · Agent Initialization
    · System Prompt Modules
  Response Generation Flow
    · Chat Response Flow
    · Text Response Flow
  Provider Integration
    · Provider Communication Pattern
  Message Formatting and Chat History
    · Messages Formatting System
    · Chat History Management
  Structured Output Processing
    · Function Calling Integration
    · Object Instance Generation
  Advanced Features
    · Streaming Response Handling
    · Response Role Detection
    · Debug Output
  Purpose and Scope
  Core Architecture
  Key Components and Configuration
    · Agent Initialization
    · System Prompt Modules
  Response Generation Flow
    · Chat Response Flow
    · Text Response Flow
  Provider Integration
    · Provider Communication Pattern
  Message Formatting and Chat History
    · Messages Formatting System
    · Chat History Management
  Structured Output Processing
    · Function Calling Integration
    · Object Instance Generation
  Advanced Features
    · Streaming Response Handling
    · Response Role Detection
    · Debug Output

## · FunctionCallingAgent  (L1840)
  源文件: examples/01_Basics/self_critique.py, examples/07_Memory/agent_core_memory.py, examples/07_Memory/core_memory.json, src/llama_cpp_agent/function_calling.py, src/llama_cpp_agent/function_calling_agent.py, src/llama_cpp_agent/gbnf_grammar_generator/gbnf_grammar_from_pydantic_models.py, src/llama_cpp_agent/llm_agent.py, src/llama_cpp_agent/messages_formatter.py, src/llama_cpp_agent/prompt_templates.py, src/llama_cpp_agent/tools/web_search/tool.py
  Purpose and Scope
  Architecture Overview
  Function Calling Process
  Built-in Function Tools
  Configuration and Initialization
  Structured Output Integration
  Advanced Features

## · StructuredOutputAgent  (L2056)
  源文件: src/llama_cpp_agent/json_schema_generator/schema_generator.py, src/llama_cpp_agent/llm_documentation/__init__.py, src/llama_cpp_agent/llm_documentation/documentation_generation.py, src/llama_cpp_agent/llm_output_settings/settings.py, src/llama_cpp_agent/structured_output_agent.py
  Purpose and Architecture
    · Core Architecture
    · Data Flow Architecture
  Core Components
    · StructuredOutputAgent Class
    · Prompt Templates
  Configuration and Settings
    · LlmStructuredOutputSettings Integration
    · Documentation Generation
  Usage Patterns
    · Basic Object Creation
    · Grammar Caching
  Integration Points
    · Provider System Integration
    · Memory System Compatibility
    · Framework Position

## · Output Processing  (L2387)
  源文件: src/llama_cpp_agent/json_schema_generator/schema_generator.py, src/llama_cpp_agent/llm_documentation/__init__.py, src/llama_cpp_agent/llm_documentation/documentation_generation.py, src/llama_cpp_agent/llm_output_settings/settings.py, src/llama_cpp_agent/output_parser.py
  System Overview
  LlmStructuredOutputSettings Architecture
  Output Types and Configuration
  GBNF Grammar Generation
  JSON Schema Generation
  Documentation Generation
  Output Parsing and Response Handling
  Function Call Processing
  Provider Integration

## · Provider System  (L2752)
  源文件: src/llama_cpp_agent/chain.py, src/llama_cpp_agent/hermes_2_pro_agent.py, src/llama_cpp_agent/providers/provider_base.py
  Provider Architecture Overview
  Core Provider Interface
    · Provider Identification and Configuration
    · Text Generation Interface
    · Tokenization Support
  Sampling Settings System
    · Core Sampling Settings Interface
    · Settings Persistence
  Provider Integration with Agent System
    · Agent Chain Integration
    · Structured Output Support
  Provider Lifecycle and Usage Patterns
    · Initialization and Configuration
    · Error Handling and Fallbacks
  Provider Enumeration System

## · Provider Architecture  (L3032)
  源文件: src/llama_cpp_agent/chain.py, src/llama_cpp_agent/hermes_2_pro_agent.py, src/llama_cpp_agent/providers/provider_base.py
  Purpose and Scope
  Provider Interface Design
    · Core Provider Interface
    · Provider Identification System
  Sampling Settings Architecture
    · Settings Interface Design
    · Settings Serialization
  Provider Orchestration Through Agent Chains
    · Agent Chain Integration
    · Chain Element Configuration
  Structured Output Integration
    · Provider-Aware Output Processing
  Specialized Agent Integration
    · Hermes2ProAgent Provider Usage
    · Custom Message Formatting
  Provider Method Contracts
    · Core Provider Methods

## · Provider Implementations  (L3329)
  源文件: examples/01_Basics/chatbot_using_groq.py, examples/04_Chains/article_summary.py, examples/07_Memory/MemoryAssistant/core_memory.json, examples/07_Memory/MemoryAssistant/main.py, examples/07_Memory/MemoryAssistant/memory.py, examples/07_Memory/MemoryAssistant/prompts.py, src/llama_cpp_agent/providers/groq.py, src/llama_cpp_agent/providers/llama_cpp_python.py, src/llama_cpp_agent/providers/llama_cpp_server.py, src/llama_cpp_agent/providers/tgi_server.py, src/llama_cpp_agent/providers/vllm_server.py, src/llama_cpp_agent/text_utils.py
  Provider Implementation Overview
  Local and Self-Hosted Providers
    · LlamaCppServerProvider
    · LlamaCppPythonProvider
  High-Performance Server Providers
    · VLLMServerProvider
    · TGIServerProvider
  Commercial and Cloud Providers
    · GroqProvider
  Provider Feature Comparison
  Usage Examples
    · Basic Provider Setup
    · Settings Configuration

## · Memory System  (L3664)
  源文件: src/llama_cpp_agent/agent_memory/core_memory_manager.py, src/llama_cpp_agent/agent_memory/memory_tools.py, src/llama_cpp_agent/agent_memory/retrieval_memory.py, src/llama_cpp_agent/agent_memory/retrieval_memory_manager.py, src/llama_cpp_agent/llm_prompt_template.py
  Memory Architecture Overview
    · Memory Architecture Diagram
  Core Memory System
    · Core Memory Implementation
    · Core Memory Structure
  Retrieval Memory System
    · Retrieval Memory Components
    · Memory Scoring Algorithm
  Event Memory System
    · Event Memory Architecture
    · Event Management
  Persistence and Storage
    · Memory Initialization Patterns

## · Memory Architecture  (L3991)
  源文件: examples/07_Memory/VirtualGameMaster/core_memory.json, examples/07_Memory/VirtualGameMaster/main.py, examples/07_Memory/VirtualGameMaster/memory.py, examples/07_Memory/VirtualGameMaster/prompts.py, src/llama_cpp_agent/agent_memory/core_memory_manager.py, src/llama_cpp_agent/agent_memory/event_memory.py, src/llama_cpp_agent/agent_memory/event_memory_manager.py, src/llama_cpp_agent/agent_memory/memory_tools.py, src/llama_cpp_agent/agent_memory/retrieval_memory.py, src/llama_cpp_agent/agent_memory/retrieval_memory_manager.py, src/llama_cpp_agent/llm_prompt_template.py
  Memory System Overview
  Core Memory Architecture
    · Core Memory Structure
    · Core Memory Operations
  Event Memory Architecture
    · Event Memory Flow
    · Event Memory Operations
  Retrieval Memory Architecture
    · Retrieval Memory Components
    · Memory Scoring Algorithm
  Memory Integration with Agents
    · Agent Memory Wrapper Classes
    · Memory Tool Integration Example

## · Memory Tools Integration  (L4341)
  源文件: examples/01_Basics/chatbot_using_groq.py, examples/07_Memory/MemoryAssistant/core_memory.json, examples/07_Memory/MemoryAssistant/main.py, examples/07_Memory/MemoryAssistant/memory.py, examples/07_Memory/MemoryAssistant/prompts.py, src/llama_cpp_agent/agent_memory/core_memory_manager.py, src/llama_cpp_agent/agent_memory/memory_tools.py, src/llama_cpp_agent/agent_memory/retrieval_memory.py, src/llama_cpp_agent/agent_memory/retrieval_memory_manager.py, src/llama_cpp_agent/llm_prompt_template.py, src/llama_cpp_agent/providers/groq.py
  Memory Tool Architecture
  Core Memory Tool Integration
    · Core Memory Function Tools
    · System Prompt Integration
  Retrieval Memory Tool Integration
    · Retrieval Memory Function Tools
  Event Memory Tool Integration
    · Event Memory Function Tools
  Agent Integration Patterns
    · Tool Registration Process
    · Runtime Memory Management
  System Prompt Integration
    · Memory Context Formatting

## · Tools and Function Calling  (L4642)
  源文件: examples/01_Basics/self_critique.py, examples/07_Memory/agent_core_memory.py, examples/07_Memory/core_memory.json, src/llama_cpp_agent/prompt_templates.py, src/llama_cpp_agent/tools/web_search/tool.py
  Function Calling Architecture
    · Function Calling Flow
    · Prompt Template System
  Tool Creation and Integration
    · LlamaCppFunctionTool Wrapper System
    · Pydantic Model Integration
  Web Search Tool Implementation
    · WebSearchTool Architecture
    · Search and Summarization Flow
  Agent Integration Patterns
    · Memory-Enabled Function Calling
    · Tool Registration and Configuration
  Advanced Function Calling Features
    · Thoughts and Reasoning Integration
    · Multi-Function Execution
    · Heartbeat Mechanism

## · Function Tools Framework  (L4961)
  源文件: docs/get-started.md, examples/01_Basics/self_critique.py, examples/02_Structured_Output/book_dataset_creation.py, examples/02_Structured_Output/dataframe_creation.py, examples/07_Memory/agent_core_memory.py, examples/07_Memory/core_memory.json, src/llama_cpp_agent/prompt_templates.py, src/llama_cpp_agent/tools/web_search/tool.py, tests/providers.py
  Core Components
    · LlamaCppFunctionTool Architecture
    · Function Tool Creation Methods
  Python Function Tools
    · Function Requirements
  Pydantic Model Tools
    · Model Structure
    · Pydantic Tool Integration Flow
  OpenAI Tool Specifications
    · OpenAI Tool Format
  Integration with Agent Framework
    · Integration Architecture
  Function Calling Prompt System
    · Prompt Template Components
    · Function Call Response Format
  Usage Patterns
    · Basic Function Tool Setup
    · Memory Integration Example
    · FunctionCallingAgent Integration

## · Web Search Tools  (L5349)
  源文件: examples/01_Basics/self_critique.py, examples/03_Tools_And_Function_Calling/web_search_agent.py, examples/07_Memory/agent_core_memory.py, examples/07_Memory/core_memory.json, src/llama_cpp_agent/prompt_templates.py, src/llama_cpp_agent/tools/__init__.py, src/llama_cpp_agent/tools/web_search/__init__.py, src/llama_cpp_agent/tools/web_search/default_web_crawlers.py, src/llama_cpp_agent/tools/web_search/default_web_search_providers.py, src/llama_cpp_agent/tools/web_search/tool.py, src/llama_cpp_agent/tools/web_search/web_search_interfaces.py
  System Architecture
    · Core Architecture Overview
  Core Components
    · WebSearchTool Class
    · Web Search Flow
    · WebCrawler Interface and Implementations
    · WebSearchProvider Interface and Implementations
  Integration with Agents
    · Function Tool Integration
    · Agent Integration Pattern
  Configuration and Token Management
    · Token Limit Handling
    · Provider-Specific Settings
  Prompt Templates for Search Operations
    · Core Search Templates
    · Template Usage Pattern
    · Structured Output Format
  Usage Examples and Best Practices
    · Basic Usage
    · Custom Configuration

## · Prompt Templates  (L5727)
  源文件: examples/01_Basics/self_critique.py, examples/07_Memory/agent_core_memory.py, examples/07_Memory/core_memory.json, src/llama_cpp_agent/prompt_templates.py, src/llama_cpp_agent/tools/web_search/tool.py
  Template System Architecture
  Core Template Categories
  Function Calling Templates
  Structured Output Templates
  Specialized Task Templates
    · Content Summarization Templates
    · Search and Research Templates
  Template Usage Patterns
    · Basic Usage Pattern
    · Integration with WebSearchTool
  Integration with Agent System

## · Examples and Applications  (L6019)
  源文件: examples/07_Memory/VirtualGameMaster/core_memory.json, examples/07_Memory/VirtualGameMaster/main.py, examples/07_Memory/VirtualGameMaster/memory.py, examples/07_Memory/VirtualGameMaster/prompts.py, src/llama_cpp_agent/agent_memory/event_memory.py, src/llama_cpp_agent/agent_memory/event_memory_manager.py
  Application Architecture Overview
  Virtual Game Master Application
    · Core Application Structure
    · Memory System Implementation
    · Dynamic Prompt System
    · Event-Driven Conversation Flow
    · Function Tool Integration
    · Structured Output Processing
    · Provider Configuration
    · Application Usage Patterns

## · Basic Examples  (L6299)
  源文件: docs/chat_history-api-reference.md, docs/get-started.md, examples/01_Basics/chatbot_using_llama_cpp_server.py, examples/02_Structured_Output/book_dataset_creation.py, examples/02_Structured_Output/dataframe_creation.py, examples/03_Tools_And_Function_Calling/duck_duck_go_websearch_agent.py, examples/03_Tools_And_Function_Calling/experimental_code_interpreter.py, tests/providers.py
  Basic Agent Setup and Provider Configuration
    · Provider Architecture Overview
    · Simple Chatbot Example
  Provider Setup Patterns
    · Provider Configuration Matrix
  Structured Output Generation
    · Structured Output Flow
  Basic Function Calling
    · Function Tool Integration
  FunctionCallingAgent for Automated Tool Use
    · FunctionCallingAgent Architecture
  Chat History Configuration
    · Chat History Strategy Options
  Message Formatting
    · Available Message Formatters

## · Virtual Game Master  (L6581)
  源文件: examples/07_Memory/VirtualGameMaster/core_memory.json, examples/07_Memory/VirtualGameMaster/main.py, examples/07_Memory/VirtualGameMaster/memory.py, examples/07_Memory/VirtualGameMaster/prompts.py, src/llama_cpp_agent/agent_memory/event_memory.py, src/llama_cpp_agent/agent_memory/event_memory_manager.py
  Overview
  Architecture Overview
  Memory Integration
    · Three-Layer Memory Architecture
    · Memory Update Mechanism
  Conversation Flow Architecture
    · Main Conversation Loop
    · Event Memory Management
  System Prompt Engineering
    · Dynamic Prompt Modules
  Structured Output Configuration
    · Function Tool Integration
  Message Processing Pipeline
    · XML Tag Wrapping System
  Game Master Prompt Design
    · Core System Instructions
    · Example-Driven Responses
  Implementation Details
    · Provider Configuration
    · Persistent Game State

## · Memory Assistant  (L6987)
  源文件: examples/01_Basics/chatbot_using_groq.py, examples/07_Memory/MemoryAssistant/core_memory.json, examples/07_Memory/MemoryAssistant/main.py, examples/07_Memory/MemoryAssistant/memory.py, examples/07_Memory/MemoryAssistant/prompts.py, src/llama_cpp_agent/providers/groq.py
  Purpose and Architecture
    · Core Components
  Memory System Integration
    · Memory Configuration
    · Core Memory Structure
  Conversation Flow and System Prompts
    · System Prompt Modules
    · Conversation Loop
  Function Tools and Structured Output
    · Memory Function Tools
    · XML Response Formatting
  Provider Configuration and Settings
  Usage and Deployment

## · Advanced Applications  (L7270)
  源文件: docs/chat_history-api-reference.md, examples/01_Basics/chatbot_using_llama_cpp_server.py, examples/03_Tools_And_Function_Calling/duck_duck_go_websearch_agent.py, examples/03_Tools_And_Function_Calling/experimental_code_interpreter.py, src/llama_cpp_agent/mixtral_8x22b_agent.py, src/llama_cpp_agent/rag/__init__.py, src/llama_cpp_agent/rag/rag_colbert_reranker.py
  Code Interpreter Systems
    · Code Execution Architecture
    · Autonomous Task Execution
  RAG Systems with Advanced Reranking
    · RAG Architecture with ColBERT
  Specialized Model Integration
    · Mixtral Agent Architecture
  Web Search and Content Extraction
    · Web Search Agent Pipeline
  Integration Patterns for Advanced Applications
    · Multi-Component Integration Pattern
    · Common Implementation Patterns

## · Development and Deployment  (L7655)
  源文件: ReadMe.md, pyproject.toml
  Development Environment Overview
    · Core Architecture
  Dependency Architecture
    · Dependency Mapping
    · Installation Patterns
  Build and Package Management
    · Build Configuration
    · Package Metadata
  Deployment Architecture
    · Provider Deployment Matrix
  Environment-Specific Considerations
    · Development Environment
    · Production Environment
    · Memory System Deployment
    · Provider-Specific Infrastructure
  Version and Release Management
    · Version Compatibility
    · Release Channels

## · Project Configuration  (L7928)
  源文件: ReadMe.md, docs/function-calling-agent.md, docs/index.md, mkdocs.yml, pyproject.toml
  Purpose and Scope
  Project Structure Overview
  Core Project Configuration
    · Build System Configuration
    · Project Metadata
  Dependency Management
    · Core Dependencies
    · Optional Dependency Groups
  Documentation Configuration
    · Documentation Build System
    · Documentation Structure
  Installation and Usage
  Python Version Requirements

## · CI/CD Pipeline  (L8201)
  源文件: .github/workflows/python-ci.yml
  Pipeline Overview
  CI/CD Workflow Architecture
  Workflow Triggers
  Build Process
    · Build Job Configuration
  Publication Process
    · Publication Job Flow
  Configuration and Secrets
    · Required Secrets
    · Workflow Configuration Details
    · Pipeline Security
  Monitoring and Troubleshooting