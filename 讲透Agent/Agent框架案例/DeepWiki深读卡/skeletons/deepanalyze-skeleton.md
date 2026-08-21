# Skeleton: deepanalyze（50 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Home | L6 | 18KB | 6 | ~9 | 7 |
| 2 | Getting Started | L495 | 23KB | 5 | ~10 | 11 |
| 3 | Model and Training | L1295 | 18KB | 5 | ~11 | 7 |
| 4 | DeepAnalyze-8B Model | L1850 | 14KB | 4 | ~7 | 11 |
| 5 | Training Pipeline | L2288 | 16KB | 6 | ~5 | 7 |
| 6 | DataScience-Instruct-500K Dataset | L2793 | 15KB | 4 | ~13 | 7 |
| 7 | Deployment | L3276 | 27KB | 6 | ~15 | 11 |
| 8 | vLLM Server Setup | L4293 | 24KB | 7 | ~16 | 7 |
| 9 | Model Quantization | L5118 | 16KB | 6 | ~8 | 7 |
| 10 | Docker Deployment | L5599 | 17KB | 4 | ~10 | 4 |
| 11 | GPU Requirements and Configuration | L6205 | 15KB | 4 | ~5 | 11 |
| 12 | Frontend Interfaces | L6650 | 13KB | 6 | ~15 | 7 |
| 13 | WebUI | L7015 | 28KB | 10 | ~14 | 12 |
| 14 | Command Line Interface (CLI) | L7899 | 26KB | 7 | ~7 | 10 |
| 15 | JupyterUI | L8772 | 15KB | 4 | ~7 | 15 |
| 16 | Gradio Apps | L9161 | 18KB | 4 | ~14 | 7 |
| 17 | Python SDK | L9743 | 24KB | 4 | ~15 | 11 |
| 18 | API Server Architecture | L10530 | 30KB | 9 | ~10 | 7 |
| 19 | Application Setup and Entry Points | L11296 | 15KB | 5 | ~7 | 8 |
| 20 | Configuration System | L11748 | 12KB | 2 | ~20 | 3 |
| 21 | Data Models | L12009 | 19KB | 3 | ~41 | 3 |
| 22 | Storage Layer | L12566 | 16KB | 7 | ~8 | 2 |
| 23 | Core Utilities | L13069 | 22KB | 7 | ~5 | 2 |
| 24 | Chat Completions API | L13731 | 16KB | 4 | ~10 | 4 |
| 25 | Code Execution and Agentic Loop | L14286 | 20KB | 4 | ~16 | 7 |
| 26 | Workspace and File Tracking | L14935 | 17KB | 6 | ~2 | 4 |
| 27 | Report Generation | L15501 | 23KB | 2 | ~7 | 5 |
| 28 | File Management API | L16189 | 14KB | 3 | ~12 | 5 |
| 29 | Models API | L16594 | 15KB | 4 | ~2 | 2 |
| 30 | Admin API | L17067 | 13KB | 4 | ~12 | 5 |
| 31 | Using DeepAnalyze | L17484 | 22KB | 13 | ~23 | 7 |
| 32 | Quick Start Guide | L18224 | 12KB | 3 | ~8 | 7 |
| 33 | API Key Configuration | L18672 | 18KB | 3 | ~4 | 7 |
| 34 | File Upload and Management | L19243 | 18KB | 6 | ~20 | 15 |
| 35 | Multi-turn Conversations | L19903 | 23KB | 5 | ~5 | 7 |
| 36 | Working with Workspaces | L20663 | 16KB | 5 | ~9 | 5 |
| 37 | Using OpenAI SDK | L21143 | 22KB | 4 | ~3 | 2 |
| 38 | Direct HTTP Requests | L21888 | 24KB | 2 | ~16 | 7 |
| 39 | Example Use Cases | L22771 | 13KB | 2 | ~4 | 5 |
| 40 | Simpson's Paradox Analysis | L23179 | 35KB | 6 | ~15 | 3 |
| 41 | Financial Insights and API Usage Analytics | L24180 | 19KB | 3 | ~5 | 2 |
| 42 | Development and Contributing | L24769 | 18KB | 3 | ~17 | 8 |
| 43 | Project Structure | L25338 | 30KB | 9 | ~7 | 8 |
| 44 | Development Environment Setup | L26221 | 19KB | 6 | ~9 | 8 |
| 45 | Contributing Guidelines | L26927 | 14KB | 4 | ~11 | 7 |
| 46 | Reference | L27305 | 32KB | 7 | ~46 | 7 |
| 47 | API Endpoints Reference | L28280 | 24KB | 3 | ~43 | 9 |
| 48 | Configuration Options | L29197 | 17KB | 6 | ~18 | 3 |
| 49 | Action Tags Reference | L29661 | 24KB | 4 | ~7 | 7 |
| 50 | License and Citation | L30347 | 14KB | 2 | ~20 | 7 |


## · Home  (L6)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  What is DeepAnalyze?
  Core Capabilities
  System Architecture Overview
  Key Components and Code Entities
    · Model and Inference
    · API Server Components
    · Frontend Interfaces
  Workspace and Thread Management
  Agentic Workflow: Code Execution Loop
  Training Pipeline
  Deployment Options
  How DeepAnalyze Differs from Traditional LLMs
  Getting Started
  Repository Structure
  Additional Resources

## · Getting Started  (L495)
  源文件: README.md, assets/wechat.jpg, docker/.dockerignore, docker/Dockerfile, docker/README.md, docker/docker-compose.yml, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Prerequisites
    · System Requirements
    · GPU Memory Requirements
    · Python Dependencies
  Installation
    · Basic Installation
    · Repository Structure
  Deployment Options
    · Deployment Decision Flow
    · Option 1: DeepAnalyze API (Recommended for First-Time Users)
    · Option 2: Local vLLM Deployment
    · Option 3: Docker Deployment
  Running Your First Analysis
    · Quick Start with Python SDK
    · Launching the API Server and Frontend Interfaces
    · Interface Options
    · Example: First Analysis with WebUI
  Configuration Reference
    · API Server Configuration
    · Model Configuration
  Verification and Testing
    · Verify vLLM Server
    · Verify API Server
    · Test Analysis with cURL
  Troubleshooting
    · Common Issues
  Next Steps

