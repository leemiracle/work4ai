# Skeleton: dspy（46 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 8KB | 3 | ~6 | 7 |
| 2 | Introduction & Core Concepts | L216 | 9KB | 5 | ~4 | 13 |
| 3 | Use Cases & Applications | L474 | 11KB | 4 | ~0 | 27 |
| 4 | Installation & Quick Start | L690 | 8KB | 2 | ~3 | 10 |
| 5 | Community & Resources | L943 | 6KB | 3 | ~1 | 13 |
| 6 | Core Architecture | L1099 | 7KB | 2 | ~0 | 10 |
| 7 | Package Structure & Public API | L1253 | 8KB | 3 | ~3 | 6 |
| 8 | Language Model Integration | L1467 | 8KB | 2 | ~1 | 18 |
| 9 | Signatures & Task Definition | L1657 | 10KB | 3 | ~5 | 12 |
| 10 | Adapter System | L1887 | 10KB | 3 | ~2 | 21 |
| 11 | Module System & Base Classes | L2078 | 10KB | 3 | ~4 | 14 |
| 12 | Example & Data Primitives | L2293 | 11KB | 3 | ~4 | 17 |
| 13 | Building DSPy Programs | L2556 | 13KB | 2 | ~1 | 10 |
| 14 | Predict Module | L2903 | 11KB | 2 | ~9 | 11 |
| 15 | Reasoning Strategies | L3150 | 11KB | 4 | ~6 | 25 |
| 16 | Tool Integration & Function Calling | L3375 | 10KB | 2 | ~0 | 19 |
| 17 | Custom Types & Multimodal Support | L3593 | 9KB | 2 | ~2 | 18 |
| 18 | Module Composition & Refinement | L3776 | 11KB | 2 | ~4 | 18 |
| 19 | History & Conversation Management | L3976 | 8KB | 3 | ~3 | 16 |
| 20 | Program Optimization | L4148 | 9KB | 2 | ~0 | 12 |
| 21 | Optimization Overview | L4316 | 12KB | 3 | ~8 | 17 |
| 22 | Evaluation Framework | L4565 | 11KB | 4 | ~5 | 25 |
| 23 | Few-Shot Optimizers | L4821 | 15KB | 5 | ~2 | 22 |
| 24 | MIPROv2: Instruction & Parameter Optimization | L5160 | 11KB | 4 | ~7 | 15 |
| 25 | GEPA & SIMBA: Reflective and Stochastic Optimization | L5422 | 11KB | 3 | ~3 | 19 |
| 26 | Fine-tuning & Weight Optimization | L5614 | 13KB | 4 | ~6 | 10 |
| 27 | Advanced Features | L5948 | 9KB | 4 | ~4 | 15 |
| 28 | Caching & Performance Optimization | L6184 | 9KB | 2 | ~2 | 9 |
| 29 | Parallel & Async Execution | L6368 | 10KB | 3 | ~4 | 17 |
| 30 | Streaming Output | L6549 | 7KB | 2 | ~3 | 11 |
| 31 | State Management & Serialization | L6731 | 9KB | 2 | ~8 | 12 |
| 32 | Assertions & Output Validation | L6936 | 8KB | 3 | ~4 | 18 |
| 33 | Code Execution & Sandboxing | L7105 | 11KB | 4 | ~6 | 20 |
| 34 | Configuration & Integration | L7390 | 7KB | 2 | ~7 | 10 |
| 35 | Settings & Configuration Management | L7563 | 9KB | 3 | ~4 | 7 |
| 36 | Model Providers & LiteLLM Integration | L7805 | 9KB | 2 | ~2 | 17 |
| 37 | Vector Databases & Retrieval | L8025 | 8KB | 2 | ~2 | 17 |
| 38 | Observability & Monitoring | L8197 | 10KB | 2 | ~5 | 20 |
| 39 | External Framework Integration | L8398 | 7KB | 2 | ~4 | 11 |
| 40 | Model Context Protocol (MCP) | L8537 | 8KB | 2 | ~2 | 6 |
| 41 | Development & Contributing | L8733 | 8KB | 3 | ~0 | 12 |
| 42 | Build System & CI/CD | L8949 | 5KB | 2 | ~6 | 12 |
| 43 | Testing Framework | L9121 | 12KB | 5 | ~3 | 21 |
| 44 | Documentation System | L9415 | 8KB | 2 | ~2 | 15 |
| 45 | Package Metadata & Release Process | L9589 | 10KB | 3 | ~4 | 14 |
| 46 | Glossary | L9866 | 12KB | 2 | ~3 | 43 |


## · Overview  (L6)
  源文件: README.md, docs/docs/index.md, docs/docs/static/img/logos/microsoft-ai.svg, docs/docs/stylesheets/extra.css, dspy/__init__.py, dspy/adapters/__init__.py, dspy/adapters/types/__init__.py
  Purpose and Scope
  What is DSPy?
  System Architecture
    · Layer Descriptions
  Core Programming Model
    · Signatures: Task Specification
    · Modules: Composable Components
    · Optimizers: Automatic Improvement
  Data Flow Through the System
  High-Level Capabilities
  Getting Started

## · Introduction & Core Concepts  (L216)
  源文件: README.md, docs/docs/learn/index.md, docs/docs/learn/programming/modules.md, docs/docs/learn/programming/overview.md, docs/docs/tutorials/build_ai_program/index.md, docs/docs/tutorials/conversation_history/index.md, docs/docs/tutorials/core_development/index.md, docs/docs/tutorials/index.md, docs/docs/tutorials/optimize_ai_program/index.md, docs/docs/tutorials/program_of_thought/index.ipynb, docs/docs/tutorials/rl_ai_program/index.md, docs/mkdocs.yml
  Core Philosophy: Programming, Not Prompting
    · The Compile-Then-Run Model
  The Three Core Abstractions
  Abstraction 1: Signatures
    · Defining Signatures
    · Key Components
  Abstraction 2: Modules
    · Core Module Types [docs/docs/learn/programming/modules.md:80-95]()
  Abstraction 3: Optimizers
    · Optimization Strategies

