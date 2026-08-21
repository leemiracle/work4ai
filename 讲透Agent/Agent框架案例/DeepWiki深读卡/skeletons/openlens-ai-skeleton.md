# Skeleton: openlens-ai（28 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 9KB | 2 | ~2 | 2 |
| 2 | System Architecture | L259 | 12KB | 4 | ~7 | 2 |
| 3 | Getting Started | L587 | 10KB | 6 | ~12 | 2 |
| 4 | Configuration | L916 | 9KB | 3 | ~10 | 4 |
| 5 | Installation | L1200 | 8KB | 3 | ~6 | 3 |
| 6 | Multi-Agent System | L1499 | 10KB | 3 | ~2 | 1 |
| 7 | Supervisor Agent | L1742 | 7KB | 2 | ~5 | 1 |
| 8 | Literature Reviewer Agent | L1944 | 8KB | 4 | ~4 | 1 |
| 9 | Data Analyzer Agent | L2175 | 9KB | 5 | ~8 | 1 |
| 10 | Coder Agent | L2436 | 10KB | 6 | ~4 | 1 |
| 11 | LaTeX Writer Agent | L2729 | 7KB | 4 | ~6 | 1 |
| 12 | LLM Router Infrastructure | L2934 | 9KB | 3 | ~3 | 2 |
| 13 | Model Configuration | L3182 | 8KB | 3 | ~8 | 1 |
| 14 | vLLM Deployment | L3393 | 7KB | 3 | ~8 | 2 |
| 15 | Performance Testing | L3627 | 6KB | 3 | ~7 | 3 |
| 16 | Evaluation Framework | L3850 | 9KB | 4 | ~5 | 2 |
| 17 | Evaluation Datasets | L4100 | 10KB | 5 | ~4 | 2 |
| 18 | Quality Assessment | L4373 | 7KB | 2 | ~5 | 1 |
| 19 | Parallel Testing | L4610 | 7KB | 3 | ~6 | 2 |
| 20 | Experiment Tracking | L4865 | 8KB | 6 | ~4 | 2 |
| 21 | Development Environment | L5106 | 7KB | 2 | ~3 | 2 |
| 22 | OpenHands Integration | L5274 | 7KB | 4 | ~4 | 3 |
| 23 | Editor Configuration | L5484 | 6KB | 2 | ~2 | 2 |
| 24 | GitHub Configuration | L5691 | 6KB | 2 | ~2 | 2 |
| 25 | Reference | L5878 | 9KB | 3 | ~11 | 2 |
| 26 | Configuration Reference | L6177 | 9KB | 4 | ~16 | 2 |
| 27 | Repository Structure | L6469 | 13KB | 10 | ~8 | 2 |
| 28 | License and Legal | L6797 | 7KB | 4 | ~4 | 1 |


## · Overview  (L6)
  源文件: README.md, modules.md
  Purpose and Scope
  System Architecture
    · Core System Components
    · Agent Workflow Orchestration
  Core Components
    · Multi-Agent Coordination
    · LangGraph Workflow Engine
    · Tool Infrastructure
  External Service Integration
    · Language Model APIs
    · Code Execution Environment
    · Academic Database Access
  User Interfaces
    · Command Line Interface
    · Web Interface
  Configuration Management

## · System Architecture  (L259)
  源文件: README.md, modules.md
  Architecture Overview
    · Core System Components
  Multi-Agent Workflow Architecture
    · Agent Interaction Flow
  Agent Specialization and Responsibilities
  State Management and Orchestration
    · State Schema Definition
  Tool Integration Architecture
    · Tool Ecosystem
  Workflow Execution Model
    · Execution Flow Control
  External Service Dependencies
    · Service Integration Points

## · Getting Started  (L587)
  源文件: .env.example, README.md
  Prerequisites
    · Required API Keys
  Installation Workflow
    · Docker Environment Setup
    · Python Environment Setup
  Configuration Setup
    · Environment File Creation
    · Core Configuration Parameters
    · Advanced Configuration Parameters
  First Execution
    · Command Line Interface
    · Web Interface
  Verification Steps
    · System Health Check
    · Common Configuration Issues
  Next Steps

