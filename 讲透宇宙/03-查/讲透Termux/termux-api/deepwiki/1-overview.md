<!-- source: DeepWiki mcp.deepwiki.com · repo termux/termux-api · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/github_action_build.yml](.github/workflows/github_action_build.yml)
- [.github/workflows/github_release_build.yml](.github/workflows/github_release_build.yml)
- [README.md](README.md)
- [app/src/main/AndroidManifest.xml](app/src/main/AndroidManifest.xml)
- [app/src/main/java/com/termux/api/KeepAliveService.java](app/src/main/java/com/termux/api/KeepAliveService.java)
- [app/src/main/java/com/termux/api/SocketListener.java](app/src/main/java/com/termux/api/SocketListener.java)
- [app/src/main/java/com/termux/api/TermuxAPIApplication.java](app/src/main/java/com/termux/api/TermuxAPIApplication.java)

</details>



Termux API is an Android application that bridges the gap between the Termux command-line environment and Android system capabilities. It enables Termux users to access Android device features and system services through simple command-line interfaces.

## Purpose and Functionality

The Termux API application serves as an interface layer that exposes Android system APIs to the Termux command-line environment. It allows scripts and programs running in Termux to interact with device hardware, system services, and UI elements that would otherwise be inaccessible from a terminal environment.

Key functions of Termux API include:

- Accessing device hardware (camera, sensors, location, etc.)
- Controlling Android UI elements (notifications, dialogs, toasts)
- Interacting with system services (telephony, SMS, clipboard)
- Managing files and storage
- Scheduling tasks and monitoring system events

Sources: [README.md:6-6]()

## System Architecture

The following diagram shows the main components of the Termux API system and how they interact:

```mermaid
graph TD
    TermuxApp["Termux Application"] -->|"executes"| TermuxApiBinary["termux-api binary"]
    
    subgraph "Termux:API Android App"
        SocketListener["SocketListener"] -->|"broadcasts to"| ApiReceiver["TermuxApiReceiver"]
        ApiReceiver -->|"dispatches to"| ApiImplementations["API Implementations"]
        ApiImplementations -->|"returns via"| ResultReturner["ResultReturner"]
        
        TermuxAPIApp["TermuxAPIApplication"] -->|"initializes"| SocketListener
    end
    
    TermuxApiBinary -->|"connects to"| SocketListener
    ResultReturner -->|"writes results to"| TermuxApiBinary
    TermuxApiBinary -->|"returns to"| TermuxApp
    
    ApiImplementations -->|"interacts with"| AndroidSystem["Android System Services"]
```

Sources: [app/src/main/java/com/termux/api/TermuxAPIApplication.java:33-33](), [app/src/main/java/com/termux/api/SocketListener.java:37-260]()

## Command Flow

When a user runs a Termux API command, the request flows through the system as follows:

```mermaid
sequenceDiagram
    participant User
    participant TermuxApp as "Termux App"
    participant Binary as "termux-api binary"
    participant Socket as "SocketListener"
    participant Receiver as "TermuxApiReceiver"
    participant API as "API Implementation"
    participant Android as "Android System"
    
    User->>TermuxApp: Execute command
    TermuxApp->>Binary: Run termux-api binary
    Binary->>Binary: Create sockets
    Binary->>Socket: Connect to listener
    Socket->>Socket: Parse command arguments
    Socket->>Receiver: Send broadcast intent
    Receiver->>API: Dispatch to appropriate implementation
    API->>Android: Call Android API
    Android-->>API: Return data
    API->>Binary: Return data via socket
    Binary->>TermuxApp: Display result
    TermuxApp->>User: Show output
```

Sources: [README.md:31-48](), [app/src/main/java/com/termux/api/SocketListener.java:42-248]()

## API Categories

Termux API provides access to a wide range of Android functionality through various API implementations. These can be categorized as follows:

```mermaid
graph TD
    TermuxAPI["Termux API"] --> SystemAPIs["System APIs"]
    TermuxAPI --> UIAPIs["UI APIs"]
    TermuxAPI --> HardwareAPIs["Hardware APIs"]
    TermuxAPI --> CommunicationAPIs["Communication APIs"]
    TermuxAPI --> FileAPIs["File System APIs"]
    
    SystemAPIs -->|"examples"| SysExamples["BatteryStatus, Clipboard,\nJobScheduler"]
    UIAPIs -->|"examples"| UIExamples["Dialog, Notification,\nToast, Wallpaper"]
    HardwareAPIs -->|"examples"| HWExamples["Camera, Location, Sensor,\nVibrate, Torch"]
    CommunicationAPIs -->|"examples"| CommExamples["Telephony, SMS,\nWiFi, NFC"]
    FileAPIs -->|"examples"| FileExamples["Storage, MediaScanner,\nSAF"]
```

Sources: [app/src/main/AndroidManifest.xml:101-213]()

## Permission Model

Termux API requires a comprehensive set of Android permissions to access various system features. These permissions are requested when needed and include access to:

| Permission Category | Examples |
|---------------------|----------|
| Location | Fine location, Background location |
| Hardware | Camera, Sensors, Microphone, NFC |
| Communication | Phone state, SMS, Contacts |
| Storage | External storage, Media |
| System | Battery optimization, Packages, Settings |

Sources: [app/src/main/AndroidManifest.xml:8-40]()

## Implementation Note

The Termux API application must be signed with the same key as the main Termux app for permissions to work correctly. This is because only the main Termux app is allowed to call the API methods provided by the Termux API application.

For more detailed information about the architecture and command flow of the Termux API system, see [Architecture](#2) and [Command Flow](#2.1). For information about specific API components and how they're implemented, see [API Components](#3).

Sources: [README.md:8-10]()

---