## · Use Cases & Applications  (L474)
  源文件: docs/docs/community/built-with-dspy.md, docs/docs/community/community-resources.md, docs/docs/community/use-cases.md, docs/docs/production/index.md, docs/docs/static/img/logos/aws.svg, docs/docs/static/img/logos/databricks-wordmark.svg, docs/docs/static/img/logos/databricks.svg, docs/docs/static/img/logos/dropbox-wordmark.svg, docs/docs/static/img/logos/dropbox.svg, docs/docs/tutorials/agents/index.ipynb, docs/docs/tutorials/classification_finetuning/index.ipynb, docs/docs/tutorials/custom_module/index.ipynb
  Overview of DSPy Applications
  Mathematical Reasoning
    · Overview
    · Architecture Pattern
    · Example Implementation
  Retrieval-Augmented Generation (RAG)
    · Overview
    · Architecture Pattern
    · Implementation
  Agent Systems & Fine-tuning
    · Overview
    · Architecture Pattern
    · Fine-tuning Agents
  Information & Entity Extraction
    · Overview
    · Implementation Example
  Multi-Hop Reasoning
    · Overview
    · Architecture Pattern
  Production Deployment
    · Lightweight & Production-Grade Options
    · Serialization

## · Installation & Quick Start  (L690)
  源文件: .github/.internal_dspyai/pyproject.toml, .github/.tmp/.generated-actions/run-pypi-publish-in-docker-container/action.yml, .github/workflows/dependency-range.yml, docs/docs/getting-started/metrics.md, docs/docs/index.md, docs/docs/static/img/logos/microsoft-ai.svg, docs/docs/stylesheets/extra.css, dspy/__metadata__.py, pyproject.toml, uv.lock
  Prerequisites
  Installation
    · Basic Installation
    · Optional Dependencies
  Configuration
    · Configuration Architecture
    · Setting Up Your Language Model
  Quick Start: Your First Program
    · Execution Flow: Natural Language to Code
    · Example: Basic QA with Chain of Thought
    · Example: Typed Signature
  Advanced Quick Start: Optimization
    · Simple Optimization Flow
    · Building a Metric
  Testing Your Installation

## · Community & Resources  (L943)
  源文件: docs/README.md, docs/docs/community/built-with-dspy.md, docs/docs/community/community-resources.md, docs/docs/community/use-cases.md, docs/docs/production/index.md, docs/docs/roadmap.md, docs/docs/static/img/logos/aws.svg, docs/docs/static/img/logos/databricks-wordmark.svg, docs/docs/static/img/logos/databricks.svg, docs/docs/static/img/logos/dropbox-wordmark.svg, docs/docs/static/img/logos/dropbox.svg, docs/requirements.txt
  Official Channels
  Documentation System Architecture
    · Build Configuration & Dependencies
    · Documentation Source to Entity Mapping
  Ecosystem & Learning Resources
    · Production Implementations
    · Research & Community Ports
  Deployment & Production Tooling

## · Core Architecture  (L1099)
  源文件: docs/docs/community/normalized-lm-api-migration.md, docs/overrides/main.html, dspy/__init__.py, dspy/adapters/__init__.py, dspy/adapters/types/__init__.py, dspy/clients/openai_format.py, dspy/core/__init__.py, dspy/core/types.py, tests/clients/test_lm_direct_live.py, tests/core/test_types.py
  Three-Layer Architecture
    · User-Facing Layer
    · Execution Layer
    · Infrastructure & Optimization
  Request Lifecycle: Code to Model Space
  Core Subsystems
    · Signature & Task Definition
    · Adapter System
    · Language Model Integration
    · Module System
    · Data & Primitives
  Summary of Infrastructure

## · Package Structure & Public API  (L1253)
  源文件: dspy/__init__.py, dspy/adapters/__init__.py, dspy/adapters/types/__init__.py, dspy/utils/__init__.py, dspy/utils/annotation.py, tests/utils/test_annotation.py
  Purpose and Scope
  Package Directory Structure
  Public API Aggregation
    · Natural Language Space to Code Entity Space Mapping
    · Wildcard and Explicit Imports
    · Utility Functions and Singletons
  Module Categorization
    · Data and Logic Flow Diagram
    · Core Subsystems
  Package Metadata and Initialization

## · Language Model Integration  (L1467)
  源文件: docs/docs/api/utils/Errors.md, docs/docs/faqs.md, docs/docs/learn/programming/language_models.md, dspy/clients/__init__.py, dspy/clients/base_lm.py, dspy/clients/cache.py, dspy/clients/databricks.py, dspy/clients/embedding.py, dspy/clients/lm.py, dspy/clients/lm_local.py, dspy/clients/openai.py, dspy/clients/provider.py
  LM Client Architecture
    · BaseLM Interface
    · LM Class (The LiteLLM Implementation)
    · LM Client Entity Mapping
  Provider Support via LiteLLM
    · Model Selection Hierarchy
    · LiteLLM Execution Flow
  Caching System
    · Cache Tiers
    · Cache Key Logic
    · Security and Serialization
  Three-Tier LM Selection Hierarchy
  Embedding Integration

## · Signatures & Task Definition  (L1657)
  源文件: docs/docs/api/primitives/Prediction.md, docs/docs/api/signatures/Signature.md, docs/docs/diving-deeper/signatures-in-depth.md, dspy/dsp/utils/__init__.py, dspy/evaluate/__init__.py, dspy/evaluate/auto_evaluation.py, dspy/evaluate/metrics.py, dspy/signatures/__init__.py, dspy/signatures/field.py, dspy/signatures/signature.py, tests/evaluate/test_auto_evaluation.py, tests/signatures/test_signature.py
  Purpose and Scope
  Overview
    · Natural Language to Code Entity Mapping
  Creating Signatures
    · String-Based Signatures
    · Class-Based Signatures
    · Dictionary-Based Signatures
  Field Definitions
    · Metadata and Constraints
    · Type Annotations and Custom Types
  Data Containers: Example & Prediction
    · Example Class
    · Prediction Class
  Signature Modification
  Implementation Details
    · SignatureMeta Metaclass
    · State Management

