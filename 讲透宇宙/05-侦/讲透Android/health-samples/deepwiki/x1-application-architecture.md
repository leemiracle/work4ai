<!-- source: DeepWiki mcp.deepwiki.com · repo android/health-samples · extra page Application Architecture · fetched 2026-10-23 -->

# Application Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [health-services/ExerciseSampleCompose/app/build.gradle](health-services/ExerciseSampleCompose/app/build.gradle)
- [health-services/ExerciseSampleCompose/app/src/main/AndroidManifest.xml](health-services/ExerciseSampleCompose/app/src/main/AndroidManifest.xml)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/app/MainActivity.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/app/MainActivity.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/di/MainModule.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/di/MainModule.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/di/ServiceModule.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/di/ServiceModule.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/component/FormattingUtils.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/component/FormattingUtils.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/component/HRText.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/component/HRText.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseScreen.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseScreen.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseScreenState.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseScreenState.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseViewModel.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseViewModel.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/summary/SummaryScreen.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/summary/SummaryScreen.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/service/ExerciseLogger.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/service/ExerciseLogger.kt)
- [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/service/ExerciseNotificationManager.kt](health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/service/ExerciseNotificationManager.kt)
- [health-services/ExerciseSampleCompose/app/src/test/java/com/example/exercisesamplecompose/presentation/ExerciseScreenTest.kt](health-services/ExerciseSampleCompose/app/src/test/java/com/example/exercisesamplecompose/presentation/ExerciseScreenTest.kt)

</details>



## Purpose and Scope

This document describes the application architecture of the ExerciseSampleCompose sample, focusing on the overall structural patterns, dependency management, and state flow. This covers the MVVM pattern implementation, Hilt dependency injection setup, Compose UI structure, and the interactions between architectural layers.

For details about the exercise lifecycle and foreground service implementation, see [Exercise Lifecycle Management](#2.1.2). For UI component details, see [User Interface Components](#2.1.3).

## Architectural Overview

ExerciseSampleCompose follows Android's recommended architecture patterns, implementing a layered MVVM (Model-View-ViewModel) architecture with clear separation of concerns.

```mermaid
graph TB
    subgraph "Presentation Layer"
        MA["MainActivity<br/>(FragmentActivity)"]
        NAV["NavHostController<br/>(Compose Navigation)"]
        
        subgraph "Screens (Composables)"
            PREP["PreparingScreen"]
            EX["ExerciseScreen"]
            SUM["SummaryScreen"]
        end
        
        subgraph "ViewModels (@HiltViewModel)"
            PVM["PreparingViewModel"]
            EVM["ExerciseViewModel"]
            SVM["SummaryViewModel"]
        end
    end
    
    subgraph "Data Layer"
        REPO["HealthServicesRepository"]
        STATE["ServiceState<br/>(Sealed Class)"]
    end
    
    subgraph "Service Layer"
        SVC["ExerciseService<br/>(Foreground Service)"]
        NOTIF["ExerciseNotificationManager"]
    end
    
    subgraph "Platform APIs"
        HSC["HealthServicesClient<br/>(androidx.health.services)"]
        EC["ExerciseClient"]
        MC["MeasureClient"]
    end
    
    MA --> NAV
    NAV --> PREP
    NAV --> EX
    NAV --> SUM
    
    PREP --> PVM
    EX --> EVM
    SUM --> SVM
    
    PVM --> REPO
    EVM --> REPO
    SVM --> REPO
    
    REPO --> STATE
    REPO --> SVC
    
    SVC --> HSC
    SVC --> NOTIF
    
    HSC --> EC
    HSC --> MC
```

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/app/MainActivity.kt:32-84](), [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt:35-96](), [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseViewModel.kt:29-77]()

### Architectural Layers

| Layer | Responsibility | Key Components |
|-------|---------------|----------------|
| **Presentation** | User interface and user interaction | Composable screens, ViewModels, UI state classes |
| **Data** | Business logic and data access | `HealthServicesRepository`, state models |
| **Service** | Background exercise tracking | `ExerciseService`, notification management |
| **Platform** | Android Health Services API | `HealthServicesClient`, exercise/measure clients |

