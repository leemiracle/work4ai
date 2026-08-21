# Skeleton: metagpt（34 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 6KB | 2 | ~2 | 20 |
| 2 | Getting Started | L158 | 7KB | 2 | ~2 | 31 |
| 3 | Software Company Metaphor | L382 | 6KB | 2 | ~2 | 19 |
| 4 | Core Architecture | L541 | 7KB | 3 | ~2 | 18 |
| 5 | Role System | L740 | 9KB | 2 | ~1 | 30 |
| 6 | Message Passing System | L958 | 9KB | 2 | ~3 | 30 |
| 7 | Action Framework | L1140 | 9KB | 4 | ~0 | 26 |
| 8 | Environment System | L1350 | 11KB | 2 | ~1 | 34 |
| 9 | LLM Integration | L1541 | 8KB | 2 | ~2 | 19 |
| 10 | OpenAI Integration | L1712 | 8KB | 3 | ~2 | 12 |
| 11 | Alternative LLM Providers | L1915 | 9KB | 3 | ~4 | 33 |
| 12 | Token Management and Cost Tracking | L2116 | 8KB | 2 | ~1 | 23 |
| 13 | Memory Systems | L2286 | 7KB | 2 | ~0 | 30 |
| 14 | Brain Memory | L2426 | 10KB | 2 | ~3 | 14 |
| 15 | Experience Pooling | L2638 | 10KB | 3 | ~2 | 28 |
| 16 | Long-term Memory and Document Stores | L2890 | 7KB | 2 | ~2 | 21 |
| 17 | Dynamic Intelligence (DI) | L3033 | 8KB | 2 | ~0 | 28 |
| 18 | RoleZero | L3209 | 10KB | 2 | ~2 | 31 |
| 19 | Tools System | L3424 | 11KB | 3 | ~2 | 38 |
| 20 | Data Interpreter | L3636 | 8KB | 2 | ~2 | 27 |
| 21 | Retrieval-Augmented Generation (RAG) | L3785 | 8KB | 4 | ~2 | 19 |
| 22 | RAG Engines | L4001 | 8KB | 2 | ~2 | 23 |
| 23 | RAG Configuration | L4163 | 8KB | 2 | ~0 | 24 |
| 24 | Specialized Capabilities | L4327 | 8KB | 3 | ~2 | 32 |
| 25 | Machine Learning Engineering | L4544 | 9KB | 2 | ~4 | 32 |
| 26 | Self-Supervised Prompt Optimization | L4711 | 9KB | 3 | ~1 | 14 |
| 27 | Git Repository Management | L4921 | 9KB | 3 | ~1 | 25 |
| 28 | Web Research and Search | L5100 | 9KB | 2 | ~2 | 35 |
| 29 | Configuration and Context | L5253 | 10KB | 4 | ~3 | 28 |
| 30 | Testing Framework | L5512 | 9KB | 2 | ~2 | 26 |
| 31 | Extension Ecosystem | L5707 | 9KB | 2 | ~0 | 30 |
| 32 | Simulation Environments | L5874 | 10KB | 2 | ~2 | 29 |
| 33 | Custom Agents and Multi-Agent Patterns | L6060 | 7KB | 2 | ~0 | 28 |
| 34 | Glossary | L6217 | 13KB | 2 | ~2 | 45 |


## · Overview  (L6)
  源文件: Dockerfile, MANIFEST.in, README.md, docs/ACADEMIC_WORK.md, docs/FAQ-EN.md, docs/NEWS.md, docs/README_CN.md, docs/README_FR.md, docs/README_JA.md, docs/install/cli_install.md, docs/install/cli_install_cn.md, docs/install/docker_install.md
  Core Architecture
    · System Architecture Diagram
    · Role System
    · Software Development Workflow
  Key Capabilities
    · Multi-Agent Collaboration
    · Dynamic Intelligence (DI)
    · RAG & Tool Integration
  Getting Started
  Summary Table