## · Adapter System  (L1887)
  源文件: docs/docs/api/adapters/Adapter.md, docs/docs/api/adapters/ChatAdapter.md, docs/docs/api/adapters/JSONAdapter.md, docs/docs/api/adapters/TwoStepAdapter.md, docs/docs/api/tools/Embeddings.md, docs/docs/api/utils/StreamListener.md, docs/docs/learn/programming/signatures.md, dspy/adapters/baml_adapter.py, dspy/adapters/base.py, dspy/adapters/chat_adapter.py, dspy/adapters/json_adapter.py, dspy/adapters/two_step_adapter.py
  Architecture Overview
  Adapter Execution Flow
  Base Adapter Class
    · Constructor Configuration
    · Native Feature Handling
  Core Adapter Implementations
    · ChatAdapter
    · JSONAdapter
    · XMLAdapter
    · TwoStepAdapter
    · BAMLAdapter
  Data Formatting and Parsing Utilities
  Multimodal and Native Feature Handling

## · Module System & Base Classes  (L2078)
  源文件: docs/docs/learn/index.md, docs/docs/learn/programming/modules.md, docs/docs/learn/programming/overview.md, dspy/predict/predict.py, dspy/primitives/base_module.py, dspy/primitives/module.py, dspy/utils/saving.py, dspy/utils/usage_tracker.py, tests/metadata/test_metadata.py, tests/predict/test_predict.py, tests/primitives/test_base_module.py, tests/primitives/test_module.py
  Purpose and Scope
  Core Abstractions
    · Module Base Class
    · Lifecycle & ProgramMeta
  Execution Flow
  Module Composition and Introspection
    · Parameter Traversal
    · Example Composition (Sequential)
  State Management and Serialization
    · Serialization Modes
    · Deep Copying
    · Whole Program Saving
  Data Primitives: Example and Prediction

## · Example & Data Primitives  (L2293)
  源文件: dspy/datasets/__init__.py, dspy/datasets/alfworld/__init__.py, dspy/datasets/alfworld/alfworld.py, dspy/datasets/alfworld/base_config.yml, dspy/datasets/colors.py, dspy/datasets/dataloader.py, dspy/datasets/dataset.py, dspy/datasets/gsm8k.py, dspy/datasets/hotpotqa.py, dspy/datasets/math.py, dspy/predict/aggregation.py, dspy/predict/parameter.py
  Overview
    · Data Flow and Entity Mapping
  The Example Class
    · Class Structure and Design
    · Initialization Patterns
    · Dictionary-Like Interface
  Input/Output Separation
    · The with_inputs() Method
    · Input and Label Extraction
  Prediction & Completions
    · Multi-Completion Handling
    · Majority Voting Logic
  Data Loading (DataLoader)
    · Supported Formats
    · Splitting and Sampling
  Serialization

## · Building DSPy Programs  (L2556)
  源文件: docs/docs/api/optimizers/SIMBA.md, docs/docs/cheatsheet.md, dspy/predict/best_of_n.py, dspy/predict/predict.py, dspy/predict/refine.py, dspy/primitives/base_module.py, dspy/teleprompt/infer_rules.py, dspy/teleprompt/simba.py, dspy/teleprompt/simba_utils.py, tests/predict/test_predict.py
  Getting Started: Basic Program Structure
  Core Building Blocks
    · Program Building Blocks Diagram
    · Signature: Task Specification
    · Predict: The Fundamental Module
    · Module: Composition and Subclassing
  Basic Module Usage
    · dspy.Predict: The Foundation
    · Program Execution Flow
  Configuration
    · Configuration Hierarchy
  Program Composition
    · Sequential Composition
    · Iterative Refinement and Best-of-N
  State Management and Persistence
    · Saving and Loading Programs
  Specialized Modules
    · Reasoning Modules
    · Tool Integration
    · Optimization via Teleprompters
  Next Steps

## · Predict Module  (L2903)
  源文件: docs/docs/api/evaluation/CompleteAndGrounded.md, docs/docs/api/evaluation/SemanticF1.md, docs/docs/api/modules/BestOfN.md, docs/docs/api/modules/ChainOfThought.md, docs/docs/api/modules/Module.md, docs/docs/api/modules/MultiChainComparison.md, docs/docs/api/modules/Predict.md, docs/docs/api/modules/Refine.md, dspy/predict/predict.py, dspy/primitives/base_module.py, tests/predict/test_predict.py
  Purpose and Scope
  Overview
    · System Flow: Natural Language to Code Entities
  Class Structure and Inheritance
  Initialization
    · Constructor Signature
    · Parameters
    · Initialization Process
  Execution Flow
    · Forward Method Entry Points
    · Preprocessing Stage
    · Postprocessing Stage
  Configuration Management
  State Management
    · Serialization: dump_state and load_state
    · Demonstrations (Few-Shot)
  Advanced Features
    · Asynchronous Execution
    · Streaming Support
  Summary of Key Functions

## · Reasoning Strategies  (L3150)
  源文件: docs/docs/api/tools/PythonInterpreter.md, docs/docs/diving-deeper/built-in-module-variants.md, docs/docs/diving-deeper/rlm.md, dspy/predict/__init__.py, dspy/predict/chain_of_thought.py, dspy/predict/program_of_thought.py, dspy/predict/react.py, dspy/predict/react_v2.py, dspy/predict/retry.py, dspy/primitives/code_interpreter.py, dspy/primitives/python_interpreter.py, dspy/primitives/runner.js
  Purpose and Scope
  Overview
  Module Architecture
  ChainOfThought
    · Implementation
  ReAct (Reasoning + Acting)
    · The Agent Loop
    · Implementation Details
  ProgramOfThought (PoT)
    · Execution Flow
  PythonInterpreter and Sandbox
  Native Reasoning Support
    · Reasoning Type and Adapters

