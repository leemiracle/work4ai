# Skeleton: storm（24 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 20KB | 7 | ~12 | 5 |
| 2 | Installation and Setup | L453 | 10KB | 3 | ~0 | 5 |
| 3 | System Architecture | L776 | 13KB | 7 | ~4 | 5 |
| 4 | STORM Wiki Generation System | L1114 | 16KB | 7 | ~0 | 4 |
| 5 | STORMWikiRunner | L1563 | 18KB | 10 | ~11 | 4 |
| 6 | Knowledge Curation Module | L2071 | 16KB | 5 | ~6 | 6 |
| 7 | Outline and Article Generation Modules | L2454 | 25KB | 6 | ~14 | 8 |
| 8 | STORM Data Structures | L3125 | 18KB | 6 | ~9 | 1 |
| 9 | Co-STORM Collaborative System | L3573 | 15KB | 8 | ~0 | 4 |
| 10 | CoStormRunner | L4026 | 18KB | 9 | ~5 | 4 |
| 11 | Knowledge Base System | L4510 | 22KB | 7 | ~7 | 3 |
| 12 | Agent System | L5087 | 17KB | 6 | ~7 | 4 |
| 13 | Collaborative Modules | L5522 | 27KB | 8 | ~16 | 6 |
| 14 | Core Infrastructure | L6166 | 21KB | 7 | ~7 | 3 |
| 15 | Language Model Integration | L6629 | 15KB | 4 | ~9 | 2 |
| 16 | Retrieval Modules | L7050 | 17KB | 5 | ~21 | 3 |
| 17 | Encoder System | L7634 | 16KB | 7 | ~13 | 1 |
| 18 | Utilities and Helpers | L8114 | 20KB | 6 | ~8 | 2 |
| 19 | Abstract Interfaces | L8765 | 13KB | 8 | ~4 | 1 |
| 20 | Usage and Examples | L9170 | 10KB | 5 | ~9 | 3 |
| 21 | STORM Examples | L9432 | 19KB | 5 | ~14 | 4 |
| 22 | Co-STORM Examples | L10021 | 18KB | 7 | ~15 | 3 |
| 23 | Streamlit Frontend Demo | L10556 | 10KB | 7 | ~5 | 6 |
| 24 | Package and Development | L10820 | 11KB | 3 | ~5 | 3 |


## · Overview  (L6)
  源文件: .github/workflows/python-package.yml, README.md, knowledge_storm/__init__.py, knowledge_storm/lm.py, setup.py
  What is STORM?
  What is Co-STORM?
  Core Package Structure
  System Architecture: Code Entity View
  STORM vs Co-STORM: Operational Paradigms
    · STORM: Linear 4-Stage Pipeline
    · Co-STORM: Iterative Collaborative Loop
  Infrastructure Layer: Shared Components
    · Language Model Integration
    · Retrieval Module Layer
  Data Flow and Transformation
    · STORM Data Pipeline
    · Co-STORM Data Flow
  Multi-LLM System Design
    · STORM Task Assignment (5 LMs)
    · Co-STORM Task Assignment (6 LMs)
  Technology Stack Summary
  Usage Patterns
    · STORM: Fully Automated Pipeline
    · Co-STORM: Interactive Collaboration
  Key Design Principles

## · Installation and Setup  (L453)
  源文件: .github/workflows/python-package.yml, README.md, knowledge_storm/__init__.py, knowledge_storm/lm.py, setup.py
  System Requirements
  Installation Methods
    · Package Installation
    · Source Code Installation
  Configuration Setup
    · API Keys and Secrets Configuration
    · Supported Components
  Installation and Setup Workflow
  Configuration Components and Code Mapping
  Quick Verification
    · For STORM Wiki Generator:
    · For Co-STORM Collaborative System:
  Package Architecture
  Basic Usage Examples
    · STORM Wiki Generator Example
    · Co-STORM Example

## · System Architecture  (L776)
  源文件: README.md, knowledge_storm/interface.py, knowledge_storm/lm.py, knowledge_storm/storm_wiki/engine.py, knowledge_storm/utils.py
  Dual Engine System
    · Primary Engine Classes
  Shared Infrastructure Components
    · Language Model Integration
    · Retrieval Module Architecture
  Abstract Interface System
    · Core Module Interfaces
    · Data Structure Interfaces
  Agent System Architecture
    · Agent Interface and Implementations
  Data Processing Pipeline
    · STORM Processing Flow
    · Co-STORM Processing Flow
  Configuration and Extensibility
    · Engine Configuration Structure

