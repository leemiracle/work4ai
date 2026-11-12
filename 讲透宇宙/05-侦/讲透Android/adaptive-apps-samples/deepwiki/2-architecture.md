<!-- source: DeepWiki mcp.deepwiki.com · repo android/adaptive-apps-samples · page 2 Architecture · fetched 2026-10-23 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/JetStreamApplication.kt](AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/JetStreamApplication.kt)
- [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt](AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt)
- [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/PlaybackService.kt](AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/PlaybackService.kt)

</details>



This document provides an overview of the AdaptiveJetStream application's core architecture, including its primary components, design patterns, and system interactions. It covers the high-level structure and relationships between major subsystems.

For detailed information about specific subsystems, see [Application Structure](#2.1), [Media Playback System](#2.2), and [Data Layer](#2.3). For UI implementation details, see [User Interface](#3). For performance optimization strategies, see [Performance Optimization](#4).

## Architecture Overview

AdaptiveJetStream is built as a modern Android application designed for cross-platform media streaming with adaptive UI capabilities. The architecture follows clean architecture principles with clear separation of concerns across presentation, business logic, and data layers.

```mermaid
graph TD
    subgraph "Application Layer"
        APP["JetStreamApplication"]
        MAIN["MainActivity"]
        SERVICE["PlaybackService"]
    end
    
    subgraph "Presentation Layer"
        UI["App (Compose UI)"]
        THEME["JetStreamTheme"]
        XR["XR Components"]
    end
    
    subgraph "Business Logic"
        REPO["MovieRepository"]
        REPOIMPL["MovieRepositoryImpl"]
    end
    
    subgraph "Data Layer"
        JSON["JSON Assets"]
        MEDIA["Media Content"]
    end
    
    subgraph "Framework Integration"
        HILT["Hilt DI Container"]
        MEDIA3["Media3/ExoPlayer"]
        COMPOSE["Jetpack Compose"]
    end
    
    APP --> HILT
    APP --> MAIN
    APP --> SERVICE
    
    MAIN --> UI
    UI --> THEME
    UI --> XR
    
    HILT --> REPO
    REPO --> REPOIMPL
    REPOIMPL --> JSON
    
    SERVICE --> MEDIA3
    MEDIA3 --> MEDIA
    
    UI --> COMPOSE
    
    style APP fill:#f9f9f9
    style MAIN fill:#f9f9f9
    style SERVICE fill:#f9f9f9
```

**Sources:** [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/JetStreamApplication.kt:1-40](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:1-265](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/PlaybackService.kt:1-68]()

## Core Components

The application consists of three primary components that form the foundation of the system architecture:

```mermaid
graph LR
    subgraph "JetStreamApplication"
        APP_CLASS["JetStreamApplication"]
        HILT_MODULE["MovieRepositoryModule"]
    end
    
    subgraph "MainActivity"
        MAIN_CLASS["MainActivity"]
        COMPOSE_SETUP["setContent{}"]
        EDGE_TO_EDGE["enableEdgeToEdge()"]
        SPLASH["installSplashScreen()"]
    end
    
    subgraph "PlaybackService"
        SERVICE_CLASS["PlaybackService"]
        MEDIA_SESSION["MediaSession"]
        EXO_PLAYER["ExoPlayer"]
    end
    
    APP_CLASS --> HILT_MODULE
    MAIN_CLASS --> COMPOSE_SETUP
    MAIN_CLASS --> EDGE_TO_EDGE
    MAIN_CLASS --> SPLASH
    SERVICE_CLASS --> MEDIA_SESSION
    SERVICE_CLASS --> EXO_PLAYER
    
    HILT_MODULE -.-> SERVICE_CLASS
    HILT_MODULE -.-> MAIN_CLASS
```

**Sources:** [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/JetStreamApplication.kt:28-39](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:49-82](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/PlaybackService.kt:29-67]()

## Application Initialization Flow

The application follows a structured initialization sequence that sets up dependency injection, UI theming, and media services:

```mermaid
sequenceDiagram
    participant System
    participant JetStreamApplication
    participant Hilt
    participant MainActivity
    participant PlaybackService
    participant App
    
    System->>JetStreamApplication: Application.onCreate()
    JetStreamApplication->>Hilt: Initialize DI Container
    Hilt->>Hilt: Bind MovieRepositoryImpl
    
    System->>MainActivity: Activity.onCreate()
    MainActivity->>MainActivity: installSplashScreen()
    MainActivity->>MainActivity: enableEdgeToEdge()
    MainActivity->>MainActivity: tryEnableCustomHeader()
    MainActivity->>App: setContent { JetStreamTheme { App() } }
    
    System->>PlaybackService: Service.onCreate()
    PlaybackService->>PlaybackService: createExoPlayer()
    PlaybackService->>PlaybackService: MediaSession.Builder().build()
```

**Sources:** [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/JetStreamApplication.kt:28-29](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:53-82](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/PlaybackService.kt:32-37]()

## Dependency Injection Architecture

The application uses Hilt for dependency injection with a clean module structure:

| Component | Responsibility | Scope |
|-----------|---------------|-------|
| `JetStreamApplication` | Application-level DI container | Singleton |
| `MovieRepositoryModule` | Provides repository implementations | Singleton |
| `MovieRepository` | Abstract repository interface | Singleton |
| `MovieRepositoryImpl` | Concrete repository implementation | Singleton |

The dependency graph is established through the `@HiltAndroidApp` annotation on `JetStreamApplication` and the `@Module` annotation on `MovieRepositoryModule`. The module uses `@Binds` to map the concrete `MovieRepositoryImpl` to the abstract `MovieRepository` interface.

**Sources:** [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/JetStreamApplication.kt:25-39]()

## UI Framework Integration

The application integrates multiple UI frameworks to support adaptive and cross-platform experiences:

```mermaid
graph TB
    subgraph "MainActivity"
        ACTIVITY["MainActivity : ComponentActivity"]
        CONTENT["setContent{}"]
    end
    
    subgraph "Theme Layer"
        JETSTREAM_THEME["JetStreamTheme"]
        MATERIAL3["Material3"]
        COMPOSITION_LOCAL["CompositionLocalProvider"]
    end
    
    subgraph "XR Integration"
        XR_OVERRIDES["EnableXrComponentOverrides"]
        XR_API["ExperimentalMaterial3XrApi"]
    end
    
    subgraph "Core UI"
        SURFACE["Surface"]
        APP_COMPONENT["App"]
        SAFE_DRAWING["safeDrawingPadding()"]
    end
    
    ACTIVITY --> CONTENT
    CONTENT --> JETSTREAM_THEME
    JETSTREAM_THEME --> COMPOSITION_LOCAL
    COMPOSITION_LOCAL --> XR_OVERRIDES
    XR_OVERRIDES --> SURFACE
    SURFACE --> APP_COMPONENT
    APP_COMPONENT --> SAFE_DRAWING
    
    JETSTREAM_THEME -.-> MATERIAL3
    XR_OVERRIDES -.-> XR_API
```

The `MainActivity` sets up the UI framework stack with XR component overrides enabled through the `@OptIn(ExperimentalMaterial3XrApi::class)` annotation. The UI uses edge-to-edge display with safe drawing padding for modern Android design guidelines.

**Sources:** [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:42-82]()

## Media Playback Architecture

The media playback system is built around Android's Media3 framework with ExoPlayer:

```mermaid
graph LR
    subgraph "PlaybackService"
        SERVICE["PlaybackService : MediaSessionService"]
        SESSION["mediaSession: MediaSession"]
        PLAYER["player: ExoPlayer"]
    end
    
    subgraph "ExoPlayer Configuration"
        BUILDER["ExoPlayer.Builder"]
        SEEK_CONFIG["setSeekForwardIncrementMs(10000)"]
        MEDIA_SOURCE["setMediaSourceFactory()"]
        SCALING["setVideoScalingMode()"]
    end
    
    subgraph "Media Source"
        PROGRESSIVE["ProgressiveMediaSource.Factory"]
        DATA_SOURCE["DefaultDataSource.Factory"]
    end
    
    SERVICE --> SESSION
    SERVICE --> PLAYER
    SESSION --> PLAYER
    
    PLAYER --> BUILDER
    BUILDER --> SEEK_CONFIG
    BUILDER --> MEDIA_SOURCE
    BUILDER --> SCALING
    
    MEDIA_SOURCE --> PROGRESSIVE
    PROGRESSIVE --> DATA_SOURCE
```

The `PlaybackService` extends `MediaSessionService` and creates an `ExoPlayer` instance with specific configurations including 10-second seek increments, progressive media source factory, and scale-to-fit-with-cropping video scaling mode. The service manages the lifecycle of both the `MediaSession` and `ExoPlayer` instances.

**Sources:** [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/PlaybackService.kt:29-67]()

## Design Patterns

The architecture employs several key design patterns:

- **Dependency Injection**: Hilt provides compile-time dependency resolution
- **Repository Pattern**: `MovieRepository` abstracts data access
- **Service Pattern**: `PlaybackService` handles background media operations
- **Component Architecture**: Compose UI components with clear separation of concerns
- **Builder Pattern**: ExoPlayer configuration through builder pattern

The application supports advanced features including custom window headers for freeform window management, comprehensive keyboard shortcuts for navigation and media control, and XR component integration for extended reality experiences.

**Sources:** [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:92-117](), [AdaptiveJetStream/jetstream/src/main/java/com/google/jetstream/MainActivity.kt:119-263]()

---

