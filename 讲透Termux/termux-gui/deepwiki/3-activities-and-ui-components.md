<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-gui · page 3 Activities and UI Components · fetched 2026-10-26 -->

# Activities and UI Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Developing.md](Developing.md)
- [README.md](README.md)
- [app/src/main/AndroidManifest.xml](app/src/main/AndroidManifest.xml)
- [app/src/main/java/com/termux/gui/ConnectionHandler.kt](app/src/main/java/com/termux/gui/ConnectionHandler.kt)
- [app/src/main/java/com/termux/gui/GUIActivity.kt](app/src/main/java/com/termux/gui/GUIActivity.kt)
- [fastlane/metadata/android/en-US/changelogs/8.txt](fastlane/metadata/android/en-US/changelogs/8.txt)

</details>



This document provides an overview of the activity and UI component system in Termux:GUI, which allows command-line programs running in Termux to create and manage native Android user interfaces. It covers how activities are created and managed, the types of UI components available, and how they can be organized into functional interfaces.

For information about how to interact with these components using the communication protocol, see [Protocol Documentation](#2). For details on buffer systems used for graphics rendering, see [Buffer System](#4).

## Activity Architecture

In Termux:GUI, activities serve as containers for UI components. The system provides different types of activities to support various use cases and display contexts.

```mermaid
graph TD
    subgraph "Activity Types"
        GUIActivity["GUIActivity<br>(Standard)"]
        GUIActivityDialog["GUIActivityDialog<br>(Dialog Style)"]
        GUIActivityLockscreen["GUIActivityLockscreen<br>(Lock Screen)"]
    end

    subgraph "Features"
        PiP["Picture-in-Picture"]
        ThemeSupport["Theme Support"]
        ConfigChanges["Config Change Handling"]
        BackEvent["Back Button Events"]
        VolumeButtons["Volume Button Events"]
    end

    GUIActivity --> PiP
    GUIActivity --> ThemeSupport
    GUIActivity --> ConfigChanges
    GUIActivity --> BackEvent
    GUIActivity --> VolumeButtons
    
    GUIActivityLockscreen --> ThemeSupport
    GUIActivityLockscreen --> ConfigChanges
    GUIActivityLockscreen --> BackEvent
    GUIActivityLockscreen --> VolumeButtons
    GUIActivityLockscreen --> PiP
    
    GUIActivityDialog --> ThemeSupport
    GUIActivityDialog --> ConfigChanges
    GUIActivityDialog --> BackEvent
```

Sources: [app/src/main/java/com/termux/gui/GUIActivity.kt:22-237](), [app/src/main/AndroidManifest.xml:66-93]()

### Activity Types

Termux:GUI provides several specialized activity types:

1. **Standard Activities** (`GUIActivity`): Regular full-screen activities that support all UI components and features including Picture-in-Picture mode.

2. **Dialog Activities** (`GUIActivityDialog`): Appear as floating dialogs rather than full-screen activities. Useful for quick interactions or confirmations.

3. **Lockscreen Activities** (`GUIActivityLockscreen`): Can appear on the lock screen and can optionally turn on the screen.

Each activity type is declared in the AndroidManifest with specific configuration options that define its behavior.

```mermaid
graph TD
    subgraph "Activity Lifecycle Events"
        CreateActivity["Create Activity"]
        ConfigChange["Configuration Change"]
        PiPChange["PiP Mode Change"]
        UserLeave["User Leave"]
        BackButton["Back Button Press"]
        VolumeButton["Volume Button Press"]
        InsetChange["Inset Change"]
        DestroyActivity["Destroy Activity"]
    end

    subgraph "GUIActivity Listener Interface"
        OnConfig["onConfigurationChanged()"]
        OnPiP["onPictureInPictureModeChanged()"]
        OnUserLeave["onUserLeaveHint()"]
        OnBack["onBackButton()"]
        OnVolume["onVolume()"]
        OnInset["onInsetChange()"]
    end

    CreateActivity --> GUIActivityInstance["GUIActivity Instance"]
    ConfigChange --> OnConfig
    PiPChange --> OnPiP
    UserLeave --> OnUserLeave
    BackButton --> OnBack
    VolumeButton --> OnVolume
    InsetChange --> OnInset
    
    GUIActivityInstance --> DestroyActivity
```

Sources: [app/src/main/java/com/termux/gui/GUIActivity.kt:27-34](), [app/src/main/java/com/termux/gui/GUIActivity.kt:176-201]()

## UI Component System

The UI component system in Termux:GUI is based on Android's native View architecture. Components are organized in a hierarchical structure, starting with a root view in an activity.

### View Hierarchy

```mermaid
graph TD
    Activity["Activity"]
    RootView["Root View (R.id.root)"]
    Layout1["Layout Container<br>(LinearLayout/FrameLayout)"]
    Layout2["Nested Layout"]
    UIComponent1["UI Component<br>(Button/TextView)"]
    UIComponent2["UI Component<br>(EditText/ImageView)"]
    UIComponent3["UI Component<br>(WebView/Others)"]

    Activity --> RootView
    RootView --> Layout1
    RootView --> UIComponent1
    Layout1 --> Layout2
    Layout1 --> UIComponent2
    Layout2 --> UIComponent3
```

Sources: [app/src/main/java/com/termux/gui/GUIActivity.kt:45-51]()

### UI Component Types

Termux:GUI supports a wide range of Android UI components:

| Component Type | Purpose | Features |
|----------------|---------|----------|
| TextView | Display text | Text styling, size adjustment |
| Button | User interaction | Click events, text/image display |
| EditText | Text input | Text watching, keyboard types |
| ImageView | Display images | Buffer support, scaling options |
| WebView | Web content | JavaScript interaction, URL loading |
| LinearLayout | Sequential arrangement | Vertical/horizontal orientation |
| FrameLayout | Stacking views | Z-order positioning |
| Specialized views | Custom interaction | Scrolling, selection widgets |

Sources: [README.md:19-31]()

## Activity and View Management

The Termux:GUI system manages activities and views through a unique ID system. When a Termux program creates an activity or view, it assigns an ID that is used in subsequent operations to reference that specific component.

```mermaid
sequenceDiagram
    participant TermuxProgram as "Termux Program"
    participant Protocol as "Protocol Layer"
    participant ConnectionHandler as "ConnectionHandler"
    participant ViewHandler as "ViewHandler"
    participant ActivityHandler as "ActivityHandler"
    participant ViewObj as "Android View Objects"
    participant ActivityObj as "GUIActivity Objects"
    
    TermuxProgram->>Protocol: Create Activity Request
    Protocol->>ConnectionHandler: Process Request
    ConnectionHandler->>ActivityHandler: Handle Activity Creation
    ActivityHandler->>ActivityObj: Launch new GUIActivity
    ActivityObj-->>ActivityHandler: Activity Created (ID)
    ActivityHandler-->>TermuxProgram: Return Activity ID
    
    TermuxProgram->>Protocol: Create View Request (Activity ID)
    Protocol->>ConnectionHandler: Process Request
    ConnectionHandler->>ViewHandler: Handle View Creation
    ViewHandler->>ActivityObj: Find Activity by ID
    ActivityObj->>ViewObj: Create View Component
    ViewObj-->>ActivityObj: View Created
    ActivityObj-->>ViewHandler: Return View ID
    ViewHandler-->>TermuxProgram: Return View ID
```

Sources: [app/src/main/java/com/termux/gui/ConnectionHandler.kt:25-167](), [app/src/main/java/com/termux/gui/GUIActivity.kt:45-51]()

### Activity Management Features

Activities in Termux:GUI provide several management features:

1. **Theme Support**: Activities can be themed with custom colors for status bar, window background, text, and accents.

2. **Configuration Change Handling**: Activities automatically handle configuration changes like orientation shifts or locale changes, maintaining state.

3. **Picture-in-Picture Mode**: Activities can enter a compact floating mode that remains visible while using other apps.

4. **Secure Mode**: Activities can prevent screenshots and screen recording.

5. **Event Interception**: Back button and volume button events can be intercepted and handled by the Termux program.

Sources: [app/src/main/java/com/termux/gui/GUIActivity.kt:56-63](), [app/src/main/java/com/termux/gui/GUIActivity.kt:100-117](), [app/src/main/java/com/termux/gui/GUIActivity.kt:133-152]()

## Event System

The event system allows Termux programs to receive notifications about user interactions and system events. These events are sent through the event socket connection established between the Termux program and the plugin.

```mermaid
graph TD
    subgraph "Event Sources"
        ActLifecycle["Activity Lifecycle"]
        UserInput["User Input<br>(clicks, text changes)"]
        SysEvents["System Events<br>(back button, volume)"]
        ConfigEvents["Configuration Events<br>(orientation, locale)"]
    end
    
    subgraph "Event Processing Pipeline"
        Listener["GUIActivity.Listener"]
        EventQueue["Event Queue<br>(JSON or Protobuf)"]
        EventWorker["Event Worker Thread"]
    end
    
    subgraph "Client Side"
        EventSocket["Event Socket"]
        ClientProgram["Termux Program"]
    end
    
    ActLifecycle --> Listener
    UserInput --> Listener
    SysEvents --> Listener
    ConfigEvents --> Listener
    
    Listener --> EventQueue
    EventQueue --> EventWorker
    EventWorker --> EventSocket
    EventSocket --> ClientProgram
```

Sources: [app/src/main/java/com/termux/gui/ConnectionHandler.kt:48-50](), [app/src/main/java/com/termux/gui/ConnectionHandler.kt:114-133]()

The `GUIActivity.Listener` interface contains methods for various events:

- `onConfigurationChanged`: Called when device configuration changes
- `onPictureInPictureModeChanged`: Called when PiP mode changes
- `onUserLeaveHint`: Called when user navigates away
- `onBackButton`: Called when back button is pressed
- `onVolume`: Called when volume buttons are pressed
- `onInsetChange`: Called when window insets change

These events are sent to the Termux program through an event queue, which can use either JSON or Protobuf formats depending on the protocol being used.

Sources: [app/src/main/java/com/termux/gui/GUIActivity.kt:27-34]()

## Connection to Termux Programs

Termux programs connect to the Termux:GUI plugin through a Unix socket interface. The connection process includes:

1. **Connection Establishment**: Program opens two sockets (main and event)
2. **Protocol Negotiation**: Program selects JSON or Protobuf protocol
3. **Activity and View Creation**: Program sends requests to create and manipulate UI
4. **Event Handling**: Program receives events from the plugin

This system enables command-line programs to create rich user interfaces while maintaining their terminal-based nature.

Sources: [app/src/main/java/com/termux/gui/ConnectionHandler.kt:25-167]()

## Summary

The Activities and UI Components system in Termux:GUI provides a comprehensive framework for creating native Android user interfaces from Termux command-line programs. It supports various activity types, a wide range of UI components, and an event system for handling user interactions. 

This architecture bridges the gap between terminal applications and graphical interfaces, enabling Termux users to create more interactive and user-friendly applications without leaving the Termux environment.

Sources: [README.md:7-45](), [Developing.md:1-38]()

---

