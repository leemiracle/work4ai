<!-- source: DeepWiki mcp.deepwiki.com · repo android/codelab-gemini-summary · page 2 Project Setup and Configuration · fetched 2026-10-23 -->

# Project Setup and Configuration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/build.gradle.kts](app/build.gradle.kts)
- [settings.gradle.kts](settings.gradle.kts)

</details>



This page covers the essential build system configuration, project structure, and setup requirements for the JetNews Android application. It focuses on the Gradle build system, dependency management, and core project configuration files that enable the application to build and run successfully.

For detailed information about the Gradle build system internals, see [Gradle Build System](#2.1). For version control configuration, see [Version Control Configuration](#2.2). For information about contributing to the project, see [Contributing Guidelines](#5.1).

## Project Structure Overview

The JetNews project follows a standard Android application structure with Gradle-based build configuration. The project uses Kotlin DSL for build scripts and integrates modern Android development tools.

### Project Structure Diagram

```mermaid
graph TB
    subgraph "JetNews_Project" ["JetNews Android Project"]
        SG["settings.gradle.kts"]
        subgraph "app_module" ["app/ (Android Application Module)"]
            ABG["build.gradle.kts"]
            AG["gradle.properties"]
            PR["proguard-rules.pro"]
            subgraph "src_structure" ["src/ (Source Code)"]
                MAIN["main/"]
                TEST["test/"]
                ATEST["androidTest/"]
                SHARED["sharedTest/"]
            end
        end
        subgraph "gradle_wrapper" ["gradle/ (Build System)"]
            GW["wrapper/"]
        end
    end
    
    SG --> ABG
    ABG --> MAIN
    ABG --> TEST
    ABG --> ATEST
    ABG --> SHARED
```

**Sources:** [settings.gradle.kts:1-40](), [app/build.gradle.kts:1-161]()

## Core Configuration Files

### settings.gradle.kts Configuration

The project-level settings file defines the basic project structure and repository configuration:

| Configuration Aspect | Value | Purpose |
|----------------------|-------|---------|
| Project Name | `"JetNews"` | Root project identifier |
| Included Modules | `":app"` | Single application module |
| Repository Mode | `FAIL_ON_PROJECT_REPOS` | Enforces centralized dependency resolution |

The settings file also includes support for Compose snapshot builds through the `COMPOSE_SNAPSHOT_ID` environment variable, enabling testing with bleeding-edge Compose versions.

**Sources:** [settings.gradle.kts:16-40]()

### app/build.gradle.kts Configuration

The application module build file contains the core Android application configuration:

```mermaid
graph TD
    subgraph "build_gradle_kts" ["app/build.gradle.kts Structure"]
        PLUGINS["plugins block"]
        ANDROID["android block"]
        COMPOSE["composeCompiler block"]
        DEPS["dependencies block"]
        TASKS["tasks configuration"]
        
        subgraph "android_config" ["Android Configuration"]
            COMPILE["compileSdk"]
            NAMESPACE["namespace"]
            DEFAULT["defaultConfig"]
            SIGNING["signingConfigs"]
            BUILD["buildTypes"]
            TEST["testOptions"]
            SOURCE["sourceSets"]
            COMPILE_OPT["compileOptions"]
            FEATURES["buildFeatures"]
            PACKAGING["packaging"]
        end
        
        subgraph "plugin_config" ["Plugin Configuration"]
            ANDROID_APP["android.application"]
            KOTLIN["kotlin.android"]
            COMPOSE_PLUGIN["compose"]
            SECRETS["secrets"]
        end
    end
    
    PLUGINS --> ANDROID_APP
    PLUGINS --> KOTLIN
    PLUGINS --> COMPOSE_PLUGIN
    PLUGINS --> SECRETS
    
    ANDROID --> COMPILE
    ANDROID --> NAMESPACE
    ANDROID --> DEFAULT
    ANDROID --> SIGNING
    ANDROID --> BUILD
    ANDROID --> TEST
    ANDROID --> SOURCE
    ANDROID --> COMPILE_OPT
    ANDROID --> FEATURES
    ANDROID --> PACKAGING
```

**Sources:** [app/build.gradle.kts:17-98]()

## Build System Architecture

### Plugin Configuration

The application uses four key Gradle plugins configured through version catalogs:

```mermaid
graph LR
    subgraph "gradle_plugins" ["Gradle Plugins"]
        APP["android.application"]
        KOTLIN["kotlin.android"]
        COMPOSE["compose"]
        SECRETS["secrets"]
    end
    
    subgraph "capabilities" ["Plugin Capabilities"]
        APP_CAP["Android App Build"]
        KOTLIN_CAP["Kotlin Compilation"]
        COMPOSE_CAP["Compose Compiler"]
        SECRETS_CAP["API Key Management"]
    end
    
    APP --> APP_CAP
    KOTLIN --> KOTLIN_CAP
    COMPOSE --> COMPOSE_CAP
    SECRETS --> SECRETS_CAP
```

**Sources:** [app/build.gradle.kts:17-22]()

### Android Configuration Details

| Configuration | Value | Description |
|---------------|-------|-------------|
| `compileSdk` | From version catalog | Target Android API level |
| `namespace` | `"com.example.jetnews"` | Application package namespace |
| `applicationId` | `"com.example.jetnews"` | Unique application identifier |
| `minSdk` | From version catalog | Minimum supported Android version |
| `targetSdk` | From version catalog | Target Android version |
| `versionCode` | `1` | Internal version number |
| `versionName` | `"1.0"` | User-facing version string |

**Sources:** [app/build.gradle.kts:24-36]()

### Build Types and Signing

The project defines two build types with different optimization settings:

```mermaid
graph TB
    subgraph "build_types" ["Build Types"]
        DEBUG["debug"]
        RELEASE["release"]
    end
    
    subgraph "signing_config" ["Signing Configuration"]
        DEBUG_KEY["Debug Keystore"]
        RELEASE_KEY["Release Keystore"]
        ENV_VARS["Environment Variables"]
    end
    
    subgraph "optimization" ["Build Optimization"]
        NO_MINIFY["No Minification"]
        MINIFY["ProGuard Minification"]
        PROGUARD["proguard-rules.pro"]
    end
    
    DEBUG --> DEBUG_KEY
    DEBUG --> NO_MINIFY
    
    RELEASE --> RELEASE_KEY
    RELEASE --> MINIFY
    RELEASE --> ENV_VARS
    
    MINIFY --> PROGUARD
```

**Sources:** [app/build.gradle.kts:38-62]()

## Dependency Management

### Dependency Categories

The project organizes dependencies into distinct categories using a Bill of Materials (BOM) approach:

| Category | Purpose | Key Dependencies |
|----------|---------|------------------|
| Compose BOM | UI Framework | `androidx.compose.bom` |
| Kotlin | Language Support | `kotlin.stdlib`, `kotlinx.coroutines.android` |
| Compose UI | User Interface | `material3`, `animation`, `foundation.layout` |
| AndroidX | Android Framework | `appcompat`, `activity.ktx`, `core.ktx` |
| Glance | Widget Framework | `androidx.glance`, `androidx.glance.appwidget` |
| Lifecycle | Component Lifecycle | `lifecycle.viewmodel.ktx`, `lifecycle.livedata.ktx` |
| Navigation | App Navigation | `androidx.navigation.compose` |
| Testing | Test Framework | `junit`, `androidx.test.core`, `robolectric` |

**Sources:** [app/build.gradle.kts:104-156]()

### Dependency Resolution Flow

```mermaid
graph TD
    subgraph "dependency_resolution" ["Dependency Resolution"]
        BOM["Compose BOM Platform"]
        MAIN["Main Dependencies"]
        DEBUG["Debug Dependencies"]
        TEST["Test Dependencies"]
        ANDROID_TEST["Android Test Dependencies"]
    end
    
    subgraph "implementation_types" ["Implementation Types"]
        IMPL["implementation"]
        DEBUG_IMPL["debugImplementation"]
        TEST_IMPL["testImplementation"]
        ANDROID_TEST_IMPL["androidTestImplementation"]
    end
    
    subgraph "dependency_sources" ["Dependency Sources"]
        VERSION_CATALOG["Version Catalog (libs)"]
        COMPOSE_SNAPSHOTS["Compose Snapshots"]
        MAVEN_CENTRAL["Maven Central"]
        GOOGLE_MAVEN["Google Maven"]
    end
    
    BOM --> MAIN
    BOM --> ANDROID_TEST
    
    MAIN --> IMPL
    DEBUG --> DEBUG_IMPL
    TEST --> TEST_IMPL
    ANDROID_TEST --> ANDROID_TEST_IMPL
    
    VERSION_CATALOG --> BOM
    COMPOSE_SNAPSHOTS --> VERSION_CATALOG
    MAVEN_CENTRAL --> VERSION_CATALOG
    GOOGLE_MAVEN --> VERSION_CATALOG
```

**Sources:** [app/build.gradle.kts:104-156](), [settings.gradle.kts:25-36]()

## Advanced Configuration

### Test Configuration

The project includes comprehensive test support with shared test directories:

- **Unit Tests**: Robolectric-based tests with Android resource access
- **Instrumented Tests**: On-device tests using Espresso
- **Shared Test Code**: Common test utilities in `src/sharedTest/java`

**Sources:** [app/build.gradle.kts:64-80]()

### Compose Compiler Configuration

The Compose compiler is configured with performance optimizations:

```mermaid
graph LR
    subgraph "compose_compiler" ["Compose Compiler"]
        STRONG_SKIP["enableStrongSkippingMode = true"]
        STABILITY["Stability Inference"]
        PERFORMANCE["Performance Optimization"]
    end
    
    STRONG_SKIP --> STABILITY
    STABILITY --> PERFORMANCE
```

**Sources:** [app/build.gradle.kts:100-102]()

### Repository Configuration

The project uses centralized repository management with snapshot support:

```mermaid
graph TB
    subgraph "repository_config" ["Repository Configuration"]
        FAIL_MODE["FAIL_ON_PROJECT_REPOS"]
        SNAPSHOT["Compose Snapshot Support"]
        STANDARD["Standard Repositories"]
    end
    
    subgraph "repositories" ["Repository Sources"]
        GRADLE_PORTAL["Gradle Plugin Portal"]
        GOOGLE["Google Maven"]
        MAVEN_CENTRAL["Maven Central"]
        ANDROIDX_SNAPSHOTS["AndroidX Snapshots"]
    end
    
    FAIL_MODE --> STANDARD
    SNAPSHOT --> ANDROIDX_SNAPSHOTS
    STANDARD --> GRADLE_PORTAL
    STANDARD --> GOOGLE
    STANDARD --> MAVEN_CENTRAL
```

**Sources:** [settings.gradle.kts:18-36]()

---

