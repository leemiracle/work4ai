# Skeleton: localgpt（31 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 8KB | 3 | ~4 | 1 |
| 2 | Key Features | L236 | 14KB | 6 | ~13 | 1 |
| 3 | System Architecture | L569 | 8KB | 3 | ~2 | 6 |
| 4 | Installation & Setup | L844 | 7KB | 3 | ~1 | 5 |
| 5 | Docker Installation | L1051 | 10KB | 5 | ~4 | 5 |
| 6 | Manual Installation | L1482 | 9KB | 2 | ~7 | 2 |
| 7 | System Requirements | L1844 | 10KB | 7 | ~10 | 2 |
| 8 | Core Components | L2143 | 11KB | 6 | ~7 | 5 |
| 9 | Document Processing Pipeline | L2443 | 10KB | 6 | ~2 | 4 |
| 10 | RAG System Architecture | L2692 | 9KB | 5 | ~0 | 5 |
| 11 | Database & Storage | L2964 | 11KB | 8 | ~6 | 7 |
| 12 | Model Integration | L3287 | 12KB | 6 | ~4 | 8 |
| 13 | Configuration | L3618 | 28KB | 9 | ~28 | 1 |
| 14 | System Configuration | L4533 | 9KB | 4 | ~2 | 5 |
| 15 | Model Configuration | L4854 | 9KB | 7 | ~8 | 4 |
| 16 | Indexing Configuration | L5186 | 9KB | 5 | ~11 | 2 |
| 17 | Usage | L5425 | 11KB | 6 | ~4 | 1 |
| 18 | System Management | L5796 | 12KB | 7 | ~6 | 6 |
| 19 | Web Interface | L6205 | 15KB | 5 | ~1 | 8 |
| 20 | API Reference | L6649 | 10KB | 3 | ~18 | 5 |
| 21 | Advanced Features | L6968 | 9KB | 5 | ~2 | 1 |
| 22 | Session Management | L7259 | 12KB | 9 | ~4 | 9 |
| 23 | Index Management | L7652 | 11KB | 7 | ~2 | 6 |
| 24 | Hybrid Search & Retrieval | L7970 | 7KB | 4 | ~0 | 4 |
| 25 | Smart Routing & Verification | L8204 | 9KB | 5 | ~6 | 4 |
| 26 | Development | L8468 | 13KB | 7 | ~6 | 1 |
| 27 | Frontend Architecture | L8841 | 15KB | 9 | ~0 | 7 |
| 28 | Backend Architecture | L9247 | 14KB | 7 | ~13 | 11 |
| 29 | Testing & Development Tools | L9665 | 9KB | 5 | ~5 | 4 |
| 30 | Troubleshooting | L9921 | 11KB | 7 | ~11 | 5 |
| 31 | Performance & Optimization | L10271 | 14KB | 8 | ~5 | 2 |


## · Overview  (L6)
  源文件: README.md
  Purpose and Scope
  Core Capabilities
  System Architecture
    · High-Level Service Architecture
    · Core Components and Code Entities
  Data Flow and Processing Pipeline
    · Document Processing and RAG Pipeline
  Deployment Options
    · Configuration Management

## · Key Features  (L236)
  源文件: README.md
  Privacy & Local Processing
  Advanced Retrieval System
    · Hybrid Search Architecture
    · Late Chunking Implementation
  Smart Query Processing
    · Query Processing Flow
  Document Processing Pipeline
    · Processing Architecture
    · Contextual Enrichment Process
  Model Integration & Flexibility
    · Model Configuration Matrix
    · Pipeline Configurations
  User Interface & Developer Experience
    · Multi-Interface Architecture
    · API Capabilities
  System Architecture Features
    · Service Orchestration
    · Deployment Flexibility

