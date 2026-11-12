<!-- source: DeepWiki mcp.deepwiki.com · repo android/socialite · page 3 Architecture · fetched 2026-10-23 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [app/src/main/java/com/google/android/samples/socialite/README.md](app/src/main/java/com/google/android/samples/socialite/README.md)
- [app/src/main/java/com/google/android/samples/socialite/data/README.md](app/src/main/java/com/google/android/samples/socialite/data/README.md)
- [app/src/main/java/com/google/android/samples/socialite/model/README.md](app/src/main/java/com/google/android/samples/socialite/model/README.md)
- [app/src/main/java/com/google/android/samples/socialite/ui/README.md](app/src/main/java/com/google/android/samples/socialite/ui/README.md)
- [app/src/main/java/com/google/android/samples/socialite/ui/camera/README.md](app/src/main/java/com/google/android/samples/socialite/ui/camera/README.md)
- [app/src/main/java/com/google/android/samples/socialite/ui/chat/README.md](app/src/main/java/com/google/android/samples/socialite/ui/chat/README.md)
- [app/src/main/java/com/google/android/samples/socialite/ui/videoedit/README.md](app/src/main/java/com/google/android/samples/socialite/ui/videoedit/README.md)

</details>



This document explains the overall MVVM (Model-View-ViewModel) architecture of the SociaLite application, including data flow patterns and layer interactions. It provides a high-level view of how the different components and modules work together to deliver the app's functionality.