## · Model and Training  (L1295)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  Model Overview
    · Base Model and Architecture
    · Special Token Extensions
  Training Methodology
    · Stage 1: Single-Ability Training
    · Stage 2: Multi-Ability Cold Start
    · Stage 3: Reinforcement Learning Optimization
  Dataset: DataScience-Instruct-500K
    · Dataset Structure
    · Data Sources
    · SFT Portion
    · RL Portion
  Model Quantization
    · Quantization Methods
    · GPU Memory Configuration Matrix
  Complete Training-to-Deployment Workflow
    · Step-by-Step Training Instructions
  Training Requirements and Dependencies
    · Environment Setup
    · Framework Dependencies
    · Hardware Requirements
  Model Artifacts and Distribution
    · Official Release Channels
    · Model Files
    · License and Citation

## · DeepAnalyze-8B Model  (L1850)
  源文件: README.md, assets/wechat.jpg, demo/deepanalyze_general/README.md, demo/deepanalyze_general/README_ZH.md, demo/deepanalyze_general/__init__.py, demo/deepanalyze_general/deepanalyze_general.py, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  Base Model Foundation
    · Model Specifications
    · Token Extension Process
  Action Tag System
    · Core Action Tags
    · System Prompt Architecture
  Model Workflow Execution
    · Single-Turn Reasoning Cycle
    · Code Execution Environment
  Model Quantization and Variants
    · Quantization Options
    · Quantization Process
    · Quantization Implementation Diagram
  Deployment Configurations
    · GPU Memory Requirements Matrix
    · vLLM Launch Commands
    · Deployment Architecture
  Model Capabilities
    · Autonomous Data Science Workflow
    · Multi-Turn Reasoning
    · Interactive Clarification (Optional)
    · Language Support
  Model Access and Distribution
    · Official Repositories
    · Installation Requirements
    · API Key Access
  Related Pages

## · Training Pipeline  (L2288)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  Training Pipeline Overview
    · Training Pipeline Architecture
  Base Model Preparation
    · Base Model Selection
    · Special Token Addition
    · Special Token Structure
  Training Data Structure
  Stage 1: Single-Ability Fine-Tuning
    · Objective
    · Training Script
    · Training Configuration
  Stage 2: Multi-Ability Cold Start
    · Objective
    · Training Script
    · Training Characteristics
  Stage 3: Reinforcement Learning Optimization
    · Objective
    · Training Script and Framework
    · Reinforcement Learning Components
  Training Frameworks
    · ms-swift
    · SkyRL
  Training Environment Setup
    · Dependency Separation
  Training Execution Summary
    · Complete Training Pipeline
    · Directory Structure for Training
  Output Model and Post-Training
    · DeepAnalyze-8B Model
    · Post-Training Quantization
  Training from Existing DeepAnalyze-8B
  Summary

## · DataScience-Instruct-500K Dataset  (L2793)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  Dataset Overview
    · Key Characteristics
  Dataset Structure
    · Directory Organization
    · SFT Portion
    · RL Portion
  Data Format and Schema
    · SFT Data Format
    · Action Tags in Training Data
    · RL Data Format
  Usage in Training Pipeline
    · Training Script Integration
  Dataset Access and Preparation
    · Downloading the Dataset
    · Required Preparation Steps
  Data Sources and Composition
    · Source Datasets
    · Source Dataset Details
    · Data Enhancement
  Dataset Statistics
    · Task Distribution
    · File Type Coverage
  Integration with Training Frameworks
    · ms-swift Integration (SFT Stages)
    · SkyRL Integration (RL Stage)
  Using the Dataset for Custom Training
    · Example: Loading SFT Data
    · Example: Preparing RL Data
  Data Quality and Validation
    · Quality Assurance
    · Known Limitations
  Citation and License
  Related Resources

## · Deployment  (L3276)
  源文件: README.md, assets/wechat.jpg, docker/.dockerignore, docker/Dockerfile, docker/README.md, docker/docker-compose.yml, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Deployment Architecture Overview
  Prerequisites and Dependencies
    · System Requirements
    · Python Dependencies
    · Environment Setup
  Model Download and Preparation
    · Obtaining the Model
    · Model Variants
    · Building from Base Model
  vLLM Server Deployment
    · Overview
    · Basic Deployment Command
    · GPU Memory Configuration Matrix
    · Deployment Scenarios with Commands
    · Verifying Deployment
  Model Quantization
    · Overview
    · Quantization Methods
    · 4-bit Quantization
    · 8-bit Quantization
    · Running Quantization
    · Quantization Output Structure
  Docker Deployment
    · Overview
    · Docker Architecture
    · Docker Image Components
    · Deployment Options
    · Running vLLM in Docker
    · Docker Networking
    · Volume Mounts
  API Server and Frontend Deployment
    · Starting the API Server
    · Frontend Deployment
    · Complete Deployment Checklist
  Configuration Reference
    · Key Configuration Files
    · Environment Variables
    · Port Summary
    · Hardware Configuration Matrix
  Troubleshooting Deployment Issues
    · Common Issues
    · Verification Commands
  Production Deployment Considerations
    · Scaling Strategies
    · Monitoring and Logging
    · Security Considerations
    · Backup and Recovery

## · vLLM Server Setup  (L4293)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  vLLM Role in DeepAnalyze Architecture
  Prerequisites
    · System Requirements
    · Installing vLLM
  Basic Deployment
    · Obtaining the Model
    · GPU Memory Configuration
    · Starting the vLLM Server
    · Deployment Examples by GPU Memory
    · Deployment Workflow
  Configuration Options
    · Model-Specific Configuration
    · Advanced vLLM Server Options
  Connecting to the API Server
    · Configuration Verification
  API Server Integration
  Testing the Inference Pipeline
    · Direct vLLM Test
    · End-to-End Test
  Model Path and Naming Configuration
    · Understanding --model vs --served-model-name
    · Configuration Scenarios
    · Configuration Alignment Table
  Multi-Instance Deployment
    · Load Balancing Architecture
    · Deployment Commands
    · Load Balancer Configuration (Nginx)
  Troubleshooting
    · Common Issues
  Monitoring and Logging
    · vLLM Server Logs
    · Performance Metrics
  Integration with Different Client Interfaces
  Summary

