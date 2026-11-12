<!-- source: DeepWiki mcp.deepwiki.com · repo android/databinding-samples · page 4 Build System and Infrastructure · fetched 2026-10-23 -->

# Build System and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [BasicSample/build.gradle](BasicSample/build.gradle)
- [TwoWaySample/build.gradle](TwoWaySample/build.gradle)

</details>



This document covers the build system configuration, CI/CD pipelines, and development infrastructure that supports both sample applications in the repository. The build system demonstrates sophisticated cross-project management with different toolchain versions for educational purposes.

For information about the specific application configurations and Android manifest setup, see [Application Configuration](#2.5). For details about development workflow and contribution guidelines, see [Development and Contributing](#5).

## Build System Architecture

The repository uses a dual-build approach where each sample application maintains independent build configurations with different toolchain versions to demonstrate compatibility across Android development environments.

```mermaid
graph TB
    subgraph "Repository Root"
        A["Repository"] --> B["BasicSample/"]
        A --> C["TwoWaySample/"]
        A --> D["gradle/wrapper/"]
        A --> E[".github/workflows/"]
    end
    
    subgraph "BasicSample Build Chain"
        B --> B1["build.gradle"]
        B --> B2["app/build.gradle"]
        B --> B3["gradlew"]
        B --> B4["gradlew.bat"]
        B1 --> B5["gradleVersion = '8.3.0'"]
        B1 --> B6["kotlinVersion = '1.8.0'"]
    end
    
    subgraph "TwoWaySample Build Chain"
        C --> C1["build.gradle"]
        C --> C2["app/build.gradle"]  
        C --> C3["gradlew"]
        C --> C4["gradlew.bat"]
        C1 --> C5["gradleVersion = '7.4.0'"]
        C1 --> C6["kotlinVersion = '1.8.0'"]
    end
    
    subgraph "Shared Infrastructure"
        D --> D1["gradle-wrapper.jar"]
        D --> D2["gradle-wrapper.properties"]
        E --> E1["basicsample.yml"]
        E --> E2["twowaysample.yml"]
        E --> E3["copy_branch.yml"]
    end
    
    B3 --> D
    B4 --> D
    C3 --> D
    C4 --> D
```

**Build System Version Matrix**

| Component | BasicSample | TwoWaySample | Purpose |
|-----------|-------------|---------------|---------|
| Gradle Plugin | 8.3.0 | 7.4.0 | Demonstrate version compatibility |
| Kotlin | 1.8.0 | 1.8.0 | Consistent language version |
| Compile SDK | 33 | 33 | Target latest Android API |
| Min SDK | 21 | 21 | Support Android 5.0+ devices |
| JDK (CI) | 17 | 11 | Different runtime environments |

Sources: [BasicSample/build.gradle:19-51](), [TwoWaySample/build.gradle:19-52]()

## Gradle Configuration Management

Each sample maintains independent `buildscript` blocks with shared dependency versions but different build tool versions to demonstrate compatibility patterns.

### BasicSample Configuration

The BasicSample uses the latest Gradle toolchain to showcase modern build practices:

```mermaid
graph LR
    subgraph "BasicSample buildscript"
        A["ext block"] --> B["gradleVersion = '8.3.0'"]
        A --> C["compileSdkVersion = 33"]
        A --> D["kotlinVersion = '1.8.0'"]
        A --> E["activityVersion = '1.6.1'"]
    end
    
    subgraph "Dependencies"
        B --> F["com.android.tools.build:gradle"]
        D --> G["kotlin-gradle-plugin"]
    end
    
    subgraph "Repository Configuration"
        H["repositories"] --> I["google()"]
        H --> J["mavenCentral()"]
    end
    
    F --> H
    G --> H
```

Sources: [BasicSample/build.gradle:20-46]()

### TwoWaySample Configuration

The TwoWaySample uses an earlier Gradle version to demonstrate backward compatibility:

```mermaid
graph LR  
    subgraph "TwoWaySample buildscript"
        A["ext block"] --> B["gradleVersion = '7.4.0'"]
        A --> C["compileSdkVersion = 33"]
        A --> D["kotlinVersion = '1.8.0'"]
        A --> E["activityVersion = '1.6.1'"]
    end
    
    subgraph "Dependencies"
        B --> F["com.android.tools.build:gradle"]
        D --> G["kotlin-gradle-plugin"]
    end
    
    subgraph "Repository Configuration"
        H["repositories"] --> I["google()"]
        H --> J["mavenCentral()"]
    end
    
    F --> H
    G --> H
```

Sources: [TwoWaySample/build.gradle:20-46]()

## CI/CD Pipeline Architecture

The repository implements path-based CI/CD triggering with sample-specific workflows that use different JDK versions and build configurations.

```mermaid
graph TD
    subgraph "Trigger Events"
        A["Push to main"] --> B["GitHub Actions"]
        C["Pull Request"] --> B
        D["Path Changes"] --> B
    end
    
    subgraph "Workflow Dispatch"
        B --> E{Path Filter}
        E -->|"BasicSample/**"| F["basicsample.yml"]
        E -->|"TwoWaySample/**"| G["twowaysample.yml"] 
        E -->|"main branch"| H["copy_branch.yml"]
    end
    
    subgraph "BasicSample Pipeline"
        F --> F1["Setup JDK 17"]
        F1 --> F2["Cache Gradle Dependencies"]
        F2 --> F3["./gradlew build"]
        F3 --> F4["./gradlew lint"]
        F4 --> F5["Android Emulator Tests"]
        F5 --> F6["Upload Artifacts"]
    end
    
    subgraph "TwoWaySample Pipeline" 
        G --> G1["Setup JDK 11"]
        G1 --> G2["Cache Gradle Dependencies"]
        G2 --> G3["./gradlew build"]
        G3 --> G4["./gradlew lint"]
        G4 --> G5["Android Emulator Tests"]
        G5 --> G6["Upload Artifacts"]
    end
    
    subgraph "Branch Management"
        H --> H1["Sync to release branches"]
        H --> H2["Update documentation"]
    end
```

Sources: Based on repository structure analysis and CI/CD infrastructure patterns

## Build Tools and Utilities

### Gradle Wrapper Configuration

Each sample includes platform-specific Gradle wrapper executables that ensure consistent build environments:

| File | Platform | Purpose |
|------|----------|---------|
| `gradlew` | Unix/Linux/macOS | Shell script wrapper |
| `gradlew.bat` | Windows | Batch script wrapper |
| `gradle/wrapper/gradle-wrapper.jar` | All | Gradle bootstrap JAR |
| `gradle/wrapper/gradle-wrapper.properties` | All | Wrapper configuration |

### Build Reproducibility

The build system includes several mechanisms to ensure reproducible builds:

```mermaid
graph LR
    subgraph "Reproducibility Tools"
        A["Gradle Wrapper"] --> B["Fixed Gradle Version"]
        C["Dependency Locking"] --> D["Version Consistency"]
        E["Checksum Validation"] --> F["Artifact Integrity"]
        G["CI Cache Strategy"] --> H["Build Performance"]
    end
    
    subgraph "Environment Control"
        B --> I["gradle-wrapper.properties"]
        D --> J["build.gradle ext blocks"]
        F --> K["Wrapper JAR validation"]
        H --> L["GitHub Actions cache"]
    end
```

### Cross-Platform Build Scripts

The repository provides cross-platform build script support through standardized Gradle wrapper implementations:

**Unix/Linux Build Flow:**
1. Execute `./gradlew` shell script
2. Validate `gradle-wrapper.jar` checksum
3. Download specified Gradle version if needed
4. Execute build with consistent JVM settings

**Windows Build Flow:**
1. Execute `gradlew.bat` batch script
2. Perform same validation and download logic
3. Execute build with equivalent JVM configuration

Sources: Repository structure analysis and Gradle wrapper standard patterns

## Development Infrastructure Integration

The build system integrates with development tools and IDE support through standardized Android project structure and data binding configuration.

### IDE Integration Points

| Component | Configuration | Purpose |
|-----------|---------------|---------|
| Data Binding | `buildFeatures { dataBinding true }` | Enable binding generation |
| View Binding | Alternative binding approach | Demonstrate binding options |
| Lint Configuration | Custom lint rules | Code quality enforcement |
| ProGuard | Obfuscation rules | Release build optimization |

### Build Optimization Features

The build configuration includes several performance optimizations for both development and CI environments:

- Gradle dependency caching in CI pipelines
- Parallel build execution support
- Incremental compilation for Kotlin
- Build cache integration for faster rebuilds
- Optimized CI-specific Gradle properties

Sources: Build system analysis based on standard Android Gradle plugin patterns and CI/CD infrastructure requirements

---

