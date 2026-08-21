# Skeleton: invisible-playwright（33 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 6KB | 2 | ~2 | 18 |
| 2 | Getting Started | L152 | 6KB | 2 | ~1 | 14 |
| 3 | Usage Examples | L315 | 8KB | 2 | ~0 | 19 |
| 4 | Core Architecture | L515 | 8KB | 2 | ~0 | 15 |
| 5 | Sync and Async APIs | L682 | 10KB | 2 | ~3 | 11 |
| 6 | Headless Mode and Virtual Displays | L855 | 7KB | 2 | ~1 | 19 |
| 7 | Binary Management and Download | L992 | 7KB | 2 | ~2 | 15 |
| 8 | Humanized Cursor Motion | L1130 | 8KB | 2 | ~1 | 19 |
| 9 | Process Lifecycle and Reaper | L1282 | 8KB | 2 | ~3 | 15 |
| 10 | Fingerprint Engine (fpforge) | L1445 | 7KB | 2 | ~2 | 16 |
| 11 | Bayesian Sampler and Network | L1577 | 8KB | 2 | ~2 | 18 |
| 12 | Profile Dataclasses | L1727 | 8KB | 2 | ~6 | 18 |
| 13 | Pinning System | L1926 | 6KB | 2 | ~6 | 11 |
| 14 | CPT Data Files | L2054 | 7KB | 2 | ~2 | 12 |
| 15 | Cookie and History Seeding | L2205 | 8KB | 2 | ~2 | 12 |
| 16 | Firefox Preference Translation | L2346 | 7KB | 2 | ~2 | 14 |
| 17 | translate_profile_to_prefs | L2493 | 8KB | 2 | ~5 | 8 |
| 18 | Platform-Specific Preference Logic | L2643 | 9KB | 2 | ~5 | 16 |
| 19 | Proxy Configuration | L2829 | 6KB | 2 | ~1 | 10 |
| 20 | CLI Reference | L2950 | 6KB | 2 | ~3 | 12 |
| 21 | Testing Infrastructure | L3118 | 5KB | 1 | ~2 | 19 |
| 22 | Unit and Integration Tests | L3237 | 8KB | 2 | ~1 | 19 |
| 23 | End-to-End and Build Tests | L3386 | 8KB | 2 | ~2 | 27 |
| 24 | Stealth Concepts and Detection Reference | L3537 | 7KB | 2 | ~3 | 15 |
| 25 | Detection Surfaces and Fingerprinting | L3705 | 10KB | 2 | ~3 | 26 |
| 26 | Comparisons with Other Tools | L3881 | 8KB | 2 | ~3 | 16 |
| 27 | Integrations | L4029 | 6KB | 2 | ~4 | 17 |
| 28 | Framework Integrations | L4178 | 8KB | 2 | ~5 | 10 |
| 29 | AI Agent and MCP Integrations | L4340 | 8KB | 2 | ~3 | 23 |
| 30 | Release and CI/CD Infrastructure | L4507 | 6KB | 1 | ~4 | 17 |
| 31 | Publication Gate and Release Ledger | L4614 | 8KB | 1 | ~2 | 17 |
| 32 | CI Workflows and Gates | L4765 | 8KB | 2 | ~0 | 18 |
| 33 | Glossary | L4931 | 9KB | 2 | ~4 | 35 |


## · Overview  (L6)
  源文件: CHANGELOG.md, README.md, docs/README.md, docs/badges/telegram.svg, docs/banner-dark.png, docs/banner-light.png, docs/configuration.md, docs/integrations/README.md, docs/pinning.md, docs/quickstart.md, docs/recaptcha-v3-score.md, docs/sannysoft-explained.md
    · Purpose and Design Philosophy
    · Comparison to Standard Playwright
    · System Architecture
    · Key Components
    · Quick Start
    · Documentation Sections

