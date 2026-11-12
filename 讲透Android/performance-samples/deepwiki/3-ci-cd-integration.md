<!-- source: DeepWiki mcp.deepwiki.com · repo android/performance-samples · page 3 CI/CD Integration · fetched 2026-10-23 -->

# CI/CD Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/ci-gradle.properties](.github/ci-gradle.properties)
- [.github/workflows/copy-branch.yml](.github/workflows/copy-branch.yml)
- [.github/workflows/firebase_test_lab.yml](.github/workflows/firebase_test_lab.yml)
- [.github/workflows/generate-bp.yml](.github/workflows/generate-bp.yml)
- [.github/workflows/macrobenchmark.yml](.github/workflows/macrobenchmark.yml)

</details>



This document covers the comprehensive CI/CD pipeline that automates performance testing and baseline profile generation for the Android Performance Samples repository. The pipeline integrates GitHub Actions, Firebase Test Lab, and Google Cloud services to provide continuous performance monitoring and regression detection.

For detailed information about individual GitHub Actions workflows, see [GitHub Actions Workflows](#3.1). For Firebase Cloud Functions that process benchmark results, see [Firebase Cloud Functions](#3.2).

## CI/CD Architecture Overview

The CI/CD system implements a multi-stage pipeline that builds applications, runs performance tests on real devices, and monitors results for regressions. The architecture consists of GitHub Actions workflows that trigger based on code changes, execute tests on Firebase Test Lab, and integrate with Google Cloud services for result processing.

**CI/CD Pipeline Architecture**
```mermaid
graph TD
    subgraph "GitHub Actions Triggers"
        PUSH["Push to main/macrobenchmark"]
        PR["Pull Request to main"]
        MANUAL["workflow_dispatch"]
    end
    
    subgraph "Change Detection"
        CHANGES["changes job"]
        FILTER["dorny/paths-filter@v3"]
        OUTPUT["macrobenchmark output"]
    end
    
    subgraph "Build Stage"
        SETUP["Setup JDK 17"]
        GRADLE["gradle-command-action@v3"]
        ASSEMBLE[":app:assembleBenchmark<br/>:macrobenchmark:assembleBenchmark"]
    end
    
    subgraph "Test Execution"
        FTL["Firebase Test Lab"]
        GCLOUD["gcloud beta firebase test android run"]
        DEVICES["model=lynx,version=33"]
    end
    
    subgraph "Results Processing"
        GCS["gs://macrobenchmark-results"]
        PULL["/sdcard/Download"]
        MONITOR["Cloud Monitoring"]
    end
    
    PUSH --> CHANGES
    PR --> CHANGES
    MANUAL --> CHANGES
    
    CHANGES --> FILTER
    FILTER --> OUTPUT
    OUTPUT --> SETUP
    
    SETUP --> GRADLE
    GRADLE --> ASSEMBLE
    ASSEMBLE --> FTL
    
    FTL --> GCLOUD
    GCLOUD --> DEVICES
    DEVICES --> GCS
    DEVICES --> PULL
    
    GCS --> MONITOR
```

Sources: [.github/workflows/firebase_test_lab.yml:1-100](), [.github/workflows/generate-bp.yml:1-82](), [.github/workflows/macrobenchmark.yml:1-65]()

## GitHub Actions Workflows

The repository implements three primary GitHub Actions workflows that handle different aspects of the CI/CD pipeline:

| Workflow File | Purpose | Triggers | Runner |
|---------------|---------|----------|---------|
| `firebase_test_lab.yml` | Execute macrobenchmarks on Firebase Test Lab | Push to main/macrobenchmark, PR to main | ubuntu-latest |
| `generate-bp.yml` | Generate baseline profiles using managed devices | Push to main only | macos-latest |
| `macrobenchmark.yml` | Build macrobenchmark APKs for validation | Push, PR, manual dispatch | macos-latest |

### Conditional Execution System

All workflows implement a two-job architecture with conditional execution based on file changes:

**Conditional Execution Flow**
```mermaid
sequenceDiagram
    participant T as "GitHub Trigger"
    participant C as "changes job"
    participant F as "dorny/paths-filter@v3"
    participant B as "build job"
    
    T->>C: "Workflow triggered"
    C->>F: "Check MacrobenchmarkSample/**"
    F->>C: "Set macrobenchmark output"
    C->>B: "Pass needs.changes.outputs.macrobenchmark"
    
    alt macrobenchmark == 'true'
        B->>B: "Execute build steps"
    else macrobenchmark == 'false'
        B->>B: "Skip job execution"
    end
```

The `changes` job uses `dorny/paths-filter@v3` to detect changes in the `MacrobenchmarkSample/**` directory path [.github/workflows/firebase_test_lab.yml:27-32](). This prevents unnecessary builds when changes occur outside the macrobenchmark sample.

Sources: [.github/workflows/firebase_test_lab.yml:16-32](), [.github/workflows/generate-bp.yml:20-34](), [.github/workflows/macrobenchmark.yml:15-29]()

### Firebase Test Lab Integration

The `firebase_test_lab.yml` workflow executes two distinct test suites on Firebase Test Lab using `gcloud beta firebase test android run`:

**Firebase Test Lab Execution**
```mermaid
graph LR
    subgraph "APK Build"
        APP["app-benchmarkRelease.apk"]
        TEST["macrobenchmark-benchmarkRelease.apk"]
    end
    
    subgraph "Macrobenchmark Tests"
        MACRO_ENV["androidx.benchmark.enabledRules=Macrobenchmark"]
        MACRO_SHARDS["num-uniform-shards 6"]
        MACRO_TIMEOUT["timeout 30m"]
    end
    
    subgraph "Baseline Profile Generation"
        BP_ENV["androidx.benchmark.enabledRules=BaselineProfile"]
        BP_SHARDS["num-uniform-shards 2"]
        BP_TIMEOUT["timeout 30m"]
    end
    
    subgraph "Device Configuration"
        DEVICE["model=lynx,version=33,locale=en,orientation=portrait"]
        RESULTS["gs://macrobenchmark-results"]
        PULL["/sdcard/Download"]
    end
    
    APP --> MACRO_ENV
    TEST --> MACRO_ENV
    MACRO_ENV --> DEVICE
    
    APP --> BP_ENV
    TEST --> BP_ENV
    BP_ENV --> DEVICE
    
    DEVICE --> RESULTS
    DEVICE --> PULL
```

The workflow executes tests on Pixel 7 devices (`model=lynx`) running Android 13 (`version=33`) with specific environment variables that control benchmark execution [.github/workflows/firebase_test_lab.yml:77-86]().

Sources: [.github/workflows/firebase_test_lab.yml:75-99]()

### Baseline Profile Generation

The `generate-bp.yml` workflow generates baseline profiles using Android Gradle Managed Devices on macOS runners. This workflow uses different Gradle parameters to optimize for baseline profile generation:

**Baseline Profile Generation Process**
```mermaid
graph TD
    subgraph "Environment Setup"
        MACOS["macos-latest runner"]
        JDK["Setup JDK 17"]
        GRADLE_PROPS["Copy CI gradle.properties"]
    end
    
    subgraph "Device Management"
        CLEAN["./gradlew cleanManagedDevices --unused-only"]
        GMD["Gradle Managed Devices"]
        GPU["swiftshader_indirect"]
    end
    
    subgraph "Build Configuration"
        RELEASE["assembleRelease"]
        BP_RULES["-Pandroid.testInstrumentationRunnerArguments.androidx.benchmark.enabledRules=BaselineProfile"]
        SHARDS["-Pandroid.experimental.androidTest.numManagedDeviceShards=1"]
    end
    
    subgraph "Artifact Output"
        APK["Production App APK"]
        UPLOAD["actions/upload-artifact@v4"]
    end
    
    MACOS --> JDK
    JDK --> GRADLE_PROPS
    GRADLE_PROPS --> CLEAN
    CLEAN --> GMD
    GMD --> GPU
    
    GPU --> RELEASE
    RELEASE --> BP_RULES
    BP_RULES --> SHARDS
    SHARDS --> APK
    APK --> UPLOAD
```

The workflow uses managed devices with specific GPU configuration (`swiftshader_indirect`) and single-shard execution to optimize baseline profile generation performance [.github/workflows/generate-bp.yml:69-75]().

Sources: [.github/workflows/generate-bp.yml:36-81]()

## CI Configuration Management

The CI system uses a dedicated Gradle properties file to optimize build performance in continuous integration environments:

**CI Gradle Configuration**
```mermaid
graph LR
    subgraph "CI Optimizations"
        DAEMON["org.gradle.daemon=false"]
        PARALLEL["org.gradle.parallel=true"]
        WORKERS["org.gradle.workers.max=2"]
    end
    
    subgraph "Kotlin Configuration"
        INCREMENTAL["kotlin.incremental=false"]
        STRATEGY["kotlin.compiler.execution.strategy=in-process"]
    end
    
    subgraph "Error Handling"
        WARNINGS["warningsAsErrors=false"]
    end
    
    DAEMON --> PARALLEL
    PARALLEL --> WORKERS
    WORKERS --> INCREMENTAL
    INCREMENTAL --> STRATEGY
    STRATEGY --> WARNINGS
```

The configuration disables Gradle daemon for CI environments, enables parallel execution with limited workers, and configures Kotlin compilation for optimal CI performance [.github/ci-gradle.properties:17-27]().

Sources: [.github/ci-gradle.properties:1-28]()

## Performance Monitoring Integration

The CI/CD pipeline integrates with Google Cloud services to provide automated performance regression detection. Firebase Test Lab results are stored in `gs://macrobenchmark-results` bucket, which triggers Cloud Functions for processing and metric extraction.

The monitoring system processes benchmark JSON files, extracts performance metrics, and uploads custom metrics to Google Cloud Monitoring for dashboard visualization and alerting on performance regressions.

Sources: [.github/workflows/firebase_test_lab.yml:83-84]()

---

