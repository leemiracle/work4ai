# Skeleton: adas（14 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 9KB | 5 | ~2 | 5 |
| 2 | Core Architecture | L274 | 14KB | 6 | ~2 | 3 |
| 3 | Evolutionary Search Algorithm | L677 | 12KB | 5 | ~4 | 3 |
| 4 | Dynamic Code Evaluation | L1069 | 11KB | 4 | ~2 | 3 |
| 5 | Problem Solvers | L1346 | 12KB | 8 | ~4 | 5 |
| 6 | ARC Solver | L1730 | 11KB | 8 | ~4 | 1 |
| 7 | Question Answering Solvers | L2093 | 9KB | 5 | ~6 | 2 |
| 8 | Math Problem Solvers | L2407 | 10KB | 6 | ~7 | 2 |
| 9 | Evaluation Systems | L2734 | 10KB | 9 | ~3 | 3 |
| 10 | GPQA and MMLU Evaluation | L3015 | 8KB | 4 | ~3 | 2 |
| 11 | Math Problem Evaluations | L3274 | 11KB | 5 | ~4 | 4 |
| 12 | Developer Guide | L3562 | 13KB | 7 | ~4 | 3 |
| 13 | LLM Integration | L3973 | 10KB | 8 | ~2 | 3 |
| 14 | Adding New Datasets | L4324 | 8KB | 5 | ~2 | 3 |


## · Overview  (L6)
  源文件: _arc/search.py, _drop/search.py, _gpqa/search.py, _mgsm/search.py, _mmlu/search.py
  System Architecture Overview
  Core Components
    · Key Classes and Functions
  Problem Domains
  Solution Generation Workflow
  Dynamic Code Execution
  OpenAI API Integration
  Summary

## · Core Architecture  (L274)
  源文件: _arc/search.py, _drop/search.py, _gpqa/search.py
  Purpose and Scope
  Key Components Overview
  Core Components in Detail
    · LLMAgentBase
    · AgentSystem
    · Info Structure
    · OpenAI Integration
  Search and Evaluation Process
  Dynamic Code Execution
  Natural Language to Code Transformation
  Common Utilities and Patterns
    · Error Handling and Rate Limiting
    · Parallel Processing
    · Confidence Calculation
  Component Reuse Across Problem Domains
  Summary

## · Evolutionary Search Algorithm  (L677)
  源文件: _arc/search.py, _gpqa/search.py, _mgsm/search.py
  Purpose and Scope
  Algorithm Overview
  Core Components
    · Search Function
    · Archive Structure
  Search Process Workflow
    · Initialization
    · Generation Loop
    · Solution Generation and Reflection
    · Error Handling and Debugging
    · Fitness Calculation
  Solution Evaluation
    · Dynamic Code Execution
    · Parallel Evaluation
  LLM Integration
    · API Interaction
  Implementation Across Problem Domains
  Integration with Support Classes
    · `LLMAgentBase` Class
    · `AgentSystem` Class
  Conclusion

## · Dynamic Code Evaluation  (L1069)
  源文件: _arc/search.py, _transfer_math/evaluate_gpqa.py, _transfer_math/evaluate_mmlu.py
  Purpose and Scope
  System Architecture
  Core Mechanism
    · Key Steps in the Process
    · Isolation and Function Extraction
  Dynamic Function Attachment
  Task-Specific Execution
    · ARC Problem Execution
    · Question-Answering Execution
  Parallel Execution
  Error Handling and Validation
    · Error Handling Process Table
  Fitness Calculation
  Integration with Evolutionary Search
  Best Practices for Solution Implementation
  Domain-Specific Adaptations
    · ARC Problems
    · Question Answering (GPQA, MMLU)
  Conclusion

## · Problem Solvers  (L1346)
  源文件: _arc/search.py, _drop/search.py, _gpqa/search.py, _mgsm/search.py, _mmlu/search.py
  Overview
  Problem Solver Architecture
    · Problem Solvers in Context
    · Common Components
  Search Workflow
  Dynamic Code Execution
  Domain-Specific Solvers
    · ARC Problem Solver
    · Question Answering Solvers
    · Math Problem Solvers
  Solution Generation
    · Reflexion and Debugging
  Parallel Evaluation
  Configuration and Usage

## · ARC Solver  (L1730)
  源文件: _arc/search.py
  Purpose and Scope
  System Architecture
  LLMAgentBase
  AgentSystem
  Evolutionary Search Process
  Dynamic Code Evaluation
  JSON Response Handling
  Data Structures
  Workflow Example
  Usage Example
  Integration with Evolutionary Systems

## · Question Answering Solvers  (L2093)
  源文件: _drop/search.py, _gpqa/search.py
  Purpose and Scope
  Architecture Overview
    · High-Level System Architecture
    · System Components and Data Flow
  DROP Solver
    · Implementation Details
    · Data Format and Evaluation
  GPQA Solver
    · Implementation Details
    · Data Format and Evaluation
  Common Implementation Patterns
    · LLM Interaction and Solution Generation
    · Dynamic Code Execution
    · Parallel Processing and Error Handling
  Technical Details
    · `LLMAgentBase` Class
    · Solution Archive Structure
    · Differences Between DROP and GPQA Solvers

