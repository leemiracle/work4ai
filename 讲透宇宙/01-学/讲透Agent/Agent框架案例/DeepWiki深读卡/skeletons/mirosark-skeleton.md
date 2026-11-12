# Skeleton: mirosark（31 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | MiroShark Overview | L6 | 5KB | 2 | ~2 | 5 |
| 2 | Getting Started & Configuration | L131 | 8KB | 2 | ~4 | 23 |
| 3 | System Architecture & Data Flow | L299 | 7KB | 2 | ~1 | 8 |
| 4 | Knowledge Graph Pipeline | L441 | 6KB | 1 | ~2 | 6 |
| 5 | Document Ingestion & Ontology Generation | L561 | 9KB | 2 | ~3 | 15 |
| 6 | NER Extraction & Graph Building | L735 | 8KB | 2 | ~2 | 7 |
| 7 | Neo4j Storage & Graph Search | L901 | 8KB | 2 | ~2 | 7 |
| 8 | Agent Generation & Simulation Preparation | L1058 | 7KB | 2 | ~2 | 4 |
| 9 | OASIS Profile Generator | L1197 | 7KB | 2 | ~1 | 4 |
| 10 | Simulation Configuration Generator | L1341 | 7KB | 2 | ~1 | 5 |
| 11 | Simulation Execution Engine | L1479 | 7KB | 2 | ~2 | 13 |
| 12 | Parallel Simulation Runner & IPC | L1618 | 7KB | 2 | ~1 | 7 |
| 13 | Wonderwall Social Platform (Twitter & Reddit) | L1737 | 7KB | 2 | ~2 | 14 |
| 14 | Polymarket Prediction Market Simulation | L1892 | 6KB | 2 | ~2 | 9 |
| 15 | Belief State, Round Memory & Cross-Platform Awareness | L2024 | 8KB | 2 | ~0 | 11 |
| 16 | Report Generation & Analysis | L2155 | 6KB | 2 | ~2 | 4 |
| 17 | ReportAgent: ReACT Loop & Report Lifecycle | L2287 | 7KB | 2 | ~3 | 2 |
| 18 | GraphToolsService: Data Retrieval Tools | L2431 | 7KB | 2 | ~4 | 3 |
| 19 | Frontend Application | L2585 | 6KB | 2 | ~2 | 9 |
| 20 | Home, Routing & Design System | L2733 | 8KB | 2 | ~2 | 7 |
| 21 | Graph Build & Environment Setup Steps (Steps 1–2) | L2908 | 8KB | 2 | ~1 | 5 |
| 22 | Simulation Execution UI (Step 3) | L3058 | 8KB | 2 | ~2 | 3 |
| 23 | Report & Interaction UI (Steps 4–5) | L3214 | 8KB | 2 | ~2 | 5 |
| 24 | Backend API Reference | L3364 | 6KB | 2 | ~0 | 6 |
| 25 | Graph API (graph_bp) | L3513 | 6KB | 2 | ~0 | 3 |
| 26 | Simulation API (simulation_bp) | L3675 | 7KB | 2 | ~3 | 2 |
| 27 | Report API (report_bp) | L3819 | 6KB | 2 | ~4 | 4 |
| 28 | Infrastructure & Deployment | L3953 | 5KB | 2 | ~0 | 9 |
| 29 | Docker & Production Deployment | L4071 | 6KB | 2 | ~3 | 7 |
| 30 | Test Fixtures & Pipeline Test Outputs | L4221 | 9KB | 2 | ~2 | 7 |
| 31 | Glossary | L4406 | 9KB | 2 | ~4 | 19 |


## · MiroShark Overview  (L6)
  源文件: README.md, frontend/index.html, frontend/src/App.vue, frontend/src/views/Home.vue, miroshark.jpg
  Core Workflow
  High-Level Architecture
    · System Components Diagram
  Key Architectural Concepts
    · 1. Knowledge Graph Grounding
    · 2. Multi-Platform Synchronization
    · 3. Hyperstitions Design System
  Subsystem Integration
  Next Steps

