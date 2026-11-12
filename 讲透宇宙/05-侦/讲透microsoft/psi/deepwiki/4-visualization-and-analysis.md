<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/psi · page 4 Visualization and Analysis · fetched 2026-10-26 -->

# Visualization and Analysis

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Sources/Data/Microsoft.Psi.Data/Session.cs](Sources/Data/Microsoft.Psi.Data/Session.cs)
- [Sources/Tools/PsiStudio/Microsoft.Psi.PsiStudio/MainWindow.xaml](Sources/Tools/PsiStudio/Microsoft.Psi.PsiStudio/MainWindow.xaml)
- [Sources/Tools/PsiStudio/Microsoft.Psi.PsiStudio/MainWindowViewModel.cs](Sources/Tools/PsiStudio/Microsoft.Psi.PsiStudio/MainWindowViewModel.cs)
- [Sources/Visualization/Microsoft.Psi.Visualization.Windows/Navigation/Navigator.cs](Sources/Visualization/Microsoft.Psi.Visualization.Windows/Navigation/Navigator.cs)
- [Sources/Visualization/Microsoft.Psi.Visualization.Windows/ViewModels/DatasetViewModel.cs](Sources/Visualization/Microsoft.Psi.Visualization.Windows/ViewModels/DatasetViewModel.cs)
- [Sources/Visualization/Microsoft.Psi.Visualization.Windows/Views/VisualizationPanelView.cs](Sources/Visualization/Microsoft.Psi.Visualization.Windows/Views/VisualizationPanelView.cs)
- [Sources/Visualization/Microsoft.Psi.Visualization.Windows/VisualizationContext.cs](Sources/Visualization/Microsoft.Psi.Visualization.Windows/VisualizationContext.cs)

</details>



This document covers the visualization and analysis capabilities of the Microsoft Psi framework, primarily implemented through PsiStudio - an interactive application for exploring, visualizing, and analyzing multimodal time-series data. The visualization system provides timeline-based navigation, real-time data exploration, and flexible visualization panels for examining Psi data stores and live streams.

