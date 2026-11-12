<!-- source: DeepWiki mcp.deepwiki.com · repo android/adaptive-apps-samples · page 5 Build System · fetched 2026-10-23 -->

# Build System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AdaptiveJetStream/build.gradle.kts](AdaptiveJetStream/build.gradle.kts)
- [AdaptiveJetStream/gradle/libs.versions.toml](AdaptiveJetStream/gradle/libs.versions.toml)
- [AdaptiveJetStream/jetstream/build.gradle.kts](AdaptiveJetStream/jetstream/build.gradle.kts)

</details>



This document covers the Gradle-based build system for the AdaptiveJetStream project, including dependency management, module configuration, and build optimization features. The build system is designed to support multi-platform Android development with performance optimization and code quality enforcement.

For information about specific dependency libraries and their usage, see [Dependencies](#5.1). For details about code quality enforcement, see [Code Quality](#5.3).

## Build System Architecture

The AdaptiveJetStream project uses a modern Gradle build system with centralized dependency management through version catalogs. The build configuration is structured to support multiple Android form factors while maintaining consistent build practices across modules.

```mermaid
graph TD
    subgraph "Root Project"
        ROOT["build.gradle.kts<br/>(Root)"]
        CATALOG["libs.versions.toml<br/>(Version Catalog)"]
        WRAPPER["gradle/wrapper<br/>(Gradle Wrapper)"]
    end
    
    subgraph "Application Module"
        APP_BUILD["jetstream/build.gradle.kts<br/>(App Module)"]
        APP_PROGUARD["jetstream/proguard-rules.pro<br/>(ProGuard Rules)"]
    end
    
    subgraph "Benchmark Module"
        BENCH_BUILD["benchmark/build.gradle.kts<br/>(Benchmark Module)"]
    end
    
    subgraph "Build Features"
        PLUGINS["Plugin Management<br/>(alias references)"]
        DEPENDENCIES["Dependency Resolution<br/>(version catalog)"]
        BASELINE["Baseline Profiles<br/>(Performance)"]
        KSP["Kotlin Symbol Processing<br/>(Code Generation)"]
    end
    
    ROOT --> APP_BUILD
    ROOT --> BENCH_BUILD
    CATALOG --> APP_BUILD
    CATALOG --> BENCH_BUILD
    WRAPPER --> ROOT
    
    APP_BUILD --> PLUGINS
    APP_BUILD --> DEPENDENCIES
    APP_BUILD --> BASELINE
    APP_BUILD --> KSP
    
    APP_BUILD --> APP_PROGUARD
```

Sources: [AdaptiveJetStream/build.gradle.kts:1-34](), [AdaptiveJetStream/gradle/libs.versions.toml:1-77](), [AdaptiveJetStream/jetstream/build.gradle.kts:1-141]()

## Top-Level Build Configuration

The root `build.gradle.kts` file establishes the plugin ecosystem for the entire project using the version catalog pattern. All plugins are declared using the `alias()` function with `apply false` to make them available to submodules without applying them at the root level.

| Plugin | Purpose | Catalog Reference |
|--------|---------|-------------------|
| `android.application` | Android app module configuration | `libs.plugins.android.application` |
| `kotlin.android` | Kotlin Android plugin | `libs.plugins.kotlin.android` |
| `kotlin.serialization` | Kotlin serialization support | `libs.plugins.kotlin.serialization` |
| `compose.compiler` | Compose compiler plugin | `libs.plugins.compose.compiler` |
| `android.test` | Android test module support | `libs.plugins.android.test` |
| `hilt` | Dependency injection | `libs.plugins.hilt` |
| `ksp` | Kotlin Symbol Processing | `libs.plugins.ksp` |

The plugin declarations in [AdaptiveJetStream/build.gradle.kts:25-33]() use the centralized version catalog to ensure consistent plugin versions across all modules.

Sources: [AdaptiveJetStream/build.gradle.kts:17-33]()

## Version Catalog Structure

The `libs.versions.toml` file implements centralized dependency management using Gradle's version catalog feature. This approach ensures consistent dependency versions across modules and simplifies dependency updates.

```mermaid
graph TB
    subgraph "Version Catalog Structure"
        VERSIONS["[versions]<br/>Version Declarations"]
        LIBRARIES["[libraries]<br/>Library Dependencies"]
        PLUGINS["[plugins]<br/>Plugin Definitions"]
    end
    
    subgraph "Key Version Groups"
        COMPOSE_GROUP["Compose BOM<br/>compose-bom = '2025.05.00'"]
        KOTLIN_GROUP["Kotlin Ecosystem<br/>kotlin-android = '2.1.10'<br/>ksp = '2.1.10-1.0.30'"]
        ANDROID_GROUP["Android Build<br/>android-gradle-plugin = '8.9.3'"]
        MEDIA_GROUP["Media3 Suite<br/>media3 = '1.6.1'"]
        ADAPTIVE_GROUP["Material3 Adaptive<br/>material3-adaptive = '1.1.0'"]
    end
    
    subgraph "Module Resolution"
        APP_MODULE["jetstream/build.gradle.kts<br/>implementation(libs.xxx)"]
        BENCH_MODULE["benchmark/build.gradle.kts<br/>implementation(libs.xxx)"]
    end
    
    VERSIONS --> LIBRARIES
    VERSIONS --> PLUGINS
    
    COMPOSE_GROUP --> LIBRARIES
    KOTLIN_GROUP --> LIBRARIES
    ANDROID_GROUP --> PLUGINS
    MEDIA_GROUP --> LIBRARIES
    ADAPTIVE_GROUP --> LIBRARIES
    
    LIBRARIES --> APP_MODULE
    LIBRARIES --> BENCH_MODULE
    PLUGINS --> APP_MODULE
    PLUGINS --> BENCH_MODULE
```

The version catalog defines 27 distinct version declarations in [AdaptiveJetStream/gradle/libs.versions.toml:1-28](), covering major dependency families including Compose, Kotlin, Android, Media3, and XR components.

Sources: [AdaptiveJetStream/gradle/libs.versions.toml:1-77]()

## Application Module Build Configuration

The main application module build script in `jetstream/build.gradle.kts` configures the Android application with comprehensive feature support including Compose, dependency injection, and performance optimization.

### Android Configuration

The Android configuration block establishes the application metadata and build behavior:

- **Namespace**: `com.google.jetstream` [AdaptiveJetStream/jetstream/build.gradle.kts:32]()
- **SDK Targets**: `compileSdk = 35`, `minSdk = 28`, `targetSdk = 35` [AdaptiveJetStream/jetstream/build.gradle.kts:34-39]()
- **Build Features**: Compose UI enabled, BuildConfig generation enabled [AdaptiveJetStream/jetstream/build.gradle.kts:59-62]()
- **JVM Toolchain**: Java 17 [AdaptiveJetStream/jetstream/build.gradle.kts:28-29]()

### Build Types Configuration

The release build type is configured for production optimization with ProGuard minification enabled [AdaptiveJetStream/jetstream/build.gradle.kts:49-58]():

```
buildTypes {
    getByName("release") {
        isMinifyEnabled = true
        signingConfig = signingConfigs.getByName("debug")
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
```

Sources: [AdaptiveJetStream/jetstream/build.gradle.kts:31-73]()

## Dependency Management Implementation

The application module demonstrates the version catalog pattern in practice through its dependency declarations. Dependencies are organized into logical groups using the `libs` accessor.

### Core Android Dependencies

| Dependency Group | Libraries | Purpose |
|------------------|-----------|---------|
| **Core Android** | `androidx.core.ktx`, `androidx.lifecycle.runtime.ktx` | Essential Android functionality |
| **Compose UI** | `androidx.compose.bom`, `androidx.compose.material3` | Jetpack Compose framework |
| **Activity/Navigation** | `androidx.activity.compose`, `androidx.navigation.compose` | App structure and navigation |

### Specialized Feature Dependencies

The build includes specialized libraries for adaptive UI, media playback, and XR functionality:

- **Material3 Adaptive**: Four separate adaptive libraries for responsive UI [AdaptiveJetStream/jetstream/build.gradle.kts:104-108]()
- **Media3 Suite**: ExoPlayer, session management, and Compose UI integration [AdaptiveJetStream/jetstream/build.gradle.kts:110-113]()
- **XR Components**: SceneCore, Compose integration, and Material3 XR support [AdaptiveJetStream/jetstream/build.gradle.kts:130-133]()

### Build-Time Dependencies

The configuration includes build-time processors and tools:

- **Hilt DI**: Runtime implementation and KSP annotation processor [AdaptiveJetStream/jetstream/build.gradle.kts:118-121]()
- **Baseline Profiles**: Connection to benchmark module for performance optimization [AdaptiveJetStream/jetstream/build.gradle.kts:139]()
- **Debug Tools**: Compose UI tooling for development [AdaptiveJetStream/jetstream/build.gradle.kts:136]()

Sources: [AdaptiveJetStream/jetstream/build.gradle.kts:75-140]()

## Plugin Integration

The application module applies multiple plugins to enable comprehensive build functionality. The plugin application follows the version catalog pattern using `alias()` references.

```mermaid
graph LR
    subgraph "Applied Plugins"
        APP_PLUGIN["android.application<br/>(libs.plugins.android.application)"]
        KOTLIN_PLUGIN["kotlin.android<br/>(libs.plugins.kotlin.android)"]
        SERIAL_PLUGIN["kotlin.serialization<br/>(libs.plugins.kotlin.serialization)"]
        COMPOSE_PLUGIN["compose.compiler<br/>(libs.plugins.compose.compiler)"]
        HILT_PLUGIN["hilt<br/>(libs.plugins.hilt)"]
        KSP_PLUGIN["ksp<br/>(libs.plugins.ksp)"]
        BASELINE_PLUGIN["androidx.baselineprofile<br/>(libs.plugins.androidx.baselineprofile)"]
        PARCELIZE_PLUGIN["kotlin.parcelize<br/>(libs.plugins.kotlin.parcelize)"]
    end
    
    subgraph "Plugin Functions"
        ANDROID_BUILD["Android App<br/>Module Support"]
        KOTLIN_COMPILE["Kotlin Language<br/>Compilation"]
        JSON_SERIAL["JSON Serialization<br/>Code Generation"]
        COMPOSE_COMPILE["Compose Compiler<br/>Optimization"]
        DI_PROCESSING["Dependency Injection<br/>Code Generation"]
        SYMBOL_PROCESS["Annotation<br/>Processing"]
        PROFILE_GEN["Baseline Profile<br/>Generation"]
        PARCEL_GEN["Parcelable<br/>Implementation"]
    end
    
    APP_PLUGIN --> ANDROID_BUILD
    KOTLIN_PLUGIN --> KOTLIN_COMPILE
    SERIAL_PLUGIN --> JSON_SERIAL
    COMPOSE_PLUGIN --> COMPOSE_COMPILE
    HILT_PLUGIN --> DI_PROCESSING
    KSP_PLUGIN --> SYMBOL_PROCESS
    BASELINE_PLUGIN --> PROFILE_GEN
    PARCELIZE_PLUGIN --> PARCEL_GEN
```

The plugin configuration enables several code generation and optimization features essential for modern Android development, particularly the KSP-based Hilt annotation processing [AdaptiveJetStream/jetstream/build.gradle.kts:121]() and baseline profile integration [AdaptiveJetStream/jetstream/build.gradle.kts:23]().

Sources: [AdaptiveJetStream/jetstream/build.gradle.kts:16-25]()

## Build Optimization Features

The build system incorporates several optimization strategies for performance and code quality:

### Baseline Profile Integration

The application module connects to the benchmark module for baseline profile generation through the `baselineProfile()` dependency declaration [AdaptiveJetStream/jetstream/build.gradle.kts:139](). This enables runtime performance optimization by pre-compiling frequently used code paths.

### ProGuard Configuration

The release build type enables code minification and optimization through ProGuard, using both the default Android optimization rules and custom application-specific rules [AdaptiveJetStream/jetstream/build.gradle.kts:53-56]().

### Packaging Optimization

Resource packaging excludes common license files to reduce APK size [AdaptiveJetStream/jetstream/build.gradle.kts:64-68]():

```
packaging {
    resources {
        excludes += "/META-INF/{AL2.0,LGPL2.1}"
    }
}
```

Sources: [AdaptiveJetStream/jetstream/build.gradle.kts:49-68](), [AdaptiveJetStream/jetstream/build.gradle.kts:139]()

---

