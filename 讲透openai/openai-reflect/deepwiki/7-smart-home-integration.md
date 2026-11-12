<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-reflect · page 7 Smart Home Integration · fetched 2026-10-26 -->

# Smart Home Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [main/lifx.cpp](main/lifx.cpp)

</details>



This document covers the LIFX smart lighting integration system that enables voice-controlled smart home functionality in the Reflect AI assistant. The system implements the LIFX LAN protocol to control smart lights through UDP broadcast messages, providing real-time lighting control in response to AI function calls.

For information about the WebRTC communication system that delivers AI function calls to the device, see [WebRTC Communication](#3). For details about the web interface that processes AI responses, see [Browser Client](#4.2).

## LIFX Protocol Implementation

The Reflect device implements a subset of the LIFX LAN protocol to control smart lights on the local network. The protocol uses structured UDP packets with specific headers and payloads for different lighting commands.

### Packet Structure Architecture

```mermaid
graph TB
    subgraph "LIFX Protocol Stack"
        Header["lifx_header_t<br/>36 bytes<br/>Protocol 1024"]
        ColorCmd["lifx_set_color_t<br/>Header + 13 bytes<br/>Type 102"]
        WaveformCmd["lifx_set_waveform_t<br/>Header + 21 bytes<br/>Type 103"]  
        PowerCmd["lifx_set_power_t<br/>Header + 6 bytes<br/>Type 21"]
    end
    
    subgraph "Header Fields"
        Size["size: uint16_t"]
        Protocol["protocol: 12 bits = 1024"]
        Flags["addressable, tagged, origin"]
        Source["source: 0x12345678"]
        Target["target[8]: broadcast zeros"]
        Type["type: command identifier"]
    end
    
    subgraph "Command Payloads"
        ColorData["hue, saturation, brightness<br/>kelvin, duration"]
        WaveformData["period, cycles, waveform<br/>transient, skew_ratio"]
        PowerData["level: 65535/0<br/>duration: 5000ms"]
    end
    
    Header --> ColorCmd
    Header --> WaveformCmd
    Header --> PowerCmd
    
    Header --> Size
    Header --> Protocol
    Header --> Flags
    Header --> Source
    Header --> Target
    Header --> Type
    
    ColorCmd --> ColorData
    WaveformCmd --> WaveformData
    PowerCmd --> PowerData
```

**Sources:** [main/lifx.cpp:11-62]()

## Network Communication Architecture

The LIFX integration uses UDP broadcast communication to reach all LIFX devices on the local network. The system establishes a socket with broadcast permissions and sends commands to the network broadcast address.

```mermaid
graph LR
    subgraph "Reflect Device Network"
        Socket["lifx_socket<br/>SOCK_DGRAM"]
        Address["lifx_addr<br/>192.168.4.255:56700"]
        Broadcast["SO_BROADCAST<br/>enabled"]
    end
    
    subgraph "Command Functions"
        SetColor["send_lifx_set_color()<br/>hue, sat, brightness"]
        SetWaveform["send_lifx_set_waveform()<br/>effect parameters"]
        SetPower["send_lifx_set_power()<br/>on/off state"]
        SendPkt["send_lifx_pkt()<br/>UDP sendto()"]
    end
    
    subgraph "LIFX Device Network"
        Light1["LIFX Light A<br/>Port 56700"]
        Light2["LIFX Light B<br/>Port 56700"]  
        Light3["LIFX Light C<br/>Port 56700"]
    end
    
    Socket --> Address
    Socket --> Broadcast
    
    SetColor --> SendPkt
    SetWaveform --> SendPkt
    SetPower --> SendPkt
    
    SendPkt --> Address
    Address --> Light1
    Address --> Light2
    Address --> Light3
```

**Sources:** [main/lifx.cpp:64-70](), [main/lifx.cpp:151-166]()

## Command Processing Flow

The smart home integration receives JSON commands through the WebRTC data channel and translates them into LIFX protocol packets. Each command type has specific parameter handling and packet construction logic.

### Color Control Implementation

The `send_lifx_set_color` function constructs type 102 packets with HSB color values and transition parameters:

| Parameter | Type | Range | Default |
|-----------|------|-------|---------|
| `hue` | `uint16_t` | 0-65535 | Caller specified |
| `saturation` | `uint16_t` | 0-65535 | Caller specified |
| `brightness` | `uint16_t` | 0-65535 | Caller specified |
| `kelvin` | `uint16_t` | 2500-9000 | 3500 |
| `duration` | `uint32_t` | milliseconds | 500 |

**Sources:** [main/lifx.cpp:72-95]()

### Waveform Effect Processing

The `send_lifx_set_waveform` function implements type 103 packets for dynamic lighting effects:

```mermaid
graph TB
    subgraph "Waveform Parameters"
        HSB["hue, saturation, brightness<br/>Color target values"]
        Timing["period: 5000ms<br/>cycles: 65535 (infinite)"]
        Effect["waveform: 1 (sine)<br/>transient: 1 (temporary)"]
        Skew["skew_ratio: 0<br/>symmetric waveform"]
    end
    
    subgraph "Packet Construction"
        Header103["header.type = 103<br/>SetWaveform command"]
        Payload["21-byte payload<br/>effect parameters"]
        Broadcast["UDP broadcast<br/>192.168.4.255:56700"]
    end
    
    HSB --> Payload
    Timing --> Payload
    Effect --> Payload
    Skew --> Payload
    
    Header103 --> Broadcast
    Payload --> Broadcast
```

**Sources:** [main/lifx.cpp:97-127]()

### Power State Management

The `send_lifx_set_power` function handles type 21 packets for device power control:

- **Power On**: `level = 65535`, `duration = 5000ms`
- **Power Off**: `level = 0`, `duration = 5000ms`

**Sources:** [main/lifx.cpp:129-149]()

## Integration with AI Command System

The LIFX integration connects to the broader Reflect AI system through JSON command processing. When the AI assistant receives voice commands about lighting, it generates function calls that are translated into LIFX protocol messages.

```mermaid
sequenceDiagram
    participant AI as "OpenAI Realtime API"
    participant Browser as "Browser Client"
    participant WebRTC as "WebRTC Data Channel"
    participant Device as "Reflect Device"
    participant LIFX as "LIFX Lights"
    
    AI->>Browser: "set_lights function call<br/>{'color': 'red', 'brightness': 50}"
    Browser->>Browser: "Parse JSON command<br/>Extract HSB values"
    Browser->>WebRTC: "Send LIFX command<br/>via data channel"
    WebRTC->>Device: "JSON message<br/>lighting parameters"
    Device->>Device: "send_lifx_set_color()<br/>Convert to protocol"
    Device->>LIFX: "UDP broadcast<br/>Type 102 packet"
    LIFX->>LIFX: "Apply color change<br/>500ms transition"
```

**Sources:** [main/lifx.cpp:67-70](), [main/lifx.cpp:72-95]()

## Network Configuration

The LIFX system operates within the Reflect device's WiFi access point network using the following configuration:

- **Network**: `192.168.4.0/24` 
- **Broadcast Address**: `192.168.4.255`
- **LIFX Port**: `56700` (standard LIFX LAN protocol port)
- **Protocol**: UDP with `SO_BROADCAST` socket option
- **Source ID**: `0x12345678` (fixed identifier for all packets)

The `reflect_lifx()` initialization function establishes the UDP socket and configures broadcast addressing for the local network subnet.

**Sources:** [main/lifx.cpp:8-9](), [main/lifx.cpp:151-166]()

---