## · Model Quantization  (L5118)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  Quantization Architecture
  The quantize.py Utility
    · Command-Line Interface
    · Basic Usage
  4-bit Quantization (NF4)
    · Configuration Parameters
    · Function Implementation
  8-bit Quantization (INT8)
    · Configuration Parameters
    · Function Implementation
  Memory and Performance Trade-offs
    · Deployment Configuration Matrix
    · Trade-off Analysis
  Integration with vLLM Deployment
    · Example Deployment Commands
  Quick Selection Guide
  Technical Implementation Details
    · BitsAndBytesConfig Entity Mapping
    · Dependencies
    · Output Directory Structure
  Common Issues and Considerations
    · Double Quantization
    · GPU Memory During Quantization
    · vLLM Compatibility

## · Docker Deployment  (L5599)
  源文件: docker/.dockerignore, docker/Dockerfile, docker/README.md, docker/docker-compose.yml
  Purpose and Scope
  Docker Environment Overview
    · Dockerfile Structure
    · Installed Components
    · Image Size Breakdown
  Deployment Methods
    · Deployment Workflow
    · Method 1: Pull Pre-built Image
    · Method 2: Build from Source
  Docker Compose Configuration
    · Service Architecture
    · Configuration File
  Running vLLM Server in Docker
    · Manual Startup
    · Direct Docker Run
    · Verifying Deployment
  Integration with DeepAnalyze API Server
    · API Server Configuration
    · Running API Server on Host
    · Alternative: All Services in Docker
  Production Considerations
    · Security
    · Resource Management
    · Logging
    · High Availability
    · Monitoring
  Summary

## · GPU Requirements and Configuration  (L6205)
  源文件: README.md, assets/wechat.jpg, docker/.dockerignore, docker/Dockerfile, docker/README.md, docker/docker-compose.yml, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  GPU Requirements Overview
    · Base Requirements
  Model Variants and Memory Footprint
    · Original Model (bf16/fp32)
    · 8-bit Quantized Model
    · 4-bit Quantized Model
  Configuration Matrix
    · Configuration Parameters Explained
  vLLM Configuration Parameters
    · Memory Allocation Breakdown
    · Core vLLM Server Arguments
  Deployment Scenarios
    · Scenario 1: Consumer GPUs (16GB VRAM)
    · Scenario 2: Professional GPUs (24GB VRAM)
    · Scenario 3: Enterprise GPUs (40GB+ VRAM)
  Context Length vs. Memory Trade-offs
    · Memory Consumption Formula
  Performance Considerations
    · Inference Speed
    · Quality Trade-offs
    · Concurrency and Batching
  Docker Deployment with GPU
  Quick Selection Guide

## · Frontend Interfaces  (L6650)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  Overview of Available Interfaces
  Frontend-Backend Architecture
  Interface Comparison Matrix
  Common Communication Patterns
    · File Upload Flow
    · Chat Completion Flow
  Detailed Interface Specifications
    · Connection Endpoints
    · Session Management
  Language Support
  Startup and Deployment
    · Startup Sequences by Interface
    · Gradio Embedded API Pattern
  File Format Support
  Feature Comparison: Standard Frontends vs Python SDK
    · Python SDK Return Format
  Next Steps

## · WebUI  (L7015)
  源文件: README.md, assets/wechat.jpg, demo/chat/backend.py, demo/chat/frontend/components/three-panel-interface.tsx, demo/chat/frontend/package-lock.json, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, docs/FAQ.md, docs/FAQ_ZH.md, example/README.md, quantize.py, requirements.txt
  Architecture Overview
  Frontend Structure
    · Three-Panel Layout
    · Key React Components and Libraries
  Backend Integration
    · API Communication
    · Session Management
  Key Features
    · File Management
    · Chat Interface
    · Code Editor
    · File Preview System
  Data Flow: Complete Analysis Session
  Deployment
    · Prerequisites
    · Installation Steps
    · Using start.sh Script
    · Remote Deployment Considerations
  Component Reference Table

## · Command Line Interface (CLI)  (L7899)
  源文件: API/README_ZH.md, README.md, assets/wechat.jpg, demo/cli/api_cli.py, demo/cli/api_cli_ZH.py, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  Overview
  System Architecture
    · CLI Integration with Backend Services
  Prerequisites and Startup
    · Starting the CLI
  Interface Components
    · DeepAnalyzeCLI Class Structure
  Command Reference
    · Available Commands
    · Help Command Output
  File Management
    · File Upload Workflow
    · File Upload Implementation
    · File Listing
    · File Deletion and Download
  Chat and Analysis
    · Streaming Chat Flow
    · Chat Implementation Details
  Thread and Workspace Management
    · Thread Persistence
    · Workspace File Tracking
  Session Management
    · Command History
    · Conversation History Management
    · Clear Operations
  System Status
    · Status Command Output
  Interactive Mode
    · Main Event Loop
  Bilingual Support
    · Language Variants
  Implementation Summary
    · Key Design Patterns
    · Dependencies
    · Entry Point

## · JupyterUI  (L8772)
  源文件: README.md, assets/wechat.jpg, demo/jupyter/.env.example, demo/jupyter/.gitignore, demo/jupyter/.python-version, demo/jupyter/mcp_tools.py, demo/jupyter/pyproject.toml, demo/jupyter/test/mock_server.py, demo/jupyter/utils.py, demo/jupyter/uv.lock, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md
  Overview and Integration Architecture
  Core Components
    · 1. MCP Tools Module (`mcp_tools.py`)
    · 2. Utility Functions (`utils.py`)
    · 3. Dependency Management
  Cell Conversion Mechanism
  Configuration and Environment
    · Environment Variables
    · Python Version
    · Workspace and Cache Management
  Testing Infrastructure
    · Mock Server for Development
  Complete Interaction Flow
  Key Differences from Other Frontends
  Integration Requirements

