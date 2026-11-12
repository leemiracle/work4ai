<!-- source: DeepWiki mcp.deepwiki.com · repo android/media-samples · extra page MainActivity - Stopwatch Example · fetched 2026-10-23 -->

# MainActivity - Stopwatch Example

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt](PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt)
- [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/widget/MovieView.kt](PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/widget/MovieView.kt)
- [PictureInPictureKotlin/gradle.properties](PictureInPictureKotlin/gradle.properties)

</details>



## Purpose and Scope

This document covers the `MainActivity` component of the PictureInPictureKotlin sample, which demonstrates Picture-in-Picture functionality using a stopwatch application. The MainActivity showcases essential PiP features including RemoteActions for custom controls, smooth animations, and proper lifecycle management. For information about the video playback example, see [MovieActivity - Video Playback Example](#2.1.2). For testing approaches, see [Testing Infrastructure](#2.1.3).

## Overview

The `MainActivity` class serves as the primary entry point for demonstrating Picture-in-Picture mode with a functional stopwatch timer. It implements core PiP patterns including:

- Custom RemoteActions for PiP mode controls
- Smooth enter/exit animations using `trackPipAnimationHintView`
- BroadcastReceiver integration for handling PiP action events
- Dynamic UI adaptation based on PiP state
- Integration with MVVM architecture via `MainViewModel`

## Component Architecture

```mermaid
graph TB
    subgraph "MainActivity System"
        MainActivity["MainActivity"]
        MainViewModel["MainViewModel"]
        BroadcastReceiver["broadcastReceiver"]
        
        subgraph "Android Framework"
            PiPParams["PictureInPictureParams"]
            RemoteAction["RemoteAction"]
            PendingIntent["PendingIntent"]
        end
        
        subgraph "UI Components"
            MainActivityBinding["MainActivityBinding"]
            StopwatchBackground["stopwatchBackground"]
            ControlButtons["Control Buttons<br/>(clear, startOrPause, pip)"]
        end
    end
    
    MainActivity --> MainViewModel
    MainActivity --> BroadcastReceiver
    MainActivity --> MainActivityBinding
    MainActivity --> PiPParams
    PiPParams --> RemoteAction
    RemoteAction --> PendingIntent
    BroadcastReceiver --> MainViewModel
    MainActivity --> StopwatchBackground
    
    MainViewModel -.->|"Observable State"| MainActivity
    PendingIntent -.->|"Triggers"| BroadcastReceiver
```

**Sources:** [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:1-202]()

## Picture-in-Picture Integration

### PiP Configuration and Parameters

The MainActivity configures Picture-in-Picture mode through the `updatePictureInPictureParams` method, which creates a `PictureInPictureParams` object with specific settings:

```mermaid
graph TD
    subgraph "PiP Configuration Flow"
        UpdateParams["updatePictureInPictureParams()"]
        PiPBuilder["PictureInPictureParams.Builder"]
        
        subgraph "Configuration Options"
            Actions["setActions()"]
            AspectRatio["setAspectRatio(Rational(16, 9))"]
            AutoEnter["setAutoEnterEnabled(true)"]
            SeamlessResize["setSeamlessResizeEnabled(false)"]
        end
        
        subgraph "RemoteActions"
            ClearAction["createRemoteAction<br/>CONTROL_TYPE_CLEAR"]
            StartPauseAction["createRemoteAction<br/>CONTROL_TYPE_START_OR_PAUSE"]
        end
    end
    
    UpdateParams --> PiPBuilder
    PiPBuilder --> Actions
    PiPBuilder --> AspectRatio
    PiPBuilder --> AutoEnter
    PiPBuilder --> SeamlessResize
    
    Actions --> ClearAction
    Actions --> StartPauseAction
```

**Sources:** [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:134-177]()

### RemoteAction Implementation

The MainActivity defines two primary control types for PiP mode:

| Control Type | Constant | Request Code | Functionality |
|--------------|----------|--------------|---------------|
| Clear | `CONTROL_TYPE_CLEAR` | `REQUEST_CLEAR` | Resets stopwatch to 00:00 |
| Start/Pause | `CONTROL_TYPE_START_OR_PAUSE` | `REQUEST_START_OR_PAUSE` | Toggles timer state |

The `createRemoteAction` method constructs RemoteAction objects that integrate with the system PiP overlay:

**Sources:** [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:42-51](), [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:183-201]()

## BroadcastReceiver and Action Handling

### Action Processing Flow

```mermaid
sequenceDiagram
    participant PiP as "PiP System UI"
    participant BR as "broadcastReceiver"
    participant VM as "MainViewModel"
    participant UI as "MainActivity UI"
    
    PiP->>BR: "Broadcast Intent<br/>ACTION_STOPWATCH_CONTROL"
    BR->>BR: "Check intent.action"
    BR->>BR: "Extract EXTRA_CONTROL_TYPE"
    
    alt CONTROL_TYPE_START_OR_PAUSE
        BR->>VM: "viewModel.startOrPause()"
    else CONTROL_TYPE_CLEAR
        BR->>VM: "viewModel.clear()"
    end
    
    VM->>UI: "Update Observable State"
    UI->>UI: "Update UI Elements"
```

The BroadcastReceiver handles action intents from the PiP overlay and delegates to the `MainViewModel`:

**Sources:** [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:64-76](), [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:110]()

## State Management and MVVM Integration

### ViewModel Integration

The MainActivity observes state changes from `MainViewModel` using Android's LiveData pattern:

```mermaid
graph LR
    subgraph "Observable State"
        TimeData["viewModel.time"]
        StartedData["viewModel.started"]
    end
    
    subgraph "UI Updates"
        TimeText["binding.time.text"]
        StartPauseIcon["binding.startOrPause.setImageResource()"]
        PiPParams["updatePictureInPictureParams()"]
    end
    
    TimeData --> TimeText
    StartedData --> StartPauseIcon
    StartedData --> PiPParams
```

**Sources:** [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:93-99]()

## UI Behavior and Mode Transitions

### PiP Mode State Changes

The `onPictureInPictureModeChanged` callback handles UI visibility based on PiP state:

| PiP State | Control Visibility | Behavior |
|-----------|-------------------|----------|
| Entering PiP | `View.GONE` | Hide in-app buttons (clear, startOrPause) |
| Exiting PiP | `View.VISIBLE` | Restore in-app buttons |

**Sources:** [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:114-128]()

### Smooth Animation Integration

The MainActivity implements smooth PiP transitions using `trackPipAnimationHintView`:

```mermaid
graph TD
    subgraph "Animation Flow"
        LifecycleScope["lifecycleScope.launch"]
        RepeatLifecycle["repeatOnLifecycle(Lifecycle.State.STARTED)"]
        TrackHint["trackPipAnimationHintView(binding.stopwatchBackground)"]
    end
    
    LifecycleScope --> RepeatLifecycle
    RepeatLifecycle --> TrackHint
    
    subgraph "Target View"
        StopwatchBg["stopwatchBackground<br/>View for transition hint"]
    end
    
    TrackHint --> StopwatchBg
```

**Sources:** [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:101-107]()

## Activity Navigation

The MainActivity provides navigation to the video example via the "Switch Example" button:

**Sources:** [PictureInPictureKotlin/app/src/main/java/com/example/android/pictureinpicture/MainActivity.kt:88-91]()

This navigation pattern allows users to explore different PiP implementation approaches within the same sample application, demonstrating both stopwatch and video playback use cases.

---

