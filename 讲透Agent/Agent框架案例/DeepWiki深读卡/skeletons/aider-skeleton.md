# Skeleton: aider（55 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 9KB | 6 | ~2 | 23 |
| 2 | Getting Started | L254 | 8KB | 2 | ~1 | 19 |
| 3 | Key Concepts and Terminology | L420 | 8KB | 2 | ~5 | 23 |
| 4 | Core Architecture | L570 | 10KB | 5 | ~2 | 23 |
| 5 | Application Entry Point and Main Loop | L820 | 16KB | 5 | ~5 | 17 |
| 6 | Coder Orchestration System | L1210 | 15KB | 6 | ~3 | 18 |
| 7 | Commands and User Interactions | L1567 | 13KB | 6 | ~8 | 18 |
| 8 | Model Management and LLM Integration | L1900 | 15KB | 5 | ~0 | 29 |
| 9 | Input/Output and Terminal Interface | L2289 | 8KB | 3 | ~4 | 15 |
| 10 | Edit Strategies and Code Modification | L2495 | 11KB | 3 | ~4 | 17 |
| 11 | Edit Format Implementations | L2762 | 11KB | 3 | ~2 | 31 |
| 12 | Search and Replace Logic | L3010 | 15KB | 8 | ~3 | 12 |
| 13 | Diff Generation and Display | L3391 | 9KB | 2 | ~2 | 12 |
| 14 | Prompt Engineering and Templates | L3556 | 8KB | 2 | ~3 | 16 |
| 15 | Message Formatting and Chat History | L3714 | 9KB | 3 | ~1 | 9 |
| 16 | Repository Understanding and Context | L3910 | 12KB | 4 | ~3 | 19 |
| 17 | Repository Mapping System | L4202 | 13KB | 4 | ~7 | 31 |
| 18 | File Management and Tracking | L4512 | 10KB | 4 | ~1 | 18 |
| 19 | Git Integration and Version Control | L4756 | 22KB | 12 | ~7 | 14 |
| 20 | File Watching and AI Comments | L5386 | 9KB | 3 | ~6 | 14 |
| 21 | Code Quality and Linting | L5628 | 16KB | 7 | ~8 | 5 |
| 22 | User Interaction Modes | L6033 | 8KB | 3 | ~4 | 19 |
| 23 | Command Line Interface | L6254 | 10KB | 3 | ~5 | 14 |
| 24 | Streamlit Web GUI | L6499 | 9KB | 2 | ~6 | 8 |
| 25 | Voice-to-Code Mode | L6726 | 7KB | 2 | ~2 | 15 |
| 26 | Copy/Paste Integration with Web Chat UIs | L6907 | 7KB | 2 | ~3 | 7 |
| 27 | Architect Mode | L7048 | 8KB | 2 | ~4 | 13 |
| 28 | Web Content Integration | L7210 | 9KB | 5 | ~3 | 12 |
| 29 | Web Scraping Architecture | L7458 | 10KB | 2 | ~1 | 12 |
| 30 | SSL Verification Configuration | L7714 | 10KB | 3 | ~1 | 5 |
| 31 | Model Configuration and Capabilities | L7946 | 9KB | 3 | ~11 | 14 |
| 32 | Model Settings and Behavioral Configuration | L8180 | 11KB | 3 | ~6 | 19 |
| 33 | Model Metadata and Technical Capabilities | L8482 | 11KB | 3 | ~7 | 12 |
| 34 | Multi-Provider LLM Integration | L8713 | 9KB | 3 | ~5 | 16 |
| 35 | Three-Tier Model System | L8909 | 11KB | 5 | ~1 | 19 |
| 36 | Reasoning and Thinking Token Configuration | L9220 | 7KB | 2 | ~1 | 9 |
| 37 | Development and Quality Assurance | L9357 | 6KB | 2 | ~4 | 9 |
| 38 | Benchmarking System Architecture | L9528 | 10KB | 2 | ~2 | 14 |
| 39 | Testing Infrastructure | L9792 | 11KB | 2 | ~5 | 19 |
| 40 | Performance Leaderboards | L10022 | 8KB | 3 | ~0 | 23 |
| 41 | Configuration and Deployment | L10212 | 8KB | 2 | ~2 | 16 |
| 42 | Configuration System | L10370 | 8KB | 3 | ~3 | 15 |
| 43 | Dependency Management | L10547 | 13KB | 4 | ~14 | 13 |
| 44 | Build and Version Management | L10871 | 9KB | 2 | ~6 | 19 |
| 45 | Utilities and Supporting Systems | L11124 | 8KB | 2 | ~2 | 8 |
| 46 | Core Utility Functions | L11315 | 9KB | 3 | ~6 | 10 |
| 47 | Error Reporting and Version Checking | L11551 | 15KB | 5 | ~8 | 12 |
| 48 | Package Installation Utilities | L11963 | 12KB | 4 | ~5 | 18 |
| 49 | Help and Documentation System | L12248 | 6KB | 2 | ~2 | 6 |
| 50 | Help System Architecture | L12389 | 7KB | 2 | ~4 | 17 |
| 51 | HelpCoder and Context Assembly | L12566 | 7KB | 3 | ~4 | 12 |
| 52 | Analytics and Self-Improvement | L12739 | 6KB | 2 | ~0 | 7 |
| 53 | Usage Analytics | L12899 | 8KB | 2 | ~4 | 11 |
| 54 | Self-Referential Development Metrics | L13083 | 9KB | 2 | ~7 | 8 |
| 55 | Glossary | L13319 | 10KB | 2 | ~3 | 39 |


## · Overview  (L6)
  源文件: HISTORY.md, README.md, aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/models.py, aider/repo.py, aider/repomap.py, aider/voice.py, aider/website/HISTORY.md
  Purpose and Scope
  What is Aider?
  High-Level Architecture
    · System Component Diagram
  Core Components
    · Application Entry Point
    · Coder Orchestration
    · Model and LLM Integration
    · Edit Strategy System
    · Repository Understanding
    · Git Integration
  Configuration System

