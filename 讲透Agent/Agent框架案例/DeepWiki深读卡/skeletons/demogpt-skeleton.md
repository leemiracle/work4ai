# Skeleton: demogpt（24 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 11KB | 5 | ~0 | 12 |
| 2 | Features and Capabilities | L304 | 9KB | 4 | ~2 | 6 |
| 3 | System Requirements | L576 | 11KB | 5 | ~9 | 14 |
| 4 | Architecture | L927 | 14KB | 4 | ~2 | 18 |
| 5 | Pipeline Overview | L1279 | 16KB | 11 | ~3 | 14 |
| 6 | Task System | L1700 | 13KB | 7 | ~3 | 19 |
| 7 | Code Generation and Assembly | L2047 | 12KB | 7 | ~5 | 15 |
| 8 | Core Components | L2383 | 15KB | 8 | ~0 | 7 |
| 9 | Model | L2823 | 14KB | 6 | ~1 | 8 |
| 10 | Chains | L3268 | 13KB | 3 | ~8 | 10 |
| 11 | Controllers | L3709 | 12KB | 6 | ~3 | 6 |
| 12 | Task Templates | L4008 | 15KB | 5 | ~8 | 11 |
| 13 | Self-Refinement | L4375 | 8KB | 3 | ~2 | 10 |
| 14 | AgentHub | L4589 | 13KB | 8 | ~5 | 12 |
| 15 | Agents | L4968 | 10KB | 3 | ~2 | 10 |
| 16 | RAG System | L5293 | 9KB | 6 | ~9 | 2 |
| 17 | LLM Interface | L5566 | 6KB | 4 | ~0 | 4 |
| 18 | Usage and Examples | L5779 | 12KB | 7 | ~4 | 13 |
| 19 | Command Line Usage | L6149 | 8KB | 5 | ~2 | 12 |
| 20 | Python API Usage | L6436 | 11KB | 4 | ~3 | 12 |
| 21 | Application Examples | L6802 | 12KB | 8 | ~2 | 15 |
| 22 | Contributing | L7114 | 13KB | 4 | ~0 | 8 |
| 23 | Adding New Tasks | L7474 | 11KB | 4 | ~6 | 15 |
| 24 | Development Roadmap | L7766 | 9KB | 7 | ~3 | 6 |


## · Overview  (L6)
  源文件: README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/chains/task_chains.py, demogpt/model.py, demogpt/utils.py, docs/README_CN.md, pyproject.toml
  Core Purpose and Capabilities
  System Architecture
  Processing Pipeline
    · 1. Planning
    · 2. Task Creation
    · 3. Code Generation
    · 4. Code Assembly
  Core Components
    · DemoGPT Model
    · Chains System
    · Task Chains
    · Controllers
  Integration with External Systems
    · LangChain Integration
    · OpenAI API Integration
    · Streamlit Integration
  System Requirements
  Conclusion

## · Features and Capabilities  (L304)
  源文件: README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, docs/README_CN.md
  Core Features
    · Automatic Streamlit Application Generation
    · Plan-Based Pipeline Architecture
    · LangChain Integration
    · Model Flexibility
  Application Capabilities
    · Web Search Integration
    · Conversational Interfaces
    · Calculator and Math Functions
    · Agent-Based Systems
  User Interfaces
    · Python API
    · Command Line Interface
    · Web Interface
  Integration with External APIs
  Self-Refinement Capability
  Upcoming Features

## · System Requirements  (L576)
  源文件: .gitignore, LICENSE, README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/chains/task_chains.py, demogpt/model.py, demogpt/utils.py
  Purpose and Scope
  System Requirements Overview
  Hardware Requirements
  Software Requirements
    · Operating System
    · Python Environment
    · Package Dependencies
  API Requirements
    · OpenAI API Key
    · Model Support
  Installation Methods
    · Package Installation
    · Source Code Installation
  Environment Configuration
    · Environment Variables
    · Configuration Flow
  Runtime Requirements
    · Process Resources
    · API Usage
  Usage Modes
    · Python API Usage Requirements
  Compatibility Notes
    · Streamlit Compatibility
    · OpenAI API Compatibility
    · Package Version Constraints
  Troubleshooting Common Requirements Issues

