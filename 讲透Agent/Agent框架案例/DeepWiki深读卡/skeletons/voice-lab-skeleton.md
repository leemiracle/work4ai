# Skeleton: voice-lab（18 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Voice Lab Overview | L6 | 9KB | 3 | ~4 | 4 |
| 2 | Getting Started | L233 | 7KB | 3 | ~7 | 3 |
| 3 | Testing Systems | L490 | 9KB | 6 | ~4 | 5 |
| 4 | LLM Conversation Testing | L783 | 10KB | 5 | ~5 | 3 |
| 5 | Web Chatbot Evaluation | L1006 | 11KB | 3 | ~7 | 2 |
| 6 | Speech Analysis Testing | L1344 | 11KB | 7 | ~7 | 6 |
| 7 | Real-time Voice Interaction | L1668 | 12KB | 8 | ~6 | 4 |
| 8 | Test Configuration | L2025 | 8KB | 4 | ~7 | 5 |
| 9 | LLM Test Scenarios | L2271 | 9KB | 3 | ~9 | 1 |
| 10 | Web Test Scenarios | L2555 | 9KB | 6 | ~3 | 1 |
| 11 | Evaluation & Metrics | L2805 | 11KB | 4 | ~7 | 4 |
| 12 | Test Results & Reporting | L3102 | 8KB | 7 | ~3 | 2 |
| 13 | Core Architecture | L3331 | 10KB | 5 | ~1 | 3 |
| 14 | Data Types & Models | L3668 | 9KB | 5 | ~8 | 2 |
| 15 | LLM Providers & Interfaces | L3947 | 9KB | 5 | ~3 | 2 |
| 16 | Speech Processing Components | L4161 | 11KB | 4 | ~4 | 5 |
| 17 | Development Guide | L4447 | 8KB | 3 | ~2 | 4 |
| 18 | FAQ & Guidelines | L4741 | 9KB | 3 | ~0 | 3 |


## · Voice Lab Overview  (L6)
  源文件: .DS_Store, LICENSE, README.md, llm_testing/.DS_Store
  Purpose and Scope
  System Architecture
    · Core Components Architecture
  Testing Modalities
    · Testing Systems Overview
    · LLM Testing System Data Flow
  Data Types and Interfaces
    · Core Data Models
    · Provider Interface Pattern
  Integration Architecture  
    · External Service Integration
  Configuration and Extensibility
    · Configuration Files Structure
  Next Steps

## · Getting Started  (L233)
  源文件: .example.env, .gitignore, requirements.txt
  Prerequisites
    · API Access Requirements
  Installation Process
    · Step 1: Clone Repository
    · Step 2: Install Dependencies
    · Step 3: Environment Configuration
  Project Structure Overview
  Running Your First Test
    · Quick Start: LLM Conversation Testing
    · Alternative Testing Systems
  Verification Steps
    · 1. Dependency Check
    · 2. Environment Variables
    · 3. Core Components
  Next Steps
  Troubleshooting Common Issues

## · Testing Systems  (L490)
  源文件: .DS_Store, LICENSE, README.md, llm_testing/.DS_Store, main.py
  System Architecture Overview
  Test Execution Flow
  LLM Conversation Testing System
    · Key Components
  Web Chatbot Evaluation System
    · Key Components
  Speech Analysis Testing System
  Real-time Voice Interaction System
    · Key Components
  Data Flow Integration
  Speech Metrics Processing
    · Interruption Detection
    · Pause Analysis
  Test Result Standardization

## · LLM Conversation Testing  (L783)
  源文件: llm_testing/example_test.py, llm_testing/run_tests.py, llm_testing/test_runner.py
  Purpose and Scope
  System Overview
    · Core Test Execution Flow
  Core Components
    · GoalBasedTestRunner
    · Test Orchestration Architecture
  Test Configuration and Scenarios
    · Test Scenario Structure
    · Agent Task Configuration
  Conversation Simulation
    · Persona-Based Response Generation
    · Conversation Termination
  Integration with Evaluation System
    · LLM-as-a-Judge Integration
  Test Execution and Results
    · Multi-Variation Testing
    · Verbose Output and Debugging
    · Result Storage and Reporting

