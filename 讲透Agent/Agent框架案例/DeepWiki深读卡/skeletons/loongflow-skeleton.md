# Skeleton: loongflow（50 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 24KB | 6 | ~20 | 2 |
| 2 | Getting Started | L573 | 16KB | 4 | ~8 | 2 |
| 3 | Installation & Setup | L1051 | 15KB | 3 | ~8 | 5 |
| 4 | Quick Start - General Agent | L1566 | 15KB | 2 | ~5 | 4 |
| 5 | Quick Start - Math Agent | L2049 | 12KB | 5 | ~3 | 4 |
| 6 | Quick Start - ML Agent | L2442 | 18KB | 3 | ~8 | 4 |
| 7 | Core Framework | L3048 | 28KB | 9 | ~19 | 4 |
| 8 | PES Paradigm (Plan-Execute-Summary) | L3852 | 21KB | 3 | ~14 | 5 |
| 9 | PESAgent Architecture | L4415 | 26KB | 9 | ~4 | 2 |
| 10 | ReActAgent Architecture | L5161 | 17KB | 6 | ~10 | 2 |
| 11 | Evolutionary Memory System | L5688 | 25KB | 11 | ~10 | 4 |
| 12 | LLM Integration | L6445 | 27KB | 9 | ~11 | 4 |
| 13 | BasePESRunner & Configuration | L7245 | 24KB | 7 | ~5 | 2 |
| 14 | General Agent | L8068 | 26KB | 9 | ~7 | 5 |
| 15 | General Agent Overview | L8777 | 16KB | 6 | ~6 | 3 |
| 16 | Planner Component | L9141 | 22KB | 7 | ~15 | 4 |
| 17 | Executor Component | L9844 | 14KB | 4 | ~10 | 2 |
| 18 | Evaluator Component | L10278 | 19KB | 4 | ~3 | 1 |
| 19 | Skills & Solution Packs | L10825 | 19KB | 7 | ~10 | 3 |
| 20 | Configuration & Running | L11354 | 17KB | 8 | ~12 | 7 |
| 21 | Math Agent | L11940 | 15KB | 3 | ~10 | 2 |
| 22 | Math Agent Overview | L12390 | 14KB | 3 | ~12 | 2 |
| 23 | Configuration Guide | L12827 | 23KB | 5 | ~26 | 4 |
| 24 | Task Structure & Files | L13568 | 14KB | 5 | ~4 | 2 |
| 25 | Running Math Tasks | L13974 | 19KB | 3 | ~9 | 2 |
| 26 | Examples & Results | L14681 | 21KB | 9 | ~8 | 4 |
| 27 | ML Agent | L15304 | 31KB | 4 | ~11 | 2 |
| 28 | ML Agent Overview | L16039 | 22KB | 3 | ~10 | 2 |
| 29 | Configuration Guide | L16566 | 25KB | 5 | ~24 | 4 |
| 30 | Running ML Tasks | L17320 | 18KB | 6 | ~17 | 2 |
| 31 | MLE-Bench Integration | L17894 | 18KB | 5 | ~15 | 4 |
| 32 | Examples & Results | L18497 | 18KB | 3 | ~15 | 2 |
| 33 | Building Custom Agents | L19022 | 15KB | 6 | ~6 | 4 |
| 34 | Custom ReAct Agents | L19526 | 29KB | 2 | ~5 | 3 |
| 35 | Custom PES Components | L20573 | 24KB | 7 | ~6 | 3 |
| 36 | Tool Development | L21358 | 19KB | 3 | ~5 | 1 |
| 37 | Custom Evaluators | L22065 | 18KB | 6 | ~4 | 1 |
| 38 | Visualization & Monitoring | L22621 | 15KB | 3 | ~1 | 8 |
| 39 | Visualization Server | L23082 | 19KB | 4 | ~7 | 3 |
| 40 | Checkpoints & Resumption | L23643 | 13KB | 3 | ~5 | 2 |
| 41 | Logging & Debugging | L24044 | 21KB | 3 | ~8 | 4 |
| 42 | Contributing to LoongFlow | L24789 | 19KB | 3 | ~29 | 2 |
| 43 | Development Guide | L25244 | 18KB | 5 | ~8 | 3 |
| 44 | Issue Reporting | L25752 | 15KB | 3 | ~10 | 2 |
| 45 | Pull Requests | L26229 | 18KB | 6 | ~13 | 2 |
| 46 | Reference | L26892 | 14KB | 3 | ~13 | 3 |
| 47 | Project Structure | L27326 | 25KB | 9 | ~24 | 3 |
| 48 | Configuration Reference | L28061 | 18KB | 4 | ~25 | 2 |
| 49 | Shell Script Reference | L28678 | 20KB | 5 | ~9 | 4 |
| 50 | API Reference | L29414 | 24KB | 5 | ~10 | 5 |


