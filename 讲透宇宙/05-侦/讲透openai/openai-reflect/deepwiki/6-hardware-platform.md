<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-reflect · page 6 Hardware Platform · fetched 2026-10-26 -->

# Hardware Platform

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dependencies.lock](dependencies.lock)
- [main/CMakeLists.txt](main/CMakeLists.txt)
- [main/idf_component.yml](main/idf_component.yml)
- [sdkconfig.defaults](sdkconfig.defaults)

</details>



This document covers the hardware platform configuration for the Reflect AI assistant system, including the ESP32-S3 microcontroller setup, build system configuration, and external component dependencies. The system runs on M5Stack CoreS3 hardware using the ESP-IDF framework.

For detailed ESP32-S3 configuration parameters, see [ESP32-S3 Configuration](#6.1). For build system specifics, see [Build System](#6.2). For external component details, see [Dependencies](#6.3).

## Hardware Foundation

The Reflect system is built on the ESP32-S3 microcontroller using the M5Stack CoreS3 development board. This provides a complete hardware platform with integrated peripherals for audio, display, camera, and wireless communication.

### ESP32-S3 Core Configuration

The system is configured for high-performance operation with the following key specifications:

| Parameter | Configuration | Source |
|-----------|---------------|--------|
| Target Chip | `esp32s3` | [sdkconfig.defaults:1]() |
| CPU Frequency | 240 MHz | [sdkconfig.defaults:8]() |
| Flash Size | 16MB QIO mode | [sdkconfig.defaults:3-4]() |
| SPIRAM | Enabled | [sdkconfig.defaults:6]() |
| FreeRTOS Tick | 1000 Hz | [sdkconfig.defaults:9]() |
| Optimization | Performance optimized | [sdkconfig.defaults:10]() |

The configuration prioritizes performance over power consumption, with assertions disabled and compiler optimization set to performance mode.

**Sources:** [sdkconfig.defaults:1-11]()

### M5Stack CoreS3 Integration

The M5Stack CoreS3 board provides integrated peripherals that the Reflect system utilizes:

```mermaid
graph TB
    subgraph "M5Stack CoreS3 Board"
        ESP32S3["ESP32-S3<br/>240MHz Dual Core<br/>16MB Flash + SPIRAM"]
        
        subgraph "Integrated Peripherals"
            ILI9341["ILI9341 LCD Display<br/>320x240 Resolution"]
            FT5x06["FT5x06 Touch Controller<br/>Capacitive Touch"]
            Camera["ESP32-CAM Module<br/>OV2640 Sensor"]
            Codec["Audio Codec<br/>I2S Interface"]
            WiFi["WiFi Radio<br/>2.4GHz 802.11n"]
        end
    end
    
    subgraph "ESP-IDF Component Mapping"
        LCDDriver["esp_lcd_ili9341<br/>Display Driver"]
        TouchDriver["esp_lcd_touch_ft5x06<br/>Touch Input"]
        CameraDriver["esp32-camera<br/>Image Capture"]
        CodecDriver["esp_codec_dev<br/>Audio Processing"]
        WiFiDriver["esp_wifi<br/>Network Stack"]
    end
    
    ESP32S3 --> ILI9341
    ESP32S3 --> FT5x06  
    ESP32S3 --> Camera
    ESP32S3 --> Codec
    ESP32S3 --> WiFi
    
    ILI9341 --> LCDDriver
    FT5x06 --> TouchDriver
    Camera --> CameraDriver
    Codec --> CodecDriver
    WiFi --> WiFiDriver
```

**Sources:** [dependencies.lock:108-139]()

## Build System Architecture

The project uses ESP-IDF's CMake-based build system with component registration and dependency management.

### Main Component Structure

The main application component is defined with C++17 standard and specific ESP-IDF requirements:

```mermaid
graph LR
    subgraph "CMake Build Configuration"
        CMakeStd["CMAKE_CXX_STANDARD=17<br/>CMAKE_CXX_STANDARD_REQUIRED=ON"]
        Sources["GLOB SOURCES<br/>*.cpp files"]
        Component["idf_component_register"]
    end
    
    subgraph "Component Registration"
        PrivReqs["PRIV_REQUIRES<br/>spi_flash, nvs_flash<br/>esp_wifi, esp_http_server<br/>esp_lcd_touch"]
        Includes["INCLUDE_DIRS<br/>Current directory"]
        Embedded["EMBED_TXTFILES<br/>index.html"]
    end
    
    subgraph "Compiler Fixes"
        SRTPFix["sepfy__srtp<br/>-Wno-error=incompatible-pointer-types"]
    end
    
    CMakeStd --> Component
    Sources --> Component
    Component --> PrivReqs
    Component --> Includes
    Component --> Embedded
    Component --> SRTPFix
```

The build system embeds the web interface HTML file directly into the firmware binary and applies compiler warning fixes for third-party libraries.

**Sources:** [main/CMakeLists.txt:1-12]()

## Component Dependencies

The system relies on several external components managed through ESP-IDF's component manager:

### Direct Dependencies

| Component | Version | Purpose |
|-----------|---------|---------|
| `espressif/m5stack_core_s3` | ^3.0.0~3 | M5Stack hardware support |
| `sepfy/libpeer` | ^0.0.3 | WebRTC peer connection library |
| `78/esp-opus` | ^1.0.5 | Opus audio codec implementation |

### Dependency Tree

```mermaid
graph TD
    subgraph "Direct Dependencies"
        M5Stack["espressif/m5stack_core_s3<br/>v3.0.0~3"]
        LibPeer["sepfy/libpeer<br/>v0.0.3"] 
        Opus["78/esp-opus<br/>v1.0.5"]
    end
    
    subgraph "M5Stack Sub-Dependencies"
        Camera["espressif/esp32-camera<br/>v2.1.2"]
        CodecDev["espressif/esp_codec_dev<br/>v1.3.6"]
        LCD["esp_lcd_ili9341<br/>v1.2.0"]
        Touch["esp_lcd_touch_ft5x06<br/>v1.0.7"]
        LVGL["esp_lvgl_port<br/>v2.6.0"]
    end
    
    subgraph "WebRTC Sub-Dependencies"
        SRTP["sepfy/srtp<br/>v2.3.0"]
        SCTP["sepfy/usrsctp<br/>v0.9.5"]
    end
    
    subgraph "Graphics Sub-Dependencies"
        LVGLCore["lvgl/lvgl<br/>v9.3.0"]
        JPEG["espressif/esp_jpeg<br/>v1.3.1"]
    end
    
    M5Stack --> Camera
    M5Stack --> CodecDev
    M5Stack --> LCD
    M5Stack --> Touch
    M5Stack --> LVGL
    
    LibPeer --> SRTP
    LibPeer --> SCTP
    
    LVGL --> LVGLCore
    Camera --> JPEG
```

The dependency tree shows how the core functionality is built on specialized libraries for graphics, audio processing, and network communication.

**Sources:** [main/idf_component.yml:1-4](), [dependencies.lock:1-186]()

## System Integration

The hardware platform integrates multiple subsystems through ESP-IDF's component architecture:

```mermaid
graph TB
    subgraph "ESP-IDF Framework v5.5.0"
        FreeRTOS["FreeRTOS Kernel<br/>1000Hz Tick Rate"]
        NVSFlash["nvs_flash<br/>Configuration Storage"]
        WiFiStack["esp_wifi<br/>Network Stack"]
        HTTPServer["esp_http_server<br/>Web Interface"]
        SPIFlash["spi_flash<br/>16MB QIO Flash"]
    end
    
    subgraph "Hardware Abstraction"
        LCDTouch["esp_lcd_touch<br/>Touch Interface"]
        CodecInterface["Audio I2S Interface<br/>Speaker/Microphone"]
        CameraInterface["Camera SPI Interface<br/>Image Capture"]
    end
    
    subgraph "Application Layer"
        ReflectMain["Reflect Main App<br/>C++17 Sources"]
        WebRTCPeer["libpeer Integration<br/>P2P Communication"]
        OpusCodec["Opus Audio Codec<br/>Voice Processing"]
    end
    
    FreeRTOS --> ReflectMain
    NVSFlash --> ReflectMain
    WiFiStack --> ReflectMain
    HTTPServer --> ReflectMain
    SPIFlash --> ReflectMain
    LCDTouch --> ReflectMain
    
    ReflectMain --> WebRTCPeer
    ReflectMain --> OpusCodec
    
    CodecInterface --> OpusCodec
    CameraInterface --> ReflectMain
```

This architecture provides a layered approach where ESP-IDF handles hardware abstraction, while application-specific components like WebRTC and Opus codec provide specialized functionality.

**Sources:** [main/CMakeLists.txt:5-8](), [sdkconfig.defaults:1-18](), [dependencies.lock:140-143]()

---