## · Gradio Apps  (L9161)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  Architecture Overview
    · System Architecture Diagram
  Deployment and Setup
    · Environment Requirements
    · Automatic Service Startup
  User Interface Components
    · Component Layout
    · Preset Instruction Examples
  File Handling and ZIP Support
    · Supported File Formats
    · ZIP Archive Processing
  Integration with Backend Services
    · Request Flow Diagram
    · API Integration Details
  Usage Workflow
    · Complete Analysis Walkthrough
  Configuration Options
    · Port Configuration
    · API Endpoint Configuration
    · Authentication
  Comparison with Other Frontends
  Troubleshooting
    · Common Issues

## · Python SDK  (L9743)
  源文件: README.md, assets/wechat.jpg, demo/deepanalyze_general/README.md, demo/deepanalyze_general/README_ZH.md, demo/deepanalyze_general/__init__.py, demo/deepanalyze_general/deepanalyze_general.py, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Architecture Overview
  DeepAnalyzeVLLM Class
    · Initialization
    · Core Methods
  Action Tag System
    · Tag Definitions
    · System Prompts
  Code Execution Environment
    · Workspace Isolation
    · Namespace Persistence
    · Warning Suppression
  Usage Patterns
    · Basic Usage
    · Interactive Mode
    · Working with Workspaces
  Configuration Options
    · Model Selection
    · Sampling Parameters
    · Round Limits
  Comparison with API-Based Interfaces
    · Architectural Differences
    · Use Case Selection
    · Security Considerations
  Advanced Features
    · Custom System Prompts
    · Extended Reasoning Mode
    · Tag Extraction Utilities
  Example: Complete Analysis Workflow

## · API Server Architecture  (L10530)
  源文件: API/chat_api.py, API/config.py, API/example/exampleOpenAI.py, API/example/exampleRequest.py, API/main.py, API/models.py, API/utils.py
  Purpose and Scope
  Multi-Port Architecture
  Application Structure
  Core Components
    · Configuration System (config.py)
    · Data Models (models.py)
    · Storage Layer (storage.py)
    · Utilities Layer (utils.py)
  Request Processing Flow
    · Chat Completion Endpoint Handler
    · Code Execution Safety Mechanisms
  Application Lifecycle
  OpenAI Client Integration
  CORS Configuration
  Health Check Endpoint
  Thread and Workspace Management
    · Thread Lifecycle
    · Thread Cleanup
  Deployment Considerations
    · State Management
    · Workspace Storage
  Summary

## · Application Setup and Entry Points  (L11296)
  源文件: API/__init__.py, API/admin_api.py, API/config.py, API/example/Simpson.csv, API/file_api.py, API/main.py, API/models.py, API/start_server.py
  Purpose and Scope
  Entry Point Architecture
    · Package-Level Entry Point
    · Standalone Script Entry Point
    · Module Entry Point
  Application Factory: create_app()
    · FastAPI Instance Creation
    · CORS Middleware Configuration
  Router Registration
    · Router Import and Registration
  Health Check Endpoint
  Server Startup: main()
    · Startup Information Display
    · HTTP File Server Initialization
    · Uvicorn Server Launch
  Multi-Process Architecture
    · Thread Safety Considerations
  Configuration Dependencies
  Summary

## · Configuration System  (L11748)
  源文件: API/config.py, API/main.py, API/models.py
  Purpose and Scope
  Configuration Architecture
  Configuration Categories
    · External Service Configuration
    · API Server Configuration
    · Workspace and File Storage
    · File Handling
    · Thread Management
    · Code Execution
    · Model Configuration
  Configuration Flow
  Environment Variables
  Configuration Reference Table
  Usage Pattern

## · Data Models  (L12009)
  源文件: API/config.py, API/main.py, API/models.py
  Overview
  Model Category Diagram
  File Management Models
    · FileObject
    · FileDeleteResponse
    · FileInfo
  Thread Management Models
    · ThreadObject
    · MessageObject
  Chat Completion Models
    · ChatCompletionRequest
    · ChatCompletionResponse
    · ChatCompletionChoice
    · ChatCompletionChunk
  Chat Completion Flow Diagram
  Administrative Models
    · ThreadCleanupRequest
    · ThreadCleanupResponse
    · ThreadStatsResponse
  Model Information Models
    · ModelObject
    · ModelsListResponse
  Health Monitoring Models
    · HealthResponse
  Model Relationships and Data Flow
  OpenAI Compatibility Fields
  DeepAnalyze-Specific Extensions
    · Generated Files Support
    · Attached Files Tracking
    · Thread Access Tracking
  Type Safety and Validation
  Model Imports and Usage

## · Storage Layer  (L12566)
  源文件: API/models_api.py, API/storage.py
  Purpose and Scope
  Storage Architecture Overview
    · Storage Class Structure
  In-Memory Data Structures
  File Storage Operations
    · Creating File Records
    · Retrieving and Managing Files
  Thread Storage Operations
    · Thread Creation and Workspace Initialization
    · File Copying to Thread Workspace
    · Thread Retrieval and Access Tracking
    · Thread Deletion and Workspace Cleanup
  Message Storage Operations
    · Message Creation
    · Message Retrieval
  Thread Lifecycle Management
    · Automatic Cleanup of Expired Threads
  Thread Safety and Concurrency
    · Lock Acquisition Patterns
  Integration with File System
    · Workspace Directory Management
    · Utility Functions Used
  Global Storage Instance
  Summary

## · Core Utilities  (L13069)
  源文件: API/example/exampleOpenAI.py, API/utils.py
  Overview
  Utility Function Pipeline
  Message Preparation
    · Overview
    · prepare_vllm_messages Function
  Code Execution System
    · Sandboxed Execution Architecture
    · Implementation Details
  Workspace Tracking
    · WorkspaceTracker Class
    · Implementation Details
    · Usage Pattern
  Report Generation
    · Architecture
    · extract_sections_from_history Function
  对话轮次 1
    · 用户指令
    · 助手响应
    · generate_report_from_messages Function
  File Management Utilities
    · Workspace and URL Functions
    · get_thread_workspace
    · build_download_url
    · render_file_block
  HTTP File Server
    · start_http_server Function
    · Implementation Details
  Utility Integration Examples
    · Example: Complete Message Processing Flow
    · Example: Multi-Turn Workflow
  Summary

