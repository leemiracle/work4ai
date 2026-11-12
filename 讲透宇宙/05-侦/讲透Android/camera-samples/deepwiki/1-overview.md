<!-- source: DeepWiki mcp.deepwiki.com · repo android/camera-samples · page 1 Overview · fetched 2026-10-23 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CameraXExtensions/README.md](CameraXExtensions/README.md)
- [CameraXExtensions/screenshots/camerax_camera_extensions_screenshot.png](CameraXExtensions/screenshots/camerax_camera_extensions_screenshot.png)
- [CameraXExtensions/screenshots/camerax_extensions_architecture_diagram.png](CameraXExtensions/screenshots/camerax_extensions_architecture_diagram.png)
- [README.md](README.md)

</details>



## Purpose and Scope

This document provides a high-level introduction to the Android Camera Samples repository. This repository contains a collection of Android Studio projects that demonstrate how to use the [Camera2](https://developer.android.com/training/camera2) and [CameraX](https://developer.android.com/training/camerax) APIs in Android applications. Each sample focuses on different camera functionality, from basic preview and capture to advanced features like HDR, slow-motion video, and machine learning integration.

For detailed information about the overall architecture, see [Architecture Overview](#2). For specifics about CameraX samples, see [CameraX Samples](#3), and for Camera2 samples, see [Camera2 Samples](#4).

Sources: [README.md:1-21]()

## Repository Structure

The Camera Samples repository is organized into independent Android Studio projects, each demonstrating specific camera capabilities. The samples are divided into two main categories based on the API they use: CameraX or Camera2.

```mermaid
graph TD
    subgraph "Camera Samples Repository"
        direction TB
        
        subgraph "CameraX API Samples"
            direction LR
            CXBasic["CameraXBasic<br>(Basic preview & capture)"]
            CXExt["CameraXExtensions<br>(Manufacturer extensions)"]
            CXVideo["CameraXVideo<br>(Video recording)"]
            CXML["CameraX-MLKit<br>(QR code scanning)"]
            CXAdv["CameraXAdvanced<br>(TFLite integration)"]
        end
        
        subgraph "Camera2 API Samples"
            direction LR
            C2Basic["Camera2Basic<br>(JPEG/RAW/DEPTH capture)"]
            C2Video["Camera2Video<br>(Video recording)"]
            C2Ext["Camera2Extensions<br>(Manufacturer extensions)"]
            C2Slow["Camera2SlowMotion<br>(High-speed recording)"]
            HDRView["HdrViewfinder<br>(HDR preview with RenderScript)"]
        end
    end
```

Sources: [README.md:1-21]()

## Samples Overview

The repository contains multiple samples that demonstrate various aspects of Android camera development, from basic functionality to advanced features.

| Sample | API | Description |
|--------|-----|-------------|
| CameraXBasic | CameraX | Demonstrates basic camera preview, image capture, and simple image analysis |
| CameraXAdvanced | CameraX | Shows integration with TensorFlow Lite and other advanced features |
| CameraXVideo | CameraX | Demonstrates video capture capabilities using CameraX VideoCapture API |
| CameraX-MLKit | CameraX | Shows how to use CameraX's MlKitAnalyzer to build a QR-code scanner |
| CameraXExtensions | CameraX | Demonstrates manufacturer-specific extensions (Auto, Bokeh, Face Retouch, HDR, Night) |
| Camera2Basic | Camera2 | Shows capturing of JPEG, RAW, and DEPTH images directly from the camera sensor |
| Camera2Video | Camera2 | Demonstrates video recording using Camera2 API and MediaRecorder |
| Camera2Extensions | Camera2 | Shows Camera2 extension live preview and still capture |
| Camera2SlowMotion | Camera2 | Demonstrates high-speed video recording in a constrained camera capture session |
| HdrViewfinder | Camera2 | Shows use of RenderScript to display a live HDR feed from camera frames |

Sources: [README.md:7-21](), [CameraXExtensions/README.md:5-18]()

## API Relationship

The following diagram illustrates the relationship between the two camera APIs demonstrated in this repository and how they interact with the Android camera framework.

```mermaid
graph TD
    subgraph "Android Camera Framework"
        Camera2API["Camera2 API<br>(Lower-level API)"]
        CameraXAPI["CameraX API<br>(Higher-level API)"]
        HW["Camera Hardware"]
    end
    
    subgraph "Sample Applications"
        CXSamples["CameraX Samples"]
        C2Samples["Camera2 Samples"]
    end
    
    CameraXAPI -- "Built on top of" --> Camera2API
    Camera2API -- "Interfaces with" --> HW
    
    CXSamples -- "Uses" --> CameraXAPI
    C2Samples -- "Uses" --> Camera2API
    
    style CameraXAPI fill:#f5f5f5,stroke:#333,stroke-width:1px
    style Camera2API fill:#f5f5f5,stroke:#333,stroke-width:1px
    style CXSamples fill:#f5f5f5,stroke:#333,stroke-width:1px
    style C2Samples fill:#f5f5f5,stroke:#333,stroke-width:1px
    style HW fill:#f5f5f5,stroke:#333,stroke-width:1px
```

Sources: [README.md:3-5]()

## Key Features

The repository demonstrates various camera functionalities across different samples:

1. **Basic Camera Operations**
   - Camera preview
   - Still image capture
   - Permission handling

2. **Advanced Camera Features**
   - Video recording (standard and slow-motion)
   - RAW image capture
   - Depth imaging
   - HDR processing

3. **Manufacturer Extensions**
   - Bokeh effect
   - Night mode
   - HDR
   - Face retouch
   - Auto mode

4. **Integration with Other Technologies**
   - ML Kit for QR code scanning
   - TensorFlow Lite
   - RenderScript for image processing

5. **Architecture Patterns**
   - MVVM architecture (particularly in CameraXExtensions)
   - Single Activity, Multiple Fragments design
   - Pipeline pattern for video processing

Sources: [README.md:7-21](), [CameraXExtensions/README.md:32-36]()

## Developer Benefits

This repository provides several benefits for Android developers working with camera functionality:

1. **Learning Resources**: Ready-to-use examples that demonstrate camera implementation best practices
2. **Code Reference**: Working code that can be used as a reference for specific camera features
3. **Architecture Guidance**: Examples of well-structured camera applications using modern Android architecture patterns
4. **Feature Exploration**: Demonstration of advanced camera capabilities that may not be obvious from the API documentation alone
5. **Cross-API Comparison**: The ability to compare implementation approaches between CameraX and Camera2

The samples are designed to be built and run independently, allowing developers to focus on specific camera features that meet their application needs.

Sources: [README.md:1-21](), [CameraXExtensions/README.md:9-18]()

---

