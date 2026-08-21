# Skeleton: lagent（21 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 12KB | 7 | ~5 | 4 |
| 2 | Installation and Setup | L465 | 8KB | 3 | ~6 | 6 |
| 3 | Core Components | L764 | 14KB | 8 | ~3 | 9 |
| 4 | Agent System | L1210 | 13KB | 10 | ~0 | 7 |
| 5 | Agent Base Classes | L1629 | 12KB | 6 | ~15 | 6 |
| 6 | ReAct Agents | L2063 | 8KB | 2 | ~5 | 5 |
| 7 | Specialized Agents | L2307 | 11KB | 6 | ~2 | 6 |
| 8 | LLM Integration | L2697 | 10KB | 7 | ~0 | 3 |
| 9 | API-based LLMs | L3006 | 10KB | 3 | ~2 | 4 |
| 10 | Local Model Integration | L3369 | 11KB | 5 | ~8 | 5 |
| 11 | Action System | L3722 | 10KB | 6 | ~7 | 4 |
| 12 | Web Browsing and Search | L4066 | 11KB | 4 | ~2 | 4 |
| 13 | Code Execution | L4414 | 11KB | 8 | ~2 | 4 |
| 14 | Research and Content Creation | L4734 | 10KB | 5 | ~1 | 3 |
| 15 | Support Systems | L5040 | 9KB | 5 | ~0 | 5 |
| 16 | Memory Management | L5326 | 9KB | 6 | ~2 | 3 |
| 17 | Hooks and Middleware | L5624 | 9KB | 4 | ~0 | 5 |
| 18 | Usage Examples | L5915 | 19KB | 7 | ~0 | 2 |
| 19 | Simple Agent Examples | L6539 | 10KB | 7 | ~0 | 1 |
| 20 | Multi-Agent Systems | L6930 | 10KB | 7 | ~4 | 4 |
| 21 | Tool Usage Examples | L7212 | 12KB | 5 | ~0 | 4 |


## · Overview  (L6)
  源文件: README.md, docs/en/changelog.md, lagent/version.py, requirements/runtime.txt
  Architecture Overview
  Communication Model
  Agent System
    · Key Agent Types
  LLM Integration System
  Action System
    · Built-in Actions
  Support Systems
    · Memory Management
    · Hooks System
    · Output Parsers
    · Aggregators
  Usage Patterns
    · Single Agent Example
    · Multi-Agent Systems
  Dual Interfaces
  Dependencies and Requirements
  License

## · Installation and Setup  (L465)
  源文件: docs/en/changelog.md, lagent/llms/lmdeploy_wrapper.py, lagent/llms/vllm_wrapper.py, lagent/version.py, requirements/optional.txt, requirements/runtime.txt
  Core Installation
  Dependencies
    · Core Dependencies
    · Optional Dependencies
  Installation with Specific Features
    · For all optional dependencies:
    · For specific features:
  Component Dependencies Diagram
  LLM Integration Options
    · Model Integration Paths
  Configuration for LLM Backends
    · API-based LLM Configuration
    · Local LLM Configuration
  LMDeploy Setup
  Verification of Installation
  Next Steps

## · Core Components  (L764)
  源文件: .pre-commit-config.yaml, README.md, lagent/actions/base_action.py, lagent/actions/google_search.py, lagent/agents/__init__.py, lagent/agents/agent.py, lagent/llms/__init__.py, lagent/memory/base_memory.py, tests/test_actions/test_google_search.py
  Core Architecture Overview
  Agent System
    · Base Agent Class
    · Agent Variants
  LLM System
    · LLM Abstraction
    · LLM Implementation Classes
  Action System
    · BaseAction and ActionExecutor
    · Built-in Actions
  Support Systems
    · Memory Management
    · Message Aggregation
    · Hooks
    · Output Parsing
  Key Communication Patterns
  Customization Options
  Synchronous vs. Asynchronous APIs

## · Agent System  (L1210)
  源文件: README.md, lagent/agents/__init__.py, lagent/agents/agent.py, lagent/agents/aggregator/tool_aggregator.py, lagent/memory/base_memory.py, lagent/prompts/parsers/__init__.py, lagent/schema.py
  Overview
  Core Agent Classes
    · Base Agent
  Agent Communication and Messages
  Memory and State Management
  Message Aggregation and Formatting
  Specialized Agent Types
    · Streaming Agents
    · Asynchronous Agents
    · Sequential Agents
  Agent Containers and Composition
  Example Usage Patterns
    · Simple Agent
    · Tool-using Agent
    · Multi-agent System
  Conclusion

## · Agent Base Classes  (L1629)
  源文件: lagent/agents/__init__.py, lagent/agents/agent.py, lagent/agents/aggregator/tool_aggregator.py, lagent/memory/base_memory.py, lagent/prompts/parsers/__init__.py, lagent/schema.py
  Overview of Agent Base Classes
  Agent Class Hierarchy
  Base Agent Class
    · Key Properties and Methods
    · Basic Usage Example
    · Agent Interaction Flow
  Asynchronous Agent
    · Key Methods
    · Usage Example
  Streaming Agent
    · Key Methods
    · Usage Example
  Sequential Agent
    · Key Methods
    · Usage Example
  Agent Container Classes
    · AgentList
    · AgentDict
    · Usage Example
  Memory Management
    · Key Memory Functions
  Hook System
    · Registering Hooks
  Summary of Agent Variants