## · Configuration  (L916)
  源文件: .env.example, .setup/env.sh, .streamlit/config.toml, langgraph.json
  Configuration Overview
    · Configuration Architecture
  Environment Variables
    · AI Model Configuration
    · Search and Reranking Services
    · System Parameters
    · Runtime Environment
  Optional Services Configuration
    · Monitoring and Tracing
    · Email Notifications
  Alternative Configuration Files
    · DeepSeek Integration
    · Streamlit SSL Configuration
    · LangGraph Runtime Configuration
  Configuration Validation

## · Installation  (L1200)
  源文件: README.md, modules/OpenHands/.devcontainer/devcontainer.json, modules/OpenHands/.devcontainer/setup.sh
  Prerequisites
    · Required API Services
  Docker Environment Setup
    · Docker Installation Verification
    · OpenLens AI Docker Image Setup
  Python Environment Setup
    · Repository Clone
    · Virtual Environment Creation
    · Dependency Installation
    · Optional: Graphviz Installation
  Environment Configuration
    · Configuration File Setup
    · Core Configuration Parameters
    · Required Environment Variables
    · Optional Configuration Parameters
  Installation Verification
    · Basic System Check
    · Docker Container Verification
    · Environment Configuration Test
    · OpenHands Integration Test
  Running the Application
    · Command Line Interface
    · Interactive Web Interface

## · Multi-Agent System  (L1499)
  源文件: modules.md
  Architecture Overview
    · Agent Communication and State Management
  Agent Roles and Responsibilities
  Workflow Orchestration
    · Agent Execution Flow
    · State Management and Routing
  Agent Integration Points
    · Tool Integration Architecture
  Prompt Template System
    · Supervisor Agent Prompts
    · Literature Reviewer Prompts  
    · Data Analyzer Prompts
    · Coder Agent Prompts
    · LaTeX Writer Prompts
  Error Handling and Workflow Control

## · Supervisor Agent  (L1742)
  源文件: modules.md
  Core Responsibilities
  Planning and Coordination Architecture
    · Supervisor Agent Workflow Components
    · Agent Coordination Flow
  Implementation Architecture
    · Tool Integration
    · Prompt Template System
  Workflow Process
    · Plan Generation Workflow
    · State Management Integration
  Integration with Multi-Agent System
    · Agent Coordination Responsibilities
    · Workflow Orchestration

## · Literature Reviewer Agent  (L1944)
  源文件: modules.md
  Purpose and Scope
  Agent Architecture Overview
    · Two-Phase Operation Model
    · Core Components
  Literature Search Tools Architecture
    · Search Tool Ecosystem
  Literature Search Phase
    · Search Strategy Implementation
  Report Writing Phase
    · Report Generation Workflow
    · Report Structure and Content
  Workflow Implementation
    · Complete Agent Workflow
    · State Management
  Integration with Multi-Agent System
    · Shared State Communication
    · Agent Coordination
  Tool Dependencies and External Services
    · External Service Integration
    · Tool Error Handling

## · Data Analyzer Agent  (L2175)
  源文件: modules.md
  Purpose and Scope
  Agent Overview
    · Core Responsibilities
  Architecture and Implementation
    · Data Analyzer Agent Architecture
    · Code Entity Mapping
  Workflow and Process Flow
    · Data Analysis Workflow
    · Processing Phases
  Tools and Integration
    · OpenHands Integration
    · Tool Configuration
    · Prompt System
  State Management and Coordination
    · Shared State Components
    · Inter-Agent Communication

## · Coder Agent  (L2436)
  源文件: modules.md
  Agent Architecture
    · Core Components
  Code Generation Workflow
    · Generation Process Flow
    · Prompt Template Integration
  Execution Environment Integration
    · OpenHands Tool Integration
  Quality Assessment and Validation
    · Validation Architecture
    · Quality Metrics
  Inter-Agent Communication
    · State Management
    · File-Based Communication
  Router Decision Logic
    · Routing States

## · LaTeX Writer Agent  (L2729)
  源文件: modules.md
  Agent Architecture and Components
    · Core Components
  Paper Generation Workflow
    · Sequential Section Generation
    · Quality Assessment Pipeline
  Integration with Multi-Agent System
    · Input Dependencies
    · Shared State Integration
  Technical Implementation Details
    · Visual-Language Model Integration
    · Workflow State Management
    · Output Integration

