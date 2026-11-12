<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-reflect · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



## Purpose and Scope

This document provides a high-level overview of the Reflect hardware AI assistant system, introducing its architecture, key components, and integration points. Reflect is a voice-controlled smart home device built on the ESP32-S3 platform that integrates with OpenAI's Realtime API to provide natural language interactions and smart home control capabilities.

For detailed information about specific subsystems, see: [Audio System](#2), [WebRTC Communication](#3), [Web Interface](#4), [System Architecture](#5), [Hardware Platform](#6), [Smart Home Integration](#7), and [Hardware Interfaces](#8).

## System Overview

Reflect is a stateless hardware AI assistant designed around the principle of natural communication through sound, light, and color while avoiding traditional screen-based interfaces. The device creates a local WiFi network that clients connect to, establishing peer-to-peer WebRTC connections for real-time audio streaming and command processing.

### Core Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Communicate naturally** | Sound, light and color interfaces instead of screens |
| **Phone is your key** | Device has no persistent state; all information stored on client |
| **Stateless operation** | No local data storage; operates as a communication bridge |
| **Easy modification** | Modular design for adding new features and integrations |
| **Cost-effective** | Built on affordable ESP32-S3 hardware platform |

### System Architecture Overview

```mermaid
graph TB
    subgraph "ESP32-S3 Hardware Platform"
        app_main["app_main()"]
        nvs_flash["nvs_flash_init()"]
        esp_netif["esp_netif_init()"]
        event_loop["esp_event_loop_create_default()"]
    end
    
    subgraph "Core Reflect Modules"
        reflect_display["reflect_display"]
        reflect_audio["reflect_audio"]
        reflect_wifi["reflect_wifi"]
        reflect_lifx["reflect_lifx"] 
        reflect_http["reflect_http"]
        reflect_peer["reflect_peer_connection_loop"]
    end
    
    subgraph "Runtime Components"
        wifi_ap["WiFi AP: reflect"]
        http_server["HTTP Server: 192.168.4.1"]
        webrtc_peer["WebRTC PeerConnection"]
        opus_codec["Opus Audio Codec"]
        lifx_udp["LIFX UDP Socket"]
    end
    
    subgraph "External Integration"
        openai_api["OpenAI Realtime API"]
        lifx_lights["LIFX Smart Lights"]
        web_browser["Browser Client"]
    end
    
    app_main --> nvs_flash
    nvs_flash --> esp_netif
    esp_netif --> event_loop
    
    event_loop --> reflect_display
    reflect_display --> reflect_audio
    reflect_audio --> reflect_wifi
    reflect_wifi --> reflect_lifx
    reflect_lifx --> reflect_http
    reflect_http --> reflect_peer
    
    reflect_wifi --> wifi_ap
    reflect_http --> http_server
    reflect_peer --> webrtc_peer
    reflect_audio --> opus_codec
    reflect_lifx --> lifx_udp
    
    http_server --> web_browser
    webrtc_peer --> web_browser
    web_browser --> openai_api
    lifx_udp --> lifx_lights
```

**System Initialization and Module Dependencies**

The system follows a strict initialization sequence where ESP-IDF foundation services must complete successfully before Reflect-specific modules initialize. Each module has clear dependencies and interfaces with specific hardware or network components.

Sources: [README.md:1-93]()

### Communication Flow Architecture

```mermaid
graph LR
    subgraph "Audio Pipeline"
        device_mic["Device Microphone"]
        opus_encoder["Opus Encoder"]
        webrtc_send["WebRTC Send Channel"]
        webrtc_recv["WebRTC Receive Channel"] 
        opus_decoder["Opus Decoder"]
        device_speaker["Device Speaker"]
    end
    
    subgraph "Network Layer"
        sdp_endpoint["POST /connect SDP Exchange"]
        peer_connection["PeerConnection Management"]
        http_interface["GET / HTML Interface"]
    end
    
    subgraph "Client Browser"
        html_client["HTML/JS Client"]
        browser_webrtc["Browser WebRTC"]
        openai_connection["OpenAI Realtime Connection"]
    end
    
    subgraph "Smart Home Control"
        json_commands["JSON Command Processing"]
        lifx_broadcast["UDP Broadcast Port 56700"]
        smart_lights["LIFX Color Control"]
    end
    
    device_mic --> opus_encoder
    opus_encoder --> webrtc_send
    webrtc_send --> peer_connection
    
    peer_connection --> sdp_endpoint
    sdp_endpoint --> html_client
    html_client --> browser_webrtc
    browser_webrtc --> openai_connection
    
    openai_connection --> browser_webrtc
    browser_webrtc --> html_client
    html_client --> peer_connection
    peer_connection --> webrtc_recv
    webrtc_recv --> opus_decoder
    opus_decoder --> device_speaker
    
    browser_webrtc --> json_commands
    json_commands --> lifx_broadcast
    lifx_broadcast --> smart_lights
    
    http_interface --> html_client
```

**Real-time Communication Pipeline**

The system establishes a complete audio processing pipeline from device microphone through Opus encoding, WebRTC transmission, OpenAI API processing, and response playback. Smart home control commands flow through the same WebRTC data channel as JSON messages.

Sources: [README.md:84-92]()

## Hardware Platform

Reflect targets the M5Stack CoreS3 ESP32S3 IoT Development Kit, chosen for its integrated camera, display, audio codec, and WiFi capabilities. The device operates as a WiFi access point, creating a network named `reflect` that clients connect to for interaction.

### Supported Hardware

| Component Type | Model | Purpose |
|---------------|-------|---------|
| **Microcontroller** | M5Stack CoreS3 ESP32S3 | Main processing unit with integrated peripherals |
| **Smart Lights** | LIFX Color A19 | Voice-controlled ambient lighting |

### Network Configuration

The device creates a WiFi access point with the following configuration:
- **SSID**: `reflect`
- **IP Address**: `192.168.4.1`
- **Web Interface**: HTTP server on port 80
- **Protocol**: WebRTC peer-to-peer connections

## Key Integration Points

### OpenAI Realtime API Integration
The browser client establishes a direct WebRTC connection to OpenAI's Realtime API, enabling low-latency voice conversations with function calling capabilities for smart home control.

### LIFX Smart Lighting Control
The device communicates with LIFX lights using UDP broadcasts on port 56700, supporting color changes, power control, and waveform effects based on AI-generated commands.

### Stateless Design Philosophy
All session state, user preferences, and conversation history are maintained in the browser client. The Reflect device operates as a stateless communication bridge, making it simple to deploy and maintain.

## Getting Started

To use Reflect:
1. Connect to the `reflect` WiFi network
2. Navigate to `http://192.168.4.1` in a web browser
3. Start a session to establish WebRTC connections
4. Begin voice interactions with the AI assistant

For installation and deployment procedures, see [Development and Deployment](#9).

Sources: [README.md:57-92]()

---

