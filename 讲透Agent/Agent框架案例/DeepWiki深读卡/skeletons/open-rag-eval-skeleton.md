# Skeleton: open-rag-eval（18 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 8KB | 6 | ~2 | 3 |
| 2 | Getting Started | L366 | 8KB | 4 | ~0 | 4 |
| 3 | Installation | L735 | 5KB | 2 | ~5 | 4 |
| 4 | Configuration | L926 | 10KB | 5 | ~13 | 4 |
| 5 | Core Components | L1254 | 11KB | 4 | ~0 | 5 |
| 6 | Evaluation Pipeline | L1643 | 9KB | 6 | ~2 | 5 |
| 7 | Evaluators | L1914 | 8KB | 4 | ~2 | 3 |
| 8 | Connectors | L2139 | 8KB | 6 | ~0 | 5 |
| 9 | Vectara Connector | L2400 | 9KB | 3 | ~4 | 3 |
| 10 | CSV Connector | L2699 | 8KB | 4 | ~2 | 6 |
| 11 | LLM Judge Models | L2926 | 7KB | 2 | ~2 | 2 |
| 12 | Metrics | L3162 | 8KB | 5 | ~3 | 9 |
| 13 | UMBRELA and Citation Metrics | L3430 | 9KB | 5 | ~3 | 3 |
| 14 | AutoNugget Metric | L3712 | 11KB | 5 | ~2 | 3 |
| 15 | No Answer Metric | L4026 | 8KB | 3 | ~2 | 1 |
| 16 | Visualization | L4259 | 9KB | 4 | ~2 | 4 |
| 17 | Development | L4541 | 8KB | 4 | ~0 | 4 |
| 18 | Testing | L4853 | 12KB | 7 | ~0 | 6 |


## · Overview  (L6)
  源文件: README.md, img/project-logo.png, sample_prompt.txt
  Purpose and Scope
  System Architecture
  Evaluation Workflow
  Core Components
    · Evaluators
    · Connectors
    · Metrics
    · LLM Judge Models
  Data Structures
  Integration Options
    · Python Library
    · Command-line Tool
    · Web API
  Visualization

## · Getting Started  (L366)
  源文件: README.md, img/project-logo.png, requirements.txt, sample_prompt.txt
  Overview of the Process
  Prerequisites
  Installation
    · Option 1: Build from Source (Recommended for Following Examples)
    · Option 2: Install via pip (For Using in Your Own Pipeline)
  Basic Evaluation Workflow
  Using with the Vectara Connector
    · Step 1: Configure Evaluation Settings
    · Step 2: Prepare Queries
    · Step 3: Run Evaluation
    · Step 4: Visualize Results
  Using with Custom RAG Outputs
    · Step 1: Prepare RAG Results
    · Step 2: Configure Evaluation Settings
    · Step 3: Run Evaluation and Visualize
  Configuration Architecture
  Data Flow in Evaluation

## · Installation  (L735)
  源文件: README.md, img/project-logo.png, requirements.txt, sample_prompt.txt
  Prerequisites
    · Required API Keys
  Installation Methods
    · Method 1: Install from Source (Recommended for Development)
    · Method 2: Install from PyPI (Recommended for Integration)
  Dependencies
    · Installation Diagram
  Installation Verification
  System Integration
  Common Issues and Troubleshooting
    · Dependency Conflicts
    · API Key Configuration
  Next Steps

## · Configuration  (L926)
  源文件: README.md, eval_config.yaml, img/project-logo.png, sample_prompt.txt
  Overview
  Configuration File Structure
  Input and Output Configuration
  Evaluator Configuration
  Connector Configuration
    · Connector Types
    · Connector Options
    · Query Configuration
  Custom Prompt Templates
  Example Configuration Workflows
    · Using with Vectara Connector
    · Using with Pre-existing Results
  Environment Variables

