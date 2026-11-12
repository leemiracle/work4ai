<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/video-sdk-samples · page 3 Broadcast Sample · fetched 2026-10-26 -->

# Broadcast Sample

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [nvEncBroadcastSample/common/inc/nvEncApp.h](nvEncBroadcastSample/common/inc/nvEncApp.h)
- [nvEncBroadcastSample/common/inc/nvEncAppUtils.h](nvEncBroadcastSample/common/inc/nvEncAppUtils.h)

</details>



## Purpose and Scope

The Broadcast Sample (`nvEncBroadcastSample`) demonstrates a comprehensive NVENC-based video encoding solution designed for broadcast and professional video applications. This sample provides a more feature-rich implementation compared to the Desktop Capture Sample, offering advanced encoding capabilities, DirectX 9/11 interoperability, and configurable encoder settings suitable for live streaming and broadcast workflows.

For desktop screen capture functionality, see [Desktop Capture Sample](#2). For detailed information about the underlying NVENC hardware API, see [NVENC Hardware API](#4.1).

## Architecture Overview

The Broadcast Sample implements a layered architecture that separates graphics API concerns from encoding logic, enabling flexible integration with different DirectX versions and encoding configurations.

### High-Level Component Architecture

```mermaid
graph TB
    subgraph "Application Layer"
        nvEncApp["nvEncApp<br/>Main Application Controller"]
        AppParams["AppEncodeParams<br/>Application Configuration"]
        EncSettings["nvEncSettings<br/>Encoder Configuration"]
    end
    
    subgraph "DirectX Interop Layer"
        INvEncDxInterop["INvEncDxInterop<br/>Abstract DirectX Interface"]
        DxFactory["CNvEncDxInteropFactory<br/>Context Factory"]
        Dx9Interop["DirectX 9 Implementation"]
        Dx11Interop["DirectX 11 Implementation"]
    end
    
    subgraph "NVENC API Layer"
        EncodeApiObj["INVENC_EncodeApiObj<br/>Encoding Interface"]
        BroadcastApi["nvEncBroadcastEncodeApi<br/>Core API Implementation"]
    end
    
    nvEncApp --> AppParams
    nvEncApp --> EncSettings
    nvEncApp --> INvEncDxInterop
    nvEncApp --> EncodeApiObj
    
    DxFactory --> Dx9Interop
    DxFactory --> Dx11Interop
    INvEncDxInterop --> Dx9Interop
    INvEncDxInterop --> Dx11Interop
    
    EncodeApiObj --> BroadcastApi
    
    style nvEncApp fill:#f9f9f9
    style INvEncDxInterop fill:#e8f4f8
    style EncodeApiObj fill:#f0e8f8
```

**Sources:** [nvEncBroadcastSample/common/inc/nvEncApp.h:98-426](), [nvEncBroadcastSample/common/inc/nvEncAppUtils.h:55-74]()

### Application Initialization Flow

```mermaid
sequenceDiagram
    participant App as "nvEncApp"
    participant Factory as "CNvEncDxInteropFactory"
    participant DxInterop as "INvEncDxInterop"
    participant EncodeAPI as "INVENC_EncodeApiObj"
    
    App->>App: "GetVersionEx(&OsVer)"
    App->>App: "IsWin7() ? DX9 : DX11"
    App->>Factory: "CreateDxInterop(dxType)"
    Factory-->>App: "INvEncDxInterop instance"
    
    App->>DxInterop: "Initialize(&initParams)"
    App->>App: "NVENC_EncodeInitialize(createParams)"
    App-->>EncodeAPI: "m_pEncodeObj created"
    
    App->>App: "initializeEncoderSettings()"
    App->>EncodeAPI: "initialize(&initParams, &m_encodeSettingsParams)"
    
    Note over App: "Ready for encoding operations"
```

**Sources:** [nvEncBroadcastSample/common/inc/nvEncApp.h:135-154](), [nvEncBroadcastSample/common/inc/nvEncApp.h:296-354]()

## Core Components

### nvEncApp Class

The `nvEncApp` class serves as the main application controller, managing the entire encoding pipeline from initialization to cleanup. It handles platform detection, graphics context creation, and encoder configuration.

| Component | Type | Purpose |
|-----------|------|---------|
| `m_pGraphicsContext` | `INvEncDxInterop*` | DirectX context management |
| `m_pEncodeObj` | `INVENC_EncodeApiObj*` | NVENC API interface |
| `m_encodeSettingsParams` | `NVENC_EncodeSettingsParams` | Encoder configuration |
| `OsVer` | `OSVERSIONINFO` | Platform version detection |

**Sources:** [nvEncBroadcastSample/common/inc/nvEncApp.h:98-106]()

### Encoder Configuration Structure

The `nvEncSettings` structure provides application-level encoder configuration that maps to the lower-level NVENC API parameters:

```mermaid
graph LR
    subgraph "Application Settings"
        nvEncSettings["nvEncSettings<br/>App-level config"]
        DefaultSettings["defaultEncoderSettings<br/>Default values"]
    end
    
    subgraph "API Parameters"
        EncodeParams["NVENC_EncodeSettingsParams<br/>API-level config"]
        AdvParams["NVENC_AdvancedEncodeParams<br/>Advanced features"]
    end
    
    nvEncSettings --> EncodeParams
    DefaultSettings --> nvEncSettings
    EncodeParams --> AdvParams
    
    style nvEncSettings fill:#f9f9f9
    style EncodeParams fill:#e8f4f8
```

**Sources:** [nvEncBroadcastSample/common/inc/nvEncApp.h:64-96]()

### DirectX Interoperability Factory

The factory pattern implementation enables runtime selection between DirectX 9 and DirectX 11 based on platform capabilities:

| Method | Purpose | Platform Logic |
|--------|---------|----------------|
| `IsWin7()` | Platform detection | Windows 7 → DX9, Windows 8+ → DX11 |
| `CreateDxInterop()` | Context creation | Factory method for DX context |
| `Initialize()` | Context setup | Graphics resource initialization |

**Sources:** [nvEncBroadcastSample/common/inc/nvEncApp.h:109-117](), [nvEncBroadcastSample/common/inc/nvEncApp.h:135-154](), [nvEncBroadcastSample/common/inc/nvEncAppUtils.h:71-74]()

## Default Configuration

The sample provides sensible defaults for broadcast applications:

| Parameter | Default Value | Range/Options |
|-----------|---------------|---------------|
| Resolution | 1920x1080 | Configurable |
| Frame Rate | 30 fps (30000/1000) | Configurable numerator/denominator |
| Bitrate | 6000 Kbps | Up to 40000 Kbps |
| Profile | High | Baseline, Main, High |
| Preset | Medium | Fast, Medium, Slow, Fastest |
| Rate Control | CBR | CBR, VBR, CONSTQUAL |
| B-Frames | 2 | 0-3 |

**Sources:** [nvEncBroadcastSample/common/inc/nvEncApp.h:43-96]()

## Input Format Support

The application supports multiple input formats with automatic detection based on file extensions:

```mermaid
graph LR
    subgraph "Input Formats"
        YUV[".yuv files<br/>kBufferFormat_NV12<br/>1.5 bytes per pixel"]
        RGB[".rgb/.argb files<br/>kBufferFormat_ARGB<br/>4 bytes per pixel"]
    end
    
    subgraph "Processing"
        InitParams["NVENC_EncodeInitParams<br/>Format configuration"]
        SizeCalc["Buffer size calculation"]
    end
    
    YUV --> InitParams
    RGB --> InitParams
    InitParams --> SizeCalc
    
    style YUV fill:#e8f4f8
    style RGB fill:#f0e8f8
```

**Sources:** [nvEncBroadcastSample/common/inc/nvEncApp.h:253-271]()

## Key Differences from Desktop Capture Sample

The Broadcast Sample provides several advantages over the simpler Desktop Capture Sample:

- **Multi-API Support**: DirectX 9 and DirectX 11 compatibility through abstraction layer
- **Advanced Configuration**: Comprehensive encoder settings with presets and advanced parameters
- **File Input Support**: Reads from video files rather than live screen capture
- **Broadcast Features**: Optimized for streaming with configurable bitrates and quality settings
- **Platform Adaptation**: Automatic platform detection and appropriate API selection

For DirectX interoperability details, see [DirectX Interoperability](#3.1). For encoding API specifics, see [Broadcast Encoding API](#3.2).

---

