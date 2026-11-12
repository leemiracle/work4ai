# Skeleton: second-brain-agent（21 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 14KB | 3 | ~11 | 2 |
| 2 | Data Processing Pipeline | L384 | 14KB | 5 | ~4 | 3 |
| 3 | Markdown and Content Extraction | L726 | 10KB | 4 | ~5 | 2 |
| 4 | Text Chunking and Vectorization | L955 | 10KB | 6 | ~4 | 2 |
| 5 | File System Monitoring | L1239 | 16KB | 7 | ~5 | 4 |
| 6 | Agent and Intelligence Layer | L1740 | 10KB | 4 | ~3 | 3 |
| 7 | Core Agent System | L2018 | 9KB | 3 | ~3 | 3 |
| 8 | Intent Classification and Extraction | L2299 | 17KB | 12 | ~14 | 3 |
| 9 | User Interfaces | L2881 | 6KB | 2 | ~4 | 4 |
| 10 | Web Interface | L3031 | 11KB | 3 | ~6 | 2 |
| 11 | MCP Protocol Server | L3308 | 16KB | 9 | ~11 | 4 |
| 12 | Command Line Tools | L3776 | 9KB | 5 | ~3 | 4 |
| 13 | Infrastructure and Deployment | L4078 | 9KB | 5 | ~8 | 4 |
| 14 | Vector Database Setup | L4359 | 8KB | 5 | ~2 | 3 |
| 15 | System Services | L4607 | 14KB | 6 | ~16 | 4 |
| 16 | Configuration Management | L4986 | 14KB | 5 | ~5 | 3 |
| 17 | Development Environment | L5466 | 9KB | 2 | ~5 | 3 |
| 18 | Project Dependencies | L5775 | 20KB | 6 | ~5 | 2 |
| 19 | Code Quality and Testing | L6456 | 12KB | 4 | ~5 | 4 |
| 20 | CI/CD Pipeline | L6901 | 19KB | 7 | ~8 | 3 |
| 21 | Appendix | L7365 | 6KB | 3 | ~6 | 1 |


## · Overview  (L6)
  源文件: README.md, pyproject.toml
  Purpose and Scope
  System Purpose
    · Core Capabilities
  System Architecture
  Data Flow Pipeline
  Query Processing Architecture
    · Query Types and Processing Chains
    · Intent Classification Flow
  Key Features
    · Multi-Source Content Ingestion
    · Domain-Based Organization
    · MCP Protocol Server
  Technology Stack
    · Core Dependencies
    · Dependency Management
  Runtime Infrastructure
    · Background Services (systemd)
    · Database Container
  System Requirements
    · Installation Prerequisites
    · API Keys Required
  Getting Started
    · Basic Usage Flow
    · Example Commands

## · Data Processing Pipeline  (L384)
  源文件: README.md, transform_md.py, transform_txt.py
  Architecture Overview
  Pipeline Stages
    · Stage 1: Content Extraction (transform_md.py)
    · Stage 2: Text Chunking and Vectorization (transform_txt.py)
  File System Monitoring and Orchestration
  Data Flow and Transformations
    · Metadata Standardization
  Output Format and Storage Structure
    · JSON Document Format
  Error Handling and Resilience

## · Markdown and Content Extraction  (L726)
  源文件: lib.py, transform_md.py
  System Role and Data Flow
    · Diagram: Content Extraction Pipeline and Code Entities
  Content Type Extraction and Routing
    · Diagram: Content Type Routing to Code Entities
  YouTube Video Extraction Logic
    · Diagram: YouTube Extraction Sequence
  History File Splitting and Temporal Organization
    · Diagram: History Splitting Logic and Code Entities
  Metadata Extraction and JSON Serialization
  Error Handling and Optimization

## · Text Chunking and Vectorization  (L955)
  源文件: lib.py, transform_txt.py
  Purpose and Scope
  System Overview
    · Processing Pipeline Flow
  Text Chunking Process
    · Chunking Configuration
    · Text Splitter Implementation
  Chunk Processing and File Management
    · Chunk File Creation
    · Metadata Enhancement
  Vectorization and Database Storage
    · Vector Storage Process
    · Embedding Model Configuration
  File Validation and Processing Logic
    · File Validation Pipeline
    · Datetime Handling
  Entry Points and Integration
    · Main Processing Modes
    · System Integration Points

## · File System Monitoring  (L1239)
  源文件: install-systemd-services.sh, monitor.sh, sba-md-service.sh, sba-txt-service.sh
  Purpose and Scope
  Architecture Overview
    · Monitoring Architecture
  Core Monitoring Script
    · Script Arguments and Validation
    · Virtual Environment Management
    · Two-Phase Processing Model
    · Event Stream Processing
  Service Wrappers
    · Markdown Service Wrapper (sba-md-service.sh)
    · Text Service Wrapper (sba-txt-service.sh)
  Event Processing Flow
    · Complete Event Flow
    · Event Types and Handling
  Integration with Processing Pipeline
    · Pipeline Integration Points
    · Cascading Pipeline Behavior
  Systemd Service Integration
    · Service Installation Process
    · Service Configuration
  Summary

