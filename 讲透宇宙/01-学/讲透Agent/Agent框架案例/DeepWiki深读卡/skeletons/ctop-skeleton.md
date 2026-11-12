# Skeleton: ctop（31 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 4KB | 2 | ~2 | 3 |
| 2 | Getting Started | L150 | 6KB | 2 | ~2 | 5 |
| 3 | Supported AI Agents | L317 | 6KB | 2 | ~2 | 6 |
| 4 | Core Architecture | L450 | 6KB | 2 | ~2 | 7 |
| 5 | Process Detection Engine | L593 | 6KB | 2 | ~1 | 7 |
| 6 | Session Data Parsing | L749 | 6KB | 2 | ~3 | 7 |
| 7 | State Management | L901 | 6KB | 2 | ~3 | 8 |
| 8 | Configuration System | L1025 | 5KB | 2 | ~3 | 8 |
| 9 | TUI Rendering System | L1150 | 5KB | 2 | ~2 | 5 |
| 10 | List View and Pane View | L1297 | 6KB | 2 | ~2 | 8 |
| 11 | Visualizations: Braille Bars, Sparklines, and Waveforms | L1441 | 5KB | 2 | ~2 | 6 |
| 12 | Animation and Theming | L1558 | 6KB | 2 | ~4 | 8 |
| 13 | User Interaction | L1716 | 5KB | 2 | ~2 | 5 |
| 14 | Keyboard Commands and Mouse Support | L1839 | 6KB | 2 | ~12 | 4 |
| 15 | Command Palette and Filter/Sort | L1985 | 6KB | 2 | ~2 | 6 |
| 16 | Quick Jump and Session Export | L2136 | 5KB | 2 | ~4 | 5 |
| 17 | Metrics and Cost Engine | L2254 | 5KB | 2 | ~3 | 8 |
| 18 | Cost Calculation | L2395 | 4KB | 2 | ~2 | 3 |
| 19 | Token Tracking and Rates | L2522 | 6KB | 2 | ~2 | 6 |
| 20 | History, Heatmap, and Timeline | L2681 | 6KB | 2 | ~2 | 8 |
| 21 | Advanced Features | L2814 | 4KB | 2 | ~0 | 4 |
| 22 | Plugin System | L2939 | 6KB | 2 | ~2 | 6 |
| 23 | Notifications and Git Integration | L3100 | 6KB | 2 | ~3 | 5 |
| 24 | Cross-Platform Support | L3241 | 5KB | 2 | ~3 | 7 |
| 25 | Performance and Caching | L3358 | 5KB | 1 | ~2 | 4 |
| 26 | Caching Layer | L3460 | 6KB | 2 | ~2 | 4 |
| 27 | Render Coalescing and Refresh Guard | L3600 | 6KB | 2 | ~1 | 5 |
| 28 | Testing and Development | L3730 | 4KB | 2 | ~0 | 3 |
| 29 | Test Suite | L3838 | 6KB | 2 | ~2 | 8 |
| 30 | Demo Recording and Documentation Assets | L3994 | 6KB | 2 | ~2 | 7 |
| 31 | Glossary | L4127 | 6KB | 2 | ~2 | 15 |


## · Overview  (L6)
  源文件: README.md, docs/index.html, package.json
    · Who it is for
  System Workflow
    · Data Flow Diagram
  Core Capabilities
  Getting Started
  Supported AI Agents
    · Agent Detection Mapping

## · Getting Started  (L150)
  源文件: README.md, package.json, test/boot.test.js, test/config.test.js, test/session.test.js
  Installation
    · via npm
    · via Homebrew
    · From Source
  First Run and Boot Sequence
    · CLI Entry and Initialization Flow
  CLI Flags
  Configuration File (`~/.ctoprc`)
    · Supported Configuration Keys
    · Example `.ctoprc`
  Basic Navigation and Controls
    · Navigation Mapping
  Data Flow: First Refresh

## · Supported AI Agents  (L317)
  源文件: README.md, docs/claude-icon.png, docs/codex-icon.png, src/_core.js, test/animations.test.js, test/caching.test.js
  Agent Detection and Mapping
    · Detection Logic Flow
  Supported Agent Types
    · 1. Claude Code
    · 2. Codex CLI
    · 3. OpenCode
  Technical Comparison
  Data Flow: From File to UI
    · Key Functions

