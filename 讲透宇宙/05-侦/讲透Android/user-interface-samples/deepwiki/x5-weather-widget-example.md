<!-- source: DeepWiki mcp.deepwiki.com · repo android/user-interface-samples · extra page Weather Widget Example · fetched 2026-10-23 -->

# Weather Widget Example

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [AppWidget/app/src/main/java/com/example/android/appwidget/glance/GlanceTheme.kt](AppWidget/app/src/main/java/com/example/android/appwidget/glance/GlanceTheme.kt)
- [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt](AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt)
- [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidgetReceiver.kt](AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidgetReceiver.kt)
- [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherInfoStateDefinition.kt](AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherInfoStateDefinition.kt)
- [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherRepo.kt](AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherRepo.kt)
- [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherWorker.kt](AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherWorker.kt)
- [AppWidget/screenshots/image-gif.gif](AppWidget/screenshots/image-gif.gif)
- [AppWidget/screenshots/run-widget-config.png](AppWidget/screenshots/run-widget-config.png)
- [AppWidget/screenshots/todo-gif.gif](AppWidget/screenshots/todo-gif.gif)
- [AppWidget/screenshots/weather-gif.gif](AppWidget/screenshots/weather-gif.gif)

</details>



This document provides a technical overview of the Weather Widget Example implemented using Glance for Android. The example demonstrates how to create a responsive, data-driven home screen widget with multiple layouts based on size, persistent state management, and background updates.

For information about other widget examples, see [Glance Widgets](#4.2) and [Image Widget Example](#4.2.2).

## Overview

The Weather Widget Example illustrates how to build a home screen widget that displays weather data with varying levels of detail based on the available space. It showcases several important capabilities of the Glance framework, including:

- Responsive layouts that adapt to different widget sizes
- Background data refreshing with WorkManager
- Custom state management using DataStore
- Handling widget lifecycle events
- Material design theming

The sample provides a simulated weather data source to avoid external dependencies, focusing on implementation patterns rather than actual weather forecasting.

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:17-42]()

## Architecture

The Weather Widget is built using a layered architecture with clear separation of concerns:

```mermaid
flowchart TD
    subgraph "UI Layer"
        A["WeatherGlanceWidget"] --> B1["WeatherThin"]
        A --> B2["WeatherSmall"] 
        A --> B3["WeatherMedium"]
        A --> B4["WeatherLarge"]
        B1 & B2 & B3 & B4 --> C1["UI Components"]
        C1 --> C11["WeatherIcon"]
        C1 --> C12["CurrentTemperature"]
        C1 --> C13["PlaceWeather"]
        C1 --> C14["HourlyForecast"]
        C1 --> C15["DailyForecast"]
    end
    
    subgraph "State Management"
        D["WeatherInfoStateDefinition"] --> D1["DataStore"]
        D --> D2["Kotlin Serialization"]
    end
    
    subgraph "Background Processing"
        E["WeatherWorker"] --> E1["WorkManager"]
        E --> E2["updateAppWidgetState()"]
    end
    
    subgraph "System Integration"
        F["WeatherGlanceWidgetReceiver"] --> F1["GlanceAppWidgetReceiver"]
        F --> E
    end
    
    subgraph "Data Layer"
        G["WeatherRepo"] --> G1["Simulated Weather Data"]
    end
    
    F -- "Widget Lifecycle" --> A
    E -- "Updates State" --> D
    A -- "Reads State" --> D
    A -- "Triggers Update" --> E
    E -- "Fetches Data" --> G
```

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:42-94](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherWorker.kt:27-69](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherInfoStateDefinition.kt:36-78](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidgetReceiver.kt:27-49]()

## Data Flow

The following diagram illustrates the data flow within the Weather Widget system:

```mermaid
sequenceDiagram
    participant System as Android System
    participant Receiver as WeatherGlanceWidgetReceiver
    participant Worker as WeatherWorker
    participant Repo as WeatherRepo
    participant State as WeatherInfoStateDefinition
    participant Widget as WeatherGlanceWidget
    participant User
    
    System->>Receiver: onEnabled()
    Receiver->>Worker: enqueue(context)
    
    loop Every 30 minutes
        Worker->>State: setWidgetState(Loading)
        Worker->>Repo: getWeatherInfo()
        Repo-->>Worker: WeatherInfo.Available
        Worker->>State: setWidgetState(Available)
        Worker->>Widget: updateAll(context)
        Widget->>State: currentState<WeatherInfo>()
        State-->>Widget: WeatherInfo
        Widget-->>User: Render UI
    end
    
    User->>Widget: Click Refresh
    Widget->>Worker: UpdateWeatherAction.onAction()
    Worker->>Worker: enqueue(force=true)
    
    System->>Receiver: onDisabled()
    Receiver->>Worker: cancel(context)
```

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherWorker.kt:71-106](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:361-370](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidgetReceiver.kt:37-49]()

