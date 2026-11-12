<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/android_env · page 3 Core Architecture · fetched 2026-10-26 -->

# Core System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [android_env/components/coordinator.py](android_env/components/coordinator.py)
- [android_env/components/coordinator_test.py](android_env/components/coordinator_test.py)
- [android_env/components/task_manager.py](android_env/components/task_manager.py)
- [android_env/components/task_manager_test.py](android_env/components/task_manager_test.py)
- [android_env/env_interface.py](android_env/env_interface.py)
- [android_env/environment.py](android_env/environment.py)
- [android_env/environment_test.py](android_env/environment_test.py)
- [android_env/wrappers/base_wrapper.py](android_env/wrappers/base_wrapper.py)
- [android_env/wrappers/base_wrapper_test.py](android_env/wrappers/base_wrapper_test.py)
- [android_env/wrappers/float_pixels_wrapper.py](android_env/wrappers/float_pixels_wrapper.py)
- [android_env/wrappers/last_action_wrapper.py](android_env/wrappers/last_action_wrapper.py)

</details>



This page describes the high-level architecture of AndroidEnv, explaining the core components and their interactions. It covers how data flows through the system during initialization, reset, and stepping of the environment. For specific details about the environment interface itself, see [Environment Interface](#2.1). For configuration details, see [Configuration System](#2.3).

## System Components

AndroidEnv follows a layered architecture with clear separation of concerns between components. The system comprises several key components that work together to provide an RL environment interface to Android devices.

```mermaid
classDiagram
    class AndroidEnv {
        +reset()
        +step()
        +action_spec()
        +observation_spec()
        +task_extras()
        +execute_adb_call()
        +load_state()
        +save_state()
    }
    
    class Coordinator {
        +rl_reset()
        +rl_step()
        +action_spec()
        +observation_spec()
        +execute_adb_call()
        -_launch_simulator()
        -_gather_simulator_signals()
    }
    
    class BaseSimulator {
        <<interface>>
        +launch()
        +get_screenshot()
        +send_touch()
        +send_key()
        +create_adb_controller()
        +create_log_stream()
        +load_state()
        +save_state()
    }
    
    class TaskManager {
        +start()
        +setup_task()
        +reset_task()
        +rl_reset()
        +rl_step()
        +stop()
    }
    
    class DeviceSettings {
        +update()
        +screen_width()
        +screen_height()
        +get_orientation()
    }
    
    class AdbController {
        +execute_command()
    }
    
    AndroidEnv --> Coordinator : delegates to
    AndroidEnv --> TaskManager : uses
    AndroidEnv --> BaseSimulator : interacts with
    
    Coordinator --> BaseSimulator : manages
    Coordinator --> TaskManager : orchestrates
    Coordinator --> DeviceSettings : configures
    Coordinator --> AdbCallParser : uses
    
    DeviceSettings --> BaseSimulator : gets data from
    
    BaseSimulator --> AdbController : creates
    
    note for AndroidEnv "Main environment interface\nimplements dm_env.Environment"
    note for Coordinator "Central orchestration component\nHandles component interaction"
    note for BaseSimulator "Abstract interface for\nsimulator implementations"
    note for TaskManager "Manages task execution\nand determines rewards"
    note for DeviceSettings "Configures and queries\ndevice properties"
```

Sources: [android_env/environment.py:32-191](), [android_env/components/coordinator.py:38-283](), [android_env/components/device_settings.py:41-175]()

### Key Components

1. **AndroidEnv**: The main environment class that implements the dm_env.Environment interface. It delegates most of its functionality to the Coordinator and exposes additional Android-specific methods like task_extras() and execute_adb_call().

2. **Coordinator**: The central orchestration component that manages communication between the simulator, task manager, and device settings. It handles the core RL operations (reset and step) and manages simulator lifecycles.

3. **BaseSimulator**: An abstract interface that defines operations for interacting with Android devices. It has implementations like EmulatorSimulator (real Android emulator) and FakeSimulator (for testing).

4. **TaskManager**: Manages the execution of RL tasks, processing signals from the simulator, and determining rewards and episode termination.

5. **DeviceSettings**: Handles device configuration and provides information about the device such as screen dimensions and orientation.

6. **AdbController/AdbCallParser**: Provides low-level communication with the Android device through the Android Debug Bridge (ADB).

Sources: [android_env/loader.py:47-89](), [android_env/environment.py:32-45](), [android_env/components/coordinator.py:38-60]()

## Initialization Process

The initialization process begins with loading the environment using the `loader.load()` function, which constructs the component hierarchy based on the provided configuration.

```mermaid
sequenceDiagram
    participant Client
    participant Loader
    participant AndroidEnv
    participant Coordinator
    participant TaskManager
    participant Simulator
    participant DeviceSettings
    
    Client->>Loader: load(config)
    Loader->>+Loader: _load_task(config.task)
    Loader->>TaskManager: create TaskManager(task)
    
    alt EmulatorConfig
        Loader->>Loader: _process_emulator_launcher_config()
        Loader->>Simulator: create EmulatorSimulator(config)
    else FakeSimulatorConfig
        Loader->>Simulator: create FakeSimulator(config)
    end
    
    Loader->>DeviceSettings: create DeviceSettings(simulator)
    Loader->>Coordinator: create Coordinator(simulator, task_manager, device_settings)
    Loader->>AndroidEnv: create AndroidEnv(simulator, coordinator, task_manager)
    Loader-->>Client: env
    
    Coordinator->>Simulator: launch()
    Simulator->>Simulator: start emulator process
    Coordinator->>DeviceSettings: update(config.device_settings)
    Coordinator->>TaskManager: start(adb_call_parser_factory, log_stream)
```

Sources: [android_env/loader.py:33-89](), [android_env/components/coordinator.py:116-171]()

## Data Flow During Reset and Step

The reset and step operations involve complex interactions between components. The following diagram illustrates the data flow during these operations.

```mermaid
sequenceDiagram
    participant Agent as "RL Agent"
    participant Env as "AndroidEnv"
    participant Coord as "Coordinator"
    participant Sim as "BaseSimulator"
    participant Task as "TaskManager"
    participant Device as "DeviceSettings"
    
    %% Reset Flow
    Agent->>Env: reset()
    Env->>Coord: rl_reset()
    
    alt simulator needs restart
        Coord->>Coord: _launch_simulator()
        Coord->>Sim: launch()
        Coord->>Device: update(device_settings)
        Coord->>Task: start(...)
        Coord->>Task: setup_task()
    end
    
    Coord->>Sim: get_screenshot()
    Sim-->>Coord: screenshot
    Coord->>Device: get_orientation()
    Device-->>Coord: orientation
    Coord->>Coord: _gather_simulator_signals()
    Coord->>Task: rl_reset(simulator_signals)
    Task-->>Coord: timestep
    Coord-->>Env: timestep
    Env->>Env: process observation/extras
    Env-->>Agent: timestep
    
    %% Step Flow
    Agent->>Env: step(action)
    Env->>Coord: rl_step(action)
    Coord->>Sim: send_touch/send_key
    Sim-->>Coord: result
    Coord->>Sim: get_screenshot()
    Sim-->>Coord: screenshot
    Coord->>Device: get_orientation()
    Device-->>Coord: orientation
    Coord->>Coord: _gather_simulator_signals()
    Coord->>Task: rl_step(simulator_signals)
    Task-->>Coord: timestep
    Coord-->>Env: timestep
    Env->>Env: process observation/extras
    Env-->>Agent: timestep
```

Sources: [android_env/environment.py:66-114](), [android_env/components/coordinator.py:182-248]()

### Reset Process

1. The agent calls `reset()` on AndroidEnv
2. AndroidEnv delegates to Coordinator's `rl_reset()`
3. Coordinator checks if the simulator needs restarting and launches it if necessary
4. Coordinator executes a lift action to ensure all fingers are lifted
5. Coordinator collects simulator signals (screenshot, orientation, timedelta)
6. TaskManager processes these signals and determines the initial timestep
7. AndroidEnv processes the timestep and returns it to the agent

### Step Process

1. The agent calls `step(action)` on AndroidEnv
2. AndroidEnv delegates to Coordinator's `rl_step(action)`
3. Coordinator sends the action to the simulator
4. Coordinator collects simulator signals
5. TaskManager processes these signals and determines the next timestep
6. AndroidEnv processes the timestep and returns it to the agent

## Component Communication

Components communicate primarily through method calls, with the Coordinator orchestrating most interactions. The following diagram illustrates the communication patterns between components.

```mermaid
graph TD
    subgraph "Client Application"
        Agent["RL Agent"]
    end
    
    subgraph "AndroidEnv Framework"
        AndroidEnv["AndroidEnv Class"]
        Coordinator["Coordinator Class"]
        TaskManager["TaskManager Class"]
        DeviceSettings["DeviceSettings Class"]
        
        subgraph "Simulator Component"
            BaseSimulator["BaseSimulator Interface"]
            EmulatorSim["EmulatorSimulator"]
            FakeSim["FakeSimulator"]
        end
        
        subgraph "Communication Components"
            AdbCallParser["AdbCallParser Class"]
            AdbController["AdbController Class"]
            LogStream["LogStream Interface"]
        end
    end
    
    subgraph "Android Device"
        Emulator["Android Emulator/Device"]
    end
    
    %% Client to Environment
    Agent -->|"reset(), step()"| AndroidEnv
    
    %% Main component flows
    AndroidEnv -->|"delegates"| Coordinator
    Coordinator -->|"manages"| BaseSimulator
    Coordinator -->|"orchestrates"| TaskManager
    Coordinator -->|"configures"| DeviceSettings
    
    %% Simulator relationships
    BaseSimulator -->|"implemented by"| EmulatorSim
    BaseSimulator -->|"implemented by"| FakeSim
    EmulatorSim -->|"controls"| Emulator
    
    %% Communication relationships
    EmulatorSim -->|"creates"| AdbController
    EmulatorSim -->|"creates"| LogStream
    Coordinator -->|"creates"| AdbCallParser
    AdbCallParser -->|"uses"| AdbController
    AdbController -->|"sends commands to"| Emulator
    LogStream -->|"receives logs from"| Emulator
    DeviceSettings -->|"queries"| BaseSimulator
    
    %% Additional connections
    TaskManager -->|"monitors"| LogStream
```

Sources: [android_env/environment.py:32-191](), [android_env/components/coordinator.py:38-283](), [android_env/loader.py:47-89]()

## Error Handling and Recovery

The AndroidEnv system includes robust error handling and recovery mechanisms, primarily managed by the Coordinator. The following diagram illustrates the error handling flow.

```mermaid
flowchart TD
    Start["Environment Operation\n(reset/step)"]
    Check["Check Simulator Health"]
    Periodic["Check for Periodic\nRestart Time"]
    
    Error1["Error During\nAction Execution"]
    Error2["Error During\nObservation Retrieval"]
    Error3["Error During\nTask Setup"]
    
    Relaunch["Relaunch Simulator\n_launch_simulator()"]
    MaxRetries["Check Max\nRetry Count"]
    TooMany["Raise TooManyRestartsError"]
    
    Recovery["Continue Operation\nwith Recovered State"]
    
    Start --> Check
    Check -->|"Healthy"| Periodic
    Check -->|"Unhealthy"| Relaunch
    
    Periodic -->|"Time to restart"| Relaunch
    Periodic -->|"Continue"| Recovery
    
    Error1 -->|"Mark simulator unhealthy\nIncrement relaunch_count_execute_action"| Check
    Error2 -->|"Mark simulator unhealthy\nIncrement relaunch_count_fetch_observation"| Check
    Error3 -->|"Increment relaunch_count_setup_steps"| MaxRetries
    
    Relaunch --> MaxRetries
    MaxRetries -->|"Retries < Max"| Relaunch
    MaxRetries -->|"Retries >= Max"| TooMany
    
    Relaunch -->|"Success"| Recovery
```

Sources: [android_env/components/coordinator.py:95-115](), [android_env/components/coordinator.py:116-171](), [android_env/components/coordinator.py:226-248]()

Key error handling features:

1. **Health Monitoring**: The Coordinator tracks simulator health and triggers relaunches when necessary
2. **Periodic Restarts**: Optional periodic restarts prevent stale states during long-running sessions
3. **Retry Limits**: Configurable retry limits prevent infinite restart loops
4. **Error Statistics**: Detailed error statistics are collected and accessible via the stats() method
5. **Graceful Degradation**: When errors occur during a step, the environment can often continue with partial data

## Component Responsibilities

### AndroidEnv
- Implements the dm_env.Environment interface
- Processes observations and extras
- Maintains episode state
- Provides additional Android-specific methods

### Coordinator
- Central orchestration component
- Manages simulator lifecycle
- Processes actions and observations
- Handles error recovery
- Connects components together

### TaskManager
- Manages task execution
- Processes simulator signals
- Determines rewards and episode termination
- Monitors task progress

### BaseSimulator
- Provides interface for Android interaction
- Sends actions to device
- Gets screenshots and logs
- Manages device communication

### DeviceSettings
- Configures device properties
- Retrieves device information
- Manages screen and orientation settings

Sources: [android_env/environment.py:32-45](), [android_env/components/coordinator.py:38-60](), [android_env/components/device_settings.py:41-86]()

## Configuration Hierarchy

The configuration system uses a hierarchical structure of dataclasses to configure different components of the environment.

```mermaid
classDiagram
    class AndroidEnvConfig {
        +task: TaskConfig
        +task_manager: TaskManagerConfig
        +coordinator: CoordinatorConfig
        +simulator: SimulatorConfig
    }
    
    class TaskConfig {
        <<abstract>>
        +tmp_dir: str
    }
    
    class FilesystemTaskConfig {
        +path: str
    }
    
    class TaskManagerConfig {
        +max_bad_states: int
        +dumpsys_check_frequency: int
        +max_failed_current_activity: int
        +extras_max_buffer_size: int
    }
    
    class CoordinatorConfig {
        +num_fingers: int
        +enable_key_events: bool
        +periodic_restart_time_min: float
        +device_settings: DeviceSettingsConfig
    }
    
    class DeviceSettingsConfig {
        +show_touches: bool
        +show_pointer_location: bool
        +show_status_bar: bool
        +show_navigation_bar: bool
    }
    
    class SimulatorConfig {
        <<abstract>>
        +verbose_logs: bool
        +interaction_rate_sec: float
    }
    
    class EmulatorConfig {
        +emulator_launcher: EmulatorLauncherConfig
        +adb_controller: AdbControllerConfig
        +logfile_path: str
        +launch_n_times_without_reboot: int
        +launch_n_times_without_reinstall: int
    }
    
    class FakeSimulatorConfig {
        +screen_dimensions: tuple[int, int]
    }
    
    AndroidEnvConfig *-- TaskConfig
    AndroidEnvConfig *-- TaskManagerConfig
    AndroidEnvConfig *-- CoordinatorConfig
    AndroidEnvConfig *-- SimulatorConfig
    
    TaskConfig <|-- FilesystemTaskConfig
    
    SimulatorConfig <|-- EmulatorConfig
    SimulatorConfig <|-- FakeSimulatorConfig
```

Sources: [android_env/components/config_classes.py:16-204]()

The configuration system is used during environment initialization to create and configure all components. The loader uses this configuration to instantiate the components in the correct order and with the appropriate settings.

## Integration with dm_env Interface

AndroidEnv implements the standard dm_env.Environment interface, which is used by most DeepMind RL agents. The following table shows how AndroidEnv maps its functionality to the dm_env interface:

| dm_env Method | AndroidEnv Implementation | Description |
|---------------|---------------------------|-------------|
| reset() | Delegates to Coordinator.rl_reset() | Resets the environment for a new episode |
| step(action) | Delegates to Coordinator.rl_step(action) | Executes an action and returns the next timestep |
| action_spec() | Delegates to Coordinator.action_spec() | Returns the action specification |
| observation_spec() | Delegates to Coordinator.observation_spec() | Returns the observation specification |

Sources: [android_env/environment.py:59-114](), [android_env/env_interface.py:31-110]()

In addition to the standard dm_env interface, AndroidEnv provides several additional methods to support Android-specific functionality:

- **task_extras()**: Returns extra information from the task
- **execute_adb_call()**: Executes an ADB command on the device
- **load_state()**: Loads a saved simulator state
- **save_state()**: Saves the current simulator state
- **stats()**: Returns internal statistics about the environment

Sources: [android_env/environment.py:127-190](), [android_env/env_interface.py:58-109]()

---

