# Skeleton: ai-scientist（28 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 8KB | 2 | ~2 | 3 |
| 2 | System Architecture | L212 | 10KB | 5 | ~4 | 6 |
| 3 | Installation and Setup | L498 | 8KB | 3 | ~2 | 3 |
| 4 | Core Components | L774 | 5KB | 2 | ~0 | 6 |
| 5 | Launch Scientist | L900 | 5KB | 2 | ~1 | 3 |
| 6 | LLM Integration | L1039 | 6KB | 3 | ~5 | 1 |
| 7 | Idea Generation | L1189 | 9KB | 3 | ~7 | 3 |
| 8 | Experiment Execution | L1428 | 11KB | 6 | ~4 | 5 |
| 9 | Paper Writing | L1732 | 10KB | 5 | ~5 | 5 |
| 10 | Paper Review | L1993 | 14KB | 6 | ~12 | 4 |
| 11 | Templates and Data | L2340 | 5KB | 1 | ~2 | 5 |
| 12 | Template System | L2455 | 8KB | 2 | ~2 | 5 |
| 13 | Data Preparation Scripts | L2596 | 9KB | 3 | ~1 | 4 |
| 14 | Available Templates | L2824 | 7KB | 3 | ~5 | 4 |
| 15 | Review System Training | L3021 | 5KB | 2 | ~1 | 4 |
| 16 | Few-Shot Learning Approach | L3136 | 6KB | 2 | ~3 | 3 |
| 17 | Training Examples | L3285 | 8KB | 3 | ~10 | 9 |
| 18 | ICLR Benchmark Evaluation | L3475 | 6KB | 2 | ~4 | 2 |
| 19 | Example Papers and Results | L3619 | 7KB | 3 | ~6 | 4 |
| 20 | Generated Paper Catalog | L3758 | 8KB | 2 | ~2 | 6 |
| 21 | Experiment Run Structure | L3926 | 7KB | 2 | ~3 | 8 |
| 22 | AI Scientist Self-Review Analysis | L4057 | 6KB | 2 | ~4 | 3 |
| 23 | Advanced Usage | L4189 | 5KB | 3 | ~0 | 2 |
| 24 | Creating Custom Templates | L4324 | 8KB | 2 | ~4 | 5 |
| 25 | Advanced LLM Configuration | L4471 | 8KB | 2 | ~3 | 2 |
| 26 | Parallel Experimentation | L4675 | 6KB | 2 | ~3 | 2 |
| 27 | Contributing | L4853 | 6KB | 3 | ~2 | 3 |
| 28 | Glossary | L5016 | 7KB | 2 | ~2 | 11 |


## · Overview  (L6)
  源文件: LICENSE, README.md, ai_scientist/__init__.py
  Purpose and Scope
  System Architecture
  Scientific Workflow
  Key Components
    · Launch Scientist
    · LLM Integration
    · Template System
  Conclusion

## · System Architecture  (L212)
  源文件: README.md, ai_scientist/__init__.py, ai_scientist/generate_ideas.py, ai_scientist/perform_experiments.py, ai_scientist/perform_review.py, ai_scientist/perform_writeup.py
  Overview
  Pipeline Orchestration
  LLM Integration Architecture
  Template System Architecture
  Data Flow and State Management
  Reliability and Error Handling

## · Installation and Setup  (L498)
  源文件: .gitignore, LICENSE, README.md
  System Requirements
    · Hardware Requirements
    · Operating System Support
    · Technical Environment Overview
  Basic Installation
    · Environment Setup
    · LaTeX Installation
    · Python Dependencies
  API Key Configuration
    · OpenAI API
    · Anthropic API
    · Additional Providers
  Template Setup
    · NanoGPT Template
    · 2D Diffusion Template
    · Grokking Template
  Installation Verification
    · Basic Execution
    · Parallel Execution
    · Review System Verification
  Troubleshooting
    · Common Issues