## · LLM Router Infrastructure  (L2934)
  源文件: llm_router/create_yaml.py, llm_router/proxy_update.sh
  System Architecture
    · Router Infrastructure Overview
  YAML Configuration Generation
    · Configuration Generation Workflow
    · Model Name Mapping
  API Key Management and Load Balancing
    · Balance Validation Process
    · Load Balancing Configuration
  Proxy Server Operations
    · Proxy Startup and Configuration
    · Model Entry Structure
  Integration with OpenLens AI
    · Client Integration Points
    · Environment Configuration

## · Model Configuration  (L3182)
  源文件: llm_router/create_yaml.py
  Purpose and Scope
  Configuration Generation Workflow
  API Key Management
    · Balance Checking
  Model Name Mapping
  Generated Configuration Structure
    · Router Settings
    · LiteLLM Settings
  Command Line Interface
    · Required Arguments
    · Optional Arguments
  Integration with Extra Models
  Error Handling and Validation

## · vLLM Deployment  (L3393)
  源文件: llm_router/deploy_model_vllm.py, llm_router/model_dl.py
  Overview
  vLLM Deployment Architecture
  Model Download and Storage
  vLLM Server Configuration
    · Core Configuration Parameters
    · Model-Specific Parser Configuration
  Multi-GPU Deployment
    · GPU Allocation Strategy
    · Tensor Parallelism Configuration
  Process Management
    · Process Lifecycle Management
    · Logging and Output Management
  Command Line Interface
    · Required Arguments
    · Optional Configuration
  Integration with LLM Router

## · Performance Testing  (L3627)
  源文件: llm_router/api_perf.py, llm_router/env_api_perf.sh, llm_router/local_api_perf.sh
  Overview
  Performance Testing Workflow
  Key Performance Metrics
    · Latency Measurements
    · Throughput Statistics
    · Concurrency Analysis
  Testing Scripts and Usage
    · Environment-Based Testing
    · Local API Testing
  API Performance Testing Function
    · Request Execution Process
  Analysis and Reporting
    · Statistical Output
    · Latency Distribution Visualization
  Command Line Interface

## · Evaluation Framework  (L3850)
  源文件: exp/eval/evaluate_experiment_quality.py, exp/eval/parallel_test.py
  Architecture Overview
  Evaluation Workflow
  Quality Assessment Dimensions
  Parallel Execution Infrastructure
  File Structure and Data Flow
  Integration with Core System

## · Evaluation Datasets  (L4100)
  源文件: exp/eval/openlens_eval_dataset.csv, exp/eval/openlens_eval_dataset_v2.csv
  Dataset Structure and Purpose
    · Dataset File Organization
  Question Categories and Difficulty Levels
    · Difficulty Classification
    · Question Type Analysis
  Dataset Evolution and Versions
    · Version Comparison
  Integration with Evaluation Framework
    · Evaluation Workflow Integration
  Medical Research Domain Coverage
    · Research Domain Matrix
    · Question Complexity Characteristics

## · Quality Assessment  (L4373)
  源文件: exp/eval/evaluate_experiment_quality.py
  Purpose and Scope
  Quality Evaluation Dimensions
    · Scoring Criteria
  Assessment Workflow
    · Quality Assessment Flow
    · File Processing Pipeline
  Implementation Details
    · LLM Client Configuration
    · Score Parsing System
    · Parallel Processing Architecture
  Evaluation Prompt Structure
    · Prompt Template
    · Content Truncation
  Output and Reporting
    · CSV Output Files
    · Result Structure
  Command Line Interface
    · Usage Pattern
    · Arguments

## · Parallel Testing  (L4610)
  源文件: exp/eval/parallel_test.py, exp/eval/run_parallel_tests.sh
  Purpose and Scope
  System Architecture
    · Parallel Execution Workflow
    · Core Components
  Test Execution Details
    · Individual Test Execution
    · Thread ID Generation
  Configuration and Parameters
    · Command Line Arguments
    · Task Generation Strategy
  Integration with Evaluation Framework
    · Shell Script Wrapper
    · Result Tracking
    · Resource Management

## · Experiment Tracking  (L4865)
  源文件: exp/eval/validate_experiment_progress.py, exp/exp.sh
  Purpose and Scope
  Experiment Progress Validation
    · Validation Architecture
    · Configuration File Processing
  Thread ID Management
    · Resume Handling System
    · Experiment Grouping
  Completion Detection
    · Node Call Stack Analysis
    · Progress Statistics
  Progress Reporting
    · Console Output Format
    · CSV Export System
  Command Line Usage
    · Script Execution
    · Parameter Configuration
    · Integration with Experiment Execution