## · Getting Started  (L254)
  源文件: .github/workflows/docker-build-test.yml, .github/workflows/docker-release.yml, .github/workflows/pages.yml, .github/workflows/release.yml, aider/website/_includes/get-started.md, aider/website/_includes/help.md, aider/website/_posts/2024-05-13-models-over-time.md, aider/website/docs/config/api-keys.md, aider/website/docs/install.md, aider/website/docs/install/optional.md, aider/website/docs/more/edit-formats.md, aider/website/docs/troubleshooting.md
  Installation
    · Recommended: Quick Install Scripts
    · Manual Installation Methods
  Initial Setup and Onboarding
    · Automatic Model Selection
    · Onboarding Logic Flow
  Configuration
    · API Key Configuration
    · Token Management
  First Use
    · Adding Files to Context
    · The Interaction Loop
    · Optional Dependencies and Docker

## · Key Concepts and Terminology  (L420)
  源文件: HISTORY.md, README.md, aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/models.py, aider/repo.py, aider/repomap.py, aider/voice.py, aider/website/HISTORY.md
  Edit Formats
    · Fencing
  Repository Map (repo-map)
  Chat Modes and File Management
  The Weak/Architect Model Pattern
    · Three-Tier Architecture
    · Data Flow: From Intent to Code
  Technical Terminology Reference
    · Component Interaction: Edit Strategy Selection

## · Core Architecture  (L570)
  源文件: MANIFEST.in, aider/__init__.py, aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/help_pats.py, aider/io.py, aider/llm.py, aider/main.py, aider/models.py, aider/repo.py, aider/repomap.py
  Purpose and Scope
  Architectural Overview
  Central Orchestrator: The Coder Class
  Core Components
    · Application Entry and Initialization
    · Command System
    · Model Management
    · Input/Output System
    · Git Integration
  Request Processing Flow

## · Application Entry Point and Main Loop  (L820)
  源文件: aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/models.py, aider/onboarding.py, aider/repo.py, aider/repomap.py, aider/voice.py, aider/website/docs/languages.md, pytest.ini
  Purpose and Scope
  The `main()` Function
  Initialization Flow Overview
  Configuration File Loading
    · YAML Configuration Search Path
    · Environment Variable Loading
    · Precedence Summary
  Argument Parsing with ConfigArgParse
    · Two-Pass Parsing
    · Argument Groups
  Special Execution Modes
    · Shell Completion Generation
    · Analytics Management
    · Version Check and Update
    · GUI Mode
  Git Repository Initialization
    · Git Root Discovery
    · Repository Setup or Creation
    · Gitignore Management
  Model Registration and Selection
    · Model Settings Registration
    · Model Metadata Registration
    · Model Selection with Onboarding
    · Model Instance Creation
  Coder Creation and Execution
    · Coder Factory Pattern
    · Main Execution Flow
  Main Interaction Loop
    · Input Collection Phase
    · Message Preprocessing Phase
    · Command Execution Branch
    · Message Execution Phase
  Loop Control Flow and Exit
    · Interrupt Handling
    · Return Modes
    · Error Handling

## · Coder Orchestration System  (L1210)
  源文件: aider/args.py, aider/coders/base_coder.py, aider/coders/chat_chunks.py, aider/commands.py, aider/help.py, aider/io.py, aider/main.py, aider/models.py, aider/repo.py, aider/repomap.py, aider/voice.py, aider/website/docs/languages.md
  Core Responsibilities
  Orchestration Architecture
  Coder Factory Pattern
  Initialization
  Core State Management
    · File Tracking
    · Message History
    · Commit Tracking
  Request Processing Pipeline
  Integration with Subsystems
    · Context Generation via RepoMap
    · Command Integration
    · Quality Control and Reflection

## · Commands and User Interactions  (L1567)
  源文件: aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/help.py, aider/io.py, aider/main.py, aider/models.py, aider/repo.py, aider/repomap.py, aider/voice.py, aider/website/docs/languages.md, aider/website/docs/usage/commands.md
  Overview
  Command Detection and Dispatch Flow
  Command Method Convention
  Available Commands by Category
    · File Management Commands
    · Git Operations
    · Chat History and Model Configuration
    · Interaction Modes
  SwitchCoder Exception Mechanism
  Auto-Completion System
  Shell Command Execution
  File Management Commands
  Commands Class Architecture

## · Model Management and LLM Integration  (L1900)
  源文件: MANIFEST.in, aider/__init__.py, aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/exceptions.py, aider/help_pats.py, aider/io.py, aider/llm.py, aider/main.py, aider/models.py, aider/repo.py
  Overview
  Model Class Architecture
  Model Configuration System
  Model Initialization Flow
  ModelInfoManager and Metadata Caching
  LiteLLM Integration Architecture
  Three-Tier Model System
  Special Model Features
    · Reasoning and Thinking Tokens
    · Prompt Caching and Warming
  Model Validation and Sanity Checks

## · Input/Output and Terminal Interface  (L2289)
  源文件: aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/mdstream.py, aider/models.py, aider/repo.py, aider/repomap.py, aider/voice.py, aider/waiting.py, aider/website/_includes/multi-line.md
  System Architecture
    · Terminal Interaction Components
  InputOutput Class Initialization
  User Input Collection System
    · Auto-completion Implementation
    · Voice Input
  Visual Feedback and Waiting Systems
    · Waiting Spinner
    · Markdown Streaming
  Confirmation Dialog System
    · Confirmation Logic
  Output Formatting and Styling
  File I/O Operations

## · Edit Strategies and Code Modification  (L2495)
  源文件: aider/coders/__init__.py, aider/coders/ask_prompts.py, aider/coders/base_prompts.py, aider/coders/editblock_coder.py, aider/coders/editblock_func_coder.py, aider/coders/editblock_func_prompts.py, aider/coders/editblock_prompts.py, aider/coders/patch_prompts.py, aider/coders/shell.py, aider/coders/single_wholefile_func_coder.py, aider/coders/single_wholefile_func_prompts.py, aider/coders/udiff_prompts.py
  Purpose and Scope
  The Strategy Pattern Architecture
  Core Interface Methods
  Edit Format Characteristics
  Edit Processing Pipeline
  SEARCH/REPLACE Block Format
  Whole File Format
  Matching and Replacement Logic
    · Ellipsis Handling
  Diff Generation and Display
  Error Handling and Reflection
  Deprecated Function-Call Strategies