## · Getting Started  (L158)
  源文件: Dockerfile, README.md, config/config2.example.yaml, docs/ACADEMIC_WORK.md, docs/FAQ-EN.md, docs/NEWS.md, docs/README_CN.md, docs/README_FR.md, docs/README_JA.md, docs/install/cli_install.md, docs/install/cli_install_cn.md, docs/install/docker_install.md
  Installation
    · Standard Installation
    · Docker Installation
  Configuration
    · The config2.yaml File
    · Key Configuration Parameters
  Data Flow: Initialization to Execution
    · Configuration and LLM Initialization
  Usage
    · CLI Interface
    · Python API
    · Multi-Agent Lifecycle
  Environment Variables

## · Software Company Metaphor  (L382)
  源文件: Dockerfile, README.md, docs/ACADEMIC_WORK.md, docs/NEWS.md, docs/README_CN.md, docs/README_FR.md, docs/README_JA.md, metagpt/config2.py, metagpt/context.py, metagpt/context_mixin.py, metagpt/llm.py, metagpt/roles/architect.py
  The Team Class
    · Key Attributes and Initialization
    · Data Flow: Idea to Project
  SOP-Driven Lifecycle
    · Team Execution Logic (`Team.run`)
  Hiring and Role Configuration
    · Standard Staffing Pattern
    · Natural Language Space to Code Entity Space: Role Mapping
  Multi-Agent Round Execution
    · Interaction Logic
    · Operational Flow Diagram
  Configuration and Context

## · Core Architecture  (L541)
  源文件: metagpt/actions/action.py, metagpt/actions/design_api.py, metagpt/actions/project_management.py, metagpt/actions/summarize_code.py, metagpt/actions/write_code.py, metagpt/actions/write_code_review.py, metagpt/actions/write_prd.py, metagpt/const.py, metagpt/environment/api/__init__.py, metagpt/environment/api/env_api.py, metagpt/environment/base_env.py, metagpt/roles/engineer.py
  High-Level Architecture Overview
  Role System
    · Role Structure
    · Role Lifecycle
  Message Passing System
    · Message Routing
  Action Framework
    · SDLC Actions
  Environment System
    · Software Development Workflow
  Key Components and Relationships

## · Role System  (L740)
  源文件: examples/di/atomization_capacity_plan.py, examples/di/automated_planning_of_tasks.py, examples/di/data_analyst_write_code.py, examples/di/interacting_with_human.py, examples/use_off_the_shelf_agent.py, examples/write_design.py, examples/write_game_code.py, metagpt/actions/action.py, metagpt/actions/design_api.py, metagpt/actions/project_management.py, metagpt/actions/summarize_code.py, metagpt/actions/write_code.py
  Core Architecture
    · Role Entity Mapping
  Role Lifecycle
    · Natural Language to Code Entity Space: Lifecycle
    · Observation Phase
    · Thinking Phase
    · Acting Phase
  Reaction Modes
  Specialized Built-in Roles
    · ProductManager
    · Architect
    · Engineer
    · QaEngineer
  Message Subscription and Routing

## · Message Passing System  (L958)
  源文件: metagpt/actions/action.py, metagpt/actions/action_output.py, metagpt/actions/design_api.py, metagpt/actions/project_management.py, metagpt/actions/summarize_code.py, metagpt/actions/write_code.py, metagpt/actions/write_code_review.py, metagpt/actions/write_prd.py, metagpt/const.py, metagpt/environment/api/__init__.py, metagpt/environment/api/env_api.py, metagpt/environment/base_env.py
  Message Structure
    · Entity Relationship: Natural Language to Code Space
    · Key Message Attributes
    · Message Types
  Message Routing and Filtering
    · Routing Constants
    · The Subscription Mechanism
  Implementation Details
    · Message Queue (`MessageQueue`)
    · Role Observation Logic
    · Memory Integration
  Examples of Message Flow
    · Engineer Observation
    · Self-Routing for Iteration
  Serialization and Persistence