## · System Architecture  (L569)
  源文件: .gitignore, README.md, backend/ollama_client.py, backend/test_ollama_connectivity.py, docker-compose.yml, docker.env
  Hardware Requirements
    · Minimum Requirements
    · Hardware Platform Support
  VRAM Requirements by Model Size
  Software Requirements
    · Python Version
    · Operating System Compatibility
    · C++ Compiler Requirements
  Installation Dependencies
    · Special Installation Considerations
  Runtime Requirements Model
  Common Hardware-Related Issues
  Docker Alternative

## · Installation & Setup  (L844)
  源文件: README.md, backend/ollama_client.py, backend/test_ollama_connectivity.py, docker-compose.yml, docker.env
  Installation Overview
    · Deployment Options
    · Service Architecture
    · Configuration and Environment Setup
  Prerequisites
    · System Requirements
    · Model Dependencies
  Quick Validation
    · Health Check System
    · Validation Commands
  Installation Method Selection

## · Docker Installation  (L1051)
  源文件: README.md, backend/ollama_client.py, backend/test_ollama_connectivity.py, docker-compose.yml, docker.env
  Overview
  Prerequisites
    · Required Software
    · Hardware Requirements
  Architecture Overview
    · Service Architecture Diagram
    · Container Dependencies
  Installation Steps
    · Step 1: Repository Setup
    · Step 2: Ollama Installation and Setup
    · Step 3: Docker Container Launch
  Service Configuration
    · Environment Variables
    · Volume Mappings
  Service Specifications
    · rag-api Service
    · rag-backend Service
    · rag-frontend Service
  Health Checks and Monitoring
    · Health Check Endpoints
    · Container Status Monitoring
  Ollama Connectivity
    · Host vs Container Ollama
    · Connectivity Testing
  Management Commands
    · Starting and Stopping
    · Service Management
    · Log Management
  Troubleshooting
    · Common Issues
    · Service Health Verification

## · Manual Installation  (L1482)
  源文件: README.md, requirements.txt
  Prerequisites
  System Dependencies
  Python Dependencies Installation
    · Key Dependencies by Category
  Node.js Dependencies Installation
  AI Model Setup
    · Ollama Installation
  System Orchestration Architecture
    · Service Architecture with Module Names
  System Orchestration with run_system.py
    · Basic System Start
    · System Management Commands
    · Service Orchestration Process
  Manual Component Startup
    · Individual Service Commands
    · Manual Startup Flow
  Environment Configuration
    · Configuration File Setup
    · Key Configuration Variables
  System Initialization and Verification
    · Database Initialization
    · Health Verification Commands
    · Validation Checklist
  Troubleshooting Manual Installation
    · Common Installation Issues
    · Log File Locations

## · System Requirements  (L1844)
  源文件: README.md, requirements.txt
  Hardware Requirements
    · Minimum System Specifications
    · Hardware Platform Support
  Software Dependencies
    · Core Runtime Requirements
    · Python Dependencies Analysis
  Platform Compatibility
    · Operating System Support
    · Container Platform Support
  Performance Considerations
    · Memory Requirements by Component
    · Performance Optimization Settings
  Database Requirements
    · Storage Backend Specifications
  Optional Components
    · Enhanced Features Dependencies
    · External Service Integration

## · Core Components  (L2143)
  源文件: Dockerfile.backend, README.md, backend/database.py, backend/server.py, rag_system/api_server.py
  Document Processing Pipeline
    · Pipeline Architecture
    · Configuration Parameters
  RAG System Architecture
    · Core RAG Components
    · Smart Routing Logic
  Database & Storage
    · Storage Architecture
    · Database Schema
    · Vector Database Integration
  Model Integration
    · Model Provider Architecture
    · Model Configuration System
    · Supported Model Types

