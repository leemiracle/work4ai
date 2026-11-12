<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/psi · page 6 Media Processing · fetched 2026-10-26 -->

# Media Processing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Sources/Imaging/Microsoft.Psi.Imaging/Image.cs](Sources/Imaging/Microsoft.Psi.Imaging/Image.cs)
- [Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCamera.cs](Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCamera.cs)
- [Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCameraConfiguration.cs](Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCameraConfiguration.cs)

</details>



## Purpose and Scope

The Media Processing system provides comprehensive capabilities for handling images, audio, and video within the Microsoft Psi framework. This system enables real-time capture, processing, transformation, and storage of multimedia data through the Psi pipeline architecture. The media processing components integrate seamlessly with the core framework's message-passing and serialization systems to support multimodal, integrative AI applications.

For detailed information about image manipulation and computer vision operations, see [Image Processing and Computer Vision](#6.1). For data persistence of media streams, see [Data Persistence and Storage](#2.2).

## Core Media Representation

### Image Class Architecture

The foundation of media processing in Psi is the `Image` class, which provides efficient representation and manipulation of image data in unmanaged memory. This design enables high-performance processing without managed memory overhead.

```mermaid
graph TB
    subgraph "Image Class Hierarchy"
        ImageBase["ImageBase<br/>Base class for all images"]
        Image["Image<br/>Standard image representation"]
        DepthImage["DepthImage<br/>Depth-specific image type"]
        EncodedImage["EncodedImage<br/>Compressed image data"]
    end
    
    subgraph "Memory Management"
        UnmanagedBuffer["UnmanagedBuffer<br/>Raw memory allocation"]
        SharedPool["Shared<T><br/>Reference counting pool"]
    end
    
    subgraph "Pixel Formats"
        BGRA32["BGRA_32bpp<br/>32-bit color with alpha"]
        BGR24["BGR_24bpp<br/>24-bit color"]
        RGB24["RGB_24bpp<br/>24-bit color"]
        Gray8["Gray_8bpp<br/>8-bit grayscale"]
        Gray16["Gray_16bpp<br/>16-bit grayscale"]
        RGBA64["RGBA_64bpp<br/>64-bit high color"]
    end
    
    ImageBase --> Image
    ImageBase --> DepthImage
    ImageBase --> EncodedImage
    Image --> UnmanagedBuffer
    Image --> SharedPool
    Image --> BGRA32
    Image --> BGR24
    Image --> RGB24
    Image --> Gray8
    Image --> Gray16
    Image --> RGBA64
```

Sources: [Sources/Imaging/Microsoft.Psi.Imaging/Image.cs:13-527]()

### Media Capture Components

The media capture system provides real-time acquisition of video and audio streams from various sources, with particular emphasis on mixed reality scenarios.

```mermaid
graph LR
    subgraph "Media Sources"
        PhotoVideoCamera["PhotoVideoCamera<br/>HoloLens PV camera"]
        MediaFrameReader["MediaFrameReader<br/>Windows Media Foundation"]
        FileSource["File sources<br/>Video/Audio files"]
    end
    
    subgraph "Stream Types"
        VideoRecord["VideoRecord<br/>Main video stream"]
        VideoPreview["VideoPreview<br/>Preview stream"]
        EncodedStreams["Encoded streams<br/>NV12/compressed data"]
        ImageStreams["Image streams<br/>BGRA converted data"]
    end
    
    subgraph "Configuration"
        StreamSettings["StreamSettings<br/>Resolution/framerate/encoding"]
        CameraConfig["PhotoVideoCameraConfiguration<br/>Multi-stream setup"]
        TriggerConfig["Triggered outputs<br/>External synchronization"]
    end
    
    subgraph "Output Data"
        ImageOutput["Shared<Image><br/>Decoded image data"]
        EncodedOutput["Shared<EncodedImage><br/>Compressed data"]
        CameraIntrinsics["ICameraIntrinsics<br/>Calibration parameters"]
        CameraPose["CoordinateSystem<br/>Spatial position"]
        CameraView["ImageCameraView<br/>Combined data"]
    end
    
    PhotoVideoCamera --> VideoRecord
    PhotoVideoCamera --> VideoPreview
    VideoRecord --> EncodedStreams
    VideoRecord --> ImageStreams
    StreamSettings --> CameraConfig
    CameraConfig --> PhotoVideoCamera
    TriggerConfig --> PhotoVideoCamera
    PhotoVideoCamera --> ImageOutput
    PhotoVideoCamera --> EncodedOutput
    PhotoVideoCamera --> CameraIntrinsics
    PhotoVideoCamera --> CameraPose
    PhotoVideoCamera --> CameraView
```

Sources: [Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCamera.cs:28-732](), [Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCameraConfiguration.cs:9-170]()

## Pipeline Integration

### Media Processing Workflow

Media processing components integrate with the Psi pipeline architecture to provide time-synchronized, message-driven processing of multimedia streams.

```mermaid
flowchart TD
    subgraph "Input Sources"
        Camera["PhotoVideoCamera<br/>Live camera capture"]
        Files["Media files<br/>FromFile() methods"]
        Network["Network streams<br/>Remote sources"]
    end
    
    subgraph "Processing Pipeline"
        Decode["Image decoding<br/>DecodeFrom()"]
        Transform["Format conversion<br/>CopyTo() operations"]
        Encode["Image encoding<br/>Encode() methods"]
        Process["Computer vision<br/>Custom operators"]
    end
    
    subgraph "Output Destinations"
        Storage["PsiStore<br/>Time-series storage"]
        Export["File export<br/>Save() methods"]
        Display["Visualization<br/>PsiStudio rendering"]
        Network2["Network output<br/>Streaming/sharing"]
    end
    
    subgraph "Supporting Components"
        Serializer["CustomSerializer<br/>Compression support"]
        MemoryPool["Memory pools<br/>Efficient allocation"]
        Sync["Stream sync<br/>Multi-modal alignment"]
    end
    
    Camera --> Decode
    Files --> Decode
    Network --> Decode
    Decode --> Transform
    Transform --> Process
    Process --> Encode
    Transform --> Storage
    Encode --> Export
    Transform --> Display
    Encode --> Network2
    Serializer --> Storage
    MemoryPool --> Transform
    Sync --> Process
```

Sources: [Sources/Imaging/Microsoft.Psi.Imaging/Image.cs:263-291](), [Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCamera.cs:552-697]()

## Supported Media Formats

### Image Formats and Conversions

The framework supports a comprehensive set of image formats with automatic conversion capabilities between different pixel representations.

| Pixel Format | Bits per Pixel | Description | Use Cases |
|--------------|---------------|-------------|-----------|
| `BGRA_32bpp` | 32 | Blue-Green-Red-Alpha | Standard color with transparency |
| `BGR_24bpp` | 24 | Blue-Green-Red | Standard color images |
| `RGB_24bpp` | 24 | Red-Green-Blue | OpenCV compatibility |
| `BGRX_32bpp` | 32 | Blue-Green-Red with padding | Memory-aligned color |
| `Gray_8bpp` | 8 | 8-bit grayscale | Efficient monochrome processing |
| `Gray_16bpp` | 16 | 16-bit grayscale | High dynamic range, depth data |
| `RGBA_64bpp` | 64 | High-precision color | Scientific imaging |

Sources: [Sources/Imaging/Microsoft.Psi.Imaging/Image.cs:336-382]()

### Encoding and Compression

Media data can be processed in both raw and compressed formats to balance quality and performance requirements.

```mermaid
graph TB
    subgraph "Raw Image Data"
        ImageClass["Image<br/>Uncompressed pixels"]
        PixelAccess["Direct pixel access<br/>GetPixel() / SetPixel()"]
        MemoryCopy["Memory operations<br/>CopyFrom() / CopyTo()"]
    end
    
    subgraph "Encoded Image Data"
        EncodedImageClass["EncodedImage<br/>Compressed data"]
        StreamEncoders["IImageToStreamEncoder<br/>Compression algorithms"]
        StreamDecoders["IImageFromStreamDecoder<br/>Decompression"]
    end
    
    subgraph "Serialization"
        CustomSerializer["Image.CustomSerializer<br/>Pipeline serialization"]
        CompressionMethod["CompressionMethod<br/>Storage optimization"]
        ConfigurableCompression["ConfigureCompression()<br/>Runtime configuration"]
    end
    
    subgraph "File Formats"
        SystemFormats["System.Drawing formats<br/>JPEG, PNG, BMP"]
        MediaFoundation["Windows Media Foundation<br/>NV12, H.264"]
        CustomFormats["Custom encodings<br/>Domain-specific formats"]
    end
    
    ImageClass --> PixelAccess
    ImageClass --> MemoryCopy
    ImageClass --> StreamEncoders
    StreamEncoders --> EncodedImageClass
    EncodedImageClass --> StreamDecoders
    StreamDecoders --> ImageClass
    ImageClass --> CustomSerializer
    CustomSerializer --> CompressionMethod
    CompressionMethod --> ConfigurableCompression
    EncodedImageClass --> SystemFormats
    EncodedImageClass --> MediaFoundation
    EncodedImageClass --> CustomFormats
```

Sources: [Sources/Imaging/Microsoft.Psi.Imaging/Image.cs:477-525](), [Sources/Imaging/Microsoft.Psi.Imaging/Image.cs:281-290]()

## Camera Capture Configuration

### Multi-Stream Configuration

The `PhotoVideoCamera` component supports simultaneous capture of multiple video streams with different resolutions and frame rates, particularly useful for mixed reality applications.

```mermaid
graph TB
    subgraph "Capture Profiles"
        Profile1["Profile 6B52B017<br/>2272x1278 @ 15/30fps"]
        Profile2["Profile CDF68AD0<br/>2284x1284 @ 24fps"]
        Profile3["Profile C5444A88<br/>1952x1100 @ 60fps"]
    end
    
    subgraph "Stream Configuration"
        VideoSettings["VideoStreamSettings<br/>Main capture stream"]
        PreviewSettings["PreviewStreamSettings<br/>Preview stream"]
        MRCapture["MixedRealityCapture<br/>Hologram overlay"]
    end
    
    subgraph "Output Options"
        OutputImage["OutputImage<br/>BGRA converted"]
        OutputEncoded["OutputEncodedImage<br/>NV12 native"]
        OutputIntrinsics["OutputCameraIntrinsics<br/>Calibration data"]
        OutputPose["OutputPose<br/>Spatial tracking"]
        OutputCameraView["OutputImageCameraView<br/>Combined data"]
    end
    
    subgraph "Triggering Modes"
        Continuous["Continuous capture<br/>Real-time streaming"]
        Triggered["Triggered outputs<br/>External synchronization"]
        TriggerFreq["TriggeredOutputFrequency<br/>Sampling rate control"]
    end
    
    Profile1 --> VideoSettings
    Profile2 --> VideoSettings
    Profile3 --> VideoSettings
    VideoSettings --> OutputImage
    VideoSettings --> OutputEncoded
    PreviewSettings --> OutputImage
    PreviewSettings --> OutputEncoded
    VideoSettings --> MRCapture
    VideoSettings --> OutputIntrinsics
    VideoSettings --> OutputPose
    VideoSettings --> OutputCameraView
    VideoSettings --> Continuous
    VideoSettings --> Triggered
    Triggered --> TriggerFreq
```

Sources: [Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCameraConfiguration.cs:52-168](), [Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCamera.cs:45-94]()

## Performance and Memory Management

### Efficient Resource Utilization

The media processing system is designed for high-performance, real-time applications with careful attention to memory allocation and processing efficiency.

| Component | Optimization Strategy | Implementation |
|-----------|----------------------|----------------|
| **Image Storage** | Unmanaged memory allocation | `UnmanagedBuffer` with direct pointer access |
| **Memory Pooling** | Shared resource pooling | `Shared<Image>` reference counting |
| **Pixel Access** | Unsafe pointer operations | Direct memory manipulation for performance |
| **Serialization** | Configurable compression | Runtime compression algorithm selection |
| **Stream Processing** | Zero-copy operations | In-place format conversions where possible |

The framework minimizes garbage collection pressure by using unmanaged memory for image data and implementing efficient copy operations that avoid unnecessary allocations.

Sources: [Sources/Imaging/Microsoft.Psi.Imaging/Image.cs:32-77](), [Sources/Imaging/Microsoft.Psi.Imaging/Image.cs:175-238](), [Sources/MixedReality/Microsoft.Psi.MixedReality.UniversalWindows/MediaCapture/PhotoVideoCamera.cs:624-695]()

---