## · Agent and Intelligence Layer  (L1740)
  源文件: extractors.py, lib.py, qa.py
  Architecture Overview
    · Agent Intelligence Architecture
    · Intelligence Processing Flow
  Core Intelligence Components
    · Agent Class Implementation
    · Query Processing Methods
    · Intent-Based Query Routing
  Intent Classification System
    · Available Extractors
    · Intent Classification Implementation
    · Temporal Query Processing
  Vector Store Integration
    · Vector Store Configuration
    · Metadata Filtering for Activity Reports
  Utility Functions and Supporting Infrastructure
    · Text Processing Utilities
    · Response Formatting

## · Core Agent System  (L2018)
  源文件: example.env, lib.py, test_lib.py
  Purpose and Scope
  Agent Architecture Overview
  Core Agent Class Structure
  Question Processing Flow
  Intent-Based Query Routing
    · Regular Questions
    · Activity Report Requests  
  Vector Database Integration
    · Connection Management
    · Embedding Configuration
  Response Formatting and Source Attribution
    · Text Format Response
    · HTML Format Response  
    · Source URL Resolution
  Supporting Utilities
    · Document Organization Integration
    · Text Cleanup Utilities

## · Intent Classification and Extraction  (L2299)
  源文件: extractors.py, lib.py, qa.py
  Purpose and Scope
  Architecture Overview
  Intent Classification
    · Intent Pydantic Model
    · Implementation Details
    · Agent Integration
  Period Extraction
    · Period Pydantic Model
    · Temporal Context Handling
    · Activity Report Integration
  Document Extraction
    · Documents Pydantic Model
    · Document Description Integration
    · Filter Construction for Multiple Documents
  Step-back Prompting
    · Few-Shot Prompt Architecture
    · Prompt Template Structure
    · Implementation Details
    · Regular Question Integration
  Sentence Rephrasing (Temporal Removal)
    · Sentence Pydantic Model
    · Implementation Details
  Common Patterns and Design
    · Shared Components
    · Error Handling
    · Debug Mode
  LLM Configuration
  Integration Summary

## · User Interfaces  (L2881)
  源文件: README.md, mcp-server.sh, mcp_server.py, second_brain_agent.py
  Purpose and Scope
  Interface Architecture Overview
    · Interface Types
  System Interface Architecture
  User Interaction Flow
  Interface Capabilities Matrix
  Interface Implementation Details
    · Session Management
    · Input Processing
    · Output Formatting

## · Web Interface  (L3031)
  源文件: lib.py, second_brain_agent.py
  Architecture Overview
    · Core Components Architecture
    · User Interaction Flow
  Core Implementation
    · Main Application Function
    · Question Processing Pipeline
  HTML Templating System
    · Template Structure
    · Chat Message Styling
  Browser Integration and Security
    · Auto-Focus JavaScript
    · Email Sanitization
  Configuration and Environment

## · MCP Protocol Server  (L3308)
  源文件: lib.py, mcp-server.sh, mcp_server.py, test_mcp_server.py
  Architecture Overview
  MCP Tools Implementation
    · search_documents Tool
    · get_document_count Tool
    · get_domains Tool
    · get_recent_documents Tool
  Filtering Capabilities
    · Metadata Filtering
    · Content Filtering
  Document Metadata Schema
  Configuration and Deployment
    · Environment Configuration
    · Deployment Script
    · Server Execution
  Integration with Vector Database

## · Command Line Tools  (L3776)
  源文件: extractors.py, lib.py, qa.py, similarity.py
  Overview
  Command Line Tool Architecture
  Similarity Search Tool
    · Basic Usage
    · Filter System
    · Search Results
  Question Answering Tool
    · Implementation
    · Usage Examples
  Smart Connections Tool
    · Connection Discovery Algorithm
    · Key Functions
    · Output Format
  Usage Patterns and Integration
    · Development Workflow Integration
    · Environment Configuration
    · Error Handling and Debugging

## · Infrastructure and Deployment  (L4078)
  源文件: README.md, compose.yaml, install-systemd-services.sh, sba-md-service.sh
  Deployment Architecture
  Vector Database Setup
    · ChromaDB Container Configuration
    · Database Deployment Commands
  System Services Configuration
    · Service Architecture
    · Service Installation Process
    · Service Management Commands
  Configuration Management
    · Environment Variable Architecture
    · Required Environment Variables
    · Directory Structure Creation
  Deployment Verification
    · Service Health Checks

