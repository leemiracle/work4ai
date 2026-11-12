# Skeleton: screenpipe（48 页）

| # | 页面 | full.md 行 | 大小 | mermaid | 表格 | 源文件数 |
|---|------|-----------|------|---------|------|---------|
| 1 | Overview | L6 | 9KB | 3 | ~5 | 14 |
| 2 | Installation | L251 | 9KB | 2 | ~1 | 29 |
| 3 | Quick Start | L453 | 12KB | 3 | ~5 | 29 |
| 4 | Core Concepts | L729 | 11KB | 3 | ~3 | 28 |
| 5 | Architecture | L960 | 12KB | 3 | ~2 | 25 |
| 6 | System Overview | L1192 | 12KB | 2 | ~4 | 27 |
| 7 | Data Capture Pipeline | L1385 | 15KB | 2 | ~6 | 29 |
| 8 | Audio Processing | L1626 | 16KB | 2 | ~2 | 25 |
| 9 | Storage & Database | L1879 | 13KB | 2 | ~4 | 28 |
| 10 | AI Gateway & Usage Tracking | L2141 | 14KB | 3 | ~3 | 26 |
| 11 | Desktop Application | L2397 | 11KB | 2 | ~8 | 21 |
| 12 | Application Lifecycle & Server | L2605 | 12KB | 3 | ~2 | 27 |
| 13 | Window Management & Overlays | L2824 | 13KB | 3 | ~2 | 20 |
| 14 | Timeline & Rewind | L3029 | 14KB | 2 | ~5 | 19 |
| 15 | Search & Filtering | L3212 | 12KB | 3 | ~2 | 16 |
| 16 | Settings & Configuration | L3444 | 13KB | 3 | ~4 | 24 |
| 17 | Global Shortcuts | L3650 | 11KB | 2 | ~3 | 18 |
| 18 | System Tray | L3841 | 14KB | 4 | ~2 | 16 |
| 19 | Onboarding & Health | L4093 | 12KB | 3 | ~5 | 20 |
| 20 | Account & Billing | L4277 | 10KB | 3 | ~0 | 20 |
| 21 | AI Integration | L4459 | 12KB | 2 | ~6 | 23 |
| 22 | Pi Coding Agent | L4660 | 14KB | 2 | ~2 | 18 |
| 23 | Pipes System | L4867 | 16KB | 2 | ~6 | 23 |
| 24 | MCP Server | L5118 | 11KB | 3 | ~2 | 21 |
| 25 | Connections & Third-Party Integrations | L5344 | 13KB | 2 | ~2 | 23 |
| 26 | Meetings & Activity Intelligence | L5523 | 17KB | 2 | ~2 | 22 |
| 27 | CLI & API | L5729 | 10KB | 2 | ~2 | 23 |
| 28 | CLI Installation & Commands | L5945 | 11KB | 2 | ~4 | 28 |
| 29 | HTTP API | L6142 | 9KB | 2 | ~4 | 26 |
| 30 | Component Registry | L6306 | 11KB | 4 | ~6 | 22 |
| 31 | Browser Extension | L6540 | 11KB | 2 | ~0 | 21 |
| 32 | Enterprise SDK | L6694 | 9KB | 2 | ~2 | 25 |
| 33 | Release & Distribution | L6845 | 10KB | 3 | ~3 | 12 |
| 34 | Desktop App Release | L7059 | 10KB | 3 | ~3 | 12 |
| 35 | CLI Release | L7268 | 9KB | 3 | ~3 | 22 |
| 36 | Enterprise Windows Release | L7475 | 10KB | 3 | ~0 | 19 |
| 37 | Distribution Channels | L7684 | 10KB | 3 | ~2 | 23 |
| 38 | Development | L7913 | 8KB | 2 | ~0 | 9 |
| 39 | Getting Started | L8090 | 9KB | 2 | ~2 | 19 |
| 40 | Build System | L8307 | 12KB | 2 | ~6 | 30 |
| 41 | Testing & Benchmarks | L8553 | 18KB | 2 | ~2 | 28 |
| 42 | CI/CD Pipeline | L8786 | 12KB | 2 | ~0 | 31 |
| 43 | Contributing Guidelines | L9034 | 7KB | 3 | ~3 | 9 |
| 44 | Platform-Specific Details | L9203 | 10KB | 3 | ~2 | 20 |
| 45 | macOS | L9424 | 14KB | 2 | ~2 | 24 |
| 46 | Windows | L9630 | 12KB | 2 | ~0 | 26 |
| 47 | Linux | L9822 | 9KB | 3 | ~2 | 17 |
| 48 | Glossary | L10036 | 18KB | 2 | ~3 | 26 |


## · Overview  (L6)
  源文件: CLAUDE.md, LICENSE.md, README.md, apps/screenpipe-app-tauri/src-tauri/src/enterprise_install_metadata.rs, apps/screenpipe-app-tauri/src-tauri/src/enterprise_policy.rs, apps/screenpipe-app-tauri/tsconfig.json, ee/README.md, ee/desktop/components/enterprise-settings-guard.tsx, ee/desktop/components/license-key-input.tsx, ee/desktop/hooks/use-enterprise.ts, ee/desktop/index.ts, ee/desktop/lib/admin-policy.ts
  What is Screenpipe?
  Core Capabilities
  System Components
  Data Flow
  Deployment Models
    · Desktop Application
    · CLI Application
    · SDK
  Storage & Performance

## · Installation  (L251)
  源文件: LICENSE.md, README.md, apps/screenpipe-app-tauri/src-tauri/src/enterprise_install_metadata.rs, apps/screenpipe-app-tauri/src-tauri/src/enterprise_policy.rs, apps/screenpipe-app-tauri/tsconfig.json, docs/mintlify/docs-mintlify-mig-tmp/ai-memory.mdx, docs/mintlify/docs-mintlify-mig-tmp/architecture.mdx, docs/mintlify/docs-mintlify-mig-tmp/claude-code.mdx, docs/mintlify/docs-mintlify-mig-tmp/cli-reference.mdx, docs/mintlify/docs-mintlify-mig-tmp/cline.mdx, docs/mintlify/docs-mintlify-mig-tmp/cloud-archive.mdx, docs/mintlify/docs-mintlify-mig-tmp/continue.mdx
  Installation Methods Overview
  Desktop Application
    · Platform Support
    · Setup & Onboarding
  CLI Installation
    · Quick Start
    · Troubleshooting CLI
    · MCP Server Installation
  Building from Source
    · Prerequisites
    · Linux Dependencies
  Development & Deployment Details
    · Local API Verification
    · Enterprise Deployment
    · Key File Locations

## · Quick Start  (L453)
  源文件: LICENSE.md, README.md, apps/screenpipe-app-tauri/src-tauri/src/enterprise_install_metadata.rs, apps/screenpipe-app-tauri/src-tauri/src/enterprise_policy.rs, apps/screenpipe-app-tauri/tsconfig.json, docs/mintlify/docs-mintlify-mig-tmp/ai-memory.mdx, docs/mintlify/docs-mintlify-mig-tmp/architecture.mdx, docs/mintlify/docs-mintlify-mig-tmp/claude-code.mdx, docs/mintlify/docs-mintlify-mig-tmp/cli-reference.mdx, docs/mintlify/docs-mintlify-mig-tmp/cline.mdx, docs/mintlify/docs-mintlify-mig-tmp/cloud-archive.mdx, docs/mintlify/docs-mintlify-mig-tmp/continue.mdx
  Installation Options
    · Desktop Application (Recommended)
    · CLI-Only Mode
  First Launch: Permissions Setup
    · Permission Flow Diagram
    · Required Permissions
  Server Startup and Health Monitoring
    · Startup Sequence
    · Health Check Response
  Verifying Recording Activity
    · Data Flow
    · Indicators of Success
  Searching Your First Data
    · Simple Search Example
    · Search Parameters
  Connecting to AI (MCP)
    · Installation
    · Example AI Interaction
  Next Steps