## · Core Components  (L1254)
  源文件: README.md, img/project-logo.png, open_rag_eval/models/__init__.py, open_rag_eval/run_eval.py, sample_prompt.txt
  System Architecture Overview
    · System Architecture Diagram
  Key Components
    · Component Hierarchy Diagram
  Evaluators
    · Evaluator (Abstract Base Class)
    · TRECEvaluator
  Connectors
    · Connector (Abstract Base Class)
    · VectaraConnector
    · CSVConnector
  LLM Judge Models
    · LLMJudgeModel (Abstract Base Class)
    · OpenAIModel
    · GeminiModel
  Metrics
    · Retrieval Metrics
    · Generation Metrics
  Data Structures
    · RAGResult
    · ScoredRAGResult
  Evaluation Workflow
    · RAG Evaluation Flow Diagram
  Configuration System
    · Configuration Structure
  Integration and Extension Points

## · Evaluation Pipeline  (L1643)
  源文件: README.md, img/project-logo.png, open_rag_eval/models/__init__.py, open_rag_eval/run_eval.py, sample_prompt.txt
  Overview
  Pipeline Architecture
  Main Components
  Execution Flow
  Configuration Loading
  Dynamic Component Instantiation
    · Evaluator Creation
    · Connector Creation
  Data Retrieval and Evaluation
  Output Generation
  Command-Line Interface
  Integration with Other Components
  Summary

## · Evaluators  (L1914)
  源文件: open_rag_eval/evaluators/base_evaluator.py, open_rag_eval/evaluators/trec_evaluator.py, tests/test_base_evaluator.py
  Purpose and Scope
  Evaluator Architecture
    · Base Evaluator Class
    · TRECEvaluator Implementation
  Evaluation Process
    · Single Evaluation
    · Batch Evaluation
  Visualization Capabilities
  Score Structure

## · Connectors  (L2139)
  源文件: CONTRIBUTING.md, img/viz_1.png, img/viz_2.png, open_rag_eval/connectors/csv_connector.py, open_rag_eval/connectors/vectara_connector.py
  1. Connector Architecture
    · 1.1 Base Connector Interface
    · 1.2 Data Flow
  2. VectaraConnector
    · 2.1 Configuration and Authentication
    · 2.2 Data Fetching Process
    · 2.3 Retry Logic
  3. CSVConnector
    · 3.1 File Format
    · 3.2 Parsing Process
    · 3.3 Citation Handling
  4. Usage in Evaluation Pipeline
  5. Adding New Connectors

## · Vectara Connector  (L2400)
  源文件: open_rag_eval/connectors/vectara_connector.py, tests/test_vectara_connector.py, tests/test_vectara_connector_integration.py
  1. Architecture Overview
  2. Class Structure
  3. Initialization and Configuration
    · 3.1 Constructor
    · 3.2 Default Configuration
  4. Core Functionality
    · 4.1 Data Flow Process
    · 4.2 Main Method: fetch_data
  5. API Communication
    · 5.1 Query Method
    · 5.2 Request Handling with Retry Logic
  6. Configuration Management
    · 6.1 Helper Methods
  7. Output Format
  8. Usage Example
  9. Error Handling

## · CSV Connector  (L2699)
  源文件: CONTRIBUTING.md, img/viz_1.png, img/viz_2.png, open_rag_eval/connectors/csv_connector.py, tests/data/test_csv_connector.csv, tests/test_csv_connector.py
  Overview
  CSV Format Requirements
  Data Flow and Processing
  Citation Parsing
  Implementation Details
    · Initialization
    · Data Fetching
    · Citation Parsing
  Usage Example
  Handling Edge Cases
  Integration with the Evaluation Pipeline

## · LLM Judge Models  (L2926)
  源文件: open_rag_eval/models/llm_judges.py, tests/test_llm_judges_integration.py
  Purpose and Scope
  Model Architecture
  Integration with Evaluation System
  Supported Model Types
    · OpenAI Models
    · Gemini Models
  Core Functionalities
    · Text Generation with `call`
    · Structured Parsing with `parse`
  Configuration in Evaluation Pipeline
  Error Handling
  Implementation Details
    · OpenAI Model
    · Gemini Model
  Usage in Metrics

