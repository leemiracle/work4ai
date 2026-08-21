# Skeleton: haystack（27 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Haystack Overview | L6 | 11KB | 2 | ~2 | 22 |
| 2 | Project Infrastructure | L214 | 10KB | 2 | ~1 | 31 |
| 3 | Installation and Dependencies | L469 | 14KB | 4 | ~2 | 23 |
| 4 | Testing and Contribution Workflow | L844 | 14KB | 2 | ~4 | 38 |
| 5 | CI/CD and Release Management | L1160 | 11KB | 2 | ~2 | 33 |
| 6 | Core Architecture | L1348 | 18KB | 7 | ~7 | 25 |
| 7 | Component System | L1810 | 14KB | 5 | ~5 | 23 |
| 8 | Pipeline System | L2072 | 18KB | 2 | ~5 | 24 |
| 9 | Core Module and Data Structures | L2425 | 22KB | 4 | ~8 | 31 |
| 10 | Observability and Tracing | L2768 | 7KB | 2 | ~0 | 18 |
| 11 | LLM Integration | L2913 | 16KB | 4 | ~2 | 20 |
| 12 | OpenAI and Azure Integration | L3186 | 20KB | 3 | ~7 | 17 |
| 13 | Hugging Face API Integration | L3469 | 9KB | 3 | ~10 | 12 |
| 14 | Hugging Face Local Integration | L3686 | 9KB | 3 | ~2 | 12 |
| 15 | Chat Messages and Prompt Building | L3914 | 16KB | 4 | ~3 | 20 |
| 16 | Document Processing | L4219 | 11KB | 2 | ~1 | 22 |
| 17 | Document Stores | L4421 | 22KB | 3 | ~8 | 17 |
| 18 | Document Converters | L4752 | 20KB | 2 | ~6 | 28 |
| 19 | Embedders and Rankers | L5050 | 12KB | 2 | ~3 | 23 |
| 20 | Document Preprocessing and Retrieval | L5248 | 19KB | 2 | ~5 | 25 |
| 21 | Advanced Features | L5476 | 11KB | 2 | ~0 | 26 |
| 22 | Agent System | L5691 | 12KB | 3 | ~2 | 28 |
| 23 | Tool Invocation | L5895 | 12KB | 2 | ~2 | 27 |
| 24 | Human-in-the-Loop and Context Management | L6087 | 10KB | 2 | ~2 | 27 |
| 25 | Evaluation Components | L6275 | 11KB | 2 | ~2 | 24 |
| 26 | Migration Guide (v2.x to v3.0) | L6475 | 12KB | 2 | ~8 | 26 |
| 27 | Glossary | L6672 | 20KB | 2 | ~2 | 35 |


## · Haystack Overview  (L6)
  源文件: .gitignore, AGENTS.md, CLAUDE.md, docs-website/docs/concepts/components.mdx, docs-website/docs/document-stores/oracledocumentstore.mdx, docs-website/docs/document-stores/supabasedocumentstore.mdx, docs-website/docs/optimization/advanced-rag-techniques/hypothetical-document-embeddings-hyde.mdx, docs-website/docs/overview/get-started.mdx, docs-website/docs/overview/migration.mdx, docs-website/docs/pipeline-components/retrievers.mdx, docs-website/docs/pipeline-components/retrievers/pgvectorembeddingretriever.mdx, docs-website/docs/pipeline-components/retrievers/sqlalchemytableretriever.mdx
  Purpose and Scope
  What is Haystack?
  Key Capabilities
  High-Level Architecture
    · Architectural Layers and Code Entities
  v3.0 Major Release Changes
    · 1. Integration Decoupling
    · 2. Generator Consolidation
    · 3. Agent and Tool Invocation
    · 4. Pipeline Convergence
  Core Concepts
    · Components
    · Pipelines
    · Data Models
  Code Entity Mapping
  Development Infrastructure