## · Edit Format Implementations  (L2762)
  源文件: aider/coders/__init__.py, aider/coders/architect_coder.py, aider/coders/architect_prompts.py, aider/coders/ask_coder.py, aider/coders/context_coder.py, aider/coders/context_prompts.py, aider/coders/editblock_coder.py, aider/coders/editblock_fenced_coder.py, aider/coders/editblock_fenced_prompts.py, aider/coders/editblock_func_coder.py, aider/coders/editblock_func_prompts.py, aider/coders/editor_diff_fenced_coder.py
  Purpose and Scope
  Coder Implementation Architecture
    · Class Hierarchy and Edit Formats
  EditBlockCoder - SEARCH/REPLACE Format
    · Edit Format Structure
    · Parsing and Application Logic
    · Replacement Strategies
  WholeFileCoder - Complete File Replacement
    · Parsing Logic
  Architect Mode and Two-Stage Editing
  UnifiedDiffCoder - Standard Diff Format
  Specialized Coder Implementations
  Deprecated Function-Based Coders

## · Search and Replace Logic  (L3010)
  源文件: aider/coders/ask_coder.py, aider/coders/editblock_fenced_coder.py, aider/coders/help_coder.py, aider/coders/patch_coder.py, aider/coders/search_replace.py, aider/coders/udiff_coder.py, aider/website/docs/ctags.md, aider/website/examples/README.md, tests/basic/test_editblock.py, tests/basic/test_find_or_blocks.py, tests/fixtures/chat-history-search-replace-gold.txt, tests/fixtures/chat-history.md
  SEARCH/REPLACE Block Format
  Block Parsing and Extraction
    · Pattern Matching
    · Filename Extraction
    · Shell Command Extraction
  Matching Strategies
    · Strategy Cascade
    · Perfect Match Strategy
    · Whitespace Handling Strategy
    · Ellipsis Handling Strategy
    · Fuzzy Matching (Disabled)
  Application Flow
    · Edit Application Process
  Error Handling and Diagnostics
    · Failed Match Response
    · Similar Line Detection
  Alternative Search and Replace Implementations
    · Unified Diff Coder (`udiff`)
    · Patch Coder (`patch`)
    · Search Replace Module Utilities

## · Diff Generation and Display  (L3391)
  源文件: aider/coders/__init__.py, aider/coders/editblock_coder.py, aider/coders/editblock_func_coder.py, aider/coders/editblock_func_prompts.py, aider/coders/single_wholefile_func_coder.py, aider/coders/single_wholefile_func_prompts.py, aider/coders/wholefile_coder.py, aider/coders/wholefile_func_coder.py, aider/coders/wholefile_func_prompts.py, aider/diffs.py, aider/mdstream.py, aider/waiting.py
  Overview
    · Natural Language to Code Entity Mapping: Diff Workflow
  Core Diff Generation Algorithm
    · The diff_partial_update Function
    · Finding the Last Non-Deleted Line
    · Progress Bar Visualization
  Incremental Display via MarkdownStream
    · Live Rendering Logic
    · Key Classes in mdstream.py
  Integration with Coder Implementations
    · WholeFileCoder
    · EditBlockCoder Matching and Diffs
    · Function Call Diffs
  Implementation Details and Edge Cases
    · Assertion for Line Endings
    · Backtick Selection
    · Handling New Files
    · Waiting Spinner

## · Prompt Engineering and Templates  (L3556)
  源文件: aider/coders/ask_prompts.py, aider/coders/base_prompts.py, aider/coders/editblock_fenced_prompts.py, aider/coders/editblock_prompts.py, aider/coders/editor_diff_fenced_coder.py, aider/coders/editor_diff_fenced_prompts.py, aider/coders/editor_editblock_prompts.py, aider/coders/editor_whole_prompts.py, aider/coders/patch_prompts.py, aider/coders/shell.py, aider/coders/udiff_prompts.py, aider/coders/wholefile_prompts.py
  Prompt Class Hierarchy
    · Class Inheritance Structure
  Prompt Template Attributes
    · Core Template Attributes
    · Behavior Modifier Attributes
  Message Assembly and History Management
    · Message Context Mapping
    · Chat History Summarization
    · Message Sanitization
  Edit Strategy Templates
    · SEARCH/REPLACE (EditBlock)
    · V4A Patch Format
    · Unified Diff (UDiff)
    · Whole File
  Specialized Task Prompts
    · Git Commits
    · Command Outputs
    · Ask Mode

## · Message Formatting and Chat History  (L3714)
  源文件: aider/coders/udiff_simple.py, aider/coders/udiff_simple_prompts.py, aider/history.py, aider/prompts.py, aider/sendchat.py, tests/basic/test_history.py, tests/basic/test_repo.py, tests/basic/test_sendchat.py, tests/scrape/test_playwright_disable.py
  Message Structure and Layers
    · Natural Language Space to Code Entity Space: Message Assembly
    · System Messages
    · Context Messages
  Message Role Alternation
    · sanity_check_messages()
    · ensure_alternating_roles()
  Chat History Management and Summarization
    · The Summarization Algorithm
    · summarize_all()
    · Chat History Summarization Flow
  Message Content Formatting
    · File Content Formatting
    · Edit Format Changes
    · Commit Message Generation

## · Repository Understanding and Context  (L3910)
  源文件: aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/models.py, aider/queries/tree-sitter-language-pack/bash-tags.scm, aider/queries/tree-sitter-languages/bash-tags.scm, aider/repo.py, aider/repomap.py, aider/voice.py, aider/website/docs/languages.md
  Purpose and Scope
  Core Components
  The RepoMap Class
    · Initialization Parameters
  Tag Extraction Process
    · Language Support via Tree-sitter Queries
  Relevance Ranking with PageRank
    · Personalization Strategy
  Context Generation and Token Budget
  Git Integration and Version Control
  Code Quality and Linting
  Supported Languages