## · Core Concepts  (L729)
  源文件: LICENSE.md, README.md, apps/screenpipe-app-tauri/components/settings/general-settings.tsx, apps/screenpipe-app-tauri/components/settings/privacy-section.tsx, apps/screenpipe-app-tauri/lib/cache.ts, apps/screenpipe-app-tauri/src-tauri/src/capture_session.rs, apps/screenpipe-app-tauri/src-tauri/src/enterprise_install_metadata.rs, apps/screenpipe-app-tauri/src-tauri/src/enterprise_policy.rs, apps/screenpipe-app-tauri/src-tauri/src/server_core.rs, apps/screenpipe-app-tauri/tsconfig.json, crates/screenpipe-audio/src/audio_manager/builder.rs, crates/screenpipe-config/src/recording.rs
  Event-Driven Capture
    · Trigger Events
    · Accessibility Tree Extraction vs OCR
  Local-First Data Storage
    · File System Structure
    · Database Architecture
  Pipes System
    · Pipe Execution Lifecycle
  MCP Integration
    · Implementation
  Privacy Model

## · Architecture  (L960)
  源文件: Cargo.lock, Cargo.toml, apps/screenpipe-app-tauri/components/settings/general-settings.tsx, apps/screenpipe-app-tauri/components/settings/privacy-section.tsx, apps/screenpipe-app-tauri/components/settings/recording-settings.tsx, apps/screenpipe-app-tauri/lib/cache.ts, apps/screenpipe-app-tauri/lib/hooks/use-settings.tsx, apps/screenpipe-app-tauri/lib/utils/tauri.ts, apps/screenpipe-app-tauri/src-tauri/Cargo.lock, apps/screenpipe-app-tauri/src-tauri/Cargo.toml, apps/screenpipe-app-tauri/src-tauri/src/capture_session.rs, apps/screenpipe-app-tauri/src-tauri/src/commands.rs
  System Topology
  Desktop Application Architecture
  Data Capture & Recording Configuration
  Workspace & Build Configuration
  Related Documentation

## · System Overview  (L1192)
  源文件: Cargo.lock, Cargo.toml, apps/screenpipe-app-tauri/components/settings/general-settings.tsx, apps/screenpipe-app-tauri/components/settings/privacy-section.tsx, apps/screenpipe-app-tauri/components/settings/recording-settings.tsx, apps/screenpipe-app-tauri/components/update-banner.tsx, apps/screenpipe-app-tauri/lib/cache.ts, apps/screenpipe-app-tauri/lib/hooks/use-settings.tsx, apps/screenpipe-app-tauri/lib/utils/tauri.ts, apps/screenpipe-app-tauri/src-tauri/Cargo.lock, apps/screenpipe-app-tauri/src-tauri/Cargo.toml, apps/screenpipe-app-tauri/src-tauri/src/capture_session.rs
  Component Topology
  1. Desktop Application (Tauri Shell)
    · Key Responsibilities
  2. Embedded Server & Recording Orchestration
    · ServerCore vs. CaptureSession
    · Boot Phase & Health
  3. Storage & Database Layer
    · Configuration Recovery & Security
  4. AI Layer (Pi Agent & Gateway)
    · Pi Coding Agent
    · AI Provider Routing
  Data Flow Summary

## · Data Capture Pipeline  (L1385)
  源文件: COVERAGE.md, apps/screenpipe-app-tauri/lib/hooks/use-permission-monitor.tsx, apps/screenpipe-app-tauri/src-tauri/src/engine_events/permission.rs, apps/screenpipe-app-tauri/src-tauri/src/monitor_events.rs, apps/screenpipe-app-tauri/src-tauri/src/notifications/client.rs, coverage/CORE.md, coverage/README.md, coverage/core-engine-map.json, coverage/scripts/generate-core-engine-coverage-report.ts, coverage/scripts/generate-unified-coverage-report.ts, crates/screenpipe-a11y/Cargo.toml, crates/screenpipe-a11y/examples/linux_e2e.rs
  Overview
  Screen Capture Pipeline
    · Capture Triggers
    · EventDrivenCapture and Vision Management
    · Accessibility Tree Extraction
    · DRM Detection
    · UI Event Monitoring
    · Monitor Watching and Lifecycle
    · Data Structures

## · Audio Processing  (L1626)
  源文件: TESTING.md, apps/screenpipe-app-tauri/lib/utils/live-capture-state.test.ts, apps/screenpipe-app-tauri/lib/utils/live-capture-state.ts, apps/screenpipe-app-tauri/src-tauri/src/engine_events.rs, apps/screenpipe-app-tauri/src-tauri/src/engine_events/audio_device.rs, apps/screenpipe-app-tauri/src-tauri/src/engine_events/audio_health.rs, crates/screenpipe-audio/Cargo.toml, crates/screenpipe-audio/examples/wer_battle_test.rs, crates/screenpipe-audio/onnxruntime-win-x64-1.22.0.zip, crates/screenpipe-audio/scripts/gen_wer_corpus.sh, crates/screenpipe-audio/src/audio_manager/device_monitor.rs, crates/screenpipe-audio/src/audio_manager/manager.rs
  Purpose and Scope
  System Architecture
    · Audio Flow: Device Capture to Database
  AudioManager
    · Handler Architecture
  Audio Capture Pipeline
    · CoreAudio Process Tap (macOS)
    · Stream Reliability
  Transcription Engines
    · Local vs. Cloud Engines
    · MLX Memory Management (macOS)
  Batch Reconciliation
    · Reconciliation Process
  Diarization and Speaker Identification
    · Diarization Pipeline

## · Storage & Database  (L1879)
  源文件: apps/screenpipe-app-tauri/components/settings/speakers-section.tsx, apps/screenpipe-app-tauri/src-tauri/src/auth_token.rs, apps/screenpipe-app-tauri/src-tauri/src/sync.rs, crates/screenpipe-config/src/defaults.rs, crates/screenpipe-core/src/sync/keys.rs, crates/screenpipe-core/src/sync/manager.rs, crates/screenpipe-core/src/sync/mod.rs, crates/screenpipe-db/Cargo.toml, crates/screenpipe-db/benches/db_benchmarks.rs, crates/screenpipe-db/benches/search_accuracy.rs, crates/screenpipe-db/src/db/maintenance.rs, crates/screenpipe-db/src/db/mod.rs
  Database Configuration
  Schema Overview
  Write Coalescing Queue
    · Implementation: `write_queue.rs`
  Transaction Management with ImmediateTx
  Retention & Archiving
    · Local Retention
    · Cloud Archive
  Cloud Sync Provider
  Speaker Management

## · AI Gateway & Usage Tracking  (L2141)
  源文件: apps/screenpipe-app-tauri/components/rewind/ai-presets-selector.tsx, apps/screenpipe-app-tauri/components/settings/ai-presets.tsx, packages/ai-gateway/bun.lock, packages/ai-gateway/migrations/0004_add_cache_token_columns.sql, packages/ai-gateway/package.json, packages/ai-gateway/router-eval/benchmark.ts, packages/ai-gateway/router-eval/dataset.ts, packages/ai-gateway/src/handlers/chat.ts, packages/ai-gateway/src/handlers/difficulty-router.ts, packages/ai-gateway/src/handlers/models.ts, packages/ai-gateway/src/handlers/vertex-proxy.ts, packages/ai-gateway/src/index.ts
  Architecture Overview
    · System Topology
  Tier System and Access Limits
    · Tier Configuration
    · Tier Determination Logic
  Usage Tracking & Credit System
    · Credit Deduction Flow
    · Cost Tracking & Daily Caps
  Model Routing & Resilience
    · Cascade Logic
    · Provider Implementation Details
  Model Catalog & Metadata