## Key Components

### WeatherGlanceWidget

The `WeatherGlanceWidget` class is the main UI component that extends `GlanceAppWidget`. It defines the widget's appearance and handles user interactions.

```mermaid
classDiagram
    class GlanceAppWidget {
        <<abstract>>
        +Content() Composable
        +stateDefinition: GlanceStateDefinition
        +sizeMode: SizeMode
    }
    
    class WeatherGlanceWidget {
        -thinMode: DpSize
        -smallMode: DpSize
        -mediumMode: DpSize
        -largeMode: DpSize
        +stateDefinition: WeatherInfoStateDefinition
        +sizeMode: SizeMode
        +Content() Composable
    }
    
    class UpdateWeatherAction {
        +onAction(context, glanceId, parameters)
    }
    
    GlanceAppWidget <|-- WeatherGlanceWidget
    WeatherGlanceWidget -- UpdateWeatherAction
```

Key features:
- Defines four different size modes for responsive layout
- Uses a custom state definition (`WeatherInfoStateDefinition`)
- Provides different UI compositions based on widget size
- Handles the refresh action through `UpdateWeatherAction`

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:42-94](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:361-370]()

### Widget State

The widget's state is managed using a sealed class with three possible states:

```mermaid
classDiagram
    class WeatherInfo {
        <<sealed>>
    }
    
    class Loading {
        <<object>>
    }
    
    class Available {
        +placeName: String
        +currentData: WeatherData
        +hourlyForecast: List~WeatherData~
        +dailyForecast: List~WeatherData~
    }
    
    class Unavailable {
        +message: String
    }
    
    class WeatherData {
        +icon: Int
        +status: Int
        +temp: Int
        +maxTemp: Int
        +minTemp: Int
        +day: String
        +hour: String
    }
    
    WeatherInfo <|-- Loading
    WeatherInfo <|-- Available
    WeatherInfo <|-- Unavailable
    Available -- WeatherData
```

The state is persisted using `WeatherInfoStateDefinition`, which implements `GlanceStateDefinition` with Kotlin serialization.

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherInfoStateDefinition.kt:36-78]()

### WeatherWorker

`WeatherWorker` is responsible for background updates of the weather information. It's implemented as a `CoroutineWorker` and uses WorkManager for scheduling.

Key features:
- Enqueues periodic work requests (every 30 minutes)
- Supports force refreshing when requested by the user
- Handles data loading, success, and error states
- Updates the widget state and triggers UI updates

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherWorker.kt:27-107]()

### WeatherRepo

`WeatherRepo` is a simulated data source that provides weather information. In a real application, this would connect to a weather API.

Key features:
- Simulates network loading with delays
- Generates random weather data
- Provides the current weather, hourly forecast, and daily forecast

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherRepo.kt:25-62]()

### WeatherGlanceWidgetReceiver

`WeatherGlanceWidgetReceiver` handles the widget lifecycle events by extending `GlanceAppWidgetReceiver`.

Key features:
- Starts the worker when the first widget instance is added
- Cancels the worker when the last widget instance is removed
- Associates the widget implementation with system events

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidgetReceiver.kt:27-49]()

## Responsive Layout System

The Weather Widget supports four different size modes, each with a specific layout:

| Size Mode | Dimensions | Layout Components |
|-----------|------------|-------------------|
| Thin      | 120dp × 120dp | Current temperature only |
| Small     | 184dp × 184dp | Weather icon, place info, current temperature |
| Medium    | 260dp × 200dp | All of small + hourly forecast |
| Large     | 260dp × 280dp | All of medium + daily forecast |

```mermaid
flowchart TD
    subgraph "Responsive Layout System"
        A["WeatherGlanceWidget"]
        A -- "size == thinMode" --> B["WeatherThin"]
        A -- "size == smallMode" --> C["WeatherSmall"]
        A -- "size == mediumMode" --> D["WeatherMedium"]
        A -- "size == largeMode" --> E["WeatherLarge"]
        
        B --> B1["CurrentTemperature"]
        
        C --> C1["Row"]
        C1 --> C11["WeatherIcon"]
        C1 --> C12["PlaceWeather"]
        C --> C2["CurrentTemperature"]
        
        D --> D1["Row"]
        D1 --> D11["WeatherIcon"]
        D1 --> D12["PlaceWeather"]
        D --> D2["Row"]
        D2 --> D21["CurrentTemperature"]
        D2 --> D22["HourlyForecast"]
        
        E --> E1["Row"]
        E1 --> E11["WeatherIcon"]
        E1 --> E12["PlaceWeather"]
        E --> E2["Row"]
        E2 --> E21["CurrentTemperature"]
        E2 --> E22["HourlyForecast"]
        E --> E3["DailyForecast"]
    end
```