## · Metrics  (L3162)
  源文件: README.md, img/project-logo.png, open_rag_eval/_version.py, open_rag_eval/metrics/citation_metric.py, open_rag_eval/metrics/umbrela_metric.py, sample_prompt.txt, UMBRELA and Citation Metrics, AutoNugget Metric, No Answer Metric
  Purpose and Scope
  Metric Architecture
    · Metric Types
  Core Metrics
    · UMBRELA Metric
    · Citation Metric
    · Other Metrics
  Metric Usage in Evaluation
    · Integration with LLM Judges
  Metric Configuration
  Interpreting Metric Scores

## · UMBRELA and Citation Metrics  (L3430)
  源文件: open_rag_eval/_version.py, open_rag_eval/metrics/citation_metric.py, open_rag_eval/metrics/umbrela_metric.py
  1. Overview
  2. UMBRELA Metric
    · 2.1 Scoring Scale
    · 2.2 Implementation
    · 2.3 Evaluation Process
  3. Citation Metric
    · 3.1 Support Levels
    · 3.2 Implementation
    · 3.3 Scoring Methodology
    · 3.4 Evaluation Process
  4. Integration in the Evaluation Pipeline
  5. Usage Examples

## · AutoNugget Metric  (L3712)
  源文件: open_rag_eval/metrics/__init__.py, open_rag_eval/metrics/autonugget_metric.py, tests/test_no_answer_metric.py
  Core Concepts
  Workflow and Components
  Implementation Details
    · 1. Nugget Creation
    · 2. Nugget Scoring and Sorting
    · 3. Nugget Assignment
    · 4. Answer Evaluation
  Scoring Metrics and Interpretation
  LLM Prompting Strategy
  Integration with Other Metrics

## · No Answer Metric  (L4026)
  源文件: open_rag_eval/metrics/no_answer_metric.py
  Overview
  Purpose and Design
  Implementation Architecture
  Processing Flow
  Prompt Design
  Integration with Evaluation Pipeline
  Usage Example
  Technical Implementation
  Error Handling
  Summary

## · Visualization  (L4259)
  源文件: README.md, img/project-logo.png, open_rag_eval/viz/visualize.py, sample_prompt.txt
  Overview of Visualization Features
  Results Plotting
    · Usage
    · Results Plotting Data Flow
  Interactive Results Explorer
    · Launching the Explorer
    · Features of the Interactive Explorer
    · Interactive Explorer Architecture
  Visualization Data Flow in Evaluation Pipeline
  Key Metrics Visualized
  Understanding the Interactive Explorer
    · Metric Visualization Components
    · Data Parsing Components
  Practical Usage Tips
  Conclusion

## · Development  (L4541)
  源文件: .gitignore, README.md, img/project-logo.png, sample_prompt.txt
  Project Structure
  Development Environment Setup
    · Prerequisites
    · Development Container
  Extension Points
    · Creating Custom Connectors
    · Creating Custom Metrics
    · Creating Custom Judge Models
  Contribution Workflow
    · Contributing Guidelines
  Extending the Visualization Components
  API Extensions
  Development Resources

## · Testing  (L4853)
  源文件: open_rag_eval/evaluators/base_evaluator.py, tests/data/test_csv_connector.csv, tests/test_base_evaluator.py, tests/test_csv_connector.py, tests/test_vectara_connector.py, tests/test_vectara_connector_integration.py
  Overview of Testing Framework
  Unit Testing Approach
    · Example Unit Test Structure
  Mocking External Dependencies
    · Key Mocking Techniques
  Integration Testing
    · Integration Test Features
  Test Data Management
    · Test Data Patterns
  Testing Abstract Base Classes
    · Testing Abstract Classes
  Writing New Tests
    · Test Structure Pattern
  Running Tests
  Best Practices