## · Document Processing Pipeline  (L2443)
  源文件: rag_system/ingestion/chunking.py, rag_system/ingestion/docling_chunker.py, rag_system/ingestion/document_converter.py, rag_system/pipelines/indexing_pipeline.py
  Pipeline Overview
    · Document Processing Flow
  Document Conversion
    · Supported Document Formats
    · PDF Processing Strategy
  Chunking Strategies
    · DoclingChunker (Token-Aware)
    · MarkdownRecursiveChunker (Legacy)
  Embedding Generation
    · Embedding Process
  Optional Enhancements
    · Contextual Enrichment
    · Document Overview Generation
  Pipeline Orchestration
    · IndexingPipeline Class Structure
    · Processing Statistics and Monitoring

## · RAG System Architecture  (L2692)
  源文件: Dockerfile.backend, README.md, backend/database.py, backend/server.py, rag_system/api_server.py
  RAG Agent Core Architecture
  Smart Routing System
  Retrieval Pipeline Architecture
  Session and Index Management
  Data Flow Architecture

## · Database & Storage  (L2964)
  源文件: Dockerfile.backend, backend/database.py, backend/server.py, rag_system/api_server.py, rag_system/indexing/embedders.py, rag_system/indexing/latechunk.py, rag_system/indexing/representations.py
  Storage Architecture Overview
  SQLite Database System
    · Database Schema
    · Database Initialization and Location
    · Session and Message Management
    · Index Metadata Persistence
  Vector Storage System (LanceDB)
    · LanceDB Architecture
    · Vector Indexing Process
    · Database Connection Management
  File Storage System
    · File Organization Structure
    · File Upload and Storage
    · Overview File Management
  Data Flow Between Storage Systems
  Configuration and Persistence
    · Environment-Specific Paths
    · Metadata Schema Evolution

## · Model Integration  (L3287)
  源文件: README.md, backend/ollama_client.py, backend/test_ollama_connectivity.py, docker-compose.yml, docker.env, rag_system/indexing/embedders.py, rag_system/indexing/latechunk.py, rag_system/indexing/representations.py
  Ollama Integration
    · OllamaClient Architecture
    · Model Pull and Management
    · Chat Interface Features
  Embedding Models
    · Embedding Model Architecture
    · QwenEmbedder Features
    · OllamaEmbedder Integration
  Model Configuration
    · Model Selection Strategy
    · Environment Configuration
  Model Caching and Memory Management
    · Global Model Cache
    · Batch Processing and Memory Estimation
  Late Chunking Embeddings
    · Late Chunking Architecture
    · Late Chunking Benefits
  Vector Indexing and Storage
    · Vector Storage Schema

## · Configuration  (L3618)
  源文件: README.md
  Configuration Overview
  System Configuration
    · Core System Settings
    · Runtime Configuration
  Model Configuration
    · Ollama Model Configuration
    · HuggingFace Model Configuration
    · Environment Override Examples
  Pipeline Configuration
    · Default Pipeline Configuration
    · Fast Pipeline Configuration  
    · Storage Configuration
  Indexing Configuration
    · Document Processing Configuration
    · Index Building API Configuration
    · Batch Processing Configuration
    · Chunking Strategy Selection
  Search and Retrieval Configuration
    · Hybrid Search Configuration
    · Search Type Options
    · Advanced Search Features
  Storage Configuration
    · Database Configuration
    · Vector Database Settings
    · Docker Volume Configuration
    · Storage Initialization
  Performance Configuration
    · Hardware Requirements and Optimization
    · Model Performance Trade-offs
    · Pipeline Performance Settings
    · Performance Monitoring
    · Performance Tuning Guidelines
  Configuration Examples
    · Development Environment Configuration
    · Production Environment Configuration
    · High-Performance Enterprise Configuration
    · Docker Compose Configuration Examples
  Example Configurations
    · Low-End Setup (8GB VRAM GPU)
    · Mid-Range Setup (24GB VRAM GPU)
    · High-End Setup (48GB+ VRAM GPU)