## · Getting Started & Configuration  (L131)
  源文件: .dockerignore, .env.example, .github/workflows/docker-image.yml, .gitignore, Dockerfile, backend/app/config.py, backend/app/services/ontology_generator.py, backend/app/storage/ner_extractor.py, backend/app/utils/__init__.py, backend/app/utils/file_parser.py, backend/app/utils/llm_client.py, backend/app/utils/logger.py
  Environment Setup & Prerequisites
    · Local Development Installation
    · Docker Deployment
  Configuration (.env)
    · LLM Provider Selection
    · Embedding Configuration
  System Initialization Flow
    · Configuration Loading & Validation
  LLM Client Architecture
    · Client Data Flow
    · Key Functions & Implementation Details
  Development Scripts Reference

## · System Architecture & Data Flow  (L299)
  源文件: README.md, backend/app/api/__init__.py, backend/app/models/task.py, backend/app/utils/logger.py, backend/run.py, frontend/src/api/report.js, frontend/src/api/simulation.js, frontend/src/router/index.js
  High-Level Architecture
    · System Component Diagram
  Data Flow Pipeline
    · 1. Knowledge Graph Construction
    · 2. Agent & Environment Preparation
    · 3. Simulation Execution (Wonderwall)
    · 4. Cross-Platform Interaction
    · 5. Analysis & Report Generation
  Technical Implementation Details
    · Threading & Process Management
    · Logging and Monitoring
    · API Blueprints

## · Knowledge Graph Pipeline  (L441)
  源文件: .env.example, backend/app/services/graph_builder.py, backend/app/services/ontology_generator.py, backend/app/storage/ner_extractor.py, backend/app/utils/__init__.py, backend/app/utils/llm_client.py
    · Pipeline Overview
    · 1. Document Ingestion & Ontology Generation
    · 2. NER Extraction & Graph Building
    · 3. Neo4j Storage & Graph Search
    · Code Entity Mapping

## · Document Ingestion & Ontology Generation  (L561)
  源文件: .env.example, .gitignore, backend/app/api/graph.py, backend/app/api/report.py, backend/app/services/ontology_generator.py, backend/app/storage/ner_extractor.py, backend/app/utils/__init__.py, backend/app/utils/file_parser.py, backend/app/utils/llm_client.py, backend/pyproject.toml, backend/requirements.txt, backend/uv.lock
  1. Document Ingestion & Parsing
    · File Parsing Logic
    · Data Flow: Ingestion to Project
  2. Ontology Generation Service
    · The Smart LLM Client
    · Design Constraints (Prompt Engineering)
    · System Sequence: Ontology Generation
  3. Implementation Details
    · Text Chunking for Analysis
    · JSON Validation and Cleaning
    · Key Class: OntologyGenerator
    · Code Structure: Ontology Definition
  4. Configuration Requirements

## · NER Extraction & Graph Building  (L735)
  源文件: .env.example, backend/app/services/graph_builder.py, backend/app/services/ontology_generator.py, backend/app/services/text_processor.py, backend/app/storage/ner_extractor.py, backend/app/utils/__init__.py, backend/app/utils/llm_client.py
  System Architecture & Data Flow
    · High-Level Build Sequence
    · Code-to-Logic Mapping: Extraction Pipeline
  NERExtractor: Intelligence Logic
    · Extraction Rules & Constraints
    · Data Flow: Text to JSON
  GraphBuilderService: Orchestration & Batching
    · Concurrency Model
    · Progress Tracking
  Persistence via Neo4j UNWIND
    · Code-to-Database Space Mapping
    · Batch Upsert Logic

## · Neo4j Storage & Graph Search  (L901)
  源文件: backend/app/services/graph_builder.py, backend/app/storage/embedding_service.py, backend/app/storage/neo4j_schema.py, backend/app/storage/neo4j_storage.py, backend/wonderwall/simulations/polymarket/__init__.py, backend/wonderwall/simulations/polymarket/platform.py, backend/wonderwall/social_agent/belief_state.py
  Neo4jStorage Implementation
    · Schema Enforcement
    · Resilience & Retries
  Embedding Pipeline
    · Data Flow: Text to Vector
    · System-to-Code Mapping: Embedding Pipeline
  Hybrid Search & SearchService
    · Implementation Logic
  Graph Reasoning & Topological Queries
    · Key Reasoning Queries
    · System-to-Code Mapping: Graph Ingestion
  Data Flow: NER to Neo4j Persistence