## · Architecture  (L927)
  源文件: README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/__init__.py, demogpt/chains/prompts/app_type.py, demogpt/chains/prompts/plan_with_inputs.py, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/chains/prompts/task_list/ui_output_text.py, demogpt/chains/task_chains.py
  High-Level Architecture Overview
  Plan-Based Pipeline
    · 1. Plan Generation
    · 2. Task Creation
    · 3. Code Generation
    · 4. Code Assembly
  Component Architecture
    · DemoGPT Class
    · Chains Class
    · TaskChains Class
    · Controllers Module
    · Utils Module
  Task System
    · Task Definition
    · Task Processing
  Application Types and Task Compatibility
  External Dependencies
  Conclusion

## · Pipeline Overview  (L1279)
  源文件: CONTRIBUTING.md, README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/chains/task_chains.py, demogpt/model.py, demogpt/test.py, demogpt/utils.py
  Purpose and Scope
  Pipeline Architecture
    · High-Level Pipeline Flow
  Detailed Pipeline Stages
    · 1. System Inputs Detection
    · 2. Plan Generation
    · 3. Task Creation
    · 4. Code Generation
    · 5. Code Assembly
  Pipeline Implementation Details
    · Component Architecture
    · Execution Flow
  Task Processing
  Special Case: Chat Applications
  Self-Refinement Mechanism
  Code Structure Generated by the Pipeline
  Conclusion

## · Task System  (L1700)
  源文件: demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/__init__.py, demogpt/chains/prompts/app_type.py, demogpt/chains/prompts/how_to_use.py, demogpt/chains/prompts/plan_with_inputs.py, demogpt/chains/prompts/task_list/chat.py, demogpt/chains/prompts/task_list/detailed_description.py, demogpt/chains/prompts/task_list/doc_load.py, demogpt/chains/prompts/task_list/summarize.py, demogpt/chains/prompts/task_list/ui_input_file.py, demogpt/chains/prompts/task_list/ui_output_text.py
  Task System in the Application Pipeline
  Task Structure and Format
    · Task Attributes
  Task Types and Categories
    · Data Type System
  Task Creation Process
    · From Plan to Tasks
    · Pattern Extraction Example
  Task Validation System
    · Validation Checks
    · Task Refinement Loop
  Task to Code Generation
    · Code Generation Process
  Task System Integration with App Types
  Conclusion

## · Code Generation and Assembly  (L2047)
  源文件: demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/combine_v2.py, demogpt/chains/prompts/how_to_use.py, demogpt/chains/prompts/task_list/chat.py, demogpt/chains/prompts/task_list/detailed_description.py, demogpt/chains/prompts/task_list/doc_load.py, demogpt/chains/prompts/task_list/python_coder.py, demogpt/chains/prompts/task_list/summarize.py, demogpt/chains/prompts/task_list/ui_input_file.py, demogpt/chains/task_chains.py, demogpt/chains/task_chains_seperate.py
  Overview
  Code Generation Process
    · Task-to-Code Translation
    · Task-Specific Code Generation
    · Self-Refinement Process
  Code Assembly Strategies
    · 1. Simple Concatenation
    · 2. Component-Based Assembly
  Code Separation and Organization
  Code Formatting and Finalization
  Generated Code Examples
    · UI Input Elements
    · AI Prompt Templates
  Relationship Between Task Types and Generated Code
  Extending the System

## · Core Components  (L2383)
  源文件: demogpt/__init__.py, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/task_chains.py, demogpt/model.py, demogpt/utils.py, pyproject.toml
  Core Components Overview
  Model
    · Pipeline Implementation
  Chains
    · Chains Class
    · TaskChains Class
  Controllers
  Task Templates
  Self-Refinement
  Component Interactions