## · Chat Completions API  (L13731)
  源文件: API/chat_api.py, API/example/exampleOpenAI.py, API/example/exampleRequest.py, API/utils.py
  Purpose and Scope
  Endpoint Definition
  Request Parameters
    · Message Format
  Response Format
    · Non-Streaming Response
    · Streaming Response
  Request Processing Flow
  File Attachment System
    · File Collection Process
  Message Processing and Template Injection
  Streaming vs Non-Streaming Modes
    · Mode Comparison
    · Streaming Implementation
    · Non-Streaming Implementation
  OpenAI SDK Compatibility
    · Supported Client Initialization
    · File Attachment Formats
    · Response Access Patterns
  Generated Files Structure
    · File Metadata Format
    · Location in Response
    · URL Construction
  Configuration Parameters
  Code Entity Reference
    · Main Router and Handler
    · Client Instances
    · Key Functions Called
  Error Handling
    · File Not Found
    · Execution Timeout
    · Thread Cleanup

## · Code Execution and Agentic Loop  (L14286)
  源文件: API/chat_api.py, API/example/exampleOpenAI.py, API/example/exampleRequest.py, API/utils.py, demo/chat/backend.py, docs/FAQ.md, docs/FAQ_ZH.md
  Purpose and Scope
  Agentic Loop Architecture
    · Loop Flow Diagram
  Code Extraction Mechanism
    · Tag Structure
    · Extraction Logic
  Sandboxed Code Execution
    · Execution Architecture
    · Subprocess Configuration
    · Chinese Font Injection
  Result Injection and Loop Continuation
    · Message Flow Through Loop Iterations
    · Message Array Structure
  Loop Termination Logic
    · Termination Conditions
    · Termination Rule Table
    · Edge Case Handling
  Streaming vs Non-Streaming Execution
    · Implementation Comparison
    · Streaming Response Format
  Complete Loop Implementation
    · Core Loop Structure
  Error Handling and Timeouts
    · Error Handling Layers
    · Timeout Behavior
    · Error Message Format
  Example: Multi-Iteration Code Execution
    · Iteration Breakdown
  Integration with Frontend Interfaces
    · Frontend Consumption Patterns
  Performance Considerations
    · Latency Components
    · Iteration Count

## · Workspace and File Tracking  (L14935)
  源文件: API/chat_api.py, API/example/exampleOpenAI.py, API/example/exampleRequest.py, API/utils.py
  Purpose and Scope
  Thread-Based Workspace Isolation
    · Workspace Directory Structure
    · Workspace Creation and Management
  The WorkspaceTracker Class
    · Class Architecture
    · Initialization and State Capture
  File Detection Algorithm
    · Detection Flow
    · Implementation
    · File Processing Logic
  File Collection Process
    · Collection Workflow
    · Path Uniquification
    · Error Handling
  Integration with Chat Completions API
    · Lifecycle in Streaming Mode
    · Instantiation in Chat API
    · Artifact Collection After Code Execution
  File URL Generation and Access
    · URL Building Process
    · build_download_url Function
    · render_file_block Function
    · File Metadata Structure
  Usage Examples
    · Multi-Turn Workflow with File Tracking
    · Example: Streaming with File Tracking
  Summary

## · Report Generation  (L15501)
  源文件: API/example/exampleOpenAI.py, API/utils.py, demo/chat/backend.py, docs/FAQ.md, docs/FAQ_ZH.md
  Purpose and Scope
  Overview
  Report Structure
    · Main Body
    · Appendix Structure
  对话轮次 1
    · 用户指令
    · 助手响应
  对话轮次 2
    · 用户指令
    · 助手响应
  Section Extraction Process
    · Tag Pattern Recognition
    · Three-Phase Processing
    · Report Assembly
  Report Generation Workflow
    · End-to-End Process
    · Function Call Sequence
  Integration with Chat Completions
    · Streaming Response Integration
    · Non-Streaming Response Integration
  File Persistence and Delivery
    · Directory Structure
    · Filename Convention
    · Download Access
  Error Handling
    · Fallback Content
    · Silent Failure
  Key Functions Reference
  Alternative: On-Demand Report Export
    · Export Endpoint
    · PDF Generation
  Related Configuration

## · File Management API  (L16189)
  源文件: API/__init__.py, API/admin_api.py, API/example/Simpson.csv, API/file_api.py, API/start_server.py
  Purpose and Scope
  Overview
  System Architecture
  Endpoint Specifications
    · POST /v1/files - File Upload
    · GET /v1/files - List Files
    · GET /v1/files/{file_id} - Retrieve File Metadata
    · DELETE /v1/files/{file_id} - Delete File
    · GET /v1/files/{file_id}/content - Download File Content
  File Lifecycle and Data Flow
  File ID Generation and Storage Structure
    · File ID Format
    · Storage Locations
  Error Handling
    · Error Recovery
  Integration with Other Components
  OpenAI Compatibility
  Thread Safety and Concurrency

## · Models API  (L16594)
  源文件: API/models_api.py, API/storage.py
  Purpose and Scope
  Overview
  API Architecture
  Endpoint Reference
    · List Models
    · Retrieve Model
  Data Models
    · ModelObject
    · ModelsListResponse
  Router Configuration
  OpenAI Compatibility
    · Using with OpenAI Python SDK
    · Using with HTTP Requests
  Implementation Flow
  Extension Points
    · Adding New Models
    · Model Validation
    · Dynamic Model Discovery
  Configuration Dependencies
  Relationship to Other Components

## · Admin API  (L17067)
  源文件: API/__init__.py, API/admin_api.py, API/example/Simpson.csv, API/file_api.py, API/start_server.py
  Overview
  Router Configuration
  Admin API Router Architecture
  Thread Cleanup Endpoint
    · Endpoint Specification
    · Purpose
    · Request Parameters
    · Response Format
    · Thread Cleanup Flow
    · Error Handling
  Thread Statistics Endpoint
    · Endpoint Specification
    · Purpose
    · Response Format
    · Thread Age Categories
    · Thread Statistics Collection Flow
    · Thread-Safe Statistics
  Thread Age Calculation Logic
  Integration with Storage Layer
  Usage Patterns
    · Periodic Cleanup
    · Monitoring
  Configuration Dependencies
  Model Dependencies
  Security Considerations