## · Web Chatbot Evaluation  (L1006)
  源文件: web_eval.py, web_test_scenarios.json
  Purpose and Scope
  System Architecture
  Test Execution Flow
  Core Components
    · ChatSessionManager Class
    · Data Models
    · Conversation Resolution Detection
  Configuration System
    · Test Scenario Structure
    · User Persona Configuration
  Browser Automation Details
    · Visual AI Integration
    · Shadow DOM Handling
    · Conversation History Extraction
  Evaluation Process
    · LLMConversationEvaluator Integration
    · Performance Metrics
  Results and Reporting
    · Test Results Structure

## · Speech Analysis Testing  (L1344)
  源文件: main.py, speech_testing/example_test.py, speech_testing/metrics/interruptions.py, speech_testing/metrics/interruptions_utils.py, speech_testing/metrics/pauses.py, speech_testing/run_tests.py
  System Architecture
  Audio Processing Pipeline
    · Speaker Diarization and Transcription
    · Data Flow and Segment Processing
  Speech Metrics Analysis
    · Interruption Detection
    · Pause Detection
  Integration with Test Framework
    · Result Integration
    · Metric Conversion
  Usage Patterns
    · Basic Test Execution
    · Test Configuration
    · File Processing
  System Dependencies
    · External Services
    · Audio Processing Libraries

## · Real-time Voice Interaction  (L1668)
  源文件: eval_agent/gemini_connection.py, eval_agent/requirements.txt, eval_agent/run_tests.py, eval_agent/voice_activity_detector.py
  System Overview
    · Core Architecture
  Core Components
    · GeminiConnection Class
    · Voice Activity Detection
  Audio Processing Pipeline
    · Input Audio Flow
    · Output Audio Flow
  Configuration and Setup
    · System Configuration
    · WebSocket Setup Message
  Integration Points
    · Test Runner Integration
    · Dependencies and Requirements
  Concurrent Task Management

## · Test Configuration  (L2025)
  源文件: .DS_Store, LICENSE, README.md, llm_testing/.DS_Store, llm_testing/config/test_scenarios.json
  Configuration Architecture
  Test Scenario Structure
  Configuration Components
    · Agent Configuration
    · Persona Configuration
    · Tool Function Definitions
  Configuration Management
    · Manual Configuration
    · Voice Lab Configuration Editor
  Multi-Model Testing
  Configuration File Locations

## · LLM Test Scenarios  (L2271)
  源文件: llm_testing/config/test_scenarios.json
  Overview
  Test Scenario Structure
    · Core Components
    · Component Mapping to Code Entities
  Configuration Structure
    · Tested Components Section
    · Agent Configuration
    · Persona Configuration
  Test Scenario Examples
    · Hotel Booking Scenario
    · Airline Seat Change Scenario
    · Jailbreaking Test Scenario
  End Conversation Tool Schema
    · Termination Reasons
    · Termination Evidence Structure
  Usage in Test Execution

## · Web Test Scenarios  (L2555)
  源文件: web_test_scenarios.json
  Purpose and Scope
  Scenario Structure Overview
  Configuration Components
    · Web Interface Configuration
    · Agent Configuration
  User Persona Modeling
  Success Criteria Definition
    · Multi-Component Success Patterns
    · Scenario-Specific Success Examples
  Mock Conversation Patterns
    · Conversation Flow Patterns
  Scenario Types and Use Cases
    · Customer Service Scenarios
    · Security and Compliance Scenarios
    · Integration with Web Testing System

## · Evaluation & Metrics  (L2805)
  源文件: core/evaluator.py, core/utils/html_report_style.css, eval_metrics.json, llm_testing/config/eval_metrics.json
  LLM-as-a-Judge Methodology
  Evaluation Architecture
  Metrics Configuration
    · Metric Types and Formats
    · Web Chatbot Metrics
    · LLM Testing Metrics
  Evaluation Workflow
  Scoring and Result Types
    · EvaluationResponse Structure
    · Success Determination Logic
  Integration with Testing Systems
    · Cross-System Integration Points