## · Action Framework  (L1140)
  源文件: metagpt/actions/__init__.py, metagpt/actions/action.py, metagpt/actions/action_node.py, metagpt/actions/debug_error.py, metagpt/actions/design_api.py, metagpt/actions/design_api_an.py, metagpt/actions/project_management.py, metagpt/actions/project_management_an.py, metagpt/actions/run_code.py, metagpt/actions/summarize_code.py, metagpt/actions/write_code.py, metagpt/actions/write_code_review.py
  Overview
    · Natural Language to Code Entity Mapping
  The Action Base Class
  The ActionNode System
    · Structured Output Flow
    · Composition and Templates
  SDLC Pipeline Actions
    · WritePRD
    · WriteDesign
    · WriteTasks
    · WriteCode
  Action Execution in Roles
    · Example: Engineer Workflow

## · Environment System  (L1350)
  源文件: metagpt/base/__init__.py, metagpt/base/base_env.py, metagpt/base/base_env_space.py, metagpt/base/base_role.py, metagpt/base/base_serialization.py, metagpt/environment/android/android_ext_env.py, metagpt/environment/android/grounding_dino_config.py, metagpt/environment/android/text_icon_localization.py, metagpt/environment/api/__init__.py, metagpt/environment/api/env_api.py, metagpt/environment/base_env.py, metagpt/environment/mgx/mgx_env.py
  Core Abstractions
    · ExtEnv
    · Environment
  Hierarchical Routing: MGXEnv
    · Message Flow in MGXEnv
    · MGX Message Routing Logic
  The RoleZero Ecosystem
    · Code Entity Space: RoleZero Architecture
  Specialized Simulation Environments
    · 1. Android Environment (`AndroidExtEnv`)
    · 2. Werewolf Environment (`WerewolfExtEnv`)
    · 3. Minecraft & Stanford Town
  Data Flow: Action to Environment

## · LLM Integration  (L1541)
  源文件: metagpt/configs/llm_config.py, metagpt/provider/__init__.py, metagpt/provider/anthropic_api.py, metagpt/provider/base_llm.py, metagpt/provider/bedrock/base_provider.py, metagpt/provider/bedrock/bedrock_provider.py, metagpt/provider/bedrock/utils.py, metagpt/provider/bedrock_api.py, metagpt/provider/dashscope_api.py, metagpt/provider/human_provider.py, metagpt/provider/openai_api.py, metagpt/provider/qianfan_api.py
  Architecture Overview
  Provider Registration and Selection
  BaseLLM Interface
  LLM Configuration
  Supported LLM Providers
  Token Management and Cost Tracking
  Advanced Capabilities
    · Multimodal and Reasoning
    · Resilience

## · OpenAI Integration  (L1712)
  源文件: examples/hello_world.py, examples/ping.py, metagpt/provider/base_llm.py, metagpt/provider/dashscope_api.py, metagpt/provider/human_provider.py, metagpt/provider/metagpt_api.py, metagpt/provider/openai_api.py, metagpt/provider/qianfan_api.py, metagpt/utils/cost_manager.py, tests/metagpt/provider/mock_llm_config.py, tests/metagpt/provider/test_base_llm.py, tests/metagpt/provider/test_openai.py
  Architecture Overview
  Provider Registration and Compatibility
  Initialization and Configuration
    · Configuration Options
  Core Request Handling
    · Streaming and Reasoning
    · Resilience and Retries
  Specialized Capabilities
    · Function/Tool Calling
    · Multimodal Support
    · Image, Speech, and Moderation
  Token Management and Cost Tracking
  Usage Example

## · Alternative LLM Providers  (L1915)
  源文件: examples/llm_vision.py, metagpt/configs/llm_config.py, metagpt/provider/__init__.py, metagpt/provider/anthropic_api.py, metagpt/provider/base_llm.py, metagpt/provider/bedrock/base_provider.py, metagpt/provider/bedrock/bedrock_provider.py, metagpt/provider/bedrock/utils.py, metagpt/provider/bedrock_api.py, metagpt/provider/dashscope_api.py, metagpt/provider/general_api_base.py, metagpt/provider/general_api_requestor.py
  Provider Architecture Overview
    · Class Hierarchy and Key Entities
  Provider Registration Mechanism
  Ollama Integration
    · Ollama Message Handling
  Google Gemini Integration
  AWS Bedrock Integration
    · Bedrock Provider Pattern
  Other Supported Providers
  Configuration Summary