## · Using DeepAnalyze  (L17484)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Overview of Usage Options
  Deployment Modes
  System Architecture Overview
  Common Workflows
    · Workflow 1: Single-Turn Analysis
    · Workflow 2: Multi-Turn Iterative Analysis
    · Workflow 3: Batch File Analysis
    · Workflow 4: Report Generation
  Response Formats
  Client Initialization
    · OpenAI SDK Method
    · Direct HTTP Method
  File Operations
    · Upload Workflow
    · File Lifecycle
  Chat Completions
    · Basic Request
    · Request with Files
  Streaming Responses
    · Streaming Pattern
    · File Collection in Streaming
  Error Handling
    · Common Error Patterns
    · Connection Verification
    · Model Availability Check
  Best Practices
    · Request Configuration
    · Workspace Management
  Code Entity Reference
    · Core API Functions
    · Data Models
    · Storage Operations

## · Quick Start Guide  (L18224)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Prerequisites
    · Python Environment
    · Core Dependencies
  System Deployment Architecture
  Step 1: Model Server Setup
    · Download the Model
    · Start vLLM Server
  Step 2: API Server Startup
    · Startup Sequence
    · Start the API Server
    · Server Endpoints
  Step 3: Verify Installation
    · Health Check
    · Check Available Models
  Configuration Overview
    · Server Ports
    · Workspace Configuration
    · Model Configuration
    · Execution Configuration
  Deployment Architecture Summary
  Environment Variables
  Next Steps
  Troubleshooting

## · API Key Configuration  (L18672)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Overview: Deployment Modes and Authentication
  Obtaining API Keys for Hosted Service
    · Application Process
    · API Endpoint
  API Key Authentication Flow
    · Diagram: API Key Authentication Mechanism
  Configuring API Keys by Interface
    · WebUI (React Frontend)
    · CLI (Command Line Interface)
    · Gradio Apps
    · Python SDK and OpenAI Client
    · Direct HTTP Requests with curl
  Local Deployment Configuration
    · No Authentication Required
    · Starting Local Services
    · Diagram: Local Deployment Configuration Points
  API Key Format and Security
    · Key Format
    · Authentication Implementation
  Security Considerations
    · Hosted Service
    · Local Deployment
    · Diagram: Security Boundaries
  Configuration Reference Table

## · File Upload and Management  (L19243)
  源文件: API/README_ZH.md, API/__init__.py, API/admin_api.py, API/example/Simpson.csv, API/file_api.py, API/start_server.py, README.md, assets/wechat.jpg, demo/cli/api_cli.py, demo/cli/api_cli_ZH.py, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md
  Purpose and Scope
  File Upload Methods
    · Upload via HTTP API
    · Upload via OpenAI SDK
    · Upload via CLI Interface
  File Storage Architecture
    · Storage Locations
    · File ID Generation
    · Storage Manager Operations
  File Metadata and Retrieval
    · File Object Structure
    · Listing Files
    · Downloading File Content
  File Lifecycle in Conversations
    · File Integration with Threads
    · File Context Injection
  File Deletion and Cleanup
    · Manual File Deletion
    · Thread Cleanup
    · CLI Cleanup Commands
  Supported File Formats
    · Structured Data
    · Semi-Structured Data
    · Code and Scripts
    · Documents and Media
  File Viewing in CLI
    · User Uploaded Files Table
    · AI Generated Files in Workspace
  Integration with Chat API
  File URLs and Download Links

## · Multi-turn Conversations  (L19903)
  源文件: API/README_ZH.md, API/chat_api.py, API/example/exampleOpenAI.py, API/example/exampleRequest.py, API/utils.py, demo/cli/api_cli.py, demo/cli/api_cli_ZH.py
  Overview
  Thread Lifecycle and Workspace Management
    · Thread Creation Flow
    · Thread Continuation Flow
  Thread Storage and Data Structures
    · In-Memory Storage Schema
    · Workspace Directory Structure
  Message Format and thread_id Handling
    · Request Message Structure
    · Response Message Structure
  Message History Management
    · Conversation History Construction
    · File Context Injection
  Multi-turn Workflow Implementation
    · Complete 2-Turn Example Flow
  Usage Examples
    · OpenAI SDK Example
    · Direct HTTP Requests Example
    · CLI Multi-turn Conversation
  Thread Management and Cleanup
    · Thread Lifecycle Commands
    · Workspace Persistence Behavior
  Best Practices
    · Client-Side Requirements
    · Thread Management Strategies
  Common Issues and Solutions
    · Issue: "Thread not found" Error
    · Issue: Files Not Found in Subsequent Turns
    · Issue: Conversation History Not Maintained

## · Working with Workspaces  (L20663)
  源文件: API/example/exampleOpenAI.py, API/utils.py, demo/chat/backend.py, docs/FAQ.md, docs/FAQ_ZH.md
  Purpose and Scope
  Thread-Based Workspace Isolation
  Workspace Directory Structure
  Workspace Lifecycle
  The `generated/` Folder
  WorkspaceTracker Class
  Accessing Workspace Files
  Workspace Cleanup
  Workspace Best Practices
  Integration Examples

## · Using OpenAI SDK  (L21143)
  源文件: API/example/exampleOpenAI.py, API/utils.py
  Client Configuration
  OpenAI SDK Integration Architecture
  File Management
    · Uploading Files
    · Listing Files
    · Retrieving File Content
    · Deleting Files
  File Operations Flow
  Chat Completions
    · Basic Chat Completion (Non-streaming)
    · Chat Completion with File Attachments
    · Streaming Chat Completions
  Multi-turn Conversations with Thread ID
    · Thread-based Conversation Flow
    · Complete Multi-turn Example
  Accessing Generated Files
    · Generated Files Structure
    · Accessing Generated Files in Non-streaming Responses
    · Collecting Generated Files During Streaming
  Generated Files Download Architecture
  DeepAnalyze-Specific Extensions
    · Extended Response Attributes
    · Message Extensions
    · API Key Handling
  Complete Example Script
  Reference Implementation