## · Test Results & Reporting  (L3102)
  源文件: core/utils/generate_report.py, test_results/test_run_example.html
  Overview
  Report Generation Process
  Report Structure and Components
    · Main Table Structure
    · Test Type Detection
    · Color Coding System
  Metric Evaluation Display
    · Success Indicators
    · Metric Display Format
  Interactive Features
    · Conversation Modal System
    · Message Format Handling
  File Organization and Output
    · Directory Structure
    · File Naming Convention
    · Auto-Launch Behavior
  CSS Styling System
  Integration with Testing Framework

## · Core Architecture  (L3331)
  源文件: core/evaluator.py, core/providers/openai.py, speech_testing/data_types.py
  Architectural Overview
    · Core Architecture Layers
  Core Component Architecture
    · Evaluation System Architecture
    · LLM Provider Interface Architecture
  Data Architecture Patterns
    · Speech Testing Data Model
  Cross-System Integration Patterns
    · Multi-Modal Integration Architecture
  Design Patterns and Principles
    · Abstract Base Class Pattern
    · Dependency Injection Pattern
    · Configuration-Driven Architecture

## · Data Types & Models  (L3668)
  源文件: core/evaluator.py, speech_testing/data_types.py
  Core Data Structure Overview
    · Data Type Architecture
  Entity Identification Types
    · EntitySpeaking Enumeration
  Speech Analysis Data Models
    · Call Segment Structure
    · Interruption Detection
    · Pause Analysis
    · Comprehensive Speech Results
  Audio Processing Configuration
    · Whisper Model Configuration
    · Speaker Identification Mapping
  Evaluation Data Types
    · Evaluation Response Structure
    · Configuration Data Types
  Data Flow Integration
    · LLM Evaluation Data Flow
    · Speech Analysis Data Flow

## · LLM Providers & Interfaces  (L3947)
  源文件: .example.env, core/providers/openai.py
  Provider Architecture Overview
  LLM Interface Contract
  OpenAI Provider Implementation
    · Initialization and Configuration
    · Core Method Implementations
    · Vision Model Integration
  Data Flow and Integration Patterns
  Environment Configuration
  Error Handling and Reliability
  Extension Points

## · Speech Processing Components  (L4161)
  源文件: speech_testing/example_test.py, speech_testing/metrics/interruptions.py, speech_testing/metrics/interruptions_utils.py, speech_testing/metrics/pauses.py, speech_testing/utils.py
  Speech Processing Pipeline
  Transcription Processing Utilities
    · Core Processing Functions
    · Transcription Format Conversion
    · Speaker Processing
  Speech Metrics Calculation
    · Interruption Detection
    · Pause Detection
    · Advanced Audio Processing
  Data Type Transformations
    · Conversation History Conversion
    · Mock Data Generation
  Audio Format Processing
    · Whisper Integration
    · Audio Chunk Processing

## · Development Guide  (L4447)
  源文件: .gitignore, core/utils.py, core/utils/__init__.py, requirements.txt
  Project Structure Overview
    · High-Level Organization
    · Directory Structure Patterns
  Development Environment
    · Core Dependencies
    · Git Configuration
  Core Development Patterns
    · Module Organization
    · Utility Functions
  Code Extension Patterns
    · Adding New Testing Modalities
    · Provider Integration
    · Utility Development
  Development Workflow
    · File Exclusions
    · Environment Management
  Testing and Quality Assurance
    · Test Structure
    · Output Management
  Contribution Guidelines
    · Code Organization Principles
    · Development Dependencies
    · File Management

## · FAQ & Guidelines  (L4741)
  源文件: faqs/billing_notion.md, faqs/fraud_substack.md, faqs/sonos_connection_issue.md
  Framework Overview FAQs
    · What testing modalities does Voice Lab support?
    · How does the evaluation system work?
    · What LLM providers are supported?
    · How are test results stored and presented?
  Configuration FAQs
    · How do I define test scenarios?
    · What environment variables are required?
    · How do I customize evaluation metrics?
  Testing System-Specific FAQs
    · Web Chatbot Testing
    · Speech Analysis Testing
    · Real-time Voice Integration
  Domain-Specific Testing Guidelines
    · Customer Support Testing Scenarios
  Testing Best Practices
    · Scenario Design Guidelines
    · Evaluation Guidelines
  Troubleshooting Common Issues
    · Setup and Configuration Issues
    · Test Execution Issues
    · Report Generation Issues