## · System Configuration  (L4533)
  源文件: README.md, backend/ollama_client.py, backend/test_ollama_connectivity.py, docker-compose.yml, docker.env
  Purpose and Scope
  Types of Language Models Supported
    · Full Models
    · GGUF/GGML Quantized Models
    · GPTQ Quantized Models
    · AWQ Quantized Models
  Hardware Support Matrix
  VRAM Requirements
  Configuring Model Selection
    · Performance Configuration Parameters
  Selecting Models Based on Hardware
    · For High-End GPUs (48GB VRAM)
    · For Mid-Range GPUs (24GB VRAM)
    · For Lower-End GPUs (8-10GB VRAM)
    · For Apple Silicon (M1/M2/M3)
    · For NVIDIA GPUs (using 4-bit quantization)
  Model Loading Process
  Troubleshooting Model Selection
  Summary

## · Model Configuration  (L4854)
  源文件: README.md, rag_system/indexing/embedders.py, rag_system/indexing/latechunk.py, rag_system/indexing/representations.py
  Model Types Overview
  LLM Models (Ollama)
    · Configuration
    · Supported Models
    · Model Selection Strategy
  Embedding Models
    · HuggingFace Embedder (QwenEmbedder)
    · Ollama Embedder (OllamaEmbedder)
    · Model Selection Function
  Late Chunking Models
    · Architecture
  Reranker Models
    · Supported Models
    · Configuration
  Model Caching and Memory Management
    · Global Model Cache
    · Device Selection Priority
    · Error Handling
  Environment Configuration
    · Required Environment Variables
    · Pipeline-Specific Configuration

## · Indexing Configuration  (L5186)
  源文件: rag_system/pipelines/indexing_pipeline.py, src/components/IndexForm.tsx
  Configuration Overview
  IndexForm Configuration Flow
  Document Processing Configuration
    · File Upload Settings
    · Chunking Configuration
  Retrieval Mode Configuration
  Advanced Features Configuration
    · Late Chunking
    · Contextual Enrichment
  Model Configuration
    · Embedding Models
    · LLM Model Configuration
  Batch Processing Configuration
  Storage Configuration
  Complete Configuration Schema

## · Usage  (L5425)
  源文件: README.md
  Overview of Usage Options
  System Management
    · Basic System Startup
    · System Management Commands
    · System Health Monitoring
    · Production Deployment
  Web Interface
    · Accessing the Web Interface
    · Web Interface Architecture
    · Core Web Interface Features
    · Web Interface Workflow
  Streamlit Interface Usage
    · Starting the Streamlit Interface
    · Streamlit Interface Features
  Using Chat History
  Viewing Source Documents
  Saving Question and Answer Pairs
  Usage with Different Hardware
  Advanced Usage Pipeline
  Typical Usage Workflow

## · System Management  (L5796)
  源文件: README.md, run_system.py, src/components/ui/conversation-page.tsx, src/components/ui/session-chat.tsx, src/utils/textNormalization.ts, test_markdown_streaming.js
  Overview
  Basic Usage
    · Starting the System
    · Monitoring and Health Checking
  Service Configuration and Management
    · Service Definitions
    · Service Lifecycle Management
  Logging and Monitoring
    · Log Aggregation System
    · Health Check System
  Process Management
    · Graceful Shutdown
    · Prerequisites Checking
  Command Line Interface
    · Available Arguments
  Integration with Other Components
    · Frontend Integration
    · Service Dependencies

## · Web Interface  (L6205)
  源文件: run_system.py, src/components/IndexForm.tsx, src/components/ui/chat-input.tsx, src/components/ui/conversation-page.tsx, src/components/ui/empty-chat-state.tsx, src/components/ui/session-chat.tsx, src/utils/textNormalization.ts, test_markdown_streaming.js
  Overview
  Component Architecture
    · Frontend Component Hierarchy
    · System Integration Flow
  Core Components
    · SessionChat Component
    · ChatInput Component  
    · IndexForm Component
  User Interface Features
    · Real-time Streaming Responses
    · Advanced Configuration Settings
    · Document Index Management
  User Interaction Flows
    · Chat Interaction Flow
    · File Upload and Indexing Flow
    · Index Creation and Configuration Flow
  Text Processing and Display
    · Streaming Response Normalization
    · Conversation Display Features
  6. Starting and Configuring the Web Interface
    · 6.1 Starting the API Server
    · 6.2 Starting the Web UI Server
    · 6.3 Configuration Options
  7. Internal Implementation Details
    · 7.1 API Server Implementation
    · 7.2 Web UI Implementation
    · 7.3 Front-end Implementation