## · Project Infrastructure  (L214)
  源文件: .github/dependabot.yml, .github/pull_request_template.md, .github/workflows/codeql.yml, .github/workflows/docker_release.yml, .github/workflows/docs-website-test-docs-snippets.yml, .github/workflows/docstring_labeler.yml, .github/workflows/docusaurus_sync.yml, .github/workflows/e2e.yml, .github/workflows/github_release.yml, .github/workflows/license_compliance.yml, .github/workflows/nightly_testpypi_release.yml, .github/workflows/promote_unstable_docs.yml
  Purpose and Scope
  Build System and Package Management
    · Project Configuration
    · Version Management
  Environment Management
    · Environment Definitions
    · Environment Configuration
    · Hatch Scripts
  Dependency Management
    · Core Dependencies
    · Development and Test Dependencies
    · Installation Methods
  Testing Framework
    · Test Categories and Markers
    · Test Fixtures
  Code Quality and CI/CD
    · Code Quality Tools
    · CI/CD Pipeline
    · Release Automation

## · Installation and Dependencies  (L469)
  源文件: .github/pull_request_template.md, .github/workflows/docs-website-test-docs-snippets.yml, .github/workflows/docstring_labeler.yml, .github/workflows/docusaurus_sync.yml, .github/workflows/e2e.yml, .github/workflows/license_compliance.yml, .github/workflows/nightly_testpypi_release.yml, .github/workflows/promote_unstable_docs.yml, .github/workflows/push_release_notes_to_website.yml, .github/workflows/pypi_release.yml, .github/workflows/release_notes.yml, .github/workflows/slow.yml
  Purpose and Scope
  Installation Methods
    · End-User Installation
    · Development Installation
  Python Version Requirements
  Dependency Management with Hatch
    · Environment Scripts
  Core Dependencies
  Development Dependencies
    · Test Environment
  CI/CD Environment Configuration
  Package Build and Distribution

## · Testing and Contribution Workflow  (L844)
  源文件: .clusterfuzzlite/Dockerfile, .clusterfuzzlite/build.sh, .clusterfuzzlite/project.yaml, .github/labeler.yml, .github/pull_request_template.md, .github/workflows/cflite_pr.yml, .github/workflows/docs-website-test-docs-snippets.yml, .github/workflows/docstring_labeler.yml, .github/workflows/docusaurus_sync.yml, .github/workflows/e2e.yml, .github/workflows/labeler.yml, .github/workflows/license_compliance.yml
  Purpose and Scope
  Development Environment Setup
    · Installing Hatch
    · Cloning and Environment Setup
    · Pre-commit Hooks
  Test Infrastructure
    · Hatch Test Environments
    · Hatch Scripts for Testing
    · Pytest Configuration and Fixtures
  Running Tests Locally
    · Unit and Integration Tests
    · Slow Integration Tests
  Fuzz Testing
  Code Quality Standards
    · Ruff (Formatting and Linting)
    · Mypy (Type Checking)
  Contribution Workflow
    · Pull Request Requirements
    · Release Note Validation
  CI/CD Pipeline Architecture

## · CI/CD and Release Management  (L1160)
  源文件: .github/dependabot.yml, .github/utils/create_unstable_docs_docusaurus.py, .github/utils/parse_validate_version.sh, .github/utils/prepare_release_notification.sh, .github/utils/promote_unstable_docs_docusaurus.py, .github/utils/wait_for_platform_pr.sh, .github/utils/wait_for_workflows.sh, .github/workflows/branch_off.yml, .github/workflows/check_api_ref.yml, .github/workflows/codeql.yml, .github/workflows/docker_release.yml, .github/workflows/docs_search_sync.yml
  CI/CD Pipeline Architecture
    · Workflow Orchestration and Triggers
    · Key Workflow Components
  Release Management
    · The Release Lifecycle
    · Versioning Logic
  Docker Image Management
    · Image Build Process
  Documentation Website Management
    · Documentation Structure and Versioning
    · Search Integration
  Release Notes (Reno)
    · Automated Note Generation