## · Core Components  (L774)
  源文件: ai_scientist/__init__.py, ai_scientist/generate_ideas.py, ai_scientist/llm.py, ai_scientist/perform_experiments.py, ai_scientist/perform_review.py, ai_scientist/perform_writeup.py
  Pipeline Orchestration
    · High-Level System Flow
  2.1 Launch Scientist
  2.2 LLM Integration
  2.3 Idea Generation
  2.4 Experiment Execution
    · Experiment Execution Entity Mapping
  2.5 Paper Writing
  2.6 Paper Review

## · Launch Scientist  (L900)
  源文件: README.md, ai_scientist/generate_ideas.py, ai_scientist/perform_experiments.py
  System Overview
  Pipeline Execution Flow
  Core Components Detail
    · Idea Generation Orchestration
    · Experiment Execution Loop
    · Open-Ended Execution (Experimental)
  Parallel Execution Support
  Error Handling and Timeouts

## · LLM Integration  (L1039)
  源文件: ai_scientist/llm.py
  Supported LLM Providers and Models
  Core Architecture
  Key Functions
    · Client Initialization (`create_client`)
    · LLM Response Generation
    · Robustness and Parsing
  Data Flow: Natural Language to Code Entities
  Model-Specific Logic Table

## · Idea Generation  (L1189)
  源文件: ai_scientist/generate_ideas.py, example_papers/adaptive_dual_scale_denoising/ideas.json, example_papers/adaptive_dual_scale_denoising/seed_ideas.json
  Overview
    · Core Workflow
  Idea Generation Process
    · Primary Generation Function
    · Template Integration
    · Idea Refinement Loop
    · Idea JSON Schema
  Novelty Checking
    · Literature Search Integration
    · Supported Search Engines
  Advanced Features
    · Open-Ended Generation
    · Error Handling and Resilience
  Configuration and Usage
    · Command Line Interface
    · File Outputs

## · Experiment Execution  (L1428)
  源文件: ai_scientist/perform_experiments.py, example_papers/adaptive_dual_scale_denoising/experiment.py, example_papers/adaptive_dual_scale_denoising/run_0/final_info.json, example_papers/adaptive_dual_scale_denoising/run_1.py, example_papers/data_augmentation_grokking/experiment.py
  Purpose and Scope
  Experiment Execution Workflow
    · Overall Process Flow
    · Coder Agent Interaction
  Experiment Running Mechanism
    · Experiment Execution Details
    · Experiment State Management
  Code Entity Interaction
  Plotting and Visualization
    · Plotting Process
    · Plotting Configuration
  Configuration and Limits
    · System Limits
    · Error Handling Strategy
  Integration Points

## · Paper Writing  (L1732)
  源文件: ai_scientist/perform_writeup.py, example_papers/adaptive_dual_scale_denoising/latex/fancyhdr.sty, example_papers/adaptive_dual_scale_denoising/latex/iclr2024_conference.sty, example_papers/adaptive_dual_scale_denoising/latex/references.bib, example_papers/adaptive_dual_scale_denoising/latex/template.tex
  System Overview
  Paper Writing Workflow
  Core Components
    · LaTeX Generation and Compilation
    · Citation Management System
    · Section Writing Framework
  Error Detection and Validation
  Integration Points
    · Aider Framework Integration
    · LLM Provider Integration
  Configuration and Usage

## · Paper Review  (L1993)
  源文件: ai_scientist/fewshot_examples/132_automated_relational.json, ai_scientist/fewshot_examples/2_carpe_diem.json, ai_scientist/fewshot_examples/attention.json, ai_scientist/perform_review.py
  Overview
  Core Review Process Flow
  Key Components and Functions
    · Core Function Descriptions
  Few-Shot Learning Approach
  Ensemble Review and Meta-Review System
  Reflection and Iterative Refinement
  Review Structure and Output Format
    · Complete Review Field Specification
  System Prompts and Reviewer Behavior
  Paper Improvement Integration