## · Desktop Application  (L2397)
  源文件: .gitignore, Cargo.lock, Cargo.toml, apps/screenpipe-app-tauri/.gitignore, apps/screenpipe-app-tauri/components/settings/recording-settings.tsx, apps/screenpipe-app-tauri/lib/hooks/use-settings.tsx, apps/screenpipe-app-tauri/lib/utils/tauri.ts, apps/screenpipe-app-tauri/src-tauri/Cargo.lock, apps/screenpipe-app-tauri/src-tauri/Cargo.toml, apps/screenpipe-app-tauri/src-tauri/src/commands.rs, apps/screenpipe-app-tauri/src-tauri/src/embedded_server.rs, apps/screenpipe-app-tauri/src-tauri/src/main.rs
  Technology Stack
  Directory Structure
  Rust Backend
    · Module Reference
  IPC Boundary
    · Command & Event Mapping
  Frontend Infrastructure
    · Settings & Configuration
    · Recording Settings UI

## · Application Lifecycle & Server  (L2605)
  源文件: Cargo.lock, Cargo.toml, apps/screenpipe-app-tauri/components/settings/general-settings.tsx, apps/screenpipe-app-tauri/components/settings/privacy-section.tsx, apps/screenpipe-app-tauri/components/settings/recording-settings.tsx, apps/screenpipe-app-tauri/components/update-banner.tsx, apps/screenpipe-app-tauri/lib/cache.ts, apps/screenpipe-app-tauri/lib/hooks/use-settings.tsx, apps/screenpipe-app-tauri/lib/utils/tauri.ts, apps/screenpipe-app-tauri/src-tauri/Cargo.lock, apps/screenpipe-app-tauri/src-tauri/Cargo.toml, apps/screenpipe-app-tauri/src-tauri/src/capture_session.rs
  Purpose and Scope
  Application Entry Point
  Embedded Server & Recording State
    · RecordingState Structure
  Health Monitoring & Boot Phases
    · Boot Phases
    · Health Polling Loop
  Recording State Management & Recovery
    · DB Wedge Recovery
    · Shutdown & Restart Gate
  Tray & UI Synchronization

## · Window Management & Overlays  (L2824)
  源文件: apps/screenpipe-app-tauri/app/notification-panel/layout.tsx, apps/screenpipe-app-tauri/app/notification-panel/page.tsx, apps/screenpipe-app-tauri/components/deeplink-handler.tsx, apps/screenpipe-app-tauri/components/notification-handler.tsx, apps/screenpipe-app-tauri/lib/__tests__/notification-actions.test.ts, apps/screenpipe-app-tauri/lib/hooks/use-notification-panel.ts, apps/screenpipe-app-tauri/lib/notifications.ts, apps/screenpipe-app-tauri/lib/notifications/actions.ts, apps/screenpipe-app-tauri/public/32x32.png, apps/screenpipe-app-tauri/src-tauri/src/native_notification.rs, apps/screenpipe-app-tauri/src-tauri/src/native_shortcut_reminder.rs, apps/screenpipe-app-tauri/src-tauri/src/window/content_process.rs
  Overview
  Window Types & IDs
    · Code Entity Mapping: Window Definitions
  macOS Implementation: NSPanel & Overlays
    · NSPanel Configuration
    · Focus Management
    · Gestures & Swizzling
  Windows Implementation: Click-Through & Monitor Awareness
    · Click-Through Logic
    · Monitor Positioning
  Native Overlays: Notifications & Shortcut Reminders
    · Notification Panel
    · Shortcut Reminder
  Window Lifecycle & Data Flow
    · State Transitions
    · Data Flow Diagram

## · Timeline & Rewind  (L3029)
  源文件: apps/screenpipe-app-tauri/components/__tests__/text-overlay.test.tsx, apps/screenpipe-app-tauri/components/__tests__/url-detection-benchmark-data.json, apps/screenpipe-app-tauri/components/__tests__/url-detection-benchmark.test.ts, apps/screenpipe-app-tauri/components/chat/standalone/prefill-context-banner.tsx, apps/screenpipe-app-tauri/components/rewind/current-frame-timeline.tsx, apps/screenpipe-app-tauri/components/rewind/hooks/use-date-navigation.ts, apps/screenpipe-app-tauri/components/rewind/hooks/use-frame-loading.ts, apps/screenpipe-app-tauri/components/rewind/hooks/use-live-text.ts, apps/screenpipe-app-tauri/components/rewind/hooks/use-scroll-zoom.ts, apps/screenpipe-app-tauri/components/rewind/hooks/use-timeline-filters.ts, apps/screenpipe-app-tauri/components/rewind/timeline.tsx, apps/screenpipe-app-tauri/components/rewind/timeline/app-context-popover.tsx
  Component Architecture
  State Management
    · useTimelineStore (Zustand)
    · Feature Hooks
  CurrentFrameTimeline: Loading Strategies
  Live Text (macOS VisionKit)
    · Implementation Flow
  Audio Transcript & Meetings
  AI Panel & Integration
  Navigation & Filters

## · Search & Filtering  (L3212)
  源文件: apps/screenpipe-app-tauri/app/search/page.tsx, apps/screenpipe-app-tauri/components/rewind/search-modal.tsx, apps/screenpipe-app-tauri/e2e/specs/search-request-priority.spec.ts, apps/screenpipe-app-tauri/lib/hooks/__tests__/use-keyword-search-store.test.ts, apps/screenpipe-app-tauri/lib/hooks/use-keyword-search-store.tsx, apps/screenpipe-app-tauri/lib/search/__tests__/facet-sql.test.ts, apps/screenpipe-app-tauri/lib/search/facet-sql.ts, crates/screenpipe-db/src/types.rs, crates/screenpipe-engine/benches/alloc_counter.rs, crates/screenpipe-engine/benches/hot_frame_cache.rs, crates/screenpipe-engine/src/hot_frame_cache.rs, crates/screenpipe-engine/src/routes/content.rs
  Search Modal Architecture
  Multi-Modal Search Flow
  FTS5 Search Implementation
  Faceted Filtering & SQL Autocomplete
  Search Highlighting
  Performance Optimization: Hot Frame Cache
  Privacy & Redaction in Search
  Search Suggestions

## · Settings & Configuration  (L3444)
  源文件: Cargo.lock, Cargo.toml, apps/screenpipe-app-tauri/components/settings/battery-saver-section.tsx, apps/screenpipe-app-tauri/components/settings/disk-usage-section.tsx, apps/screenpipe-app-tauri/components/settings/display-section.tsx, apps/screenpipe-app-tauri/components/settings/feedback-section.tsx, apps/screenpipe-app-tauri/components/settings/general-settings.tsx, apps/screenpipe-app-tauri/components/settings/notifications-settings.tsx, apps/screenpipe-app-tauri/components/settings/privacy-section.tsx, apps/screenpipe-app-tauri/components/settings/recording-settings.tsx, apps/screenpipe-app-tauri/components/settings/retention-settings.tsx, apps/screenpipe-app-tauri/components/settings/setting-previews.tsx
  Store Architecture
    · Store File Structure
    · Settings-Loss Recovery
    · Encryption & Security
  `useSettings` Hook
    · Key Types and Interfaces
  Hardware-Aware Defaults
  Recording Settings
    · Audio Configuration
    · Vision Configuration
  AI Presets & Providers
  Persistence and Data Flow

