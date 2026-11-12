<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-reflect · page 3 WebRTC Communication · fetched 2026-10-26 -->

# WebRTC Communication

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main/webrtc.cpp](main/webrtc.cpp)

</details>



This document covers the WebRTC peer-to-peer communication system that enables real-time audio streaming and JSON command processing between the Reflect device and browser clients. The WebRTC implementation handles SDP exchange, ICE candidate negotiation, Opus audio codec streaming, and data channel communication for smart home control.

For information about the audio encoding/decoding system, see [Audio System](#2). For details about the HTTP server that facilitates the initial WebRTC handshake, see [HTTP Server](#4.1).

## WebRTC Architecture Overview

The WebRTC system establishes direct peer-to-peer connections between the Reflect device and browser clients. The device acts as a WebRTC peer that can receive audio streams and JSON commands while sending processed audio back to clients.

**WebRTC Component Architecture**
```mermaid
graph TB
    subgraph "Browser Client"
        BrowserRTC["Browser WebRTC API"]
        OpenAI["OpenAI Realtime API"]
        ClientAudio["Client Audio Stream"]
    end
    
    subgraph "Reflect Device WebRTC Layer"
        peer_connection["PeerConnection*<br/>Global Instance"]
        PeerConfiguration["PeerConfiguration<br/>CODEC_OPUS, DATA_CHANNEL_STRING"]
        peer_connection_loop["peer_connection_loop()<br/>Main Processing Loop"]
    end
    
    subgraph "WebRTC Callbacks"
        onaudiotrack["onaudiotrack<br/>→ reflect_play_audio()"]
        onicecandidate_task["onicecandidate_task<br/>SDP Answer Generation"]
        oniceconnectionstatechange["oniceconnectionstatechange<br/>Connection State Monitoring"]
        ondatachannel["ondatachannel<br/>→ handle_json()"]
    end
    
    subgraph "Audio Processing Tasks"
        reflect_send_audio_task["reflect_send_audio_task<br/>FreeRTOS Task, Core 0, Priority 7"]
        reflect_send_audio["reflect_send_audio()<br/>Opus Encoding Pipeline"]
    end
    
    subgraph "Command Processing"
        handle_json["handle_json()<br/>cJSON Parser"]
        LIFX_Commands["send_lifx_set_color()<br/>send_lifx_set_waveform()<br/>send_lifx_set_power()"]
    end
    
    %% Connections
    BrowserRTC <-->|"WebRTC P2P"| peer_connection
    peer_connection -->|"Callbacks"| onaudiotrack
    peer_connection -->|"Callbacks"| onicecandidate_task
    peer_connection -->|"Callbacks"| oniceconnectionstatechange
    peer_connection -->|"Callbacks"| ondatachannel
    
    onaudiotrack -->|"Incoming Audio"| reflect_send_audio
    oniceconnectionstatechange -->|"PEER_CONNECTION_CONNECTED"| reflect_send_audio_task
    ondatachannel -->|"JSON Commands"| handle_json
    handle_json -->|"Parse & Execute"| LIFX_Commands
    
    reflect_send_audio_task -->|"Outgoing Audio"| peer_connection
    
    OpenAI <-->|"AI Audio & Functions"| BrowserRTC
    ClientAudio -->|"Microphone Input"| BrowserRTC
```

Sources: [main/webrtc.cpp:1-111]()

## Connection Establishment Process

The WebRTC connection establishment follows the standard offer/answer model with SDP exchange. The process begins when a browser client sends an SDP offer to the device's HTTP endpoint.

**SDP Exchange and ICE Negotiation Flow**
```mermaid
sequenceDiagram
    participant Browser as "Browser Client"
    participant HTTP as "HTTP Server<br/>/connect endpoint"
    participant WebRTC as "reflect_new_peer_connection()"
    participant PeerConn as "PeerConnection*"
    participant ICE as "onicecandidate_task()"
    
    Browser->>HTTP: "POST /connect<br/>{SDP offer}"
    HTTP->>WebRTC: "reflect_new_peer_connection(offer, answer)"
    
    WebRTC->>PeerConn: "peer_connection_create(&peer_connection_config)"
    WebRTC->>PeerConn: "peer_connection_onicecandidate(onicecandidate_task)"
    WebRTC->>PeerConn: "peer_connection_set_remote_description(offer)"
    
    PeerConn->>ICE: "Generate ICE candidates"
    ICE->>WebRTC: "strncpy(answer, description, SDP_BUFFER_SIZE-1)"
    
    Note over WebRTC: "while (strlen(answer) == 0)<br/>vTaskDelay(TICK_INTERVAL)"
    
    WebRTC->>HTTP: "Return populated answer buffer"
    HTTP->>Browser: "HTTP 200 {SDP answer}"
    
    Browser->>PeerConn: "WebRTC P2P connection established"
    PeerConn->>WebRTC: "PEER_CONNECTION_CONNECTED state change"
```

The `reflect_new_peer_connection()` function creates a new peer connection with specific configuration parameters optimized for audio streaming and data channel communication.

Sources: [main/webrtc.cpp:57-93]()

## Peer Connection Configuration

The WebRTC peer connection is configured specifically for audio communication with no video support and string-based data channels for JSON command processing.

| Configuration Parameter | Value | Purpose |
|------------------------|-------|---------|
| `ice_servers` | `{}` (empty) | Local network only, no STUN/TURN servers |
| `audio_codec` | `CODEC_OPUS` | High-quality audio compression for voice |
| `video_codec` | `CODEC_NONE` | No video streaming capability |
| `datachannel` | `DATA_CHANNEL_STRING` | Text-based command transmission |
| `onaudiotrack` | Lambda function | Routes audio to `reflect_play_audio()` |
| `user_data` | `answer` buffer | SDP answer storage location |

**Peer Connection Initialization Code Structure**
```mermaid
graph LR
    PeerConfiguration["PeerConfiguration struct<br/>Line 58-69"] --> peer_connection_create["peer_connection_create()<br/>Line 71"]
    peer_connection_create --> Callbacks["Callback Registration<br/>Lines 74-88"]
    
    subgraph "Callback Functions"
        onicecandidate_task["onicecandidate_task<br/>Lines 13-15"]
        oniceconnectionstatechange["Lambda: state change<br/>Lines 76-85"]
        ondatachannel["handle_json<br/>Lines 87-88"]
    end
    
    Callbacks --> onicecandidate_task
    Callbacks --> oniceconnectionstatechange  
    Callbacks --> ondatachannel
    
    oniceconnectionstatechange -->|"PEER_CONNECTION_CONNECTED"| TaskCreation["xTaskCreateStaticPinnedToCore<br/>reflect_send_audio_task"]
```

Sources: [main/webrtc.cpp:58-88]()

## Audio Streaming Task Management

When a WebRTC connection is established, the system creates a dedicated FreeRTOS task for audio transmission. This task runs on Core 0 with high priority to ensure real-time audio streaming performance.

**Audio Task Creation and Execution**
```mermaid
graph TB
    ConnectionState["PEER_CONNECTION_CONNECTED<br/>State Change Event"]
    
    subgraph "FreeRTOS Task Creation"
        StackAllocation["heap_caps_malloc()<br/>30000 * sizeof(StackType_t)<br/>MALLOC_CAP_SPIRAM"]
        TaskCreation["xTaskCreateStaticPinnedToCore()<br/>Task: reflect_send_audio_task<br/>Stack: 30000 bytes<br/>Priority: 7<br/>Core: 0"]
    end
    
    subgraph "Audio Processing Loop"
        TaskLoop["while(1) loop"]
        TimerStart["esp_timer_get_time()<br/>start_us"]
        AudioSend["reflect_send_audio(peer_connection)"]
        TimerEnd["esp_timer_get_time()<br/>elapsed_us calculation"]
        DelayCalculation["ms_sleep = TICK_INTERVAL - (elapsed_us / 1000)"]
        TaskDelay["vTaskDelay(pdMS_TO_TICKS(ms_sleep))"]
    end
    
    ConnectionState --> StackAllocation
    StackAllocation --> TaskCreation
    TaskCreation --> TaskLoop
    
    TaskLoop --> TimerStart
    TimerStart --> AudioSend
    AudioSend --> TimerEnd
    TimerEnd --> DelayCalculation
    DelayCalculation --> TaskDelay
    TaskDelay --> TaskLoop
```

The audio task maintains precise timing with a `TICK_INTERVAL` of 15 milliseconds, measuring execution time to maintain consistent audio streaming intervals.

Sources: [main/webrtc.cpp:41-55](), [main/webrtc.cpp:76-84]()

## Data Channel JSON Command Processing

The WebRTC data channel processes JSON commands sent from browser clients to control smart home devices. Commands are parsed using the cJSON library and routed to appropriate LIFX control functions.

**JSON Command Processing Flow**
```mermaid
graph TB
    DataChannel["WebRTC Data Channel<br/>String Messages"]
    
    subgraph "handle_json() Function"
        cJSONParse["cJSON_Parse(command)<br/>Line 18"]
        EventExtract["cJSON_GetObjectItemCaseSensitive(root, 'event')<br/>Line 20"]
        
        subgraph "Command Routing"
            ColorCheck["strcmp('color', event->valuestring)<br/>Line 22"]
            WaveformCheck["strcmp('waveform', event->valuestring)<br/>Line 27"]
            PowerCheck["strcmp('power', event->valuestring)<br/>Line 32"]
        end
        
        subgraph "LIFX Function Calls"
            ColorCall["send_lifx_set_color(hue, saturation, brightness)<br/>Lines 23-26"]
            WaveformCall["send_lifx_set_waveform(hue, saturation, brightness)<br/>Lines 28-31"]
            PowerCall["send_lifx_set_power(power)<br/>Lines 33-34"]
        end
        
        Cleanup["cJSON_Delete(root)<br/>Line 37"]
    end
    
    DataChannel --> cJSONParse
    cJSONParse --> EventExtract
    EventExtract --> ColorCheck
    EventExtract --> WaveformCheck
    EventExtract --> PowerCheck
    
    ColorCheck -->|"Match"| ColorCall
    WaveformCheck -->|"Match"| WaveformCall
    PowerCheck -->|"Match"| PowerCall
    
    ColorCall --> Cleanup
    WaveformCall --> Cleanup
    PowerCall --> Cleanup
```

### Supported JSON Command Formats

The system supports three types of LIFX control commands:

**Color Command**
```json
{
  "event": "color",
  "hue": 120,
  "saturation": 100,
  "brightness": 75
}
```

**Waveform Command**
```json
{
  "event": "waveform", 
  "hue": 240,
  "saturation": 90,
  "brightness": 85
}
```

**Power Command**
```json
{
  "event": "power",
  "power": 1
}
```

Sources: [main/webrtc.cpp:17-39]()

## Connection Management Loop

The main WebRTC processing occurs in `reflect_peer_connection_loop()`, which initializes the peer library, manages connection state, and provides periodic status updates to connected devices.

**Main Processing Loop Structure**
```mermaid
graph TB
    LoopEntry["reflect_peer_connection_loop()"]
    PeerInit["peer_init()<br/>Initialize libpeer library"]
    
    subgraph "Infinite Loop (i = 0 to ∞)"
        ConnectionCheck["if (peer_connection != nullptr)<br/>Line 99"]
        PeerLoop["peer_connection_loop(peer_connection)<br/>Line 100"]
        
        PeriodicCheck["if ((i % 3000) == 0)<br/>Line 103"]
        StatusUpdate["send_lifx_set_power(peer_connection != nullptr)<br/>Line 104"]
        SpinUpdate["reflect_set_spin(peer_connection != nullptr)<br/>Line 105"]
        
        TaskDelay["vTaskDelay(pdMS_TO_TICKS(1))<br/>1ms delay"]
    end
    
    LoopEntry --> PeerInit
    PeerInit --> ConnectionCheck
    
    ConnectionCheck -->|"Connected"| PeerLoop
    ConnectionCheck --> PeriodicCheck
    PeerLoop --> PeriodicCheck
    
    PeriodicCheck -->|"Every 3000 iterations"| StatusUpdate
    PeriodicCheck --> TaskDelay
    StatusUpdate --> SpinUpdate
    SpinUpdate --> TaskDelay
    
    TaskDelay --> ConnectionCheck
```

The loop runs every millisecond and performs status updates every 3000 iterations (approximately every 3 seconds), signaling connection status to LIFX lights and the display system.

Sources: [main/webrtc.cpp:95-110]()

## Global State Management

The WebRTC system maintains minimal global state with a single peer connection instance and associated task management structures.

| Global Variable | Type | Purpose | Location |
|----------------|------|---------|----------|
| `peer_connection` | `PeerConnection*` | Active WebRTC connection instance | Line 11 |
| `send_audio_task_buffer` | `StaticTask_t` | FreeRTOS static task control block | Line 41 |
| `TICK_INTERVAL` | `#define 15` | Audio streaming timing constant | Line 10 |
| `SDP_BUFFER_SIZE` | Constant | SDP answer buffer size limit | Line 14 |

The system is designed to handle only one active peer connection at a time, with the global `peer_connection` pointer being set to `NULL` initially and updated when new connections are established.

Sources: [main/webrtc.cpp:10-11](), [main/webrtc.cpp:41]()

---