## · Repository Mapping System  (L4202)
  源文件: aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/models.py, aider/queries/tree-sitter-language-pack/arduino-tags.scm, aider/queries/tree-sitter-language-pack/bash-tags.scm, aider/queries/tree-sitter-language-pack/c-tags.scm, aider/queries/tree-sitter-language-pack/chatito-tags.scm, aider/queries/tree-sitter-language-pack/commonlisp-tags.scm, aider/queries/tree-sitter-language-pack/cpp-tags.scm
  Architecture Overview
  Tag Extraction with Tree-Sitter
    · Tag Structure
  Caching System
  Reference Graph and PageRank
    · Graph Construction
  Token Budget Management
    · Token Budget Calculation
  Output Formatting
    · Format Structure
  Supported Languages

## · File Management and Tracking  (L4512)
  源文件: aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/help.py, aider/io.py, aider/main.py, aider/models.py, aider/repo.py, aider/repomap.py, aider/special.py, aider/voice.py, aider/website/docs/languages.md
  Purpose and Scope
  File Types and State Management
    · File State Transitions
  File Addition Mechanisms
    · Command-Line Initialization
    · Interactive File Addition
  File Mention Detection System
    · Detection Strategies
  Path Resolution and Encoding
    · Absolute Path Normalization
    · Encoding Validation
  File Removal and Filtering
    · The `/drop` Command
    · Gitignore and .aiderignore
    · Important Files List
  File Management Architecture

## · Git Integration and Version Control  (L4756)
  源文件: aider/coders/udiff_simple.py, aider/coders/udiff_simple_prompts.py, aider/help.py, aider/website/docs/git.md, aider/website/docs/install/docker.md, scripts/blame.py, scripts/issues.py, tests/basic/test_coder.py, tests/basic/test_commands.py, tests/basic/test_history.py, tests/basic/test_repo.py, tests/basic/test_sanity_check_repo.py
  Overview of Git Integration
  GitRepo Class
    · Initialization and Configuration
  Commit Attribution System
    · Attribution Logic Flow
    · Attribution Behavior Summary
    · Implementation of Attribution
  Auto-Commits and Dirty Commits
    · Auto-Commits
    · Dirty Commits
  Git-Related Commands
    · /commit Command
    · /undo Command
    · /diff Command
  Commit Message Generation
  Integration with Coder Class
    · Coder-GitRepo Class Relationship
  Error Handling

## · File Watching and AI Comments  (L5386)
  源文件: aider/copypaste.py, aider/watch.py, aider/watch_prompts.py, aider/website/assets/copypaste.jpg, aider/website/assets/copypaste.mp4, aider/website/assets/watch.jpg, aider/website/assets/watch.mp4, aider/website/docs/usage/copypaste.md, aider/website/docs/usage/watch.md, benchmark/prompts.py, tests/basic/test_watch.py, tests/fixtures/watch.js
  Purpose and Scope
  Overview
    · Data Flow and System Interaction
  AI Comment Syntax and Detection
    · Comment Pattern
    · Action Types
    · Multi-Language Support
  FileWatcher Architecture
    · Class Definition and Key Entities
    · Monitoring Lifecycle
  Gitignore Integration
    · load_gitignores Logic
    · Built-in Exclusions
  Processing and Context Assembly
    · AI Comment Extraction
    · TreeContext Formatting
  Copy/Paste Mode Interaction
    · ClipboardWatcher Architecture
    · Comparison of Watcher Systems

## · Code Quality and Linting  (L5628)
  源文件: aider/linter.py, aider/run_cmd.py, aider/website/docs/usage/lint-test.md, tests/basic/test_linter.py, tests/basic/test_run_cmd.py
  Overview
    · Lint-and-Fix Reflection Cycle
  Core Linting Architecture
    · Linter Class Structure
    · Key Methods
  Language Support and Extensibility
    · Python Linting Pipeline
    · Fallback: Tree-sitter Syntax Checking
    · Custom Linter Registration
  Tree-sitter Error Detection
    · Detection Pipeline
    · Error Node Detection
    · Language Exclusions
  Error Reporting with Context
    · Report Format
  See relevant line(s) below marked with █.
    · TreeContext Integration
  External Tool Execution
    · Command Execution Flow
    · Path Quoting and Safety
    · Error Parsing
  Auto-Lint Feedback Loop
    · Feedback Loop Integration
  Test Command Integration
    · Configuration and Execution
    · Subprocess vs Pexpect
  Linter Test Suite
    · Test Coverage

## · User Interaction Modes  (L6033)
  源文件: aider/args.py, aider/coders/architect_coder.py, aider/coders/architect_prompts.py, aider/coders/base_coder.py, aider/coders/editor_editblock_coder.py, aider/coders/editor_whole_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/models.py, aider/repo.py, aider/repomap.py
  Overview of Interaction Modes
    · Interaction Modes Architecture
  Mode Comparison
  Mode Selection Flow
  Common Components Across Modes
    · InputOutput System
    · Coder Integration
  Mode-Specific Features
    · CLI Features
    · Voice Mode Features
    · Architect Mode Features
    · File Watcher Mode
  Mode Switching at Runtime

## · Command Line Interface  (L6254)
  源文件: aider/args.py, aider/args_formatter.py, aider/coders/base_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/models.py, aider/onboarding.py, aider/repo.py, aider/repomap.py, aider/voice.py, aider/website/docs/languages.md
  Purpose and Scope
  Argument Parsing System
    · Parser Configuration
    · Argument Groups
  Configuration Precedence and Layering
    · Precedence Diagram
    · Configuration File Discovery
  Environment Variable Processing
    · .env File Loading
    · Command Line Environment Variable Overrides
  Initialization Sequence
    · Initialization Flow
    · Key Initialization Steps
  Model Selection and Registration
    · Model Settings and Metadata
    · Model Aliases
  Special CLI Flags and Exit Paths
  Color and I/O Configuration
    · Color Theme Presets
    · Autocompletion
  Onboarding Flow

## · Streamlit Web GUI  (L6499)
  源文件: aider/gui.py, aider/report.py, aider/scrape.py, aider/urls.py, aider/utils.py, aider/versioncheck.py, scripts/update-docs.sh, tests/browser/test_browser.py
  Purpose and Scope
  Architecture Overview
    · Component Relationship Diagram
  Entry Point and Initialization
    · Page Configuration
    · GUI Class Initialization
  Cached Resource Management
    · Coder Instance Caching
    · State Instance Caching
  Custom I/O Handling: CaptureIO
    · CaptureIO Implementation
  Chat Processing Flow
    · Data Flow Diagram: User Prompt to Code Change
    · Processing Implementation
  Web Content Integration
  Undo Functionality
  UI Components and State