## · API Reference  (L6649)
  源文件: Dockerfile.backend, README.md, backend/database.py, backend/server.py, rag_system/api_server.py
  API Architecture Overview
  Backend API Server (Port 8000)
    · Session Management
    · Chat Operations
    · File and Document Management
    · Index Management
    · System Operations
  RAG API Server (Port 8001)
    · Chat Processing
    · Document Indexing
    · Model Discovery
  Request Flow Architecture
  Error Handling and CORS
  Database Integration

## · Advanced Features  (L6968)
  源文件: README.md
  Purpose and Scope
  Chat History
    · Overview
    · Technical Implementation
    · Enabling Chat History
  Source Citation
    · Overview
    · Technical Implementation
    · Enabling Source Citation
  Q&A Logging
    · Overview
    · Technical Implementation
    · Enabling Q&A Logging
  API Usage
    · Overview
    · Technical Implementation
    · Using the API
    · Web UI
  Combining Advanced Features
  Feature Comparison
  Summary

## · Session Management  (L7259)
  源文件: Dockerfile.backend, backend/database.py, backend/server.py, rag_system/api_server.py, run_system.py, src/components/ui/conversation-page.tsx, src/components/ui/session-chat.tsx, src/utils/textNormalization.ts, test_markdown_streaming.js
  Overview
  Database Schema
  Session Lifecycle Management
    · Session Creation
    · Message Storage
    · Session Cleanup
  API Integration
    · REST Endpoints
    · Smart Routing Integration
  Document and Index Association
    · Session-Document Linking
    · Session-Index Linking  
  Frontend Session Management
    · SessionChat Component
    · Session State Management
  Message Metadata and Context
    · Message Structure
    · Conversation History Format
  Performance and Optimization
    · Database Indexing
    · Memory Management

## · Index Management  (L7652)
  源文件: Dockerfile.backend, backend/database.py, backend/server.py, rag_system/api_server.py, src/components/IndexForm.tsx, src/components/IndexWizard.tsx
  Index Lifecycle Overview
  Database Schema
  Configuration Options
  API Workflow
  Index Building Process
  Metadata Management
  Session Integration

## · Hybrid Search & Retrieval  (L7970)
  源文件: README.md, rag_system/indexing/embedders.py, rag_system/indexing/latechunk.py, rag_system/indexing/representations.py
  Overview
  Purpose of Source Citation
  How Source Citation Works
  Enabling Source Citation
    · Command Line Interface
    · Web API
  Source Document Structure
  Source Display Implementation
    · Command Line Interface
    · API Interface
  Technical Implementation
  Code Details
  Best Practices
  Limitations
  Summary

## · Smart Routing & Verification  (L8204)
  源文件: README.md, backend/simple_pdf_processor.py, backend/test_backend.py, rag_system/agent/verifier.py
  Overview
  Smart Routing System
    · Triage Decision Flow
    · Implementation Architecture
  Answer Verification System
    · VerificationResult Class
    · Verification Process
    · Verification Prompt Structure
  Query Decomposition Integration
    · Decomposition Decision Logic
    · Configuration Parameters
  System Integration
    · Async Processing Architecture
    · Cache Integration

## · Development  (L8468)
  源文件: requirements.txt
  7.1 Frontend Architecture
    · Core Frontend Components
    · Frontend Service Integration
    · State Management Patterns
  7.2 Backend Architecture
    · Service Architecture Overview
    · Core Backend Classes and Responsibilities
    · Database Schema and Storage
    · API Endpoint Structure
  7.3 Testing & Development Tools
    · Development Environment Setup
    · Development Dependencies and Tools
    · Testing and Debugging Utilities
    · Development Environment Configuration
    · Performance Monitoring and Debugging
  Architecture for Contributors
    · Key Extension Points
  Testing Guidelines
  License and Legal Considerations
  Getting Help

