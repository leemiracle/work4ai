<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/jetson-gpio · page 6 Internal Architecture · fetched 2026-10-26 -->

# Internal Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/python/Jetson/GPIO/gpio.py](lib/python/Jetson/GPIO/gpio.py)
- [lib/python/Jetson/GPIO/gpio_cdev.py](lib/python/Jetson/GPIO/gpio_cdev.py)
- [lib/python/Jetson/GPIO/gpio_event.py](lib/python/Jetson/GPIO/gpio_event.py)
- [lib/python/Jetson/GPIO/gpio_pin_data.py](lib/python/Jetson/GPIO/gpio_pin_data.py)

</details>



This document explains the internal design and implementation of the Jetson.GPIO library. It covers the core components, interactions, and mechanisms that enable GPIO control on NVIDIA Jetson platforms. For API usage information, see [API Reference](#3), and for hardware-specific details, see [Hardware Support](#4).

## Overall Architecture

The Jetson.GPIO library uses a layered architecture to provide Python interfaces for controlling GPIO pins on NVIDIA Jetson platforms. The library implements both a Jetson-specific API (`Jetson.GPIO`) and a Raspberry Pi-compatible API (`RPi.GPIO`) for easier code portability.

```mermaid
flowchart TD
    subgraph "Application Layer"
        App["User Applications"]
        RPi["RPi.GPIO Compatibility Layer"]
    end
    
    subgraph "API Layer"
        GPIO["Jetson.GPIO Python API"]
    end
    
    subgraph "Core Layer"
        Core["gpio.py - Core Implementation"]
        PinData["gpio_pin_data.py - Board Detection and Pin Mapping"]
        Event["gpio_event.py - Event Detection"]
    end
    
    subgraph "Hardware Interface Layer"
        CDEV["gpio_cdev.py - Character Device Interface"]
        PWM["PWM Interface (sysfs)"]
    end
    
    subgraph "Linux Kernel"
        LinuxGPIO["/dev/gpiochipX Character Devices"]
        LinuxPWM["/sys/class/pwm/ Interface"]
    end
    
    App --> GPIO
    App --> RPi
    RPi --> GPIO
    GPIO --> Core
    Core --> PinData
    Core --> Event
    Core --> CDEV
    Core --> PWM
    CDEV --> LinuxGPIO
    PWM --> LinuxPWM
```

Sources: [lib/python/Jetson/GPIO/gpio.py:1-653](), [lib/python/Jetson/GPIO/gpio_pin_data.py:1-664](), [lib/python/Jetson/GPIO/gpio_event.py:1-518](), [lib/python/Jetson/GPIO/gpio_cdev.py:1-285]()

## Core Components

The library is structured around four primary modules, each with distinct responsibilities:

### 1. GPIO Pin Data Module

The `gpio_pin_data.py` module handles board detection and pin mapping. It contains:
- Pin definitions for all supported Jetson boards
- Logic to detect which Jetson board the code is running on
- Mapping between various pin numbering modes (BOARD, BCM, CVM, TEGRA_SOC)

```mermaid
flowchart TD
    A["get_data()"] --> B["get_model()"]
    B --> C{"Detect Board Type"}
    C --> D["JETSON_ORIN"]
    C --> E["JETSON_XAVIER"]
    C --> F["JETSON_TX2"]
    C --> G["JETSON_TX1"]
    C --> H["JETSON_NANO"]
    
    D --> I["Load JETSON_ORIN_PIN_DEFS"]
    E --> J["Load JETSON_XAVIER_PIN_DEFS"]
    F --> K["Load JETSON_TX2_PIN_DEFS"]
    G --> L["Load JETSON_TX1_PIN_DEFS"]
    H --> M["Load JETSON_NANO_PIN_DEFS"]
    
    I --> N["Create channel_data dictionary"]
    J --> N
    K --> N
    L --> N
    M --> N
    
    N --> O["Return model, info, and channel_data"]
```

Sources: [lib/python/Jetson/GPIO/gpio_pin_data.py:499-664]()

### 2. Core GPIO Module

The `gpio.py` module implements the main functionality and API of the library:
- Pin setup and configuration
- Input/output operations
- PWM control
- Clean-up functions

```mermaid
flowchart TD
    A["setmode()"] --> B["_channel_data selection"]
    
    C["setup()"] --> D["_channels_to_infos()"]
    D --> E{"Direction is OUT?"}
    E -->|"Yes"| F["_do_one_channel() with initial value"]
    E -->|"No"| G["_do_one_channel() without initial value"]
    
    H["input()"] --> I["_channel_to_info()"]
    I --> J["gpio_cdev.get_value()"]
    
    K["output()"] --> L["_channels_to_infos()"]
    L --> M["gpio_cdev.set_value()"]
    
    N["cleanup()"] --> O{"Channel specified?"}
    O -->|"Yes"| P["_cleanup_one()"]
    O -->|"No"| Q["_cleanup_all()"]
```

Sources: [lib/python/Jetson/GPIO/gpio.py:21-653]()

### 3. GPIO Event Detection

The `gpio_event.py` module handles event detection and callback management:
- Non-blocking edge detection with callbacks
- Blocking edge detection
- Event management and cleanup

```mermaid
flowchart TD
    A["add_event_detect()"] --> B["_add_gpio_event()"]
    B --> C["Set up epoll monitoring"]
    C --> D["Start event handler thread"]
    
    E["_edge_handler() Thread"] --> F["epoll.poll() for events"]
    F --> G{"Event detected?"}
    G -->|"Yes"| H["Process event"]
    G -->|"No"| F
    H --> I{"Within bouncetime?"}
    I -->|"No"| J["Set event_occurred flag"]
    J --> K["Execute callbacks"]
    I -->|"Yes"| F
    
    L["wait_for_edge()"] --> M["blocking_wait_for_edge()"]
    M --> N["select.select() for events"]
```

Sources: [lib/python/Jetson/GPIO/gpio_event.py:21-518]()

### 4. Character Device Interface

The `gpio_cdev.py` module provides the interface to the Linux GPIO character device API:
- Opening and closing GPIO chips and lines
- Reading and writing GPIO values
- Creating and managing GPIO event requests

```mermaid
flowchart TD
    A["chip_open_by_label()"] --> B["Search for gpiochip devices"]
    B --> C["chip_check_info()"]
    C --> D["Return chip file descriptor"]
    
    E["open_line()"] --> F["ioctl(GPIO_GET_LINEHANDLE_IOCTL)"]
    F --> G["Store line handle in ch_info"]
    
    H["get_value()"] --> I["ioctl(GPIOHANDLE_GET_LINE_VALUES_IOCTL)"]
    I --> J["Return line value"]
    
    K["set_value()"] --> L["ioctl(GPIOHANDLE_SET_LINE_VALUES_IOCTL)"]
```

Sources: [lib/python/Jetson/GPIO/gpio_cdev.py:20-285]()

## Pin Mapping and Board Detection

The library supports multiple Jetson boards and provides several pin numbering modes. This system allows users to write portable code across different boards.

### Board Detection

The library automatically detects the Jetson board type by:
1. Reading `/proc/device-tree/compatible` to identify the board model
2. Using compatible strings to match known Jetson platforms
3. Falling back to the `JETSON_MODEL_NAME` environment variable for Docker containers

```mermaid
flowchart TD
    A["get_model()"] --> B["Read /proc/device-tree/compatible"]
    B --> C{"Match against\nknown compatibles"}
    
    C -->|"TX1 match"| D["Return JETSON_TX1"]
    C -->|"TX2 match"| E["Return JETSON_TX2"]
    C -->|"Xavier match"| F["Return JETSON_XAVIER"]
    C -->|"Nano match"| G["Return JETSON_NANO"]
    C -->|"Orin match"| H["Return JETSON_ORIN"]
    C -->|"No match"| I["Check JETSON_MODEL_NAME env"]
    
    I --> J{"Valid model name?"}
    J -->|"Yes"| K["Return model name"]
    J -->|"No"| L["Raise Exception"]
```

Sources: [lib/python/Jetson/GPIO/gpio_pin_data.py:499-607]()

### Pin Numbering Modes

The library supports four pin numbering modes:

1. **BOARD** - Physical pin numbering on the 40-pin header
2. **BCM** - Broadcom SoC pin numbering (for Raspberry Pi compatibility)
3. **CVM** - NVIDIA Computer Vision Module pin naming
4. **TEGRA_SOC** - Tegra SoC-specific pin naming

```mermaid
flowchart LR
    A["Pin Definitions Array"] --> B["channel_data Dictionary"]
    
    B --> C["BOARD Mode Mapping"]
    B --> D["BCM Mode Mapping"]
    B --> E["CVM Mode Mapping"]
    B --> F["TEGRA_SOC Mode Mapping"]
    
    G["setmode(mode)"] --> H["Select appropriate mapping"]
    H --> I["_channel_data = _channel_data_by_mode[mode]"]
```

Sources: [lib/python/Jetson/GPIO/gpio_pin_data.py:36-52](), [lib/python/Jetson/GPIO/gpio.py:38-42](), [lib/python/Jetson/GPIO/gpio.py:287-306]()

## GPIO Operations Flow

This section explains the sequence of operations for the most common GPIO tasks.

### Pin Setup and Configuration

When a GPIO pin is configured using `setup()`:

```mermaid
sequenceDiagram
    participant A as "User Code"
    participant B as "gpio.py"
    participant C as "gpio_pin_data.py"
    participant D as "gpio_cdev.py"
    participant E as "Linux Kernel"
    
    A->>B: GPIO.setup(channel, direction)
    B->>C: _channels_to_infos(channel)
    C-->>B: channel_info
    B->>B: _do_one_channel(ch_info, direction, initial)
    B->>D: chip_open_by_label(ch_info.gpio_chip)
    D->>E: os.open("/dev/gpiochipX")
    E-->>D: chip_fd
    D-->>B: chip_fd
    B->>D: request_handle(line_offset, direction, initial)
    D-->>B: request
    B->>D: open_line(ch_info, request)
    D->>E: ioctl(GPIO_GET_LINEHANDLE_IOCTL)
    E-->>D: line_handle
    D->>B: Update ch_info.line_handle
    B->>B: _channel_configuration[channel] = direction
```

Sources: [lib/python/Jetson/GPIO/gpio.py:326-363](), [lib/python/Jetson/GPIO/gpio.py:151-162]()

### Reading and Writing GPIO Values

Input/output operations flow:

```mermaid
sequenceDiagram
    participant A as "User Code"
    participant B as "gpio.py"
    participant C as "gpio_cdev.py"
    participant D as "Linux Kernel"
    
    Note over A,D: Reading a GPIO value
    A->>B: GPIO.input(channel)
    B->>B: _channel_to_info(channel)
    B->>C: get_value(ch_info.line_handle)
    C->>D: ioctl(GPIOHANDLE_GET_LINE_VALUES_IOCTL)
    D-->>C: data.values[0]
    C-->>B: value
    B-->>A: value
    
    Note over A,D: Writing a GPIO value
    A->>B: GPIO.output(channel, value)
    B->>B: _channels_to_infos(channels)
    B->>C: set_value(ch_info.line_handle, value)
    C->>D: ioctl(GPIOHANDLE_SET_LINE_VALUES_IOCTL)
    D-->>C: status
    C-->>B: status
    B-->>A: status
```

Sources: [lib/python/Jetson/GPIO/gpio.py:392-419](), [lib/python/Jetson/GPIO/gpio_cdev.py:263-283]()

## Event Handling System

The event handling system enables detection of GPIO pin state changes. It offers three different approaches for detecting events:

1. Polling - Simple checking of current pin value
2. Blocking wait - Wait for an event on a specific pin
3. Event detection with callbacks - Non-blocking detection with callbacks

### Event Detection Mechanism

The event detection system uses the Linux GPIO character device event interface and `epoll` to detect edge events efficiently:

```mermaid
flowchart TD
    A["add_event_detect()"] --> B["_channel_to_info()"]
    B --> C["gpio_cdev.request_event()"]
    C --> D["event.add_edge_detect()"]
    
    D --> E["Create epoll object"]
    E --> F["Register fd with epoll"]
    F --> G["Start _edge_handler thread"]
    
    G --> H["epoll.poll() with timeout"]
    H --> I{"Event detected?"}
    I -->|"No"| H
    I -->|"Yes"| J["Read event data"]
    
    J --> K{"Within bouncetime?"}
    K -->|"Yes"| H
    K -->|"No"| L["Set event_occurred flag"]
    
    L --> M{"Callbacks registered?"}
    M -->|"Yes"| N["Execute callbacks"]
    N --> H
    M -->|"No"| H
    
    O["event_detected()"] --> P["Check and clear event_occurred flag"]
```

Sources: [lib/python/Jetson/GPIO/gpio.py:429-464](), [lib/python/Jetson/GPIO/gpio_event.py:104-169](), [lib/python/Jetson/GPIO/gpio_event.py:349-445]()

### Callback Handling

Callbacks are managed through a list in the GPIO event object:

```mermaid
sequenceDiagram
    participant A as "User Code"
    participant B as "gpio.py"
    participant C as "gpio_event.py"
    participant D as "Event Thread"
    
    A->>B: add_event_callback(channel, callback)
    B->>C: add_edge_callback(chip, channel, callback)
    C->>C: _gpio_event_list[chip][channel].callbacks.append(callback)
    
    Note over D: When event occurs
    D->>D: event detected
    D->>C: Execute callbacks in callback list
    C->>A: callback(channel)
```

Sources: [lib/python/Jetson/GPIO/gpio.py:488-504](), [lib/python/Jetson/GPIO/gpio_event.py:212-226]()

## PWM Implementation

Pulse Width Modulation (PWM) is implemented using the Linux sysfs interface for hardware PWM control.

### PWM Class Structure

```mermaid
classDiagram
    class PWM {
        +__init__(channel, frequency_hz)
        +start(duty_cycle_percent)
        +ChangeFrequency(frequency_hz)
        +ChangeDutyCycle(duty_cycle_percent)
        +stop()
        -_reconfigure(frequency_hz, duty_cycle_percent, start)
    }
```

Sources: [lib/python/Jetson/GPIO/gpio.py:571-652]()

### PWM Operations Flow

The PWM functionality follows this sequence of operations:

```mermaid
sequenceDiagram
    participant A as "User Code"
    participant B as "PWM Class"
    participant C as "gpio.py helpers"
    participant D as "Linux sysfs"
    
    A->>B: PWM(channel, frequency)
    B->>C: _export_pwm(ch_info)
    C->>D: Write to /sys/class/pwm/export
    B->>C: _set_pwm_duty_cycle(ch_info, 0)
    C->>D: Write to pwm/pwmX/duty_cycle
    B->>C: _set_pwm_period(ch_info, period_ns)
    C->>D: Write to pwm/pwmX/period
    
    A->>B: start(duty_cycle_percent)
    B->>B: _reconfigure(frequency, duty_cycle, start=True)
    B->>C: _set_pwm_duty_cycle(ch_info, duty_cycle_ns)
    C->>D: Write to pwm/pwmX/duty_cycle
    B->>C: _enable_pwm(ch_info)
    C->>D: Write "1" to pwm/pwmX/enable
    
    A->>B: stop()
    B->>C: _disable_pwm(ch_info)
    C->>D: Write "0" to pwm/pwmX/enable
```

Sources: [lib/python/Jetson/GPIO/gpio.py:166-239](), [lib/python/Jetson/GPIO/gpio.py:571-652]()

## Memory Management and Resource Handling

The library manages resources carefully to avoid leaks and ensure proper cleanup:

```mermaid
flowchart TD
    A["setup()"] --> B["Create line_handle"]
    
    C["cleanup()"] --> D{"Channel specified?"}
    D -->|"Yes"| E["_cleanup_one()"]
    D -->|"No"| F["_cleanup_all()"]
    
    E --> G["event_cleanup()"]
    E --> H["Close line_handle"]
    E --> I["Close chip_fd"]
    
    J["PWM.__del__()"] --> K["stop()"]
    K --> L["_unexport_pwm()"]
    
    M["add_event_detect()"] --> N["Register event"]
    M --> O["Start monitoring thread"]
    
    P["remove_event_detect()"] --> Q["Signal thread to stop"]
    Q --> R["Unregister from epoll"]
    R --> S["Clean up resources"]
```

Sources: [lib/python/Jetson/GPIO/gpio.py:241-276](), [lib/python/Jetson/GPIO/gpio.py:370-387](), [lib/python/Jetson/GPIO/gpio_event.py:179-204]()

## Thread Safety and Synchronization

The event handling system uses thread synchronization to prevent race conditions:

1. A mutex lock (`_mutex`) protects access to shared data structures
2. Thread states are tracked in a dictionary (`_thread_running_dict`)
3. Thread exit states are monitored to ensure proper cleanup

```mermaid
sequenceDiagram
    participant A as "Main Thread"
    participant B as "Mutex"
    participant C as "Event Thread"
    participant D as "Shared Data"
    
    A->>B: acquire()
    A->>D: Update _gpio_event_list
    A->>D: Update _thread_running_dict
    A->>B: release()
    
    C->>B: acquire()
    C->>D: Read _thread_running_dict[thread_id]
    C->>B: release()
    
    Note over C: Process events if running
    
    C->>B: acquire()
    C->>D: Update event_occurred flag
    C->>B: release()
    
    A->>B: acquire()
    A->>D: Set _thread_running_dict[thread_id] = False
    A->>B: release()
    
    C->>B: acquire()
    C->>D: Set thread_exited = True
    C->>B: release()
```

Sources: [lib/python/Jetson/GPIO/gpio_event.py:76-80](), [lib/python/Jetson/GPIO/gpio_event.py:349-445]()

---