## · Voice-to-Code Mode  (L6726)
  源文件: aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/models.py, aider/repo.py, aider/repomap.py, aider/voice.py, aider/website/docs/languages.md, aider/website/docs/usage/tips.md, aider/website/docs/usage/tutorials.md
  Purpose and Scope
  Overview
  Voice Input Flow
  Key Classes and Functions
    · The `Voice` Class
    · Integration in `Commands`
  Audio Processing and Constraints
    · Format Validation and Conversion
    · Whisper API Integration
  System Architecture
  Configuration and Setup
    · Command Line Arguments
    · Runtime Requirements

## · Copy/Paste Integration with Web Chat UIs  (L6907)
  源文件: aider/copypaste.py, aider/website/assets/copypaste.jpg, aider/website/assets/copypaste.mp4, aider/website/assets/watch.jpg, aider/website/assets/watch.mp4, aider/website/docs/usage/copypaste.md, aider/website/docs/usage/watch.md
  Purpose and Scope
  Architecture and Data Flow
    · Component Interaction Diagram
  Key Components
    · ClipboardWatcher
    · Command Integration
    · Coder Logic for Copy/Paste
  Technical Implementation Details
    · Context Assembly
    · Automated Edit Application
  Workflow Comparison
  Terms of Service Considerations

## · Architect Mode  (L7048)
  源文件: aider/coders/architect_coder.py, aider/coders/architect_prompts.py, aider/coders/editblock_fenced_prompts.py, aider/coders/editor_diff_fenced_coder.py, aider/coders/editor_diff_fenced_prompts.py, aider/coders/editor_editblock_coder.py, aider/coders/editor_editblock_prompts.py, aider/coders/editor_whole_coder.py, aider/coders/editor_whole_prompts.py, aider/website/_data/architect.yml, aider/website/_posts/2024-09-26-architect.md, aider/website/_sass/custom/custom.scss
  Purpose and Workflow
  Two-Stage Execution Flow
  Technical Implementation: ArchitectCoder
  Model Configuration and Benchmarks
  Editor Edit Formats
  User Interaction and Commands
  Data Flow: Reasoning to Entity Modification
  Comparison of Coding Modes

## · Web Content Integration  (L7210)
  源文件: aider/gui.py, aider/report.py, aider/scrape.py, aider/urls.py, aider/utils.py, aider/versioncheck.py, pytest.ini, scripts/update-docs.sh, tests/basic/test_main.py, tests/basic/test_model_info_manager.py, tests/basic/test_ssl_verification.py, tests/scrape/test_scrape.py
  Scraper Architecture
  Playwright Strategy
  httpx Fallback Strategy
  HTML to Markdown Conversion
  SSL Verification Configuration
  Integration with GUI
  Error Handling and Fallbacks

## · Web Scraping Architecture  (L7458)
  源文件: aider/gui.py, aider/report.py, aider/scrape.py, aider/urls.py, aider/utils.py, aider/versioncheck.py, pytest.ini, scripts/update-docs.sh, tests/basic/test_main.py, tests/basic/test_model_info_manager.py, tests/basic/test_ssl_verification.py, tests/scrape/test_scrape.py
  Purpose and Scope
  Core Architecture
  Scraper Class Public API
    · Constructor
    · Main Method
  Two-Strategy Fetching System
    · Playwright Strategy
    · httpx Strategy
  HTML Processing Pipeline
    · HTML Detection and Conversion
    · HTML Slimming
  Dependency Management and Installation
    · install_playwright Helper
    · check_env Logic
  SSL Verification Configuration
  Integration with Aider Components
    · Web GUI Integration
    · User Agent Branding

## · SSL Verification Configuration  (L7714)
  源文件: pytest.ini, tests/basic/test_main.py, tests/basic/test_model_info_manager.py, tests/basic/test_ssl_verification.py, tests/scrape/test_scrape.py
  Purpose and Scope
  Overview
  SSL Verification Control Flow
  Configuration Entry Point
    · Command-Line Flag
  Component-Level SSL Configuration
    · ModelInfoManager
    · Scraper Class
    · litellm Integration
  SSL Configuration State Diagram
  Testing SSL Configuration
    · Functional Testing against BadSSL
    · Test Coverage Table
  Implementation Sequence
  Security Considerations

## · Model Configuration and Capabilities  (L7946)
  源文件: README.md, aider/resources/__init__.py, aider/resources/model-metadata.json, aider/resources/model-settings.yml, aider/website/_data/polyglot_leaderboard.yml, aider/website/assets/sample-analytics.jsonl, aider/website/docs/config/adv-model-settings.md, aider/website/docs/config/model-aliases.md, aider/website/docs/faq.md, aider/website/docs/leaderboards/index.md, aider/website/docs/more/infinite-output.md, aider/website/index.html
  Configuration Architecture
  Model Settings System
    · Behavioral Configuration
    · Technical Metadata
  Model Capabilities
    · Edit Format Support
    · Reasoning and Thinking Tokens
  Multi-Provider Integration
  Three-Tier Model System
  Model Aliases

## · Model Settings and Behavioral Configuration  (L8180)
  源文件: README.md, aider/resources/__init__.py, aider/resources/model-metadata.json, aider/resources/model-settings.yml, aider/website/_data/polyglot_leaderboard.yml, aider/website/assets/sample-analytics.jsonl, aider/website/assets/sample.aider.conf.yml, aider/website/assets/sample.env, aider/website/docs/config/adv-model-settings.md, aider/website/docs/config/aider_conf.md, aider/website/docs/config/dotenv.md, aider/website/docs/config/model-aliases.md
  Model Settings File Structure
    · Configuration Application Flow
  Edit Strategy Configuration
    · Edit Format Settings
  Repository Context Settings
    · Context Logic Flow
    · use_repo_map
    · lazy
  Message Formatting and Prompt Engineering
    · Message Placement Settings
    · reminder
    · examples_as_sys_msg
  Provider-Specific Parameters
    · extra_params
    · cache_control
  Multi-Model Architecture Settings
    · Model Role Delegation
    · weak_model_name
    · editor_model_name
  Advanced Runtime Configuration
    · Accepts Settings
    · Reasoning and Thinking
  Settings Loading and Priority