## · Getting Started  (L152)
  源文件: CHANGELOG.md, README.md, docs/README.md, docs/badges/telegram.svg, docs/banner-dark.png, docs/banner-light.png, docs/cli-reference.md, docs/installation.md, docs/integrations/README.md, pyproject.toml, src/invisible_playwright/_geo.py, src/invisible_playwright/constants.py
  Installation
    · Dependencies
  Binary Management (CLI)
    · Fetching the Binary
    · CLI Commands Reference
    · Data Flow: CLI to Binary Storage
  Minimal Working Example
    · Execution Logic

## · Usage Examples  (L315)
  源文件: README.md, docs/README.md, docs/badges/telegram.svg, docs/banner-dark.png, docs/banner-light.png, docs/configuration.md, docs/integrations/README.md, docs/pinning.md, docs/quickstart.md, docs/recaptcha-v3-score.md, docs/sannysoft-explained.md, docs/screen-size-headless-tells.md
  Basic Browser Launch
    · Implementation Flow
  Proxy Configuration
    · Proxy Data Flow
  Seed-based Deterministic Sessions
    · Seed Validation and Eager Materialization
  Humanized Cursor Motion
    · Cursor Engine Resolution
  Async API Usage
    · Lifecycle Comparison

## · Core Architecture  (L515)
  源文件: CHANGELOG.md, pyproject.toml, src/invisible_playwright/__init__.py, src/invisible_playwright/_geo.py, src/invisible_playwright/_pin.py, src/invisible_playwright/_recaptcha_seed.py, src/invisible_playwright/async_api.py, src/invisible_playwright/constants.py, src/invisible_playwright/download.py, src/invisible_playwright/launcher.py, tests/test_async_api.py, tests/test_core_pin.py
  System Lifecycle
    · 1. Initialization and Fingerprinting
    · 2. Environment Preparation
    · 3. Browser Launch and Patching
    · 4. Teardown
  High-Level Component Interaction
    · System Entity Map
  Major Subsystems
    · [Sync and Async APIs](#2.1)
    · [Headless Mode and Virtual Displays](#2.2)
    · [Binary Management and Download](#2.3)
    · [Humanized Cursor Motion](#2.4)
    · [Process Lifecycle and Reaper](#2.5)
  Logic Flow and Code Entities
    · Sequence of Operation

## · Sync and Async APIs  (L682)
  源文件: src/invisible_playwright/_engine.py, src/invisible_playwright/_recaptcha_seed.py, src/invisible_playwright/async_api.py, src/invisible_playwright/launcher.py, tests/test_async_api.py, tests/test_launcher_config.py, tests/test_launcher_helpers.py, tests/test_new_page_defaults.py, tests/test_recaptcha_seed.py, tests/test_seal_wire_version.py, tests/test_suite_boundaries.py
  The InvisiblePlaywright Class
    · Constructor and Eager Initialization
    · Data Flow: From Constructor to Browser Launch
  Lifecycle Management
    · Context Manager Implementation
    · Teardown Sequence
  Viewport and Screen Geometry
    · Geometry Calculation Logic
  Timezone and Locale Handling
    · TZ Environment Mapping
    · Realm Overrides
  API Parity and Patching
    · The `new_page` Settle Race-Condition Fix
    · Cookie Pre-seeding
    · Implementation Parity

## · Headless Mode and Virtual Displays  (L855)
  源文件: .github/workflows/e2e-hunt.yml, .github/workflows/e2e.yml, scripts/run_e2e.py, src/invisible_playwright/_fpforge/__init__.py, src/invisible_playwright/_headless.py, src/invisible_playwright/_proxy.py, src/invisible_playwright/_recaptcha_seed.py, src/invisible_playwright/async_api.py, src/invisible_playwright/launcher.py, tests/conftest.py, tests/test_async_api.py, tests/test_backcompat.py
  Architecture Overview
    · Virtual Display Lifecycle
  Implementation Details
    · Linux Implementation: `_LinuxVirtualDisplay` (Xvfb)
    · Windows Implementation: `_WindowsVirtualDesktop` (Win32 CreateDesktop)
  Configuration and Environment Variables
  Stealth Advantages
  Teardown and Idempotency

## · Binary Management and Download  (L992)
  源文件: .github/workflows/user-install.yml, CHANGELOG.md, pyproject.toml, src/invisible_playwright/_engine.py, src/invisible_playwright/_geo.py, src/invisible_playwright/cli.py, src/invisible_playwright/constants.py, src/invisible_playwright/download.py, tests/test_cli.py, tests/test_launcher_config.py, tests/test_release_e2e.py, tests/test_seal_wire_version.py
  Binary Lifecycle and Pipeline
    · Download Flow
    · Download Pipeline Architecture
  Configuration and Versioning
  Verification and Deadlines
    · Seal Verification
    · Download Deadlines
  GitHub Authentication
    · Entity Mapping: CLI to Core Implementation
  CLI Reference for Binary Management

## · Humanized Cursor Motion  (L1130)
  源文件: .github/workflows/firefox-launch-matrix.yml, .github/workflows/publish.yml, .github/workflows/tests.yml, .github/workflows/webrtc-e2e.yml, src/invisible_playwright/_behaviour.py, src/invisible_playwright/_cursor.py, src/invisible_playwright/_motion.py, src/invisible_playwright/_recaptcha_seed.py, src/invisible_playwright/async_api.py, src/invisible_playwright/launcher.py, tests/test_async_api.py, tests/test_behaviour.py
  Architecture Overview
    · Data Flow: From Call to Cursor
  Configuration and Control
  Behavioral Planning (`_behaviour.py`)
    · Key Behavioral Features
  Motion Generation (`_motion.py`)
    · Mathematical Models
  Dispatch and Interception (`_cursor.py`)
    · Integration Mechanism

## · Process Lifecycle and Reaper  (L1282)
  源文件: CHANGELOG.md, pyproject.toml, src/invisible_playwright/_geo.py, src/invisible_playwright/_reaper.py, src/invisible_playwright/_recaptcha_seed.py, src/invisible_playwright/async_api.py, src/invisible_playwright/constants.py, src/invisible_playwright/download.py, src/invisible_playwright/launcher.py, tests/test_async_api.py, tests/test_cursor_wiring.py, tests/test_launcher_helpers.py
  Overview and Purpose
  Session Token Minting and Stamping
    · Implementation Details
    · Token Flow Diagram
  Lifetime Guards
    · Windows Job Objects and `spawn_into`
  The `reap()` Teardown Pattern
    · Execution Flow
    · Lifecycle Entity Mapping
  Implementation Comparison: Sync vs Async

## · Fingerprint Engine (fpforge)  (L1445)
  源文件: docs/configuration.md, docs/pinning.md, docs/quickstart.md, docs/recaptcha-v3-score.md, docs/sannysoft-explained.md, docs/screen-size-headless-tells.md, src/invisible_playwright/__init__.py, src/invisible_playwright/_fpforge/__init__.py, src/invisible_playwright/_headless.py, src/invisible_playwright/_pin.py, src/invisible_playwright/_proxy.py, tests/test_backcompat.py
  Core Concepts
    · Bayesian Coherence
    · The Sampling Pipeline
    · System Architecture Diagram
  Sub-Modules
    · [Bayesian Sampler and Network](#3.1)
    · [Profile Dataclasses](#3.2)
    · [Pinning System](#3.3)
    · [CPT Data Files](#3.4)
    · [Cookie and History Seeding](#3.5)
  Data Flow: From Seed to Code Entities
  Locked Identity

## · Bayesian Sampler and Network  (L1577)
  源文件: docs/configuration.md, docs/creepjs-explained.md, docs/headless-fonts-differ.md, docs/navigator-webdriver-explained.md, docs/pinning.md, docs/playwright-detected-as-bot.md, docs/playwright-stealth-levels.md, docs/quickstart.md, docs/recaptcha-v3-score.md, docs/sannysoft-explained.md, docs/screen-size-headless-tells.md, docs/webgl-renderer-strings.md
  Core Implementation
    · Bayesian Entities
    · Data Flow and Sampling
    · Code Entity Space to Bayesian Logic
  The Sampling Graph
    · GPU Pool and Classification
    · The Hidden `intra_tier` Variable
    · Font Whitelist Derivation
  Locked Identity Constants
  Conditional Probability Tables (CPTs)

## · Profile Dataclasses  (L1727)
  源文件: docs/configuration.md, docs/pinning.md, docs/quickstart.md, docs/recaptcha-v3-score.md, docs/sannysoft-explained.md, docs/screen-size-headless-tells.md, src/invisible_playwright/_fpforge/__init__.py, src/invisible_playwright/_headless.py, src/invisible_playwright/_proxy.py, src/invisible_playwright/_recaptcha_seed.py, src/invisible_playwright/async_api.py, src/invisible_playwright/launcher.py
    · Overview of Data Flow
    · The Profile Dataclass
    · Sub-Profile Components
    · Generating Profiles
    · Seeded History and Cookies
    · Integration: Profile to Preferences

## · Pinning System  (L1926)
  源文件: docs/configuration.md, docs/pinning.md, docs/quickstart.md, docs/recaptcha-v3-score.md, docs/sannysoft-explained.md, docs/screen-size-headless-tells.md, src/invisible_playwright/__init__.py, src/invisible_playwright/_pin.py, tests/test_core_pin.py, tests/test_pin.py, tests/test_seal_floor.py
  Core Logic and Data Structures
    · Validation Tables
    · Internal Mapping (`_PIN_TO_RAW`)
  Implementation Flow
    · Pin Propagation Pipeline
  Key Functions
    · `_validate_pin_key(key: str)`
    · `_apply_pins_to_raw(raw, pin)`
  Bayesian Coherence Implications
    · Coherence Mapping
  Supported Pin Keys

## · CPT Data Files  (L2054)
  源文件: docs/configuration.md, docs/pinning.md, docs/quickstart.md, docs/recaptcha-v3-score.md, docs/sannysoft-explained.md, docs/screen-size-headless-tells.md, src/invisible_playwright/_fpforge/__init__.py, src/invisible_playwright/_headless.py, src/invisible_playwright/_proxy.py, tests/test_backcompat.py, tests/test_cloak.py, tests/test_fingerprint_surface.py
  Bayesian Network Topology
    · Data Flow: From Priors to Profiles
  Core CPT Definitions
    · 1. Hardware Concurrency
    · 2. Screen Distributions
    · 3. Storage Quota
    · 4. WebGL MSAA
    · 5. Audio, Codecs, and Fonts
  CPT Relationship Mapping
  Implementation Details
    · Pinning and Sampling Interaction
    · Profile Integration

## · Cookie and History Seeding  (L2205)
  源文件: docs/configuration.md, docs/pinning.md, docs/quickstart.md, docs/recaptcha-v3-score.md, docs/sannysoft-explained.md, docs/screen-size-headless-tells.md, src/invisible_playwright/_recaptcha_seed.py, src/invisible_playwright/async_api.py, src/invisible_playwright/launcher.py, tests/test_async_api.py, tests/test_launcher_helpers.py, tests/test_recaptcha_seed.py
  Deterministic Cookie Generation
    · Sub-seeding via FNV-1a
    · The Google Batch
  Cookie Profiles and Recipes
    · Supported Profiles
    · Implementation Logic Flow
  Locale-Derived Consent
  Integration in Launcher
    · Sync API
    · Async API

## · Firefox Preference Translation  (L2346)
  源文件: docs/configuration.md, docs/pinning.md, docs/quickstart.md, docs/recaptcha-v3-score.md, docs/sannysoft-explained.md, docs/screen-size-headless-tells.md, scripts/ci_font_gate.py, src/invisible_playwright/_session.py, src/invisible_playwright/_webgl_personas.py, src/invisible_playwright/prefs.py, tests/test_canvas_render_stealth.py, tests/test_ci_font_gate_declaration.py
  Overview of the Translation Pipeline
    · The Stealth Namespace
    · Determinism
    · System Architecture
  Baseline and Identity Overrides
  Platform-Specific Branching
    · Cross-Platform Normalization
  Key Preference Categories

## · translate_profile_to_prefs  (L2493)
  源文件: scripts/ci_font_gate.py, src/invisible_playwright/_session.py, src/invisible_playwright/_webgl_personas.py, src/invisible_playwright/prefs.py, tests/test_canvas_render_stealth.py, tests/test_ci_font_gate_declaration.py, tests/test_integration.py, tests/test_prefs_composition_arm.py
  Overview of the Translation Pipeline
    · Data Flow Diagram: Profile to Prefs
  Function Parameters and Composition
  The Stealth Baseline and Identity
  Helper Logic and Platform Overlays
    · Font Metrics and Generics
    · Platform Branching
  Implementation Details: Profile Mapping

## · Platform-Specific Preference Logic  (L2643)
  源文件: docs/ai-browser-agents-stealth.md, docs/browser-use-detection.md, docs/bundled-fonts-cross-platform.md, docs/canvas-fingerprint-noise.md, docs/canvas-webgl-cross-platform-consistency.md, docs/crawl4ai-stealth-custom-browser.md, docs/creepjs-explained.md, docs/headless-fonts-differ.md, docs/navigator-webdriver-explained.md, docs/playwright-detected-as-bot.md, docs/playwright-stealth-levels.md, docs/webgl-renderer-strings.md
  Overview of Platform Branching
    · Data Flow: Profile to Platform Prefs
  Windows-Specific Logic
    · GPU and WebGL Handling
    · System Color Palette
  Linux-Specific Logic
    · GPU Spoofing (ANGLE Injection)
    · Font Metric Compensation
    · Xvfb and WebRender Workarounds
  Key Entity Mapping
  Implementation Details
    · Font Metric Logic
    · Summary Table: Preference Divergence

## · Proxy Configuration  (L2829)
  源文件: docs/resist-fingerprinting.md, docs/speech-synthesis-voices.md, docs/webrtc-leak-proxy.md, src/invisible_playwright/_recaptcha_seed.py, src/invisible_playwright/async_api.py, src/invisible_playwright/launcher.py, tests/test_async_api.py, tests/test_launcher_helpers.py, tests/test_proxy_socks_auth_e2e.py, tests/test_recaptcha_seed.py
  Dual-Path Routing Strategy
    · Data Flow: Proxy Configuration
  SOCKS Configuration via Firefox Prefs
    · Preference Keys
    · Implementation Details
  Patched nsProtocolProxyService
  WebRTC Egress Resolution

## · CLI Reference  (L2950)
  源文件: .github/workflows/user-install.yml, docs/cli-reference.md, docs/installation.md, src/invisible_playwright/__init__.py, src/invisible_playwright/_pin.py, src/invisible_playwright/cli.py, tests/test_cli.py, tests/test_core_pin.py, tests/test_release_e2e.py, tests/test_seal_floor.py, tests/test_upgrade_e2e.py, tests/test_version.py
    · CLI Entry Points
    · Command Dispatch Architecture
    · Subcommand Reference
    · Binary Management and Logic
    · Environment Variables
    · Error Handling and Testing

## · Testing Infrastructure  (L3118)
  源文件: .github/workflows/e2e-hunt.yml, .github/workflows/e2e.yml, .github/workflows/firefox-launch-matrix.yml, .github/workflows/publish.yml, .github/workflows/tests.yml, .github/workflows/user-install.yml, .github/workflows/webrtc-e2e.yml, scripts/run_e2e.py, src/invisible_playwright/cli.py, tests/conftest.py, tests/test_cli.py, tests/test_e2e.py
    · Test Suite Structure
    · Hang Detection (Watchdog)
    · CI/CD Infrastructure
    · Test Configuration and Fixtures
    · Execution Guide
    · Detailed Test Categories

## · Unit and Integration Tests  (L3237)
  源文件: src/invisible_playwright/_behaviour.py, src/invisible_playwright/_cursor.py, src/invisible_playwright/_engine.py, src/invisible_playwright/_motion.py, src/invisible_playwright/_reaper.py, src/invisible_playwright/_webgl_personas.py, src/invisible_playwright/prefs.py, tests/test_behaviour.py, tests/test_canvas_render_stealth.py, tests/test_cursor_dispatch.py, tests/test_cursor_wiring.py, tests/test_integration.py
  Overview and Scope
  Data Flow: Seed to Preferences
  Unit Test Modules
    · 1. Preference Translation (`src/invisible_playwright/prefs.py`)
    · 2. Process Lifecycle and Reaper (`tests/test_reaper.py`)
    · 3. Cursor Motion and Behaviour (`tests/test_motion.py`, `tests/test_behaviour.py`)
    · 4. Launcher Configuration (`tests/test_launcher_config.py`)
  Integration Test Patterns (`test_integration.py`)
    · Key Integration Checks
  Stealth Regression Tests (`tests/test_canvas_render_stealth.py`)

## · End-to-End and Build Tests  (L3386)
  源文件: .github/workflows/e2e-hunt.yml, .github/workflows/e2e.yml, .github/workflows/firefox-launch-matrix.yml, .github/workflows/publish.yml, .github/workflows/tests.yml, .github/workflows/user-install.yml, .github/workflows/webrtc-e2e.yml, scripts/run_e2e.py, src/invisible_playwright/cli.py, tests/conftest.py, tests/test_cli.py, tests/test_cross_origin_iframe.py
  Overview of Test Categories
  End-to-End Lifecycle and Detectors
    · Detector Validation (`test_detectors_e2e.py`)
    · Mouse and Humanization (`test_mouse.py`)
  CLI and Release Infrastructure
    · CLI Tests (`test_cli.py`)
    · User-Install and Release (`test_release_e2e.py`)
  CI/CD Workflows (`.github/workflows/`)
    · Test Matrix and Floor (`tests.yml`)
    · E2E and Hang Detection (`e2e.yml` & `e2e-hunt.yml`)
    · Publication Gate (`publish.yml`)

## · Stealth Concepts and Detection Reference  (L3537)
  源文件: docs/botd-explained.md, docs/cdc-variable-explained.md, docs/configuration.md, docs/creepjs-explained.md, docs/fingerprintjs-visitor-id.md, docs/headless-fonts-differ.md, docs/navigator-webdriver-explained.md, docs/pinning.md, docs/playwright-detected-as-bot.md, docs/playwright-stealth-levels.md, docs/quickstart.md, docs/recaptcha-v3-score.md
  The Three Levels of Stealth
    · Sources:
  Key Detection Vectors
    · 1. Automation Artifacts
    · 2. Hardware and Environment (The "Server" Tell)
    · 3. Network and Metadata
    · Sources:
  The Concept of Determinism
    · Code Entity Space: Fingerprint Generation
    · Sources:
  Detection Tooling Reference
    · System Mapping: Detection Interaction
    · Sources:
  Child Pages

## · Detection Surfaces and Fingerprinting  (L3705)
  源文件: docs/ai-browser-agents-stealth.md, docs/audiocontext-fingerprinting.md, docs/browser-use-detection.md, docs/bundled-fonts-cross-platform.md, docs/canvas-fingerprint-noise.md, docs/canvas-webgl-cross-platform-consistency.md, docs/crawl4ai-stealth-custom-browser.md, docs/creepjs-explained.md, docs/hardware-concurrency-device-memory.md, docs/headless-fonts-differ.md, docs/hover-mouse-movement-bug.md, docs/human-mouse-movement.md
  Core Identity Surfaces
  Graphics and Rendering (WebGL & Canvas)
    · WebGL Renderer and ANGLE
    · Canvas Fingerprinting
  Font Subsystem and Metrics
  Network and Environment Consistency
    · WebRTC ICE Candidates
    · TLS/JA3/JA4 Fingerprints
    · Timezone and Locale
  Implementation Mapping
    · From Detection Surface to Code Entity
    · Data Flow: Profile to Browser Surface
  Summary of Detection Resistance

## · Comparisons with Other Tools  (L3881)
  源文件: docs/creepjs-explained.md, docs/headless-fonts-differ.md, docs/headless-vs-headful.md, docs/navigator-webdriver-explained.md, docs/playwright-detected-as-bot.md, docs/playwright-proxy-per-context.md, docs/playwright-socks5-proxy-authentication.md, docs/playwright-stealth-levels.md, docs/vs-camoufox.md, docs/vs-fingerprint-suite.md, docs/vs-nodriver.md, docs/vs-patchright.md
  The Three Stealth Levels Framework
    · Logic Flow: Detection vs. Intervention Depth
  Comparison: invisible_playwright vs. Level 1 (playwright-stealth)
    · The "Same Runtime" Race
  Comparison: invisible_playwright vs. Level 2 (Patchright / rebrowser)
    · CDP vs. Juggler
    · The Hardware Wall
  Comparison: invisible_playwright vs. Level 3 (Camoufox)
  Technical Summary: Why Engine Patching Wins

## · Integrations  (L4029)
  源文件: README.md, docs/README.md, docs/badges/telegram.svg, docs/banner-dark.png, docs/banner-light.png, docs/integrations/README.md, docs/integrations/codeceptjs.md, docs/integrations/crawlee-js.md, docs/integrations/crawlee-python.md, docs/integrations/other-languages.md, docs/integrations/playwright-mcp.md, docs/integrations/robot-framework.md
  The Integration Pattern
    · Integration Architecture
  Framework Integrations
  AI Agent and MCP Integrations
  Test Runner Integrations
    · Summary of Test Runner Support

## · Framework Integrations  (L4178)
  源文件: docs/integrations/codeceptjs.md, docs/integrations/crawlee-js.md, docs/integrations/crawlee-python.md, docs/integrations/other-languages.md, docs/integrations/playwright-mcp.md, docs/integrations/robot-framework.md, docs/integrations/scrapy-playwright.md, docs/integrations/test-runners.md, src/invisible_playwright/config.py, tests/unit/test_config_public.py
  Integration Strategies
    · The Config API
    · Implementation Data Flow
  Scrapy-Playwright (Python)
    · Implementation Details
  Crawlee (Python & JavaScript)
    · Crawlee for Python
    · Crawlee for JavaScript
  Robot Framework
    · Configuration Example
  Test Runners (Cypress, WebdriverIO, CodeceptJS)
  Other Languages (Go, Java, C#, Ruby, Rust)
  Feature Limitations Outside Python

## · AI Agent and MCP Integrations  (L4340)
  源文件: docs/ai-browser-agents-stealth.md, docs/browser-use-detection.md, docs/bundled-fonts-cross-platform.md, docs/canvas-fingerprint-noise.md, docs/canvas-webgl-cross-platform-consistency.md, docs/crawl4ai-stealth-custom-browser.md, docs/http-basic-auth-playwright-http-credentials.md, docs/integrations/codeceptjs.md, docs/integrations/crawlee-js.md, docs/integrations/crawlee-python.md, docs/integrations/other-languages.md, docs/integrations/playwright-mcp.md
  Integration Architecture
    · Data Flow: Agent to Patched Engine
  Playwright MCP Integration
    · Implementation
  Parallel Agent Sessions and Fingerprinting
    · Deterministic Fingerprinting
  Stealth Requirements for AI Agents
    · Behavioral Mitigation
    · Integration Limitations

## · Release and CI/CD Infrastructure  (L4507)
  源文件: .gitattributes, .githooks/pre-push, .github/workflows/firefox-launch-matrix.yml, .github/workflows/publish.yml, .github/workflows/tests.yml, .github/workflows/user-install.yml, .github/workflows/webrtc-e2e.yml, PUBLISHED.json, scripts/install_hooks.py, src/invisible_playwright/cli.py, tests/test_cli.py, tests/test_mouse.py
    · System Overview: Release & CI Logic
  10.1 Publication Gate and Release Ledger
  10.2 CI Workflows and Gates

## · Publication Gate and Release Ledger  (L4614)
  源文件: .gitattributes, .githooks/pre-push, .github/workflows/firefox-launch-matrix.yml, .github/workflows/publish.yml, .github/workflows/tests.yml, .github/workflows/user-install.yml, .github/workflows/webrtc-e2e.yml, PUBLISHED.json, scripts/install_hooks.py, src/invisible_playwright/cli.py, tests/test_cli.py, tests/test_mouse.py
  Release Integrity Architecture
    · Release Flow and Data Gateways
  The Release Ledger (`PUBLISHED.json`)
    · Ledger Structure and Validation
  Publication Gates (`publish.yml`)
    · 1. Dependency Synchronization Gate
    · 2. Index Probing and Idempotency
    · 3. OIDC Trusted Publishing
  Local Integrity: Pre-Push Hooks
    · Hook Mechanism
  Release Validation Tests
    · `test_release_e2e.py`
    · `test_upgrade_e2e.py`
  CLI Version and Diagnostic Reporting

## · CI Workflows and Gates  (L4765)
  源文件: .github/workflows/e2e-hunt.yml, .github/workflows/e2e.yml, .github/workflows/firefox-launch-matrix.yml, .github/workflows/publish.yml, .github/workflows/tests.yml, .github/workflows/webrtc-e2e.yml, scripts/ci_drive_gate.py, scripts/ci_font_gate.py, scripts/run_e2e.py, src/invisible_playwright/_session.py, tests/conftest.py, tests/test_ci_font_gate_declaration.py
  Core Workflows
    · 1. Unit Tests (`tests.yml`)
    · 2. End-to-End Suite (`e2e.yml`)
    · 3. WebRTC Realness (`webrtc-e2e.yml`)
    · 4. Windows Launch Matrix (`firefox-launch-matrix.yml`)
  Workflow Data Flow and Runners
  Specialized CI Scripts
    · `scripts/run_e2e.py`
    · `scripts/ci_drive_gate.py`
    · `scripts/ci_font_gate.py`
  Hang Detection and the Watchdog
    · Artifacts and Proofs
  Release Gates (`publish.yml`)

## · Glossary  (L4931)
  源文件: .gitattributes, .githooks/pre-push, .github/workflows/firefox-launch-matrix.yml, .github/workflows/publish.yml, .github/workflows/tests.yml, .github/workflows/webrtc-e2e.yml, CHANGELOG.md, PUBLISHED.json, README.md, docs/README.md, docs/badges/telegram.svg, docs/banner-dark.png
  1. Core Concepts
    · Stealth Patches (C++ Level)
    · Coherent Fingerprinting
    · Headed-on-Virtual-Display
  2. Fingerprint Engine (fpforge)
    · Bayesian Sampler
    · Key Data Structures
  3. Browser Launch & Display
    · Humanized Cursor Motion
    · Preference Translation
  4. Network & Proxy
    · Dual-Path Proxy Strategy
  5. Process Lifecycle
    · Reaper and Guards
  6. Jargon & Abbreviations