## · Direct HTTP Requests  (L21888)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Purpose and Scope
  Base Configuration
  HTTP Request Structure Overview
  File Upload Endpoint
    · POST /v1/files
  Chat Completions Endpoint
    · POST /v1/chat/completions
  Multi-Turn Conversations
  Other API Endpoints
    · GET /v1/files
    · GET /v1/files/{file_id}
    · DELETE /v1/files/{file_id}
    · GET /v1/models
    · POST /v1/threads/cleanup
    · GET /v1/admin/stats
  Downloading Generated Files
  Streaming Response Handling
    · curl with Streaming
    · Python with requests
    · httpie with Streaming
  Complete Workflow Example
    · Shell Script Example
  Error Handling
    · Common Error Responses
    · Error Response Format
    · Handling Specific Errors
  Testing with Different HTTP Clients
    · Postman Collection
    · HTTPie Examples
    · wget Example
  Advanced Usage Patterns
    · Parallel File Upload
    · Batch Processing
    · Custom Headers and Authentication
    · Monitoring Long-Running Analysis
  Comparison with OpenAI SDK

## · Example Use Cases  (L22771)
  源文件: example/financial_insights_and_api_usage_analytics/bank_data.xlsx, example/financial_insights_and_api_usage_analytics/interface_calls.xlsx, example/simpson_paradox_analysis/README.md, example/simpson_paradox_analysis/data/Simpson.csv, example/simpson_paradox_analysis/prompt.txt
  Purpose and Scope
  Available Example Use Cases
  Running Examples
    · Method 1: Python SDK (Programmatic Access)
    · Method 2: API with Thread-Based Sessions
    · Method 3: Command Line Interface
  Example Workflow Architecture
  Common Patterns Across Examples
    · Pattern 1: Iterative Debugging
    · Pattern 2: Multi-Step Analysis
    · Pattern 3: Workspace File Management
  Example Categories
    · Statistical Analysis Examples
    · Business Analytics Examples
  Detailed Walkthroughs
  Running Custom Examples
  Sources

## · Simpson's Paradox Analysis  (L23179)
  源文件: example/simpson_paradox_analysis/README.md, example/simpson_paradox_analysis/data/Simpson.csv, example/simpson_paradox_analysis/prompt.txt
  Overview
  Problem Setup
  DeepAnalyze's Iterative Analysis Process
  Key Analysis Steps with Code Examples
    · Step 1: Initial Data Loading (Lines 80-125)
    · Step 2: Naive Aggregate Analysis (Lines 236-334)
    · Step 3: Stratified Analysis Discovery (Lines 236-298)
    · Step 4-5: Iterative Debugging (Lines 313-990)
    · Step 6: Final Statistical Model (Lines 876-1004)
  Execution Architecture
  Final Output and Insights
    · Generated Artifacts
    · Key Findings
  Comparison with Other LLMs
    · Failure Modes of Other Models
    · Why Models Fail
    · DeepAnalyze's Advantages
  Running the Example
    · Using the Python SDK
    · Using the OpenAI-Compatible API
  Technical Implementation Details
    · Workspace Isolation
    · Code Execution Safety
    · Artifact Detection
    · Report Generation
  Configuration Parameters
  Key Takeaways
  Using the API Example
    · File Upload
    · Chat Completion with File Attachment
    · Response Structure
  Code Entity Mapping
  Typical Analysis Steps
    · 1. Data Loading and Initial Exploration
    · 2. Overall Treatment Effect Analysis
    · 3. Stratified Analysis
    · 4. Visualization Generation
  Execution Flow Details
  Expected Outputs
    · Generated Files
    · Report Structure
  Streaming Support
  File Access Patterns
  Configuration Parameters
  Practical Considerations
    · Memory Requirements
    · Execution Safety
    · Artifact Collection
  Integration Example

## · Financial Insights and API Usage Analytics  (L24180)
  源文件: example/financial_insights_and_api_usage_analytics/bank_data.xlsx, example/financial_insights_and_api_usage_analytics/interface_calls.xlsx
  Purpose and Scope
  Example Datasets
  Workflow Overview
  Financial Data Analysis Example
    · Dataset Characteristics
    · Analysis Workflow
    · Typical Analysis Steps
    · Generated Artifacts
  API Usage Analytics Example
    · Dataset Characteristics
    · Analysis Capabilities
    · Common Insights Extracted
    · Code Execution Environment
  Key Capabilities Demonstrated
    · 1. Multi-File Analysis
    · 2. Iterative Refinement
    · 3. Autonomous Code Generation
    · 4. Structured Output Format
  Frontend Integration Examples
    · Using the WebUI
    · Using the CLI
    · Using the Python SDK
  Report Generation
  Executive Summary
  Customer Segmentation Analysis
  API Usage Patterns
  Recommendations
  Accessing Generated Files
  Comparison with Other Examples

## · Development and Contributing  (L24769)
  源文件: .gitignore, README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Overview
  Types of Contributions
    · Code Contributions
    · Model Contributions
    · Case Study Contributions
    · Documentation Contributions
  Repository Structure Overview
  Quick Start for Contributors
    · Basic Development Setup
    · Testing Your Changes
  Contribution Workflow
    · Standard GitHub Flow
    · Pull Request Guidelines
  Description
  Type of Change
  Testing
  Checklist
  Component-Specific Contribution Guide
    · Contributing to the API Server
    · Contributing to Frontend Interfaces
    · Contributing to Training Code
    · Contributing to Quantization
  Code Organization Patterns
    · API Server Architecture
    · Frontend Interface Patterns
  Excluded Files and Directories
  Tool Integration Summary

## · Project Structure  (L25338)
  源文件: .gitignore, README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Repository Root Structure
  Core Model Package (`deepanalyze/`)
  API Server (`API/`)
  Frontend Interfaces (`demo/`)
  Training Infrastructure
  Configuration and Deployment Files
  Examples and Documentation
  File System Conventions
  Module Import Paths and Key Classes

## · Development Environment Setup  (L26221)
  源文件: .gitignore, README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Prerequisites
  Repository Setup
    · Cloning the Repository
    · Understanding Version Control Configuration
  Python Environment Configuration
    · Creating an Isolated Environment
    · Setting Up the Inference Environment
    · Setting Up the Training Environment (Optional)
  Dependency Installation by Component
    · Frontend Dependencies (WebUI Development)
    · CLI and Jupyter Dependencies
  Component Setup and Testing
    · Directory Structure for Development
    · Setting Up vLLM Server for Development
    · Setting Up API Server for Development
    · Setting Up WebUI for Development
    · Setting Up CLI for Development
    · Setting Up JupyterUI for Development
  Development Tools and IDE Configuration
    · Recommended IDE Setup
    · VS Code Configuration Example
    · Testing API Endpoints
  Environment Validation
    · Verification Checklist
    · Common Setup Issues
    · Quick Start Verification Script
  Model Quantization for Development
  Next Steps