## · Global Shortcuts  (L3650)
  源文件: apps/screenpipe-app-tauri/app/shortcut-reminder/audio-equalizer.tsx, apps/screenpipe-app-tauri/app/shortcut-reminder/page.tsx, apps/screenpipe-app-tauri/app/shortcut-reminder/screen-matrix.tsx, apps/screenpipe-app-tauri/app/shortcut-reminder/use-overlay-data.ts, apps/screenpipe-app-tauri/components/onboarding/particle-stream.tsx, apps/screenpipe-app-tauri/lib/api.ts, apps/screenpipe-app-tauri/lib/hooks/use-health-check.tsx, apps/screenpipe-app-tauri/lib/hooks/use-timeline-store.tsx, apps/screenpipe-app-tauri/src-tauri/src/native_notification.rs, apps/screenpipe-app-tauri/src-tauri/src/native_shortcut_reminder.rs, apps/screenpipe-app-tauri/src-tauri/src/window/content_process.rs, apps/screenpipe-app-tauri/src-tauri/src/window/gesture.rs
  Purpose and Scope
  Shortcut Types and Defaults
  Architecture Overview
    · Natural Language to Code Entity Mapping
  Handler Logic and Main Thread Deferral
    · Main Thread Execution
  Shortcut Reminder Overlay
    · Meeting Integration Logic
    · Key Components:
  Dynamic Updates and Configuration
    · Persistence Flow
  Platform-Specific Implementation Details
    · macOS Gesture Interception
    · Windows Click-Through Overlay

## · System Tray  (L3841)
  源文件: apps/screenpipe-app-tauri/app/notification-panel/layout.tsx, apps/screenpipe-app-tauri/app/notification-panel/page.tsx, apps/screenpipe-app-tauri/components/deeplink-handler.tsx, apps/screenpipe-app-tauri/components/notification-handler.tsx, apps/screenpipe-app-tauri/components/update-banner.tsx, apps/screenpipe-app-tauri/lib/__tests__/notification-actions.test.ts, apps/screenpipe-app-tauri/lib/hooks/use-notification-panel.ts, apps/screenpipe-app-tauri/lib/notifications.ts, apps/screenpipe-app-tauri/lib/notifications/actions.ts, apps/screenpipe-app-tauri/public/32x32.png, apps/screenpipe-app-tauri/src-tauri/src/health.rs, apps/screenpipe-app-tauri/src-tauri/src/recording.rs
  Architecture Overview
  Tray Icon Management
    · Icon States and Theme Handling
    · Tooltip and Health Updates
  Menu Structure
    · Onboarding vs Full Menu
    · Dynamic Menu Items
  Notification Architecture
    · Notification Flow
    · Notification Payload and Actions
    · Native SwiftUI Panel (macOS)
    · Webview Notification Panel
  Menu State and Lifecycle
    · Memory Safety (Use-After-Free Prevention)

## · Onboarding & Health  (L4093)
  源文件: apps/screenpipe-app-tauri/app/onboarding/page.tsx, apps/screenpipe-app-tauri/app/permission-recovery/page.tsx, apps/screenpipe-app-tauri/app/shortcut-reminder/audio-equalizer.tsx, apps/screenpipe-app-tauri/app/shortcut-reminder/page.tsx, apps/screenpipe-app-tauri/app/shortcut-reminder/screen-matrix.tsx, apps/screenpipe-app-tauri/app/shortcut-reminder/use-overlay-data.ts, apps/screenpipe-app-tauri/components/chat/standalone/attachment-tray.tsx, apps/screenpipe-app-tauri/components/chat/standalone/hooks/use-chat-conversation-events.ts, apps/screenpipe-app-tauri/components/chat/standalone/queued-prompts-list.tsx, apps/screenpipe-app-tauri/components/chat/standalone/upgrade-quota-banner.tsx, apps/screenpipe-app-tauri/components/login-dialog.tsx, apps/screenpipe-app-tauri/components/onboarding/connect-apps.tsx
  Onboarding Flow
    · Onboarding State Machine
    · Engine Startup & Readiness
    · Permission Checks & Recovery
  Health Check System
    · useHealthCheck Hook
    · Health Response Structure
  External App Connections (Onboarding)
    · MCP Configuration
    · Pipe Selection

## · Account & Billing  (L4277)
  源文件: apps/screenpipe-app-tauri/components/app-entitlement-gate.test.tsx, apps/screenpipe-app-tauri/components/app-entitlement-gate.tsx, apps/screenpipe-app-tauri/components/chat/standalone/chat-composer.tsx, apps/screenpipe-app-tauri/components/settings/account-section.tsx, apps/screenpipe-app-tauri/components/settings/team-section.tsx, apps/screenpipe-app-tauri/e2e/specs/zz-app-entitlement-gate.spec.ts, apps/screenpipe-app-tauri/e2e/specs/zz-audio-fallback-reverify.spec.ts, apps/screenpipe-app-tauri/lib/__tests__/team-api-contract.test.ts, apps/screenpipe-app-tauri/lib/__tests__/team-crypto.test.ts, apps/screenpipe-app-tauri/lib/__tests__/upsell-gating.test.ts, apps/screenpipe-app-tauri/lib/app-entitlement.test.ts, apps/screenpipe-app-tauri/lib/app-entitlement.ts
  Entitlement & Access Control
    · Entitlement Logic Space to Code Mapping
  Authentication & Login
    · Login Flow
  Subscription & Billing
    · Checkout Process
  AI Usage Tracking
    · Usage Status Data Flow
  Team Management
    · Team Lifecycle & Crypto
  Sync Settings
    · Sync Controls

## · AI Integration  (L4459)
  源文件: apps/screenpipe-app-tauri/components/__tests__/chat-sidebar-grouping.test.ts, apps/screenpipe-app-tauri/components/chat-sidebar.tsx, apps/screenpipe-app-tauri/components/chat/chat-history-view.tsx, apps/screenpipe-app-tauri/components/hooks/use-chat-conversations.ts, apps/screenpipe-app-tauri/components/pipe-install-dialog.tsx, apps/screenpipe-app-tauri/components/pipe-store.tsx, apps/screenpipe-app-tauri/components/post-install-connections-modal.tsx, apps/screenpipe-app-tauri/components/settings/pipes-section.tsx, apps/screenpipe-app-tauri/components/standalone-chat.tsx, apps/screenpipe-app-tauri/components/ui/context-menu.tsx, apps/screenpipe-app-tauri/components/ui/dropdown-menu.tsx, apps/screenpipe-app-tauri/lib/__tests__/chat-storage.test.ts
  AI Integration Architecture
  Screenpipe API Foundation
  AI Provider Authentication
  Pi Agent Communication Protocol
  Pi Agent Skills & State
  Integration Paths Overview