## · Tool Integration & Function Calling  (L3375)
  源文件: docs/docs/api/modules/CodeAct.md, docs/docs/api/modules/ProgramOfThought.md, docs/docs/diving-deeper/bootstrap-fewshot-family.md, docs/docs/diving-deeper/choosing-an-optimizer.md, docs/docs/diving-deeper/flex.md, docs/docs/diving-deeper/gepa-in-depth.md, docs/docs/diving-deeper/metrics-and-evaluation.md, docs/docs/diving-deeper/modules.md, docs/docs/diving-deeper/saving-and-loading.md, docs/docs/diving-deeper/settings-and-context.md, docs/docs/diving-deeper/tools-react-and-mcp.md, docs/docs/learn/figures/native_tool_call.png
  Purpose and Scope
  Overview of Tool Integration
    · Tool Registration Workflow
  The `dspy.Tool` Type System
    · Metadata Extraction
    · Complex Type Support
  ReAct: Reasoning and Acting
    · ReAct Loop Mechanics
    · Trajectory Management
  CodeAct: Code-Based Tool Usage
    · Execution Flow
    · Limitations & Deprecation
  Native Function Calling Support
    · Adapter Behavior
    · External Tool Conversions
  Practical Examples
    · Basic ReAct Usage
    · Manual Tool Handling with ToolCalls

## · Custom Types & Multimodal Support  (L3593)
  源文件: docs/docs/api/evaluation/EvaluationResult.md, docs/docs/api/experimental/Citations.md, docs/docs/api/experimental/Document.md, docs/docs/api/primitives/Audio.md, docs/docs/api/primitives/Code.md, docs/docs/api/primitives/Image.md, docs/docs/api/primitives/ToolCalls.md, docs/docs/diving-deeper/adapters.md, docs/docs/tutorials/audio/index.ipynb, docs/docs/tutorials/image_generation_prompting/index.ipynb, dspy/adapters/types/audio.py, dspy/adapters/types/code.py
  The `Type` Extension System
  Built-in Custom Types
  Multimodal Types: Image, Audio, and File
    · Image
    · Audio
    · File
  Code Type
  Multimodal Data Flow: From Signature to LM
  Type Coercion and Parsing
  Optimization and Persistence

## · Module Composition & Refinement  (L3776)
  源文件: docs/docs/api/optimizers/SIMBA.md, docs/docs/cheatsheet.md, docs/docs/tutorials/output_refinement/best-of-n-and-refine.md, dspy/predict/avatar/__init__.py, dspy/predict/avatar/avatar.py, dspy/predict/avatar/models.py, dspy/predict/avatar/signatures.py, dspy/predict/best_of_n.py, dspy/predict/parallel.py, dspy/predict/refine.py, dspy/teleprompt/avatar_optimizer.py, dspy/teleprompt/infer_rules.py
  Purpose and Scope
  Composition Architecture
    · Module Wrapping and Coordination
  Parallel Execution
    · Implementation Details
  Agentic Composition: ReAct and Avatar
    · ReAct (Reasoning and Acting)
    · Avatar
    · Code Entity Space: Agentic Flow
  Error Handling: The Retry Mechanism
  Selection and Refinement Patterns
    · BestOfN
    · Refine
  Optimization of Composed Modules
    · Avatar Optimization Logic
    · SIMBA (Stochastic Introspective Mini-Batch Ascent)
    · Natural Language to Code Entity Mapping
  Summary of Composition Modules

## · History & Conversation Management  (L3976)
  源文件: docs/docs/tutorials/build_ai_program/index.md, docs/docs/tutorials/conversation_history/index.md, docs/docs/tutorials/core_development/index.md, docs/docs/tutorials/index.md, docs/docs/tutorials/optimize_ai_program/index.md, docs/docs/tutorials/program_of_thought/index.ipynb, docs/docs/tutorials/rl_ai_program/index.md, docs/mkdocs.yml, docs/overrides/partials/tabs.html, dspy/adapters/types/history.py, dspy/predict/knn.py, dspy/teleprompt/ensemble.py
  Overview
  The History Class
    · Structure and Implementation
    · History as a Signature Field
  Usage Patterns
    · Multi-Turn Workflow
    · Code Entity Space to Natural Language Space
  History in Demonstrations (Few-Shot)
    · JSON Serialization in Examples
  Integration with Retrieval (KNN)
  Debugging and Inspection
    · Key Implementation Files

## · Program Optimization  (L4148)
  源文件: docs/docs/api/optimizers/BetterTogether.md, docs/docs/learn/optimization/optimizers.md, docs/docs/learn/optimization/overview.md, dspy/evaluate/evaluate.py, dspy/teleprompt/__init__.py, dspy/teleprompt/bootstrap.py, dspy/teleprompt/copro_optimizer.py, dspy/teleprompt/random_search.py, dspy/teleprompt/signature_opt.py, dspy/teleprompt/teleprompt_optuna.py, tests/teleprompt/test_bettertogether.py, tests/teleprompt/test_random_search.py
  Purpose and Scope
  Optimization System Architecture
  Core Components
    · Teleprompter Base Class
    · Evaluation Framework (`dspy.Evaluate`)
    · Metric Functions
  Optimizer Categories
    · Few-Shot Optimizers
    · Instruction & Parameter Optimizers
    · Weight Optimization & Meta-Optimizers
  Optimization Workflow