## · Token Management and Cost Tracking  (L2116)
  源文件: examples/hello_world.py, examples/ping.py, metagpt/configs/llm_config.py, metagpt/provider/__init__.py, metagpt/provider/anthropic_api.py, metagpt/provider/base_llm.py, metagpt/provider/bedrock/base_provider.py, metagpt/provider/bedrock/bedrock_provider.py, metagpt/provider/bedrock/utils.py, metagpt/provider/bedrock_api.py, metagpt/provider/dashscope_api.py, metagpt/provider/human_provider.py
  Overview
    · System Architecture and Code Entities
  Token Counting System
    · Token Cost and Limit Data
    · Key Counting Functions
  Cost Manager
  Token Management and Message Compression
    · Compression Strategies
    · Compression Logic
  Provider-Specific Implementations
    · OpenAI Integration
    · Bedrock Integration
    · Anthropic Integration
  Summary of Constants

## · Memory Systems  (L2286)
  源文件: .gitignore, docs/.agent-store-config.yaml.example, docs/.well-known/ai-plugin.json, metagpt/actions/action_output.py, metagpt/actions/skill_action.py, metagpt/actions/talk_action.py, metagpt/document.py, metagpt/document_store/base_store.py, metagpt/document_store/chromadb_store.py, metagpt/document_store/faiss_store.py, metagpt/learn/skill_loader.py, metagpt/memory/__init__.py
  Memory System Architecture
  Core Memory Components
    · Basic Memory
    · Brain Memory
    · Long-term Memory (LTM)
  Experience Pooling
  Memory Integration Flow
  Child Pages

## · Brain Memory  (L2426)
  源文件: docs/.agent-store-config.yaml.example, docs/.well-known/ai-plugin.json, metagpt/actions/skill_action.py, metagpt/actions/talk_action.py, metagpt/learn/skill_loader.py, metagpt/memory/brain_memory.py, metagpt/roles/assistant.py, metagpt/utils/redis.py, metagpt/utils/s3.py, tests/metagpt/memory/test_brain_memory.py, tests/metagpt/roles/test_assistant.py, tests/metagpt/test_llm.py
  Architecture Overview
    · Code Entity Space to Natural Language Space
  Core Components
  Memory Processing Flow
  Message Management
    · Adding Messages
    · Knowledge Management
  Memory Persistence with Redis
  Memory Optimization through Summarization
    · Summarization Strategies
  Semantic Analysis and Rewriting
  Integration in Assistant Role

## · Experience Pooling  (L2638)
  源文件: config/config2.example.yaml, examples/data/exp_pool/team_leader_exps.json, examples/exp_pool/decorator.py, examples/exp_pool/manager.py, examples/exp_pool/scorer.py, metagpt/configs/exp_pool_config.py, metagpt/exp_pool/__init__.py, metagpt/exp_pool/context_builders/action_node.py, metagpt/exp_pool/context_builders/base.py, metagpt/exp_pool/context_builders/role_zero.py, metagpt/exp_pool/context_builders/simple.py, metagpt/exp_pool/decorator.py
  Overview and Purpose
    · System Architecture
  Core Data Model
  Experience Manager
    · Storage Resolution
  Experience Cache Decorator
    · Execution Flow
  RoleZero Context Builders
    · RoleZeroContextBuilder
    · RoleZeroSerializer
  Configuration Reference
  Implementation Example
    · Basic Usage
    · Manual Management

## · Long-term Memory and Document Stores  (L2890)
  源文件: .gitignore, metagpt/document.py, metagpt/document_store/base_store.py, metagpt/document_store/chromadb_store.py, metagpt/document_store/faiss_store.py, metagpt/document_store/lancedb_store.py, metagpt/document_store/milvus_store.py, metagpt/document_store/qdrant_store.py, metagpt/memory/longterm_memory.py, metagpt/memory/memory_storage.py, metagpt/prompts/summarize.py, metagpt/utils/embedding.py
  Long-term Memory Architecture
    · Key Components
    · Data Flow: Message Observation to LTM
  Document Stores
    · Supported Backends
    · FaissStore Implementation
  MemoryStorage and Retrieval
    · Similarity Filtering
    · Persistence Lifecycle