## · Math Problem Solvers  (L2407)
  源文件: _mgsm/search.py, _mmlu/search.py
  Purpose and Scope
  Architecture Overview
    · Math Solver Architecture
  Shared Implementation
    · Core Classes
    · Search and Evaluation Workflow
  MGSM Solver
    · Key Features
    · Implementation Details
    · Evaluation Process
  MMLU Solver
    · Key Features
    · Implementation Details
    · Evaluation Process
  OpenAI Integration
    · API Interaction Flow
  Configuration Parameters
  Key Differences Between Solvers
  Usage Examples

## · Evaluation Systems  (L2734)
  源文件: _transfer_math/evaluate_gpqa.py, _transfer_math/evaluate_mmlu.py, _transfer_math/evaluation_Asdiv.py
  Purpose and Scope
  Core Evaluation Architecture
    · Evaluation Workflow
  Evaluation Components
    · Dynamic Code Execution
    · Parallel Processing
  Specific Evaluation Systems
    · GPQA Evaluation
    · MMLU Evaluation
    · Math Problem Evaluations
  Code Entity Mapping
  Implementation Details
    · Command-Line Configuration
    · Solution Archive Format
  Error Handling and Robustness

## · GPQA and MMLU Evaluation  (L3015)
  源文件: _transfer_math/evaluate_gpqa.py, _transfer_math/evaluate_mmlu.py
  Purpose and Scope
  Overview
  System Architecture
  Core Components
    · LLMAgentBase
    · AgentSystem
    · OpenAI API Utilities
  Evaluation Process
  Dynamic Code Evaluation
  Dataset-Specific Processing
    · GPQA Evaluation
    · MMLU Evaluation
  Answer Processing and Scoring
  Statistical Analysis
  Command-Line Interface
  Usage Example

## · Math Problem Evaluations  (L3274)
  源文件: _transfer_math/evaluation_Asdiv.py, _transfer_math/evaluation_DROP.py, _transfer_math/evaluation_SVAMP.py, _transfer_math/evaluation_gsm8k.py
  Purpose and Scope
  Common Evaluation Architecture
    · Evaluation System Architecture
    · Evaluation Workflow
  Dynamic Code Evaluation
    · Code Injection Process
  Dataset-Specific Evaluations
    · ASDiv Evaluation
    · DROP Evaluation
    · SVAMP Evaluation
    · GSM8k Evaluation
  Statistical Evaluation Methods
    · Bootstrap Confidence Interval Process
  Parallel Execution Architecture
  Configuration and Usage
  Solution Format

## · Developer Guide  (L3562)
  源文件: _arc/search.py, _transfer_math/evaluation_DROP.py, _transfer_math/evaluation_gsm8k.py
  Development Environment Setup
    · Prerequisites
    · Installation
  Core Components for Developers
    · Development Architecture Overview
    · Key Classes and Functions
  Working with the OpenAI API
    · Making API Calls
    · API Integration Best Practices
  Dynamic Code Execution Pattern
    · The Execution Flow
    · Implementation Example
  Adding New Problem Domains
    · Step-by-Step Guide
  Working with Evolutionary Search
    · Search Algorithm Components
  Evaluation Systems Integration
    · Evaluation Implementation Pattern
  Testing and Debugging
    · Testing Strategies
    · Debugging Tips
  Performance Optimization
    · Parallel Execution
    · API Cost Management
  Common Development Tasks
    · Adding a New Agent Type
    · Implementing a New Evaluation Metric
    · Creating New Problem Templates
  Conclusion

## · LLM Integration  (L3973)
  源文件: _arc/search.py, _drop/search.py, _gpqa/search.py
  Purpose and Scope
  OpenAI API Integration Overview
  Core Request Functions
    · Basic API Requests with `get_json_response_from_gpt`
    · Multi-Message Conversations with `get_json_response_from_gpt_reflect`
  Error Handling and Resilience
    · Rate Limit Backoff
    · JSON Validation and Error Recovery
    · Context Length Management
  The LLMAgentBase Class
    · Prompt Generation
    · Query Execution
  Integration with the Search Algorithm
  Prompt Engineering Patterns
    · Format Instructions
    · Role Descriptions
    · Task-Specific Instructions
  Best Practices for LLM Integration
  Configuration Options

## · Adding New Datasets  (L4324)
  源文件: _arc/search.py, _transfer_math/evaluation_Asdiv.py, _transfer_math/evaluation_gsm8k.py
  Dataset Integration Architecture
  Required Components for New Datasets
    · 1. Dataset Utilities
    · 2. Search Implementation
    · 3. Evaluation Script
  Implementation Guide
    · Step 1: Create Dataset Utilities
    · Step 2: Implement Search Functionality
    · Step 3: Create Evaluation Script
  Key Considerations
  Integration with Core Components
  Example Integration Workflow