## · Model Metadata and Technical Capabilities  (L8482)
  源文件: aider/resources/__init__.py, aider/resources/model-metadata.json, aider/resources/model-settings.yml, aider/website/_data/polyglot_leaderboard.yml, pytest.ini, scripts/clean_metadata.py, tests/basic/test_main.py, tests/basic/test_model_info_manager.py, tests/basic/test_models.py, tests/basic/test_reasoning.py, tests/basic/test_ssl_verification.py, tests/scrape/test_scrape.py
  Purpose and Scope
  Overview
  Metadata Structure
  Token Limits and Context Windows
  Cost and Cache Structure
  ModelInfoManager Retrieval Interface
    · Key Functions and Data Flow
  Technical Capabilities and Flags
    · Reasoning and Thinking
  Relationship to Benchmarks

## · Multi-Provider LLM Integration  (L8713)
  源文件: aider/openrouter.py, aider/website/docs/llms/anthropic.md, aider/website/docs/llms/azure.md, aider/website/docs/llms/cohere.md, aider/website/docs/llms/deepseek.md, aider/website/docs/llms/github.md, aider/website/docs/llms/groq.md, aider/website/docs/llms/lm-studio.md, aider/website/docs/llms/ollama.md, aider/website/docs/llms/openai-compat.md, aider/website/docs/llms/openai.md, aider/website/docs/llms/openrouter.md
  Architecture Overview
    · High-Level Architecture Diagram
  Provider Configuration
    · API Key Management
    · Local and Compatible Providers
  Model Registration and Selection
    · Model Discovery and OpenRouter Integration
    · Technical Capability Mapping
  Provider-Specific Features
    · Reasoning and Thinking Tokens
    · Prompt Caching and Prefill
  Three-Tier Model System
    · Model Logic Flow Diagram

## · Three-Tier Model System  (L8909)
  源文件: aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/io.py, aider/main.py, aider/models.py, aider/repo.py, aider/repomap.py, aider/resources/__init__.py, aider/resources/model-metadata.json, aider/resources/model-settings.yml, aider/voice.py
  Purpose and Scope
  Overview
  The Three Model Tiers
    · Main Model
    · Weak Model
    · Editor Model
  Model Configuration in Settings
    · ModelSettings Dataclass
    · Configuration File Structure
  Model Initialization Flow
  Switching Models at Runtime
  Cost Optimization Strategy
    · Task Routing
    · Disabling the Weak or Editor Model

## · Reasoning and Thinking Token Configuration  (L9220)
  源文件: aider/reasoning_tags.py, aider/resources/__init__.py, aider/resources/model-metadata.json, aider/resources/model-settings.yml, aider/website/_data/polyglot_leaderboard.yml, aider/website/assets/thinking.jpg, aider/website/docs/config/reasoning.md, tests/basic/test_models.py, tests/basic/test_reasoning.py
  Overview
  Thinking Tokens Configuration
    · Supported Models and Settings
    · Implementation in Model Class
  Reasoning Effort Configuration
  Reasoning Tags and Extraction
    · The reasoning_tags Module
    · UI Rendering Flow
  Configuration and Metadata
    · Model Settings (YAML)
    · Model Metadata (JSON)
    · Benchmark Performance

## · Development and Quality Assurance  (L9357)
  源文件: .github/workflows/check_pypi_version.yml, .github/workflows/ubuntu-tests.yml, .github/workflows/windows-tests.yml, .github/workflows/windows_check_pypi_version.yml, .gitignore, benchmark/Dockerfile, benchmark/benchmark.py, requirements/pydub.in, requirements/python-compat.in
  Purpose and Scope
  Benchmarking System
    · Benchmark Architecture
    · Test Execution and Isolation
  Testing Infrastructure
    · CI/CD and Version Verification
    · Dependency and Compatibility Testing
  Performance Leaderboards
    · Leaderboard Metrics
    · Data and Visualization

## · Benchmarking System Architecture  (L9528)
  源文件: .dockerignore, .gitignore, aider/website/_data/r1_architect.yml, aider/website/_posts/2025-01-24-r1-sonnet.md, benchmark/Dockerfile, benchmark/benchmark.py, benchmark/clone-exercism.sh, benchmark/docker.sh, benchmark/docker_build.sh, benchmark/install-docker-ubuntu.sh, benchmark/problem_stats.py, benchmark/rsync.sh
  Purpose and Scope
  Architecture Overview
    · System Orchestration Diagram
  Test Discovery and Organization
    · Exercise Directory Structure
    · Exercise Configuration
    · Directory Naming and Resolution
  Test Execution Flow
    · Initialization and Setup
    · Single Test Execution Lifecycle
    · Language-Specific Test Execution
  Result Collection and Metrics
    · Natural Language Space to Code Entity Space Mapping
    · Result File Format
    · Evaluation Metrics
  Docker and Infrastructure
    · Containerization
    · Grid and Replay Modes
    · Resource Cleanup

## · Testing Infrastructure  (L9792)
  源文件: .github/workflows/check_pypi_version.yml, .github/workflows/ubuntu-tests.yml, .github/workflows/windows-tests.yml, .github/workflows/windows_check_pypi_version.yml, aider/help.py, pytest.ini, requirements/pydub.in, requirements/python-compat.in, scripts/issues.py, tests/basic/test_coder.py, tests/basic/test_commands.py, tests/basic/test_deprecated.py
  Overview
  Test Organization
    · Directory Structure
    · Test Classes and Code Entity Mapping
  Test Fixtures and Setup
    · Common Test Setup Pattern
    · Pytest Fixtures
  Mocking Strategies
    · LLM and Coder Mocking
    · Git State Mocking
  Integration Testing
    · Web Scraping and SSL
    · Help System and RAG
  CI Workflows