## · Model  (L2823)
  源文件: CONTRIBUTING.md, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/task_chains.py, demogpt/model.py, demogpt/test.py, demogpt/utils.py, pyproject.toml
  Core Architecture
  System Component Integration
  Model Initialization and Configuration
  Processing Pipeline
    · 1. System Inputs Detection
    · 2. Plan Generation
    · 3. Plan Validation and Refinement
    · 4. Task Generation
    · 5. Task Validation and Refinement
    · 6. Code Generation
    · 7. Code Assembly
  Special Application Types
  Progress Tracking and Feedback
  Error Handling and Fallbacks
  Integration with Utils and Chains
  Python API Usage
  Technical Details
    · Available Model Detection
    · LLM Configuration Management
  Summary

## · Chains  (L3268)
  源文件: demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/plan.py, demogpt/chains/prompts/plan1.py, demogpt/chains/self_refiner.py, demogpt/chains/task_chains.py, demogpt/model.py, demogpt/test_cases.py, demogpt/utils.py, pyproject.toml
  Chain Architecture
    · Core Chain Classes
  Chain Types
    · Planning Chains
    · Task Chains
    · Code Generation Chains
    · Utility Chains
  Chain Execution Flow
    · Key Execution Steps:
  Implementation Details
    · Chains Class Methods
    · TaskChains Class Methods
    · Chain Data Flow
  Chain Utilities
    · Task-Specific Code Generation
    · Code Assembly
  Chain Prompts
  Conclusion

## · Controllers  (L3709)
  源文件: demogpt/chains/prompts/__init__.py, demogpt/chains/prompts/app_type.py, demogpt/chains/prompts/plan_with_inputs.py, demogpt/chains/prompts/task_list/ui_output_text.py, demogpt/chains/task_definitions.py, demogpt/controllers.py
  Overview of the Controllers System
  Task Validation Process
    · Plan to Task Format Conversion
    · Validation Checks
    · Prompt Template Validation
  Integration with Task Definitions
  Controller Flow in DemoGPT System
  Key Validation Rules
  Validation Feedback Examples
  Conclusion

## · Task Templates  (L4008)
  源文件: demogpt/chains/prompts/how_to_use.py, demogpt/chains/prompts/self_refinement/__init__.py, demogpt/chains/prompts/self_refinement/final_refiner.py, demogpt/chains/prompts/task_list/chat.py, demogpt/chains/prompts/task_list/detailed_description.py, demogpt/chains/prompts/task_list/doc_load.py, demogpt/chains/prompts/task_list/summarize.py, demogpt/chains/prompts/task_list/ui_input_chat.py, demogpt/chains/prompts/task_list/ui_input_file.py, demogpt/chains/prompts/task_list/ui_input_text.py, demogpt/chains/task_chains_seperate.py
  What are Task Templates?
  Template Structure and Interface
  Available Task Templates
    · UI Input/Output Templates
    · Document Processing Templates
    · LLM Interaction Templates
    · Search Templates
    · General Code Generation Template
  How Task Templates Are Used in the Pipeline
  Self-Refinement in Task Templates
  Template Prompt System
  Extending with New Task Templates

## · Self-Refinement  (L4375)
  源文件: README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/chains/prompts/plan.py, demogpt/chains/prompts/plan1.py, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/chains/self_refiner.py, demogpt/test_cases.py, docs/README_CN.md
  Architecture Overview
  SelfRefiner Class
    · Key Components
  The Refinement Process
  Implementation Details
    · Conversation History Management
    · Feedback Generation
    · Code Refinement
    · Completion Check
  Usage in DemoGPT
  Development Status
  Conclusion