## · Templates and Data  (L2340)
  源文件: data/enwik8/prepare.py, data/shakespeare_char/prepare.py, data/shakespeare_char/readme.md, data/text8/prepare.py, example_papers/adaptive_dual_scale_denoising/prompt.json
  Purpose and Scope
  3.1 Template System
    · Template Structure
  3.2 Data Preparation Scripts
    · Character-Level Modeling Pipeline
    · Key Datasets
  3.3 Available Templates
    · Core Templates
    · Community Templates
    · System Mapping: Natural Language to Code Entities

## · Template System  (L2455)
  源文件: example_papers/adaptive_dual_scale_denoising/experiment.py, example_papers/adaptive_dual_scale_denoising/plot.py, example_papers/adaptive_dual_scale_denoising/prompt.json, example_papers/adaptive_dual_scale_denoising/seed_ideas.json, example_papers/data_augmentation_grokking/prompt.json
  Overview
  Template Architecture and Data Flow
  Core Template Components
    · 1. Experimental Logic (`experiment.py`)
    · 2. Visualization (`plot.py`)
    · 3. Domain Context (`prompt.json`)
    · 4. Seed Ideas (`seed_ideas.json`)
    · 5. Paper Template (`latex/`)
  Mapping Code Entities to Research Workflow
  Execution and Data Flow
    · Result Extraction Implementation
  Available Templates

## · Data Preparation Scripts  (L2596)
  源文件: data/enwik8/prepare.py, data/shakespeare_char/prepare.py, data/shakespeare_char/readme.md, data/text8/prepare.py
  Overview
  Available Datasets
    · enwik8 Dataset
    · shakespeare_char Dataset
    · text8 Dataset
  Common Processing Pattern
    · Character Encoding
    · Output Files
  Integration with Templates
    · Usage in Experiments
  File Format Specifications
    · Binary Data Format
    · Metadata Format

## · Available Templates  (L2824)
  源文件: example_papers/adaptive_dual_scale_denoising/DatasaurusDozen.tsv, example_papers/adaptive_dual_scale_denoising/datasets.py, example_papers/adaptive_dual_scale_denoising/ema_pytorch.py, example_papers/adaptive_dual_scale_denoising/prompt.json
  Overview
  Template Architecture
    · Template Structure and Integration
    · Template File Structure
  Core Templates
    · NanoGPT Template
    · 2D Diffusion Template
    · Grokking Template
  Community-Contributed Templates
  Template Selection and Usage
    · Running Templates with AI Scientist
    · Template Execution Flow
  Creating Custom Templates

## · Review System Training  (L3021)
  源文件: ai_scientist/fewshot_examples/132_automated_relational.json, ai_scientist/fewshot_examples/2_carpe_diem.json, ai_scientist/fewshot_examples/attention.json, ai_scientist/perform_review.py
  Few-Shot Learning Approach
  Training Examples
    · Core Training Corpus
  Review Pipeline Architecture
    · Review Generation Logic
  ICLR Benchmark Evaluation
  Meta-Review and Ensemble Training
    · Meta-Review Workflow

## · Few-Shot Learning Approach  (L3136)
  源文件: ai_scientist/fewshot_examples/132_automated_relational.json, ai_scientist/fewshot_examples/2_carpe_diem.json, ai_scientist/perform_review.py
  Overview
    · Few-Shot Learning Architecture
  Review Schema and Instructions
    · Mandatory Fields
    · Prompting Strategy
  Few-Shot Example Loading
    · Training Data Integration
    · Text Extraction and Caching
  Ensemble Methods and Reflection
    · Execution Flow
    · Reflection Loops
  Configuration Parameters