## · Performance Leaderboards  (L10022)
  源文件: CONTRIBUTING.md, aider/resources/__init__.py, aider/resources/model-metadata.json, aider/resources/model-settings.yml, aider/website/_data/edit_leaderboard.yml, aider/website/_data/o1_polyglot_leaderboard.yml, aider/website/_data/polyglot_leaderboard.yml, aider/website/_data/qwen3_leaderboard.yml, aider/website/_includes/leaderboard.js, aider/website/_includes/leaderboard_graph.html, aider/website/_includes/leaderboard_table.js, aider/website/_posts/2024-12-21-polyglot.md
  Purpose and Scope
  Leaderboard Data Formats
    · Polyglot Leaderboard (`polyglot_leaderboard.yml`)
    · Edit Leaderboard (`edit_leaderboard.yml`)
  Metrics and Data Flow
    · Metric Calculation Logic
  Informing Model Recommendations
    · Mapping Results to Code Entities
  Over-Time Visualizations
    · Implementation Details
    · Visualization Data Flow
  Website Integration

## · Configuration and Deployment  (L10212)
  源文件: .pre-commit-config.yaml, aider/website/assets/sample.aider.conf.yml, aider/website/assets/sample.env, aider/website/docs/config/aider_conf.md, aider/website/docs/config/dotenv.md, aider/website/docs/config/options.md, requirements.txt, requirements/common-constraints.txt, requirements/requirements-browser.txt, requirements/requirements-dev.in, requirements/requirements-dev.txt, requirements/requirements-help.in
  Configuration System Overview
    · Configuration Precedence
    · Configuration Loading Flow
  Dependency Management
    · Dependency File Structure
    · Component Requirements
  Build and Version Management
    · Release Automation
    · Deployment Considerations

## · Configuration System  (L10370)
  源文件: aider/website/_includes/help-tip.md, aider/website/_includes/keys.md, aider/website/_includes/model-warnings.md, aider/website/assets/sample.aider.conf.yml, aider/website/assets/sample.env, aider/website/docs/config.md, aider/website/docs/config/aider_conf.md, aider/website/docs/config/dotenv.md, aider/website/docs/config/options.md, aider/website/docs/troubleshooting/support.md, pytest.ini, tests/basic/test_main.py
  Overview
  Configuration Sources and Precedence
    · Search Path Generation
  Configuration File Formats
    · YAML Configuration Files
    · Environment Variables
  Environment File Loading
    · .env File Search Path
    · API Key Configuration
  Model Configuration System
    · Model Settings and Metadata
    · SSL Verification
  Key Configuration Parameters
    · Model Roles
    · Reasoning and Thinking
    · Git Integration

## · Dependency Management  (L10547)
  源文件: .pre-commit-config.yaml, requirements.txt, requirements/common-constraints.txt, requirements/requirements-browser.in, requirements/requirements-browser.txt, requirements/requirements-dev.in, requirements/requirements-dev.txt, requirements/requirements-help.in, requirements/requirements-help.txt, requirements/requirements-playwright.in, requirements/requirements-playwright.txt, requirements/requirements.in
  Purpose and Scope
  Dependency File Structure
  Core Dependencies
    · Primary Dependency Categories
    · Critical Dependencies
  Optional Dependency Sets
    · Help Feature Dependencies
    · Browser Feature Dependencies
    · Playwright Feature Dependencies
    · Development Dependencies
  Compilation Process with UV
    · Compilation Workflow
  Version Constraints System
    · Critical Version Pins
    · Platform Shimming
  Key Dependency Details
    · LLM Integration Stack
    · Code Analysis and Mapping Stack
  Installation Scenarios
    · Standard Installation
    · Development Installation
    · Feature-Specific Installation

## · Build and Version Management  (L10871)
  源文件: .github/workflows/check_pypi_version.yml, .github/workflows/docker-build-test.yml, .github/workflows/docker-release.yml, .github/workflows/pages.yml, .github/workflows/release.yml, .github/workflows/ubuntu-tests.yml, .github/workflows/windows-tests.yml, .github/workflows/windows_check_pypi_version.yml, MANIFEST.in, aider/__init__.py, aider/help_pats.py, aider/llm.py
  Version Resolution System
    · Version Resolution Flow
    · Version String Components
  setuptools_scm Integration
    · Build Configuration
  Version Bumping Workflow
    · Version Bump Process Flow
    · Pre-Release Safety Checks
  CI/CD Pipelines
    · Test Matrix
    · Docker Build Strategy
    · Release Workflow
  Performance Optimization: Lazy Loading
    · LazyLiteLLM Implementation
  Distribution Configuration
    · Project Metadata and Extras
    · MANIFEST.in Filtering

## · Utilities and Supporting Systems  (L11124)
  源文件: aider/dump.py, aider/gui.py, aider/report.py, aider/scrape.py, aider/urls.py, aider/utils.py, aider/versioncheck.py, scripts/update-docs.sh
  Overview
  System Integration Architecture
  Core Utility Functions
    · Temporary Directory Management
    · Path Handling and Formatting
  Error Reporting and Version Checking
    · Exception Handler
    · Version Check System
  Package Installation Utilities
    · Just-in-Time Dependencies
    · Installation Helpers
  GUI Utilities
    · CaptureIO Class
    · State Management

## · Core Utility Functions  (L11315)
  源文件: aider/dump.py, aider/editor.py, aider/gui.py, aider/report.py, aider/scrape.py, aider/urls.py, aider/utils.py, aider/versioncheck.py, scripts/update-docs.sh, tests/basic/test_editor.py
  Purpose and Scope
  Temporary Directory Management
    · Directory Class Hierarchy
    · IgnorantTemporaryDirectory
    · ChdirTemporaryDirectory
    · GitTemporaryDirectory
  File System Utilities
    · Path Resolution
    · Image File Detection
  Package Installation Utilities
    · Installation Flow
    · run_install()
  External Editor Integration
    · Editor Discovery and Usage
    · Key Editor Functions
  Message Formatting and Chat Parsing
    · format_messages()
    · split_chat_history_markdown()
  Web Scraping Integration
  Summary of Core Utilities

## · Error Reporting and Version Checking  (L11551)
  源文件: aider/exceptions.py, aider/gui.py, aider/report.py, aider/scrape.py, aider/urls.py, aider/utils.py, aider/versioncheck.py, aider/website/_includes/install.md, aider/website/docs/llms/bedrock.md, aider/website/docs/llms/gemini.md, scripts/update-docs.sh, tests/basic/test_exceptions.py
  Purpose and Scope
  Version Checking System
    · Version Check Components
    · Rate Limiting Mechanism
    · PyPI Version Query
    · Installation Methods
  Error Reporting System
    · Exception Handler Architecture
    · System Information Collection
    · Traceback Processing
    · GitHub Issue URL Generation
    · User Interaction Flow
    · Version Check Cache Deletion
  LLM Exception Handling
    · LiteLLM Exception Classification
    · Logic for Specific Errors
  Implementation Details
    · Constants and Configuration
    · Version Comparison Logic

