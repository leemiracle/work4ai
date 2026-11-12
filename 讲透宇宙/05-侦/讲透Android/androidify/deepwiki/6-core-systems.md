<!-- source: DeepWiki mcp.deepwiki.com · repo android/androidify · page 6 Core Systems · fetched 2026-10-23 -->

# Core Systems

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/build.gradle.kts](app/build.gradle.kts)
- [core/network/build.gradle.kts](core/network/build.gradle.kts)
- [core/testing/build.gradle.kts](core/testing/build.gradle.kts)
- [core/theme/build.gradle.kts](core/theme/build.gradle.kts)
- [core/util/build.gradle.kts](core/util/build.gradle.kts)
- [data/build.gradle.kts](data/build.gradle.kts)
- [settings.gradle.kts](settings.gradle.kts)

</details>



## Purpose and Scope

This document provides an overview of the shared core modules in the Androidify application. These modules encapsulate cross-cutting functionality that is used across multiple feature modules, implementing the horizontal layers of the application architecture.

The core systems include:
- **Network Layer** (`core/network`) - External service integration and AI data sources.
- **Data Layer** (`data`) - Repository implementations and business logic aggregation.
- **Theme and UI Components** (`core/theme`) - Design system, Material 3 theming, and reusable UI.
- **Utilities** (`core/util`) - Layout helpers, file providers, and animation utilities.
- **XR Support** (`core/xr`) - Spatial computing functionality for XR-enabled devices.
- **Testing Infrastructure** (`core/testing`) - Test doubles and utilities for unit and instrumented tests.