## · Dynamic Intelligence (DI)  (L3033)
  源文件: metagpt/actions/di/write_analysis_code.py, metagpt/actions/di/write_plan.py, metagpt/environment/mgx/mgx_env.py, metagpt/prompts/di/architect.py, metagpt/prompts/di/data_analyst.py, metagpt/prompts/di/engineer2.py, metagpt/prompts/di/role_zero.py, metagpt/prompts/di/team_leader.py, metagpt/prompts/di/write_analysis_code.py, metagpt/prompts/task_type.py, metagpt/roles/di/data_analyst.py, metagpt/roles/di/data_interpreter.py
  Core Architecture
    · DI Class Hierarchy and Entity Mapping
  RoleZero: The Foundation of DI
  Tools System
    · Tool-to-Code Mapping
  Data Interpreter
  Team Coordination and Environment

## · RoleZero  (L3209)
  源文件: metagpt/configs/role_zero_config.py, metagpt/environment/mgx/mgx_env.py, metagpt/memory/role_zero_memory.py, metagpt/prompts/di/data_analyst.py, metagpt/prompts/di/engineer2.py, metagpt/prompts/di/role_zero.py, metagpt/prompts/di/team_leader.py, metagpt/roles/di/data_analyst.py, metagpt/roles/di/engineer2.py, metagpt/roles/di/role_zero.py, metagpt/roles/di/team_leader.py, metagpt/strategy/__init__.py
  Architecture Overview
    · Code Entity Mapping
  Reactive Cycle and Decision Making
    · Quick vs. Deep Thinking
  Planning and Tool Execution
    · Command Execution Map
  TeamLeader and MGXEnv Routing
  Specialized Extensions
    · Engineer2
    · DataAnalyst
  Memory Systems

## · Tools System  (L3424)
  源文件: examples/di/fix_github_issue.py, examples/di/run_flask.py, examples/di/use_github_repo.py, metagpt/actions/di/execute_nb_code.py, metagpt/actions/di/write_analysis_code.py, metagpt/actions/di/write_plan.py, metagpt/configs/role_custom_config.py, metagpt/logs.py, metagpt/prompts/di/architect.py, metagpt/prompts/di/write_analysis_code.py, metagpt/prompts/task_type.py, metagpt/roles/di/data_interpreter.py
  Tool Registry and Recommendation
    · Tool Registration Pattern
    · Tool Recommendation System
  Core Tool Libraries
    · Editor (File Management)
    · Terminal (Bash/Shell)
    · Browser (Web Interaction)
  Data Interpreter Tools
    · ExecuteNbCode (Jupyter/IPython)
    · IndexRepo (Semantic Search)
  Tool Schema Conversion
  Implementation Details
    · Data Flow for Tool Execution

## · Data Interpreter  (L3636)
  源文件: examples/di/InfiAgent-DABench/DABench.py, examples/di/InfiAgent-DABench/README.md, examples/di/InfiAgent-DABench/run_InfiAgent-DABench.py, examples/di/InfiAgent-DABench/run_InfiAgent-DABench_all.py, examples/di/InfiAgent-DABench/run_InfiAgent-DABench_single.py, examples/di/README.md, examples/di/machine_learning.py, examples/di/requirements_prompt.py, examples/di/run_ml_benchmark.py, examples/di/run_open_ended_tasks.py, metagpt/actions/di/execute_nb_code.py, metagpt/actions/di/write_analysis_code.py
  Overview and Architecture
    · Natural Language to Code Entity Mapping
  Core Components
    · 1. DataInterpreter Role
    · 2. Planning and Task Classification
    · 3. Execution via ExecuteNbCode
  Data Flow and Execution Loop
  Tool Integration
  DataAnalyst Variant

## · Retrieval-Augmented Generation (RAG)  (L3785)
  源文件: metagpt/rag/benchmark/base.py, metagpt/rag/engines/__init__.py, metagpt/rag/engines/simple.py, metagpt/rag/factories/base.py, metagpt/rag/factories/index.py, metagpt/rag/factories/ranker.py, metagpt/rag/factories/retriever.py, metagpt/rag/interface.py, metagpt/rag/rankers/__init__.py, metagpt/rag/retrievers/__init__.py, metagpt/rag/retrievers/base.py, metagpt/rag/retrievers/bm25_retriever.py
  Overview
  Architecture
    · Main Components
  Retrievers and Configuration
    · Supported Retrievers
    · Rankers and Reranking
  RAG Workflow
  Performance Evaluation
  Child Pages