## · Overview  (L6)
  源文件: README.md, agents/ml_agent/README.md
  What is LoongFlow?
  The PES Paradigm
  Framework Architecture Overview
  PESAgent and Worker System
  Three Specialized Agent Types
  Execution Infrastructure
  Key Framework Components
    · Core Classes
    · Tool System
    · Utilities and Support
  Evolutionary Memory System
  LLM Integration
  Performance and Results
    · Mathematical Optimization (Tao's & AlphaEvolve Sets)
    · Machine Learning (MLE-bench Kaggle Competitions)
  Next Steps

## · Getting Started  (L573)
  源文件: README.md, agents/ml_agent/README.md
  Overview
  Prerequisites
  Installation Flow
  LLM Configuration
    · Supported Providers
    · Configuration Methods
  Agent Type Selection
    · General-Agent
    · Math-Agent
    · ML-Agent
  Task Execution Flow
  Running Your First Task
    · Quick Start Sequence
  Execution Modes
  Understanding Task Structure
    · Required Files
  Output and Workspace
  Next Steps

## · Installation & Setup  (L1051)
  源文件: README.md, agents/ml_agent/README.md, pyproject.toml, src/loongflow/agentsdk/models/formatter/litellm_formatter.py, uv.lock
  Prerequisites
  Installation Overview
  Base Installation
    · Method 1: Using uv (Recommended for Math/General Agents)
    · Method 2: Using conda/mamba (Required for ML Agent)
  Agent-Specific Environment Setup
    · ML Agent Environment Initialization
    · Math Agent Environment Setup
    · General Agent Environment Setup
  Environment Structure and Key Files
  Environment Activation and Management
    · Activation Commands
    · Conda/Mamba Initialization
  LLM Configuration
    · Configuration Structure
    · Supported Providers
    · Recommended Models
  Verification Steps
    · 1. Import Core Framework
    · 2. Verify Script Executability
    · 3. Verify ML Environment (if installed)
    · 4. Check MLE-bench Installation (if needed)
  Troubleshooting
    · Common Installation Issues
    · Environment Detection Issues
  Next Steps

## · Quick Start - General Agent  (L1566)
  源文件: README.md, agents/ml_agent/README.md, run_general.sh, run_math.sh
  Overview of General Agent Examples
  Task Directory Structure
  Running Your First Task
    · Step 1: Configure LLM Credentials
    · Step 2: Execute the Task
    · Step 3: Understanding the Execution Flow
  Execution Sequence
  Task Configuration
  Monitoring Progress
    · Real-time Logs
    · Workspace Inspection
  Stopping a Running Task
  Understanding Results
    · Solution Pack Structure
    · Evaluation Scores
  Next Steps
  Command Reference

## · Quick Start - Math Agent  (L2049)
  源文件: README.md, agents/ml_agent/README.md, run_general.sh, run_math.sh
  Prerequisites
  Task File Structure
  Step 1: Configure LLM Settings
  Step 2: Install Task Dependencies
  Step 3: Run the Task
    · Foreground Execution
    · Background Execution
  Step 4: Monitor Progress
    · Log File Monitoring
    · Workspace Structure
  Step 5: Stop the Task
  Understanding the Execution Flow
  Expected Output
  Next Steps

## · Quick Start - ML Agent  (L2442)
  源文件: README.md, agents/ml_agent/README.md, run_ml.sh, run_mlebench.sh
  Prerequisites
  ML Agent Execution Paths
  Quick Start: Custom ML Task
    · Step 1: Initialize Environment
    · Step 2: Configure LLM Credentials
    · Step 3: Run the Task
    · Step 4: Monitor Progress
    · Step 5: Stop the Task
  Quick Start: MLE-Bench Competition
    · Step 1: Initialize MLE-Bench Environment
    · Step 2: Prepare Competition Data
    · Step 3: Configure LLM (First Run Only)
    · Step 4: Run the Competition
    · Step 5: Monitor and Stop
  Understanding Command Line Arguments
  Task Directory Structure
  Evolution Output Structure
  Common Tasks
    · Resume from Checkpoint
    · Pass Additional Arguments
    · Clean Previous Runs
  Troubleshooting
    · Environment Not Found
    · PID File Already Exists
    · Competition Data Not Found
    · GPU Not Detected
  Next Steps

## · Core Framework  (L3048)
  源文件: README.md, agents/ml_agent/README.md, src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py
  Overview
  Framework Architecture
    · High-Level Component Organization
    · Directory Structure
  Agent Architectures
    · Architecture Comparison
    · PESAgent Execution Flow
    · ReActAgent Execution Flow
  Worker Registration and Component Model
    · Worker Registration Pattern
    · Worker Lifecycle in Evolution Cycle
  Context and Configuration
    · Context Object
    · EvolveChainConfig
  BasePESRunner Template
    · BasePESRunner Abstract Methods
    · Configuration Loading and Merging
  Checkpoint System
    · Checkpoint Naming Convention
  Concurrency and Asynchronous Execution
    · Concurrency Model
    · Async Execution Patterns
  Signal Handling and Graceful Shutdown
  Error Handling and Validation
    · Configuration Validation
    · Evolution Cycle Error Handling
  Extension Points
  Framework Dependencies
  Relationship to Application Agents

## · PES Paradigm (Plan-Execute-Summary)  (L3852)
  源文件: README.md, agents/general_agent/README.md, agents/general_agent/README_zh.md, agents/ml_agent/README.md, src/loongflow/framework/claude_code/general_prompt.py
  Conceptual Overview
    · The Core Insight
    · From Evolution to Reasoning
  The Three Phases
    · Architectural Diagram
    · Phase 1: Plan
    · Phase 2: Execute
    · Phase 3: Summary
  Phase Communication and Data Flow
    · Message Flow Diagram
    · Context Object
    · Message Objects
  Prompt Engineering Strategy
    · Universal Prompts
    · Prompt Parameter System
    · Required Output Structures
  Situation Analysis
  Strategy  
  Action Steps
  Expected Deliverables
  Success Criteria
  Assessment
  What Was Done
  What Worked
  What Didn't Work
  Insights
  Recommendations
  Evaluation Strategy
    · Two Evaluation Modes
  Implementation Structure
    · Code Entity Mapping
    · Prompt Formatting Example
    · Worker Registration Pattern
  PES vs Traditional Approaches
    · Comparison Table
    · Key Differentiators
    · When to Use PES
  Summary

## · PESAgent Architecture  (L4415)
  源文件: src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py
  Overview
  Class Structure and Initialization
    · PESAgent Class Hierarchy
    · Constructor Parameters
    · State Management Variables
    · Checkpoint Path Parsing
  Worker Registration System
    · Registration Interface
    · Worker Lifecycle
  Evolution Cycle Execution
    · Single Cycle Flow
    · Context Object Creation
    · Token Tracking
  Concurrency Architecture
    · Atomic Task Spawning
    · Three-Lock Architecture
    · Concurrency Control Flow
  Checkpoint and Resumption System
    · Checkpoint Triggering Logic
    · Checkpoint Naming Convention
    · Resumption Process
  Main Execution Loop
    · Initialization and Early Exit
    · Main Loop Architecture
    · Stop Conditions
  Lifecycle Management
    · Interruption Handling
    · Task Cleanup
    · Finalization
  Integration with BasePESRunner
    · Runner Responsibilities
    · Signal Handling
  Key Design Patterns
    · Producer-Consumer with Work Stealing
    · Lock Segregation for Scalability
    · Two-Level Iteration Tracking
  Summary

## · ReActAgent Architecture  (L5161)
  源文件: README.md, agents/ml_agent/README.md
  Purpose and Scope
  ReAct Framework Overview
  Core Components
    · ReActAgent Class
    · Toolkit System
    · ReActAgent Creation and Configuration
  Execution Architecture
  Step-by-Step Execution Model
  Integration with LLM Layer
  ReActAgent vs PESAgent Comparison
  Usage in LoongFlow Codebase
    · Internal Tool-Based Workers
    · Standalone Tool-Based Agents
  Configuration and Customization
    · Agent Configuration Parameters
    · System Prompt Structure
    · Toolkit Customization
  Message Protocol and Data Structures
    · Message Element Types
  Summary

## · Evolutionary Memory System  (L5688)
  源文件: README.md, agents/ml_agent/README.md, src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py
  Purpose and Scope
  Overview: Hybrid Memory Architecture
  Multi-Island Architecture
    · Island Structure
    · Configuration Parameters
    · Island Operations
  MAP-Elites System
    · Behavioral Grid Structure
    · Behavioral Dimensions
    · Elite Selection and Storage
    · Retrieval During Planning
  Adaptive Boltzmann Selection
    · Temperature-Based Selection
    · Selection Probability Formula
    · Temperature Adaptation Schedule
    · Adaptive Temperature Update
  Global Evolution Tree
    · Tree Structure and Lineage
    · Tree Node Information
    · Retrieval Strategies
    · Long-Range Context Retrieval
  Memory Integration with PES Cycle
    · Plan Phase: Memory Retrieval
    · Execute Phase: Tracking Metadata
    · Summary Phase: Memory Updates
  Storage and Persistence
    · Directory Structure
    · Checkpoint Contents and Memory Status
    · Resumption from Checkpoint
  Memory System Configuration
  Performance Characteristics
    · Memory vs. Simple Fitness-Based Selection
  Summary

## · LLM Integration  (L6445)
  源文件: pyproject.toml, src/loongflow/agentsdk/models/formatter/litellm_formatter.py, src/loongflow/framework/claude_code/claude_code_agent.py, uv.lock
  Purpose and Scope
  Architecture Overview
  LiteLLMFormatter: The Core Adapter
    · Key Responsibilities
  Message Conversion Flow
    · Element Collection Logic
  Message Element Types
    · ContentElement
    · ToolCallElement
    · ToolOutputElement
    · ThinkElement
  Request Formatting
    · Request Parameters
    · Example Flow
  Response Parsing
    · Response Types
    · Parsing Logic
  Tool Arguments Parsing
    · Safe JSON Parsing Strategy
  Provider Support
    · Supported Providers
    · Provider Detection Logic
  Special Model Handling
    · DeepSeek-Reasoner
  Configuration
    · task_config.yaml LLM Configuration
    · Model Name Formats
    · Environment Variables
  Usage Examples
    · Basic Request Flow
    · Tool Call Handling
  Integration with ClaudeCodeAgent
    · ClaudeCodeAgent LLM Configuration
    · Integration Points in Agent Architecture
  Dependencies

## · BasePESRunner & Configuration  (L7245)
  源文件: src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py
  Overview
  Architecture Diagram
  Configuration System Architecture
  CLI Argument Parsing
    · Standard Arguments
    · Custom Arguments
  Configuration Loading and Merging
    · YAML Loading
    · Configuration Merging Strategy
    · Custom Configuration Merging
    · Configuration Validation
  Logging Setup
    · Logging Features
  Abstract Methods for Subclassing
    · Required Implementations
    · Optional Overrides
  Agent Initialization and Execution
    · Initialization Sequence
    · Worker Registration
    · Signal Handling
    · Startup Banner
  Entry Point
  Implementation Example Pattern
  Relationship to PESAgent

## · General Agent  (L8068)
  源文件: README.md, agents/general_agent/README.md, agents/general_agent/README_zh.md, agents/ml_agent/README.md, src/loongflow/framework/claude_code/general_prompt.py
  Purpose and Capabilities
  When to Use General Agent
  Example Progression
  High-Level Architecture
  Solution Pack Concept
  Core Components
    · GeneralPlanAgent
    · GeneralExecuteAgent
    · Tool Conversion System
  Skills System
    · Skill Loading Process
  Data Flow Through PES Cycle
  Configuration
  Integration with PES Framework
  Summary

## · General Agent Overview  (L8777)
  源文件: agents/general_agent/README.md, agents/general_agent/README_zh.md, src/loongflow/framework/claude_code/general_prompt.py
  Purpose and Scope
  Architecture Overview
  Key Components
    · GeneralPlanAgent
    · GeneralExecuteAgent
    · GeneralEvaluator
  Solution Pack Protocol
    · Directory Structure
    · Manifest File (index.json)
    · Solution Pack Context Loading
  Skills System
    · Loading Skills
    · Skill Information Formatting
  PES Workflow in General Agent
  Integration with ClaudeCodeAgent
    · ClaudeCodeAgent Configuration
    · Database Tools for Planner
    · System Prompts
  Workspace Management
    · Directory Structure
  ExecutionContext Data Structure
  Message Flow

## · Planner Component  (L9141)
  源文件: agents/general_agent/README.md, agents/general_agent/README_zh.md, agents/general_agent/executor.py, src/loongflow/framework/claude_code/general_prompt.py
  Purpose and Scope
  Architecture Overview
    · GeneralPlanAgent Class Structure
    · Key Components
  Database Tool Integration
    · Available Database Tools
    · Tool Descriptions
  Solution Pack Processing
    · Solution Pack Loading Workflow
    · _process_parent_solution Method
    · Solution Pack Metadata Structure
  ClaudeCodeAgent Integration
    · Agent Initialization Flow
    · Configuration Parameters
    · Model Validation
  Planning Workflow
    · Complete Planning Data Flow
    · Execution Steps
  Output Artifacts
    · Artifact Structure
    · best_plan.md
    · parent_info.json
    · meta.json
    · Return Message
  Configuration
    · ClaudeAgentConfig Schema
    · LLM Configuration Requirements
  Error Handling
    · Validation Errors
    · Skill Loading Errors
    · Plan File Recovery
  Integration with PES Framework
    · Worker Interface Implementation
    · Context Usage
    · Workspace Integration
  Logging and Monitoring
    · Log Levels
    · Structured Logging

## · Executor Component  (L9844)
  源文件: agents/general_agent/executor.py, src/loongflow/framework/claude_code/claude_code_agent.py
  Overview
  Architecture
    · Class Structure
    · Execution Context
  Execution Workflow
    · Complete Execution Flow
    · Detailed Workflow Steps
  ClaudeCodeAgent Integration
    · Agent Instantiation and Execution
    · Prompt Construction
    · Agent Configuration
  Manifest Generation
  Evaluation Integration
    · Evaluation Workflow
    · Evaluation Data Structure
  Message Interface
    · Input Message Structure
    · Output Message Structure
  Configuration
    · ClaudeAgentConfig Requirements
    · Model Validation
    · Optional Configuration
  Error Handling
  Integration with PES Framework
    · Worker Registration
    · Context Usage

## · Evaluator Component  (L10278)
  源文件: agents/general_agent/evaluator.py
  Overview
  Evaluation Architecture
  AI Agent Evaluation Mode
    · Workflow
  Custom Tool Evaluation Mode
    · User Evaluation Script Interface
    · Tool-Based Evaluation Flow
    · Two-Stage Agent Involvment
  Subprocess Isolation and Timeout Control
    · Subprocess Execution Architecture
    · Process Lifecycle
  EvaluationResult Structure
    · Score Interpretation
    · Status Mapping
  Configuration
    · Configuration Fields
    · Model Restrictions
  Workspace Organization
  Integration with PES Cycle
    · Message Protocol
  Interrupt Handling
  Factory Function
  Error Handling and Recovery
    · Framework-Level Errors
    · Subprocess Errors
    · Timeout Errors

## · Skills & Solution Packs  (L10825)
  源文件: agents/general_agent/README.md, agents/general_agent/README_zh.md, src/loongflow/framework/claude_code/general_prompt.py
  Overview
  Skills System
    · What are Skills?
    · Skill Structure
    · Loading Mechanism
    · Skill Formatting for Prompts
    · Usage in GeneralExecuteAgent
  Solution Packs System
    · What are Solution Packs?
    · Manifest Structure
    · Directory Operations
    · Key Utility Functions
    · Copy-on-Write Pattern
  Integration with General Agent
    · Executor Workflow
    · Agent Prompt Context
    · ClaudeCodeAgent Execution
  Utility Functions Reference
    · Skill Management Functions
    · Solution Pack Functions
    · Tool Conversion Functions
  Error Handling
    · Common Exceptions
  Best Practices
    · Skills
    · Solution Packs
    · Integration

## · Configuration & Running  (L11354)
  源文件: agents/general_agent/README.md, agents/general_agent/README_zh.md, agents/general_agent/examples/03_bug_hunter/task_config.yaml, agents/general_agent/examples/04_circle_packing/task_config.yaml, run_general.sh, run_math.sh, src/loongflow/framework/claude_code/general_prompt.py
  Task Directory Structure
    · Required Files
  Configuration File Structure
    · Core Configuration Sections
    · LLM Configuration Requirements
    · Agent-Specific Settings
  Running General Agent Tasks
    · Basic Usage Syntax
    · Execution Flow
    · Path Resolution
  Command-Line Options
    · Script-Level Options
    · Python Script Options
    · Command Construction
  Process Management
    · Background Execution
    · Stopping Background Tasks
    · Process Hierarchy Discovery
  Logging and Monitoring
    · Log File Locations
    · Monitoring Background Tasks
  Example Usage Scenarios
    · Scenario 1: Quick Foreground Test
    · Scenario 2: Long-Running Background Execution
    · Scenario 3: Custom Configuration
  Integration with PES Framework
  Troubleshooting
    · Common Issues
    · Debug Steps

## · Math Agent  (L11940)
  源文件: README.md, agents/ml_agent/README.md
  Purpose and Scope
  Architecture Overview
  Execution Workflow
  Unique Features for Mathematical Problems
    · Initial Solution Seeding
    · Numerical Evaluation
    · Evolution-Friendly Configuration
  Performance Highlights
    · Terence Tao's Challenge Set
    · Key Success Factors
  Quick Start Example
  Task Configuration at a Glance
  File Structure Reference
  Comparison with Other Agents
  Next Steps

## · Math Agent Overview  (L12390)
  源文件: README.md, agents/ml_agent/README.md
  Purpose and Scope
  Capabilities and Characteristics
  Architecture Overview
    · Component Stack
  PES Workflow for Math Problems
    · Phase-Specific Behaviors
  Task Structure Requirements
  Performance Benchmarks
    · Terence Tao & AlphaEvolve Challenge Set
  Comparison with Other Agents
  Execution Model
    · Command-Line Interface
    · Workspace Output
  Evolution Database Integration
  Summary

## · Configuration Guide  (L12827)
  源文件: README.md, agents/general_agent/examples/03_bug_hunter/task_config.yaml, agents/general_agent/examples/04_circle_packing/task_config.yaml, agents/ml_agent/README.md
  Purpose and Scope
  Configuration File Structure
  Global Configuration
    · workspace_path
    · llm_config
  Component Configuration
    · Planners Configuration
    · Executors Configuration
    · Summarizers Configuration
  Evolution Configuration
    · Task Definition
    · Component Selection
    · Iteration Control Parameters
    · Evaluator Settings
    · Database Settings
  LLM Provider Configuration
    · Supported Providers
    · Provider-Specific Configuration
  Configuration Examples
    · Minimal Configuration
    · Production Configuration
    · Multi-Island Configuration
  Configuration Reference
    · Complete Field Reference
  Environment Variable Overrides
  Validation and Defaults

## · Task Structure & Files  (L13568)
  源文件: run_general.sh, run_math.sh
  Task Directory Structure
  File Validation in run_math.sh
  Required Files
    · task_config.yaml
    · eval_program.py
    · initial_program.py
    · description.md (Optional)
  File Interaction Flow
  File Location Resolution
  Common Patterns and Best Practices
    · Evaluator Design Patterns
    · Initial Program Guidelines
    · File Organization

## · Running Math Tasks  (L13974)
  源文件: run_general.sh, run_math.sh
  Prerequisites
  Execution Workflow Overview
  Basic Task Execution
    · Starting a Task
    · Command Line Arguments
    · Example: Complete Startup Sequence
  Execution Modes
    · Foreground Mode
    · Background Mode
  Monitoring Task Execution
    · Real-Time Log Monitoring
    · Process Status Check
    · Visualization Server
  Output Directory Structure
    · Key Output Files
  Checkpoint System
    · Understanding Checkpoints
    · Automatic Checkpoint Saving
  Resuming from Interruptions
    · Automatic Resumption
    · Manual Checkpoint Selection
    · Checkpoint Resume Flow
  Stopping Tasks
    · Graceful Shutdown
    · Forceful Termination
    · Foreground Mode Interruption
  Advanced Execution Patterns
    · Direct Python Execution
    · Environment Variable Configuration
    · Multiple Concurrent Tasks
    · Debugging Failed Evaluations
  Execution Lifecycle Summary
  Troubleshooting Execution Issues
    · Task Won't Start
    · Process Hangs on Startup
    · Cannot Stop Task
    · Checkpoint Not Loading

## · Examples & Results  (L14681)
  源文件: README.md, agents/general_agent/examples/03_bug_hunter/task_config.yaml, agents/general_agent/examples/04_circle_packing/task_config.yaml, agents/ml_agent/README.md
  Purpose and Scope
  Example Problem Catalog
    · Problem Categories and Results
    · Problem Comparison Table
  Evaluator Architecture
    · Evaluator Execution Flow
    · Evaluator Result Contract
  Evaluator Components
    · Core Evaluation Function
    · Timeout Protection
    · Validation Logic
  Example: Heilbronn Convex Regions Evaluator
    · Problem Interface
    · Validation Pipeline
    · Key Validation Functions
    · Result Structure
  Example: Hexagon Packing Evaluator
    · Problem Interface
    · Geometric Validation Functions
    · Validation Logic Flow
    · Score Computation
  Writing Custom Evaluators
    · 1. Define the Problem Interface
    · 2. Implement Core Functions
    · 3. Structure the Evaluation Logic
    · 4. Constants and Configuration
    · 5. Test Your Evaluator
  Evaluator Integration with PES

## · ML Agent  (L15304)
  源文件: README.md, agents/ml_agent/README.md
  MLE-Bench Performance
  System Architecture
  PES Component Implementation
    · Worker Configuration
    · Evaluation Program Interface
  Entry Points and Execution
    · Command Reference
    · Execution Flow
    · Process Management
  Directory Structure
    · File Roles
  Task Configuration Structure
    · Configuration Schema
    · Key Parameters
  Integration with LoongFlow Core
  Comparison with Other Agents
  Next Steps

## · ML Agent Overview  (L16039)
  源文件: README.md, agents/ml_agent/README.md
  Purpose and Scope
  Architecture Overview
    · ML Agent PES Cycle
  Core Components
    · ML Planner Worker
    · ML Executor Worker (EvoCoder)
    · ML Summary Worker
    · ML Evaluator
  Task Data Structure
  Workspace and Output Structure
  ML Agent Data Flow
  Capabilities and Autonomous Features
    · Data Understanding and Preprocessing
    · Feature Engineering
    · Model Selection and Training
    · Iterative Improvement
  Performance and Results
    · MLE-Bench Medal Distribution
    · Competition Domains
    · Example Gold Medal Competitions
  Comparison with Other Agents
  Component Integration Diagram
  Next Steps

## · Configuration Guide  (L16566)
  源文件: README.md, agents/general_agent/examples/03_bug_hunter/task_config.yaml, agents/general_agent/examples/04_circle_packing/task_config.yaml, agents/ml_agent/README.md
  Purpose and Scope
  Configuration Architecture
  Configuration File Structure
    · Complete task_config.yaml Template
  LLM Configuration (llm_config)
    · Parameter Reference
    · Provider-Specific Model Naming
    · Configuration Examples
  Component Configuration
    · Planner Configuration (ml_planner)
    · Executor Configuration (ml_executor)
    · Summarizer Configuration (ml_summary)
  Evolution Configuration (evolve)
    · Core Parameters
    · Evaluator Configuration
    · Database Configuration
  Task File Structure
    · Directory Layout
    · File Descriptions
  Evaluation Program Specification
    · Required Interface
    · Implementation Example
    · Return Value Specification
  Advanced Configuration Patterns
    · Adjusting for Task Complexity
    · Resource-Constrained Environments
    · Multi-GPU Configurations
  Configuration Validation
    · Component Name Mismatches
    · Invalid Parameter Ranges
    · Missing Required Files
  Configuration Best Practices
    · LLM Selection Guidelines
    · Timeout Tuning
    · Memory and Diversity Trade-offs

## · Running ML Tasks  (L17320)
  源文件: run_ml.sh, run_mlebench.sh
  Script Comparison
  Prerequisites
  Task Directory Structure
  Environment Initialization
    · The `init` Command
    · Environment Files
  Running ML Tasks
    · The `run` Command
    · Execution Flow
    · Task File Verification
    · Python Command Construction
    · Environment Variables
  Monitoring Running Tasks
    · Log Files
    · Process Status
    · Output Directory Structure
  Stopping Running Tasks
    · The `stop` Command
    · Process Tree Management
    · Global Cleanup
  Complete Workflow Example
  Command Reference Table
  Shell Script Function Reference
  Troubleshooting
    · Common Issues
    · Debug Tips

## · MLE-Bench Integration  (L17894)
  源文件: README.md, agents/ml_agent/README.md, run_ml.sh, run_mlebench.sh
  Overview
    · Key Components
  MLE-Bench Workflow
  Environment Initialization
    · GPU Detection and Environment Selection
    · MLE-Bench Library Installation
  Competition Data Structure
    · Directory Layout
    · Critical File Paths
  Competition Preparation
    · Data Download Process
  Execution Model
    · Command Construction
    · Background vs Foreground Execution
    · Debug Mode
    · Environment Configuration
  Grading System
    · Checkpoint-Based Submission Locator
    · Grading Fallback Strategy
    · Submission File Path Extraction
  Process Management
    · PID Tracking and Cleanup
    · Global Cleanup
  Integration with ML Agent Pipeline
    · Configuration Template
    · Evaluator Integration
    · Data Path Mapping
  Differences from General ML Tasks
    · Initialization
    · Data Preparation
    · Execution
    · Post-Execution
  Command Reference
    · Full Command Syntax
    · Example Workflow
  Environment Variables
    · Execution Context
    · Conda Detection

## · Examples & Results  (L18497)
  源文件: README.md, agents/ml_agent/README.md
  Overall MLE-Bench Performance
  Results by Difficulty Level
    · Simple Competitions (10 Total)
    · Medium Competitions (20 Total)
    · Hard Competitions (18 Total)
  Competition Execution Flow
  Example Competition Deep-Dive: stanford-covid-vaccine
    · Competition Overview
    · Directory Structure
    · Task Configuration
    · Evolution Process Visualization
  Output Structure Analysis
    · Iteration Directory Layout
    · Key File Contents
  Analysis of Parent Solution (Iteration 18, Score: 0.79)
  Proposed Improvements
  Expected Outcome
  Success Factors
  Failures & Learnings
  Reusable Insights
  Evaluation Pipeline Architecture
    · Score Normalization Example
  Performance Analysis Across Domains
    · Domain Breakdown
    · Medal Thresholds
  Reproducibility and Access

## · Building Custom Agents  (L19022)
  源文件: README.md, agents/ml_agent/README.md, src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py
  Purpose and Scope
  Agent Architecture Overview
    · ReActAgent vs PESAgent Architecture
  Customization Decision Framework
  Component Structure and Interfaces
    · ReActAgent Component Hierarchy
    · PESAgent Component Hierarchy
  Development Workflow
    · Environment and Module Structure
    · Custom Agent Development Pattern
  Key Design Principles
    · 1. Separation of Framework and Domain Logic
    · 2. Async-First Architecture
    · 3. Type Safety and Validation
    · 4. Path Handling
  Component Lifecycle and Interfaces
    · ReActAgent Component Lifecycle
    · PESAgent Component Lifecycle
  Configuration Integration
    · ReActAgent Configuration
    · PESAgent Configuration
  Testing Custom Components
    · Unit Testing Pattern
  Safety Considerations
    · Code Execution Sandboxing
  Next Steps

## · Custom ReAct Agents  (L19526)
  源文件: README.md, agents/ml_agent/README.md, src/loongflow/framework/claude_code/claude_code_agent.py
  ReActAgent Overview
    · ReActAgent vs PESAgent
    · When to Use ReActAgent
  Creating ReActAgent Instances
    · Basic Creation Pattern
    · ReActAgent Configuration
  Building Custom Toolkits
    · Toolkit Registration Pattern
    · Example: TODO List Toolkit
    · Toolkit Organization by Domain
  Integration with ClaudeCodeAgent
    · ClaudeCodeAgent Tool Architecture
    · ClaudeCodeAgent Initialization with Custom Tools
    · Tool List Configuration
  Custom Tool Development
    · Tool Function Requirements
    · Custom Tool Implementation Pattern
    · Example: File Statistics Tool
    · Example: Database Query Tool
  Tool Registration and Management
    · Adding Custom Tools
    · Removing Custom Tools
    · Listing and Inspecting Tools
    · Tool Name Validation
  Advanced Usage Patterns
    · Multi-Domain Agent with Toolkit Composition
    · Conditional Tool Loading
    · Tool Permission Modes
    · Custom Tool with Error Handling
  Best Practices
    · 1. Tool Granularity
    · 2. Parameter Validation
    · 3. Informative Tool Descriptions
    · 4. Error Reporting
    · 5. Async Best Practices
    · 6. Tool Testing
  Complete Example: Data Analysis Agent

## · Custom PES Components  (L20573)
  源文件: agents/general_agent/executor.py, src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py
  Worker Interface Overview
  Worker Base Class
  Worker Registration System
  Implementing a Planner Worker
  Implementing an Executor Worker
  Implementing a Summary Worker
  Context and Message Objects
  Complete Integration Example
  Worker Configuration Patterns
  Best Practices

## · Tool Development  (L21358)
  源文件: src/loongflow/framework/claude_code/claude_code_agent.py
  Tool Architecture
    · ClaudeCodeAgent Tool Integration Flow
  Tool Structure
    · Required Components
    · Tool Function Requirements
    · Tool Content Block Format
  Creating Custom Tools
    · Method 1: Constructor Initialization
    · Method 2: Dynamic Tool Addition
  Tool Registration and Validation
    · Tool Registration Process
    · Validation Rules
  Tool Decorator Application
    · The @tool Decorator
    · MCP Server Creation
    · Tool Name Resolution
  Tool Lifecycle Management
    · Tool Management Methods
    · Removing Tools
    · Listing and Inspecting Tools
  Practical Examples
    · Example 1: Simple Calculator Tool
    · Example 2: File Search Tool
    · Example 3: API Client Tool
  Best Practices
    · Naming Conventions
    · Error Handling
    · Async Patterns
    · Parameter Validation
    · Detailed Descriptions

## · Custom Evaluators  (L22065)
  源文件: agents/general_agent/evaluator.py
  Evaluator Contract
    · Standard Return Structure
  Required Fields
    · Core Fields
    · Status Values
  Evaluation Workflow
  Implementation Patterns
    · Timeout Protection
    · Validation Stages
    · Error Handling Strategy
  Integration with Tool System
    · Tool Integration Flow
    · Tool Builder Implementation
  Example: Heilbronn Problem Evaluator
    · Problem Definition
    · Evaluator Structure
    · Key Implementation Details
  Multi-Run Evaluation Pattern
    · MoE Load Balancing Example
  Best Practices
    · 1. Subprocess Isolation for Untrusted Code
    · 2. Tolerance-Based Comparisons
    · 3. Staged Validation with Early Exit
    · 4. Comprehensive Error Reporting
    · 5. Normalized Scoring
    · 6. Path Validation
  Testing Evaluators

## · Visualization & Monitoring  (L22621)
  源文件: agents/general_agent/README.md, agents/general_agent/README_zh.md, src/loongflow/framework/claude_code/general_prompt.py, src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py, Visualization Server, Checkpoints & Resumption, Logging & Debugging
  Monitoring Architecture
    · Monitoring Data Flow
  Workspace Organization
  Real-Time Progress Tracking
    · Token and Cost Tracking
    · Score Evolution Tracking
  Monitoring Components Overview
    · 1. Visualization Server
    · 2. Checkpoint System
    · 3. Logging Infrastructure
  Trace ID System
  Integration with PES Cycle
  Command-Line Monitoring
    · Background Execution
    · Stopping Tasks
  Configuration Reference
  Next Steps

## · Visualization Server  (L23082)
  源文件: agents/general_agent/README.md, agents/general_agent/README_zh.md, src/loongflow/framework/claude_code/general_prompt.py
  Purpose and Scope
  Architecture Overview
    · System Components
  Launching the Visualizer
    · Command-Line Interface
    · Typical Usage Patterns
  Dashboard Interface
    · UI Component Layout
  Data Format and Directory Structure
    · Workspace Organization
    · Evaluation Data Format
    · File Tree Data Structure
  REST API Endpoints
    · Data Retrieval Flow
  Features in Detail
    · Score Evolution Chart
    · Markdown Rendering
    · Hierarchical File Tree
    · Code Viewer
  Troubleshooting
    · Common Issues and Solutions
  Integration with Evolution Workflow
    · Typical Monitoring Workflow
  Advanced Usage
    · Multi-Workspace Monitoring
    · Analyzing Completed Runs
  Technical Implementation Notes
    · Backend Technology Stack
    · Frontend Technology Stack
    · Performance Considerations

## · Checkpoints & Resumption  (L23643)
  源文件: src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py
  Overview
  Checkpoint Naming Convention
    · Distinction Between Iteration ID and Completion Count
  When Checkpoints Are Created
    · 1. Regular Interval Checkpoints
    · 2. Target Score Reached
    · 3. Max Iterations Reached
  What Is Saved in a Checkpoint
  Resuming from a Checkpoint
    · Command-Line Usage
    · Resumption Process
  State Restoration Details
    · Completion Count Restoration
    · Iteration ID Restoration
    · Database State Loading
  Configuration Options
    · Checkpoint Interval
    · Output Path
  Error Handling
    · Invalid Checkpoint Format
    · Checkpoint Save Failures
  Concurrency Considerations
  Example Checkpoint Lifecycle

## · Logging & Debugging  (L24044)
  源文件: run_general.sh, run_math.sh, src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py
  Purpose and Scope
  Log Configuration System
    · Configuration Sources
  Logging Architecture
    · Component Hierarchy
  Log Output Destinations
    · Console Logging
    · File Logging
    · Background Execution Logs
  Log Message Format and Structure
    · Standard Log Format
    · Trace ID System
  Log Levels and Usage
    · Level Hierarchy
    · Level-Specific Patterns
  Token Usage Tracking
    · Token Accounting Flow
    · Token Logging Format
    · Token Data Collection
  Debugging Techniques
    · Common Debugging Scenarios
  Interpreting Evolution Logs
    · Typical Evolution Cycle Log Sequence
    · Key Log Patterns
  Advanced Debugging
    · Trace ID Correlation Across Workspace
    · Multi-Worker Concurrency Debugging
    · Database State Inspection
  Log File Management
    · Disk Space Monitoring
    · Backup Count Management
  Summary

## · Contributing to LoongFlow  (L24789)
  源文件: .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/feature_request.md
  Overview
  Quick Navigation
  Repository Structure for Contributors
    · Diagram: Repository Structure and Contribution Areas
  Contribution Areas by Component
  Overview
  Quick Navigation
  Repository Structure for Contributors
    · Diagram: Repository Structure and Contribution Areas
  Contribution Areas by Component
  Contribution Workflow Overview
    · Diagram: GitHub Issue Template Usage
  Key Contribution Guidelines
    · Development Environment Setup
    · Code Organization Principles
  Types of Contributions
    · Bug Reports
    · Feature Requests
    · Code Contributions
    · Documentation Contributions
  Getting Help
  Contribution Best Practices
    · Before Submitting
    · During Submission
    · After Submission
  Summary

## · Development Guide  (L25244)
  源文件: pyproject.toml, src/loongflow/agentsdk/models/formatter/litellm_formatter.py, uv.lock
  Prerequisites
  Setting Up Development Environment
    · Installation Methods
    · Dependency Overview
    · PyPI Mirror Configuration
  Project Structure
    · Directory Layout
    · Package Organization
    · Build System Configuration
  Running Tests
    · Test Framework Configuration
    · Running Tests
    · Test Dependencies
  Code Organization Patterns
    · LLM Integration Architecture
    · Message Element Types
    · Provider Detection Pattern
    · JSON Parsing Resilience
  Development Workflow Best Practices
    · Code Style Guidelines
    · Testing Async Code
    · Debugging LLM Interactions
    · Working with Fake Filesystems
  Understanding Core Abstractions
    · The Formatter Interface
    · Message Conversion Pipeline
  Next Steps

## · Issue Reporting  (L25752)
  源文件: .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/feature_request.md
  Overview
  Issue Template Structure
  Bug Reports
    · Required Information
    · Environment Information
    · Critical Information for Different Components
  Feature Requests
    · Template Structure
    · Effective Feature Proposals
    · LoongFlow-Specific Considerations
  Issue Reporting Workflow
  Best Practices
    · Writing Effective Bug Reports
    · Feature Request Guidelines
  Use Case
  Proposed Solution
  Impact
  Common Issue Categories
    · Bug Report Categories
    · Feature Request Categories
  Template Fields Reference
    · Bug Report Fields
    · Feature Request Fields
  Issue Labels and Organization
  Next Steps After Reporting

## · Pull Requests  (L26229)
  源文件: .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/feature_request.md
  PR Workflow Overview
    · Pull Request Lifecycle
  Creating a Pull Request
    · Branch Naming Conventions
    · Commit Message Format
    · Pull Request Description Template
  Description
  Type of Change
  Related Issues
  Changes Made
  Testing
  Documentation
  Checklist
  Coding Standards
    · Python Style Guidelines
    · Configuration Standards
  Testing Requirements
    · Test Organization
    · Required Test Coverage
    · Running Tests
  Documentation Requirements
    · Code Documentation
    · Wiki Documentation
    · Skills Documentation
  Review Process
    · Code Review Workflow
    · What Reviewers Look For
    · Review Component Mapping
  Responding to Feedback
    · Addressing Review Comments
    · Comment Response Examples
    · When to Request Re-Review
  Merge Criteria
    · Requirements for Merging
    · Breaking Changes
    · Post-Merge
  Summary

## · Reference  (L26892)
  源文件: pyproject.toml, src/loongflow/agentsdk/models/formatter/litellm_formatter.py, uv.lock
  Reference Documentation Overview
  Repository Structure Overview
  Core Framework Code Entities
  Configuration Files Quick Reference
  Shell Script Command Reference
  Python API Entry Points
  File Organization by Concern
  Navigating the Reference Documentation
  Version and Compatibility Information

## · Project Structure  (L27326)
  源文件: pyproject.toml, src/loongflow/agentsdk/models/formatter/litellm_formatter.py, uv.lock
  Repository Overview
    · Root Directory Layout
  Directory Structure Diagram
    · Top-Level Organization
  Core Framework Structure (`src/loongflow/`)
    · Framework Module Hierarchy
    · Core Framework Modules
  Pre-built Agents Structure (`agents/`)
    · Agent Types and Organization
    · Agent Module Overview
    · Common Agent Directory Structure
  GitHub Infrastructure (`.github/`)
    · GitHub Directory Structure
    · GitHub Infrastructure Files
  CLI Scripts
    · CLI Script Overview
    · Script Functionality Table
    · Script Operations Detail
  Documentation Files
    · Documentation File Mapping
    · Documentation Files
  Version Control Configuration (`.gitignore`)
    · Excluded Categories
  Data Flow and Output Structure
    · Runtime Output Organization
    · Output Directory Structure by Agent Type
    · Output Components
  Package Initialization Structure
    · Initialization File Locations
  Module Import Patterns
    · Example Import Patterns
  Configuration File Locations
    · Configuration File Mapping
    · Configuration Files by Purpose
    · Task Configuration Structure
  Summary: Architectural Principles

## · Configuration Reference  (L28061)
  源文件: agents/general_agent/examples/03_bug_hunter/task_config.yaml, agents/general_agent/examples/04_circle_packing/task_config.yaml
  Configuration File Structure
  Global Configuration Parameters
    · `workspace_path`
  LLM Configuration (`llm_config`)
    · LLM Parameters Reference
    · Model Naming Convention
  Component Configurations
    · Configuration Structure
    · Planner Configuration
    · Executor Configuration
    · Summarizer Configuration
  Evolution Configuration (`evolve`)
    · Core Evolution Parameters
    · Evaluator Configuration (`evolve.evaluator`)
    · Database Configuration (`evolve.database`)
  Complete Configuration Examples
    · Math Agent Configuration
    · ML Agent Configuration
  Configuration Loading and Validation
  Configuration Hierarchy
  Environment Variables
  Configuration Best Practices
    · Task Complexity Guidelines
    · LLM Selection Guidelines
    · Timeout Configuration

## · Shell Script Reference  (L28678)
  源文件: run_general.sh, run_math.sh, run_ml.sh, run_mlebench.sh
  Overview
  Common Architecture
    · Shell Script Execution Flow
    · Shared Functions
  run_math.sh
    · Overview
    · Commands
    · Directory Structure
    · Execution Pattern
    · Usage Examples
  run_ml.sh
    · Overview
    · Commands
    · Command Details
    · Directory Structure
    · Environment Variables
    · Usage Examples
  run_mlebench.sh
    · Overview
    · Commands
    · Command Details
    · Directory Structure
    · File Path Resolution
    · Usage Examples
  Environment Management
    · Conda Environment Detection
    · GPU vs CPU Detection
    · Environment Activation
  Process Management
    · PID File Lifecycle
    · Background vs Foreground Execution
    · Graceful Shutdown Process
    · Global Cleanup
  Common Patterns
    · Command Array Construction
    · Error Handling
    · Path Resolution
  Troubleshooting
    · Common Issues
    · Debug Logging
    · Checking Environment Status

## · API Reference  (L29414)
  源文件: agents/general_agent/evaluator.py, agents/general_agent/executor.py, src/loongflow/framework/claude_code/claude_code_agent.py, src/loongflow/framework/pes/base_runner.py, src/loongflow/framework/pes/pes_agent.py
  Agent Architectures
    · PESAgent
    · ReActAgent
  Component Interfaces
    · Worker (IWorker)
    · Finalizer
  Message & Communication
    · Message
    · ContentElement, ToolCallElement, ToolOutputElement
  LLM Integration
    · LiteLLMFormatter
    · CompletionRequest
    · CompletionResponse
    · BaseLLMModel
  Tools
    · BaseTool
    · FunctionTool
    · Toolkit
  Context & Memory
    · AgentContext
    · Memory
  Class Hierarchy Diagram
  Usage Examples
    · Creating a Custom Tool
    · Initializing a ReActAgent
  Configuration Integration