## · ReAct Agents  (L2063)
  源文件: lagent/agents/__init__.py, lagent/agents/agent.py, lagent/agents/react.py, lagent/memory/base_memory.py, lagent/prompts/parsers/str_parser.py
  Core Concept and Architecture
  Implementation Details
    · Key Components
  Core API and Configuration
    · Initialization Parameters
  Implementation Workflow
  Output Format and Processing
  Memory Management
  Integration with Action System
  Example Usage
  Asynchronous Implementation
  Customization

## · Specialized Agents  (L2307)
  源文件: lagent/agents/__init__.py, lagent/agents/agent.py, lagent/agents/stream.py, lagent/memory/base_memory.py, lagent/prompts/parsers/tool_parser.py, setup.cfg
  Agent Specialization Hierarchy
  Streaming Agents
    · StreamingAgent and AsyncStreamingAgent
    · Implementation Details
  Sequential Agents
    · Sequential and Streaming Variants
    · Implementation Details
  InternLM Agents
    · Key Features of InternLM Agents
    · Tool Processing Flow
  MathCoder Agents
    · Key Features of MathCoder
    · AsyncMathCoder Implementation
  Usage Examples
    · Streaming Agent
    · InternLM Agent with Python Interpreter
    · MathCoder for Solving Math Problems

## · LLM Integration  (L2697)
  源文件: .pre-commit-config.yaml, README.md, lagent/llms/__init__.py
  1. LLM Abstraction Architecture
  2. Types of LLM Implementations
    · 2.1 API-based LLMs
    · 2.2 Model-based LLMs
    · 2.3 Deployment-based LLMs
  3. LLM Integration in the Agent Framework
  4. Configuring LLMs
    · 4.1 API-based LLM Configuration
    · 4.2 Local Model Configuration 
    · 4.3 Deployment Configuration
  5. Dual Interface Design
  6. Extension and Customization
  Summary

## · API-based LLMs  (L3006)
  源文件: lagent/llms/base_api.py, lagent/llms/openai.py, lagent/llms/sensenova.py, lagent/utils/gen_key.py
  Overview
  Common Base Classes
    · BaseAPILLM
    · AsyncBaseAPILLM
  Message Template Handling
  OpenAI GPT Models
    · Key Features
    · Basic Usage Example
    · Async Usage Example
  SenseNova Models
    · Key Features
    · Basic Usage Example
  API Key Management
    · Implementation Details
  Advanced Features
    · Streaming Responses
    · JSON Mode
  Generation Parameters
  SenseNova Authentication
  Error Handling
  Implementation Note

## · Local Model Integration  (L3369)
  源文件: lagent/llms/base_llm.py, lagent/llms/huggingface.py, lagent/llms/lmdeploy_wrapper.py, lagent/llms/vllm_wrapper.py, requirements/optional.txt
  Overview of Local Model Integration Architecture
  Common LLM Interface
  Hugging Face Models Integration
    · Key Features of Hugging Face Integration
    · Usage Example
  vLLM Integration
    · Key Features of vLLM Integration
    · Async Implementation
  LMDeploy Integration
    · LMDeploy Integration Options
    · Model Loading Options
  Implementation Comparison
  Installation Requirements
  Integration with Agent System

## · Action System  (L3722)
  源文件: lagent/actions/__init__.py, lagent/actions/base_action.py, lagent/actions/google_search.py, tests/test_actions/test_google_search.py
  Core Architecture
  BaseAction
    · Key Components
    · Action Method Documentation
  Action Executor
  Action Types
    · Web Interaction Actions
    · Code Execution Actions
    · Research Tools
    · Document Creation
    · Utility Actions
  Action Implementation Structure
  Action Return Format
  Creating Custom Actions
    · 1. Simple Action with run() Method
    · 2. Toolkit with Multiple APIs
    · 3. Asynchronous Action
  Integration with Agent System
  Conclusion

## · Web Browsing and Search  (L4066)
  源文件: lagent/actions/parser.py, lagent/actions/web_browser.py, lagent/llms/anthropic_llm.py, tests/test_actions/test_searxng_search.py
  Purpose and Scope
  Architecture Overview
  Search Engine Interface
    · Available Search Engines
    · Search Result Filtering
  Web Browser Actions
    · 1. Search
    · 2. Select
    · 3. Open URL
  Content Fetching
  Advanced Features
    · Caching and Efficiency
    · Error Handling and Retries
    · Asynchronous Operations
  Integration with Parsers
  Usage Flow
  Example Configuration