## · Pi Coding Agent  (L4660)
  源文件: apps/screenpipe-app-tauri/components/__tests__/chat-sidebar-grouping.test.ts, apps/screenpipe-app-tauri/components/chat-sidebar.tsx, apps/screenpipe-app-tauri/components/chat/chat-history-view.tsx, apps/screenpipe-app-tauri/components/chat/standalone/ask-user-tool-card.test.tsx, apps/screenpipe-app-tauri/components/chat/standalone/ask-user-tool-card.tsx, apps/screenpipe-app-tauri/components/chat/standalone/chat-message-list.tsx, apps/screenpipe-app-tauri/components/chat/standalone/collapsed-steer-work-row.tsx, apps/screenpipe-app-tauri/components/chat/standalone/hooks/pi-types.ts, apps/screenpipe-app-tauri/components/chat/standalone/hooks/use-chat-message-actions.ts, apps/screenpipe-app-tauri/components/chat/standalone/hooks/use-chat-window-events.ts, apps/screenpipe-app-tauri/components/chat/standalone/hooks/use-pi-foreground-events.ts, apps/screenpipe-app-tauri/components/chat/standalone/hooks/use-pi-live-send.ts
  Architecture Overview
    · Component Topology
  PiManager & Process Management
    · Implementation Details
    · Multi-Session Architecture
  JSON-RPC Protocol & Event Routing
    · Event Routing (Agent Event Bus)
    · Session Status Mapping
  State Management: Chat Store
    · Data Flow & Persistence
  Skills & Installation
    · Skill Implementation
    · Automated Setup
  Data Flow: Natural Language to Code

## · Pipes System  (L4867)
  源文件: apps/screenpipe-app-tauri/components/__tests__/clean-pipe-stdout.test.ts, apps/screenpipe-app-tauri/components/__tests__/pipe-ndjson-to-chat.test.ts, apps/screenpipe-app-tauri/components/advisory-overlay.tsx, apps/screenpipe-app-tauri/components/pipe-install-dialog.tsx, apps/screenpipe-app-tauri/components/pipe-store.tsx, apps/screenpipe-app-tauri/components/post-install-connections-modal.tsx, apps/screenpipe-app-tauri/components/settings/pipes-section.tsx, apps/screenpipe-app-tauri/components/standalone-chat.tsx, apps/screenpipe-app-tauri/e2e/specs/chat-source-file-preview.spec.ts, apps/screenpipe-app-tauri/e2e/specs/focus-server.spec.ts, apps/screenpipe-app-tauri/e2e/specs/pipes-mcp-connections.spec.ts, apps/screenpipe-app-tauri/e2e/specs/pipes.spec.ts
  Purpose and Scope
  Pipe.md File Format
    · Example Pipe
    · Configuration Fields
  Scheduling System
    · Schedule Syntax
    · Event Triggers
  Execution Lifecycle
    · Context Header Injection
    · Execution Flow Diagram
  3-Layer Security & Permissions
    · 1. Permission Rules
    · 2. Environment Isolation
    · 3. Server-Side Enforcement
  Pipe Store & Discovery
    · Pipe Store UI
    · Local Management
  Key Components Reference

## · MCP Server  (L5118)
  源文件: apps/screenpipe-app-tauri/components/settings/custom-mcp-card.tsx, apps/screenpipe-app-tauri/components/settings/registry-browser.tsx, apps/screenpipe-app-tauri/lib/__tests__/mcp-registry.test.ts, apps/screenpipe-app-tauri/lib/mcp-registry.ts, apps/screenpipe-app-tauri/src-tauri/assets/extensions/mcp-bridge.ts, crates/screenpipe-connect/src/mcp_servers.rs, crates/screenpipe-core/assets/extensions/mcp-bridge.ts, crates/screenpipe-engine/src/cli/mcp.rs, crates/screenpipe-engine/src/mcp_servers_api.rs, crates/screenpipe-engine/src/oauth_result_page.rs, packages/screenpipe-mcp/.gitignore, packages/screenpipe-mcp/README.md
  Purpose
  Overview
  Architecture
    · Data Flow: Natural Language to Code Entities
    · Component Topology
  Installation & Setup
    · Automated Setup
    · Manual Configuration (Stdio)
    · Remote/Network Access (HTTP)
  MCP Tools
  Implementation Details
    · API Key Discovery
    · Dynamic MCP Server Management
    · Proxy-Tool Bridge
    · OAuth Integration

## · Connections & Third-Party Integrations  (L5344)
  源文件: apps/screenpipe-app-tauri/components/meeting-notes/calendar-connect-dialog.tsx, apps/screenpipe-app-tauri/components/settings/connections-section.tsx, apps/screenpipe-app-tauri/components/settings/google-calendar-card.tsx, apps/screenpipe-app-tauri/components/settings/google-docs-card.tsx, apps/screenpipe-app-tauri/src-tauri/src/oauth.rs, apps/screenpipe-app-tauri/src-tauri/src/secrets.rs, crates/screenpipe-audio/src/core/device_detection.rs, crates/screenpipe-audio/src/core/e2e_ghost_word_silent_room.rs, crates/screenpipe-audio/src/core/source_buffer.rs, crates/screenpipe-audio/tests/bluetooth_gap_hallucination_test.rs, crates/screenpipe-connect/src/connections/calcom.rs, crates/screenpipe-connect/src/connections/calendly.rs
  Overview
    · Connection Architecture Diagram
  Credential Management & Proxying
    · SecretStore
    · API Proxy Flow
  OAuth Flow Lifecycle
  Key Integrations
    · Microsoft 365 & Teams
    · Google Workspace (Gmail, Docs, Calendar)
    · WhatsApp
    · Local AI (Ollama & LM Studio)
  Code Entity Reference

## · Meetings & Activity Intelligence  (L5523)
  源文件: apps/screenpipe-app-tauri/app/error.tsx, apps/screenpipe-app-tauri/app/global-error.tsx, apps/screenpipe-app-tauri/app/layout.tsx, apps/screenpipe-app-tauri/app/providers.tsx, apps/screenpipe-app-tauri/components/conversation-bubble.tsx, apps/screenpipe-app-tauri/components/meeting-notes/coming-up.tsx, apps/screenpipe-app-tauri/components/meeting-notes/image-utils.ts, apps/screenpipe-app-tauri/components/meeting-notes/index.tsx, apps/screenpipe-app-tauri/components/meeting-notes/list-view.tsx, apps/screenpipe-app-tauri/components/meeting-notes/note-view.tsx, apps/screenpipe-app-tauri/components/meeting-notes/past-meetings.tsx, apps/screenpipe-app-tauri/components/meeting-notes/receipts.tsx
  Meeting Detection Engine
    · Architecture and Signal Philosophy
    · Candidate Resolution
    · Detection Flow
  Meeting Notes & Calendar Integration
    · Meeting Notes UI
    · Calendar & Enrichment
    · Data Flow for Meeting Management
  Live Streaming & Audio Intelligence
    · Streaming Lifecycle
    · Speaker Identification & Grouping
  Activity Intelligence & Summarization
    · Activity Context Bundling
    · Shortcut Reminder Overlay

## · CLI & API  (L5729)
  源文件: apps/screenpipe-app-tauri/components/settings/general-settings.tsx, apps/screenpipe-app-tauri/components/settings/privacy-section.tsx, apps/screenpipe-app-tauri/lib/cache.ts, apps/screenpipe-app-tauri/src-tauri/src/capture_session.rs, apps/screenpipe-app-tauri/src-tauri/src/server_core.rs, crates/screenpipe-audio/src/audio_manager/builder.rs, crates/screenpipe-config/src/recording.rs, crates/screenpipe-db/src/types.rs, crates/screenpipe-engine/benches/alloc_counter.rs, crates/screenpipe-engine/benches/hot_frame_cache.rs, crates/screenpipe-engine/src/bin/screenpipe-engine.rs, crates/screenpipe-engine/src/cli/mod.rs
  Overview
  CLI Installation & Commands
    · Core Commands
    · Pipe Management
  HTTP API
    · Authentication & API Key Management
    · Key Endpoints
    · Intelligence Features
  Component Registry
  Browser Extension
  Enterprise SDK
  Technical Architecture: API & Data Flow