## MVVM Pattern Implementation

The application implements MVVM with unidirectional data flow: user actions flow down through ViewModels to the repository, while state flows up from the repository through ViewModels to the UI.

### ViewModels

All ViewModels are annotated with `@HiltViewModel` for automatic dependency injection and implement the standard Android `ViewModel` lifecycle.

#### PreparingViewModel

Manages the pre-exercise preparation state, including capability checks, permission handling, and exercise preparation.

```mermaid
graph LR
    subgraph "PreparingViewModel"
        INIT["init block<br/>calls prepareExercise()"]
        REPO["HealthServicesRepository<br/>(injected)"]
        STATE["uiState: StateFlow<br/>&lt;PreparingScreenState&gt;"]
        
        INIT --> REPO
        REPO --> STATE
        
        START["startExercise()"]
        START --> REPO
    end
    
    subgraph "UI State Mapping"
        SVC_STATE["serviceState: Flow"]
        TRACK["isTrackingInAnotherApp"]
        CAP["hasExerciseCapabilities"]
        
        SVC_STATE --> UI_STATE["toUiState()"]
        TRACK --> UI_STATE
        CAP --> UI_STATE
        UI_STATE --> STATE
    end
    
    PERMS["permissions: List<br/>BODY_SENSORS, LOCATION,<br/>ACTIVITY_RECOGNITION,<br/>POST_NOTIFICATIONS"]
```

**Key characteristics:**
- Automatically calls `prepareExercise()` in the `init` block [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt:41-45]()
- Maps `ServiceState` to `PreparingScreenState` with additional capability checks [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt:51-67]()
- Defines required permissions as a companion object constant [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt:85-95]()
- Uses `WhileSubscribed(5.seconds)` sharing strategy for state collection [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt:65]()

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt:35-96]()

#### ExerciseViewModel

Manages active exercise state and provides operations for controlling the exercise lifecycle.

```mermaid
graph TB
    subgraph "ExerciseViewModel"
        REPO2["HealthServicesRepository"]
        
        subgraph "State Transformation"
            SVC_FLOW["serviceState: Flow"]
            MAP["map {} transformation"]
            UI_STATE2["uiState: StateFlow<br/>&lt;ExerciseScreenState&gt;"]
            
            SVC_FLOW --> MAP
            MAP --> UI_STATE2
        end
        
        subgraph "Exercise Controls"
            START2["startExercise()"]
            PAUSE["pauseExercise()"]
            RESUME["resumeExercise()"]
            END["endExercise()"]
            
            START2 --> REPO2
            PAUSE --> REPO2
            RESUME --> REPO2
            END --> REPO2
        end
    end
    
    CHECK["isExerciseInProgress()<br/>(suspend)"]
    CHECK --> REPO2
```

**Key characteristics:**
- Maps `ServiceState` to `ExerciseScreenState` with capability checks [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseViewModel.kt:35-57]()
- Provides direct control methods delegating to repository [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseViewModel.kt:62-76]()
- Uses `WhileSubscribed(3_000)` sharing strategy [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseViewModel.kt:48]()

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseViewModel.kt:29-77]()

### UI State Classes

Immutable data classes represent screen state, enabling predictable UI updates through Compose's recomposition mechanism.

#### ExerciseScreenState

```mermaid
graph LR
    subgraph "ExerciseScreenState"
        DATA["data class<br/>hasExerciseCapabilities: Boolean<br/>isTrackingAnotherExercise: Boolean<br/>serviceState: ServiceState<br/>exerciseState: ExerciseServiceState?"]
        
        COMPUTED["Computed Properties"]
        
        DATA --> COMPUTED
        
        ENDING["isEnding: Boolean"]
        ENDED["isEnded: Boolean"]
        PAUSED["isPaused: Boolean"]
        ERROR["error: String?"]
        
        COMPUTED --> ENDING
        COMPUTED --> ENDED
        COMPUTED --> PAUSED
        COMPUTED --> ERROR
        
        TO_SUMMARY["toSummary()<br/>returns SummaryScreenState"]
        DATA --> TO_SUMMARY
    end
```

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseScreenState.kt:23-53]()