Each layout reuses common UI components but arranges them differently based on the available space.

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:54-58](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:74-80](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:96-146]()

## UI Components

The Weather Widget is built from several reusable UI components:

1. **WeatherIcon**: Displays the weather condition icon
2. **CurrentTemperature**: Shows current temperature with min/max values
3. **PlaceWeather**: Displays location name and weather condition
4. **HourlyForecast**: Shows hourly weather predictions
5. **DailyForecast**: Shows daily weather predictions with a scrollable list

Each component is implemented as a Composable function that accepts a `WeatherInfo.Available` object and optional modifiers.

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:172-356]()

## Background Updates and WorkManager Integration

The Weather Widget uses WorkManager to perform background updates:

```mermaid
flowchart TD
    subgraph "Background Update System"
        A["WeatherGlanceWidgetReceiver"]
        B["WorkManager"]
        C["PeriodicWorkRequest"]
        D["WeatherWorker"]
        E["WeatherRepo"]
        F["WeatherInfoStateDefinition"]
        G["WeatherGlanceWidget"]
        
        A -- "onEnabled()" --> B
        B -- "enqueueUniquePeriodicWork()" --> C
        C -- "builds" --> D
        D -- "doWork()" --> E
        E -- "getWeatherInfo()" --> D
        D -- "updateAppWidgetState()" --> F
        D -- "updateAll()" --> G
        
        A -- "onDisabled()" --> B
        B -- "cancelUniqueWork()" --> C
    end
```

Key aspects:
- Uses `PeriodicWorkRequest` for regular updates (every 30 minutes)
- Can be triggered on-demand via `UpdateWeatherAction`
- Handles retry logic with exponential backoff
- Manages the loading state by updating the widget before and after data fetching

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherWorker.kt:27-107](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidgetReceiver.kt:37-49]()

## State Management and Persistence

The widget state is managed using a custom implementation of `GlanceStateDefinition`:

```mermaid
flowchart TD
    subgraph "State Management System"
        A["WeatherInfoStateDefinition"]
        B["GlanceStateDefinition"]
        C["DataStore"]
        D["WeatherInfoSerializer"]
        E["Serializer"]
        F["Kotlin JSON"]
        
        A -- "implements" --> B
        A -- "uses" --> C
        A -- "uses" --> D
        D -- "implements" --> E
        D -- "uses" --> F
        
        G["WeatherGlanceWidget"]
        H["WeatherWorker"]
        
        G -- "reads state" --> A
        H -- "updates state" --> A
    end
```

Key aspects:
- Uses DataStore for persistent storage
- Custom serializer with Kotlin JSON serialization
- Shared state between all widget instances
- Supports three state types: Loading, Available, Unavailable

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherInfoStateDefinition.kt:36-78]()

## User Interaction Handling

The Weather Widget handles user interactions through action callbacks:

1. **Widget Refresh**: When the user taps the widget, the `UpdateWeatherAction` is triggered, which forces the worker to update data immediately.

```mermaid
sequenceDiagram
    participant User
    participant Widget as WeatherGlanceWidget
    participant Action as UpdateWeatherAction
    participant Worker as WeatherWorker
    
    User->>Widget: Tap Widget
    Widget->>Action: actionRunCallback<UpdateWeatherAction>()
    Action->>Worker: enqueue(context, force=true)
    Worker->>Worker: doWork()
    Worker-->>User: Updated Widget UI
```

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:361-370](), [AppWidget/app/src/main/java/com/example/android/appwidget/glance/weather/WeatherGlanceWidget.kt:98-104]()

## Theming Integration

The Weather Widget uses a custom theming implementation called `GlanceTheme`:

Key aspects:
- Provides a consistent color system across widget components
- Supports Material Design color roles (primary, secondary, surface, etc.)
- Allows theming to be applied at the composition level

Sources: [AppWidget/app/src/main/java/com/example/android/appwidget/glance/GlanceTheme.kt:31-126]()

## Summary

The Weather Widget Example demonstrates a comprehensive implementation of a data-driven, responsive home screen widget using the Glance framework. It showcases:

1. **Responsive UI**: Adapting layouts to different widget sizes
2. **Background Processing**: Using WorkManager for timely updates
3. **State Management**: Persisting widget state with DataStore
4. **Widget Lifecycle**: Handling system events appropriately
5. **User Interaction**: Responding to user actions
6. **Theming**: Applying consistent visual styling

This example provides a solid foundation for building other types of widgets with similar requirements.

---