## · Agent Generation & Simulation Preparation  (L1058)
  源文件: backend/app/api/simulation.py, backend/app/services/oasis_profile_generator.py, backend/app/services/simulation_manager.py, backend/app/services/simulation_runner.py
    · Transformation Overview
    · Architecture: Preparation Lifecycle
  OASIS Profile Generator (3.1)
  Simulation Configuration Generator (3.2)
    · Data Mapping: Graph to Simulation
    · Preparation Orchestration

## · OASIS Profile Generator  (L1197)
  源文件: backend/app/services/oasis_profile_generator.py, backend/app/services/simulation_manager.py, backend/app/services/web_enrichment.py, backend/run.md
  1. Core Architecture & Data Flow
    · Profile Generation Sequence
  2. Entity Context Assembly
    · 2.1 Graph Attribute Retrieval
    · 2.2 Web Enrichment
  3. Persona Generation Logic
    · 3.1 Individual vs. Institutional Prompts
    · 3.2 Metric Grounding from Graph Topology
  4. Platform-Specific Serialization
    · Polymarket Integration
  5. Implementation Details
    · Key Functions
    · Error Handling & Retries

## · Simulation Configuration Generator  (L1341)
  源文件: backend/app/api/simulation.py, backend/app/services/oasis_profile_generator.py, backend/app/services/simulation_config_generator.py, backend/app/services/simulation_manager.py, backend/app/services/simulation_runner.py
  SimulationManager Lifecycle
    · The prepare_simulation Workflow
  SimulationConfigGenerator Implementation
    · 1. Time Configuration (`TimeSimulationConfig`)
    · 2. Platform Algorithm Weights (`PlatformConfig`)
    · 3. Event Configuration and Reality Seeds
  Reality Seeds to Code Entity Mapping
  Profile Generation and Real-time Streaming
    · Metric Grounding
    · Real-time Streaming Architecture
  Configuration Data Structures

## · Simulation Execution Engine  (L1479)
  源文件: .gitignore, backend/app/__init__.py, backend/app/services/simulation_ipc.py, backend/app/utils/file_parser.py, backend/pyproject.toml, backend/requirements.txt, backend/scripts/run_parallel_simulation.py, backend/scripts/run_reddit_simulation.py, backend/scripts/run_twitter_simulation.py, backend/uv.lock, backend/wonderwall/simulations/social_media/__init__.py, package-lock.json
  Parallel Simulation Orchestration
    · Execution Flow Diagram
  Social Platform Dynamics (Twitter & Reddit)
  Prediction Market Integration
  Belief State & Memory Management
  Inter-Process Communication (IPC)
    · System Entity Mapping

## · Parallel Simulation Runner & IPC  (L1618)
  源文件: backend/app/__init__.py, backend/app/api/simulation.py, backend/app/services/simulation_ipc.py, backend/app/services/simulation_runner.py, backend/scripts/run_parallel_simulation.py, backend/scripts/run_reddit_simulation.py, backend/scripts/run_twitter_simulation.py
  Parallel Simulation Execution
    · Execution Modes
    · Boost LLM & Rate Limiting
  Simulation IPC Protocol
    · Protocol Components
    · Supported Commands
  Subprocess Management
    · Process Lifecycle
    · Data Flow: Backend to Simulation
  Implementation Detail: SimulationRunner
    · Key Functions

## · Wonderwall Social Platform (Twitter & Reddit)  (L1737)
  源文件: .gitignore, backend/app/utils/file_parser.py, backend/pyproject.toml, backend/requirements.txt, backend/uv.lock, backend/wonderwall/simulations/base.py, backend/wonderwall/simulations/polymarket/actions.py, backend/wonderwall/simulations/polymarket/environment.py, backend/wonderwall/simulations/polymarket/prompts.py, backend/wonderwall/simulations/social_media/__init__.py, backend/wonderwall/simulations/social_media/prompts.py, backend/wonderwall/social_agent/agent_action.py
  Architectural Overview
    · Core Components
  Platform Implementation & Schema
    · Simulation Configurations
    · Social Media Data Flow
  SocialAgent & CAMEL Integration
    · Action Selection Strategy
    · Prompt Construction
  Recommendation Systems (RecSys)
    · Twhin-BERT (Twitter)
    · Reddit Algorithm
  Implementation Details: From Profile to Prompt
    · Key Functions