For detailed information about the navigation system implementation, see [Navigation System](#3.1). For specifics about data persistence and the Repository pattern, see [Data Layer](#3.2).

## Overall Architecture Overview

SociaLite follows a clean architecture pattern with clear separation of concerns across multiple layers. The application is structured around the MVVM architectural pattern, which promotes testability, maintainability, and clear data flow.

### High-Level Layer Structure

```mermaid
graph TB
    subgraph "UI Layer"
        MainActivity["MainActivity"]
        MainNavigation["MainNavigation"]
        CameraScreen["CameraScreen"]
        ChatScreen["ChatScreen"] 
        TimelineScreen["TimelineScreen"]
        VideoEditScreen["VideoEditScreen"]
    end
    
    subgraph "ViewModel Layer"
        CameraViewModel["CameraViewModel"]
        ChatViewModel["ChatViewModel"]
        TimelineViewModel["TimelineViewModel"] 
        VideoEditViewModel["VideoEditViewModel"]
    end
    
    subgraph "Repository Layer"
        ChatRepository["ChatRepository"]
        WidgetModelRepository["WidgetModelRepository"]
    end
    
    subgraph "Data Layer"
        AppDatabase["AppDatabase"]
        ChatDao["ChatDao"]
        MessageDao["MessageDao"]
        ContactDao["ContactDao"]
    end
    
    subgraph "Model Layer"
        Chat["Chat"]
        Message["Message"]
        Contact["Contact"]
    end
    
    MainActivity --> MainNavigation
    MainNavigation --> CameraScreen
    MainNavigation --> ChatScreen
    MainNavigation --> TimelineScreen
    MainNavigation --> VideoEditScreen
    
    CameraScreen --> CameraViewModel
    ChatScreen --> ChatViewModel
    TimelineScreen --> TimelineViewModel
    VideoEditScreen --> VideoEditViewModel
    
    CameraViewModel --> ChatRepository
    ChatViewModel --> ChatRepository
    TimelineViewModel --> ChatRepository
    VideoEditViewModel --> ChatRepository
    
    ChatRepository --> ChatDao
    ChatRepository --> MessageDao
    ChatRepository --> ContactDao
    
    ChatDao --> AppDatabase
    MessageDao --> AppDatabase
    ContactDao --> AppDatabase
    
    ChatDao --> Chat
    MessageDao --> Message
    ContactDao --> Contact
```

Sources: [app/src/main/java/com/google/android/samples/socialite/README.md:7-11](), [app/src/main/java/com/google/android/samples/socialite/ui/README.md:5-8](), [app/src/main/java/com/google/android/samples/socialite/data/README.md:5-7]()

## MVVM Pattern Implementation

The application strictly follows the MVVM architectural pattern with clear responsibilities for each component:

### Package Structure and Responsibilities

| Layer | Package | Responsibilities | Key Classes |
|-------|---------|------------------|-------------|
| **UI Layer** | `ui/` | Jetpack Compose screens, user interactions | `CameraScreen`, `ChatScreen`, `TimelineScreen` |
| **ViewModel Layer** | `ui/*/` | UI state management, business logic coordination | `CameraViewModel`, `ChatViewModel` |
| **Repository Layer** | `repository/` | Data abstraction, business logic | `ChatRepository`, `WidgetModelRepository` |
| **Data Layer** | `data/` | Data access, persistence | `AppDatabase`, DAOs |
| **Model Layer** | `model/` | Data structures, entities | `Message`, `Chat`, `Contact` |

### Component Interaction Pattern

```mermaid
graph LR
    subgraph "View Layer"
        Composables["@Composable Functions<br/>CameraScreen<br/>ChatScreen<br/>TimelineScreen"]
    end
    
    subgraph "ViewModel Layer" 
        ViewModels["ViewModels<br/>CameraViewModel<br/>ChatViewModel<br/>TimelineViewModel"]
        StateHolders["UI State<br/>LiveData/StateFlow"]
    end
    
    subgraph "Repository Layer"
        Repositories["Repositories<br/>ChatRepository<br/>WidgetModelRepository"]
        BusinessLogic["Business Logic<br/>Data Coordination"]
    end
    
    subgraph "Data Sources"
        RoomDB["Room Database<br/>AppDatabase"]
        External["External APIs<br/>Firebase AI<br/>CameraX"]
    end
    
    Composables --> ViewModels
    ViewModels --> StateHolders
    ViewModels --> Repositories
    Repositories --> BusinessLogic
    Repositories --> RoomDB
    Repositories --> External
    
    StateHolders -.-> Composables
```

Sources: [app/src/main/java/com/google/android/samples/socialite/ui/README.md:7-9](), [app/src/main/java/com/google/android/samples/socialite/data/README.md:6-7]()

## Layer Interaction and Data Flow

### Unidirectional Data Flow

The application implements unidirectional data flow where data flows down through the layers and events flow up:

1. **User Interactions**: Captured in Compose UI components
2. **Event Handling**: ViewModels process user actions
3. **Data Operations**: Repositories handle business logic and data access
4. **State Updates**: ViewModels expose updated state to UI
5. **UI Recomposition**: Compose reacts to state changes

### Core Data Flow Example

```mermaid
sequenceDiagram
    participant UI as "ChatScreen"
    participant VM as "ChatViewModel" 
    participant Repo as "ChatRepository"
    participant DAO as "MessageDao"
    participant DB as "AppDatabase"
    
    UI->>VM: "Send Message Event"
    VM->>Repo: "sendMessage(content)"
    Repo->>DAO: "insertMessage(message)"
    DAO->>DB: "SQL INSERT"
    DB-->>DAO: "Confirmation"
    DAO-->>Repo: "Message Saved"
    Repo-->>VM: "StateFlow Update"
    VM-->>UI: "UI State Change"
    UI->>UI: "Recomposition"
```

Sources: [app/src/main/java/com/google/android/samples/socialite/ui/chat/README.md:7-8](), [app/src/main/java/com/google/android/samples/socialite/data/README.md:6]()

## Module Organization

### Feature-Based Module Structure

Each major feature is organized into its own module within the `ui/` package, following a consistent structure:

```mermaid
graph TB
    subgraph "Feature Modules"
        subgraph "camera/"
            CameraScreen_kt["CameraScreen.kt"]
            CameraViewModel_kt["CameraViewModel.kt"] 
            CameraControls_kt["CameraControls.kt"]
        end
        
        subgraph "chat/"
            ChatScreen_kt["ChatScreen.kt"]
            ChatViewModel_kt["ChatViewModel.kt"]
            ChatListScreen_kt["ChatListScreen.kt"]
        end
        
        subgraph "videoedit/"
            VideoEditScreen_kt["VideoEditScreen.kt"]
            VideoEditViewModel_kt["VideoEditViewModel.kt"]
        end
        
        subgraph "timeline/"
            TimelineScreen_kt["TimelineScreen.kt"] 
            TimelineViewModel_kt["TimelineViewModel.kt"]
        end
    end
    
    subgraph "Shared Components"
        ChatRepository_shared["ChatRepository"]
        AppDatabase_shared["AppDatabase"]
        Models_shared["Model Classes"]
    end
    
    CameraViewModel_kt --> ChatRepository_shared
    ChatViewModel_kt --> ChatRepository_shared
    VideoEditViewModel_kt --> ChatRepository_shared
    TimelineViewModel_kt --> ChatRepository_shared
    
    ChatRepository_shared --> AppDatabase_shared
    AppDatabase_shared --> Models_shared
```

### Cross-Module Dependencies

| Module | Dependencies | Purpose |
|--------|-------------|---------|
| `camera/` | `ChatRepository`, CameraX APIs | Photo/video capture and effects |
| `chat/` | `ChatRepository`, Firebase AI | Messaging and AI responses |
| `videoedit/` | `ChatRepository`, Media3 Transformer | Video editing and processing |
| `timeline/` | `ChatRepository`, ExoPlayer | Media playback and timeline |

Sources: [app/src/main/java/com/google/android/samples/socialite/README.md:5-10](), [app/src/main/java/com/google/android/samples/socialite/ui/camera/README.md:5-6](), [app/src/main/java/com/google/android/samples/socialite/ui/videoedit/README.md:5-6]()

## Dependency Management

### Dependency Injection with Hilt

The application uses Hilt for dependency injection to manage object creation and provide dependencies across layers:

```mermaid
graph TB
    subgraph "Hilt Components"
        SingletonComponent["@SingletonComponent<br/>Application Scope"]
        ActivityComponent["@ActivityComponent<br/>Activity Scope"] 
        ViewModelComponent["@ViewModelComponent<br/>ViewModel Scope"]
    end
    
    subgraph "Injectable Classes"
        ChatRepository_hilt["@Singleton<br/>ChatRepository"]
        AppDatabase_hilt["@Singleton<br/>AppDatabase"]
        ViewModels_hilt["@HiltViewModel<br/>ChatViewModel<br/>CameraViewModel"]
    end
    
    subgraph "Modules"
        DatabaseModule["@Module<br/>DatabaseModule"]
        AppModule["@Module<br/>AppModule"]
    end
    
    SingletonComponent --> ChatRepository_hilt
    SingletonComponent --> AppDatabase_hilt
    ViewModelComponent --> ViewModels_hilt
    
    DatabaseModule --> AppDatabase_hilt
    AppModule --> ChatRepository_hilt
```

### Key Architectural Patterns

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| **Repository Pattern** | `ChatRepository` centralizes data access | Abstract data sources, provide clean API |
| **Observer Pattern** | `StateFlow`/`LiveData` in ViewModels | Reactive UI updates |
| **Dependency Injection** | Hilt annotations and modules | Loose coupling, testability |
| **Single Source of Truth** | Repository layer manages all data | Data consistency, conflict resolution |

Sources: [app/src/main/java/com/google/android/samples/socialite/data/README.md:6-7](), [app/src/main/java/com/google/android/samples/socialite/model/README.md:9]()

The architecture provides a solid foundation for the SociaLite application, enabling clean separation of concerns, testability, and maintainability while supporting complex features like real-time messaging, media processing, and AI integration.

---