## · Frontend Architecture  (L8841)
  源文件: run_system.py, src/components/IndexForm.tsx, src/components/ui/chat-input.tsx, src/components/ui/conversation-page.tsx, src/components/ui/session-chat.tsx, src/utils/textNormalization.ts, test_markdown_streaming.js
  Architecture Overview
  Core Components
    · SessionChat Component
    · IndexForm Component
    · ChatInput Component
    · ConversationPage Component
  State Management Pattern
  API Communication
    · REST API Pattern
    · Streaming Communication
  Text Processing Pipeline

## · Backend Architecture  (L9247)
  源文件: Dockerfile.backend, backend/database.py, backend/ollama_client.py, backend/server.py, backend/simple_pdf_processor.py, backend/test_backend.py, backend/test_ollama_connectivity.py, docker-compose.yml, docker.env, rag_system/agent/verifier.py, rag_system/api_server.py
  Service Architecture Overview
  Core Backend Services
    · Main Backend Server (ChatHandler)
    · RAG API Server (AdvancedRagApiHandler)
  Database Schema and Storage
    · SQLite Database Schema
    · Database Operations
  API Layer and Routing
    · REST API Endpoints
    · Smart Query Routing Logic
  Service Integration and Communication
    · Inter-Service Communication
    · Ollama Client Integration
  Deployment Architecture
    · Docker Multi-Service Setup
    · Environment Configuration

## · Testing & Development Tools  (L9665)
  源文件: backend/simple_pdf_processor.py, backend/test_backend.py, rag_system/agent/verifier.py, src/test-upload.html
  Backend Testing Infrastructure
    · Test Backend Script
    · Health Check Validation
    · Chat Functionality Testing
  Frontend Testing Tools
    · Manual File Upload Testing
  Document Processing Testing
    · Simple PDF Processor
  Verification and Validation Tools
    · Answer Verification System
  Development Utilities
    · Global Service Initialization
    · Logging and Debugging
    · Test Execution Patterns

## · Troubleshooting  (L9921)
  源文件: README.md, backend/ollama_client.py, backend/test_ollama_connectivity.py, docker-compose.yml, docker.env
  System Health Diagnostics
    · Health Check Architecture
    · Running System Diagnostics
  Service Connectivity Issues
    · Port and Service Mapping
    · Service Dependency Chain
    · Common Connectivity Problems
  Ollama Server Issues
    · Ollama Connectivity Testing
    · Model Management Issues
    · Docker Ollama Configuration
  Database and Storage Issues
    · Database Architecture
    · Database Recovery
  Performance Issues
    · Memory and Resource Monitoring
    · Pipeline Performance Tuning
  Log Analysis and Debugging
    · Log File Structure
    · Health Check Commands Summary

## · Performance & Optimization  (L10271)
  源文件: README.md, rag_system/pipelines/indexing_pipeline.py
  System Performance Architecture
    · Service Performance Topology
    · Resource Allocation Strategy
  Processing Pipeline Optimization
    · Batch Processing Configuration
    · Chunking Strategy Performance
  Memory Management
    · Memory Usage Estimation
    · Pipeline Configuration Optimization
  Storage Optimization
    · Vector Database Performance
  Model Optimization
    · Multi-Model Performance Strategy
    · Model Loading and Caching
  Network and Deployment Optimization
    · Service Communication Optimization
    · Docker Performance Configuration
  Monitoring and Profiling
    · Progress Tracking and Timing
  Configuration Tuning
    · Environment-Specific Optimization
    · Hardware-Specific Tuning
  Performance Monitoring Commands
    · System Health Checking
    · Performance Profiling Endpoints