## · STORM Wiki Generation System  (L1114)
  源文件: README.md, knowledge_storm/lm.py, knowledge_storm/storm_wiki/engine.py, knowledge_storm/utils.py
  System Architecture
  STORMWikiRunner
    · Configuration and Initialization
    · Pipeline Execution
  Knowledge Curation Pipeline
    · Perspective-Guided Question Asking
    · Simulated Conversations
    · Information Organization
  Outline Generation
  Article Generation
  Article Polishing
  Language Model Configuration
  Data Structures
    · StormInformationTable
    · StormArticle
    · DialogueTurn
  Integration with External Components
    · Retrieval Module
    · Language Model Integration
  Summary

## · STORMWikiRunner  (L1563)
  源文件: README.md, knowledge_storm/lm.py, knowledge_storm/storm_wiki/engine.py, knowledge_storm/utils.py
  Overview
  Configuration Classes
    · STORMWikiLMConfigs
    · STORMWikiRunnerArguments
  Initialization and Architecture
    · Component Structure
  Execution Flow
    · The `run()` Method
  Module Execution Methods
    · Knowledge Curation Stage
    · Outline Generation Stage
    · Article Generation Stage
    · Article Polishing Stage
  File System Artifacts
    · Artifact Details
  State Loading and Resume Capability
  Post-Run Operations
  Usage Example
  Integration with Infrastructure

## · Knowledge Curation Module  (L2071)
  源文件: knowledge_storm/storm_wiki/modules/article_generation.py, knowledge_storm/storm_wiki/modules/article_polish.py, knowledge_storm/storm_wiki/modules/knowledge_curation.py, knowledge_storm/storm_wiki/modules/outline_generation.py, knowledge_storm/storm_wiki/modules/persona_generator.py, knowledge_storm/storm_wiki/modules/retriever.py
  Purpose and Scope
  Overview
  Architecture
    · Component Hierarchy
  Core Components
    · StormKnowledgeCurationModule
    · Perspective Generation
    · Conversation Simulation
    · Question Generation (WikiWriter)
    · Information Retrieval and Answering (TopicExpert)
  Complete Data Flow
  Parallel Execution Strategy
  Source Reliability Filtering
  Output Format
  Configuration Parameters
  Callback Integration
  Usage Example

## · Outline and Article Generation Modules  (L2454)
  源文件: knowledge_storm/storm_wiki/engine.py, knowledge_storm/storm_wiki/modules/article_generation.py, knowledge_storm/storm_wiki/modules/article_polish.py, knowledge_storm/storm_wiki/modules/knowledge_curation.py, knowledge_storm/storm_wiki/modules/outline_generation.py, knowledge_storm/storm_wiki/modules/persona_generator.py, knowledge_storm/storm_wiki/modules/retriever.py, knowledge_storm/utils.py
  Overview: Pipeline Stages 2-4
  Stage 2: Outline Generation Module
    · Module Architecture
    · Two-Step Outline Generation Process
    · Outline Format and Cleanup
    · Key Methods
  Stage 3: Article Generation Module
    · Module Architecture
    · Configuration Parameters
    · Section Generation Workflow
    · Information Retrieval for Sections
    · Section Writing with Citations
    · Parallel Execution
  Stage 4: Article Polishing Module
    · Module Architecture
    · Lead Section Generation
    · Duplicate Content Removal
    · Key Methods
  Integration in STORMWikiRunner
    · Module Initialization
    · Execution Flow in STORMWikiRunner
    · Stage Runner Methods
    · Modular Execution Support
  Data Flow and Transformations
    · Key Data Transformations
  LLM Configuration for Each Stage
  Text Processing Utilities
    · Citation Management
    · Outline and Section Cleanup
    · Content Limits

## · STORM Data Structures  (L3125)
  源文件: knowledge_storm/storm_wiki/modules/storm_dataclass.py
  Purpose and Scope
  Overview
  DialogueTurn Class
    · Structure and Purpose
    · Attributes
    · Initialization and Serialization
  StormInformationTable Class
    · Overview and Design
    · URL-Based Information Aggregation
    · Semantic Retrieval System
    · Persistence
  StormArticle Class
    · Architecture and Hierarchical Structure
    · Core Components
    · Key Methods
    · Serialization and Deserialization
    · Post-Processing
  Data Flow Through Pipeline

