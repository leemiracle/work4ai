# Skeleton: maestro-framework（18 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 8KB | 3 | ~3 | 1 |
| 2 | Core Concepts | L255 | 8KB | 9 | ~3 | 1 |
| 3 | Architecture | L524 | 14KB | 10 | ~1 | 3 |
| 4 | Installation & Setup | L949 | 8KB | 3 | ~3 | 1 |
| 5 | API Keys Configuration | L1289 | 8KB | 2 | ~5 | 1 |
| 6 | Usage Guide | L1576 | 9KB | 4 | ~3 | 1 |
| 7 | Basic Workflow | L1907 | 9KB | 6 | ~3 | 2 |
| 8 | Code Generation | L2180 | 10KB | 4 | ~2 | 3 |
| 9 | Search Integration | L2430 | 8KB | 4 | ~2 | 2 |
| 10 | Implementations | L2662 | 10KB | 8 | ~3 | 1 |
| 11 | OpenAI (GPT) Implementation | L2976 | 10KB | 4 | ~1 | 2 |
| 12 | Local LLM with Ollama | L3295 | 8KB | 3 | ~2 | 2 |
| 13 | Other Implementations | L3551 | 8KB | 3 | ~3 | 1 |
| 14 | Web Interface | L3813 | 7KB | 4 | ~1 | 3 |
| 15 | Web Interface Setup | L4040 | 6KB | 4 | ~2 | 2 |
| 16 | Using the Web Interface | L4232 | 6KB | 3 | ~4 | 3 |
| 17 | Customizing Maestro | L4402 | 13KB | 5 | ~2 | 3 |
| 18 | Troubleshooting & FAQ | L4883 | 18KB | 10 | ~4 | 3 |


## · Overview  (L6)
  源文件: README.md
  Core Architecture
  Implementation Variants
  Execution Workflow
  Core Components
    · Main Execution Function
    · Orchestrator Model
    · Sub-agent Model
    · Refiner Model
  Data Flow
  Key Features
    · Task Decomposition
    · LLM Provider Flexibility
    · Search Integration
    · Code Generation
    · Exchange Logging
    · Web Interface
  Technical Requirements

## · Core Concepts  (L255)
  源文件: README.md
  The Maestro Orchestration Model
  Key Components
    · 1. Orchestrator Model
    · 2. Sub-agent Model
    · 3. Refiner Model
  Task Orchestration Process
  Enhanced Capabilities
    · Search Integration
    · Code Generation
  Implementation Models
  Code to Concept Mapping
  Memory and Context Flow

## · Architecture  (L524)
  源文件: README.md, maestro-gpt4o.py, maestro-ollama.py
  1. System Overview
  2. Core Components
  3. Implementation Variants
  4. Process Flow
    · 4.1 Orchestrator Function Flow
    · 4.2 Sub-agent Function Flow
    · 4.3 Refiner Function Flow
  5. Data Structures
    · 5.1 Task Exchanges
    · 5.2 Previous Tasks Context
    · 5.3 Code Generation Data
  6. Storage and Persistence
    · 6.1 Exchange Log
    · 6.2 Task Data Persistence
    · 6.3 Project Files
  7. Optional Integrations
    · 7.1 Search Integration
    · 7.2 File Content Processing
  8. Error Handling
  9. Control Flow

## · Installation & Setup  (L949)
  源文件: README.md
  Prerequisites
  Installation Steps
    · 1. Clone the Repository
    · 2. Install Dependencies
    · 3. Configure API Keys
  Implementation-Specific Setup
    · Original Maestro (Anthropic Claude)
    · Maestro with Any API (LiteLLM)
    · OpenAI GPT-4 Implementation
    · OpenAI GPT-4o Implementation
    · Local Setup with LM Studio
    · Local Setup with Ollama
    · Groq Implementation
  Search Integration (Optional)
  Dependency Relationships
  Verifying Installation
  Implementation Comparison

## · API Keys Configuration  (L1289)
  源文件: README.md
  Overview of Required API Keys
  Implementation-to-API Key Mapping
  Obtaining API Keys
    · Anthropic API Key
    · OpenAI API Key
    · Gemini API Key
    · Groq API Key
    · Tavily API Key (Optional, for search functionality)
  Configuring API Keys
    · Method 1: Environment Variables (Recommended)
    · Method 2: Direct Code Modification
  Implementation-Specific Configuration
    · maestro.py (Anthropic Claude)
    · maestro-anyapi.py (Multi-provider)
    · maestro-gpt.py and maestro-gpt4o.py (OpenAI)
    · maestro-groq.py (Groq)
  Local LLM Configuration
    · maestro-lmstudio.py
    · maestro-ollama.py
  Troubleshooting API Key Issues
    · Common Problems and Solutions
    · Best Practices for API Key Security

## · Usage Guide  (L1576)
  源文件: README.md
  Getting Started with Maestro
    · Basic Command Line Usage
  Selecting a Maestro Implementation
  Configuring Models
  Common Usage Patterns
    · Basic Workflow
    · Code Generation
    · Search Integration
  Using Different Implementations
    · Using with Cloud Providers
    · Using with Local LLMs
  Output and Results
  Customization Options
  Web Interface
  Next Steps

## · Basic Workflow  (L1907)
  源文件: README.md, maestro-gpt4o.py
  Workflow Overview
  Step 1: Defining Your Objective
    · Example Objective Input
  Step 2: Task Orchestration
  Step 3: Sub-task Execution
  Step 4: Result Refinement
  Step 5: Output Generation
    · Exchange Log Structure
    · Project Structure Creation
  Common Options and Parameters
    · Model Roles
  Understanding Task Completion