## · Polymarket Prediction Market Simulation  (L1892)
  源文件: backend/app/storage/neo4j_storage.py, backend/wonderwall/simulations/base.py, backend/wonderwall/simulations/polymarket/__init__.py, backend/wonderwall/simulations/polymarket/actions.py, backend/wonderwall/simulations/polymarket/environment.py, backend/wonderwall/simulations/polymarket/platform.py, backend/wonderwall/simulations/polymarket/prompts.py, backend/wonderwall/simulations/social_media/prompts.py, backend/wonderwall/social_agent/belief_state.py
  PolymarketPlatform Architecture
    · Market Mechanics and AMM
    · Data Entity Mapping
  Simulation Configuration
  Trader Agent Behavior
    · Action Selection Logic
    · Market-Media Bridge
  Execution Data Flow
  Market Resolution

## · Belief State, Round Memory & Cross-Platform Awareness  (L2024)
  源文件: backend/app/__init__.py, backend/app/services/simulation_ipc.py, backend/app/storage/neo4j_storage.py, backend/scripts/belief_integration.py, backend/scripts/run_parallel_simulation.py, backend/scripts/run_reddit_simulation.py, backend/scripts/run_twitter_simulation.py, backend/wonderwall/simulations/polymarket/__init__.py, backend/wonderwall/simulations/polymarket/platform.py, backend/wonderwall/social_agent/belief_state.py, backend/wonderwall/social_agent/round_analyzer.py
  1. Belief State Heuristic Model
    · 1.1 Core Components
    · 1.2 The Resistance Formula
    · 1.3 Data Flow: Belief Initialization to Update
  2. Round Analysis & Trajectory Tracking
    · 2.1 Key Metrics
    · 2.2 Trajectory Serialization
  3. Round Memory & Context Compaction
    · 3.1 Implementation Details
  4. Cross-Platform Awareness
    · 4.1 CrossPlatformLog Digest
    · 4.2 Injection Mechanism
  5. Market-Media Bridge
    · 5.1 Sentiment to Market
    · 5.2 Price to Social

## · Report Generation & Analysis  (L2155)
  源文件: backend/app/api/graph.py, backend/app/api/report.py, backend/app/services/graph_tools.py, backend/app/services/report_agent.py
    · System Overview
    · Conceptual Bridge: Natural Language to Code Entities
    · The ReportAgent & ReACT Loop
    · GraphToolsService: Data Retrieval
    · Report Artifacts & Accessibility

## · ReportAgent: ReACT Loop & Report Lifecycle  (L2287)
  源文件: backend/app/services/graph_tools.py, backend/app/services/report_agent.py
  Report Lifecycle Overview
    · 1. Planning Phase
    · 2. Iterative Section Generation (ReACT Loop)
    · 3. Synthesis & Post-Processing
    · 4. Artifact Persistence
  Technical Architecture: Code-to-Entity Mapping
    · Report Generation Flow
  The ReACT Implementation
    · Tool Call Constraints
    · ReACT Loop State Machine
  Data Management & Logging
    · Report Artifacts Structure
    · Logging Flow

## · GraphToolsService: Data Retrieval Tools  (L2431)
  源文件: backend/app/services/graph_builder.py, backend/app/services/graph_tools.py, backend/app/services/report_agent.py
    · Architectural Role
  1. Core Retrieval Tools
    · InsightForge (Deep Insight Retrieval)
    · PanoramaSearch & QuickSearch
    · Tool Data Structures
  2. Simulation & Market Analysis Tools
    · simulation_feed
    · market_state
    · analyze_trajectory
  3. Agent Interaction Tools
    · interview_agents
  4. Entity Mapping: Natural Language to Code
    · Diagram: Tool Dispatch Logic
    · Diagram: InsightForge Decomposition Flow
  5. Tool Summary Table