## · RAG Engines  (L4001)
  源文件: metagpt/configs/omniparse_config.py, metagpt/rag/engines/__init__.py, metagpt/rag/engines/simple.py, metagpt/rag/interface.py, metagpt/rag/parsers/__init__.py, metagpt/rag/parsers/omniparse.py, metagpt/rag/rankers/__init__.py, metagpt/rag/retrievers/__init__.py, metagpt/rag/retrievers/base.py, metagpt/rag/retrievers/bm25_retriever.py, metagpt/rag/retrievers/faiss_retriever.py, metagpt/rag/retrievers/hybrid_retriever.py
  Overview
  Architecture
    · RAG Component Mapping
  SimpleEngine
    · Creation Methods
    · Core Functionality
  Retriever Implementations
    · Retriever Capabilities
  OmniParse Integration
  IndexRepo Tool
    · Search Flow
    · Key Components of IndexRepo

## · RAG Configuration  (L4163)
  源文件: config/config2.example.yaml, examples/exp_pool/decorator.py, metagpt/configs/exp_pool_config.py, metagpt/exp_pool/__init__.py, metagpt/exp_pool/decorator.py, metagpt/exp_pool/manager.py, metagpt/exp_pool/schema.py, metagpt/rag/benchmark/base.py, metagpt/rag/factories/__init__.py, metagpt/rag/factories/base.py, metagpt/rag/factories/embedding.py, metagpt/rag/factories/index.py
  RAG Configuration Architecture
    · System Components and Code Entities
  Configuration Schemas
    · Retriever Configurations
    · Ranker Configurations
    · Index Configurations
  The Factory Pattern
    · Key Factory Methods
  LLM and Embedding Integration
    · RAGLLM Wrapper
    · Embedding Configuration
  Experience Pool Configuration

## · Specialized Capabilities  (L4327)
  源文件: examples/spo/README.md, examples/spo/optimize.py, metagpt/actions/prepare_documents.py, metagpt/actions/rebuild_class_view.py, metagpt/actions/rebuild_sequence_view.py, metagpt/ext/spo/app.py, metagpt/ext/spo/components/evaluator.py, metagpt/ext/spo/components/optimizer.py, metagpt/ext/spo/utils/data_utils.py, metagpt/ext/spo/utils/evaluation_utils.py, metagpt/ext/spo/utils/llm_client.py, metagpt/ext/spo/utils/load.py
  1. Machine Learning Engineering (7.1)
    · ML Capabilities Architecture
  2. Self-Supervised Prompt Optimization (SPO) (7.2)
    · SPO Architecture
  3. Git Repository Management (7.3)
    · Git Integration Architecture
  4. Web Research and Search (7.4)
    · Search and Research Components
  5. Code Analysis and Visualization

## · Machine Learning Engineering  (L4544)
  源文件: examples/aflow/README.md, examples/aflow/optimize.py, metagpt/ext/aflow/scripts/evaluator.py, metagpt/ext/aflow/scripts/optimizer.py, metagpt/ext/aflow/scripts/optimizer_utils/convergence_utils.py, metagpt/ext/aflow/scripts/optimizer_utils/data_utils.py, metagpt/ext/aflow/scripts/optimizer_utils/experience_utils.py, metagpt/ext/aflow/scripts/workflow.py, metagpt/ext/sela/README.md, metagpt/ext/sela/data/custom_task.py, metagpt/ext/sela/run_experiment.py, metagpt/ext/sela/runner/README.md
  Purpose and Scope
  Architecture Overview
  Automated ML (AutoML) and Optimization
    · AFlow: Agentic Workflow Optimizer
    · SELA: Tree-Search Enhanced AutoML
  Data Preprocessing and Feature Engineering
    · Data Preprocessing Tools
    · Feature Engineering Tools
  Multimodal ML Capabilities
    · Stable Diffusion Integration
    · Vision-to-Webpage Generation
  Tool Registration and Conversion