## · Code Generation  (L2180)
  源文件: README.md, maestro-gpt4o.py, maestro-ollama.py
  Overview of Code Generation
  Code Generation Process
  Expected Refiner Output Format
  Folder Structure Generation
    · JSON Format
    · Extraction and Processing
  Code Files Generation
    · Code Block Format
    · Extraction and File Creation
  Implementation-Specific Details
  Projects and File Management
  Error Handling
  Triggering Code Generation

## · Search Integration  (L2430)
  源文件: README.md, maestro-gpt4o.py
  Overview
  Setting Up Search Integration
    · API Key Configuration
  Search Integration Workflow
  Implementation Details
    · Search Query Generation
    · Search Execution
  Using Search Integration
  Technical Implementation Reference
  Search Integration Architecture
  Limitations and Considerations
  Conclusion

## · Implementations  (L2662)
  源文件: README.md
  Implementation Overview
  Implementation Components
  Implementation Comparison
  Core Implementation: Anthropic Claude
  Multi-Provider Implementation
  Local LLM Implementations
  Groq Implementation
  OpenAI Implementations
  Common Features Across Implementations
  Implementation Selection Guide

## · OpenAI (GPT) Implementation  (L2976)
  源文件: README.md, maestro-gpt4o.py
  Overview
  Architecture
    · Architecture Diagram
    · Components and Model Configuration
  Workflow Process
  Core Functions
    · Orchestrator Function
    · Sub-Agent Function
    · Refiner Function
  Code Generation Capabilities
    · Project Structure Extraction and Creation
  Optional Features
    · File Input Context
    · Search Integration
  Token Usage and Cost Tracking
  Usage Example
  Integration with Other Maestro Components
  Conclusion

## · Local LLM with Ollama  (L3295)
  源文件: README.md, maestro-ollama.py
  Overview of Maestro with Ollama
  Installation and Setup
    · 1. Install Ollama
    · 2. Install Required Python Package
    · 3. Pull Required Models
  Architecture and Implementation
    · Model Configuration
    · Key Components
  Using Maestro with Ollama
    · Running the Script
    · Processing Flow
  Task Persistence and Resumption
  Advantages and Limitations
    · Advantages
    · Limitations
  Example Use Cases
  Troubleshooting

## · Other Implementations  (L3551)
  源文件: README.md
  Implementation Overview
  Common Architecture
  Multi-Provider Implementation (maestro-anyapi.py)
    · Overview
    · Setup and Usage
  Groq Implementation (maestro-groq.py)
    · Overview
    · Setup and Usage
  LM Studio Implementation (maestro-lmstudio.py)
    · Overview
    · Setup and Usage
  Original Claude/Anthropic Implementation (maestro.py)
    · Overview
    · Setup and Usage
  Implementation Comparison
  Implementation Selection Process
  Technical Considerations

## · Web Interface  (L3813)
  源文件: flask_app/app.py, flask_app/templates/base.html, flask_app/templates/index.html
  Architecture Overview
  Components
    · Flask Application
    · HTML Templates
  User Interaction Flow
  Integration with Maestro Framework
  Technical Details
    · Flask Application
    · Routes
  Form Submission and Processing
  User Interface Elements
  Summary

## · Web Interface Setup  (L4040)
  源文件: flask_app/app.py, flask_app/requirements.txt
  Overview
  Prerequisites
  Installation
    · Step 1: Clone the Repository
    · Step 2: Install Required Dependencies
  Web Application Structure
  Configuration
  Running the Web Interface
  Implementation Details
    · Main Application File
  Security Considerations
  Common Issues and Troubleshooting
  Next Steps

## · Using the Web Interface  (L4232)
  源文件: flask_app/app.py, flask_app/static/css/style.css, flask_app/templates/index.html
  Overview
    · User Interaction Flow
  Web Interface Architecture
  Web Interface Components
  Using the Web Interface
    · Accessing the Interface
    · Submitting an Objective
    · Viewing Results
  Data Flow in the Web Interface
  Best Practices
  Troubleshooting

## · Customizing Maestro  (L4402)
  源文件: README.md, maestro-gpt4o.py, maestro-ollama.py
  Model Configuration
    · Customizing Model Selection
  LLM Provider Configuration
    · Setting API Keys
  Customizing Local Models
    · Ollama Implementation
    · LM Studio Implementation
  Customizing Prompts
    · Orchestrator Prompts
    · Sub-agent Prompts
    · Refiner Prompts
  Integrating Search Capability
    · Enabling Search
  Customizing Output Generation
    · Exchange Log Customization
    · Code Generation Customization
  Advanced Customization
    · Customizing the Main Loop
    · Customizing Model Parameters
  Example Customization Scenarios
  Summary

## · Troubleshooting & FAQ  (L4883)
  源文件: README.md, maestro-gpt4o.py, maestro-ollama.py
  Common Installation Issues
    · API Key Configuration Problems
    · Package Installation Issues
  Runtime Issues
    · Model Selection Problems
    · Response Truncation Issues
  Integration Issues
    · Local LLM Integration
    · Search Integration Issues
  Code Generation Issues
    · JSON Parsing Errors
  Technical FAQ
    · How do I resume a previously interrupted task?
    · How do I customize the models used for different roles?
    · What are the token limits and how do I handle them?
    · How do I troubleshoot file processing issues?
  Performance Considerations
    · Cost Optimization
  Diagrams
    · Error Resolution Flow
    · Maestro Technical Architecture