### Compose UI Layer

All screens are implemented as Composable functions following the "Route" and "Screen" pattern:

| Pattern | Purpose | Example |
|---------|---------|---------|
| **Route Composable** | Hooks up ViewModel and state collection | `ExerciseRoute()` |
| **Screen Composable** | Pure UI presentation with state parameter | `ExerciseScreen(uiState, ...)` |

This separation enables easier testing and preview composition.

**Example from ExerciseScreen:**

```mermaid
graph TB
    ROUTE["ExerciseRoute<br/>(stateful)"]
    VM["hiltViewModel&lt;ExerciseViewModel&gt;()"]
    COLLECT["collectAsStateWithLifecycle()"]
    
    ROUTE --> VM
    VM --> COLLECT
    
    SCREEN["ExerciseScreen<br/>(stateless)"]
    UI_STATE["uiState: ExerciseScreenState"]
    CALLBACKS["onPauseClick, onEndClick,<br/>onResumeClick, onStartClick"]
    
    COLLECT --> UI_STATE
    UI_STATE --> SCREEN
    CALLBACKS --> SCREEN
    
    AMBIENT["AmbientAware"]
    SCREEN --> AMBIENT
    
    PAGER["HorizontalPagerScaffold"]
    AMBIENT --> PAGER
    
    CONTROLS["ExerciseControlButtons<br/>(page 0)"]
    METRICS["ExerciseMetrics<br/>(page 1)"]
    
    PAGER --> CONTROLS
    PAGER --> METRICS
```

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseScreen.kt:72-106](), [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseScreen.kt:150-202]()

## Dependency Injection with Hilt

The application uses Dagger Hilt for compile-time dependency injection, providing type-safe dependencies across all architectural layers.

### Module Structure

```mermaid
graph TB
    subgraph "MainModule<br/>@InstallIn(SingletonComponent)"
        SCOPE_MAIN["@Singleton scope"]
        
        COROUTINE["CoroutineScope<br/>SupervisorJob + Dispatchers.Default"]
        HSC_PROV["HealthServicesClient<br/>HealthServices.getClient()"]
        LOGGER["ExerciseLogger<br/>AndroidLogExerciseLogger()"]
        
        SCOPE_MAIN --> COROUTINE
        SCOPE_MAIN --> HSC_PROV
        SCOPE_MAIN --> LOGGER
    end
    
    subgraph "ServiceModule<br/>@InstallIn(ServiceComponent)"
        SCOPE_SVC["@ServiceScoped"]
        
        NOTIF_MGR["NotificationManager<br/>getSystemService()"]
        
        SCOPE_SVC --> NOTIF_MGR
    end
    
    subgraph "ViewModels<br/>@HiltViewModel"
        PVM2["PreparingViewModel"]
        EVM2["ExerciseViewModel"]
        SVM2["SummaryViewModel"]
    end
    
    subgraph "Services<br/>@AndroidEntryPoint"
        EX_SVC["ExerciseService"]
    end
    
    subgraph "Activities<br/>@AndroidEntryPoint"
        MAIN_ACT["MainActivity"]
    end
    
    HSC_PROV --> PVM2
    HSC_PROV --> EVM2
    HSC_PROV --> SVM2
    COROUTINE --> EX_SVC
    LOGGER --> EX_SVC
    
    NOTIF_MGR --> EX_SVC
```

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/di/MainModule.kt:33-55](), [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/di/ServiceModule.kt:28-40]()

### Dependency Scopes

| Scope | Lifecycle | Use Case | Components |
|-------|-----------|----------|------------|
| `@Singleton` | Application lifetime | Shared resources, API clients | `HealthServicesClient`, `CoroutineScope`, `ExerciseLogger` |
| `@ServiceScoped` | Service lifetime | Service-specific resources | `NotificationManager` |
| `@ViewModelScoped` | ViewModel lifetime | ViewModel dependencies | Automatic through `@HiltViewModel` |