## · Core Architecture  (L1348)
  源文件: haystack/core/component/component.py, haystack/core/component/sockets.py, haystack/core/component/types.py, haystack/core/errors.py, haystack/core/pipeline/base.py, haystack/core/pipeline/breakpoint.py, haystack/core/pipeline/component_checks.py, haystack/core/pipeline/descriptions.py, haystack/core/pipeline/pipeline.py, haystack/core/pipeline/utils.py, haystack/dataclasses/breakpoints.py, releasenotes/notes/allow-break-point-with-pipeline-snapshot-686cbbecc7ca0ae3.yaml
  Purpose and Scope
  Architecture Overview
  Component Abstraction
    · Component Contract
    · Component Instance Attributes
  Pipeline Orchestration
    · Pipeline Graph Structure
    · Adding Components and Connections
    · Pipeline Variants
  Socket-Based I/O System
    · Socket Types
    · Variadic Inputs
  Execution Model
    · Component Priorities
    · Execution Flow (Synchronous Pipeline)
    · Async Execution Flow
  Error Handling and Recovery
    · Runtime Error Handling
    · Breakpoints and Snapshots
  Serialization and Persistence
    · Serialization API
    · Component Registry

## · Component System  (L1810)
  源文件: haystack/core/__init__.py, haystack/core/component/component.py, haystack/core/component/sockets.py, haystack/core/component/types.py, haystack/core/pipeline/descriptions.py, haystack/core/super_component/__init__.py, haystack/core/super_component/super_component.py, haystack/core/super_component/utils.py, haystack/tools/pipeline_tool.py, releasenotes/notes/add-pipeline-viz-to-supercomponent-80165756cc777056.yaml, releasenotes/notes/allow-non-leaf-outputs-in-supercomponents-outputs-adf29d68636c23ba.yaml, releasenotes/notes/async-component-support-machinery-6ea4496241aeb3b2.yaml
  Component Declaration
    · Required Methods
  Component Lifecycle
    · Initialization Phase
    · Warm-up Phase
  Input/Output Socket System
    · Input Socket Creation
    · Output Socket Creation
    · Socket Management
  SuperComponent Wrapper
  Advanced Features
    · Asynchronous Component Support
    · Component Pre-initialization Hooks
    · Error Handling and Validation

## · Pipeline System  (L2072)
  源文件: haystack/components/retrievers/multi_query_embedding_retriever.py, haystack/components/retrievers/multi_query_text_retriever.py, haystack/components/retrievers/multi_retriever.py, haystack/components/retrievers/text_embedding_retriever.py, haystack/core/errors.py, haystack/core/pipeline/base.py, haystack/core/pipeline/breakpoint.py, haystack/core/pipeline/component_checks.py, haystack/core/pipeline/draw.py, haystack/core/pipeline/pipeline.py, haystack/core/pipeline/utils.py, haystack/core/serialization.py
  Purpose and Scope
  Pipeline Architecture Overview
    · Core Class Hierarchy
  Core Classes
    · PipelineBase
    · Pipeline (Synchronous)
    · AsyncPipeline (Asynchronous)
  Execution Model
    · Component Priority System
    · Scheduling Algorithm
  Component Execution Flow
    · Synchronous Pipeline Execution
    · AsyncPipeline Concurrent Execution
  Component State and Data Flow
    · Input State Management
    · Component Visit Tracking
  Error Handling
    · PipelineRuntimeError
    · Error Propagation and Snapshots
  Breakpoints and Debugging
    · Breakpoint Types
    · PipelineSnapshot Structure
    · Resuming from Snapshot
  Pipeline Construction
    · Adding Components
    · Connecting Components
  Serialization
    · Dictionary Format
    · Deserialization Callbacks