For information about data persistence and storage formats, see [Data Persistence and Storage](#2.2). For details about the core pipeline processing that generates the data being visualized, see [Pipeline and Message Processing](#2.1).

## System Overview

The visualization and analysis system centers around PsiStudio, a Windows-based application that provides interactive exploration of Psi datasets. The architecture consists of several key layers: data management, visualization objects, timeline navigation, and user interface components.

```mermaid
graph TB
    subgraph "PsiStudio Application"
        MainWindow["MainWindow<br/>(MainWindow.xaml)"]
        MainWindowVM["MainWindowViewModel<br/>(MainWindowViewModel.cs)"]
        
        subgraph "Core Visualization"
            VisContext["VisualizationContext<br/>(VisualizationContext.cs)"]
            VisContainer["VisualizationContainer"]
            Navigator["Navigator<br/>(Navigator.cs)"]
        end
        
        subgraph "Data Models"
            DatasetVM["DatasetViewModel<br/>(DatasetViewModel.cs)"]
            SessionVM["SessionViewModel"]
            PartitionVM["PartitionViewModel"]
        end
        
        subgraph "Visualization Components"
            VisPanels["VisualizationPanels"]
            VisObjects["VisualizationObjects"]
            StreamTree["StreamTreeNodes"]
        end
    end
    
    subgraph "Data Layer"
        DataManager["DataManager"]
        PsiStore["PsiStore"]
        Session["Session<br/>(Session.cs)"]
    end
    
    MainWindow --> MainWindowVM
    MainWindowVM --> VisContext
    VisContext --> VisContainer
    VisContext --> DatasetVM
    VisContainer --> Navigator
    VisContainer --> VisPanels
    VisPanels --> VisObjects
    DatasetVM --> SessionVM
    SessionVM --> PartitionVM
    PartitionVM --> StreamTree
    VisContext --> DataManager
    DataManager --> PsiStore
    DatasetVM --> Session
```

Sources: [Sources/Tools/PsiStudio/Microsoft.Psi.PsiStudio/MainWindow.xaml](), [Sources/Tools/PsiStudio/Microsoft.Psi.PsiStudio/MainWindowViewModel.cs](), [Sources/Visualization/Microsoft.Psi.Visualization.Windows/VisualizationContext.cs](), [Sources/Visualization/Microsoft.Psi.Visualization.Windows/Navigation/Navigator.cs]()

## Core Components

### VisualizationContext

The `VisualizationContext` serves as the central coordination point for the entire visualization system. It maintains the singleton pattern and coordinates between data loading, visualization container management, and user interactions.

```mermaid
graph LR
    subgraph "VisualizationContext Responsibilities"
        DatasetMgmt["Dataset Management<br/>DatasetViewModel"]
        LayoutMgmt["Layout Management<br/>OpenLayout()"]
        StreamVis["Stream Visualization<br/>VisualizeStream()"]
        LiveMode["Live Mode Support<br/>ToggleLiveMode()"]
        PluginMap["Plugin Management<br/>PluginMap"]
    end
    
    VisContext["VisualizationContext<br/>.Instance"] --> DatasetMgmt
    VisContext --> LayoutMgmt
    VisContext --> StreamVis
    VisContext --> LiveMode
    VisContext --> PluginMap
    
    DatasetMgmt --> LoadDataset["LoadDatasetOrStoreAsync()"]
    LayoutMgmt --> ClearLayout["ClearLayout()"]
    StreamVis --> CreateVisObj["Create VisualizationObject"]
    LiveMode --> NavigatorMode["Navigator.SetLiveCursorMode()"]
```

Sources: [Sources/Visualization/Microsoft.Psi.Visualization.Windows/VisualizationContext.cs:26-561]()

### Navigator

The `Navigator` class manages timeline navigation, cursor positioning, and playback controls. It provides three cursor modes: Manual, Playback, and Live, each with specific behaviors for data exploration.

| Property | Type | Purpose |
|----------|------|---------|
| `CursorMode` | `CursorMode` | Current navigation mode (Manual/Playback/Live) |
| `Cursor` | `DateTime` | Current cursor position in timeline |
| `DataRange` | `NavigatorRange` | Overall time range of loaded data |
| `ViewRange` | `NavigatorRange` | Currently visible time range |
| `SelectionRange` | `NavigatorRange` | User-selected time interval |
| `PlaySpeed` | `double` | Playback speed multiplier |

```mermaid
stateDiagram-v2
    [*] --> Manual
    Manual --> Playback : SetPlaybackCursorMode()
    Manual --> Live : SetLiveCursorMode()
    Playback --> Manual : SetManualCursorMode()
    Live --> Manual : SetManualCursorMode()
    
    state Manual {
        [*] --> CursorFollowsMouse
        CursorFollowsMouse --> CursorPositioning
    }
    
    state Playback {
        [*] --> AudioPlayback
        AudioPlayback --> TimerBasedAdvancement
        TimerBasedAdvancement --> RepeatMode
    }
    
    state Live {
        [*] --> FollowLiveData
        FollowLiveData --> AutoViewportUpdate
    }
```

Sources: [Sources/Visualization/Microsoft.Psi.Visualization.Windows/Navigation/Navigator.cs:25-1465]()

### Data Model Hierarchy

The visualization system organizes data through a hierarchical model that mirrors the structure of Psi datasets:

```mermaid
graph TB
    Dataset["Dataset<br/>(Session.cs)"] --> Session1["Session"]
    Dataset --> Session2["Session"]
    Dataset --> SessionN["Session..."]
    
    Session1 --> Partition1["Partition"]
    Session1 --> Partition2["Partition"]
    Session1 --> PartitionN["Partition..."]
    
    Partition1 --> Stream1["StreamTreeNode"]
    Partition1 --> Stream2["StreamTreeNode"]
    Partition1 --> StreamN["StreamTreeNode..."]
    
    subgraph "View Models"
        DatasetVM2["DatasetViewModel<br/>(DatasetViewModel.cs)"]
        SessionVM2["SessionViewModel"]
        PartitionVM2["PartitionViewModel"]
    end
    
    Dataset -.-> DatasetVM2
    Session1 -.-> SessionVM2
    Partition1 -.-> PartitionVM2
    
    Stream1 --> VisObject["VisualizationObject"]
```

Sources: [Sources/Data/Microsoft.Psi.Data/Session.cs:19-507](), [Sources/Visualization/Microsoft.Psi.Visualization.Windows/ViewModels/DatasetViewModel.cs:307-1182]()

## Visualization Pipeline

The process of visualizing data follows a well-defined pipeline from data loading to visual presentation:

```mermaid
flowchart TD
    LoadData["Load Dataset/Store<br/>OpenDatasetOrStoreAsync()"] --> CreateViewModel["Create DatasetViewModel"]
    CreateViewModel --> BuildStreamTree["Build StreamTreeNodes"]
    BuildStreamTree --> SelectStream["User Selects Stream"]
    
    SelectStream --> FindVisualizer["Find Compatible Visualizer<br/>PluginMap.GetVisualizers()"]
    FindVisualizer --> CreateVisPanel["Create/Select VisualizationPanel"]
    CreateVisPanel --> CreateVisObject["Create VisualizationObject<br/>VisualizeStream()"]
    
    CreateVisObject --> BindStream["Bind Stream<br/>StreamBinding"]
    BindStream --> UpdateSource["UpdateStreamSource()"]
    UpdateSource --> ReadData["DataManager.ReadAndPublishStreamValue()"]
    ReadData --> RenderVisualization["Render in Panel"]
    
    RenderVisualization --> NavigatorUpdate["Navigator Cursor Movement"]
    NavigatorUpdate --> ReadData
```

Sources: [Sources/Visualization/Microsoft.Psi.Visualization.Windows/VisualizationContext.cs:236-307](), [Sources/Visualization/Microsoft.Psi.Visualization.Windows/VisualizationContext.cs:472-529]()

## Timeline Navigation Features

The Navigator provides comprehensive timeline control capabilities:

### Cursor Modes and Navigation

| Mode | Behavior | Use Case |
|------|----------|----------|
| **Manual** | User-controlled cursor positioning | Interactive data exploration |
| **Playback** | Automated cursor advancement with audio sync | Data replay and presentation |
| **Live** | Follows live data streams | Real-time monitoring |

### Timing Display Options

The system supports multiple timing reference frames accessible through toolbar toggles:

- **Absolute Timing**: Wall-clock timestamps
- **Relative to Session Start**: Elapsed time from session beginning  
- **Relative to Selection Start**: Elapsed time from selection start

```mermaid
graph LR
    subgraph "Navigation Controls"
        PlayPause["Play/Pause<br/>PlayPauseFromCursorCommand"]
        ZoomControls["Zoom Controls<br/>ZoomToSelection(), ZoomToDataRange()"]
        SelectionMgmt["Selection Management<br/>MoveSelectionLeft/Right()"]
        CursorMgmt["Cursor Movement<br/>MoveCursorTo(), NudgeLeft/Right()"]
        SpeedControl["Speed Control<br/>PlaySpeed property"]
    end
    
    Navigator --> PlayPause
    Navigator --> ZoomControls  
    Navigator --> SelectionMgmt
    Navigator --> CursorMgmt
    Navigator --> SpeedControl
```

Sources: [Sources/Visualization/Microsoft.Psi.Visualization.Windows/Navigation/Navigator.cs:193-211](), [Sources/Tools/PsiStudio/Microsoft.Psi.PsiStudio/MainWindowViewModel.cs:254-600]()

## User Interface Structure

PsiStudio organizes its interface into distinct functional areas:

### Main Window Layout

```mermaid
graph TB
    subgraph "MainWindow Layout"
        MenuBar["Menu Bar<br/>File, Tools, Help"]
        ToolBar["Tool Bar<br/>Quick Actions"]
        
        subgraph "Content Area"
            DatasetsPanel["Datasets Panel<br/>TreeView"]
            VisualizationArea["Visualization Area<br/>Panels & Timeline"]
            PropertiesPanel["Properties Panel<br/>Object Inspector"]
        end
        
        StatusArea["Status & Timing Info"]
    end
    
    MenuBar --> OpenStore["Open Store Command"]
    MenuBar --> SaveDataset["Save Dataset Command"]
    ToolBar --> PlaybackControls["Playback Controls"]
    ToolBar --> NavigationControls["Navigation Controls"]
    
    DatasetsPanel --> StreamSelection["Stream Selection"]
    VisualizationArea --> TimelinePanel["Timeline Panels"]
    VisualizationArea --> InstantPanel["Instant Panels"]
    PropertiesPanel --> ObjectProperties["Selected Object Properties"]
```

Sources: [Sources/Tools/PsiStudio/Microsoft.Psi.PsiStudio/MainWindow.xaml:54-534]()

### Command Structure

The application uses the MVVM pattern with RelayCommands for user interactions:

| Command Category | Key Commands | Purpose |
|------------------|--------------|---------|
| **File Operations** | `OpenStoreCommand`, `OpenDatasetCommand`, `SaveDatasetAsCommand` | Data loading and saving |
| **Navigation** | `PlayPauseFromCursorCommand`, `ZoomToSelectionCommand`, `GoToTimeCommand` | Timeline control |
| **Layout Management** | `InsertTimelinePanelCommand`, `SaveLayoutCommand`, `ClearLayoutCommand` | Visualization setup |
| **Selection Control** | `MoveSelectionLeftCommand`, `ClearSelectionCommand` | Time interval selection |

Sources: [Sources/Tools/PsiStudio/Microsoft.Psi.PsiStudio/MainWindowViewModel.cs:254-643]()

## Data Flow and Updates

The visualization system maintains data currency through event-driven updates:

```mermaid
sequenceDiagram
    participant User
    participant Navigator
    participant DataManager
    participant VisualizationObject
    participant UI
    
    User->>Navigator: Move Cursor
    Navigator->>Navigator: Update Cursor Property
    Navigator->>DataManager: ReadAndPublishStreamValue(cursor)
    DataManager->>DataManager: Read data at timestamp
    DataManager->>VisualizationObject: Publish new data
    VisualizationObject->>VisualizationObject: Process/transform data
    VisualizationObject->>UI: Update visual representation
    UI->>User: Display updated visualization
```

Sources: [Sources/Visualization/Microsoft.Psi.Visualization.Windows/Navigation/Navigator.cs:165-170]()

This visualization and analysis system provides a comprehensive platform for exploring Psi data, supporting both offline analysis of recorded sessions and real-time monitoring of live data streams. The modular architecture allows for extensible visualization types while maintaining consistent navigation and timing semantics across all visualization modes.

---