## · Co-STORM Collaborative System  (L3573)
  源文件: README.md, knowledge_storm/collaborative_storm/engine.py, knowledge_storm/collaborative_storm/modules/information_insertion_module.py, knowledge_storm/lm.py
  Architecture Overview
  Core Components
    · DiscourseManager
    · Knowledge Base System
    · Agent System
  Workflow
    · Warm Start Process
    · Collaborative Discourse
    · Report Generation
  Implementation
    · CoStormRunner
    · Configuration
  Usage Example
  Summary

## · CoStormRunner  (L4026)
  源文件: README.md, knowledge_storm/collaborative_storm/engine.py, knowledge_storm/collaborative_storm/modules/information_insertion_module.py, knowledge_storm/lm.py
  Core Architecture
  Configuration Classes
    · CollaborativeStormLMConfigs
    · RunnerArgument
  Initialization
  Warm Start Phase
  Conversation Management: The step() Method
    · Turn Policy Management
    · Usage Patterns
  Knowledge Base Integration
  Report Generation
  Persistence and State Management
  DiscourseManager Internal Structure
  Callback Hooks
  Complete Workflow Diagram

## · Knowledge Base System  (L4510)
  源文件: knowledge_storm/collaborative_storm/engine.py, knowledge_storm/collaborative_storm/modules/information_insertion_module.py, knowledge_storm/dataclass.py
  Overview
  Core Data Structures
    · KnowledgeNode
    · KnowledgeBase
  Information Management
    · UUID-Based Citation System
    · Information Object Storage
  Information Insertion System
    · Architecture
    · Strategy 1: Embedding-Based Ranking
    · Strategy 2: Layer-by-Layer Navigation
    · Multi-Threaded Processing
  Knowledge Base Reorganization
    · Reorganization Workflow
    · Node Expansion
    · Cleaning Operations
  Knowledge Base Traversal and Queries
    · Tree Traversal Methods
    · Structure Representation
    · Structure Embedding Cache
  Report Generation
  Integration with Co-STORM
    · Initialization in CoStormRunner
    · Update from Conversation Turns
    · Warm Start Initialization
    · Serialization and Persistence
    · Thread Safety

## · Agent System  (L5087)
  源文件: knowledge_storm/collaborative_storm/modules/callback.py, knowledge_storm/collaborative_storm/modules/co_storm_agents.py, knowledge_storm/collaborative_storm/modules/grounded_question_generation.py, knowledge_storm/collaborative_storm/modules/warmstart_hierarchical_chat.py
  Purpose and Scope
  Agent Base Class and Interface
  Agent Type Overview
  CoStormExpert
    · Initialization and Configuration
    · Utterance Generation Pipeline
    · Utterance Generation Module
  Moderator
    · Moderator Architecture
    · Unused Information Detection and Reranking
    · Question Generation
  SimulatedUser
    · Configuration and Intent
    · Utterance Generation
  PureRAGAgent
    · Simplified Architecture
    · Implementation Details
  Agent Interaction in the Discourse
  Callback System for Agent Actions
    · Callback Hook Points
    · Example: LocalConsolePrintCallBackHandler
  Warm Start Agents
    · WarmStartConversation
    · Background Discussion Agents
  Agent Selection and Lifecycle

## · Collaborative Modules  (L5522)
  源文件: knowledge_storm/collaborative_storm/engine.py, knowledge_storm/collaborative_storm/modules/callback.py, knowledge_storm/collaborative_storm/modules/co_storm_agents.py, knowledge_storm/collaborative_storm/modules/grounded_question_generation.py, knowledge_storm/collaborative_storm/modules/information_insertion_module.py, knowledge_storm/collaborative_storm/modules/warmstart_hierarchical_chat.py
  Module Architecture Overview
  WarmStartModule
    · WarmStartModule Components
    · Warm Start Pipeline
    · Multi-Expert Perspective-Guided QA
    · Outline Generation and Knowledge Base Initialization
    · Conversation Synthesis
  InsertInformationModule
    · Module Components
    · Information Insertion Strategies
    · Embedding-Based Candidate Selection
    · Layer-by-Layer Navigation
    · Parallel vs Sequential Insertion
  ExpandNodeModule
    · Module Architecture
    · Node Expansion Process
    · Expansion Trigger Configuration
    · Subsection Generation
    · Re-insertion After Expansion
  DiscourseManager
    · DiscourseManager Components
    · DiscourseManager Role Management
    · Turn Policy Determination
    · Moderator Override Logic
    · Expert Pool Rotation
  TurnPolicySpec
    · TurnPolicySpec Structure
    · Turn Policy Flags
    · Integration with CoStormRunner
  Module Integration Patterns
    · Integration Architecture