## · Optimization Overview  (L4316)
  源文件: docs/docs/api/models/BaseLM.md, docs/docs/api/models/LM.md, docs/docs/api/modules/ReAct.md, docs/docs/api/optimizers/BetterTogether.md, docs/docs/api/optimizers/BootstrapFewShot.md, docs/docs/api/optimizers/BootstrapFewShotWithRandomSearch.md, docs/docs/api/optimizers/BootstrapFinetune.md, docs/docs/api/optimizers/BootstrapRS.md, docs/docs/api/optimizers/COPRO.md, docs/docs/api/optimizers/Ensemble.md, docs/docs/api/optimizers/InferRules.md, docs/docs/api/optimizers/KNNFewShot.md
  Why Optimize?
  The Three Inputs
  The Development Workflow
  How Optimizers Work
  Optimizer Categories
    · 1. Few-Shot Learning Optimizers
    · 2. Instruction & Parameter Optimizers
    · 3. Fine-tuning Optimizers
    · 4. Meta-Optimizers
  Choosing an Optimizer
    · Chaining and Ensembling

## · Evaluation Framework  (L4565)
  源文件: docs/docs/learn/evaluation/overview.md, docs/docs/tutorials/optimizer_tracking/child_run.png, docs/docs/tutorials/optimizer_tracking/experiment.png, docs/docs/tutorials/optimizer_tracking/index.md, docs/docs/tutorials/optimizer_tracking/parent_run.png, dspy/dsp/utils/__init__.py, dspy/evaluate/__init__.py, dspy/evaluate/auto_evaluation.py, dspy/evaluate/evaluate.py, dspy/evaluate/metrics.py, dspy/predict/parallel.py, dspy/signatures/__init__.py
  Overview
  Core Classes
    · `EvaluationResult`
    · `Evaluate`
  Execution Flow
  Metric Functions
    · Function Signature
    · Standard Metrics
    · Auto-Evaluation (LLM-as-a-Judge)
  Parallel Execution and Threading
    · Concurrency Details
  Result Display and Persistence
    · Table Display
    · File Export
  Integration with Optimizers
    · Optimization Workflow

## · Few-Shot Optimizers  (L4821)
  源文件: dspy/adapters/types/history.py, dspy/evaluate/evaluate.py, dspy/predict/chain_of_thought.py, dspy/predict/knn.py, dspy/teleprompt/__init__.py, dspy/teleprompt/bootstrap.py, dspy/teleprompt/copro_optimizer.py, dspy/teleprompt/ensemble.py, dspy/teleprompt/knn_fewshot.py, dspy/teleprompt/random_search.py, dspy/teleprompt/signature_opt.py, dspy/teleprompt/teleprompt_optuna.py
  Purpose and Scope
  Overview of Few-Shot Optimization
  The Bootstrapping Process
    · Conceptual Overview
    · Detailed Bootstrapping Mechanism
  Individual Optimizers
    · LabeledFewShot
    · BootstrapFewShot
    · BootstrapFewShotWithRandomSearch
    · KNNFewShot
    · BootstrapFewShotWithOptuna
  Interaction with Evaluation Framework
  Error Handling during Optimization

## · MIPROv2: Instruction & Parameter Optimization  (L5160)
  源文件: docs/docs/api/models/BaseLM.md, docs/docs/api/models/LM.md, docs/docs/api/modules/ReAct.md, docs/docs/api/optimizers/InferRules.md, docs/docs/api/optimizers/MIPROv2.md, docs/docs/api/primitives/Tool.md, dspy/propose/__init__.py, dspy/propose/dataset_summary_generator.py, dspy/propose/grounded_proposer.py, dspy/propose/propose_base.py, dspy/propose/utils.py, dspy/teleprompt/mipro_optimizer_v2.py
  How MIPROv2 Works
  Class Overview
  Constructor Parameters
  Auto-Run Modes
  Phase 1: Bootstrapping Few-Shot Examples
  Phase 2: Instruction Proposal via GroundedProposer
    · GroundedProposer Context Signals
  Phase 3: Bayesian Optimization via Optuna
    · Search Execution Flow
  Implementation Details
    · Instruction Set History
    · Dataset Summary Generation
    · Optuna Integration

## · GEPA & SIMBA: Reflective and Stochastic Optimization  (L5422)
  源文件: docs/docs/api/optimizers/GEPA/GEPA_Advanced.md, docs/docs/api/optimizers/GEPA/overview.md, docs/docs/api/optimizers/SIMBA.md, docs/docs/cheatsheet.md, docs/docs/tutorials/gepa_aime/index.ipynb, docs/docs/tutorials/gepa_facilitysupportanalyzer/index.ipynb, docs/docs/tutorials/gepa_papillon/index.ipynb, dspy/predict/best_of_n.py, dspy/predict/refine.py, dspy/teleprompt/bootstrap_trace.py, dspy/teleprompt/gepa/gepa.py, dspy/teleprompt/gepa/gepa_utils.py
  Purpose and Scope
  GEPA: Reflective Prompt Evolution
    · System Architecture & Data Flow
    · Key Classes and Functions
  SIMBA: Stochastic Introspective Mini-Batch Ascent
    · Optimization Strategy
    · Key Components
  InferRules: Iterative Rule Induction
    · Data Flow in InferRules
    · Key Classes
  Comparative Metrics and Iterative Refinement
    · Implementation Details: Trace Capture

## · Fine-tuning & Weight Optimization  (L5614)
  源文件: docs/docs/api/optimizers/BetterTogether.md, docs/docs/learn/optimization/optimizers.md, docs/docs/learn/optimization/overview.md, docs/docs/tutorials/rl_multihop/index.ipynb, docs/docs/tutorials/rl_papillon/index.ipynb, dspy/teleprompt/bettertogether.py, dspy/teleprompt/bootstrap_finetune.py, dspy/teleprompt/grpo.py, tests/teleprompt/test_bettertogether.py, tests/teleprompt/test_bootstrap_finetune.py
  Weight Optimization vs Prompt Optimization
  BootstrapFinetune: Supervised Fine-Tuning
    · Basic Usage
    · Compilation Pipeline
    · Key Parameters
  BetterTogether: Meta-Optimization
    · Common Strategies
  GRPO: Online Reinforcement Learning
    · Arbor Integration
    · RL Workflow Architecture
    · Key GRPO Parameters
  Infrastructure and Providers
    · Provider Capabilities
    · Data Flow for Fine-Tuning
  Comparison of Weight-Based Optimizers