## · Self-Supervised Prompt Optimization  (L4711)
  源文件: examples/spo/README.md, examples/spo/optimize.py, metagpt/ext/spo/app.py, metagpt/ext/spo/components/evaluator.py, metagpt/ext/spo/components/optimizer.py, metagpt/ext/spo/prompts/evaluate_prompt.py, metagpt/ext/spo/prompts/optimize_prompt.py, metagpt/ext/spo/settings/Navigate.yaml, metagpt/ext/spo/settings/Poem.yaml, metagpt/ext/spo/utils/data_utils.py, metagpt/ext/spo/utils/evaluation_utils.py, metagpt/ext/spo/utils/llm_client.py
  Core Concepts and Advantages
  System Architecture
    · Code Entity Mapping
    · Class Definitions and Roles
  Optimization Process Flow
  Multi-LLM Configuration
  Template Configuration
    · YAML Structure
  Execution Methods
    · 1. Python API
    · 2. Command-Line Interface
    · 3. Streamlit Web Interface
  Output and Results

## · Git Repository Management  (L4921)
  源文件: metagpt/actions/prepare_documents.py, metagpt/actions/rebuild_class_view.py, metagpt/actions/rebuild_sequence_view.py, metagpt/prompts/di/swe_agent.py, metagpt/repo_parser.py, metagpt/roles/di/swe_agent.py, metagpt/startup.py, metagpt/tools/libs/git.py, metagpt/utils/dependency_file.py, metagpt/utils/di_graph_repository.py, metagpt/utils/file_repository.py, metagpt/utils/git_repository.py
  Overview
    · System Architecture: Natural Language to Code Entity Space
  Core Components
    · GitRepository Class
    · FileRepository and Dependency Tracking
  Autonomous Issue Resolution: SWEAgent
    · SWEAgent Key Features
  GitHub Integration Tools
    · Pull Request Creation
    · Issue Creation
  Incremental Development & Repository Initialization
  Reverse Engineering and Visualization

## · Web Research and Search  (L5100)
  源文件: .dockerignore, examples/agent_creator.py, examples/build_customized_agent.py, examples/build_customized_multi_agents.py, examples/debate.py, examples/debate_simple.py, examples/search_enhanced_qa.py, examples/search_with_specific_engine.py, metagpt/actions/research.py, metagpt/actions/search_enhanced_qa.py, metagpt/configs/browser_config.py, metagpt/configs/search_config.py
  Researcher Role and Workflow
    · Data Flow and Action Sequence
  Search Engine Integrations
    · Supported Search Engines
    · Configuration and Initialization
  Web Browsing and Scraping
    · Browser Drivers
    · WebBrowseAndSummarize Action
  SearchEnhancedQA
    · Key Components
    · Implementation Details

## · Configuration and Context  (L5253)
  源文件: config/config2.example.yaml, config/config2.yaml, examples/di/crawl_webpage.py, examples/di/data_visualization.py, examples/di/email_summary.py, examples/di/imitate_webpage.py, examples/di/machine_learning_with_tools.py, examples/di/sd_tool_usage.py, examples/di/solve_math_problems.py, examples/di/use_browser.py, examples/exp_pool/decorator.py, metagpt/config2.py
  Overview
    · System Interaction Diagram
  Configuration System
    · Config Class Structure
    · Configuration Sources and Merging
    · Key Configuration Sections
  Context System
    · Context Class as Service Locator
    · ContextMixin: Dependency Injection Pattern
  Using Configuration and Context
    · Per-Role LLM Configuration
    · Experience Pool Configuration
    · CLI Initialization Flow

## · Testing Framework  (L5512)
  源文件: .coveragerc, .gitattributes, .github/ISSUE_TEMPLATE/config.yaml, .github/ISSUE_TEMPLATE/request_new_features.md, .github/ISSUE_TEMPLATE/show_me_the_bug.md, .github/PULL_REQUEST_TEMPLATE.md, .github/workflows/fulltest.yaml, .github/workflows/stale.yaml, .github/workflows/unittest.yaml, examples/data/rag/travel.txt, pytest.ini, tests/conftest.py
  Overview
  Architecture and Data Flow
    · Mock LLM Class Hierarchy
    · LLM Interception Flow
  Core Components
    · Response Caching System
    · Serialization Testing
    · Global Fixtures (`conftest.py`)
  CI/CD Workflows
    · Unit Tests (`unittest.yaml`)
    · Full Tests (`fulltest.yaml`)
  Implementation Details: Mocking LLM Responses