## · AgentHub  (L4589)
  源文件: demogpt_agenthub/__init__.py, demogpt_agenthub/agents/__init__.py, demogpt_agenthub/agents/base.py, demogpt_agenthub/agents/react.py, demogpt_agenthub/agents/tool_calling.py, demogpt_agenthub/prompts/__init__.py, demogpt_agenthub/prompts/agents/react/success_decider.py, demogpt_agenthub/prompts/agents/tool_calling/final_answer.py, demogpt_agenthub/prompts/agents/tool_calling/tool_decider.py, demogpt_agenthub/rag/__init__.py, demogpt_agenthub/tools/repl.py, demogpt_agenthub/utils/parsers.py
  Overview
  Agent System Architecture
    · Agent Interaction Flow
  BaseAgent
    · Key Methods and Properties
    · Prompt Templates
  Agent Implementations
    · ToolCallingAgent
    · ReactAgent
    · Agent Comparison
  Tools
    · PythonTool
    · Other Tools
  Output Parsers
    · BooleanOutputParser
  RAG System
  LLM Interface
  Integration with DemoGPT

## · Agents  (L4968)
  源文件: demogpt_agenthub/agents/__init__.py, demogpt_agenthub/agents/base.py, demogpt_agenthub/agents/react.py, demogpt_agenthub/agents/tool_calling.py, demogpt_agenthub/prompts/agents/react/success_decider.py, demogpt_agenthub/prompts/agents/tool_calling/final_answer.py, demogpt_agenthub/prompts/agents/tool_calling/tool_decider.py, demogpt_agenthub/rag/__init__.py, demogpt_agenthub/tools/repl.py, demogpt_agenthub/utils/parsers.py
  Agent Architecture
    · BaseAgent
    · ToolCallingAgent
    · ReactAgent
  Agent Operation Flow
  Prompt Templates
    · Tool Decider Prompt
    · Success Decider Prompt
    · Final Answer Prompt
  Tool Integration
  Usage Example
  Custom Output Parsers
  Integration with DemoGPT

## · RAG System  (L5293)
  源文件: demogpt_agenthub/rag/base.py, tests/test_rag.py
  Overview
  Components
    · BaseRAG Class
    · Supported Vector Stores
    · Embedding Models
    · Document Loaders
  Workflow
    · Document Ingestion Workflow
    · Query Processing Workflow
  Usage Examples
  Integration with DemoGPT
  Initialization Parameters
  Main Methods
  Error Handling

## · LLM Interface  (L5566)
  源文件: demogpt_agenthub/llms/base.py, demogpt_agenthub/llms/openai.py, tests/__init__.py, tests/test_llms.py
  Overview
  Architecture
  Components
    · BaseLLM
    · OpenAIModel
    · OpenAIChatModel
  Usage
    · Example Usage
  Integration with Other Components
  Extending the LLM Interface

## · Usage and Examples  (L5779)
  源文件: README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/chains/task_chains.py, demogpt/model.py, demogpt/prompt.py, demogpt/utils.py, docs/README_CN.md
  Command Line Usage
    · Installation
    · Running DemoGPT
  Python API Usage
    · Basic Usage
    · Processing Phases
    · Example Output
  Application Examples
    · Example Instructions to DemoGPT
    · Generation Process Flow
    · Example 1: Translation Application
    · Example 2: Document Processing Application
    · Example 3: Chat-Based Application
    · Example 4: Web Search Application
  Customizing Generated Applications
    · Editing in the Web Interface
    · Modifying Output Files
  Example User Workflow
  Troubleshooting
  Best Practices

## · Command Line Usage  (L6149)
  源文件: README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/chains/task_chains.py, demogpt/model.py, demogpt/utils.py, docs/README_CN.md, pyproject.toml
  Installation
  Basic Usage
  Command Flow
  Environment Configuration
  Architecture and Integration
  Behind the Scenes: Command Processing
  System Requirements
  Command Arguments and Options
  Application Execution
  Advanced Usage Tips
  Troubleshooting
  Examples
  Related Documentation