## · Contributing Guidelines  (L26927)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Overview
  Contribution Types and Entry Points
  Contributing Code and Model Improvements
    · Submission Process
    · Development Standards
  Contributing Case Studies
    · Purpose and Value
    · Required Folder Structure
    · README.md Requirements
    · Case Study Submission Workflow
  Contribution Areas Mapped to Code Entities
  Pull Request Process
    · Standard Workflow
    · Pre-Submission Checklist
  Contributor Recognition
  Additional Resources

## · Reference  (L27305)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  Overview
  Model Variants and Quantization
    · Available Model Formats
    · Quantization Configuration
  GPU Memory and Context Length Matrix
  vLLM Deployment Commands
    · Command Template
    · Scenario-Specific Commands
  System Port Mappings
    · Port Allocation Table
    · Service Communication Pattern
  Core Dependencies
    · Minimal Inference Requirements
    · API and UI Dependencies
  File System Paths
    · Directory Structure
    · Key Path Constants
  Command-Line Interface Quick Reference
    · CLI File Management Commands
    · CLI Startup
  API Quick Start Examples
    · File Upload and Analysis
    · Python SDK Usage
  Training Pipeline Reference
    · Training Stages
    · Training Scripts
    · Special Token Addition
  Dataset Reference
    · DataScience-Instruct-500K
    · Dataset Sources
  Contribution Guidelines
    · Contribution Types
    · Case Study Structure
  License and Citation
    · License
    · Citation
    · Contact
  External Resources
    · Official Links
    · API Key Application
  Version Control Patterns
    · Gitignore File Locations
    · Ignored Artifact Categories
    · Gitignore Pattern Specificity
    · Skyagent-Specific Patterns
  Artifact Management Guidelines
    · Files That Should Be Committed
    · Files That Should Not Be Committed
    · Data Directory Management
  Development Best Practices
    · Adding New Gitignore Patterns
    · Environment Variable Management
    · File Commit Decision Matrix
    · External System Dependencies
  Repository Health Indicators

## · API Endpoints Reference  (L28280)
  源文件: API/__init__.py, API/admin_api.py, API/chat_api.py, API/example/Simpson.csv, API/example/exampleRequest.py, API/file_api.py, API/models_api.py, API/start_server.py, API/storage.py
  Endpoint Overview
  Endpoint to Code Mapping
  Chat Completions API
    · POST /v1/chat/completions
  File Management API
    · POST /v1/files
    · GET /v1/files
    · GET /v1/files/{file_id}
    · DELETE /v1/files/{file_id}
    · GET /v1/files/{file_id}/content
  File API Storage Flow
  Models API
    · GET /v1/models
    · GET /v1/models/{model_id}
  Admin API
    · POST /v1/admin/cleanup-threads
    · GET /v1/admin/threads-stats
  Health Check Endpoint
    · GET /health
  Data Models and Types
  Complete API Reference Table
  Configuration Constants
  Error Responses
  Usage Examples
    · Example 1: Simple Chat (Non-Streaming)
    · Example 2: Chat with File Attachment
    · Example 3: Streaming Chat
    · Example 4: Multi-Turn Conversation

## · Configuration Options  (L29197)
  源文件: API/config.py, API/main.py, API/models.py
  Configuration System Overview
  Server Configuration
  vLLM Integration Configuration
  File Management Configuration
    · Directory Structure
  HTTP File Server Configuration
    · File Server Architecture
  Code Execution Configuration
    · Code Execution Flow
  Model Configuration
    · Model Configuration in Request Flow
  Thread Management Configuration
    · Thread Lifecycle
  Environment Variables
  Configuration Dependencies and Relationships
    · Complete Configuration Map
    · Key Configuration Relationships
  Configuration Usage in Code
    · Import Pattern
    · Configuration Access Map
  Summary Table: All Configuration Constants

## · Action Tags Reference  (L29661)
  源文件: demo/chat/backend.py, demo/deepanalyze_general/README.md, demo/deepanalyze_general/README_ZH.md, demo/deepanalyze_general/__init__.py, demo/deepanalyze_general/deepanalyze_general.py, docs/FAQ.md, docs/FAQ_ZH.md
  Overview of Action Tags
  Standard Action Tags
  Tag Lifecycle and State Transitions
  Detailed Tag Specifications
    · `<Analyze>` Tag
    · `<Understand>` Tag
    · `<Code>` Tag
    · `<Execute>` Tag
    · `<Answer>` / `<Finish>` Tag
  Interactive Mode Tags
    · `<Ask>` Tag
  System-Generated Output Tags
    · `<File>` Tag
  Tag Detection and Parsing
    · Tag Detection Patterns
    · Tag Auto-Completion
  Multi-Turn Workflow Example
  Core Rules and Best Practices
    · Mandatory Rules
    · Code Generation Guidelines
    · Interactive Mode Guidelines
  Frontend Rendering
  Configuration and Customization
    · Stop Token Configuration
    · Custom Tag Extensions
  Summary Table: Tag Properties

## · License and Citation  (L30347)
  源文件: README.md, assets/wechat.jpg, docs/DeepAnalyze_API_Key_Usage_Guide.md, docs/DeepAnalyze_API_Key_Usage_Guide_ZH.md, example/README.md, quantize.py, requirements.txt
  License
  Citation
    · BibTeX Format
    · Publication Details
    · Author Contact
  Model Lineage and Attribution
  Acknowledgements
    · Training Frameworks
    · Training Data Sources
    · API Services
  Runtime Dependencies
    · Core Dependencies Table
    · API Server Dependencies
    · Dependency Installation
    · Dependency Isolation
  Dependency Graph
  Quantization Tools
    · Quantization Script: `quantize.py`
  Community and Support
    · Community Channels
    · Contribution Recognition
    · Project Metrics
  Version History
  Legal and Compliance
    · Usage Terms
    · Disclaimer