## · CLI Installation & Commands  (L5945)
  源文件: apps/screenpipe-app-tauri/src-tauri/src/analytics.rs, crates/screenpipe-a11y/examples/linux_debug.rs, crates/screenpipe-a11y/examples/linux_deep.rs, crates/screenpipe-audio-eval/src/bin/screenpipe_fixtures.rs, crates/screenpipe-engine/src/analytics.rs, crates/screenpipe-engine/src/calendar_speaker_id.rs, crates/screenpipe-engine/src/cli/backup.rs, crates/screenpipe-engine/src/cli/browser.rs, crates/screenpipe-engine/src/cli/db.rs, crates/screenpipe-engine/src/cli/install.rs, crates/screenpipe-engine/src/cli/login.rs, crates/screenpipe-engine/src/cli/pipe.rs
  Installation Methods
    · 1. NPM Installation (Recommended)
    · 2. Platform-Specific Setup
    · 3. Build from Source
  CLI Command Architecture
    · Command Structure Diagram
  Core Commands & Usage
    · 1. Authentication & Tokens
    · 2. Pipe Management (`pipe`)
    · 3. AI Agent Setup
  Data Flow: Resource Monitoring & Telemetry
    · Resource Monitor Implementation
  CLI Environment Variables

## · HTTP API  (L6142)
  源文件: apps/screenpipe-app-tauri/lib/utils/live-capture-state.test.ts, apps/screenpipe-app-tauri/lib/utils/live-capture-state.ts, crates/screenpipe-audio/src/lib.rs, crates/screenpipe-audio/src/metrics.rs, crates/screenpipe-audio/src/speaker/prepare_segments.rs, crates/screenpipe-audio/src/transcription/deepgram/batch.rs, crates/screenpipe-audio/src/transcription/handle_new_transcript.rs, crates/screenpipe-audio/src/transcription/mod.rs, crates/screenpipe-audio/src/transcription/openai_compatible/batch.rs, crates/screenpipe-audio/src/transcription/transcription_result.rs, crates/screenpipe-audio/src/vad/mod.rs, crates/screenpipe-core/src/pii_removal.rs
  Purpose and Scope
  API Architecture
    · Data Flow and Entity Mapping
  Core API Endpoints
    · 1. Intelligence & Search
    · 2. Audio & Speaker Management
    · 3. System Health & Monitoring
  PII Redaction
  Request Processing Flow
  Context Window Optimization
  WebSocket Streaming

## · Component Registry  (L6306)
  源文件: apps/screenpipe-app-tauri/components/settings/__tests__/integration-icon-keys.test.ts, apps/screenpipe-app-tauri/components/settings/agent-card.tsx, apps/screenpipe-app-tauri/components/settings/custom-mcp-card.tsx, apps/screenpipe-app-tauri/components/settings/input-monitoring-card.tsx, apps/screenpipe-app-tauri/components/settings/registry-browser.tsx, apps/screenpipe-app-tauri/lib/__tests__/mcp-registry.test.ts, apps/screenpipe-app-tauri/lib/constants/connections.ts, apps/screenpipe-app-tauri/lib/hooks/use-hardcoded-tiles.ts, apps/screenpipe-app-tauri/lib/mcp-registry.ts, apps/screenpipe-app-tauri/lib/utils/connection-chip.test.ts, apps/screenpipe-app-tauri/lib/utils/connection-chip.ts, apps/screenpipe-app-tauri/public/images/bee.png
  Registry Structure
  Component Schema
  Register Command
  Connection & Agent Registry
    · Connection Registry Schema
    · Hardcoded Tile Detection
  MCP Server Registry
    · Storage Model
    · Registry API
  Security & Capabilities

## · Browser Extension  (L6540)
  源文件: apps/screenpipe-app-tauri/components/browser-sidebar.tsx, apps/screenpipe-app-tauri/e2e/specs/zz-owned-browser-background-nav.spec.ts, apps/screenpipe-app-tauri/lib/__tests__/owned-browser-ownership.test.ts, apps/screenpipe-app-tauri/lib/owned-browser-ownership.ts, apps/screenpipe-app-tauri/src-tauri/src/owned_browser.rs, apps/screenpipe-app-tauri/src-tauri/src/owned_browser_cookies.rs, crates/screenpipe-connect/src/connections/browser/bridge.rs, crates/screenpipe-connect/src/connections/browser/mod.rs, crates/screenpipe-connect/src/connections/browser/owned.rs, crates/screenpipe-engine/src/routes/browser.rs, packages/browser-extension/dist/manifest.json, packages/browser-extension/dist/options.html
  Browser Bridge (Chrome Extension)
    · Implementation Details
    · System Interaction Diagram
  Owned Browser
    · Implementation: Embedded Native Webview
    · Cookie Inheritance (Session Sync)
    · Owned Browser Integration Diagram
  Auth & Ownership Integration
    · Token Management
    · Navigation Ownership

## · Enterprise SDK  (L6694)
  源文件: LICENSE.md, README.md, apps/screenpipe-app-tauri/src-tauri/src/enterprise_install_metadata.rs, apps/screenpipe-app-tauri/src-tauri/src/enterprise_policy.rs, apps/screenpipe-app-tauri/tsconfig.json, crates/screenpipe-capture/Cargo.toml, crates/screenpipe-capture/src/lib.rs, ee/README.md, ee/desktop/components/enterprise-settings-guard.tsx, ee/desktop/components/license-key-input.tsx, ee/desktop/hooks/use-enterprise.ts, ee/desktop/index.ts
  Architecture & Platform Support
    · System Component Topology
  Recorder API & Session Management
    · Key Functions and Classes
    · Data Flow: Recording Lifecycle
  Privacy Filters & Permission Handling
    · Permission Management
  Telemetry and Enterprise Controls
  Multi-Platform Implementation
    · Tauri Plugin
    · Node.js (NAPI)
    · Swift Integration

## · Release & Distribution  (L6845)
  源文件: .github/scripts/assert_windows_audio_rms.ps1, .github/scripts/linux/bundle-appimage-runtime-deps.sh, .github/workflows/ci.yml, .github/workflows/e2e-test.yml, .github/workflows/linux-appimage-smoke.yml, .github/workflows/release-app.yml, .github/workflows/release-cli.yml, .github/workflows/release-enterprise.yml, .github/workflows/windows-integration-test.yml, apps/screenpipe-app-tauri/scripts/find_tools.js, apps/screenpipe-app-tauri/scripts/pre_build.js, apps/screenpipe-app-tauri/scripts/setup_openblas.js
  Scope
  Release Workflow Triggers
  Desktop App Release Pipeline
    · Runner Selection Strategy
    · Build Matrix and Targets
  CLI Release Pipeline
  Enterprise Release
  Platform-Specific Build Requirements
    · macOS
    · Windows
    · Linux
  Distribution Channels

## · Desktop App Release  (L7059)
  源文件: .github/scripts/assert_windows_audio_rms.ps1, .github/scripts/linux/bundle-appimage-runtime-deps.sh, .github/workflows/ci.yml, .github/workflows/e2e-test.yml, .github/workflows/linux-appimage-smoke.yml, .github/workflows/release-app.yml, .github/workflows/release-cli.yml, .github/workflows/release-enterprise.yml, .github/workflows/windows-integration-test.yml, apps/screenpipe-app-tauri/scripts/find_tools.js, apps/screenpipe-app-tauri/scripts/pre_build.js, apps/screenpipe-app-tauri/scripts/setup_openblas.js
  Workflow Overview
  Release Gating & Runner Selection
    · Commit Message Gate
    · Runner Selection
  Build Matrix & Cargo Features
    · Feature Flags
  Pre-Build Infrastructure
    · Native Dependency Staging
  macOS Notarization & Signing
  Windows Packaging & Signing
    · Code Signing and Driver Installation
    · Enterprise Releases
  Linux AppImage Repacking
    · Dependency Bundling
  Distribution via Cloudflare R2