## · Training Examples  (L3285)
  源文件: ai_scientist/fewshot_examples/132_automated_relational.json, ai_scientist/fewshot_examples/132_automated_relational.pdf, ai_scientist/fewshot_examples/132_automated_relational.txt, ai_scientist/fewshot_examples/2_carpe_diem.json, ai_scientist/fewshot_examples/2_carpe_diem.pdf, ai_scientist/fewshot_examples/2_carpe_diem.txt, ai_scientist/fewshot_examples/attention.json, ai_scientist/fewshot_examples/attention.pdf, ai_scientist/fewshot_examples/attention.txt
  Overview
  File Structure and Organization
  Review Data Structure
  Training Example Descriptions
    · 1. Automated Relational Meta-Learning (ARML)
    · 2. Carpe Diem (Recency Bias)
    · 3. Attention Is All You Need
  Integration with Review System
  Content Diversity and Coverage

## · ICLR Benchmark Evaluation  (L3475)
  源文件: ai_scientist/fewshot_examples/2_carpe_diem.json, ai_scientist/perform_review.py
  Overview of Evaluation Infrastructure
    · Key Components
  Data Flow and Architecture
    · Review Generation Pipeline
  Review Schema and Scoring
    · Quantitative Fields
    · Qualitative Fields
  Implementation Detail: `perform_review.py`
    · Ensemble and Prompting Strategy
  Comparative Model Analysis

## · Example Papers and Results  (L3619)
  源文件: example_papers/adaptive_dual_scale_denoising.pdf, example_papers/adaptive_dual_scale_denoising/adaptive_dual_scale_denoising.pdf, example_papers/data_augmentation_grokking.pdf, example_papers/data_augmentation_grokking/data_augmentation_grokking.pdf
  Purpose and Scope
  Generated Paper Catalog
    · Example Papers Overview
  Experiment Run Structure
    · Key Components of a Run
  AI Scientist Self-Review Analysis
    · Analysis Infrastructure Components
  Integration with AI Scientist Pipeline

## · Generated Paper Catalog  (L3758)
  源文件: example_papers/adaptive_dual_scale_denoising.pdf, example_papers/adaptive_dual_scale_denoising/ideas.json, example_papers/adaptive_dual_scale_denoising/notes.txt, example_papers/adaptive_dual_scale_denoising/review.txt, example_papers/data_augmentation_grokking.pdf, example_papers/data_augmentation_grokking/ideas.json
  Overview of Generated Research
    · Mapping Natural Language Ideas to Code Entities
  1. Adaptive Dual-Scale Denoising
  2. Data Augmentation Grokking
  3. Dual Expert Denoiser
  4. GAN Diffusion
  5. Grid-Based Noise Adaptation
  6. Layerwise LR Grokking
  7. MDL Grokking Correlation
  8. Multi-Style Adapter
  9. RL LR Adaptation
  10. Weight Initialization Grokking
  Data Flow and Result Structure
    · Catalog Summary Table

## · Experiment Run Structure  (L3926)
  源文件: example_papers/adaptive_dual_scale_denoising/20240802_090035_adaptive_dual_scale_denoising_aider.txt, example_papers/adaptive_dual_scale_denoising/experiment.py, example_papers/adaptive_dual_scale_denoising/log.txt, example_papers/adaptive_dual_scale_denoising/notes.txt, example_papers/adaptive_dual_scale_denoising/plot.py, example_papers/adaptive_dual_scale_denoising/run_0/final_info.json, example_papers/adaptive_dual_scale_denoising/run_1.py, example_papers/adaptive_dual_scale_denoising/run_1/final_info.json
  Directory Overview
    · Key Components
  Iterative Experimentation Flow
    · Data Flow Diagram: Experiment Iteration
  The Role of Aider and Snapshots
    · Code Snapshotting Relationship
  Result Aggregation and Plotting
    · Result Structure (`final_info.json`)
  Summary of Execution Logs

