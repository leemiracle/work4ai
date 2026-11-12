<!-- source: DeepWiki mcp.deepwiki.com · repo android/connectivity-samples · page 1 Overview · fetched 2026-10-23 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [BluetoothAdvertisements/README.md](BluetoothAdvertisements/README.md)
- [BluetoothAdvertisementsKotlin/README.md](BluetoothAdvertisementsKotlin/README.md)
- [BluetoothAdvertisementsKotlin/screenshots/1-main.png](BluetoothAdvertisementsKotlin/screenshots/1-main.png)
- [BluetoothAdvertisementsKotlin/screenshots/icon-web.png](BluetoothAdvertisementsKotlin/screenshots/icon-web.png)
- [BluetoothChat/README.md](BluetoothChat/README.md)
- [BluetoothLeChat/README.md](BluetoothLeChat/README.md)
- [BluetoothLeGatt/README.md](BluetoothLeGatt/README.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [LICENSE](LICENSE)
- [README.md](README.md)

</details>



This technical documentation provides a comprehensive guide to the Android Connectivity Samples repository, a collection of sample applications demonstrating various device-to-device connectivity technologies on the Android platform. It serves as an entry point for developers looking to implement different connectivity solutions in their Android applications.

The repository showcases implementations of Bluetooth (classic and Low Energy), Ultra-Wideband (UWB) ranging, Google's Nearby Connections API, and the Cross-Device SDK. These samples illustrate best practices and provide working code for establishing various types of connections between Android devices.

Sources: [README.md:5-22]()

## Repository Structure

The Android Connectivity Samples repository is organized by connectivity technology, with each sample application focused on demonstrating a specific connectivity feature or use case.

```mermaid
graph TD
    subgraph "Android Connectivity Samples Repository"
        A["Repository Root"] --> B["Bluetooth Samples"]
        A --> C["UWB Samples"]
        A --> D["Nearby Connections Samples"]
        A --> E["Cross-Device SDK Samples"]
        
        B --> B1["BluetoothChat"]
        B --> B2["BluetoothLeChat"]
        B --> B3["BluetoothAdvertisements"]
        B --> B4["BluetoothLeGatt"]
        
        C --> C1["UwbRanging"]
        
        D --> D1["NearbyConnectionsWalkieTalkie"]
        
        E --> E1["CrossDeviceRockPaperScissors"]
    end
    
    classDef default stroke-width:1px;
```

**Note:** The Bluetooth samples have been migrated to the [platform-samples repository](https://github.com/android/platform-samples/tree/main/samples/connectivity/bluetooth) but are still referenced here for completeness.

Sources: [README.md:1-22](), [BluetoothAdvertisementsKotlin/README.md:1-5](), [BluetoothLeChat/README.md:1-5](), [BluetoothLeGatt/README.md:1-5]()

## Connectivity Technologies Overview

The repository demonstrates the following connectivity technologies:

| Technology | Key Features | Power Usage | Range | Bandwidth | Sample Applications |
|------------|--------------|-------------|-------|-----------|---------------------|
| Bluetooth Classic | Device discovery, pairing, data transfer | Medium-High | ~10m | Up to 3 Mbps | BluetoothChat |
| Bluetooth Low Energy | Advertising, scanning, GATT services | Low | ~10m | Up to 2 Mbps | BluetoothLeChat, BluetoothAdvertisements, BluetoothLeGatt |
| Ultra-Wideband | Precise distance and direction measurement | Medium | ~10m | N/A (not for data transfer) | UwbRanging |
| Nearby Connections | Out-of-band discovery, connection establishment | Varies | ~30m | Varies based on transport | NearbyConnectionsWalkieTalkie |
| Cross-Device SDK | Multi-device experiences | Varies | Varies | Varies | CrossDeviceRockPaperScissors |

Sources: [BluetoothChat/README.md:10-35](), [BluetoothLeChat/README.md:10-33](), [BluetoothLeGatt/README.md:10-26](), [BluetoothAdvertisementsKotlin/README.md:10-32]()

## Connectivity Technology Relationships

The following diagram illustrates how the different connectivity technologies interact and their relative positioning in terms of functionality:

```mermaid
graph LR
    subgraph "Connectivity Technologies"
        BT["Bluetooth Classic"] --- BLE["Bluetooth Low Energy"]
        BLE --- UWB["Ultra-Wideband"]
        NC["Nearby Connections API"] --- BT
        NC --- BLE
        NC --- UWB
        CDSDK["Cross-Device SDK"] --- NC
    end
    
    subgraph "Core Capabilities"
        DC["Device Discovery"] --- PC["Pairing/Connection"]
        PC --- DT["Data Transfer"]
        PC --- RM["Range Measurement"]
    end
    
    BT --> DC
    BT --> PC
    BT --> DT
    BLE --> DC
    BLE --> PC
    BLE --> DT
    UWB --> RM
    NC --> DC
    NC --> PC
    NC --> DT
    CDSDK --> PC
    CDSDK --> DT
    
    classDef default stroke-width:1px;
```

In this architecture, Nearby Connections often serves as an out-of-band (OOB) channel for technologies like UWB, which require initial discovery and connection setup through another protocol before their specialized functionality can be used.

Sources: All provided files and diagrams

## Key Sample Applications

### Bluetooth Samples

#### BluetoothChat

Demonstrates two-way communication between Android devices using traditional Bluetooth RFCOMM sockets.

```mermaid
graph TD
    subgraph "BluetoothChat Architecture"
        BC["BluetoothChatService"] --> AS["AcceptThread"]
        BC --> CT["ConnectThread"]
        BC --> CMT["ConnectedThread"]
        
        MA["MainActivity"] --> BC
        MA --> CF["ChatFragment"]
        
        CF --> DLF["DeviceListFragment"]
    end
    
    classDef default stroke-width:1px;
```

Key features:
- Device discovery and pairing
- Establishing RFCOMM channels
- Connection management
- Data transfer over Bluetooth

Sources: [BluetoothChat/README.md:7-35]()

#### BluetoothLeChat

Implements a two-way chat application using Bluetooth Low Energy GATT profiles.

```mermaid
graph TD
    subgraph "BluetoothLeChat Architecture"
        CS["ChatServer"] --> GS["GattServer"]
        CS --> GS["GattService"]
        CS --> AD["Advertisement"]
        
        MA["MainActivity"] --> CS
        MA --> BCF["BluetoothChatFragment"]
        
        BCF --> DSF["DeviceScanFragment"]
    end
    
    classDef default stroke-width:1px;
```

Key features:
- BLE device scanning
- GATT server and client implementation
- BLE characteristic read/write operations
- BLE advertisements

Sources: [BluetoothLeChat/README.md:7-33]()

#### BluetoothAdvertisements

Demonstrates how to advertise small amounts of data using the Bluetooth Low Energy API and scan for those advertisements.

```mermaid
graph TD
    subgraph "BluetoothAdvertisements Architecture"
        MA["MainActivity"] --> AF["AdvertiserFragment"]
        MA --> SF["ScannerFragment"]
        
        AF --> BLA["BluetoothLeAdvertiser"]
        SF --> BLS["BluetoothLeScanner"]
    end
    
    classDef default stroke-width:1px;
```

Key features:
- BLE advertising
- Scanning for BLE advertisements
- Data payload in advertisements
- Advertisement filtering

Sources: [BluetoothAdvertisementsKotlin/README.md:7-32]()

#### BluetoothLeGatt

Demonstrates how to use the Bluetooth LE Generic Attribute Profile (GATT) to transmit arbitrary data between devices.

```mermaid
graph TD
    subgraph "BluetoothLeGatt Architecture"
        BS["BluetoothService"] --> BG["BluetoothGatt"]
        BG --> BC["BluetoothGattCallback"]
        
        DA["DeviceActivity"] --> BS
        DCA["DeviceControlActivity"] --> BS
        DSA["DeviceScanActivity"] --> BS
    end
    
    classDef default stroke-width:1px;
```

Key features:
- Scanning for BLE devices
- Connecting to GATT servers
- Reading/writing GATT characteristics
- Receiving notifications from GATT servers

Sources: [BluetoothLeGatt/README.md:7-26]()

### UWB Samples

#### UwbRanging

Demonstrates the use of Ultra-Wideband (UWB) technology for precise distance and direction measurement between devices.

```mermaid
graph TD
    subgraph "UwbRanging Architecture"
        subgraph "Controller Device"
            CApp["UwbRanging App"] --> CUWL["UWB Jetpack Library"]
            CApp --> COOB["Nearby Connections (OOB)"]
            CUWL --> CUWH["UWB Hardware"]
        end
        
        subgraph "Controllee Device"
            RApp["UwbRanging App"] --> RUWL["UWB Jetpack Library"]
            RApp --> ROOB["Nearby Connections (OOB)"]
            RUWL --> RUWH["UWB Hardware"]
        end
        
        COOB <--> ROOB
        CUWH <--> RUWH
    end
    
    classDef default stroke-width:1px;
```

Key features:
- UWB device discovery
- Ranging session establishment
- Distance and angle measurement
- Use of Nearby Connections as an out-of-band channel

Sources: All provided diagrams

### Nearby Connections Samples

#### NearbyConnectionsWalkieTalkie

Real-time audio communication between devices using Google's Nearby Connections API.

```mermaid
graph TD
    subgraph "NearbyConnectionsWalkieTalkie Architecture"
        CA["ConnectionsActivity"] --> CLCB["ConnectionLifecycleCallback"]
        CA --> PC["PayloadCallback"]
        CA --> EM["Endpoint Management"]
        
        EM --> DE["Discovered Endpoints"]
        EM --> PC["Pending Connections"]
        EM --> EC["Established Connections"]
        
        CA --> CC["ConnectionsClient"]
        
        CC --> AD["startAdvertising()"]
        CC --> DS["startDiscovery()"]
        CC --> CN["connectToEndpoint()"]
        CC --> SP["sendPayload()"]
    end
    
    classDef default stroke-width:1px;
```

Key features:
- Device discovery via Nearby Connections
- Audio capture and streaming
- Real-time communication
- Connection lifecycle management

Sources: All provided diagrams

### Cross-Device SDK Samples

#### CrossDeviceRockPaperScissors

Demonstrates Google's Cross-Device SDK for creating multi-device experiences through a simple game.

```mermaid
graph TD
    subgraph "CrossDeviceRockPaperScissors Architecture"
        MA["MainActivity"] --> DTPA["DiscoveryTwoPlayerActivity"]
        MA --> STPA["SessionsTwoPlayerActivity"]
        MA --> SSPA["SessionsSinglePlayerActivity"]
        
        DTPA --> DTPGM["DiscoveryTwoPlayerGameManager"]
        STPA --> STPGM["SessionsTwoPlayerGameManager"]
        SSPA --> SPGM["SinglePlayerGameManager"]
        
        DTPGM --> TPGD["TwoPlayerGameData"]
        STPGM --> TPGD
        SPGM --> SPGD["SinglePlayerGameData"]
    end
    
    classDef default stroke-width:1px;
```

Key features:
- Cross-device discovery
- Session management
- State synchronization
- User interface coordination

Sources: All provided diagrams

## Getting Started

To use these samples, you'll need:

- Android SDK 28 or higher
- Android Build Tools v28.0.3 or higher
- Android Support Repository
- Compatible Android devices for testing (some samples require two devices)

Each sample includes its own README with specific instructions and requirements.

```mermaid
graph LR
    subgraph "Development Flow"
        S1["Clone Repository"] --> S2["Select Sample"]
        S2 --> S3["Build with Gradle"]
        S3 --> S4["Deploy to Devices"]
        S4 --> S5["Test Functionality"]
    end
    
    classDef default stroke-width:1px;
```

Sources: [README.md:8-22](), [BluetoothAdvertisementsKotlin/README.md:36-52](), [BluetoothLeChat/README.md:37-54](), [BluetoothLeGatt/README.md:28-45]()

## License and Contributions

The repository is licensed under the Apache License 2.0. Contributions are welcome. See the CONTRIBUTING.md file for details on how to contribute.

Sources: [LICENSE:1-191](), [CONTRIBUTING.md:1-36]()

---

