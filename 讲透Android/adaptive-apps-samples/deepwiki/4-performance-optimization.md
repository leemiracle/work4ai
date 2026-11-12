<!-- source: DeepWiki mcp.deepwiki.com · repo android/adaptive-apps-samples · page 4 Performance Optimization · fetched 2026-10-23 -->

# Performance Optimization

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AdaptiveJetStream/baseline-profiles.md](AdaptiveJetStream/baseline-profiles.md)
- [AdaptiveJetStream/benchmark/build.gradle.kts](AdaptiveJetStream/benchmark/build.gradle.kts)
- [AdaptiveJetStream/benchmark/src/main/java/com/google/jetstream/benchmark/BaselineProfileGenerator.kt](AdaptiveJetStream/benchmark/src/main/java/com/google/jetstream/benchmark/BaselineProfileGenerator.kt)

</details>



## Purpose and Scope

This document provides an overview of the performance optimization strategies implemented in AdaptiveJetStream, focusing on startup performance improvements and automated performance measurement. The optimization approach centers on baseline profile generation and comprehensive benchmarking infrastructure to ensure consistent application performance across different device types and form factors.

For detailed information about baseline profile implementation, see [Baseline Profiles](#4.1). For comprehensive benchmarking setup and procedures, see [Benchmarking](#4.2).

## Performance Optimization Overview

AdaptiveJetStream implements a multi-layered performance optimization strategy designed to minimize application startup time and improve runtime performance. The optimization framework consists of three primary components:

| Component | Purpose | Implementation |
|-----------|---------|----------------|
| Baseline Profiles | AOT compilation optimization | Profile-guided optimization for hot code paths |
| Macrobenchmarks | Performance measurement | Automated startup and navigation benchmarks |
| Managed Test Devices | Consistent testing | Virtual TV devices for reproducible performance tests |

The performance optimization system integrates directly with the build pipeline to automatically generate and validate performance improvements during development.

### Performance Optimization Architecture

```mermaid
graph TB
    subgraph "Main Application"
        APP["JetStreamApplication"]
        MAIN["MainActivity"]
        SERVICE["PlaybackService"]
    end
    
    subgraph "Benchmark Module"
        GENERATOR["BaselineProfileGenerator"]
        RULE["BaselineProfileRule"]
        TESTS["MacrobenchmarkTests"]
    end
    
    subgraph "Performance Artifacts"
        PROFILE["baseline-prof.txt"]
        REPORTS["Benchmark Reports"]
        METRICS["Performance Metrics"]
    end
    
    subgraph "Build System Integration"
        GRADLE["benchmark/build.gradle.kts"]
        DEVICE["ManagedVirtualDevice tvApi34"]
        PLUGIN["androidx.baselineprofile plugin"]
    end
    
    GENERATOR --> RULE
    RULE --> APP
    GENERATOR --> PROFILE
    TESTS --> REPORTS
    REPORTS --> METRICS
    
    GRADLE --> DEVICE
    GRADLE --> PLUGIN
    PLUGIN --> GENERATOR
    DEVICE --> TESTS
    
    PROFILE --> APP
    
    style GENERATOR fill:#e8f5e8
    style PROFILE fill:#fff3e0
    style DEVICE fill:#f3e5f5
```

Sources: [AdaptiveJetStream/benchmark/build.gradle.kts:1-83](), [AdaptiveJetStream/benchmark/src/main/java/com/google/jetstream/benchmark/BaselineProfileGenerator.kt:1-203]()

## Baseline Profile System

The baseline profile system captures runtime performance data during typical user interactions and generates optimization rules for AOT (Ahead-of-Time) compilation. This approach significantly improves application startup performance by pre-compiling frequently executed code paths.

### Baseline Profile Generation Process

```mermaid
graph LR
    subgraph "Profile Collection"
        START["startActivityAndWait()"]
        WAIT["device.waitForIdle()"]
        CAROUSEL["Wait for Carousel focus"]
    end
    
    subgraph "Navigation Simulation"
        HOME["Home tab exploration"]
        CATEGORIES["Categories tab navigation"]
        MOVIES["Movies tab exploration"]
        SHOWS["Shows tab exploration"]
        FAVOURITES["Favourites tab navigation"]
        SEARCH["Search tab exploration"]
    end
    
    subgraph "Screen Interactions"
        PROFILE_SCREEN["Account screen navigation"]
        CATEGORY_DETAILS["Category details exploration"]
        MOVIE_DETAILS["Movie details navigation"]
    end
    
    subgraph "Profile Output"
        BASELINE_PROF["baseline-prof.txt generation"]
    end
    
    START --> WAIT
    WAIT --> CAROUSEL
    CAROUSEL --> HOME
    HOME --> CATEGORIES
    CATEGORIES --> MOVIES
    MOVIES --> SHOWS
    SHOWS --> FAVOURITES
    FAVOURITES --> SEARCH
    SEARCH --> PROFILE_SCREEN
    PROFILE_SCREEN --> CATEGORY_DETAILS
    CATEGORY_DETAILS --> MOVIE_DETAILS
    MOVIE_DETAILS --> BASELINE_PROF
```

The `BaselineProfileGenerator` class orchestrates this process through the `startup()` method, which systematically navigates through all application screens using D-pad controls to simulate TV remote interactions.

Sources: [AdaptiveJetStream/benchmark/src/main/java/com/google/jetstream/benchmark/BaselineProfileGenerator.kt:30-186]()

### Profile Application Workflow

The baseline profile application follows a specific sequence to ensure optimal performance benefits:

```mermaid
graph TD
    subgraph "Installation Phase"
        INSTALL["App Installation"]
        LAUNCH["Initial Launch"]
    end
    
    subgraph "Compilation Phase"
        COMPILE["adb shell cmd package compile"]
        SPEED_PROFILE["speed-profile compilation"]
        BG_DEXOPT["Background optimization job"]
    end
    
    subgraph "Verification Phase"
        STATUS_CHECK["dumpsys package dexopt"]
        PROFILE_APPLIED["Profile status verification"]
    end
    
    subgraph "Performance Phase"
        FORCE_STOP["Force stop application"]
        OPTIMIZED_LAUNCH["Optimized restart"]
        PERFORMANCE_GAIN["Startup improvement"]
    end
    
    INSTALL --> LAUNCH
    LAUNCH --> COMPILE
    COMPILE --> SPEED_PROFILE
    SPEED_PROFILE --> STATUS_CHECK
    STATUS_CHECK --> BG_DEXOPT
    BG_DEXOPT --> PROFILE_APPLIED
    PROFILE_APPLIED --> FORCE_STOP
    FORCE_STOP --> OPTIMIZED_LAUNCH
    OPTIMIZED_LAUNCH --> PERFORMANCE_GAIN
```

Sources: [AdaptiveJetStream/baseline-profiles.md:23-69]()

## Benchmarking Infrastructure

The benchmarking infrastructure provides automated performance measurement capabilities through the dedicated `benchmark` module. This module is configured as an Android Test module with specific optimizations for TV device testing.

### Benchmark Module Configuration

The benchmark module configuration includes several key components:

| Configuration | Value | Purpose |
|---------------|-------|---------|
| `targetProjectPath` | `:jetstream` | Links benchmark module to main app |
| `managedDevices` | `tvApi34` | Virtual TV device for testing |
| `suppressErrors` | `EMULATOR` | Allows benchmarking on virtual devices |
| `baselineProfile.useConnectedDevices` | `false` | Forces use of managed virtual devices |

### Managed Virtual Device Setup

```mermaid
graph LR
    subgraph "Device Configuration"
        DEVICE_DEF["Television (1080p)"]
        API_LEVEL["API Level 34"]
        SYSTEM_IMAGE["AOSP system image"]
    end
    
    subgraph "Benchmark Module"
        BUILD_GRADLE["benchmark/build.gradle.kts"]
        DEVICE_CONFIG["ManagedVirtualDevice tvApi34"]
        BASELINE_CONFIG["baselineProfile configuration"]
    end
    
    subgraph "Test Execution"
        GENERATOR["BaselineProfileGenerator"]
        UI_AUTOMATOR["UiAutomator interactions"]
        PROFILE_COLLECTION["Profile data collection"]
    end
    
    DEVICE_DEF --> DEVICE_CONFIG
    API_LEVEL --> DEVICE_CONFIG
    SYSTEM_IMAGE --> DEVICE_CONFIG
    
    BUILD_GRADLE --> DEVICE_CONFIG
    DEVICE_CONFIG --> BASELINE_CONFIG
    
    BASELINE_CONFIG --> GENERATOR
    GENERATOR --> UI_AUTOMATOR
    UI_AUTOMATOR --> PROFILE_COLLECTION
```

Sources: [AdaptiveJetStream/benchmark/build.gradle.kts:48-62]()

## Performance Measurement Workflow

The performance measurement workflow integrates baseline profile generation with the application build process, ensuring that performance optimizations are automatically validated and applied.

### Build System Integration

The benchmark module integrates with the main application through several Gradle plugins and configurations:

- `androidx.baselineprofile` plugin manages profile generation and application
- `android.test` plugin provides the testing framework
- `compose.compiler` plugin ensures Compose-specific optimizations
- Target project path configuration links the benchmark to the main `jetstream` module

### UI Automation Strategy

The baseline profile generation uses `UiAutomator` to simulate realistic user interactions:

| Interaction Pattern | Implementation | Purpose |
|-------------------|---------------|---------|
| D-pad navigation | `pressDPadRight()`, `pressDPadLeft()` | TV remote simulation |
| Focus verification | `Until.findObject().focused(true)` | Ensures UI element accessibility |
| Content exploration | Systematic tab navigation | Comprehensive code path coverage |
| Screen transitions | `pressDPadCenter()` for selection | Deep navigation patterns |

Sources: [AdaptiveJetStream/benchmark/src/main/java/com/google/jetstream/benchmark/BaselineProfileGenerator.kt:36-185]()

### Performance Optimization Dependencies

The performance optimization system relies on several key dependencies managed through the version catalog:

```mermaid
graph TB
    subgraph "Core Dependencies"
        MACRO["androidx.benchmark.macro.junit4"]
        BASELINE["androidx.baselineprofile plugin"]
        UI_AUTOMATOR["androidx.uiautomator"]
    end
    
    subgraph "Test Framework"
        JUNIT["androidx.junit"]
        RULES["androidx.rules"]
        COMPOSE_RUNTIME["androidx.compose.runtime"]
    end
    
    subgraph "Build Configuration"
        ANDROID_TEST["android.test plugin"]
        KOTLIN_ANDROID["kotlin.android plugin"]
        COMPOSE_COMPILER["compose.compiler plugin"]
    end
    
    BASELINE --> MACRO
    MACRO --> UI_AUTOMATOR
    UI_AUTOMATOR --> JUNIT
    JUNIT --> RULES
    RULES --> COMPOSE_RUNTIME
    
    ANDROID_TEST --> BASELINE
    KOTLIN_ANDROID --> COMPOSE_COMPILER
```

Sources: [AdaptiveJetStream/benchmark/build.gradle.kts:19-76]()

The performance optimization framework ensures that AdaptiveJetStream maintains optimal startup and runtime performance across different device configurations while providing automated validation of performance improvements through the development lifecycle.

---

