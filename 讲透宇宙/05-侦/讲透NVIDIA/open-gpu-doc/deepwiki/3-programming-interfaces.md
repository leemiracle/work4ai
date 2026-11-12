<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/open-gpu-doc · page 3 Programming Interfaces · fetched 2026-10-26 -->

# Programming Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [classes/index.html](classes/index.html)
- [classes/twod/cl902d.h](classes/twod/cl902d.h)
- [classes/video/clc5b0.h](classes/video/clc5b0.h)
- [classes/video/clc5b7.h](classes/video/clc5b7.h)
- [classes/video/cle7d0.h](classes/video/cle7d0.h)
- [classes/video/index.html](classes/video/index.html)

</details>



This document provides an overview of the software programming interfaces for NVIDIA GPU hardware subsystems. These interfaces define the hardware abstraction layer that enables software to interact with GPU engines for graphics, compute, display, and video processing operations.

For detailed coverage of specific subsystem interfaces, see [3D Graphics System](#3.1), [Display System](#3.2), [Video Processing System](#3.3), and [Compute System](#3.4). For the underlying hardware architecture specifications, see [GPU Hardware Architecture](#2).

## Architecture Overview

The GPU programming interfaces are organized as a layered abstraction system where software interacts with hardware engines through standardized class interfaces. Each hardware engine exposes its functionality through a specific hardware class that defines methods, registers, and operational semantics.

### Interface Layer Architecture

```mermaid
graph TB
    subgraph "Software Layer"
        USERMODE["User Mode Applications"]
        DRIVER["GPU Driver"]
    end
    
    subgraph "Hardware Abstraction Layer"
        CLASSES["Hardware Classes"]
        TWOD_CLASS["FERMI_TWOD_A<br/>0x902D"]
        VIDEO_DEC["NVC5B0_VIDEO_DECODER<br/>0xC5B0"] 
        VIDEO_ENC["NVC5B7_VIDEO_ENCODER<br/>0xC5B7"]
        NVJPG_CLASS["NVE7D0_VIDEO_NVJPG<br/>0xE7D0"]
        DISPLAY_CLASSES["Display Classes<br/>Core, Window, Cursor"]
        GRAPHICS_CLASSES["3D Graphics Classes<br/>Hopper_A, Ada_A"]
        COMPUTE_CLASSES["Compute Classes<br/>Blackwell, Hopper"]
    end
    
    subgraph "Hardware Layer"
        TWOD_ENGINE["2D Engine"]
        VIDEO_ENGINES["Video Engines<br/>NVDEC, NVENC, NVJPG"]
        DISPLAY_ENGINE["Display Controller"]
        GRAPHICS_ENGINE["3D Graphics Engine"]
        COMPUTE_ENGINE["Compute Engine"]
    end
    
    USERMODE --> DRIVER
    DRIVER --> CLASSES
    
    CLASSES --> TWOD_CLASS
    CLASSES --> VIDEO_DEC
    CLASSES --> VIDEO_ENC
    CLASSES --> NVJPG_CLASS
    CLASSES --> DISPLAY_CLASSES
    CLASSES --> GRAPHICS_CLASSES
    CLASSES --> COMPUTE_CLASSES
    
    TWOD_CLASS --> TWOD_ENGINE
    VIDEO_DEC --> VIDEO_ENGINES
    VIDEO_ENC --> VIDEO_ENGINES
    NVJPG_CLASS --> VIDEO_ENGINES
    DISPLAY_CLASSES --> DISPLAY_ENGINE
    GRAPHICS_CLASSES --> GRAPHICS_ENGINE
    COMPUTE_CLASSES --> COMPUTE_ENGINE
```

Sources: [classes/index.html:1-14](), [classes/twod/cl902d.h:26-27](), [classes/video/clc5b0.h:31](), [classes/video/clc5b7.h:31](), [classes/video/cle7d0.h:31]()

## Hardware Class System

The programming interfaces are implemented through hardware classes that provide standardized method interfaces. Each class is identified by a unique class ID and defines a set of methods for controlling the associated hardware engine.

### Core Interface Categories

| Category | Description | Example Classes |
|----------|-------------|-----------------|
| **3D Graphics** | Rendering pipeline control | Hopper_A, Ada_A, Blackwell_A |
| **Display** | Output display management | Core, Window, Cursor channels |
| **Video Processing** | Encode/decode operations | NVC5B0 (decoder), NVC5B7 (encoder) |
| **2D Graphics** | Blitting and composition | FERMI_TWOD_A (0x902D) |
| **Compute** | GPGPU workload execution | Hopper, Blackwell compute classes |
| **Copy Engine** | Memory transfer operations | DMA copy classes |
| **Host Interface** | System interaction | Host configuration classes |

Sources: [classes/index.html:5-12]()

### Hardware Class Structure

Each hardware class follows a standardized structure with common method categories and register layouts:

```mermaid
graph TD
    subgraph "Hardware Class Structure"
        CLASS_ID["Class ID<br/>(e.g., 0x902D, 0xC5B0)"]
        
        subgraph "Standard Methods"
            SET_OBJECT["SET_OBJECT<br/>Class identification"]
            NO_OPERATION["NO_OPERATION<br/>Pipeline synchronization"]
            EXECUTE["EXECUTE<br/>Command execution"]
            SEMAPHORE["Semaphore Operations<br/>Synchronization primitives"]
            CTX_SWITCH["CTX_SWITCH<br/>Context management"]
        end
        
        subgraph "Engine-Specific Methods"
            CONFIG_METHODS["Configuration Methods<br/>Engine setup"]
            OPERATION_METHODS["Operation Methods<br/>Workload submission"]
            STATUS_METHODS["Status Methods<br/>State monitoring"]
        end
        
        subgraph "Error Handling"
            ERROR_CODES["Error Codes<br/>Hardware exceptions"]
            INTERRUPTS["Interrupt Definitions<br/>Asynchronous events"]
        end
    end
    
    CLASS_ID --> SET_OBJECT
    CLASS_ID --> NO_OPERATION
    CLASS_ID --> EXECUTE
    CLASS_ID --> SEMAPHORE
    CLASS_ID --> CTX_SWITCH
    CLASS_ID --> CONFIG_METHODS
    CLASS_ID --> OPERATION_METHODS
    CLASS_ID --> STATUS_METHODS
    CLASS_ID --> ERROR_CODES
    CLASS_ID --> INTERRUPTS
```

Sources: [classes/twod/cl902d.h:230-249](), [classes/video/clc5b0.h:35-79](), [classes/video/clc5b7.h:35-105]()

## Common Interface Patterns

All hardware classes implement consistent patterns for basic operations, providing a uniform programming model across different GPU engines.

### Standard Method Interface

The following methods are present in virtually all hardware classes:

#### Object Management
- `SET_OBJECT`: Identifies the hardware class being used [classes/twod/cl902d.h:230-232]()
- `NO_OPERATION`: Provides pipeline synchronization points [classes/twod/cl902d.h:234-235]()

#### Execution Control  
- `EXECUTE`: Initiates command processing with notification options [classes/video/clc5b0.h:69-78]()
- `WAIT_FOR_IDLE`: Ensures engine completion [classes/twod/cl902d.h:248-249]()

#### Synchronization Primitives
- `SEMAPHORE_A/B/C/D`: Memory-based synchronization [classes/video/clc5b7.h:53-127]()
- Configurable notification and awakening mechanisms

#### Context Management
- `CTX_SWITCH`: Context save/restore operations [classes/video/clc5b0.h:57-68]()
- `CTX_SAVE_AREA`: Context storage location [classes/video/clc5b7.h:65-71]()

### Error and Interrupt Handling

Each interface defines comprehensive error reporting:

```mermaid
graph LR
    subgraph "Error Categories"
        OS_ERRORS["OS Errors<br/>NVC5B0_OS_ERROR_*"]
        APP_ERRORS["Application Errors<br/>Hardware-specific"]
        VLD_ERRORS["VLD Errors<br/>Bitstream processing"]
        HW_ERRORS["Hardware Errors<br/>Engine exceptions"]
    end
    
    subgraph "Interrupt Types"
        EXECUTE_AWAKEN["EXECUTE_AWAKEN<br/>0x100"]
        SEMAPHORE_AWAKEN["SEMAPHORE_AWAKEN<br/>0x200"] 
        CTX_ERROR["CTX_ERROR_FBIF<br/>0x300"]
        LIMIT_VIOLATION["LIMIT_VIOLATION<br/>0x400"]
        HALT_ENGINE["HALT_ENGINE<br/>0x600"]
    end
    
    OS_ERRORS --> EXECUTE_AWAKEN
    APP_ERRORS --> SEMAPHORE_AWAKEN
    VLD_ERRORS --> CTX_ERROR
    HW_ERRORS --> HALT_ENGINE
```

Sources: [classes/video/clc5b0.h:242-258](), [classes/video/clc5b7.h:464-481](), [classes/video/cle7d0.h:103-125]()

## Method Register Layout

Hardware class methods follow a consistent register addressing scheme with standardized field definitions:

### Address Space Organization
- **0x0000-0x00FF**: Object and control methods
- **0x0100-0x02FF**: Standard interface methods  
- **0x0300-0x03FF**: Execution and synchronization
- **0x0400+**: Engine-specific method ranges

### Field Encoding Patterns
- Bit field definitions use consistent naming: `METHOD_FIELD_NAME_BITRANGE`
- Address offsets specified as `METHOD_NAME (0xOffset)`
- Enumerated values follow `METHOD_NAME_VALUE` convention

Sources: [classes/twod/cl902d.h:230-300](), [classes/video/clc5b0.h:35-130]()

The programming interfaces provide a comprehensive abstraction layer that enables consistent software interaction with diverse GPU hardware engines while maintaining the flexibility needed for engine-specific optimizations and capabilities.

---

