<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-ipmi-oem · page 5 Hardware Integration · fetched 2026-10-26 -->

# Hardware Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Grace/src/ghoemcommands.cpp](Grace/src/ghoemcommands.cpp)
- [include/dgx-a100-config.hpp](include/dgx-a100-config.hpp)
- [src/BF/oemcommands.cpp](src/BF/oemcommands.cpp)
- [src/BF/spectre/oemcommands.cpp](src/BF/spectre/oemcommands.cpp)

</details>



This document describes how the NVIDIA IPMI OEM commands system interfaces with physical hardware components through various communication protocols and abstraction layers. It covers the hardware communication mechanisms, component management strategies, and platform-specific integration patterns used across different NVIDIA platforms.

For information about the platform-specific command implementations that utilize this hardware integration, see [Platform Implementations](#3). For details about the D-Bus services that mediate hardware control, see [D-Bus Service Integration](#2.2).

## Hardware Communication Protocols

The system primarily uses I2C and GPIO protocols for direct hardware communication, with additional abstraction through D-Bus services for system-level hardware management.

### I2C Communication Layer

The core I2C communication is implemented through the `i2cTransaction()` function which provides a standardized interface for hardware access across all platforms.

```mermaid
graph TB
    subgraph "IPMI Command Layer"
        A[ipmiOemCommand]
    end
    
    subgraph "I2C Abstraction Layer"
        B[i2cTransaction]
        C[ipmi::i2cWriteRead]
    end
    
    subgraph "Hardware Layer"
        D["/dev/i2c-N"]
        E["Hardware Components"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    
    A --> F["D-Bus Services"]
    F --> G["System Hardware Control"]
```

The I2C transaction function handles device file operations, error handling, and provides a consistent interface for all hardware communication:

```mermaid
graph LR
    subgraph "I2C Transaction Flow"
        A["writeData Vector"] --> B["i2cTransaction()"]
        B --> C["Open /dev/i2c-bus"]
        C --> D["ipmi::i2cWriteRead()"]
        D --> E["readData Vector"]
        
        B --> F["Error Handling"]
        F --> G["ipmi::ccInvalidFieldRequest"]
        F --> H["ipmi::ccSuccess"]
    end
```

Sources: [src/BF/oemcommands.cpp:372-393](), [Grace/src/ghoemcommands.cpp:328-349]()

### GPIO Control Interface

GPIO control is used for direct hardware manipulation, particularly for write protection and LED control. The system uses Linux GPIO interfaces with specific chip and pin mappings.

```mermaid
graph TB
    subgraph "GPIO Control Flow"
        A["IPMI GPIO Command"] --> B["Platform Config Lookup"]
        B --> C["GPIO Chip/Pin Mapping"]
        C --> D["Linux GPIO Interface"]
        D --> E["Hardware Pin Control"]
    end
    
    subgraph "GPIO Configuration"
        F["mbWpGpioChip: gpiochip792"]
        G["mbWpGpioId: 55"]
        H["biosGpioId: 74"]
    end
    
    B --> F
    B --> G
    B --> H
```

Sources: [include/dgx-a100-config.hpp:82-84](), [include/dgx-a100-config.hpp:103-104]()

## Hardware Component Management

The system manages various hardware components through standardized addressing schemes and communication protocols.

### Power Supply Unit (PSU) Management

PSU management involves monitoring and control of multiple power supply units through I2C communication with predefined addresses and registers.

```mermaid
graph TB
    subgraph "PSU Hardware Topology"
        A["PSU Array: 6 Units"]
        B["psuAddr[]: {0x40, 0x41, 0x42, 0x40, 0x41, 0x42}"]
        C["psuBus[]: {215, 216, 217, 219, 220, 221}"]
    end
    
    subgraph "PSU Registers"
        D["psuRegSerialNumber: 0x9e"]
        E["psuRegPartNumber: 0x9A"]
        F["psuRegVendor: 0x99"]
        G["psuRegPowerReal: 0x96"]
    end
    
    subgraph "IPMI Commands"
        H["ipmiOemPsuPower()"]
        I["PSU Monitoring Commands"]
    end
    
    A --> B
    A --> C
    B --> D
    B --> E
    B --> F
    B --> G
    H --> I
    I --> A
```

Sources: [include/dgx-a100-config.hpp:28-44]()

### FPGA and Control Hardware

The system manages multiple FPGAs for various control functions including write protection, LED control, and system monitoring.

```mermaid
graph TB
    subgraph "FPGA Hardware Layout"
        A["fpgaI2cAddress: 0x3c"]
        B["fpgaMbI2cBus: 1"]
        C["fpgaMidI2cBus: 2"]
    end
    
    subgraph "FPGA Registers"
        D["fpgaMbVersionAddr: 0x00"]
        E["fpgaMidVersionAddr: 0x2d"]
        F["fpgaMidWpReg: 0x30"]
        G["fpgaMidSSDLedReadyMove: 0x0e"]
    end
    
    subgraph "Control Functions"
        H["Write Protection Control"]
        I["SSD LED Management"]
        J["Version Monitoring"]
    end
    
    A --> B
    A --> C
    B --> D
    C --> E
    C --> F
    C --> G
    
    D --> J
    E --> J
    F --> H
    G --> I
```

Sources: [include/dgx-a100-config.hpp:45-62]()

### Switch and Network Hardware

The system manages PEX switches and Ethernet switches through I2C communication for network topology control.

```mermaid
graph TB
    subgraph "Switch Hardware Configuration"
        A["pexSwitchI2CBus[]: {7, 9, 7, 9}"]
        B["pexSwitchI2CVersionAddress[]: {0x48, 0x49, 0x48, 0x49}"]
        C["ethSwitchI2caddressBF3"]
        D["ethSwitchI2cBusBF3"]
    end
    
    subgraph "Switch Operations"
        E["ipmi3PortEthSwitchStatus()"]
        F["Switch Version Reading"]
        G["Switch Reset Control"]
    end
    
    A --> E
    B --> F
    C --> E
    D --> E
    E --> G
```

Sources: [include/dgx-a100-config.hpp:70-73](), [src/BF/oemcommands.cpp:485-513]()

## Platform-Specific Hardware Integration

Different NVIDIA platforms implement varying levels of hardware integration based on their capabilities and intended use cases.

### Bluefield Platform Hardware Support

The Bluefield platform provides comprehensive hardware integration with full support for all hardware components.

```mermaid
graph TB
    subgraph "Bluefield Hardware Features"
        A["Full I2C Support"]
        B["PSU Management"]
        C["FPGA Control"]
        D["Switch Management"]
        E["LED Control"]
        F["GPIO Operations"]
    end
    
    subgraph "Implementation Functions"
        G["i2cTransaction()"]
        H["ipmiSupportLaunchpad()"]
        I["ipmi3PortEthSwitchStatus()"]
        J["DPUHardRST()"]
    end
    
    A --> G
    B --> G
    C --> H
    D --> I
    E --> G
    F --> J
```

Sources: [src/BF/oemcommands.cpp:372-393](), [src/BF/oemcommands.cpp:395-483]()

### Grace Platform Hardware Support

The Grace platform focuses on GPU management and system control with specialized SMBPBI passthrough capabilities.

```mermaid
graph TB
    subgraph "Grace Hardware Features"
        A["GPU SMBPBI Interface"]
        B["Fan Control"]
        C["LED Management"]
        D["I2C Communication"]
    end
    
    subgraph "Implementation Functions"
        E["ipmiSMBPBIPassthroughCmd()"]
        F["ipmiSetFanZonePWMDuty()"]
        G["ipmiOemGetSSDLed()"]
        H["i2cTransaction()"]
    end
    
    A --> E
    B --> F
    C --> G
    D --> H
```

Sources: [Grace/src/ghoemcommands.cpp:167-275](), [Grace/src/ghoemcommands.cpp:463-574]()

### Platform Hardware Differentiation

The system implements graduated hardware support across platforms, with some platforms disabling hardware commands entirely.

```mermaid
graph TB
    subgraph "Platform Support Matrix"
        A["Bluefield: Full Support"]
        B["Grace: GPU-Focused Support"]
        C["BF2: Limited Support"]
        D["Spectre: No Support"]
    end
    
    subgraph "Implementation Strategy"
        E["Platform-Specific Files"]
        F["Conditional Compilation"]
        G["Function Rejection Handlers"]
    end
    
    A --> E
    B --> E
    C --> F
    D --> G
```

Sources: [src/BF/spectre/oemcommands.cpp:58-110]()

## Hardware Control Flow

The hardware control flow demonstrates how IPMI commands are translated into actual hardware operations through multiple abstraction layers.

### Command Processing to Hardware Execution

```mermaid
graph TD
    subgraph "IPMI Layer"
        A["IPMI OEM Command"]
        B["Parameter Validation"]
    end
    
    subgraph "Platform Layer"
        C["Platform-Specific Handler"]
        D["Hardware Address Lookup"]
    end
    
    subgraph "Communication Layer"
        E["i2cTransaction()"]
        F["GPIO Control"]
        G["D-Bus Service Call"]
    end
    
    subgraph "Hardware Layer"
        H["I2C Device"]
        I["GPIO Pin"]
        J["System Service"]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
    
    E --> H
    F --> I
    G --> J
```

Sources: [src/BF/oemcommands.cpp:372-393](), [Grace/src/ghoemcommands.cpp:328-349]()

### Fan Control Hardware Integration

Fan control demonstrates the integration between IPMI commands, system services, and hardware PWM control.

```mermaid
graph LR
    subgraph "Fan Control Flow"
        A["ipmiSetFanControl()"] --> B["Mode Selection"]
        B --> C["Auto Mode"]
        B --> D["Manual Mode"]
        
        C --> E["systemctl start phosphor-pid-control"]
        D --> F["systemctl stop phosphor-pid-control"]
        D --> G["ipmiSetAllFanZonesPWMDuty()"]
        
        G --> H["ipmiSetFanZonePWMDuty()"]
        H --> I["PWM Hardware Write"]
    end
```

Sources: [Grace/src/ghoemcommands.cpp:607-638](), [Grace/src/ghoemcommands.cpp:463-574]()

## Hardware Configuration and Addressing

The system uses comprehensive configuration constants to define hardware addressing schemes and communication parameters.

### I2C Bus and Address Mapping

```mermaid
graph TB
    subgraph "Hardware Address Configuration"
        A["PSU Addresses"]
        B["FPGA Addresses"]
        C["Switch Addresses"]
        D["Sensor Addresses"]
    end
    
    subgraph "Bus Configuration"
        E["I2C Bus Numbers"]
        F["GPIO Chip Names"]
        G["Hardware Register Maps"]
    end
    
    A --> E
    B --> E
    C --> E
    D --> E
    
    E --> F
    E --> G
```

The hardware configuration provides compile-time constants for all hardware addressing:

| Component | Bus/Address | Register | Purpose |
|-----------|-------------|----------|---------|
| PSU Array | Buses 215-221 | Addresses 0x40-0x42 | Power monitoring |
| MB FPGA | Bus 1 | Address 0x3c | Motherboard control |
| MID FPGA | Bus 2 | Address 0x3c | System control |
| PEX Switches | Buses 7,9 | Addresses 0x48,0x49 | Network topology |

Sources: [include/dgx-a100-config.hpp:28-107]()

### Hardware Register Organization

```mermaid
graph TB
    subgraph "Register Categories"
        A["Version Registers"]
        B["Control Registers"]
        C["Status Registers"]
        D["Data Registers"]
    end
    
    subgraph "Access Patterns"
        E["Read-Only Monitoring"]
        F["Read-Write Control"]
        G["Write-Only Commands"]
    end
    
    A --> E
    B --> F
    C --> E
    D --> F
    D --> G
```

Sources: [include/dgx-a100-config.hpp:33-68]()

---