## · Core Architecture  (L450)
  源文件: src/_core.js, src/main.js, src/process.js, src/session.js, src/state.js, test/animations.test.js, test/caching.test.js
  Module Layout and Single Source of Truth
  The Poll-Enrich-Render Pipeline
    · 1. Poll (Discovery)
    · 2. Enrich (Data Correlation)
    · 3. Render (Visual Output)
    · Architecture Flow Diagram
  Subsystem Overviews
    · Process Detection Engine
    · Session Data Parsing
    · State Management
    · Configuration System
    · Component Interaction Diagram

## · Process Detection Engine  (L593)
  源文件: src/_core.js, src/process.js, test/animations.test.js, test/caching.test.js, test/heatmap.test.js, test/quick-jump.test.js, test/windows.test.js
  Overview
    · Key Responsibilities
  Platform-Specific Discovery
    · Unix-like Systems (macOS & Linux)
    · Windows
  CWD Resolution and `resolveCwds`
    · Implementation Details
    · Data Flow: Process to Session Mapping
  Caching Strategy
    · `pidCwdCache`
    · Project Directory Normalization
  Implementation Mapping
  Key Functions
    · `resolveCwds(pids)`
    · `pruneCwdCache(activePids)`
    · `buildKillCommand(pid, force)`

## · Session Data Parsing  (L749)
  源文件: src/_core.js, src/session.js, test/animations.test.js, test/caching.test.js, test/config.test.js, test/log-tailing.test.js, test/session.test.js
  Overview of Parsing Pipeline
    · Data Flow: PID to Session Metrics
  Claude Code: JSONL Dual-Buffer Parsing
    · Implementation Details
    · Natural Language Space to Code Entity Space (Claude)
  Codex and OpenCode Parsing
    · Diagram: Multi-Agent Parsing Pipeline
  Log Tailing and Partial-Line Handling
    · The Tail-Read Algorithm
    · Natural Language Space to Code Entity Space (Logs)
  Caching Layer (mtime/size)

## · State Management  (L901)
  源文件: claude-manager, src/_core.js, src/state.js, test/animations.test.js, test/caching.test.js, test/history.test.js, test/search.test.js, test/themes.test.js
  The Global State Objects
    · `_state` Object
    · `_notif` Object
    · `tokenHistory` Map
  The Refresh Cycle and Re-entry Guard
    · Refresh Flow
  Render Coalescing via `setImmediate`
    · Natural Language to Code: Render Logic
  History Persistence and `SNAPSHOT_INTERVAL`
    · Throttling Snapshots
    · Natural Language to Code: History Flow

## · Configuration System  (L1025)
  源文件: claude-manager, src/config.js, test/boot.test.js, test/config.test.js, test/history.test.js, test/search.test.js, test/session.test.js, test/themes.test.js
  Configuration Resolution Hierarchy
    · Data Flow Diagram
  Supported Configuration Keys
  Implementation Details
    · Validation and Sanitization
    · Theming System Integration
    · CLI Override Logic
  Persistence