## · Core Module and Data Structures  (L2425)
  源文件: docs-website/docs/token-counters.mdx, docs-website/docs/token-counters/approximatetokencounter.mdx, docs-website/docs/token-counters/openaitokencounter.mdx, docs-website/docs/token-counters/tiktokencounter.mdx, haystack/components/agents/tool_calling.py, haystack/components/builders/answer_builder.py, haystack/components/builders/chat_prompt_builder.py, haystack/components/builders/prompt_builder.py, haystack/components/converters/output_adapter.py, haystack/components/routers/conditional_router.py, haystack/core/serialization_security.py, haystack/core/type_utils.py
  Purpose and Scope
  Module Initialization and Exports
    · Exported Symbols
    · Initialization Sequence
  Document Dataclass
    · Document Structure
  ChatMessage and Multi-modal Content
    · Content Types (ChatMessageContentT)
    · ChatRole Enumeration
  Serialization and Type System
    · Runtime Value Serialization
    · Component Serialization
  Core Component Logic
    · ConditionalRouter
    · AnswerBuilder
  In-Memory Filter Syntax
    · Filter Logic
    · BM25 and Similarity

## · Observability and Tracing  (L2768)
  源文件: haystack/logging.py, haystack/tracing/__init__.py, haystack/tracing/tracer.py, haystack/tracing/utils.py, releasenotes/notes/fix-auto-tracing-51ed3a590000d6c8.yaml, releasenotes/notes/fix-logging-index-error-c58691db633542c5.yaml, releasenotes/notes/fix-logs-containing-json-1393a00b4904f996.yaml, releasenotes/notes/fix-pipeline-output-data-trace-tag-6f9e2c1a4b8d3e70.yaml, releasenotes/notes/logging-tty-detection-8136769cb4d1da67.yaml, releasenotes/notes/opentelemetry-tracer-33d44eb125a3145b.yaml, releasenotes/notes/remove-opentelemetry-tracer-9d3e1f7a4c6b8052.yaml, releasenotes/notes/scope-logging-configuration-4a38bf0c8ea89fc9.yaml
  Tracing Infrastructure
    · Core Abstractions
    · Tracing Lifecycle
    · Configuration and Management
  Pipeline Instrumentation
    · Content Tracing
  Structured Logging
    · Configuration
    · Trace-Log Correlation
  Data Flow and Serialization

## · LLM Integration  (L2913)
  源文件: docs-website/docs/pipeline-components/embedders.mdx, docs-website/docs/pipeline-components/embedders/edenaidocumentembedder.mdx, docs-website/docs/pipeline-components/embedders/edenaitextembedder.mdx, docs-website/docs/pipeline-components/embedders/mockdocumentembedder.mdx, docs-website/docs/pipeline-components/embedders/mocktextembedder.mdx, docs-website/docs/pipeline-components/generators.mdx, docs-website/docs/pipeline-components/generators/edenaichatgenerator.mdx, docs-website/docs/pipeline-components/generators/litellmchatgenerator.mdx, docs-website/docs/pipeline-components/generators/mockchatgenerator.mdx, docs-website/docs/pipeline-components/generators/vllmchatgenerator.mdx, docs-website/versioned_docs/version-3.0/pipeline-components/embedders.mdx, docs-website/versioned_docs/version-3.0/pipeline-components/embedders/edenaidocumentembedder.mdx
  Architecture Overview
  Generator Component Types
    · Chat Generators
  Core Data Structures
    · ChatMessage
    · StreamingChunk
  Execution Patterns
    · Synchronous and Asynchronous Generation
    · Streaming Generation
  Tool Calling Support
    · Key Tool Components

## · OpenAI and Azure Integration  (L3186)
  源文件: docs-website/docs/pipeline-components/connectors/jinareaderconnector.mdx, docs-website/docs/pipeline-components/embedders/nvidiadocumentembedder.mdx, docs-website/docs/pipeline-components/embedders/nvidiatextembedder.mdx, docs-website/docs/pipeline-components/generators/amazonbedrockchatgenerator.mdx, docs-website/docs/pipeline-components/generators/amazonbedrockgenerator.mdx, docs-website/docs/pipeline-components/generators/anthropicchatgenerator.mdx, docs-website/docs/pipeline-components/generators/anthropicgenerator.mdx, docs-website/docs/pipeline-components/generators/anthropicvertexchatgenerator.mdx, docs-website/docs/pipeline-components/generators/azureopenaichatgenerator.mdx, docs-website/docs/pipeline-components/generators/azureopenairesponseschatgenerator.mdx, docs-website/docs/pipeline-components/generators/coherechatgenerator.mdx, docs-website/docs/pipeline-components/generators/coheregenerator.mdx
  Component Architecture
  OpenAIChatGenerator
    · Initialization
    · Execution Flow
    · Structured Outputs and Tools
  OpenAIResponsesChatGenerator
    · Key Features
  Azure OpenAI Variants
    · Azure Configuration
  Streaming Implementation
    · Streaming Data Flow
    · StreamingChunk Contents
  Error Handling and Metadata
    · Finish Reasons
    · Usage Statistics