## · Development Environment  (L5106)
  源文件: modules/OpenHands/.devcontainer/devcontainer.json, modules/OpenHands/.devcontainer/setup.sh
  Development Environment Overview
    · Development Environment Architecture
  OpenHands Integration Architecture
    · Container and Execution Flow
  VS Code Development Container Configuration
    · Container Specification
    · Post-Creation Setup Process
  Integration with Multi-Agent System
    · Agent Execution Flow

## · OpenHands Integration  (L5274)
  源文件: modules/OpenHands/.devcontainer/devcontainer.json, modules/OpenHands/.devcontainer/setup.sh, modules/OpenHands/.dockerignore
  Purpose and Scope
  OpenHands Runtime Architecture
    · Integration Overview
  Container Configuration
    · DevContainer Specification
    · Container Environment Variables
  Setup and Initialization
    · Post-Creation Setup Process
  Docker Build Configuration
    · Excluded Files and Directories
    · Critical Included Files
  Integration with Multi-Agent System
    · Agent-Container Communication

## · Editor Configuration  (L5484)
  源文件: modules/OpenHands/.editorconfig, modules/OpenHands/.gitattributes
  Purpose and Scope
  EditorConfig Settings
    · Line Ending Standardization
    · Whitespace Management
  Git Attributes Configuration
    · Language Detection Override
    · Line Ending Enforcement
    · Binary File Handling
  Configuration Flow Diagram
  Cross-Platform Consistency
    · Windows Container Compatibility
    · Git Workflow Consistency
  File Type Processing Flow

## · GitHub Configuration  (L5691)
  源文件: modules/OpenHands/.github/CODEOWNERS, modules/OpenHands/.github/ISSUE_TEMPLATE/bug_template.yml
  Purpose and Scope
  Code Ownership Configuration
    · CODEOWNERS File Structure
    · Ownership Mapping
  Issue Template Configuration
    · Bug Report Template
  GitHub Workflow Integration
  Configuration Management
    · File Locations
    · Maintenance Requirements

## · Reference  (L5878)
  源文件: .env.example, LICENSE
  Configuration Reference
    · Core Model Configuration
    · Search and Reranking Configuration
    · Context and Token Limits
    · Agent Execution Parameters
    · Optional Monitoring and Notifications
  Configuration to Code Entity Mapping
  Repository Structure Overview
  Key System Integration Points
  License Information
    · MIT License Summary
    · License Requirements
    · Disclaimer
  Version and Copyright Information

## · Configuration Reference  (L6177)
  源文件: .env.example, langgraph.json
  Environment Configuration Overview
    · Configuration Architecture
  Core Model Configuration
    · Language Models
    · Model API Configuration
  Reranking Service Configuration
  Search Service Configuration
  Operational Limits Configuration
    · Context Token Limits
    · Agent Execution Limits
    · Container Configuration
  Optional Service Configuration
    · LangSmith Tracing
    · Email Notifications
  LangGraph Configuration
    · LangGraph Parameters
  Configuration Validation
    · Required Configuration
    · Development Configuration
    · Production Configuration

## · Repository Structure  (L6469)
  源文件: .gitignore, google95d114587c90b3e8.html
  Directory Organization Overview
  Core Application Structure
    · Main Package: `curie/`
  Integration and Baseline Systems
    · OpenHands Integration: `baselines/openhands/`
  LLM Router Infrastructure
    · Model Management: `llm_router/`
  Evaluation and Experimentation
    · Experiment Directory: `exp/`
  External Dependencies and Modules
    · External Module Integration: `modules/`
  Configuration and Credentials
    · Environment Configuration
  Data and Output Directories
    · Working Directories
  Build and Development Artifacts
    · Excluded Development Files
  Special Files
    · Web and Verification Files

## · License and Legal  (L6797)
  源文件: LICENSE
  MIT License Overview
  License Terms and Permissions
    · Permitted Actions
    · Required Conditions
  Warranty and Liability Disclaimers
    · No Warranty Provision
    · Liability Limitations
  Third-Party Dependencies and Legal Compliance
    · License Compliance Guidelines
  Distribution and Modification Guidelines
    · For Users
    · For Contributors
    · For Redistributors
  Legal Contact and Questions