<!-- source: DeepWiki mcp.deepwiki.com · repo android/socialite · page 2 Getting Started · fetched 2026-10-23 -->

# Getting Started

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [app/build.gradle.kts](app/build.gradle.kts)
- [app/google-services.json](app/google-services.json)
- [app/src/main/java/com/google/android/samples/socialite/repository/ChatRepository.kt](app/src/main/java/com/google/android/samples/socialite/repository/ChatRepository.kt)
- [app/src/main/res/values/strings.xml](app/src/main/res/values/strings.xml)
- [baselineprofile/.gitignore](baselineprofile/.gitignore)
- [baselineprofile/build.gradle.kts](baselineprofile/build.gradle.kts)
- [baselineprofile/src/main/AndroidManifest.xml](baselineprofile/src/main/AndroidManifest.xml)
- [build.gradle.kts](build.gradle.kts)
- [gradle/libs.versions.toml](gradle/libs.versions.toml)
- [settings.gradle.kts](settings.gradle.kts)

</details>



This document provides technical guidance for setting up, building, and running the SociaLite Android application. It covers the build system configuration, dependency management, and module structure required for development.

For information about the overall application architecture and component interactions, see [Architecture](#3). For details about specific features like chat, media, and AI integration, see [Core Features](#4).

## Prerequisites

The SociaLite project requires the following development environment:

| Component | Version | Configuration |
|-----------|---------|---------------|
| Android Studio | Latest stable | With Kotlin support |
| Java | 17 | JVM toolchain configured |
| Android SDK | API 21-36 | Min SDK 21, Target SDK 35, Compile SDK 36 |
| Gradle | 8.9+ | Managed by wrapper |

Sources: [app/build.gradle.kts:32-34](), [app/build.gradle.kts:42-47](), [app/build.gradle.kts:60-67]()

## Project Structure

SociaLite uses a multi-module Gradle project with dependency management via version catalogs:

```mermaid
graph TB
    subgraph "Root Project: social"
        RootBuild["build.gradle.kts<br/>Root Configuration"]
        Settings["settings.gradle.kts<br/>Module Declaration"]
        LibsVersions["gradle/libs.versions.toml<br/>Version Catalog"]
    end
    
    subgraph "App Module: :app"
        AppBuild["app/build.gradle.kts<br/>Main Application"]
        AppSrc["app/src/main/<br/>Source Code"]
        AppRes["app/src/main/res/<br/>Resources"]
        AppAssets["app/src/main/assets/<br/>Static Assets"]
        GoogleServices["app/google-services.json<br/>Firebase Config"]
    end
    
    subgraph "Performance Module: :baselineprofile"
        BaselineBuild["baselineprofile/build.gradle.kts<br/>Performance Optimization"]
        BaselineSrc["baselineprofile/src/<br/>Profile Generation"]
    end
    
    Settings --> AppBuild
    Settings --> BaselineBuild
    LibsVersions --> AppBuild
    LibsVersions --> BaselineBuild
    RootBuild --> AppBuild
    RootBuild --> BaselineBuild
```

Sources: [settings.gradle.kts:40-42](), [build.gradle.kts:19-29](), [gradle/libs.versions.toml:15-67]()

## Build System Configuration

### Version Catalog Management

The project uses Gradle's version catalog system for centralized dependency management:

```mermaid
graph LR
    subgraph "libs.versions.toml Structure"
        Versions["[versions]<br/>accompanist = 0.32.0<br/>compose = 1.9.0-alpha03<br/>kotlin = 2.1.10<br/>hilt = 2.56.1"]
        Libraries["[libraries]<br/>compose-ui<br/>hilt-android<br/>room-ktx<br/>media3-exoplayer"]
        Plugins["[plugins]<br/>androidApplication<br/>compose-compiler<br/>hilt<br/>kotlinAndroid"]
    end
    
    AppModule["app/build.gradle.kts<br/>alias(libs.plugins.hilt)<br/>implementation(libs.compose.ui)"]
    
    Versions --> Libraries
    Versions --> Plugins
    Libraries --> AppModule
    Plugins --> AppModule
```

Key dependency categories managed in the version catalog:

| Category | Key Libraries | Purpose |
|----------|---------------|---------|
| UI Framework | `compose-bom`, `compose-ui`, `compose-material3` | Jetpack Compose UI |
| Dependency Injection | `hilt-android`, `hilt-compiler` | Dependency management |
| Database | `room-ktx`, `room-compiler` | Local data persistence |
| Media Processing | `media3-exoplayer`, `camera-core`, `camera-compose` | Media capture and playback |
| AI Integration | `firebase-ai`, `generativeai` | Gemini AI capabilities |

Sources: [gradle/libs.versions.toml:70-147](), [gradle/libs.versions.toml:149-162](), [app/build.gradle.kts:92-192]()

### Build Configuration

The main application module configuration includes:

```mermaid
graph TB
    subgraph "App Build Configuration"
        Namespace["namespace = com.google.android.samples.socialite"]
        SDKVersions["minSdk = 21<br/>targetSdk = 35<br/>compileSdk = 36"]
        BuildFeatures["buildFeatures:<br/>compose = true"]
        KotlinOptions["kotlinOptions:<br/>jvmTarget = 17<br/>freeCompilerArgs = -Xcontext-receivers"]
    end
    
    subgraph "Applied Plugins"
        AndroidApp["androidApplication"]
        ComposeCompiler["compose-compiler"]
        Hilt["hilt"]
        KotlinAndroid["kotlinAndroid"]
        KSP["ksp"]
        Secrets["secrets"]
    end
    
    AndroidApp --> Namespace
    ComposeCompiler --> BuildFeatures
    Hilt --> KotlinOptions
    KotlinAndroid --> SDKVersions
```

Sources: [app/build.gradle.kts:18-30](), [app/build.gradle.kts:40-52](), [app/build.gradle.kts:64-73]()

## Building and Running

### Standard Build Process

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/android/socialite
   cd socialite
   ```

2. **Build with Gradle**:
   ```bash
   ./gradlew :app:assembleDebug
   ```

3. **Run Tests**:
   ```bash
   ./gradlew :app:testDebugUnitTest
   ./gradlew :app:connectedDebugAndroidTest
   ```

### Code Quality and Formatting

The project includes automated code formatting via Spotless:

```mermaid
graph LR
    SpotlessConfig["build.gradle.kts<br/>spotless plugin configuration"]
    KtLint["ktlint version 1.1.1<br/>Kotlin code style"]
    TargetFiles["target: **/*.kt<br/>exclude: **/camera/viewfinder/**"]
    
    SpotlessConfig --> KtLint
    KtLint --> TargetFiles
```

Apply formatting before committing:
```bash
./gradlew spotlessApply
```

Sources: [build.gradle.kts:32-43](), [gradle/libs.versions.toml:141]()

## Firebase AI Integration (Optional)

### Default Configuration

The project includes a mock Firebase configuration for basic functionality:

```mermaid
graph TB
    MockConfig["app/google-services.json<br/>project_id: mock_project<br/>package_name: com.google.android.samples.socialite"]
    ChatRepository["ChatRepository.kt<br/>toggleChatbotSetting()<br/>Firebase.ai integration"]
    
    MockConfig --> ChatRepository
```

### Production Setup

To enable full AI capabilities:

1. **Create Firebase Project**: Follow [Firebase AI setup guide](https://firebase.google.com/docs/ai-logic/get-started?platform=android&api=dev)

2. **Replace Configuration**: Replace `app/google-services.json` with your project's configuration

3. **Enable AI Features**: 
   - Launch app
   - Navigate to Settings screen
   - Toggle "AI Chatbot" setting

The `ChatRepository` class handles AI integration through the Firebase AI SDK:

```mermaid
graph LR
    UserMessage["User sends message"]
    ChatRepo["ChatRepository.sendMessage()"]
    GeminiAPI["Firebase.ai().generativeModel<br/>model: gemini-2.0-flash-lite-001"]
    AIResponse["AI generates response"]
    
    UserMessage --> ChatRepo
    ChatRepo --> GeminiAPI
    GeminiAPI --> AIResponse
```

Sources: [app/google-services.json:1-30](), [app/src/main/java/com/google/android/samples/socialite/repository/ChatRepository.kt:114-120](), [app/src/main/java/com/google/android/samples/socialite/repository/ChatRepository.kt:396-414]()

## Performance Optimization

### Baseline Profiles

The project includes a dedicated module for generating baseline profiles to improve app startup performance:

```mermaid
graph TB
    BaselineModule[":baselineprofile module"]
    ManagedDevice["Pixel 6 API 34<br/>Virtual Device"]
    ProfileGeneration["Profile Generation<br/>UI Automation Tests"]
    OptimizedAPK["Optimized APK<br/>with ART compilation hints"]
    
    BaselineModule --> ManagedDevice
    ManagedDevice --> ProfileGeneration
    ProfileGeneration --> OptimizedAPK
```

The baseline profile is automatically generated during release builds and included in the main app module.

Sources: [baselineprofile/build.gradle.kts:40-45](), [app/build.gradle.kts:114]()

## Asset Management

### Model Downloads

The project includes automatic download of ML models for camera effects:

```mermaid
graph LR
    DownloadScript["download_model.gradle<br/>Asset Download Script"]
    AssetDir["app/src/main/assets/<br/>Model Storage"]
    CameraEffects["Camera Effects<br/>TensorFlow Lite Models"]
    
    DownloadScript --> AssetDir
    AssetDir --> CameraEffects
```

Models are downloaded automatically during build unless manually placed in the assets directory.

Sources: [app/build.gradle.kts:84-90]()

---