## · Advanced Features  (L5948)
  源文件: dspy/adapters/types/citation.py, dspy/adapters/types/document.py, dspy/clients/__init__.py, dspy/clients/cache.py, dspy/clients/embedding.py, dspy/streaming/__init__.py, dspy/streaming/messages.py, dspy/streaming/streamify.py, dspy/streaming/streaming_listener.py, dspy/utils/asyncify.py, tests/adapters/test_citation.py, tests/adapters/test_document.py
  Feature Areas at a Glance
  Caching & Performance Optimization
    · How Caching Fits Into the LM Call
    · Cache Configuration
    · Cache Key Computation
  Parallel & Async Execution
    · Code Entity Map
    · `asyncify` Utility
  Streaming Output
    · Streaming Architecture
    · Key Streaming Components
  State Management & Serialization
    · Security: Unsafe LM State Keys
  Code Execution & Sandboxing
    · Architecture: PythonInterpreter
    · Key Security Features
  Observability
    · Usage and History

## · Caching & Performance Optimization  (L6184)
  源文件: docs/docs/tutorials/cache/index.md, dspy/clients/__init__.py, dspy/clients/cache.py, dspy/clients/disk_serialization.py, dspy/clients/embedding.py, dspy/utils/hasher.py, tests/clients/test_cache.py, tests/clients/test_disk_serialization.py, tests/clients/test_embedding.py
  Caching Architecture Overview
    · The Two-Tier Cache System
  Cache Key Computation
    · Computation Logic
  Cache Control with Rollout ID
    · Rollout ID Mechanics
  Security & Restricted Deserialization
    · Restricted Pickle Mode
  Global Configuration & Management
    · Configuration Function
    · Cache Persistence & Reset
  Performance Metrics & Tracking
    · Cache Hit Indicators
    · Provider-Side Caching

## · Parallel & Async Execution  (L6368)
  源文件: docs/docs/tutorials/async/index.md, docs/docs/tutorials/yahoo_finance_react/index.md, dspy/adapters/types/citation.py, dspy/adapters/types/document.py, dspy/predict/parallel.py, dspy/streaming/__init__.py, dspy/streaming/messages.py, dspy/streaming/streamify.py, dspy/streaming/streaming_listener.py, dspy/utils/asyncify.py, dspy/utils/parallelizer.py, tests/adapters/test_citation.py
  Overview
  Configuration & Context Isolation
    · Settings Management
    · Context Propagation
  Parallel Execution with `dspy.Parallel`
    · Implementation Details
  Async & Streaming Infrastructure
    · `asyncify` Utility
    · `streamify` Infrastructure
  Summary of Execution Primitives

## · Streaming Output  (L6549)
  源文件: docs/docs/tutorials/streaming/index.md, dspy/adapters/types/citation.py, dspy/adapters/types/document.py, dspy/streaming/__init__.py, dspy/streaming/messages.py, dspy/streaming/streamify.py, dspy/streaming/streaming_listener.py, dspy/utils/asyncify.py, tests/adapters/test_citation.py, tests/adapters/test_document.py, tests/streaming/test_streaming.py
  Overview
  Internal Architecture
  Key Components
    · `streamify`
    · `StreamListener`
    · `StatusStreamingCallback`
  Structured Output Streaming
  Settings and Configuration
    · Caching Behavior
  Usage Example

## · State Management & Serialization  (L6731)
  源文件: docs/docs/tutorials/saving/index.md, dspy/predict/predict.py, dspy/primitives/base_module.py, dspy/primitives/module.py, dspy/utils/saving.py, dspy/utils/usage_tracker.py, tests/metadata/test_metadata.py, tests/predict/test_predict.py, tests/primitives/test_base_module.py, tests/primitives/test_module.py, tests/utils/test_saving.py, tests/utils/test_usage_tracker.py
  Overview
  State Management Architecture
    · State Persistence Flow
  Module State Management
    · State Components
    · Security and Unsafe LM State
    · Implementation: Dump and Load
  Program Persistence (Whole Program Saving)
    · Save and Load Mechanism
    · Serializing Imported Modules
    · Environment Validation
  Serialization Utilities
    · Object Serialization
    · Dependency Tracking
  Security Considerations
    · Component Interaction Diagram
  Comparison of Persistence Methods

## · Assertions & Output Validation  (L6936)
  源文件: dspy/predict/__init__.py, dspy/predict/react.py, dspy/predict/react_v2.py, dspy/predict/retry.py, dspy/utils/exceptions.py, tests/predict/test_react.py, tests/predict/test_react_v2.py, tests/reliability/README.md, tests/reliability/__init__.py, tests/reliability/conftest.py, tests/reliability/generate/__init__.py, tests/reliability/generate/__main__.py
  Architecture Overview
  Structural Validation: Signatures & Types
    · Type Enforcement
  Procedural Validation: The Retry Mechanism
    · Signature Augmentation
    · Integration with Predictors
  Error Recovery and Exception Handling
    · Retryable vs. Fatal Errors
    · Context Window Management
  Validation in Agentic Loops (ReAct)
  Summary of Validation Patterns

## · Code Execution & Sandboxing  (L7105)
  源文件: docs/docs/api/modules/CodeAct.md, docs/docs/api/modules/ProgramOfThought.md, docs/docs/api/modules/RLM.md, docs/docs/api/tools/PythonInterpreter.md, docs/docs/diving-deeper/built-in-module-variants.md, docs/docs/diving-deeper/flex.md, docs/docs/diving-deeper/rlm.md, dspy/predict/code_act.py, dspy/predict/program_of_thought.py, dspy/predict/rlm.py, dspy/primitives/__init__.py, dspy/primitives/code_interpreter.py
  Overview
  Core Abstractions
    · `CodeInterpreter` Protocol
    · `FinalOutput`
    · `CodeInterpreterError` & `CodeExecutionError`
  `PythonInterpreter`
    · Architecture Diagram
    · Lifecycle
  Security Model
  JSON-RPC 2.0 Communication Protocol
  Recursive Language Model (RLM)
    · Built-in RLM Tools
  Component Map