## · Package Installation Utilities  (L11963)
  源文件: .pre-commit-config.yaml, aider/gui.py, aider/report.py, aider/scrape.py, aider/urls.py, aider/utils.py, aider/versioncheck.py, requirements.txt, requirements/common-constraints.txt, requirements/requirements-browser.txt, requirements/requirements-dev.in, requirements/requirements-dev.txt
  Purpose and Scope
  Core Installation Functions
    · `check_pip_install_extra`
    · `get_pip_install`
    · `run_install`
  Integration Points
    · Playwright Installation Flow
    · Self-Update Installation Flow
  Requirements and Dependency Files
  Error Handling and Recovery
    · Platform-Specific Escaping
    · Exception Sanitization

## · Help and Documentation System  (L12248)
  源文件: aider/help.py, scripts/issues.py, tests/basic/test_coder.py, tests/basic/test_commands.py, tests/basic/test_sanity_check_repo.py, tests/help/test_help.py
  Purpose and Scope
  System Architecture Overview
    · Help System Component Architecture
  Help System Architecture
    · llama-index Integration
    · HuggingFace Embeddings (bge-small-en-v1.5)
    · Local Cache and Persistence
  HelpCoder and Context Assembly
    · HelpCoder and /help Command
    · Context Assembly Process
    · Help Context Assembly Sequence
  Dependencies and Installation
    · Graceful Installation

## · Help System Architecture  (L12389)
  源文件: .pre-commit-config.yaml, aider/help.py, requirements.txt, requirements/common-constraints.txt, requirements/requirements-browser.txt, requirements/requirements-dev.in, requirements/requirements-dev.txt, requirements/requirements-help.in, requirements/requirements-help.txt, requirements/requirements-playwright.txt, requirements/requirements.in, scripts/issues.py
  Purpose and Scope
  System Overview
  Core Architecture
    · Component Overview
  Embedding Model Configuration
  Indexing and Retrieval Pipeline
    · 1. Document Loading and Parsing
    · 2. URL Mapping
    · 3. Local Caching
    · Retrieval Flow
  Integration with HelpCoder
    · Context Formatting
  Installation and Dependencies
  Performance and Caching

## · HelpCoder and Context Assembly  (L12566)
  源文件: aider/coders/ask_coder.py, aider/coders/editblock_fenced_coder.py, aider/coders/help_coder.py, aider/coders/patch_coder.py, aider/coders/search_replace.py, aider/coders/udiff_coder.py, aider/help.py, scripts/issues.py, tests/basic/test_coder.py, tests/basic/test_commands.py, tests/basic/test_sanity_check_repo.py, tests/help/test_help.py
  HelpCoder Class Overview
  Context Assembly Pipeline
    · Retrieval and Fragment Injection
  Integration with the Commands System
  Help System Prompts
  Data Flow: From URL to Context
  Summary of Differences

## · Analytics and Self-Improvement  (L12739)
  源文件: HISTORY.md, aider/analytics.py, aider/website/HISTORY.md, aider/website/_data/blame.yml, aider/website/docs/more/analytics.md, scripts/update-blame.sh, tests/basic/test_analytics.py
  Purpose and Scope
  Usage Analytics
    · Core Components and Class Structure
    · Event Collection and Privacy
  Self-Referential Development Metrics
    · Git Blame Analysis Pipeline
    · The "Singularity" Metric

## · Usage Analytics  (L12899)
  源文件: README.md, aider/analytics.py, aider/website/assets/sample-analytics.jsonl, aider/website/docs/config/adv-model-settings.md, aider/website/docs/config/model-aliases.md, aider/website/docs/faq.md, aider/website/docs/leaderboards/index.md, aider/website/docs/more/analytics.md, aider/website/docs/more/infinite-output.md, aider/website/index.html, tests/basic/test_analytics.py
  Purpose and Scope
  Analytics Architecture
    · System Components and Data Flow
    · Key Functions and Classes
  Event Types and Properties
    · Core Session Events
    · Repository and Configuration Events
    · Message and Token Events
  Opt-In and Privacy Logic
    · The Opt-In Mechanism
    · Model Name Redaction
  Configuration and Log Format
    · Custom PostHog Integration
    · The sample-analytics.jsonl Format
  Transparency Metrics

## · Self-Referential Development Metrics  (L13083)
  源文件: HISTORY.md, aider/website/HISTORY.md, aider/website/_data/blame.yml, aider/website/_includes/blame.md, aider/website/docs/git.md, aider/website/docs/install/docker.md, scripts/blame.py, scripts/update-blame.sh
  Purpose and Scope
  Overview
  System Architecture
    · Overall Data Flow
    · Git Author Attribution System
  Blame Analysis Pipeline
    · Script Execution
    · Blame Data Structure
    · Calculation Methodology
  Publication and Display
    · Release Notes Integration
    · Aider v0.86.0
    · Chart Visualization
  Historical Trends and Analysis
    · Release-by-Release Statistics
    · Evolution of AI Contribution
  Implementation Details
    · Key Functions and Classes
    · File Exclusions and Inclusions

## · Glossary  (L13319)
  源文件: .gitignore, HISTORY.md, MANIFEST.in, README.md, aider/__init__.py, aider/args.py, aider/coders/base_coder.py, aider/commands.py, aider/help_pats.py, aider/io.py, aider/llm.py, aider/main.py
  Core Concepts
    · Coder
    · Edit Format
    · Repo Map (Repository Map)
    · Main / Weak / Editor Model
  Technical Terms & Jargon
  Architectural Diagrams
    · From Natural Language to Code Modification
    · Model Resolution and Capability Mapping
  File and Class References
    · `aider/coders/base_coder.py`
    · `aider/models.py`
    · `aider/repomap.py`
    · `aider/io.py`
    · `aider/commands.py`