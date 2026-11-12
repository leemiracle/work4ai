<!-- source: DeepWiki mcp.deepwiki.com · repo android/user-interface-samples · page 6 Development Infrastructure · fetched 2026-10-23 -->

# Development Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/scripts/checksum.sh](.github/scripts/checksum.sh)
- [.github/scripts/gradlew_recursive.sh](.github/scripts/gradlew_recursive.sh)
- [.github/workflows/android.yml](.github/workflows/android.yml)

</details>



This page documents the development infrastructure used across the Android User Interface Samples repository. It covers the continuous integration (CI) setup, build scripts, and other development tools that support the various UI samples. 

## Overview

The Android User Interface Samples repository uses GitHub Actions for continuous integration to ensure code quality and build reliability. The infrastructure consists of:

1. GitHub Actions workflows for automated builds
2. Custom build scripts for optimized building across multiple sample modules
3. Caching mechanisms to improve build performance

```mermaid
flowchart TD
    A["GitHub Repository"] --> B["GitHub Actions"]
    B --> C["CI Workflow"]
    C --> D["Build Scripts"]
    D --> E["Gradle Build System"]
    D --> F["Caching Mechanism"]
    E --> G["Build Artifacts"]
    G --> H["APKs/AABs/AARs"]
```

Sources: [.github/workflows/android.yml]()

## CI Setup with GitHub Actions

The continuous integration system is implemented using GitHub Actions, which automatically builds the project when code is pushed to the main branch or when pull requests are created.

### Workflow Configuration

The CI workflow is defined in the `android.yml` file and consists of several steps:

1. Checkout code from the repository
2. Set up JDK 17 with Zulu distribution
3. Generate a cache key for Gradle dependencies
4. Cache Gradle modules for faster builds
5. Build all projects recursively
6. Package and upload build artifacts

```mermaid
sequenceDiagram
    participant D as "Developer"
    participant G as "GitHub"
    participant A as "GitHub Actions"
    participant B as "Build Scripts"
    
    D->>G: Push to main branch
    D->>G: Create pull request
    G->>A: Trigger workflow
    A->>A: Setup JDK 17
    A->>B: Generate cache key
    Note over A,B: checksum.sh
    A->>A: Restore cached dependencies
    A->>B: Execute build
    Note over A,B: gradlew_recursive.sh
    B->>A: Return build results
    A->>A: Zip artifacts
    A->>G: Upload artifacts
```

Sources: [.github/workflows/android.yml:15-59]()

### Workflow Trigger Configuration

The CI workflow is configured to run automatically on specific repository events:

```mermaid
flowchart LR
    A["GitHub Events"] --> B["push to main branch"]
    A --> C["any pull request"]
    B --> D["Trigger CI Workflow"]
    C --> D
```

Sources: [.github/workflows/android.yml:17-22]()

## Build Scripts

The repository uses custom bash scripts to optimize the build process across multiple sample modules.

### Recursive Gradle Build Script

The `gradlew_recursive.sh` script finds all Gradle wrapper instances within the repository and executes the specified Gradle task on each one. This is particularly useful in a monorepo structure with multiple independent sample projects.

```mermaid
flowchart TD
    A["gradlew_recursive.sh"] --> B["Set Gradle Optimizations"]
    A --> C["Find all gradlew files"]
    C --> D["For each gradlew"]
    D --> E["Execute gradle task"]
    E --> F["Next gradlew or exit"]
```

The script configures Gradle with optimized settings for CI environments:

| Setting | Value | Purpose |
|---------|-------|---------|
| Max Memory | 5120m | Increases memory allocation for builds |
| Heap Dump | Enabled | Helps diagnose out-of-memory errors |
| Gradle Daemon | Disabled | Prevents daemon overhead in CI |
| Parallel Execution | Enabled | Speeds up build by using multiple cores |
| Kotlin Compiler Strategy | in-process | Optimizes Kotlin compilation |

Sources: [.github/scripts/gradlew_recursive.sh:19-26](), [.github/scripts/gradlew_recursive.sh:30-35]()

### Checksum Generation for Caching

The `checksum.sh` script generates a deterministic checksum based on all Gradle build files in the repository. This checksum is used as a cache key for GitHub Actions to efficiently cache dependencies between workflow runs.

```mermaid
flowchart TD
    A["checksum.sh"] --> B["Initialize result file"]
    A --> C["Find Gradle files"]
    C --> D["Calculate MD5 hashes"]
    D --> E["Append to result file"]
    E --> F["Sort result file"]
```

The script targets these file types for checksum generation:
- `*.gradle` files (Gradle build scripts)
- `*.gradle.kts` files (Kotlin DSL build scripts)
- `gradle-wrapper.properties` files (Gradle Wrapper configuration)

Sources: [.github/scripts/checksum.sh:24-38]()

## Cache Management System

The CI workflow implements an intelligent cache management system to speed up builds by reusing previously downloaded dependencies.

```mermaid
flowchart TD
    A["CI Workflow"] --> B["Generate Cache Key"]
    B --> C["checksum.sh"]
    C --> D["MD5 hash of all build files"]
    D --> E["Look up cache"]
    E --> F{Cache hit?}
    F -->|Yes| G["Restore cached dependencies"]
    F -->|No| H["Download dependencies"]
    G --> I["Run build"]
    H --> I
    I --> J["Save new cache"]
```

The cache system is configured to store:
- Gradle module cache (`~/.gradle/caches/modules-*`)
- Gradle JAR cache (`~/.gradle/caches/jars-*`)
- Gradle build cache (`~/.gradle/caches/build-cache-*`)

Sources: [.github/workflows/android.yml:37-48]()

## CI Workflow Detail

The complete CI workflow can be visualized as follows:

```mermaid
flowchart TD
    A["GitHub Event"] --> B["Start CI Workflow"]
    B --> C["actions/checkout@v4"]
    C --> D["Setup JDK 17 with actions/setup-java@v4"]
    D --> E["Generate cache key with checksum.sh"]
    E --> F["Setup cache with actions/cache@v4"]
    F --> G["Run gradlew_recursive.sh assembleDebug"]
    G --> H["Zip artifacts"]
    H --> I["Upload artifacts with actions/upload-artifact@v4"]
    I --> J["Complete Workflow"]
```

Sources: [.github/workflows/android.yml:28-59]()

## Relationship to Sample Projects

The development infrastructure is designed to work with the various UI sample projects in the repository. Each sample project has its own Gradle build system, but they all share the common CI infrastructure.

```mermaid
flowchart TD
    subgraph "Development Infrastructure"
        A["GitHub Actions CI"]
        B["Build Scripts"]
        C["Cache System"]
    end
    
    subgraph "Sample Projects"
        D["Window Management Samples"]
        E["Canonical UI Layout Samples"]
        F["App Widget Samples"]
        G["Other UI Feature Samples"]
    end
    
    A --> B
    B --> D
    B --> E
    B --> F
    B --> G
    C --> B
```

Sources: [.github/scripts/gradlew_recursive.sh:30-35]()

## Conclusion

The development infrastructure in the Android User Interface Samples repository provides a robust foundation for building and testing UI samples. The GitHub Actions workflow, combined with custom build scripts and caching mechanisms, ensures that all sample projects can be built efficiently in an automated fashion.

For details about the continuous integration setup specifically, see [CI Setup](#6.1).

---