## · Frontend Application  (L2585)
  源文件: frontend/.gitignore, frontend/index.html, frontend/src/App.vue, frontend/src/api/graph.js, frontend/src/api/index.js, frontend/src/api/report.js, frontend/src/api/simulation.js, frontend/src/router/index.js, frontend/src/views/Home.vue
  Workflow Progression
  System Architecture & Routing
    · Navigation & Code Mapping
  Hyperstitions v2.0 Design System
  API Layer & Data Flow
    · API Module Responsibilities
  Detailed Area Documentation

## · Home, Routing & Design System  (L2733)
  源文件: frontend/index.html, frontend/src/App.vue, frontend/src/api/report.js, frontend/src/api/simulation.js, frontend/src/components/HistoryDatabase.vue, frontend/src/router/index.js, frontend/src/views/Home.vue
  Design System: Hyperstitions v2.0
    · Core Visual Language
  Routing Configuration
    · Route Mapping Table
  Home View: Entry & Upload
    · Implementation Details
    · Data Flow: Initialization
  History Database
    · Key Components
    · Data Fetching
    · Natural Language to Code Entity Space: Home & History
  API Layer Integration
    · Simulation Service (`simulation.js`)
    · Report Service (`report.js`)
    · System Architecture: Routing & API Flow

## · Graph Build & Environment Setup Steps (Steps 1–2)  (L2908)
  源文件: frontend/src/components/GraphPanel.vue, frontend/src/components/Step1GraphBuild.vue, frontend/src/components/Step2EnvSetup.vue, frontend/src/views/InteractionView.vue, frontend/src/views/MainView.vue
  1. MainView Layout & Orchestration
    · 1.1 Split-Panel Layout
    · 1.2 Step Navigation and Logging
  2. Step 1: Graph Construction (`Step1GraphBuild.vue`)
    · 2.1 Ontology Generation Polling
    · 2.2 Graph Build Progress
    · Data Flow: Document to Graph
  3. Step 2: Environment Setup (`Step2EnvSetup.vue`)
    · 3.1 Three-Stage Preparation
    · 3.2 Agent Persona Cards
    · 3.3 Simulation Config & Round Calculation
    · Environment Orchestration Flow
  4. Graph Visualization (`GraphPanel.vue`)
    · 4.1 Node & Edge Details
    · 4.2 Real-time Updates

## · Simulation Execution UI (Step 3)  (L3058)
  源文件: frontend/src/components/Step3Simulation.vue, frontend/src/views/SimulationRunView.vue, frontend/src/views/SimulationView.vue
  SimulationRunView Layout
    · View Modes and Layout
    · Lifecycle and Reconnection
    · Graceful Shutdown
  Step3Simulation Controls
    · Execution Lifecycle Management
    · Dual Timeline and Deduplication
    · Platform Counters and Action Icons
  Data Flow: UI to Backend IPC
    · Simulation Control Flow
  Component Communication and State
    · Key State Properties
    · Timeline Deduplication and Sorting
    · UI Action Mappings

## · Report & Interaction UI (Steps 4–5)  (L3214)
  源文件: frontend/src/components/GraphPanel.vue, frontend/src/components/Step4Report.vue, frontend/src/components/Step5Interaction.vue, frontend/src/views/InteractionView.vue, frontend/src/views/ReportView.vue
  Step 4: Report Generation
    · Report Assembly & Polling
    · Structured Result Parsing
    · Markdown Rendering Engine
    · Report Generation Flow
  Step 5: Deep Interaction
    · Interaction Modes
    · Chat State & Cache
    · World 1/2 Platform Switching
    · Interaction Entity Mapping
  Shared Layout & View Management
    · Split-Panel Architecture
    · Profile & Project Loading

## · Backend API Reference  (L3364)
  源文件: backend/app/api/__init__.py, backend/app/api/graph.py, backend/app/api/report.py, backend/app/api/simulation.py, backend/app/models/task.py, backend/app/services/simulation_runner.py
    · API Architecture Overview
    · 7.1 Graph API (`graph_bp`)
    · 7.2 Simulation API (`simulation_bp`)
    · 7.3 Report API (`report_bp`)
    · Task Lifecycle Management