## · Hugging Face API Integration  (L3469)
  源文件: docs-website/reference/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.18/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.19/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.20/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.21/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.22/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.23/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.24/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.25/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.26/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.27/integrations-api/fastembed.md, haystack/utils/hf.py
  Overview
    · API Components Architecture
  API Types and Configuration
    · API Type Enumerations
    · Configuration and Validation
  Chat Generation with HuggingFaceAPIChatGenerator
    · Component Features
    · Multimodal and Reasoning Data Flow
  Text Embedding Integration
    · HuggingFaceAPITextEmbedder & HuggingFaceAPIDocumentEmbedder
    · FastEmbed Integration
  Serialization of HF Arguments
    · Kwargs Serialization Logic
  Migration to v3.0
    · Package Mapping

## · Hugging Face Local Integration  (L3686)
  源文件: docs-website/reference/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.18/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.19/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.20/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.21/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.22/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.23/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.24/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.25/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.26/integrations-api/fastembed.md, docs-website/reference_versioned_docs/version-2.27/integrations-api/fastembed.md, haystack/utils/hf.py
  Purpose and Scope
  Architecture Overview
    · System Architecture Diagram
  Data Transformation and Messaging
    · Message Conversion Flow
  Model Configuration and Serialization
    · Kwargs Serialization Process
  Local Embedders (FastEmbed)
    · FastembedDocumentEmbedder
    · FastembedSparseDocumentEmbedder
  Code Entity Space Mapping
  v3.0 Migration Summary

## · Chat Messages and Prompt Building  (L3914)
  源文件: docs-website/docs/concepts/data-classes.mdx, docs-website/docs/concepts/data-classes/chatmessage.mdx, docs-website/docs/concepts/data-classes/filecontent.mdx, docs-website/docs/concepts/data-classes/imagecontent.mdx, docs-website/docs/concepts/device-management.mdx, docs-website/docs/concepts/pipelines.mdx, docs-website/docs/concepts/pipelines/pipeline-loops.mdx, docs-website/docs/concepts/pipelines/smart-pipeline-connections.mdx, docs-website/docs/development/enabling-gpu-acceleration.mdx, docs-website/docs/pipeline-components/builders/chatpromptbuilder.mdx, docs-website/docs/pipeline-components/builders/promptbuilder.mdx, docs-website/docs/pipeline-components/extractors.mdx
  ChatMessage Data Structure
    · Architecture Overview
    · Factory Methods
    · Content Properties
  Content Part Types
    · TextContent
    · ImageContent
    · FileContent
    · ToolCall and ToolCallResult
    · ReasoningContent
  ChatPromptBuilder Component
    · Component Logic and Data Flow
    · Template Formats
    · Variable Handling and Security
  PromptBuilder Component
    · PromptBuilder Implementation
    · Jinja2TimeExtension
  Serialization and OpenAI Format

## · Document Processing  (L4219)
  源文件: docs-website/docs/pipeline-components/converters/markdowntodocument.mdx, haystack/components/converters/html.py, haystack/components/converters/markdown.py, haystack/components/converters/pypdf.py, haystack/components/converters/txt.py, haystack/components/converters/xlsx.py, haystack/components/routers/metadata_router.py, haystack/document_stores/in_memory/document_store.py, haystack/testing/document_store.py, haystack/testing/document_store_async.py, haystack/utils/filters.py, releasenotes/notes/add-getmetadata-async-methods-and-tests-3ff2601b692697cb.yaml
  Overview of Document Processing in Haystack
    · Document Processing Flow
  Core Data Structures
    · Document Entity Mapping
  Document Converters
  Storage and Retrieval
    · InMemoryDocumentStore
  Routing and Utilities