## · Python API Usage  (L6436)
  源文件: README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/chains/task_chains.py, demogpt/model.py, demogpt/utils.py, docs/README_CN.md, pyproject.toml
  Installation
  Basic Usage
  API Components
    · DemoGPT Class
  Generation Pipeline
  Phase Information
  Detailed Component Architecture
  Advanced Configuration
    · Using Different Models
    · Running the Generated Streamlit App
  Example Applications
    · Chat-Based Applications
    · Document Processing Applications
    · Search-Based Applications
  Generation Process Deep Dive
  Error Handling
  Conclusion

## · Application Examples  (L6802)
  源文件: README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/app.py, demogpt/chains/chains.py, demogpt/chains/prompts/plan_feedback.py, demogpt/chains/prompts/plan_refiner.py, demogpt/chains/prompts/system_inputs.py, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/chains/task_chains.py, demogpt/model.py
  Application Generation Overview
  Types of Applications
  Text Processing Applications
    · Translation Application Example
  Chat-Based Applications
    · Character Clone Example
  Document Processing Applications
    · Document Summarizer Example
  Search-Based Applications
    · Web Research Assistant Example
  Content Generation Applications
    · Blog Post Generator Example
  Best Practices for Application Examples
  Application Example Table
  Advanced Application Examples
    · Multi-Step Research and Summarization Tool
  Application Extension Patterns
  Limitations and Considerations

## · Contributing  (L7114)
  源文件: CONTRIBUTING.md, README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, demogpt/test.py, docs/README_CN.md
  System Overview
  Project Structure
  Adding New Tasks
    · 1. Fill the Task Template File
    · 2. Update Task Definitions
    · 3. Add Task Implementation in TaskChains
    · 4. Update `__init__.py`
    · 5. Update `getCodeSnippet` Function
    · 6. Add Test Cases
    · 7. Add Test Function
    · 8. Test Your Implementation
  Modifying Main Prompts
  Testing Your Changes
  Development Roadmap
  Submission Guidelines
  Conclusion

## · Adding New Tasks  (L7474)
  源文件: CONTRIBUTING.md, demogpt/chains/prompts/__init__.py, demogpt/chains/prompts/app_type.py, demogpt/chains/prompts/how_to_use.py, demogpt/chains/prompts/plan_with_inputs.py, demogpt/chains/prompts/task_list/chat.py, demogpt/chains/prompts/task_list/detailed_description.py, demogpt/chains/prompts/task_list/doc_load.py, demogpt/chains/prompts/task_list/summarize.py, demogpt/chains/prompts/task_list/ui_input_file.py, demogpt/chains/prompts/task_list/ui_output_text.py, demogpt/chains/task_chains_seperate.py
  Task System Overview
  Task Structure
    · Task Attributes Explained
  Step-by-Step Guide to Adding a New Task
    · 1. Define Task Requirements
    · 2. Add Task Definition
    · 3. Create Task Implementation File
    · 4. Update Task Imports
    · 5. Add Task Implementation to TaskChains Class
    · 6. Update Task Processing
    · 7. Add Test Cases
    · 8. Add Test Function
  Task Validation System
    · Key Validation Rules
  Task Type Constraints
    · Application Type Requirements
  Testing Your New Task
  Task Chaining and Data Flow
  Common Issues and Solutions
  Best Practices

## · Development Roadmap  (L7766)
  源文件: README.md, assets/demogpt_new_pipeline.jpeg, assets/demogpt_new_pipeline1.jpeg, demogpt/chains/prompts/task_list/search.py, demogpt/chains/prompts/task_list/search_chat.py, docs/README_CN.md
  Purpose and Scope
  Current Status
  Short-Term Roadmap (0-3 months)
    · Gorilla Integration for API Usage
    · Self-Refining Strategy
    · Remaining LangChain Tasks
  Medium-Term Roadmap (3-9 months)
    · Database for Example Storage
    · Llama2 Integration
    · Enhanced Search and Retrieval Capabilities
  Long-Term Vision (9+ months)
    · Technical Infrastructure Evolution
  Technical Implementation Details
    · Database Integration Architecture
    · Self-Refinement Mechanism
    · API Integration Architecture
  Contribution Areas
  Conclusion