### Hilt Entry Points

All entry points are annotated with `@AndroidEntryPoint` or `@HiltViewModel`:

- **MainActivity**: `@AndroidEntryPoint` [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/app/MainActivity.kt:32]()
- **ExerciseService**: Injected via service module
- **ViewModels**: `@HiltViewModel` enables automatic injection [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt:35]()

## State Management

The application uses Kotlin Flows and StateFlow for reactive state management with lifecycle-aware collection.

### State Flow Architecture

```mermaid
graph TB
    subgraph "Repository Layer"
        REPO_STATE["serviceState: MutableStateFlow<br/>&lt;ServiceState&gt;"]
    end
    
    subgraph "ViewModel Layer"
        MAP_OP["map {} operator"]
        STATE_IN["stateIn() operator"]
        
        REPO_STATE --> MAP_OP
        MAP_OP --> STATE_IN
        
        UI_FLOW["uiState: StateFlow<br/>&lt;ScreenState&gt;"]
        STATE_IN --> UI_FLOW
    end
    
    subgraph "UI Layer (Compose)"
        COLLECT["collectAsStateWithLifecycle()"]
        UI_FLOW --> COLLECT
        
        COMPOSE_STATE["by uiState.collectAsState()"]
        COLLECT --> COMPOSE_STATE
        
        RECOMPOSE["Automatic Recomposition"]
        COMPOSE_STATE --> RECOMPOSE
    end
    
    subgraph "Sharing Strategy"
        WHILE_SUB["WhileSubscribed(timeout)"]
        INIT_VAL["initialValue"]
        
        WHILE_SUB --> STATE_IN
        INIT_VAL --> STATE_IN
    end
```

### StateFlow Configuration

ViewModels use `stateIn()` to convert cold Flows into hot StateFlows with specific sharing strategies:

**PreparingViewModel:**
```kotlin
// 5 seconds timeout before stopping upstream collection
SharingStarted.WhileSubscribed(5.seconds)
```

**ExerciseViewModel:**
```kotlin
// 3 seconds timeout
SharingStarted.WhileSubscribed(3_000)
```

This configuration ensures:
1. Upstream flows stop when no collectors are active (battery optimization)
2. Brief configuration changes don't restart collection (timeout buffer)
3. Initial value is immediately available for UI rendering

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt:63-67](), [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseViewModel.kt:46-57]()

### Lifecycle-Aware Collection

UI components use `collectAsStateWithLifecycle()` to automatically manage subscriptions based on lifecycle state:

```mermaid
graph LR
    STARTED["Lifecycle.State.STARTED"]
    COLLECT["Begin Collection"]
    STOPPED["Lifecycle.State.STOPPED"]
    CANCEL["Cancel Collection"]
    
    STARTED --> COLLECT
    STOPPED --> CANCEL
    COLLECT --> UPDATE["Update Compose State"]
    UPDATE --> RECOMP["Trigger Recomposition"]
```

This ensures state collection only occurs when the UI is visible, preventing wasted resources.

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseScreen.kt:79](), [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/summary/SummaryScreen.kt:49]()

## Navigation Architecture

The application uses Jetpack Compose Navigation with Wear OS swipe-dismiss support.

```mermaid
graph TB
    subgraph "MainActivity"
        NAV_CTRL["rememberSwipeDismissableNavController()"]
        APP["ExerciseSampleApp"]
        NAV_CTRL --> APP
    end
    
    subgraph "Navigation Routes"
        PREP_ROUTE["Screen.PreparingExercise"]
        EX_ROUTE["Screen.Exercise"]
        SUM_ROUTE["Screen.Summary"]
    end
    
    subgraph "Navigation Logic"
        CHECK_ACTIVE["isExerciseInProgress()"]
        
        CHECK_ACTIVE -->|false| NAV_PREP["navigate(PreparingExercise)"]
        CHECK_ACTIVE -->|true| NAV_EX["navigate(Exercise)"]
        
        END_EX["endExercise()"]
        END_EX --> NAV_SUM["navigate(Summary)"]
        
        RESTART["onRestartClick()"]
        RESTART --> NAV_PREP
    end
    
    APP --> PREP_ROUTE
    APP --> EX_ROUTE
    APP --> SUM_ROUTE
```

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/app/MainActivity.kt:61-83]()