## · Core Infrastructure  (L6166)
  源文件: README.md, knowledge_storm/interface.py, knowledge_storm/lm.py
  Purpose and Scope
  Infrastructure Architecture
  Language Model Integration Architecture
    · Key Components
    · Token Tracking
  Retrieval Module Architecture
    · Retriever Interface
    · Retrieval Module Implementations
  Abstract Interface System
    · Key Abstract Contracts
    · Decorator Pattern for Execution Tracking
  Performance Optimization and Observability
    · Two-Tier Caching System
    · Token Usage Tracking
    · Parallel Query Execution
    · Execution Time and Cost Summary
  Integration with STORM and Co-STORM
    · STORM Configuration
    · Co-STORM Configuration

## · Language Model Integration  (L6629)
  源文件: README.md, knowledge_storm/lm.py
  Overview
  Language Model Architecture
  LitellmModel: The Primary Integration Class
  Multi-Model Strategy for Cost and Performance
    · Configuration Implementation
  Caching System
    · Implementation Architecture
    · Configuration Details
    · Usage Control
    · Cache Flow
  Token Usage Tracking
    · Implementation Details
    · Usage Tracking Flow
    · Code Example
    · Response Structure
  Legacy Model Integrations
  Integration Examples
    · Basic STORM Integration
    · Co-STORM Integration
  Related Pages

## · Retrieval Modules  (L7050)
  源文件: MANIFEST.in, knowledge_storm/rm.py, requirements.txt
  Purpose and Scope
  Unified Interface Architecture
    · Core Interface Contract
    · Standard Return Format
  Web Search Retrieval Modules
    · YouRM
    · BingSearch
    · BraveRM
    · SerperRM
    · DuckDuckGoSearchRM
    · TavilySearchRM
    · GoogleSearch
    · SearXNG
    · Web Search Module Comparison
  Vector Search Retrieval Module
    · VectorRM
  Specialized Retrieval Modules
    · AzureAISearch
    · StanfordOvalArxivRM
  WebPageHelper Pattern
    · Modules Using WebPageHelper
    · WebPageHelper Configuration
    · Two-Phase Retrieval Pattern
  Configuration and Usage Tracking
    · API Key Management
    · Usage Tracking Pattern
    · Source Filtering Pattern
  Return Format Details
    · Standard Dictionary Structure
    · Snippet Processing
  Implementation Summary
    · Module Selection Guide
    · Common Integration Pattern

## · Encoder System  (L7634)
  源文件: knowledge_storm/encoder.py
  Purpose and Scope
  Architecture Overview
  Initialization and Configuration
    · Supported Providers
    · Initialization Example
  Embedding Generation
    · Processing Flow
    · Single Text Embedding
    · Batch Embedding
  Caching Mechanism
    · Cache Implementation Details
  Token Usage Tracking
    · Tracking Architecture
    · Token Tracking Implementation
  Integration with STORM Systems
    · Usage Map
    · Primary Use Cases
    · Co-STORM Integration Details
    · VectorRM Integration Details
  Error Handling
    · Import Error Handling
    · Configuration Validation
    · Runtime Error Handling
  LiteLLM Configuration

## · Utilities and Helpers  (L8114)
  源文件: knowledge_storm/storm_wiki/engine.py, knowledge_storm/utils.py
  Overview of Utility Components
  QdrantVectorStoreManager
    · Core Functionality
    · Vector Store Creation
    · Collection Management
    · Text Splitting Configuration
  ArticleTextProcessing
    · Citation Processing Methods
    · Key Methods
    · Article Parsing
  FileIOHelper
    · Supported Operations
    · JSON Handling
    · Usage Pattern
  WebPageHelper
    · Architecture
    · Configuration
    · Download Process
    · Text Splitting Configuration
  Input Validation Functions
    · user_input_appropriateness_check
    · purpose_appropriateness_check
    · Implementation Details
  Other Utility Functions
    · truncate_filename
    · load_api_key
    · makeStringRed
  Utility Integration Patterns
    · Usage in STORMWikiRunner
    · Usage in Retrieval Modules