For detailed information about specific core modules, see:
- Network Layer details: [Network Layer](#6.1)
- Data Layer details: [Data Layer](#6.2)
- Theme and UI Components: [Theme and UI Components](#6.3)
- Utilities: [Utilities](#6.4)
- XR Support: [XR Support](#6.5)

For AI/ML integration details that span the network and data layers, see [AI and ML Integration](#4).

---

## Core Module Architecture

The core modules form the foundation of the application, providing shared functionality to all feature modules. The diagram below illustrates the dependency relationships between core modules and how feature modules consume them.

```mermaid
graph TB
    subgraph "Feature Modules"
        [feature/home]
        [feature/camera]
        [feature/creation]
        [feature/results]
    end
    
    subgraph "Core Modules"
        [core/theme]
        [core/util]
        [core/xr]
        [core/network]
        [core/testing]
    end
    
    subgraph "Data Layer"
        [data]
    end
    
    [feature/home] --> [core/theme]
    [feature/home] --> [core/util]
    [feature/home] --> [core/xr]
    [feature/home] --> [data]
    
    [feature/camera] --> [core/theme]
    [feature/camera] --> [core/util]
    [feature/camera] --> [core/xr]
    [feature/camera] --> [core/network]
    [feature/camera] --> [data]
    
    [feature/creation] --> [core/theme]
    [feature/creation] --> [core/util]
    [feature/creation] --> [core/xr]
    [feature/creation] --> [data]
    [feature/creation] --> [core/network]
    
    [feature/results] --> [core/theme]
    [feature/results] --> [core/util]
    [feature/results] --> [core/xr]
    [feature/results] --> [data]
    [feature/results] --> [core/network]
    
    [data] --> [core/network]
    [data] --> [core/util]
    
    [core/testing] --> [data]
    [core/testing] --> [core/network]
    [core/testing] --> [core/util]
```

**Diagram: Core Module Dependencies**

The dependency flow follows these rules:
1. Feature modules depend on one or more core modules [app/build.gradle.kts:130-137]().
2. The `data` module aggregates functionality from `core/network` and `core/util` [data/build.gradle.kts:33-34]().
3. `core/testing` provides test infrastructure for the data and network layers [core/testing/build.gradle.kts:42-44]().
4. Core modules do not depend on feature modules, ensuring a clean hierarchy [settings.gradle.kts:55-70]().

**Sources:** [app/build.gradle.kts:130-137](), [data/build.gradle.kts:33-34](), [core/testing/build.gradle.kts:42-44](), [settings.gradle.kts:55-70]()

---

## Module Responsibilities

The following table summarizes the responsibilities of each core module based on their build configurations and dependencies:

| Module | Namespace | Primary Responsibilities | Key Dependencies |
|--------|-----------|-------------------------|------------------|
| `core/network` | `com.android.developers.androidify.network` | Firebase AI integration, ML Kit services, Retrofit/OkHttp setup, App Check initialization | `firebase-ai`, `mlkit-segmentation`, `retrofit`, `okhttp` |
| `data` | `com.android.developers.androidify.data` | Repository pattern implementations, business logic aggregation, domain model definitions | `core/network`, `core/util`, `genai-prompt` |
| `core/theme` | `com.android.developers.androidify.theme` | Material 3 theming, shared element transitions, reusable Composables, background assets | `androidx-adaptive`, `navigation3-ui`, `material3` |
| `core/util` | `com.android.developers.androidify.util` | Layout utilities for adaptive design, file provider for local storage, animation helpers | `androidx-window`, `androidx-animation` |
| `core/xr` | `com.android.developers.androidify.xr` | Spatial UI modes, XR-specific layouts, adaptive 3D experiences | `androidx-xr-extensions` (compileOnly) |
| `core/testing` | `com.android.developers.androidify.testing` | Test doubles for repositories, fake data sources, test runners | `hilt-android-testing`, `kotlinx-coroutines-test` |

**Sources:** [core/network/build.gradle.kts:24,63,68,71](), [data/build.gradle.kts:23,33,47](), [core/theme/build.gradle.kts:22,51,54](), [core/util/build.gradle.kts:23,39-41](), [app/build.gradle.kts:140](), [core/testing/build.gradle.kts:23,34,41]()

---

## Core Module Dependency Chain

The following diagram illustrates the internal dependency chain within core modules and the data layer, showing how functionality flows from low-level infrastructure to high-level business logic.

```mermaid
graph LR
    subgraph "Infrastructure Layer"
        [OkHttp]
        [Retrofit]
        [FirebaseBOM]
        [MLKit]
        [ComposeBOM]
        [Hilt]
    end
    
    subgraph "core/network"
        [FirebaseAppCheckInitializer]
        [FirebaseAiDataSource]
        [GeminiNanoDataSource]
        [LocalSegmentationDataSource]
        [RemoteConfigDataSource]
    end
    
    subgraph "core/util"
        [LayoutUtils]
        [LocalFileProvider]
    end
    
    subgraph "data"
        [ImageGenerationRepository]
    end
    
    [FirebaseBOM] --> [FirebaseAppCheckInitializer]
    [FirebaseBOM] --> [FirebaseAiDataSource]
    [FirebaseBOM] --> [RemoteConfigDataSource]
    
    [MLKit] --> [LocalSegmentationDataSource]
    [MLKit] --> [GeminiNanoDataSource]
    
    [Retrofit] --> [FirebaseAiDataSource]
    [OkHttp] --> [FirebaseAiDataSource]
    
    [ComposeBOM] --> [LayoutUtils]
    
    [Hilt] --> [FirebaseAiDataSource]
    [Hilt] --> [GeminiNanoDataSource]
    [Hilt] --> [LocalSegmentationDataSource]
    [Hilt] --> [RemoteConfigDataSource]
    [Hilt] --> [ImageGenerationRepository]
    
    [FirebaseAiDataSource] --> [ImageGenerationRepository]
    [GeminiNanoDataSource] --> [ImageGenerationRepository]
    [LocalSegmentationDataSource] --> [ImageGenerationRepository]
    [RemoteConfigDataSource] --> [ImageGenerationRepository]
    [LocalFileProvider] --> [ImageGenerationRepository]
```

**Diagram: Core Module Internal Dependencies**

This chain demonstrates the layering principle:
1. **Infrastructure Layer**: Third-party libraries and platform SDKs defined in `libs.versions.toml`.
2. **Data Source Layer** (`core/network`): Direct integrations with external services like Firebase and ML Kit [core/network/build.gradle.kts:61-74]().
3. **Utility Layer** (`core/util`): Helper functions for UI and storage [core/util/build.gradle.kts:33-42]().
4. **Repository Layer** (`data`): Business logic that orchestrates data sources [data/build.gradle.kts:33-34]().

**Sources:** [core/network/build.gradle.kts:48-76](), [data/build.gradle.kts:32-47](), [core/util/build.gradle.kts:32-42]()

---

## Build Configuration

Each core module uses Gradle Kotlin DSL with the version catalog for dependency management. The table below shows key build configuration details:

| Module | Plugin Configuration | Special Build Features |
|--------|---------------------|------------------------|
| `core/network` | `androidify.androidLibrary`, `serialization`, `ksp`, `hilt` | `buildConfig` enabled with debug/release flags [core/network/build.gradle.kts:28-38]() |
| `data` | `androidify.androidLibrary`, `ksp`, `hilt` | Standard library configuration [data/build.gradle.kts:16-20]() |
| `core/theme` | `androidify.androidComposeLibrary` | `fontName` `buildConfig` field for dynamic font selection [core/theme/build.gradle.kts:23-33]() |
| `core/util` | `androidify.androidComposeLibrary`, `ksp`, `hilt` | Compose support for UI utilities [core/util/build.gradle.kts:16-20]() |
| `core/testing` | `androidify.androidComposeLibrary`, `ksp`, `hilt` | `api` exposure of `kotlinx-coroutines-test` [core/testing/build.gradle.kts:34]() |

**Sources:** [core/network/build.gradle.kts:16-46](), [data/build.gradle.kts:16-30](), [core/theme/build.gradle.kts:16-40](), [core/util/build.gradle.kts:16-30](), [core/testing/build.gradle.kts:16-31]()

---

## Convention Plugins

The core modules use custom Gradle convention plugins (prefixed with `androidify.*`) that encapsulate common build configuration:

- **`androidify.androidLibrary`**: Base Android library configuration [core/network/build.gradle.kts:17]().
- **`androidify.androidComposeLibrary`**: Android library with Jetpack Compose enabled [core/theme/build.gradle.kts:17]().

These plugins ensure consistent SDK versions (Compile SDK 37, Min SDK 26) and compiler options across the multi-module project [settings.gradle.kts:37-47]().

**Sources:** [core/network/build.gradle.kts:17](), [core/theme/build.gradle.kts:17](), [settings.gradle.kts:37-47]()

---

## Dependency Injection Strategy

All core modules that provide injectable components use Hilt for dependency injection. The pattern follows these principles:

```mermaid
graph TB
    subgraph "Hilt Module Definitions"
        [NetworkModule]
        [DataModule]
    end
    
    subgraph "Provided Dependencies"
        [FirebaseAiDataSource]
        [GeminiNanoDataSource]
        [LocalSegmentationDataSource]
        [RemoteConfigDataSource]
        [ImageGenerationRepository]
    end
    
    subgraph "Consumers"
        [ViewModels]
        [UseCases]
    end
    
    [NetworkModule] -.provides.-> [FirebaseAiDataSource]
    [NetworkModule] -.provides.-> [GeminiNanoDataSource]
    [NetworkModule] -.provides.-> [LocalSegmentationDataSource]
    [NetworkModule] -.provides.-> [RemoteConfigDataSource]
    
    [DataModule] -.provides.-> [ImageGenerationRepository]
    
    [FirebaseAiDataSource] --> [ImageGenerationRepository]
    [GeminiNanoDataSource] --> [ImageGenerationRepository]
    [LocalSegmentationDataSource] --> [ImageGenerationRepository]
    [RemoteConfigDataSource] --> [ImageGenerationRepository]
    
    [ImageGenerationRepository] --> [ViewModels]
    [ImageGenerationRepository] --> [UseCases]
```

**Diagram: Hilt Dependency Injection Architecture**

Key aspects:
1. All data sources and repositories are singleton-scoped.
2. Modules are installed in `SingletonComponent` for app-wide availability.
3. Feature modules receive dependencies through constructor injection [app/build.gradle.kts:110,114]().
4. Testing modules provide alternative implementations via test modules [core/testing/build.gradle.kts:41]().

**Sources:** [core/network/build.gradle.kts:20,54,75](), [data/build.gradle.kts:19,42,48](), [core/testing/build.gradle.kts:19,39,48]()

---

## Testing Infrastructure Integration

The `core/testing` module provides test doubles for the data and network layers, enabling isolated unit testing of feature modules. The architecture supports testing at multiple levels:

```mermaid
graph TB
    subgraph "Production Code"
        [ImageGenerationRepository]
        [FirebaseAiDataSource]
        [RemoteConfigDataSource]
    end
    
    subgraph "core/testing Module"
        [FakeImageGenerationRepository]
        [TestFirebaseAiDataSource]
        [TestRemoteConfigDataSource]
        [AndroidifyTestRunner]
        [TestFileProvider]
    end
    
    subgraph "Test Implementations"
        [UnitTests]
        [InstrumentedTests]
    end
    
    [ImageGenerationRepository] -.implements.-> [FakeImageGenerationRepository]
    [FirebaseAiDataSource] -.implements.-> [TestFirebaseAiDataSource]
    [RemoteConfigDataSource] -.implements.-> [TestRemoteConfigDataSource]
    
    [FakeImageGenerationRepository] --> [UnitTests]
    [TestFirebaseAiDataSource] --> [UnitTests]
    [TestRemoteConfigDataSource] --> [UnitTests]
    [AndroidifyTestRunner] --> [InstrumentedTests]
    [TestFileProvider] --> [UnitTests]
```

**Diagram: Testing Infrastructure Architecture**

The testing module provides:
1. **Fake implementations** that follow production interfaces but use in-memory state.
2. **Test data sources** with controllable behavior for deterministic testing.
3. **Test utilities** like `AndroidifyTestRunner` for Hilt integration [core/network/build.gradle.kts:26]().
4. **API exposure** of testing libraries like `kotlinx-coroutines-test` [core/testing/build.gradle.kts:34]().

**Sources:** [core/testing/build.gradle.kts:33-48](), [core/network/build.gradle.kts:26]()

---

## Inter-module Communication

Feature modules communicate with core modules through well-defined interfaces. Direct dependencies between feature modules are minimized to prevent circular dependencies.

The communication pattern follows these rules:
1. **Feature → Data**: Feature modules inject `ImageGenerationRepository` for business logic [data/build.gradle.kts:42]().
2. **Feature → Network**: Direct injection of data sources when needed (e.g., camera uses ML Kit services) [core/network/build.gradle.kts:71-72]().
3. **Feature → Theme**: Direct usage of Composable functions and theme values [core/theme/build.gradle.kts:44-47]().
4. **Feature → Util**: Direct usage of utility functions and extension methods [core/util/build.gradle.kts:33-37]().
5. **Data → Network**: Repository implementations delegate to data sources [data/build.gradle.kts:33]().

**Sources:** [data/build.gradle.kts:32-35](), [core/testing/build.gradle.kts:42-47](), [app/build.gradle.kts:130-137]()

---

## Module Initialization

Some core modules require initialization at app startup. The application uses AndroidX App Startup for automatic initialization:

| Module | Initializer Class | Purpose | When Initialized |
|--------|------------------|---------|------------------|
| `core/network` | `FirebaseAppCheckInitializer` | Sets up Firebase App Check for API security | App startup (automatic) |
| `core/theme` | None | Theme is applied in Composable hierarchy | On composition |
| `core/util` | None | Utilities are stateless functions | On first use |

The `androidx.app.startup` library is a dependency in both `core/network` and `data` modules to facilitate this [core/network/build.gradle.kts:49](), [data/build.gradle.kts:36]().

**Sources:** [core/network/build.gradle.kts:49](), [data/build.gradle.kts:36]()

---