## Component Dependencies

### Build Configuration

The application's dependencies are defined in `app/build.gradle` using Gradle version catalogs:

| Category | Key Dependencies | Purpose |
|----------|------------------|---------|
| **Wear Compose** | `wear.compose.material`, `wear.compose.foundation` | Wear OS UI components |
| **Compose Navigation** | `compose.wear.navigation` | Screen navigation |
| **Horologist** | `horologist.compose.layout`, `horologist.health.composables` | Wear OS patterns and health UI |
| **Health Services** | `androidx.health.services` | Health Services API client |
| **Lifecycle** | `androidx.lifecycle.viewmodel`, `androidx.lifecycle.runtime.compose` | ViewModel and lifecycle integration |
| **Dependency Injection** | `dagger.hilt.android`, `hilt.navigation.compose` | Hilt DI framework |
| **Background Work** | `wear.ongoing.activity` | Foreground service notifications |
| **Testing** | `roborazzi`, `horologist.roboscreenshots` | Screenshot testing |

**Sources:** [health-services/ExerciseSampleCompose/app/build.gradle:80-141]()

### Permission Requirements

The application declares required permissions in `AndroidManifest.xml`:

```mermaid
graph TB
    subgraph "Runtime Permissions"
        BODY["BODY_SENSORS<br/>(maxSdkVersion=35)"]
        LOC["ACCESS_FINE_LOCATION"]
        ACT["ACTIVITY_RECOGNITION"]
        NOTIF["POST_NOTIFICATIONS"]
        HR["health.READ_HEART_RATE<br/>(SDK 36+)"]
    end
    
    subgraph "Service Permissions"
        FG["FOREGROUND_SERVICE"]
        FG_HEALTH["FOREGROUND_SERVICE_HEALTH"]
        FG_LOC["FOREGROUND_SERVICE_LOCATION"]
    end
    
    subgraph "Feature Requirements"
        WATCH["android.hardware.type.watch"]
    end
```

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/AndroidManifest.xml:18-33]()

## Application Entry Point

The application is initialized through `ExerciseSampleApplication`, which must be declared in the manifest to enable Hilt:

```mermaid
graph LR
    MANIFEST["AndroidManifest.xml<br/>android:name=<br/>ExerciseSampleApplication"]
    
    APP_CLASS["ExerciseSampleApplication<br/>@HiltAndroidApp"]
    
    HILT_GEN["Hilt_ExerciseSampleApplication<br/>(generated)"]
    
    DI_GRAPH["DI Component Graph"]
    
    MANIFEST --> APP_CLASS
    APP_CLASS --> HILT_GEN
    HILT_GEN --> DI_GRAPH
```

**Sources:** [health-services/ExerciseSampleCompose/app/src/main/AndroidManifest.xml:39]()

## Summary

The ExerciseSampleCompose application demonstrates a production-ready architecture with:

- **Clear layer separation**: Presentation, data, service, and platform layers
- **MVVM pattern**: ViewModels manage state, Composables render UI
- **Dependency injection**: Hilt provides compile-time safety and automatic injection
- **Reactive state management**: StateFlow with lifecycle-aware collection
- **Compose-first UI**: Modern declarative UI with Wear OS optimizations
- **Testability**: Screenshot testing and clear architectural boundaries

This architecture enables maintainability, testability, and follows Android best practices for Wear OS health applications.

**Sources:** [health-services/ExerciseSampleCompose/app/build.gradle:1-142](), [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/di/MainModule.kt:33-55](), [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/preparing/PreparingViewModel.kt:35-96](), [health-services/ExerciseSampleCompose/app/src/main/java/com/example/exercisesamplecompose/presentation/exercise/ExerciseViewModel.kt:29-77]()

---