## · Abstract Interfaces  (L8765)
  源文件: knowledge_storm/interface.py
  Interface Architecture Overview
  Core Data Structures
    · Information and InformationTable
    · Article Structure
  Processing Module Interfaces
    · Knowledge Curation Interface
    · Generation Module Interfaces
    · Retriever Base Class
  Orchestration Interfaces
    · Engine Abstract Base Class
    · LMConfigs Abstract Base Class
  Agent Interface
  Interface Implementation Patterns
    · Logging and Monitoring Integration
    · Extension Points

## · Usage and Examples  (L9170)
  源文件: examples/costorm_examples/run_costorm_gpt.py, examples/storm_examples/run_storm_wiki_mistral.py, examples/storm_examples/run_storm_wiki_ollama.py
  Overview of Example Structure
  Example Output Structure
  Language Model Configuration Pattern
  Retrieval Module Selection
  Pipeline Stage Control
  Open Model Enhancement Techniques
  Command Line Interface Structure
    · Global Configuration Parameters
    · Pipeline Hyperparameters
  Environment Setup Requirements

## · STORM Examples  (L9432)
  源文件: README.md, examples/storm_examples/run_storm_wiki_mistral.py, examples/storm_examples/run_storm_wiki_ollama.py, knowledge_storm/lm.py
  Overview
  Configuration Pattern
  Example 1: OpenAI GPT Models
  Example 2: Ollama (Local Models)
  Example 3: VLLM Server (Mistral)
  Retrieval Module Configuration
  Pipeline Execution
  Hyperparameter Configuration
  Prompt Engineering for Open-Source Models
  Output Structure
  API Key Configuration
  Command Reference Table

## · Co-STORM Examples  (L10021)
  源文件: README.md, examples/costorm_examples/run_costorm_gpt.py, knowledge_storm/lm.py
  Quick Start Example
    · Basic Execution with Bing Search
  Environment Setup and Configuration
    · API Keys and Environment Variables
    · Supported Retrieval Modules
  Command Line Arguments Reference
    · Core System Arguments
    · Retrieval Parameters
    · Discourse Control Parameters
    · Warm Start Parameters
    · Knowledge Base Parameters
  Example Script Components
    · Language Model Configuration in run_costorm_gpt.py
    · RunnerArgument Configuration
    · Retrieval Module Instantiation
  Complete Execution Flow Example
  Conversation Interaction Patterns
    · Observation Mode
    · Active Participation Mode
    · ConversationTurn Data Structure
  Output Files and Format
    · Output Directory Structure
    · File Generation Process
  Example Usage Commands
    · Basic Co-STORM Execution with Bing Search
    · Advanced Configuration with Custom Parameters
    · Using DuckDuckGo (No API Key Required)

## · Streamlit Frontend Demo  (L10556)
  源文件: frontend/demo_light/README.md, frontend/demo_light/demo_util.py, frontend/demo_light/pages_util/CreateNewArticle.py, frontend/demo_light/pages_util/MyArticles.py, frontend/demo_light/stoc.py, frontend/demo_light/storm.py
  Architecture Overview
    · Application Structure
    · Session State Management
  My Articles Page
    · Article Discovery and Display
    · File Structure Processing
  Create New Article Page
    · State Machine Workflow
    · Article Generation Pipeline
    · Real-time Progress Tracking
  Core Utility Components
    · DemoFileIOHelper Class
    · Article Display System
  Configuration and Setup
    · STORM Runner Configuration
    · Environment Setup
  Text Processing and Citations
    · Citation Processing Pipeline
    · Table of Contents Generation

## · Package and Development  (L10820)
  源文件: .github/workflows/python-package.yml, knowledge_storm/__init__.py, setup.py
  Package Information
    · Package Metadata
    · Module Structure
  Distribution on PyPI
    · Build Configuration
    · Installation
  Dependencies
    · Dependency Categories
  CI/CD Workflow
    · Workflow Overview
    · Workflow Stages
    · Security Considerations
  Development Setup
    · Local Development Installation
    · Version Management
    · Package Structure Considerations
    · Publishing Workflow
  Summary