## · Document Stores  (L4421)
  源文件: docs-website/reference/integrations-api/elasticsearch.md, docs-website/reference/integrations-api/opensearch.md, docs-website/reference_versioned_docs/version-2.18/integrations-api/elasticsearch.md, docs-website/reference_versioned_docs/version-2.18/integrations-api/opensearch.md, docs-website/reference_versioned_docs/version-2.19/integrations-api/elasticsearch.md, docs-website/reference_versioned_docs/version-2.19/integrations-api/opensearch.md, docs-website/reference_versioned_docs/version-2.20/integrations-api/elasticsearch.md, docs-website/reference_versioned_docs/version-2.20/integrations-api/opensearch.md, docs-website/reference_versioned_docs/version-2.21/integrations-api/elasticsearch.md, docs-website/reference_versioned_docs/version-2.21/integrations-api/opensearch.md, docs-website/reference_versioned_docs/version-2.22/integrations-api/elasticsearch.md, docs-website/reference_versioned_docs/version-2.22/integrations-api/opensearch.md
  Document Store Architecture
    · Natural Language to Code Entity Space: Retrieval & Writing
    · Interface and Implementation Flow
  InMemoryDocumentStore Implementation
  Document Store Integration: OpenSearch and Elasticsearch
    · Custom Queries and Placeholders
    · Filter Policies
  DocumentWriter Component
    · Core Functionality
  Document Storage and Retrieval Operations
    · Document Writing and Duplicate Policies
    · Document Filtering and Dynamic Filters
  BM25 Retrieval System
    · BM25 Algorithm Variants
    · Scoring and Scaling
  Embedding-based Retrieval
    · Similarity Computation
  Contextual Retrieval: SentenceWindowRetriever
  Async Operations
  Testing Infrastructure
    · Key Test Classes

## · Document Converters  (L4752)
  源文件: docs-website/docs/pipeline-components/converters/filetofilecontent.mdx, docs-website/docs/pipeline-components/converters/markdowntodocument.mdx, haystack/components/converters/__init__.py, haystack/components/converters/csv.py, haystack/components/converters/docx.py, haystack/components/converters/file_to_file_content.py, haystack/components/converters/html.py, haystack/components/converters/json.py, haystack/components/converters/markdown.py, haystack/components/converters/pdfminer.py, haystack/components/converters/pptx.py, haystack/components/converters/pypdf.py
  Purpose and Scope
  Overview
    · Converter Architecture
  Common Interface Pattern
    · Data Flow and System Entities
    · Common Parameters
  PyPDFToDocument
    · Class Definition
    · Extraction Modes
    · Page Separation
  HTMLToDocument
    · Configuration
  DOCXToDocument
    · Features
  JSONConverter
    · Key Parameters
  Routing and Fetching
    · FileTypeRouter
    · LinkContentFetcher
  Summary of Available Converters

## · Embedders and Rankers  (L5050)
  源文件: haystack/components/embedders/azure_document_embedder.py, haystack/components/embedders/azure_text_embedder.py, haystack/components/embedders/openai_document_embedder.py, haystack/components/embedders/openai_text_embedder.py, haystack/components/embedders/types/__init__.py, haystack/components/embedders/types/protocol.py, haystack/components/preprocessors/embedding_based_document_splitter.py, haystack/components/rankers/__init__.py, haystack/components/rankers/lost_in_the_middle.py, haystack/components/rankers/meta_field.py, haystack/components/rankers/meta_field_grouping_ranker.py, haystack/components/samplers/top_p.py
  Overview
  OpenAI and Azure Embedders
    · Implementation Details
    · Azure Variants
  Specialized Document Processing
    · Embedding-Based Splitting
  Rankers
    · Meta Field Ranker
    · Meta Field Grouping Ranker
    · Lost In The Middle Ranker