## · Configuration & Integration  (L7390)
  源文件: docs/docs/api/utils/configure.md, docs/docs/api/utils/context.md, dspy/clients/databricks.py, dspy/clients/lm_local.py, dspy/clients/openai.py, dspy/clients/provider.py, dspy/clients/utils_finetune.py, dspy/dsp/utils/settings.py, tests/clients/test_lm_local.py, tests/utils/test_settings.py
  Configuration & Integration Landscape
  Configuration Architecture
  Global Settings Object
  Model Providers & Training Integration
  Model Context Protocol (MCP)
  Sub-page Reference

## · Settings & Configuration Management  (L7563)
  源文件: docs/docs/api/utils/configure.md, docs/docs/api/utils/context.md, dspy/__init__.py, dspy/adapters/__init__.py, dspy/adapters/types/__init__.py, dspy/dsp/utils/settings.py, tests/utils/test_settings.py
  Settings Architecture
  The `settings` Singleton
    · Configuration Resolution Logic
  Configuration Methods
    · `dspy.configure(**kwargs)`
    · `dspy.context(**kwargs)`
  Context Propagation in Parallelism
    · Parallel Propagation
    · Async Propagation
  Available Configuration Keys
  Configuration Resolution Hierarchy
  Typical Usage Patterns
    · Global Initialization
    · Nested Context Overrides
    · Async Task Isolation

## · Model Providers & LiteLLM Integration  (L7805)
  源文件: docs/docs/api/utils/Errors.md, docs/docs/faqs.md, docs/docs/learn/programming/language_models.md, dspy/clients/_litellm.py, dspy/clients/base_lm.py, dspy/clients/databricks.py, dspy/clients/lm.py, dspy/clients/lm_local.py, dspy/clients/openai.py, dspy/clients/provider.py, dspy/clients/utils_finetune.py, dspy/utils/dummies.py
  Purpose and Architecture
    · System-to-Code Mapping: LM Execution Flow
  The dspy.LM Class
    · Basic Construction
    · Model Types and API Formats
  Provider Support and Specialization
    · Major Provider Integration Patterns
    · OpenAI Reasoning Models (o1, o3, gpt-5)
    · Local Models via SGLang
  Fine-tuning and Training Jobs
    · Code Entity Space: Provider and Training Architecture
    · Fine-tuning Workflow
  Caching and Performance
    · Cache Control: rollout_id
  History and Usage Tracking

## · Vector Databases & Retrieval  (L8025)
  源文件: docs/docs/api/evaluation/Evaluate.md, docs/docs/api/evaluation/answer_exact_match.md, docs/docs/api/evaluation/answer_passage_match.md, docs/docs/api/models/Embedder.md, docs/docs/api/optimizers/KNN.md, dspy/dsp/colbertv2.py, dspy/dsp/utils/dpr.py, dspy/dsp/utils/utils.py, dspy/retrievers/__init__.py, dspy/retrievers/embeddings.py, dspy/utils/caching.py, dspy/utils/unbatchify.py
  Role of Retrieval in DSPy
  The Embedder Class
    · Key Features
    · Implementation Flow
  ColBERTv2 Integrations
    · Remote Client (`ColBERTv2`)
    · Local Retriever (`ColBERTv2RetrieverLocal`)
    · Local Reranker (`ColBERTv2RerankerLocal`)
  Vector Store & Embedding Retrieval
    · Search Strategy Selection
    · Unbatching and Efficiency
    · Data Flow: Query to Prediction
  Persistence and Serialization
    · Scoring Support
  Summary of Retrieval Components

## · Observability & Monitoring  (L8197)
  源文件: docs/docs/tutorials/observability/index.md, dspy/primitives/module.py, dspy/teleprompt/teleprompt.py, dspy/utils/callback.py, dspy/utils/callback_context.py, dspy/utils/inspect_history.py, dspy/utils/saving.py, dspy/utils/usage_tracker.py, tests/callback/test_callback.py, tests/callback/test_interpreter_callback.py, tests/callback/test_optimizer_callback.py, tests/clients/test_databricks.py
  Purpose and Scope
  Supported Observability Platforms
  Architecture Overview
    · Data Flow: Execution to Trace
  Built-in Observability Features
    · History Tracking (`dspy.inspect_history`)
    · Usage Tracking (`UsageTracker`)
    · Callback System (`BaseCallback`)
  MLflow Integration
    · Configuration Flow
    · Trace Inspection
  Logging & Trace Configuration
    · Multimodal and File Handling in Logs

## · External Framework Integration  (L8398)
  源文件: .github/.internal_dspyai/pyproject.toml, .github/.tmp/.generated-actions/run-pypi-publish-in-docker-container/action.yml, .github/workflows/dependency-range.yml, dspy/__metadata__.py, dspy/utils/langchain_tool.py, dspy/utils/mcp.py, pyproject.toml, tests/utils/resources/mcp_server.py, tests/utils/test_langchain_tool.py, tests/utils/test_mcp.py, uv.lock
  Purpose and Scope
  Integration Philosophy
    · Bridging External Entities to DSPy Core
  Package Dependencies
  LangChain Integration
    · Tool Conversion Implementation
  Model Context Protocol (MCP) Integration
    · Technical Workflow
    · MCP Data Flow
  Optuna Integration
    · Bayesian Search Backends
  Integration Summary Table

## · Model Context Protocol (MCP)  (L8537)
  源文件: docs/docs/tutorials/mcp/index.md, dspy/utils/langchain_tool.py, dspy/utils/mcp.py, tests/utils/resources/mcp_server.py, tests/utils/test_langchain_tool.py, tests/utils/test_mcp.py
  Overview
    · Key Capabilities
  Technical Architecture
    · Data Flow: MCP to DSPy
  Implementation Details
    · Tool Conversion (`convert_mcp_tool`)
    · Integration with `dspy.Tool`
  Integration with Code Entities
  Usage Patterns
    · 1. Initialization and Conversion
    · 2. Error Handling
    · 3. Comparison with Other Tool Integrations