## · Code Execution  (L4414)
  源文件: lagent/actions/ipython_interactive.py, lagent/actions/ipython_interpreter.py, lagent/actions/ipython_manager.py, lagent/actions/python_interpreter.py
  Overview
  Interpreter Types
  Execution Flow
  Python Interpreter
  IPython Interactive
  IPython Interpreter
  Async Execution Support
  Code Extraction
  Result Handling
  Integration with Agents
  Timeout and Safety

## · Research and Content Creation  (L4734)
  源文件: lagent/actions/arxiv_search.py, lagent/actions/google_scholar_search.py, lagent/actions/ppt.py
  Purpose and Scope
  Overview of Research and Content Creation Tools
  Research Actions
    · ArXiv Search
    · Google Scholar Search
  Content Creation Actions
    · PowerPoint Presentation Creator
  Integration with Agent System
    · Example Configuration
  Limitations and Considerations

## · Support Systems  (L5040)
  源文件: lagent/hooks/__init__.py, lagent/hooks/hook.py, lagent/hooks/logger.py, lagent/utils/__init__.py, lagent/utils/util.py
  Overview of Support Systems
  Hook System
    · Hook Architecture
    · Hook Implementation
    · MessageLogger Example
  Memory Management
  Output Parsers
  Aggregator System
  Utility Functions
    · Key Utilities:
  Integration with Agent System
  Summary

## · Memory Management  (L5326)
  源文件: lagent/agents/__init__.py, lagent/agents/agent.py, lagent/memory/base_memory.py
  Purpose and Scope
  Memory Architecture
  Memory Class
    · Key Features
    · Core Methods
  Memory Manager
  Agent Memory Integration
    · Memory Update Flow
  Session Management
    · Session Handling in Agents
  State Management
    · State Serialization
  Memory in Agent Containers
    · Memory Hierarchy
  Usage Examples
    · Basic Memory Access
    · Saving and Loading State
  Advanced Memory Management
    · Custom Memory Filtering
    · Memory Window Limits

## · Hooks and Middleware  (L5624)
  源文件: lagent/hooks/__init__.py, lagent/hooks/hook.py, lagent/hooks/logger.py, lagent/utils/__init__.py, lagent/utils/util.py
  Hook System Architecture
    · Hook Registration and Lifecycle
  Built-in Hooks
    · MessageLogger
    · Action Preprocessors
  Hook System Implementation
  Hook Integration in the Agent Architecture
  Example: MessageLogger Implementation
  Using Hooks in Custom Agents
  Integration with the Broader System
  Conclusion

## · Usage Examples  (L5915)
  源文件: README.md, examples/model_cli_demo.py
  Basic Agent Usage
    · Creating a Simple Agent
    · Working with Agent Memory
    · Using Different LLM Implementations
  Custom Message Processing
    · Creating a Custom Message Aggregator
    · Structured Response Parsing
  Tool Integration
    · Using Action Executors
  Single Agent Examples
    · Math Problem Solver
  Multi-Agent Systems
    · Asynchronous Content Refinement
    · Multi-Tool Workflow
  Advanced Usage Patterns
    · Synchronous vs Asynchronous Interfaces
    · Session Management
  Summary

## · Simple Agent Examples  (L6539)
  源文件: examples/model_cli_demo.py
  Introduction
  Initializing Language Models
  Agent Types
    · Basic Agent
    · ReAct Agent
    · Streaming Agent
  Managing Conversation History
  Common Usage Patterns
    · Interactive Chat Loop
    · ReAct Agent with Tools
    · Batch Processing with Agent
  Model CLI Demo Implementation
  Conclusion

## · Multi-Agent Systems  (L6930)
  源文件: README.md, lagent/agents/__init__.py, lagent/agents/agent.py, lagent/memory/base_memory.py
  Purpose and Scope
  Introduction to Multi-Agent Systems
  Core Components for Multi-Agent Systems
    · Agent Composition Classes
    · Agent Communication
  Agent Organization Patterns
    · Sequential Agent Chains
    · Nested Agent Hierarchies
  Memory Management in Multi-Agent Systems
  Practical Examples of Multi-Agent Systems
    · Blogging Agent with Self-Refinement
    · Data Visualization Multi-Agent System
  Implementation Guidelines for Multi-Agent Systems
    · Session Management
    · Agent Synchronization Options
  Best Practices for Multi-Agent System Design
  Conclusion

## · Tool Usage Examples  (L7212)
  源文件: examples/model_cli_demo.py, lagent/actions/base_action.py, lagent/actions/google_search.py, tests/test_actions/test_google_search.py
  Understanding the Tool System in LAgent
  Tool Execution Flow
  Implementing and Using Basic Tools
    · Single-Function Tools
    · Multi-Function Toolkits
  Using Built-in Tools
    · Google Search
    · Asynchronous Tools
  Creating Custom Tools
    · Example Custom Tool
  Integrating Tools with Agents
    · Tool Selection and Execution
  Error Handling in Tools
  Advanced Tool Usage Patterns
    · Combining Multiple Tools
    · Sequential Tool Usage
  Best Practices for Tool Usage
  Conclusion