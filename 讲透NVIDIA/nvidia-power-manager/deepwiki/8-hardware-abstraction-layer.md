<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/nvidia-power-manager · page 8 Hardware Abstraction Layer · fetched 2026-10-26 -->

# Hardware Abstraction Layer

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cpld_utility/dragonCpld.hpp](cpld_utility/dragonCpld.hpp)
- [cpld_utility/meson.build](cpld_utility/meson.build)
- [cpld_utility/utils.cpp](cpld_utility/utils.cpp)
- [cpld_utility/utils.hpp](cpld_utility/utils.hpp)
- [include/dragonChassisBase.hpp](include/dragonChassisBase.hpp)

</details>



## Purpose and Scope

The Hardware Abstraction Layer (HAL) provides a platform-agnostic abstraction for firmware update operations on Dragon Chassis platforms. It centralizes common I2C communication patterns, arbitration mechanisms, GPIO control, and image loading infrastructure used by both CPLD and PSU firmware update utilities.

This page documents the core abstraction classes (`DragonChassisBase`, `I2c`), I2C arbitration protocols, PEC (Packet Error Code) calculation, and retry logic. For information about specific CPLD update implementations using this HAL, see [Dragon Chassis CPLD Update](#3.2.2). For PSU-specific implementations, see [PSU Firmware Update Utilities](#4.2).

## Architecture Overview

The hardware abstraction layer implements a class hierarchy that separates common Dragon Chassis behaviors from device-specific update sequences:

```mermaid
graph TB
    I2c["I2c Base Class<br/>transfer()<br/>calculate_PEC()"]
    DragonBase["DragonChassisBase<br/>Abstract Class"]
    DragonCpld["DragonCpld<br/>Lattice CPLD Implementation"]
    DragonPsu["DragonChassisPsuUpdate<br/>PSU Implementation"]
    
    I2c --> DragonBase
    DragonBase --> DragonCpld
    DragonBase --> DragonPsu
    
    DragonBase -.provides.-> Arbitration["I2C Arbitration<br/>enableArbitration()"]
    DragonBase -.provides.-> ImageLoad["Image Loading<br/>loadImage()"]
    DragonBase -.provides.-> DataSend["Data Transmission<br/>sendData()<br/>sendDataWithRetry()"]
    DragonBase -.provides.-> SysfsIO["Sysfs I/O<br/>readSysFs()<br/>writeSysFs()"]
    DragonBase -.provides.-> ErrorHandling["Error Handling<br/>printError()<br/>UpdateError enum"]
    
    DragonCpld -.implements.-> SendImage1["sendImage()<br/>Lattice-specific"]
    DragonPsu -.implements.-> SendImage2["sendImage()<br/>PSU-specific"]
```

**Sources:** [include/dragonChassisBase.hpp:1-503](), [cpld_utility/dragonCpld.hpp:1-168]()

The abstraction provides three layers:
1. **I2c Base Class**: Low-level I2C transfer operations and PEC calculation
2. **DragonChassisBase**: Common Dragon Chassis behaviors (arbitration, image loading, retry logic)
3. **Derived Classes**: Device-specific update sequences (`DragonCpld`, `DragonChassisPsuUpdate`)

## DragonChassisBase Abstract Class

### Class Definition and Responsibilities

The `DragonChassisBase` class serves as the foundation for all Dragon Chassis firmware update utilities. It inherits from `I2c` and provides platform-specific infrastructure while remaining device-agnostic.

```mermaid
classDiagram
    class I2c {
        +transfer()
        +calculate_PEC()
    }
    
    class DragonChassisBase {
        #int devIdx
        #int address
        #bool arb
        #char* imageName
        #char* image
        #int imageSize
        #int imageOffset
        #int fd
        #array~uint8_t~ deviceIdArray
        #int arbTrials
        
        +DragonChassisBase(index, address, arbitrator, imageName)
        +printError(code)
        #readSysFs(path) int
        #writeSysFs(path, value) int
        #enableArbitration(enable) int
        #loadImage() int
        #sendData(fd, addr, data, length, error) int
        #sendDataWithRetry(...) int
        #transferWithRetry(...) int
        #sendImage()* int
    }
    
    class UpdateError {
        <<enumeration>>
        ERROR_LOAD_IMAGE
        ERROR_ENABLE_ARB
        ERROR_DISABLE_ARB
        ERROR_OPEN_BUS
        ERROR_UNLOCK
        ERROR_ERASE
        ERROR_SEND_IMAGE
        ERROR_ACTIVATE
        ...40+ error codes
    }
    
    I2c <|-- DragonChassisBase
    DragonChassisBase ..> UpdateError
```

**Sources:** [include/dragonChassisBase.hpp:36-503]()

### Constructor Parameters

The constructor initializes common state required for Dragon Chassis updates:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `index` | `int` | Device index (e.g., CPLD0, CPLD1, PSU0, PSU1) |
| `address` | `int` | I2C slave address of target device |
| `arbitrator` | `bool` | Whether I2C bus requires arbitration |
| `imageName` | `char*` | Path to firmware image file |

**Sources:** [include/dragonChassisBase.hpp:46-49]()

## I2C Communication Infrastructure

### Sysfs Interface Layer

The HAL provides methods to interact with kernel driver sysfs interfaces, primarily for arbitration control:

```mermaid
graph LR
    ReadSysFs["readSysFs(path)"]
    WriteSysFs["writeSysFs(path, value)"]
    SysfsFile["/sys/devices/platform/i2carb/arb_state"]
    
    ReadSysFs -->|"open, read, parse"| SysfsFile
    WriteSysFs -->|"open, write"| SysfsFile
    
    EnableArb["enableArbitration(enable)"]
    EnableArb -->|"read current state"| ReadSysFs
    EnableArb -->|"write new state"| WriteSysFs
    EnableArb -->|"verify with retry"| ReadSysFs
```

**Sources:** [include/dragonChassisBase.hpp:273-308]()

#### readSysFs() Implementation

The `readSysFs()` method reads an integer value from a sysfs file:

- Opens file at specified path
- Reads content as string
- Converts to integer using `std::stoi()`
- Returns -1 on any error (file not found, parse failure)

**Sources:** [include/dragonChassisBase.hpp:273-291]()

#### writeSysFs() Implementation

The `writeSysFs()` method writes an integer value to a sysfs file:

- Opens file for writing
- Writes integer value
- Returns 0 on success, -1 on failure

**Sources:** [include/dragonChassisBase.hpp:300-308]()

### Data Transmission with PEC

The HAL implements PEC-enabled I2C data transmission for enhanced reliability:

```mermaid
sequenceDiagram
    participant Caller
    participant sendData
    participant calculate_PEC
    participant transfer
    participant I2C_Bus
    
    Caller->>sendData: data[], length, error
    sendData->>sendData: malloc(length + 1)
    sendData->>sendData: memcpy(data)
    sendData->>calculate_PEC: dataWithPec, address, length
    calculate_PEC-->>sendData: PEC byte appended
    sendData->>transfer: fd, addr, dataWithPec, length+1
    transfer->>I2C_Bus: I2C transaction
    I2C_Bus-->>transfer: status
    transfer-->>sendData: result
    sendData->>sendData: free(dataWithPec)
    sendData-->>Caller: 0 or error code
```

**Sources:** [include/dragonChassisBase.hpp:441-469]()

The `sendData()` method:
1. Allocates buffer with space for PEC byte
2. Copies data to new buffer
3. Calls `calculate_PEC()` to append checksum
4. Performs I2C transfer via `transfer()` method
5. Returns error code on failure, 0 on success

### Retry Logic

Both data transmission and I2C transfer operations support configurable retry mechanisms:

| Method | Purpose | Retry Count |
|--------|---------|-------------|
| `sendDataWithRetry()` | Retry data send with PEC | Configurable parameter |
| `transferWithRetry()` | Retry raw I2C transfer | Configurable parameter |

**Sources:** [include/dragonChassisBase.hpp:471-497]()

The retry methods loop up to `retry` times, breaking on first success:

```cpp
for (int i = 0; i < retry; i++) {
    ret = sendData(send_fd, send_addr, data, length, error);
    if (!ret) break;
}
```

## I2C Arbitration Mechanism

### Arbitration Protocol Overview

Dragon Chassis implements a sophisticated I2C arbitration protocol coordinated between BMC and CPLD via GPIO handshake. The BMC-side implementation is provided by a kernel driver exposed through sysfs.

```mermaid
graph TB
    subgraph "BMC (DragonChassisBase)"
        EnableArbMethod["enableArbitration(enable)"]
        ReadState["readSysFs(ARB_STATE_PATH)"]
        WriteState["writeSysFs(ARB_STATE_PATH, value)"]
    end
    
    subgraph "Kernel Driver"
        ArbDriver["i2carb driver"]
        WatchdogPet["Watchdog Pet Logic<br/>20-minute timeout"]
    end
    
    subgraph "Hardware"
        GPIO1["BMC GPIO<br/>Request Signal"]
        GPIO2["CPLD GPIO<br/>Grant Signal"]
        I2C_Bus["Arbitrated I2C Bus"]
    end
    
    EnableArbMethod -->|"1. Read current"| ReadState
    ReadState --> ArbDriver
    EnableArbMethod -->|"2. Write new value"| WriteState
    WriteState --> ArbDriver
    EnableArbMethod -->|"3. Verify (retry 5x)"| ReadState
    
    ArbDriver -->|"Assert"| GPIO1
    GPIO1 -.->|"Request"| GPIO2
    GPIO2 -.->|"Grant"| ArbDriver
    ArbDriver -->|"Controls access"| I2C_Bus
    ArbDriver -->|"Automatic"| WatchdogPet
```

**Sources:** [include/dragonChassisBase.hpp:310-370]()

### Arbitration State Machine

The `enableArbitration()` method implements a state machine with verification and retry:

1. **Read Current State**: Check if arbitration is already in desired state
2. **Write New State**: If different, write to `ARB_STATE_PATH`
3. **Verify with Retry**: Read back state up to `arbTrials` (5) times
4. **Timeout Check**: 20-minute watchdog timeout enforced by kernel driver

**Arbitration Path Constant:**
```cpp
#define ARB_STATE_PATH "/sys/devices/platform/i2carb/arb_state"
```

**Sources:** [include/dragonChassisBase.hpp:28](), [include/dragonChassisBase.hpp:323-370]()

### Arbitration Flow

```mermaid
stateDiagram-v2
    [*] --> ReadCurrentState
    ReadCurrentState --> CheckValue: readSysFs()
    CheckValue --> AlreadySet: value == desired
    CheckValue --> WriteLoop: value != desired
    
    WriteLoop --> WriteSysfs: writeSysFs(desired)
    WriteSysfs --> ReadVerify: readSysFs()
    ReadVerify --> Success: value == desired
    ReadVerify --> CheckRetry: value != desired
    CheckRetry --> WriteLoop: cnt < arbTrials
    CheckRetry --> Error: cnt >= arbTrials
    
    AlreadySet --> [*]: Success
    Success --> [*]: Return 0
    Error --> [*]: Return error code
```

**Sources:** [include/dragonChassisBase.hpp:323-370]()

### Error Handling for Arbitration

Arbitration failures return specific error codes:

| Error Code | Scenario |
|------------|----------|
| `ERROR_ENABLE_ARB` | Failed to enable arbitration |
| `ERROR_DISABLE_ARB` | Failed to disable arbitration |
| `ERROR_ARB_NOT_FOUND` | Arbitration sysfs path not found |

**Sources:** [include/dragonChassisBase.hpp:209-252]()

## Image Loading Infrastructure

### Image Loading Process

The `loadImage()` method handles firmware image file operations:

```mermaid
flowchart TD
    Start["loadImage()"]
    Start --> CheckName{"imageName != NULL"}
    CheckName -->|No| ErrorOpen["ERROR_OPEN_IMAGE"]
    CheckName -->|Yes| OpenFile["open(imageName, O_RDONLY)"]
    
    OpenFile --> CheckFd{"fd < 0"}
    CheckFd -->|Yes| ErrorOpen
    CheckFd -->|No| StatFile["stat(imageName, &st)"]
    
    StatFile --> CheckStat{"stat() == 0"}
    CheckStat -->|No| ErrorStat["ERROR_STAT_IMAGE"]
    CheckStat -->|Yes| SeekOffset["lseek(fd, imageOffset, SEEK_SET)"]
    
    SeekOffset --> CheckSeek{"lseek != -1"}
    CheckSeek -->|No| ErrorSeek["ERROR_SEEK_IMAGE"]
    CheckSeek -->|Yes| CalcSize["imageSize = st.st_size - imageOffset"]
    
    CalcSize --> CheckSize{"imageSize > 0"}
    CheckSize -->|No| ErrorStat
    CheckSize -->|Yes| Malloc["malloc(imageSize)"]
    
    Malloc --> CheckMalloc{"malloc != NULL"}
    CheckMalloc -->|No| ErrorLoad["ERROR_LOAD_IMAGE"]
    CheckMalloc -->|Yes| ReadFile["read(fd, image, imageSize)"]
    
    ReadFile --> CheckRead{"read == imageSize"}
    CheckRead -->|No| ErrorLoad
    CheckRead -->|Yes| CloseFile["close(fd)"]
    CloseFile --> Success["Return 0"]
    
    ErrorOpen --> End["Return error"]
    ErrorStat --> CloseFile2["close(fd)"]
    ErrorSeek --> CloseFile2
    ErrorLoad --> CloseFile2
    CloseFile2 --> End
```

**Sources:** [include/dragonChassisBase.hpp:375-429]()

### Image Memory Management

The base class maintains image state in protected member variables:

| Member | Type | Purpose |
|--------|------|---------|
| `imageName` | `char*` | Path to firmware image file |
| `image` | `char*` | Pointer to loaded image in memory |
| `imageSize` | `int` | Size of loaded image in bytes |
| `imageOffset` | `int` | Bytes to skip from beginning of file |
| `fd` | `int` | File descriptor for image file |

**Sources:** [include/dragonChassisBase.hpp:259-264]()

The destructor ensures proper cleanup:

```cpp
virtual ~DragonChassisBase() {
    if (image)
        free(image);
}
```

**Sources:** [include/dragonChassisBase.hpp:51-55]()

## Error Handling System

### UpdateError Enumeration

The HAL defines a comprehensive error enumeration with over 40 distinct error codes:

```mermaid
graph LR
    subgraph "Image Operations"
        E1["ERROR_LOAD_IMAGE<br/>ERROR_OPEN_IMAGE<br/>ERROR_STAT_IMAGE<br/>ERROR_SEEK_IMAGE"]
    end
    
    subgraph "Arbitration Operations"
        E2["ERROR_ENABLE_ARB<br/>ERROR_DISABLE_ARB<br/>ERROR_ARB_NOT_FOUND"]
    end
    
    subgraph "I2C Operations"
        E3["ERROR_OPEN_BUS<br/>ERROR_UNLOCK<br/>ERROR_SEND_IMAGE"]
    end
    
    subgraph "CPLD-Specific"
        E4["ERROR_ENABLE_CFG_INTER<br/>ERROR_ERASE<br/>ERROR_ACTIVATE<br/>ERROR_CPLD_REFRESH_*"]
    end
    
    subgraph "Config Operations"
        E5["ERROR_CONFIG_NOT_FOUND<br/>ERROR_CONFIG_FORMAT<br/>ERROR_CONFIG_PARSE_FAILED"]
    end
    
    subgraph "Device Validation"
        E6["ERROR_WRONG_MANUFACTURER<br/>ERROR_WRONG_MODEL<br/>ERROR_INVALID_DEVICE_ID"]
    end
    
    UpdateError["UpdateError Enum"] --> E1
    UpdateError --> E2
    UpdateError --> E3
    UpdateError --> E4
    UpdateError --> E5
    UpdateError --> E6
```

**Sources:** [include/dragonChassisBase.hpp:209-252]()

### Error Reporting

The `printError()` method converts error codes to human-readable messages:

```mermaid
sequenceDiagram
    participant Code as Update Code
    participant PrintError as printError()
    participant Switch as Switch Statement
    participant Logger as phosphor::logging
    participant Console as std::cerr
    
    Code->>PrintError: error code
    PrintError->>Switch: match code
    Switch-->>PrintError: error message string
    PrintError->>Console: std::cerr << msg
    PrintError->>Logger: log<level::ERR>(msg)
```

**Sources:** [include/dragonChassisBase.hpp:62-204]()

Example error code mapping:
- `ERROR_ENABLE_ARB` (2) → "UpdateError::ERROR_ENABLE_ARB"
- `ERROR_LOAD_IMAGE` (1) → "UpdateError::ERROR_LOAD_IMAGE"
- `ERROR_CPLD_REFRESH_FAILED` (29) → "UpdateError::ERROR_CPLD_REFRESH_FAILED"
- Success (0) → "Update was successful"

## DragonCpld Implementation Example

### Class Structure

The `DragonCpld` class demonstrates how device-specific implementations extend `DragonChassisBase`:

```mermaid
classDiagram
    class DragonChassisBase {
        <<abstract>>
        +DragonChassisBase(index, address, arb, image)
        #sendData()
        #loadImage()
        #enableArbitration()
        #sendImage()* abstract
    }
    
    class DragonCpld {
        -int bus
        -int cpldRegBus
        -int cpldRegAddress
        -int cpldRegFd
        -int cpldRawBus
        -int numOfPagesWritten
        -const char* config
        -string devName
        -gpiod::line cpldRefreshGpio
        
        +DragonCpld(cpldDevSel, imageName, config)
        +fwUpdate() int
        #enableConfigurationInterface() int
        #erase(reset) int
        #activate() int
        #validate() int
        #readDeviceId() int
        #readFwVersion() string
        #cleanUp() int
        #waitBusy(wait, errorCode) int
        #readStatusRegister(value) int
        #waitRefresh(result) int
        #loadConfig() int
        #sendImage() int
        -handlHexString(str) int
    }
    
    DragonChassisBase <|-- DragonCpld
```

**Sources:** [cpld_utility/dragonCpld.hpp:28-167]()

### Constructor Parameters

The `DragonCpld` constructor requires additional configuration beyond the base class:

| Parameter | Type | Purpose |
|-----------|------|---------|
| `cpldDevSel` | `int` | Index of CPLD to update |
| `imageName` | `char*` | Path to firmware image file |
| `config` | `const char*` | Path to configuration file containing bus mappings |

**Configuration File Necessity:** The config file is required because CPLD updates involve multiple I2C buses:
- **Arbitrated bus**: Main communication path
- **Raw bus**: Non-arbitrated version for refresh commands (used when arbitration is disabled during activation)
- **Register bus**: Separate bus for CPLD register access

**Sources:** [cpld_utility/dragonCpld.hpp:46]()

### GPIO Refresh Signaling

Dragon CPLD updates require GPIO manipulation for the refresh signal:

```cpp
gpiod::line cpldRefreshGpio;
```

This GPIO line is used to signal the CPLD to refresh its configuration after firmware activation. The implementation uses `libgpiodcxx` for GPIO control.

**Sources:** [cpld_utility/dragonCpld.hpp:70](), [cpld_utility/meson.build:16-21]()

### Lattice Update Flow

The `fwUpdate()` method implements the Lattice CPLD update sequence:

1. **enableConfigurationInterface()**: Enter programming mode
2. **erase()**: Erase existing firmware
3. **sendImage()**: Transfer new firmware data
4. **activate()**: Activate new firmware
5. **validate()**: Verify update success

**Sources:** [cpld_utility/dragonCpld.hpp:49-56]()

## Conditional Compilation

### Build-Time Configuration

The HAL is conditionally compiled based on Meson options:

```mermaid
graph TB
    MesonOptions["meson_options.txt"]
    BuildFlag{"dragon_chassis_cpld<br/>option"}
    
    MesonOptions --> BuildFlag
    
    BuildFlag -->|enabled| AddGPIO["Add libgpiodcxx<br/>dependency"]
    BuildFlag -->|enabled| AddSource["sources +=<br/>dragonCpld.cpp"]
    BuildFlag -->|enabled| AddDefine["cpp_args +=<br/>-DDRAGON_CHASSIS"]
    
    BuildFlag -->|disabled| GenericPath["Use generic<br/>libcpld implementation"]
    
    AddGPIO --> Compile["Compile cpldupdate<br/>with Dragon support"]
    AddSource --> Compile
    AddDefine --> Compile
    
    GenericPath --> CompileGeneric["Compile cpldupdate<br/>without Dragon support"]
```

**Sources:** [cpld_utility/meson.build:16-24]()

### Build Configuration

When `dragon_chassis_cpld` option is enabled:
- **Dependency added**: `libgpiodcxx` (for GPIO line control)
- **Source added**: `dragonCpld.cpp` (Dragon-specific implementation)
- **Compile flag**: `-DDRAGON_CHASSIS` (enables conditional code paths)

When disabled:
- Uses generic `libcpld` C library implementation
- No GPIO dependencies
- No C++ abstraction layer

**Sources:** [cpld_utility/meson.build:1-34]()

## Integration with D-Bus Services

### Version Update Utilities

The HAL utilities integrate with D-Bus services to update firmware version properties after successful updates:

```mermaid
sequenceDiagram
    participant Update as cpldupdate utility
    participant DragonCpld as DragonCpld::fwUpdate()
    participant Utils as utils.cpp
    participant DBus as D-Bus System Bus
    participant Service as com.Nvidia.Cpld
    
    Update->>DragonCpld: Execute update
    DragonCpld-->>Update: Success (0)
    Update->>Utils: setFwVersion(objPath, version)
    Utils->>DBus: new_method_call()<br/>Set property
    DBus->>Service: Update Version property
    Service-->>DBus: PropertiesChanged signal
```

**Sources:** [cpld_utility/utils.cpp:24-48]()

### D-Bus Property Setting

The `setFwVersion()` utility function updates version properties on the D-Bus service:

```cpp
void setFwVersion(const std::string& objPath, const std::string& version)
{
    PropertyValue ver(version);
    setProperty(objPath, "xyz.openbmc_project.Software.Version", "Version", ver);
}
```

- **Service**: `com.Nvidia.Cpld`
- **Interface**: `xyz.openbmc_project.Software.Version`
- **Property**: `Version`
- **Base Path**: `/xyz/openbmc_project/software/`

**Sources:** [cpld_utility/utils.cpp:43-48](), [cpld_utility/utils.hpp:25-27]()

---

**Page Summary**: This Hardware Abstraction Layer provides a robust foundation for Dragon Chassis firmware updates through the `DragonChassisBase` abstract class. It implements I2C arbitration with kernel driver coordination, PEC-enabled data transmission with retry logic, comprehensive error handling with 40+ error codes, and image loading infrastructure. Device-specific implementations like `DragonCpld` extend this base to implement vendor-specific update sequences (e.g., Lattice CPLD flow) while reusing common platform behaviors. The layer is conditionally compiled via Meson build options, enabling a single codebase to support both Dragon Chassis and generic platforms.

---

