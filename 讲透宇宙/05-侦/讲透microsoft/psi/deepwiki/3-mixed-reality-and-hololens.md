<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/psi · page 3 Mixed Reality and HoloLens · fetched 2026-10-26 -->

# Mixed Reality and HoloLens

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/Assets/Logo/SplashScreen.scale-100.png](Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/Assets/Logo/SplashScreen.scale-100.png)
- [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/Assets/Logo/Square150x150Logo.scale-100.png](Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/Assets/Logo/Square150x150Logo.scale-100.png)
- [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/Assets/Logo/Wide310x150Logo.scale-100.png](Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/Assets/Logo/Wide310x150Logo.scale-100.png)
- [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.cs](Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.cs)
- [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.csproj](Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.csproj)
- [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.cs](Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.cs)
- [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.csproj](Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.csproj)
- [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/ImageViewer.cs](Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/ImageViewer.cs)

</details>



The Mixed Reality and HoloLens subsystem provides comprehensive capabilities for capturing, streaming, and processing multi-modal sensor data from Microsoft HoloLens devices within the Psi framework. This system enables real-time collection of spatial computing data including head tracking, hand tracking, eye gaze, audio, RGB video, depth imaging, and scene understanding for research and application development.

For information about general mixed reality framework components, see [Mixed Reality Framework Components](#3.4). For data export and analysis tools, see [Data Export and Format Conversion](#3.2). For the Sigma task assistance application, see [Sigma Task Assistance Application](#3.3).

## System Architecture

The HoloLens integration follows a client-server architecture where a UWP application running on the HoloLens device captures sensor data and streams it over TCP to a desktop server application for persistence and analysis.

```mermaid
graph TB
    subgraph "HoloLens Device"
        CaptureApp["HoloLensCaptureApp<br/>(UWP Application)"]
        
        subgraph "Sensor Systems"
            IMU["IMU Sensors<br/>Accelerometer, Gyroscope, Magnetometer"]
            PhotoVideo["PhotoVideoCamera<br/>RGB Video Stream"]
            DepthSensors["Research Mode Cameras<br/>DepthCamera, VisibleLightCamera"]
            Tracking["Tracking Systems<br/>Head, Hands, Eyes"]
            Audio["Audio<br/>Microphone Array"]
            SceneUnderstanding["SceneUnderstanding<br/>Spatial Mapping"]
        end
        
        PipelineEngine["Pipeline Engine<br/>Stream Processing"]
        TcpWriters["TCP Writers<br/>Data Streaming"]
    end
    
    subgraph "Desktop/Server"
        CaptureServer["HoloLensCaptureServer<br/>(Console Application)"]
        RendezvousServer["RendezvousServer<br/>Connection Management"]
        PsiStore["PsiStore<br/>Data Persistence"]
        ImageViewer["ImageViewer<br/>Real-time Preview"]
    end
    
    IMU --> PipelineEngine
    PhotoVideo --> PipelineEngine
    DepthSensors --> PipelineEngine
    Tracking --> PipelineEngine
    Audio --> PipelineEngine
    SceneUnderstanding --> PipelineEngine
    
    PipelineEngine --> TcpWriters
    TcpWriters -->|"TCP Streams"| RendezvousServer
    RendezvousServer --> CaptureServer
    CaptureServer --> PsiStore
    CaptureServer --> ImageViewer
```

Sources: [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.cs:1-750](), [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.cs:1-569]()

## HoloLens Capture Application

The `HoloLensCaptureApp` class implements the client-side data collection system that runs on HoloLens devices. It constructs a comprehensive sensor pipeline and streams data to a connected server.

### Sensor Configuration

The application provides configurable access to all major HoloLens sensor systems:

| Sensor Type | Configuration Class | Key Parameters |
|-------------|-------------------|----------------|
| IMU | `Accelerometer`, `Gyroscope`, `Magnetometer` | Always enabled when `IncludeImu = true` |
| RGB Video | `PhotoVideoCamera` | Resolution: 896x504, Frame rate: 30fps |
| Depth | `DepthCamera` | Long-throw and AHAT modes available |
| Gray Cameras | `VisibleLightCamera` | Front and side cameras, JPEG/GZip encoding |
| Head Tracking | `StereoKitHeadSensor` | 20ms interval |
| Eye Tracking | `WinRTGazeSensor` | 45Hz update rate |
| Hand Tracking | `OpenXRHandsSensor` | 45Hz update rate |
| Audio | `Microphone` | 16384 sample frames |
| Scene Understanding | `SceneUnderstanding` | 60-second intervals |

Sources: [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.cs:58-110](), [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.cs:249-387]()

### Pipeline Construction and State Management

The application uses a state machine to manage the capture lifecycle:

```mermaid
stateDiagram-v2
    [*] --> WaitingToStart
    WaitingToStart --> ConstructPipeline : User clicks Start
    ConstructPipeline --> ConstructingPipeline
    ConstructingPipeline --> CalibrateCameras : Cameras need calibration
    ConstructingPipeline --> ConnectToCaptureServer : No calibration needed
    CalibrateCameras --> CalibratingCameras
    CalibratingCameras --> ConnectToCaptureServer
    ConnectToCaptureServer --> WaitingForCaptureServer
    WaitingForCaptureServer --> Capturing : Server connected
    Capturing --> StoppingPipeline : Stop requested
    StoppingPipeline --> WaitingToStart
    StoppingPipeline --> Exited : Exit requested
```

Sources: [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.cs:124-136](), [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.cs:214-397]()

### TCP Streaming Protocol

Data streams are transmitted using the Rendezvous protocol with `TcpWriter` components. Each sensor stream is assigned a dedicated TCP port starting from 30000:

```mermaid
graph LR
    subgraph "Sensor Streams"
        AccelStream["Accelerometer<br/>Port 30000"]
        GyroStream["Gyroscope<br/>Port 30001"] 
        MagStream["Magnetometer<br/>Port 30002"]
        HeadStream["Head<br/>Port 30003"]
        EyesStream["Eyes<br/>Port 30004"]
        HandsStream["Hands<br/>Port 30005"]
        AudioStream["Audio<br/>Port 30006"]
        VideoStream["VideoEncodedImageCameraView<br/>Port 30007"]
        DepthStream["DepthImageCameraView<br/>Port 30008"]
    end
    
    subgraph "TCP Writers"
        TcpWriter1["TcpWriter&lt;IMU&gt;"]
        TcpWriter2["TcpWriter&lt;CoordinateSystem&gt;"]
        TcpWriter3["TcpWriter&lt;WinRTEyes&gt;"]
        TcpWriter4["TcpWriter&lt;OpenXRHands&gt;"]
        TcpWriter5["TcpWriter&lt;AudioBuffer&gt;"]
        TcpWriter6["TcpWriter&lt;EncodedImageCameraView&gt;"]
    end
    
    AccelStream --> TcpWriter1
    HeadStream --> TcpWriter2
    EyesStream --> TcpWriter3
    HandsStream --> TcpWriter4
    AudioStream --> TcpWriter5
    VideoStream --> TcpWriter6
```

Sources: [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.cs:504-509](), [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.cs:513-647]()

## HoloLens Capture Server

The `HoloLensCaptureServer` class implements the server-side component that receives streams from HoloLens devices and persists them to `PsiStore` for analysis.

### Stream Type Mapping

The server maintains a dictionary mapping stream types to capture actions:

```mermaid
graph TD
    subgraph "Stream Type Recognition"
        TypeName["SimplifyTypeName()<br/>Stream Type Parser"]
        CaptureActions["CaptureStreamAction<br/>Dictionary"]
    end
    
    subgraph "Supported Types"
        CoordSystem["CoordinateSystem<br/>Head tracking data"]
        OpenXRHand["OpenXRHand<br/>Hand tracking data"]
        WinRTEyes["WinRTEyes<br/>Eye gaze data"]
        AudioBuffer["AudioBuffer<br/>Microphone data"]
        SharedImage["Shared&lt;Image&gt;<br/>RGB camera data"]
        EncodedImage["Shared&lt;EncodedImage&gt;<br/>Compressed images"]
        DepthImage["Shared&lt;DepthImage&gt;<br/>Depth sensor data"]
        SceneObjects["SceneObjectCollection<br/>Scene understanding"]
    end
    
    TypeName --> CaptureActions
    CaptureActions --> CoordSystem
    CaptureActions --> OpenXRHand
    CaptureActions --> WinRTEyes
    CaptureActions --> AudioBuffer
    CaptureActions --> SharedImage
    CaptureActions --> EncodedImage
    CaptureActions --> DepthImage
    CaptureActions --> SceneObjects
```

Sources: [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.cs:37-143]()

### Data Processing Pipeline

The server creates a processing pipeline for each connected HoloLens device:

```mermaid
graph TB
    subgraph "Server Pipeline"
        RendezvousServer["RendezvousServer<br/>Client connection handler"]
        RemoteClock["RemoteClockImporter<br/>Time synchronization"]
        TcpSources["TcpSource&lt;T&gt;<br/>Stream receivers"]
        Statistics["StreamStatistics<br/>Performance monitoring"]
        PsiStore["PsiStore<br/>Data persistence"]
        ImageViewer["ImageViewer<br/>Real-time preview"]
    end
    
    subgraph "Processing Functions"
        CaptureTcpStream["CaptureTcpStream&lt;T&gt;<br/>Generic stream capture"]
        ViewImageStream["ViewImageStream<br/>Image display routing"]
        ReportMessage["ReportMessage<br/>Statistics tracking"]
    end
    
    RendezvousServer --> RemoteClock
    RendezvousServer --> TcpSources
    TcpSources --> CaptureTcpStream
    CaptureTcpStream --> Statistics
    CaptureTcpStream --> PsiStore
    CaptureTcpStream --> ViewImageStream
    ViewImageStream --> ImageViewer
    Statistics --> ReportMessage
```

Sources: [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.cs:223-353](), [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.cs:355-379]()

## Configuration and Deployment

### Build Configuration

The HoloLens capture system requires specific build configurations for Universal Windows Platform (UWP) deployment:

| Component | Target Framework | Platform |
|-----------|------------------|----------|
| HoloLensCaptureApp | UWP 10.0.22621.0 | ARM |
| HoloLensCaptureServer | .NET Framework 4.7.2 | AnyCPU |

Sources: [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.csproj:14-16](), [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.csproj:5]()

### Dependencies

The system relies on several key dependencies:

- **HoloLens2ResearchMode**: Native C++ component for accessing research mode cameras
- **Microsoft.Psi.MixedReality**: Core mixed reality components and sensor interfaces  
- **Microsoft.Psi.Interop**: Cross-process communication and serialization
- **StereoKit**: Mixed reality toolkit for spatial interaction
- **MathNet.Spatial**: Spatial mathematics and coordinate transformations

Sources: [Sources/MixedReality/HoloLensCapture/HoloLensCaptureApp/HoloLensCaptureApp.csproj:92-131](), [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.csproj:36-43]()

## Performance Monitoring

The server provides comprehensive performance monitoring through the `StreamStatistics` class:

```mermaid
graph LR
    subgraph "Statistics Tracking"
        MessageCount["MessageCount<br/>Total messages received"]
        FirstMessage["FirstMessage<br/>Session start time"]
        LastMessage["LastMessage<br/>Most recent message"]
        MessagesPerSecond["MessagesPerSecond<br/>5-second sliding window"]
    end
    
    subgraph "Reporting"
        Console["Console Output<br/>Real-time statistics"]
        LogFile["CaptureLog.txt<br/>Persistent logging"]
        ServerHeartbeat["ServerHeartbeat<br/>FPS monitoring stream"]
    end
    
    MessageCount --> Console
    MessagesPerSecond --> Console
    FirstMessage --> LogFile
    LastMessage --> LogFile
    MessagesPerSecond --> ServerHeartbeat
```

Sources: [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.cs:511-566](), [Sources/MixedReality/HoloLensCapture/HoloLensCaptureServer/HoloLensCaptureServer.cs:285-346]()

---