## · AI Scientist Self-Review Analysis  (L4057)
  源文件: ai_scientist/perform_review.py, example_papers/adaptive_dual_scale_denoising/review.txt, example_papers/data_augmentation_grokking/review.txt
  Overview of Self-Review Infrastructure
    · Key Components
  Data Flow and Implementation
    · Review Process Diagram
  Review Schema and Scoring
    · Schema Fields
    · Example Review Output
  Multi-Model Comparison
  Implementation Details
    · Prompting Strategy
    · Review Ensemble
    · Parsing Logic

## · Advanced Usage  (L4189)
  源文件: README.md, ai_scientist/llm.py
  Advanced LLM Configuration
    · Multi-Provider Architecture
    · Configuration and Model Selection
  Creating Custom Templates
    · Template-to-Code Mapping
    · Template Component Requirements
  Parallel Experimentation
    · Parallel Execution Architecture
    · Resource Management
  Advanced Reviewer Configuration

## · Creating Custom Templates  (L4324)
  源文件: example_papers/adaptive_dual_scale_denoising/experiment.py, example_papers/adaptive_dual_scale_denoising/plot.py, example_papers/adaptive_dual_scale_denoising/prompt.json, example_papers/adaptive_dual_scale_denoising/seed_ideas.json, example_papers/data_augmentation_grokking/prompt.json
  Purpose and Scope
  Template Architecture Overview
    · Template Directory Structure
    · System-to-Code Mapping: Idea Generation
  Core Template Components
    · 1. experiment.py Requirements
    · 2. plot.py Requirements
    · 3. prompt.json Structure
    · 4. seed_ideas.json Format
    · System-to-Code Mapping: Experiment Execution
  Community Template Examples
  Creating a New Template: Step-by-Step

## · Advanced LLM Configuration  (L4471)
  源文件: README.md, ai_scientist/llm.py
  LLM Provider Architecture
    · Provider Routing System
    · Supported Model Matrix
  Authentication Configuration
    · Environment Variables Setup
  Request Processing Architecture
    · Single Response Flow
    · Batch Response Processing
  Model-Specific Configuration Details
    · OpenAI O1/O3 Models
    · DeepSeek Reasoner
    · Google Gemini
  Advanced Features
    · JSON Extraction
    · Retry and Backoff
    · Experimental: Open-Ended Scientist
  Custom Model Integration

## · Parallel Experimentation  (L4675)
  源文件: README.md, ai_scientist/perform_experiments.py
  Overview
  Usage and Configuration
    · Basic Parallel Execution
    · GPU Detection and Allocation
  Process Coordination
    · Independent Process Execution
    · Resource Isolation and Data Flow
  Containerization (Experimental)
  Performance Considerations
    · Hardware Requirements
    · Throughput and Limitations

## · Contributing  (L4853)
  源文件: .gitignore, LICENSE, README.md
  Licensing and The "AI Scientist" Clause
  Types of Contributions
    · Contribution Workflow
  Development Setup
    · Setup Commands
    · Codebase Organization
  Contributing New Templates
    · Required Template Components
    · Template Data Flow
  Pull Request Guidelines
    · Community Templates

## · Glossary  (L5016)
  源文件: README.md, ai_scientist/__init__.py, ai_scientist/fewshot_examples/132_automated_relational.json, ai_scientist/fewshot_examples/2_carpe_diem.json, ai_scientist/fewshot_examples/attention.json, ai_scientist/generate_ideas.py, ai_scientist/llm.py, ai_scientist/perform_experiments.py, ai_scientist/perform_review.py, ai_scientist/perform_writeup.py, example_papers/adaptive_dual_scale_denoising/seed_ideas.json
  Core System Concepts
    · Idea Generation & Novelty
    · Experimentation & Execution
    · Writeup & Review
  Natural Language to Code Mapping
    · Pipeline Orchestration Mapping
    · Data Flow & File Artifacts
  Technical Abbreviations & Jargon
  Key Class/Function Reference
    · `get_response_from_llm`
    · `generate_ideas`
    · `perform_experiments`
    · `generate_latex`