## · CLI Release  (L7268)
  源文件: .github/scripts/assert_windows_audio_rms.ps1, .github/scripts/linux/bundle-appimage-runtime-deps.sh, .github/workflows/ci.yml, .github/workflows/e2e-test.yml, .github/workflows/linux-appimage-smoke.yml, .github/workflows/release-app.yml, .github/workflows/release-cli.yml, .github/workflows/release-enterprise.yml, .github/workflows/windows-integration-test.yml, apps/screenpipe-app-tauri/scripts/find_tools.js, apps/screenpipe-app-tauri/scripts/pre_build.js, apps/screenpipe-app-tauri/scripts/setup_openblas.js
  Workflow Overview
  Triggers and Gatekeeping
  Platform Build Jobs
    · macOS
    · Windows
    · Linux
  Data Flow: Build to Distribution
  Telemetry and Distribution Context
    · Resource Monitoring Flow
  Release Publication
    · npm Multi-Package Strategy
    · GitHub Releases

## · Enterprise Windows Release  (L7475)
  源文件: .github/scripts/assert_windows_audio_rms.ps1, .github/scripts/linux/bundle-appimage-runtime-deps.sh, .github/workflows/ci.yml, .github/workflows/e2e-test.yml, .github/workflows/linux-appimage-smoke.yml, .github/workflows/release-app.yml, .github/workflows/release-cli.yml, .github/workflows/release-enterprise.yml, .github/workflows/windows-integration-test.yml, apps/screenpipe-app-tauri/lib/hooks/use-enterprise-policy.ts, apps/screenpipe-app-tauri/scripts/find_tools.js, apps/screenpipe-app-tauri/scripts/pre_build.js
  Purpose & Scope
  Workflow Architecture
  Enterprise Authentication & Policy
    · Data Flow: License and Policy Enforcement
  Enterprise Telemetry Sync
    · Telemetry Architecture
  Code Signing Process
  Intune Packaging (.intunewin)
  Distribution & Notification

## · Distribution Channels  (L7684)
  源文件: .github/ci/ort-smoke/Cargo.toml, .github/ci/ort-smoke/src/main.rs, .github/scripts/assert_windows_audio_rms.ps1, .github/scripts/linux/bundle-appimage-runtime-deps.sh, .github/workflows/ci.yml, .github/workflows/close-inactive.yml, .github/workflows/e2e-test.yml, .github/workflows/linux-appimage-smoke.yml, .github/workflows/ort-init-smoke.yml, .github/workflows/release-app.yml, .github/workflows/release-browser-extension.yml, .github/workflows/release-cli.yml
  Overview
  GitHub Releases
    · CLI: Rolling `cli-latest` Release
    · Desktop App: Versioned GitHub Releases
  npm Registry
    · Core CLI and MCP Server
    · Enterprise SDK
  Cloudflare R2
  Sentry Debug Symbols
    · CLI and App Symbol Upload
  Enterprise: Microsoft Intune
  Privacy-Filter Tinfoil Enclave Deployment
    · Redaction Pipeline Implementation

## · Development  (L7913)
  源文件: .claude/skills/release/SKILL.md, .claude/skills/screenpipe-tauri/SKILL.md, .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/documentation.md, .github/ISSUE_TEMPLATE/feature_request.md, .github/ISSUE_TEMPLATE/question.md, .github/pull_request_template.md, CLAUDE.md, CONTRIBUTING.md
  Overview
  Development Environment Architecture
  Build System
  Testing & Benchmarks
  CI/CD Pipeline
  Contributing Guidelines
  Code Entity Map

## · Getting Started  (L8090)
  源文件: .cargo/config.toml, .claude/skills/release/SKILL.md, .claude/skills/screenpipe-tauri/SKILL.md, .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/documentation.md, .github/ISSUE_TEMPLATE/feature_request.md, .github/ISSUE_TEMPLATE/question.md, .github/pull_request_template.md, CONTRIBUTING.md, apps/screenpipe-app-tauri/bun.lock, apps/screenpipe-app-tauri/components/settings/storage-section.tsx, apps/screenpipe-app-tauri/lib/__tests__/context-pruning.test.ts
  Development Environment Setup
    · Development Setup Flow
    · Prerequisites
    · Cargo Workspace Configuration
  Workspace Structure & Key Entities
    · Code Entity Relationship Diagram
  Build Commands & Lifecycle
    · CLI & Core Build
    · Desktop App Build
  Development Principles & Extensions
    · Extension Logic
    · Testing Suite

## · Build System  (L8307)
  源文件: .gitattributes, .github/scripts/assert_windows_audio_rms.ps1, .github/scripts/audio_test.wav, .github/scripts/linux/bundle-appimage-runtime-deps.sh, .github/workflows/ci.yml, .github/workflows/e2e-test.yml, .github/workflows/linux-appimage-smoke.yml, .github/workflows/release-app.yml, .github/workflows/release-cli.yml, .github/workflows/release-enterprise.yml, .github/workflows/windows-integration-test.yml, .gitignore
  Overview
  Build System Architecture
  Pre-build Script (pre_build.js)
    · Platform-Specific Configuration
    · Bun Binary Management
  Cargo Build Scripts
    · screenpipe-app-tauri/src-tauri/build.rs
  Tauri Configuration
    · Resource Mapping (Windows)
  AI Runtime Setup
    · ONNX Runtime (ORT) Setup
    · Model Acceleration Flags
  Dependency Flow Diagram
  Code Entity Mapping

## · Testing & Benchmarks  (L8553)
  源文件: .github/scripts/e2e/lib.ts, .github/scripts/e2e/run-all.ts, .github/scripts/e2e/test-api.ts, .github/scripts/e2e/test-app-launch.ts, .github/scripts/e2e/test-capture-fidelity.ts, .github/scripts/e2e/test-chat.ts, .github/scripts/e2e/test-main-window.ts, .github/scripts/e2e/test-onboarding.ts, .github/scripts/e2e/test-permissions.ts, .github/scripts/e2e/test-recording.ts, .github/scripts/e2e/test-settings.ts, .github/workflows/benchmark.yml
  Test Organization
    · Core Test Suites
  System Topology & Code Entities
  Integration & Regression Testing
    · Audio Processing & Hardware
    · UI & System Integration
  End-to-End (E2E) Infrastructure
    · E2E Coverage Dashboard
    · Specialized E2E Specs
  Benchmarks & Performance Tracking
    · Automated Benchmark Suites
    · Performance Analysis

## · CI/CD Pipeline  (L8786)
  源文件: .github/ci/ort-smoke/Cargo.toml, .github/ci/ort-smoke/src/main.rs, .github/scripts/assert_windows_audio_rms.ps1, .github/scripts/check_logs.sh, .github/scripts/install_dependencies.sh, .github/scripts/linux/bundle-appimage-runtime-deps.sh, .github/scripts/run_screenpipe.sh, .github/scripts/test_audio_capture.sh, .github/scripts/test_ocr.sh, .github/workflows/benchmark.yml, .github/workflows/ci.yml, .github/workflows/close-inactive.yml
  Workflow Architecture Overview
  Continuous Integration (ci.yml)
    · Test Jobs
  Desktop App Release (release-app.yml)
    · Workflow Trigger Logic
    · Runner Selection
    · Feature Matrix
  Enterprise Release (release-enterprise.yml)
  MCP & SDK Release
    · MCP Server (release-mcp.yml)
    · SDK Release (sdk-release.yml)
  Integration and E2E Testing
    · E2E Tests (e2e-test.yml)
    · Windows CLI Integration (windows-integration-test.yml)
  Performance and Quality (style.yml, benchmark.yml)
    · Code Quality (style.yml)
    · Benchmarks (benchmark.yml)
  Build Automation Scripts
    · pre_build.js