## · Document Preprocessing and Retrieval  (L5248)
  源文件: e2e/pipelines/test_evaluation_pipeline.py, e2e/pipelines/test_pdf_content_extraction_pipeline.py, haystack/components/converters/multi_file_converter.py, haystack/components/joiners/__init__.py, haystack/components/joiners/answer_joiner.py, haystack/components/joiners/document_joiner.py, haystack/components/joiners/list_joiner.py, haystack/components/preprocessors/__init__.py, haystack/components/preprocessors/csv_document_splitter.py, haystack/components/preprocessors/document_cleaner.py, haystack/components/preprocessors/document_preprocessor.py, haystack/components/preprocessors/document_splitter.py
  Document Preprocessors
    · Document Cleaning
    · Document Splitting
  Retrieval Strategies
    · InMemory Retrievers
  Document Joining
    · DocumentJoiner
  Summary Table of Components

## · Advanced Features  (L5476)
  源文件: MIGRATION.md, docs-website/docs/pipeline-components/agents-1/state.mdx, haystack/components/agents/agent.py, haystack/components/agents/state/state.py, haystack/components/agents/state/state_utils.py, haystack/components/agents/utils.py, haystack/hooks/__init__.py, haystack/hooks/invocation.py, haystack/hooks/protocol.py, haystack/hooks/utils.py, haystack/tools/__init__.py, haystack/tools/component_tool.py
  Agent System
    · Overview
    · Architecture
    · State Management and Hooks
  Tool Invocation
    · Overview
    · Tool Entities and Invocation
  Human-in-the-Loop and Context Management
  Evaluation Components
  Migration Guide (v2.x to v3.0)

## · Agent System  (L5691)
  源文件: MIGRATION.md, docs-website/docs/concepts/agents.mdx, docs-website/docs/concepts/agents/multi-agent-systems.mdx, docs-website/docs/concepts/concepts-overview.mdx, docs-website/docs/overview/migrating-from-langgraphlangchain-to-haystack.mdx, docs-website/docs/pipeline-components/agents-1/agent.mdx, docs-website/docs/pipeline-components/agents-1/state.mdx, docs-website/docs/tools/agenttool.mdx, docs-website/docs/tools/componenttool.mdx, docs-website/docs/tools/pipelinetool.mdx, docs-website/docs/tools/tool.mdx, docs-website/docs/tools/toolset.mdx
  Core Architecture
  State Management
    · Schema and Handlers
  Agent Execution Lifecycle
  Hooks and Human-in-the-Loop
    · Confirmation Strategies
  Breakpoints and Snapshots
  Configuration Parameters

## · Tool Invocation  (L5895)
  源文件: docs-website/docs/concepts/agents.mdx, docs-website/docs/concepts/agents/multi-agent-systems.mdx, docs-website/docs/concepts/concepts-overview.mdx, docs-website/docs/overview/migrating-from-langgraphlangchain-to-haystack.mdx, docs-website/docs/pipeline-components/agents-1/agent.mdx, docs-website/docs/tools/agenttool.mdx, docs-website/docs/tools/componenttool.mdx, docs-website/docs/tools/pipelinetool.mdx, docs-website/docs/tools/searchabletoolset.mdx, docs-website/docs/tools/tool.mdx, docs-website/docs/tools/toolset.mdx, docs-website/versioned_docs/version-2.28/concepts/agents.mdx
  Purpose and Scope
  Architecture Overview
    · Bridging Natural Language to Code
  Tool Abstractions
    · The Tool Class
    · Specialized Tool Types
    · ComponentTool Features
  Toolsets and Dynamic Discovery
  Execution Model
    · Parallel Execution sequence
    · State Injection and Extraction
    · Output Formatting (`outputs_to_string`)
  Error Handling
  Serialization