## · Graph API (graph_bp)  (L3513)
  源文件: backend/app/api/graph.py, backend/app/api/report.py, backend/app/services/graph_builder.py
  Overview and Data Flow
    · System Flow: Document to Graph
  Project Management & File Ingestion
    · File Validation and Parsing
    · Project Creation Logic
  Ontology Generation
    · Implementation Detail
  Graph Building Service (GraphBuilderService)
    · Asynchronous Execution Pattern
    · Key Functions
  API Endpoint Reference
    · 1. Ontology Generation
    · 2. Build Graph
    · 3. Task Status
    · 4. Graph Data Retrieval

## · Simulation API (simulation_bp)  (L3675)
  源文件: backend/app/api/simulation.py, backend/app/services/simulation_runner.py
  Simulation Lifecycle Overview
    · System Flow: API to Simulation Runner
  Endpoint Reference
    · 1. Preparation & Configuration
    · 2. Execution Control
    · 3. Agent Interaction (Interviews)
  Key Service Classes
    · SimulationRunner
    · SimulationManager
  Data Flow: Inter-Process Communication (IPC)
  Implementation Details
    · Environment Auto-Restart
    · Prompt Optimization

## · Report API (report_bp)  (L3819)
  源文件: backend/app/api/graph.py, backend/app/api/report.py, backend/app/services/graph_tools.py, backend/app/services/report_agent.py
    · Report Generation Lifecycle
    · Core Endpoints
    · Report Agent & Tool Integration
    · File Storage & Artifact Serving

## · Infrastructure & Deployment  (L3953)
  源文件: .dockerignore, .github/workflows/docker-image.yml, Dockerfile, backend/app/utils/logger.py, backend/run.py, docker-compose.yml, frontend/package-lock.json, frontend/package.json, frontend/src/store/pendingUpload.js
  Deployment Overview
    · System Component Architecture
  Deployment Options
    · Configuration & Validation
  Containerization & CI/CD
    · Docker Architecture
  Testing & Artifacts
    · Pipeline Artifacts
  Logging & Observability
    · Child Pages

## · Docker & Production Deployment  (L4071)
  源文件: .dockerignore, .github/workflows/docker-image.yml, Dockerfile, docker-compose.yml, frontend/package-lock.json, frontend/package.json, frontend/src/store/pendingUpload.js
  Container Orchestration
    · Service Architecture
    · Dependency & Data Flow
  Application Containerization
    · Build Process Implementation
    · .dockerignore Configuration
  Environment Configuration
  CI/CD Workflow
    · Docker Image Pipeline
  Production Considerations

## · Test Fixtures & Pipeline Test Outputs  (L4221)
  源文件: backend/e2e_test_output/01_ontology.json, backend/e2e_test_output/02_graph_data.json, backend/e2e_test_output/03_simulation_created.json, backend/pipeline_test_output/03_graph_stats.json, backend/pipeline_test_output/04_profiles.json, backend/pipeline_test_output/05_simulation_config.json, backend/pipeline_test_output/06_action_analysis.json
  Purpose of Test Artifacts
  Pipeline Output Directory Structure
    · 01_ontology.json
    · 02_graph_data.json
    · 03_graph_stats.json
    · 04_profiles.json
    · 05_simulation_config.json
    · 06_action_analysis.json
  Data Flow & Entity Association
    · Natural Language to Code Entity Mapping
  Implementation Details: Simulation Persistence
    · Simulation Databases (SQLite)
    · Trajectory and Logs
  Validation Usage

## · Glossary  (L4406)
  源文件: .env.example, README.md, backend/app/__init__.py, backend/app/services/graph_tools.py, backend/app/services/oasis_profile_generator.py, backend/app/services/ontology_generator.py, backend/app/services/report_agent.py, backend/app/services/simulation_ipc.py, backend/app/services/simulation_manager.py, backend/app/storage/neo4j_storage.py, backend/app/storage/ner_extractor.py, backend/app/utils/__init__.py
  1. Knowledge Graph & Ingestion
    · Knowledge Graph Pipeline Data Flow
  2. Agent & Simulation Concepts
    · OASIS Profile
    · Belief State
    · Reality Seeds
    · Web Enrichment
  3. Simulation Execution & IPC
    · Simulation IPC (Inter-Process Communication)
    · Market-Media Bridge
    · Round Memory
  4. Analysis & Reporting
    · ReACT (Reasoning and Acting)
    · Retrieval Tools
    · Simulation IPC Flow
  5. Abbreviations & Technical Jargon