## · Contributing Guidelines  (L9034)
  源文件: .claude/skills/release/SKILL.md, .claude/skills/screenpipe-tauri/SKILL.md, .github/ISSUE_TEMPLATE/bug_report.md, .github/ISSUE_TEMPLATE/documentation.md, .github/ISSUE_TEMPLATE/feature_request.md, .github/ISSUE_TEMPLATE/question.md, .github/pull_request_template.md, CLAUDE.md, CONTRIBUTING.md
  Design Principles
  Development Workflow
    · Local Development
    · macOS Permission Management
  Code Style & Linting
    · File Headers
    · Git Commit Messages
    · Tauri Bindings
  Pull Request Process
  Testing Suite
  Release Process

## · Platform-Specific Details  (L9203)
  源文件: apps/screenpipe-app-tauri/lib/utils/clipboard-image.test.ts, apps/screenpipe-app-tauri/lib/utils/clipboard-image.ts, apps/screenpipe-app-tauri/src-tauri/src/tray_monitor_preview.rs, crates/screenpipe-a11y/src/incognito/linux.rs, crates/screenpipe-a11y/src/incognito/macos.rs, crates/screenpipe-a11y/src/incognito/mod.rs, crates/screenpipe-a11y/src/incognito/titles.rs, crates/screenpipe-a11y/src/incognito/windows.rs, crates/screenpipe-a11y/src/tree/linux.rs, crates/screenpipe-a11y/src/tree/macos.rs, crates/screenpipe-a11y/src/tree/mod.rs, crates/screenpipe-a11y/src/tree/windows.rs
  Platform Build Matrix
  macOS Platform Details
    · Key Characteristics
  Windows Platform Details
    · Key Characteristics
  Linux Platform Details
    · Key Characteristics
  Code Entity Association
    · Platform Accessibility & Capture Drivers
    · OCR & Vision Pipeline Implementation
  Cross-Platform Dependency Summary
    · Build Configuration Summary

## · macOS  (L9424)
  源文件: TESTING.md, apps/screenpipe-app-tauri/components/chat/standalone/prefill-context-banner.tsx, apps/screenpipe-app-tauri/components/rewind/current-frame-timeline.tsx, apps/screenpipe-app-tauri/components/rewind/hooks/use-frame-loading.ts, apps/screenpipe-app-tauri/components/rewind/hooks/use-live-text.ts, apps/screenpipe-app-tauri/components/rewind/timeline.tsx, apps/screenpipe-app-tauri/components/rewind/timeline/app-context-popover.tsx, apps/screenpipe-app-tauri/components/rewind/timeline/timeline-tag-toolbar.tsx, apps/screenpipe-app-tauri/components/rewind/timeline/timeline.tsx, apps/screenpipe-app-tauri/lib/hooks/use-audio-playback.tsx, apps/screenpipe-app-tauri/src-tauri/src/engine_events.rs, apps/screenpipe-app-tauri/src-tauri/src/engine_events/audio_device.rs
  Purpose and Scope
  macOS Subsystem Overview
  Screen Capture & OCR
    · CoreAudio Process Tap
    · Meeting Piggyback ("Smart Recording")
    · DRM & Content Protection
  Accessibility Tree Extraction
  UI Event Monitoring
  Live Text Integration (VisionKit)
    · Implementation Architecture
    · Key Components
  Application Lifecycle & UI
    · Window Management
    · Regression Checklist

## · Windows  (L9630)
  源文件: apps/screenpipe-app-tauri/lib/utils/clipboard-image.test.ts, apps/screenpipe-app-tauri/lib/utils/clipboard-image.ts, apps/screenpipe-app-tauri/src-tauri/src/native_notification.rs, apps/screenpipe-app-tauri/src-tauri/src/native_shortcut_reminder.rs, apps/screenpipe-app-tauri/src-tauri/src/tray_monitor_preview.rs, apps/screenpipe-app-tauri/src-tauri/src/window/content_process.rs, apps/screenpipe-app-tauri/src-tauri/src/window/gesture.rs, apps/screenpipe-app-tauri/src-tauri/src/window/mod.rs, apps/screenpipe-app-tauri/src-tauri/src/window/panel.rs, apps/screenpipe-app-tauri/src-tauri/src/window/show.rs, apps/screenpipe-app-tauri/src-tauri/src/windows_overlay.rs, apps/screenpipe-app-tauri/src-tauri/src/windows_webview_env.rs
  Screen Capture Backends
    · WGC (Windows Graphics Capture)
    · High-FPS Recording
  OCR Engine: Windows Native OCR
  Accessibility: UI Automation (UIA)
    · WindowsTreeWalker
  Windows Overlay System
    · Win32 Implementation
    · Shortcut Reminder
  DRM and Content Protection
  ONNX Runtime & Environment Setup
  Incognito Detection

## · Linux  (L9822)
  源文件: .github/scripts/assert_windows_audio_rms.ps1, .github/scripts/check_logs.sh, .github/scripts/install_dependencies.sh, .github/scripts/linux/bundle-appimage-runtime-deps.sh, .github/scripts/run_screenpipe.sh, .github/scripts/test_audio_capture.sh, .github/scripts/test_ocr.sh, .github/workflows/ci.yml, .github/workflows/e2e-test.yml, .github/workflows/linux-appimage-smoke.yml, .github/workflows/release-app.yml, .github/workflows/release-cli.yml
  Purpose and Scope
  System Dependencies Overview
    · Dependency Architecture
  Package Installation
    · Ubuntu/Debian Dependencies
  OCR: Tesseract Engine
    · OCR Pipeline Mapping
  Audio Capture and Acceleration
    · PulseAudio & PipeWire
    · OpenBLAS Acceleration
  AppImage Packaging and Portability
    · Runtime Dependency Bundling
    · Bun Sidecar
  Development Environments
    · DevContainer
    · Linux System Mapping
  Summary of Linux-Specific Code Entities

## · Glossary  (L10036)
  源文件: Cargo.lock, Cargo.toml, LICENSE.md, README.md, apps/screenpipe-app-tauri/components/pipe-install-dialog.tsx, apps/screenpipe-app-tauri/components/pipe-store.tsx, apps/screenpipe-app-tauri/components/post-install-connections-modal.tsx, apps/screenpipe-app-tauri/components/rewind/ai-presets-selector.tsx, apps/screenpipe-app-tauri/components/settings/ai-presets.tsx, apps/screenpipe-app-tauri/components/settings/general-settings.tsx, apps/screenpipe-app-tauri/components/settings/pipes-section.tsx, apps/screenpipe-app-tauri/components/settings/privacy-section.tsx
  Core System Concepts
    · 1. Pi Agent (Pi)
    · 2. Pipes
    · 3. ImmediateTx
    · 4. Accessibility Tree (a11y)
    · 5. AI Gateway
  Technical Mapping: Natural Language to Code
    · Diagram: AI Execution & Pipe Lifecycle
  Key Terms Table
  Data Flow & Architecture
    · Diagram: Search Data Flow
  Domain Concepts
    · Event-Driven Capture
    · Local-First Privacy
    · Connection Lifecycle
    · CoreAudio Process Tap