## · Human-in-the-Loop and Context Management  (L6087)
  源文件: MIGRATION.md, docs-website/docs/pipeline-components/agents-1/compaction.mdx, docs-website/docs/pipeline-components/agents-1/compaction/compaction-hook.mdx, docs-website/docs/pipeline-components/agents-1/compaction/sliding-window-compactor.mdx, docs-website/docs/pipeline-components/agents-1/compaction/tool-result-pruning-compactor.mdx, docs-website/docs/pipeline-components/agents-1/hooks.mdx, docs-website/docs/pipeline-components/agents-1/state.mdx, haystack/components/agents/agent.py, haystack/components/agents/state/state.py, haystack/components/agents/state/state_utils.py, haystack/components/agents/utils.py, haystack/hooks/__init__.py
  Human-in-the-Loop (HITL)
    · Core HITL Components
    · HITL Data Flow
  Context Management and Compaction
    · Compaction Strategies
    · Compaction Mechanism
  Tool Result Offloading
    · Offloading Policies
    · Storage Backends
  Implementation Detail: Agent State Interaction
    · Hook Points in the Agent Loop

## · Evaluation Components  (L6275)
  源文件: haystack/components/evaluators/__init__.py, haystack/components/evaluators/answer_exact_match.py, haystack/components/evaluators/context_relevance.py, haystack/components/evaluators/document_map.py, haystack/components/evaluators/document_mrr.py, haystack/components/evaluators/document_recall.py, haystack/components/evaluators/faithfulness.py, haystack/components/evaluators/llm_evaluator.py, haystack/components/evaluators/sas_evaluator.py, haystack/evaluation/__init__.py, haystack/evaluation/eval_run_result.py, haystack/utils/__init__.py
  Overview
  LLM-Based Evaluators
    · LLMEvaluator Architecture
    · Specialized LLM Evaluators
  SASEvaluator
  Metric-Based Evaluators
  EvalRunResult

## · Migration Guide (v2.x to v3.0)  (L6475)
  源文件: MIGRATION.md, docs-website/docs/concepts/components.mdx, docs-website/docs/document-stores/oracledocumentstore.mdx, docs-website/docs/document-stores/supabasedocumentstore.mdx, docs-website/docs/optimization/advanced-rag-techniques/hypothetical-document-embeddings-hyde.mdx, docs-website/docs/overview/get-started.mdx, docs-website/docs/overview/migration.mdx, docs-website/docs/pipeline-components/agents-1/state.mdx, docs-website/docs/pipeline-components/retrievers/pgvectorembeddingretriever.mdx, docs-website/docs/pipeline-components/routers/metadatarouter.mdx, docs-website/docs/pipeline-components/writers/documentwriter.mdx, docs-website/versioned_docs/version-2.22/overview/get-started.mdx
  Serialization Format Changes
    · Flattened Dictionary Structure
  Component Relocation to External Packages
    · Migration Mapping for External Packages
  Removed and Renamed Components
    · Legacy Generators
    · ToolInvoker Removal
  The New Agent and State System
    · State and Schema
    · Reserved State Keys
  Hook System Lifecycle
  Async and Pipeline Consolidation

## · Glossary  (L6672)
  源文件: MIGRATION.md, docs-website/docs/pipeline-components/agents-1/state.mdx, haystack/components/agents/agent.py, haystack/components/agents/state/state.py, haystack/components/agents/state/state_utils.py, haystack/components/agents/utils.py, haystack/components/builders/chat_prompt_builder.py, haystack/components/builders/prompt_builder.py, haystack/components/evaluators/context_relevance.py, haystack/components/evaluators/faithfulness.py, haystack/components/evaluators/llm_evaluator.py, haystack/components/routers/metadata_router.py
  Core Concepts
    · Component
    · Pipeline
    · Socket
  Data Structures & Messaging
    · ChatMessage
    · Document
    · StreamingChunk
  Agentic & Tool Terms
    · Agent
    · Tool
    · Tool Calling
  Execution & Lifecycle
    · Breakpoint
    · Warm Up
  System Mapping Diagrams
    · From Natural Language to Pipeline Entities
    · Agent and Tool Interaction
  Technical Jargon Summary