## · Development & Contributing  (L8733)
  源文件: .github/.internal_dspyai/pyproject.toml, .github/.tmp/.generated-actions/run-pypi-publish-in-docker-container/action.yml, .github/workflows/build_and_release.yml, .github/workflows/dependency-range.yml, .github/workflows/docs-push.yml, .github/workflows/precommits_check.yml, .github/workflows/run_tests.yml, .pre-commit-config.yaml, CONTRIBUTING.md, dspy/__metadata__.py, pyproject.toml, uv.lock
  Development Environment Setup
    · Package Manager: uv
    · Code Quality Tools
    · Pre-commit Hooks
  Continuous Integration Pipeline
    · CI/CD Architecture
  Testing Framework
    · Test Categories
  Documentation System
  Package Metadata and Release Process
    · Release Workflow
  Contributing Guidelines
    · Finding an Issue
    · AI-Generated Contributions
    · Pull Request Process

## · Build System & CI/CD  (L8949)
  源文件: .github/.internal_dspyai/pyproject.toml, .github/.tmp/.generated-actions/run-pypi-publish-in-docker-container/action.yml, .github/workflows/build_and_release.yml, .github/workflows/dependency-range.yml, .github/workflows/docs-push.yml, .github/workflows/precommits_check.yml, .github/workflows/run_tests.yml, .pre-commit-config.yaml, CONTRIBUTING.md, dspy/__metadata__.py, pyproject.toml, uv.lock
  Build System
    · Package Discovery & Assets
  Dependency Management
    · Core Dependencies
    · Optional Extras
  Development Tooling
    · uv & Virtual Environments
    · Linting & Formatting
  CI/CD Pipeline
    · Automated Test Suites
    · Dependency Range Validation
  Release Process
    · Compatibility Alias

## · Testing Framework  (L9121)
  源文件: .github/workflows/build_and_release.yml, .github/workflows/docs-push.yml, .github/workflows/precommits_check.yml, .github/workflows/run_tests.yml, .pre-commit-config.yaml, CONTRIBUTING.md, tests/conftest.py, tests/reliability/README.md, tests/reliability/__init__.py, tests/reliability/conftest.py, tests/reliability/generate/__init__.py, tests/reliability/generate/__main__.py
  Purpose and Scope
  Test Organization
    · Test Directory Structure
  Pytest Configuration
    · Configuration and Hooks
  Test Dependencies
    · Core Testing Dependencies
    · Extended Testing Dependencies
  Test Categories and Markers
    · Specialized Markers
  Reliability and Judge Infrastructure
    · Natural Language to Code Entity Mapping: Reliability
    · Key Reliability Components
  Integration Testing with LiteLLM Server
    · LM Simulation Flow
  Running Tests Locally
    · Basic Test Execution
    · Running Specialized Tests
  CI/CD Pipeline
    · LLM Call Test Job Infrastructure
  Testing Best Practices

## · Documentation System  (L9415)
  源文件: docs/README.md, docs/docs/api/index.md, docs/docs/tutorials/build_ai_program/index.md, docs/docs/tutorials/conversation_history/index.md, docs/docs/tutorials/core_development/index.md, docs/docs/tutorials/index.md, docs/docs/tutorials/optimize_ai_program/index.md, docs/docs/tutorials/program_of_thought/index.ipynb, docs/docs/tutorials/rl_ai_program/index.md, docs/mkdocs.yml, docs/overrides/partials/tabs.html, docs/requirements.txt
  Overview
  Documentation Architecture
    · Data Flow Diagram
  API Reference Generation
    · Automated Documentation Scripts
    · Code Entity to Documentation Mapping
  Tutorial Organization
    · Learning Path Mapping
    · Key Tutorial Sections
  Contribution Workflow
    · Build Steps
    · Deployment Configuration

## · Package Metadata & Release Process  (L9589)
  源文件: .github/.internal_dspyai/internals/build-and-release.md, .github/.internal_dspyai/internals/release-checklist.md, .github/.internal_dspyai/pyproject.toml, .github/.tmp/.generated-actions/run-pypi-publish-in-docker-container/action.yml, .github/workflows/build_and_release.yml, .github/workflows/dependency-range.yml, .github/workflows/docs-push.yml, .github/workflows/precommits_check.yml, .github/workflows/run_tests.yml, .pre-commit-config.yaml, CONTRIBUTING.md, dspy/__metadata__.py
  Package Metadata
    · Metadata Validation
  Published Packages
  Version & Name Marker System
  Release Workflow
    · Jobs Overview
    · Job: `extract-tag`
    · Job: `build-and-publish-test-pypi`
    · Job: `build-and-publish-pypi`
  `pyproject.toml` Configuration
    · Build System
    · Core Dependencies
    · Optional Dependency Groups
  Code Entity Map

## · Glossary  (L9866)
  源文件: README.md, docs/docs/api/tools/PythonInterpreter.md, docs/docs/api/utils/Errors.md, docs/docs/faqs.md, docs/docs/learn/programming/language_models.md, docs/docs/learn/programming/signatures.md, dspy/__init__.py, dspy/adapters/__init__.py, dspy/adapters/base.py, dspy/adapters/chat_adapter.py, dspy/adapters/json_adapter.py, dspy/adapters/types/__init__.py
  Core Concepts & Data Primitives
    · Signature
    · Module
    · Example
  The Adapter System
    · ChatAdapter
    · JSONAdapter
    · Adapter Flow Diagram
  Optimization (Teleprompters)
    · Bootstrapping
    · MIPROv2 (Multi-stage Instruction Proposal and Response Optimization)
    · GEPA (Reflective Prompt Evolution)
    · GroundedProposer
  Execution & Sandboxing
    · PythonInterpreter
  Evaluation Framework
    · Evaluate
    · Metric
  Technical Abbreviations & Jargon