## · Vector Database Setup  (L4359)
  源文件: .github/workflows/pr.yml, Makefile, compose.yaml
  Purpose and Scope
  Docker Compose Configuration
    · Container Architecture
    · Service Configuration
    · Network Configuration
  Version Synchronization
    · Makefile Version Extraction
  Data Storage and Persistence
    · Volume Mounting Strategy
  Client Integration
    · HTTP API Access
  Administrative and Development Features
    · Reset Capability
    · Persistence Configuration

## · System Services  (L4607)
  源文件: install-systemd-services.sh, monitor.sh, sba-md-service.sh, sba-txt-service.sh
  Service Architecture Overview
    · Service Architecture Diagram
  Monitoring Mechanism
    · monitor.sh Architecture
  Service Components
    · sba-md.service
    · sba-txt.service
  Service Installation and Management
    · Installation Process
  Service Management Commands
    · Systemctl Operations
    · Service Dependencies
    · Service Interaction Flow

## · Configuration Management  (L4986)
  源文件: README.md, example.env, test_lib.py
  Purpose and Scope
  Overview
  Environment File Structure
    · Template File
    · Setup Process
  API Key Configuration
    · OpenAI API Key
    · HuggingFace API Token
    · AssemblyAI API Key
  Directory Path Configuration
    · SRCDIR - Source Directory
    · DSTDIR - Destination Directory
  Optional Configuration
    · SBA_ORG_DOC - Organization Document
  Configuration Loading Mechanism
    · Loading Pattern
    · Environment Variable Precedence
  Integration with System Components
  Configuration Validation
    · Missing Required Variables
    · Invalid Directory Paths
    · Invalid API Keys
    · Best Practices
  Example Configuration

## · Development Environment  (L5466)
  源文件: .pre-commit-config.yaml, README.md, pyproject.toml
  Purpose and Scope
  Overview
  Development Environment Architecture
  Python Version Requirements
  Environment Configuration
  Development Workflow
  Quick Start
    · Initial Setup
    · Development Setup
    · Running Tests
  Development Tools Summary
  System Requirements
  Related Documentation

## · Project Dependencies  (L5775)
  源文件: poetry.lock, pyproject.toml
  Overview
  Poetry Dependency Management Architecture
  Dependency Groups Configuration
    · Main Dependencies (Runtime)
    · Test Dependencies
    · Development Dependencies
  Technology Stack Layers
  Version Constraints and Pinning
    · Critical Version Constraints
  Lock File Structure and Versioning
    · ChromaDB Lock Example
  Transitive Dependency Resolution
  Core Technology Stack Detail
    · LangChain Integration Packages
    · Document Processing Stack
    · AI Service Dependencies
  Build System and Metadata
  Test Configuration
  Dependency Installation Workflows
  Version Synchronization with Docker
  Dependency Vulnerabilities and Updates
  Summary

## · Code Quality and Testing  (L6456)
  源文件: .pre-commit-config.yaml, example.env, integration-test.sh, test_lib.py
  Code Quality Framework
    · Pre-commit Hook Pipeline
    · Custom Quality Hooks
  Testing Strategy
    · Test Classification
    · Unit Testing Framework
    · Integration Testing Framework
  Integration Testing Pipeline
    · Integration Test Workflow
    · Test Environment Setup
    · Document Processing Validation
    · Document Lifecycle Testing
  MCP Server Testing
    · MCP Test Architecture
    · MCP Tool Testing
    · Test Result Parsing
  Testing Infrastructure Requirements
    · System Dependencies
    · Container Management
    · Test Isolation

## · CI/CD Pipeline  (L6901)
  源文件: .github/workflows/pr.yml, Makefile, integration-test.sh
  Pipeline Overview
    · CI/CD Architecture
  Pull Request Workflow
    · Job Configuration
    · Test Execution Pipeline
  Build and Dependency Management
    · Automated Version Synchronization
    · Makefile Dependency Chain
    · Version Extraction Process
  Integration Testing
    · Integration Test Architecture
    · Test Phases
  References
  Links
    · Test Environment Configuration
  Dependency Validation System
    · Dependent PR Management
    · Two-Phase Dependency Validation
  Workflow Triggers and Events
    · Trigger Configuration

## · Appendix  (L7365)
  源文件: .gitignore
  Licensing
    · License Summary
  Project Structure Overview
    · Project File Organization
  Configuration and Metadata Files
    · Git Configuration
    · Dependency Management
  System Entry Points and Utilities
    · Code Entry Points Mapping
  File Patterns and Exclusions
    · Generated and Temporary Files
  Legal and Compliance Information
    · GPL-3.0 License Compliance
    · Third-Party Dependencies