## · Extension Ecosystem  (L5707)
  源文件: examples/stanford_town/run_st_game.py, examples/stanford_town/storage/.gitignore, metagpt/environment/android/env_space.py, metagpt/environment/minecraft/minecraft_env.py, metagpt/environment/werewolf/const.py, metagpt/environment/werewolf/werewolf_env.py, metagpt/environment/werewolf/werewolf_ext_env.py, metagpt/ext/__init__.py, metagpt/ext/android_assistant/README.md, metagpt/ext/android_assistant/README_CN.md, metagpt/ext/android_assistant/__init__.py, metagpt/ext/android_assistant/actions/__init__.py
  Simulation Environments
    · Werewolf Game
    · Stanford Town
    · Minecraft Integration
    · Environment-Role Interaction Space
  Android Assistant
  Code Review (CR) Extension
    · Key Components
    · Automated PR Workflow
  Custom Agents and Multi-Agent Patterns

## · Simulation Environments  (L5874)
  源文件: examples/stanford_town/run_st_game.py, examples/stanford_town/storage/.gitignore, metagpt/environment/minecraft/minecraft_env.py, metagpt/environment/stanford_town/stanford_town_env.py, metagpt/environment/werewolf/const.py, metagpt/environment/werewolf/werewolf_env.py, metagpt/environment/werewolf/werewolf_ext_env.py, metagpt/ext/__init__.py, metagpt/ext/android_assistant/README.md, metagpt/ext/android_assistant/README_CN.md, metagpt/ext/android_assistant/__init__.py, metagpt/ext/android_assistant/actions/__init__.py
  Core Abstractions
    · ExtEnv Base Class
    · Action and Observation Spaces
  Werewolf Game Simulation
    · Environment Logic
    · Game Flow Diagram
    · Key Classes
  Stanford Town (Generative Agents)
    · Spatial Memory and Environment
    · Integration with Frontend
  Android Assistant Simulation
    · Operation Phases
    · Interaction Mapping
  Building Custom Environments

## · Custom Agents and Multi-Agent Patterns  (L6060)
  源文件: examples/agent_creator.py, examples/build_customized_agent.py, examples/build_customized_multi_agents.py, examples/debate.py, examples/debate_simple.py, examples/write_tutorial.py, metagpt/actions/design_api_review.py, metagpt/actions/execute_task.py, metagpt/actions/search_and_summarize.py, metagpt/actions/write_docstring.py, metagpt/actions/write_review.py, metagpt/actions/write_tutorial.py
  1. Building Customized Agents
    · Single-Action vs. Multi-Action Agents
    · Agent Creation Flow
  2. Multi-Agent Debate Patterns
    · Implementation Details
    · Debate Orchestration
  3. Researcher and Searcher Roles
    · Researcher
    · Searcher and Sales
  4. Code Review (CR) Extension
    · Key Components
    · Data Flow for Code Review

## · Glossary  (L6217)
  源文件: Dockerfile, README.md, config/config2.example.yaml, docs/ACADEMIC_WORK.md, docs/NEWS.md, docs/README_CN.md, docs/README_FR.md, docs/README_JA.md, examples/exp_pool/decorator.py, metagpt/actions/action.py, metagpt/actions/action_node.py, metagpt/actions/design_api.py
  Core Concepts
    · Role
    · Action
    · Message
    · SOP (Standard Operating Procedure)
  Technical Jargon & Abbreviations
  Code Entity Mapping
    · Natural Language Space to Code Space: The SOP Lifecycle
    · Dynamic Intelligence Architecture
  Detailed Definitions
    · FileRepository
    · ActionNode Context & Parsing
    · Role Context (`RoleContext`)
    · Experience Retriever