## · TUI Rendering System  (L1150)
  源文件: docs/index.html, src/_core.js, src/render.js, test/animations.test.js, test/caching.test.js
  Manual Buffer Construction
  Layout and Visual Width
  Primary View Modes
    · List View
    · Pane View
  Rendering Pipeline
    · TUI Assembly Flow
  Subsystems
    · [List View and Pane View](#3.1)
    · [Visualizations: Braille Bars, Sparklines, and Waveforms](#3.2)
    · [Animation and Theming](#3.3)
  Rendering Entity Map

## · List View and Pane View  (L1297)
  源文件: src/_core.js, src/render.js, test/animations.test.js, test/caching.test.js, test/dashboard.test.js, test/filter-sort.test.js, test/format.test.js, test/status-bar.test.js
  Rendering Pipeline
    · Visual Width and Formatting
    · The Dashboard Stats Bar
  List View (`renderListMode`)
    · Implementation Flow
    · Column Layout
    · List View Architecture
  Pane View (`renderPaneMode`)
    · Card-Grid Layout
    · Card Content
    · Pane View Entity Mapping
  Technical Details
    · Fixed-Width String Formatting
    · ANSI Styling
    · Selection Animation

## · Visualizations: Braille Bars, Sparklines, and Waveforms  (L1441)
  源文件: src/_core.js, src/render.js, test/animations.test.js, test/braille.test.js, test/caching.test.js, test/sparkline.test.js
  Braille-Based Visualizations
    · Braille Fill Mechanics
    · Context Bar Rendering
    · Visual Data Flow: Token Metrics to Braille Bar
  Sparklines and History
    · Sparkline Implementation
    · 24-Hour History Chart
  Message Waveforms
    · Implementation Details
    · Component Summary Table

## · Animation and Theming  (L1558)
  源文件: claude-manager, src/_core.js, src/colors.js, test/animations.test.js, test/caching.test.js, test/history.test.js, test/search.test.js, test/themes.test.js
    · Animation System
    · Theming Engine
    · Configuration

## · User Interaction  (L1716)
  源文件: README.md, src/_core.js, src/input.js, test/animations.test.js, test/caching.test.js
    · Interaction Subsystems
  Input Flow and State Management
    · System Interaction Overview
  Core Interaction Modes
    · 1. Navigation and View Toggles
    · 2. Process Control
    · 3. Search and Filtering
    · 4. Command Palette
  Subsystem Details

## · Keyboard Commands and Mouse Support  (L1839)
  源文件: README.md, docs/index.html, src/input.js, test/mouse.test.js
  Keyboard Command Reference
    · Navigation and Selection
    · View and UI Toggles
    · Sorting, Filtering, and Search
    · Process Control and Quick-Jump
  Mouse Support Implementation
    · Mouse Event Parsing
    · Coordinate Mapping
  Technical Data Flow: Interaction to Render
  Key Functions and Classes

## · Command Palette and Filter/Sort  (L1985)
  源文件: src/input.js, test/filter-sort.test.js, test/format.test.js, test/grouping.test.js, test/palette.test.js, test/token-rate.test.js
  Command Palette (`showPalette`)
    · Available Actions
    · Implementation Details
  Filter and Sort Pipeline
    · Filtering (`filterMode`)
    · Sorting (`SORT_MODES`)
  Grouping and Path Normalization
    · Process Grouping
    · Flat List Construction
    · Path Shortening
  Data Flow: Interaction to State
    · Input Processing Flow
  Process Aggregation Logic
    · Grouping and Flattening Pipeline

## · Quick Jump and Session Export  (L2136)
  源文件: src/input.js, test/export.test.js, test/heatmap.test.js, test/quick-jump.test.js, test/windows.test.js
  Quick Jump: `openDirectory`
    · Implementation Details
    · Editor Resolution
    · Windows Path Normalization
  Session Export Formats
    · 1. Markdown (`formatSessionMarkdown`)
    · 2. JSON (`formatSessionJSON`)
    · 3. CSV (`formatSessionCSV`)
    · Data Mapping Table

## · Metrics and Cost Engine  (L2254)
  源文件: claude-manager, src/_core.js, src/cost.js, test/animations.test.js, test/caching.test.js, test/history.test.js, test/search.test.js, test/themes.test.js
    · Architectural Overview
    · Key Subsystems
    · Metrics Data Model
    · Summary Table of Metrics

## · Cost Calculation  (L2395)
  源文件: src/cost.js, test/cost.test.js, test/status-bar.test.js
  Model Pricing Table
    · Prefix Matching Logic
  Cost Calculation Formula
    · Formula
    · Data Flow: Log to Cost
  Formatting and Visualization
    · `formatCost`
    · Cost Gauge (`buildCostGauge`)

## · Token Tracking and Rates  (L2522)
  源文件: src/_core.js, test/animations.test.js, test/caching.test.js, test/dashboard.test.js, test/grouping.test.js, test/token-rate.test.js
  Token Extraction and Aggregation
    · Key Data Fields
    · Implementation Logic
  Token Rates and Delta Calculation
    · The `tokenHistory` Map
    · Rate Calculation Pipeline
    · Rate Formatting
  Context Window Computation
    · Calculation Logic
    · Visualization
  Token Flow Architecture
    · Data Extraction to UI Flow
  Rate Calculation Lifecycle
    · updateTokenRates Sequence

## · History, Heatmap, and Timeline  (L2681)
  源文件: claude-manager, test/heatmap.test.js, test/history.test.js, test/quick-jump.test.js, test/search.test.js, test/themes.test.js, test/timeline.test.js, test/windows.test.js
  History Persistence System
    · Data Storage and Lifecycle
    · Aggregate Stats Calculation
    · History Persistence Flow
  Heatmap Aggregation Pipeline
    · Aggregation Logic
    · Thresholds and Color Levels
    · Heatmap Data Flow
  Session Timeline View
    · Parsing and Event Detection
    · Temporal Analysis
    · Formatting
    · Timeline Logic Table

## · Advanced Features  (L2814)
  源文件: README.md, src/_core.js, test/animations.test.js, test/caching.test.js
    · Feature Overview
    · Plugin System
    · Notifications and Git Integration
    · Cross-Platform Support
    · Advanced Logic Mapping

## · Plugin System  (L2939)
  源文件: README.md, examples/plugins/uptime.js, src/_core.js, test/animations.test.js, test/caching.test.js, test/plugins.test.js
  Plugin Architecture
    · The Plugin Contract
    · Column Definition
    · Data Flow: Plugin Integration
  Implementation Details
    · Plugin Loading Logic
    · Column Rendering
  Example: Uptime Plugin
    · Installation
  Technical Constraints

## · Notifications and Git Integration  (L3100)
  源文件: src/_core.js, test/animations.test.js, test/caching.test.js, test/git-diff.test.js, test/notifications.test.js
  Desktop Notifications
    · Key Components
    · Notification Logic and Thresholds
    · Platform Implementation
    · State Transition Data Flow
  Git Integration
    · Git Diff Pipeline
    · Data Structures
    · Git Entity Mapping
  Configuration and Tuning

## · Cross-Platform Support  (L3241)
  源文件: src/_core.js, src/process.js, test/animations.test.js, test/caching.test.js, test/heatmap.test.js, test/quick-jump.test.js, test/windows.test.js
  Platform Detection
  Process Discovery and Management
    · Windows-Specific Discovery
    · Signal Handling and Killing Processes
  Path Normalization
  Terminal and Directory Invocation
  Visual Rendering and ANSI Compatibility

## · Performance and Caching  (L3358)
  源文件: docs/designs/2026-05-10-perf-many-sessions.md, src/_core.js, test/animations.test.js, test/caching.test.js
    · Performance Architecture Overview
    · Caching Layers
    · Execution Control
    · System Integration Diagram
    · Performance Metrics and Scaling

## · Caching Layer  (L3460)
  源文件: docs/designs/2026-05-10-perf-many-sessions.md, src/_core.js, test/animations.test.js, test/caching.test.js
  Core Caches Overview
  PID to CWD Resolution (`pidCwdCache`)
    · Implementation and Batching
    · Invalidation Policy
    · Process-to-Cache Data Flow
  Session Data Caching (`sessionDataCache`)
  Log Tail Caching (`sessionLogCache`)
  Directory and File Caching (`sessionFileCache`)
  Summary of Code Entities

## · Render Coalescing and Refresh Guard  (L3600)
  源文件: docs/designs/2026-05-10-perf-many-sessions.md, src/_core.js, src/render.js, test/animations.test.js, test/caching.test.js
  Render Coalescing
    · Implementation Details
    · Render Coalescing Data Flow
  Refresh Re-entry Guard
    · The Problem: Overlapping Ticks
    · The Solution: `refreshing` Flag
    · Code Entity Mapping: Refresh Cycle
  Combined System Impact
    · Event Loop Starvation Prevention

## · Testing and Development  (L3730)
  源文件: .github/workflows/static.yml, package.json, scripts/mock-sessions.sh
  Testing Architecture
    · Test Isolation and Patterns
    · Testing Workflow Diagram
  Documentation and Demo Assets
    · Mock Session Generation
    · Automated GIF Recording
    · Documentation Deployment
  Related Pages

## · Test Suite  (L3838)
  源文件: claude-manager, package.json, test/boot.test.js, test/config.test.js, test/history.test.js, test/search.test.js, test/session.test.js, test/themes.test.js
  Overview and Philosophy
  Running Tests
  Test Suite Structure
    · Data Flow: Configuration Loading
  Test Isolation Patterns
    · 1. Temporary Directories
    · 2. Global State Manipulation
    · 3. CLI Flag Simulation
  Core Logic Validation
    · Session Parsing Logic
    · Token and Cost Accuracy

## · Demo Recording and Documentation Assets  (L3994)
  源文件: .github/workflows/static.yml, assets/features.gif, assets/features.tape, assets/hero.gif, assets/hero.tape, docs/index.html, scripts/mock-sessions.sh
  Mock Session Engine
    · Implementation Details
    · Data Flow: Mock to TUI
  VHS Tape Recordings
    · hero.tape
    · features.tape
    · Asset Optimization
  GitHub Pages Deployment
    · Landing Page Implementation
    · CI/CD Workflow

## · Glossary  (L4127)
  源文件: README.md, claude-manager, docs/index.html, src/_core.js, src/cost.js, test/animations.test.js, test/caching.test.js, test/grouping.test.js, test/heatmap.test.js, test/history.test.js, test/quick-jump.test.js, test/search.test.js
  Core Domain Concepts
    · Agent
    · Context Window
    · Session Data
  Technical Terms & Abbreviations
  Data Flow & Architecture Diagrams
    · Agent Discovery & Enrichment Pipeline
    · TUI State to Visual Mapping
  Implementation Details
    · Caching Layer
    · Cost Engine
    · Visualizations