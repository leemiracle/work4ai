<!-- source: DeepWiki mcp.deepwiki.com · repo zai-org/Open-AutoGLM · page 3 Architecture · fetched 2026-10-29 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README_coding_agent.md](README_coding_agent.md)
- [README_en.md](README_en.md)
- [phone_agent/agent.py](phone_agent/agent.py)
- [phone_agent/device_factory.py](phone_agent/device_factory.py)

</details>



This document describes the high-level architecture of Open-AutoGLM, a multi-platform mobile automation framework powered by vision-language models. It covers the system's layered design, core components, data flow patterns, and abstraction mechanisms that enable cross-platform device control.

For detailed implementation of specific subsystems, see [System Overview](#3.1), [Core Components](#3.2), [Agent Execution Loop](#3.3), [AI Model Integration](#3.4), and [Device Communication Layer](#3.5).

For practical usage information, see [Getting Started](#2) and [User Guide](#5).

## System Layers

Open-AutoGLM is organized into five distinct architectural layers, each with specific responsibilities:

```mermaid
graph TB
    subgraph "Layer 1: User Interface"
        CLI["main.py CLI<br/>Command-line interface"]
        API["Python API<br/>PhoneAgent/IOSPhoneAgent classes"]
    end
    
    subgraph "Layer 2: Agent Logic"
        PA["PhoneAgent<br/>(phone_agent/agent.py)"]
        IPA["IOSPhoneAgent<br/>(phone_agent/agent_ios.py)"]
        AC["AgentConfig<br/>IOSAgentConfig"]
    end
    
    subgraph "Layer 3: AI Intelligence"
        MC["ModelClient<br/>(phone_agent/model/client.py)"]
        MCFG["ModelConfig<br/>API settings"]
    end
    
    subgraph "Layer 4: Action Execution"
        AH["ActionHandler<br/>(phone_agent/actions/handler.py)"]
        PARSER["Action parsing<br/>validation"]
    end
    
    subgraph "Layer 5: Device Abstraction"
        DF["DeviceFactory<br/>(phone_agent/device_factory.py)"]
        ADB["ADBConnection<br/>(phone_agent/adb/)"]
        HDC["HDCConnection<br/>(phone_agent/hdc/)"]
        WDA["XCTestConnection<br/>(phone_agent/xctest/)"]
    end
    
    subgraph "Configuration Layer (Cross-cutting)"
        APPS["APP_PACKAGES<br/>(phone_agent/config/apps*.py)"]
        PROMPTS["System Prompts<br/>(phone_agent/config/prompts*.py)"]
        TIMING["Timing Config<br/>(phone_agent/config/timing.py)"]
    end
    
    CLI --> PA
    CLI --> IPA
    API --> PA
    API --> IPA
    
    PA --> AC
    IPA --> AC
    PA --> MC
    IPA --> MC
    PA --> AH
    IPA --> AH
    
    MC --> MCFG
    AH --> PARSER
    
    PA --> DF
    IPA -.->|"uses XCTestConnection<br/>directly"| WDA
    DF --> ADB
    DF --> HDC
    
    PA --> APPS
    PA --> PROMPTS
    AH --> TIMING
```

**Sources:** [main.py:1-854](), [phone_agent/agent.py](), [phone_agent/agent_ios.py](), [phone_agent/model/client.py](), [phone_agent/actions/handler.py](), [phone_agent/device_factory.py]()

### Layer Responsibilities

| Layer | Components | Responsibilities |
|-------|-----------|------------------|
| **User Interface** | `main.py`, Python API | Command parsing, interactive mode, system checks |
| **Agent Logic** | `PhoneAgent`, `IOSPhoneAgent`, configs | Task orchestration, message management, callback handling |
| **AI Intelligence** | `ModelClient`, `ModelConfig` | OpenAI-compatible API communication, response parsing |
| **Action Execution** | `ActionHandler` | Action validation, coordinate transformation, device operation dispatch |
| **Device Abstraction** | `DeviceFactory`, connection classes | Platform-specific device control, screenshot capture, input methods |
| **Configuration** | `APP_PACKAGES`, prompts, timing | Application mappings, system prompts, operational parameters |

**Sources:** [main.py:1-854](), [phone_agent/agent.py](), [phone_agent/actions/handler.py](), [phone_agent/device_factory.py]()

## Core Component Interaction

The following diagram shows how the primary code entities interact during task execution:

```mermaid
sequenceDiagram
    participant User
    participant main["main.py"]
    participant PA["PhoneAgent<br/>(agent.py)"]
    participant MC["ModelClient<br/>(model/client.py)"]
    participant AH["ActionHandler<br/>(actions/handler.py)"]
    participant DF["DeviceFactory<br/>(device_factory.py)"]
    participant Device["Device Module<br/>(adb/hdc/xctest)"]
    
    User->>main: python main.py "task"
    main->>main: parse_args()
    main->>main: check_system_requirements()
    main->>main: check_model_api()
    
    main->>PA: PhoneAgent(model_config, agent_config)
    main->>PA: run(task)
    
    loop "max_steps iterations"
        PA->>DF: capture_screenshot()
        DF->>Device: screenshot command
        Device-->>DF: image bytes
        DF-->>PA: screenshot image
        
        PA->>PA: _build_messages(screenshot)
        PA->>MC: request(messages)
        MC->>MC: _prepare_request()
        MC-->>PA: ModelResponse(thinking, action)
        
        PA->>PA: _parse_action(response)
        PA->>AH: execute(action, screen_size, device_id)
        
        alt "Normal Action"
            AH->>DF: device operation
            DF->>Device: adb/hdc/wda command
            Device-->>DF: result
            DF-->>AH: execution result
        else "Sensitive Action"
            AH->>User: confirmation_callback()
            User-->>AH: approval
        else "Take_over Action"
            AH->>User: takeover_callback()
            User-->>AH: completion signal
        end
        
        AH-->>PA: ActionResult
        
        alt "Task Complete"
            PA-->>main: success message
        else "Max Steps"
            PA-->>main: max steps reached
        end
    end
    
    main-->>User: display result
```

**Sources:** [main.py:684-853](), [phone_agent/agent.py](), [phone_agent/model/client.py](), [phone_agent/actions/handler.py](), [phone_agent/device_factory.py]()

## Device Factory Pattern

Open-AutoGLM uses the Factory pattern to abstract device-specific implementations behind a unified interface. This enables the same agent logic to control Android, HarmonyOS, and iOS devices.

```mermaid
graph TB
    subgraph "Factory Initialization"
        DT["DeviceType Enum<br/>(device_factory.py)"]
        GDF["get_device_factory()<br/>Global factory accessor"]
        SDT["set_device_type(type)<br/>Global type setter"]
    end
    
    subgraph "Factory Interface"
        DF["DeviceFactory<br/>Abstract factory"]
    end
    
    subgraph "Concrete Factories"
        ADF["ADBDeviceFactory<br/>Android implementation"]
        HDF["HDCDeviceFactory<br/>HarmonyOS implementation"]
        IDF["IOSDeviceFactory<br/>iOS implementation"]
    end
    
    subgraph "Device Modules"
        ADB_MOD["phone_agent.adb<br/>ADBConnection<br/>screenshot.py<br/>input.py<br/>device.py"]
        HDC_MOD["phone_agent.hdc<br/>HDCConnection<br/>screenshot.py<br/>input.py<br/>device.py"]
        IOS_MOD["phone_agent.xctest<br/>XCTestConnection<br/>screenshot.py<br/>input.py<br/>device.py"]
    end
    
    DT --> GDF
    SDT --> GDF
    GDF --> DF
    
    DF --> ADF
    DF --> HDF
    DF --> IDF
    
    ADF --> ADB_MOD
    HDF --> HDC_MOD
    IDF --> IOS_MOD
```

**Sources:** [phone_agent/device_factory.py](), [phone_agent/adb/__init__.py](), [phone_agent/hdc/__init__.py](), [phone_agent/xctest/__init__.py]()

### Factory Methods

Each factory implementation provides standardized methods:

| Method | Return Type | Purpose |
|--------|-------------|---------|
| `get_connection_class()` | `Type[Connection]` | Returns connection class for device type |
| `list_devices()` | `List[DeviceInfo]` | Enumerates connected devices |
| `capture_screenshot(device_id)` | `bytes` | Captures device screen |
| `get_screen_size(device_id)` | `Tuple[int, int]` | Returns screen dimensions |
| `get_current_app(device_id)` | `str` | Gets foreground app package/bundle ID |
| `launch_app(app_name, device_id)` | `bool` | Launches application |
| `tap(x, y, device_id)` | `bool` | Performs tap at coordinates |
| `swipe(start, end, duration, device_id)` | `bool` | Performs swipe gesture |
| `type_text(text, device_id)` | `bool` | Inputs text |
| `press_back(device_id)` | `bool` | Presses back button |
| `press_home(device_id)` | `bool` | Returns to home screen |

**Sources:** [phone_agent/device_factory.py]()

## Agent Configuration Architecture

Configuration flows from multiple sources into structured configuration objects:

```mermaid
graph LR
    subgraph "Configuration Sources"
        ENV["Environment Variables<br/>PHONE_AGENT_*"]
        CLI["CLI Arguments<br/>(main.py argparse)"]
        DEFAULTS["Default Values<br/>(hardcoded)"]
    end
    
    subgraph "Configuration Objects"
        MC["ModelConfig<br/>(model/client.py)<br/>- base_url<br/>- model_name<br/>- api_key<br/>- max_tokens<br/>- temperature"]
        AC["AgentConfig<br/>(agent.py)<br/>- max_steps<br/>- device_id<br/>- lang<br/>- verbose"]
        IAC["IOSAgentConfig<br/>(agent_ios.py)<br/>- wda_url<br/>- device_id"]
    end
    
    subgraph "Runtime Components"
        PA["PhoneAgent<br/>IOSPhoneAgent"]
        MCL["ModelClient"]
        AH["ActionHandler"]
    end
    
    ENV --> MC
    ENV --> AC
    CLI --> MC
    CLI --> AC
    CLI --> IAC
    DEFAULTS --> MC
    DEFAULTS --> AC
    
    MC --> MCL
    AC --> PA
    IAC --> PA
    MCL --> PA
    PA --> AH
```

**Sources:** [main.py:355-524](), [phone_agent/model/client.py](), [phone_agent/agent.py](), [phone_agent/agent_ios.py]()

### Configuration Precedence

Configuration values are resolved in the following order (highest to lowest priority):

1. CLI arguments (e.g., `--base-url`, `--model`)
2. Environment variables (e.g., `PHONE_AGENT_BASE_URL`)
3. Default values in code

**Sources:** [main.py:405-524]()

## Data Flow: Screenshot to Action

The core automation loop transforms visual observations into device actions:

```mermaid
graph TB
    subgraph "Observation Phase"
        SS["Screenshot Capture<br/>(device_factory.py)"]
        ENC["Base64 Encoding<br/>(agent.py)"]
        APP["Get Current App<br/>(device_factory.py)"]
        SIZE["Get Screen Size<br/>(device_factory.py)"]
    end
    
    subgraph "Context Building"
        MSG["Message Construction<br/>(agent.py _build_messages)"]
        HIST["Message History<br/>(agent.py messages list)"]
        PROMPT["System Prompt<br/>(config/prompts_*.py)"]
    end
    
    subgraph "AI Decision"
        REQ["API Request<br/>(model/client.py)"]
        RESP["Model Response<br/>thinking + action"]
        PARSE["Parse Action<br/>(agent.py _parse_action)"]
    end
    
    subgraph "Action Execution"
        VAL["Validate Action<br/>(actions/handler.py)"]
        TRANS["Transform Coordinates<br/>(actions/handler.py)"]
        EXEC["Execute on Device<br/>(device_factory.py)"]
    end
    
    SS --> ENC
    APP --> MSG
    SIZE --> MSG
    ENC --> MSG
    MSG --> HIST
    PROMPT --> MSG
    HIST --> REQ
    
    REQ --> RESP
    RESP --> PARSE
    PARSE --> VAL
    VAL --> TRANS
    TRANS --> EXEC
```

**Sources:** [phone_agent/agent.py](), [phone_agent/model/client.py](), [phone_agent/actions/handler.py](), [phone_agent/device_factory.py]()

## Platform-Specific Implementation Details

Each platform has distinct implementation characteristics:

### Android (ADB)

```mermaid
graph LR
    subgraph "ADB Module (phone_agent/adb/)"
        CONN["connection.py<br/>ADBConnection"]
        SS["screenshot.py<br/>capture_screenshot()"]
        INPUT["input.py<br/>ADB Keyboard integration"]
        DEV["device.py<br/>tap, swipe, launch_app"]
    end
    
    subgraph "ADB Commands"
        SHELL["adb shell"]
        SCREENCAP["screencap -p"]
        MONKEY["monkey -p package"]
        IME["ime set/enable"]
    end
    
    CONN --> SHELL
    SS --> SCREENCAP
    INPUT --> IME
    DEV --> MONKEY
    DEV --> SHELL
```

**Key characteristics:**
- Uses `adb shell` for command execution
- Requires ADB Keyboard app for text input [phone_agent/adb/input.py]()
- Screenshot via `screencap -p` command [phone_agent/adb/screenshot.py]()
- Supports USB and WiFi connections [phone_agent/adb/connection.py]()

**Sources:** [phone_agent/adb/]()

### HarmonyOS (HDC)

```mermaid
graph LR
    subgraph "HDC Module (phone_agent/hdc/)"
        CONN["connection.py<br/>HDCConnection"]
        SS["screenshot.py<br/>capture_screenshot()"]
        INPUT["input.py<br/>Native input"]
        DEV["device.py<br/>uitest commands"]
    end
    
    subgraph "HDC Commands"
        SHELL["hdc shell"]
        SNAP["snapshot_display -f"]
        UITEST["uitest uiInput<br/>click, inputText"]
        AA["aa start"]
    end
    
    CONN --> SHELL
    SS --> SNAP
    INPUT --> UITEST
    DEV --> UITEST
    DEV --> AA
```

**Key characteristics:**
- Uses `hdc shell` for command execution
- Native input via `uitest uiInput` (no keyboard app needed) [phone_agent/hdc/input.py]()
- Screenshot via `snapshot_display` command [phone_agent/hdc/screenshot.py]()
- App launch via `aa start` (Ability Manager) [phone_agent/hdc/device.py]()

**Sources:** [phone_agent/hdc/]()

### iOS (WebDriverAgent)

```mermaid
graph LR
    subgraph "XCTest Module (phone_agent/xctest/)"
        CONN["connection.py<br/>XCTestConnection"]
        SS["screenshot.py<br/>GET /screenshot"]
        INPUT["input.py<br/>POST /keys"]
        DEV["device.py<br/>WebDriver protocol"]
    end
    
    subgraph "WDA API Endpoints"
        STATUS["/status"]
        SCREENSHOT["/screenshot"]
        TAP["/wda/tap"]
        KEYS["/wda/keys"]
        LAUNCH["/wda/apps/launch"]
    end
    
    CONN --> STATUS
    SS --> SCREENSHOT
    INPUT --> KEYS
    DEV --> TAP
    DEV --> LAUNCH
```

**Key characteristics:**
- Uses WebDriverAgent HTTP API (WebDriver protocol) [phone_agent/xctest/connection.py]()
- No external keyboard app needed (native iOS input) [phone_agent/xctest/input.py]()
- Screenshot via HTTP GET endpoint [phone_agent/xctest/screenshot.py]()
- Requires WebDriverAgent running on device [docs/ios_setup/]()

**Sources:** [phone_agent/xctest/](), [docs/ios_setup/ios_setup.md]()

## Action Handling Pipeline

The `ActionHandler` validates and executes actions through a multi-stage pipeline:

```mermaid
graph TB
    INPUT["Action JSON<br/>from Model"]
    
    PARSE["Parse JSON<br/>(actions/handler.py)"]
    VALIDATE["Validate Action Type<br/>Check required fields"]
    
    CLASSIFY{"Action Type?"}
    
    LAUNCH["Launch Action<br/>- Get package ID<br/>- Call launch_app()"]
    TAP["Tap Action<br/>- Transform coordinates<br/>- Call tap()"]
    TYPE["Type Action<br/>- Switch to input method<br/>- Call type_text()"]
    SWIPE["Swipe Action<br/>- Transform coordinates<br/>- Call swipe()"]
    NAV["Navigation Action<br/>- Back/Home<br/>- Call press_*()"]
    TAKEOVER["Take_over Action<br/>- Invoke callback<br/>- Wait for user"]
    
    COORD_TRANS["Coordinate Transformation<br/>(actions/handler.py)<br/>Scale to screen dimensions"]
    
    CONFIRM{"Sensitive<br/>Action?"}
    CALLBACK["confirmation_callback()<br/>Request user approval"]
    
    EXECUTE["Execute on Device<br/>(device_factory.py)"]
    
    INPUT --> PARSE
    PARSE --> VALIDATE
    VALIDATE --> CLASSIFY
    
    CLASSIFY -->|"Launch"| LAUNCH
    CLASSIFY -->|"Tap"| TAP
    CLASSIFY -->|"Type"| TYPE
    CLASSIFY -->|"Swipe"| SWIPE
    CLASSIFY -->|"Back/Home"| NAV
    CLASSIFY -->|"Take_over"| TAKEOVER
    
    LAUNCH --> CONFIRM
    TAP --> COORD_TRANS
    TYPE --> EXECUTE
    SWIPE --> COORD_TRANS
    NAV --> EXECUTE
    
    COORD_TRANS --> CONFIRM
    CONFIRM -->|"Yes"| CALLBACK
    CONFIRM -->|"No"| EXECUTE
    CALLBACK -->|"Approved"| EXECUTE
    CALLBACK -->|"Denied"| INPUT
    
    TAKEOVER --> CALLBACK
```

**Sources:** [phone_agent/actions/handler.py]()

### Coordinate Transformation

The model outputs coordinates in normalized space, which `ActionHandler` transforms to device-specific pixel coordinates:

```python
# Normalized coordinates (0-1000 range) from model
model_x, model_y = action["element"]

# Transform to actual screen pixels
screen_width, screen_height = get_screen_size()
actual_x = int((model_x / 1000.0) * screen_width)
actual_y = int((model_y / 1000.0) * screen_height)
```

**Sources:** [phone_agent/actions/handler.py]()

## Application Package Resolution

The system maintains platform-specific application mappings:

```mermaid
graph TB
    subgraph "App Name Resolution"
        INPUT["App Name<br/>(from model/user)"]
        DETECT["Detect Platform<br/>(device_factory.py)"]
        
        ANDROID["APP_PACKAGES<br/>(config/apps.py)<br/>130+ Android apps"]
        HARMONY["APP_PACKAGES_HARMONYOS<br/>(config/apps_harmonyos.py)<br/>60+ HarmonyOS apps"]
        IOS["APP_PACKAGES_IOS<br/>(config/apps_ios.py)<br/>50+ iOS apps"]
        
        RESOLVE["Resolve to Package ID<br/>actions/handler.py"]
        LAUNCH["Launch Application<br/>device_factory.py"]
    end
    
    INPUT --> DETECT
    DETECT -->|"ADB"| ANDROID
    DETECT -->|"HDC"| HARMONY
    DETECT -->|"IOS"| IOS
    
    ANDROID --> RESOLVE
    HARMONY --> RESOLVE
    IOS --> RESOLVE
    
    RESOLVE --> LAUNCH
```

**Example mappings:**

| App Name | Android Package | HarmonyOS Bundle | iOS Bundle ID |
|----------|----------------|------------------|---------------|
| 微信 (WeChat) | `com.tencent.mm` | `com.tencent.wechat` | `com.tencent.xin` |
| 淘宝 (Taobao) | `com.taobao.taobao` | `com.taobao.taobao` | `com.taobao.taobao4iphone` |
| 抖音 (Douyin) | `com.ss.android.ugc.aweme` | `com.ss.android.ugc.aweme` | `com.ss.iphone.ugc.Aweme` |

**Sources:** [phone_agent/config/apps.py](), [phone_agent/config/apps_harmonyos.py](), [phone_agent/config/apps_ios.py](), [phone_agent/actions/handler.py]()

## System Prompt Architecture

System prompts guide the model's behavior and are language-specific:

```mermaid
graph LR
    subgraph "Prompt Selection"
        LANG["Language Parameter<br/>(--lang cn/en)"]
        
        CN["prompts_zh.py<br/>Chinese prompts<br/>- SYSTEM_PROMPT_ZH<br/>- APP_GUIDELINES_ZH"]
        EN["prompts_en.py<br/>English prompts<br/>- SYSTEM_PROMPT_EN<br/>- APP_GUIDELINES_EN"]
    end
    
    subgraph "Prompt Components"
        SYS["System Instruction<br/>Role, capabilities, output format"]
        APP["App-Specific Guidelines<br/>Known app behaviors"]
        CONST["Constraints<br/>Safety, sensitive actions"]
    end
    
    subgraph "Message Construction"
        MSGS["Messages List<br/>(agent.py)"]
        FIRST["First Message:<br/>System Prompt"]
        CONTEXT["Subsequent Messages:<br/>Screenshot + Context"]
    end
    
    LANG -->|"cn"| CN
    LANG -->|"en"| EN
    
    CN --> SYS
    EN --> SYS
    SYS --> APP
    APP --> CONST
    
    CONST --> FIRST
    FIRST --> MSGS
    MSGS --> CONTEXT
```

**Sources:** [phone_agent/config/prompts_zh.py](), [phone_agent/config/prompts_en.py](), [phone_agent/agent.py]()

## Model Integration Architecture

Open-AutoGLM uses OpenAI-compatible APIs for model interaction:

```mermaid
graph TB
    subgraph "Model Configuration"
        MC["ModelConfig<br/>- base_url<br/>- model_name<br/>- api_key<br/>- max_tokens<br/>- temperature"]
    end
    
    subgraph "Client Implementation"
        MCL["ModelClient<br/>(model/client.py)"]
        OPENAI["OpenAI SDK<br/>openai.OpenAI"]
    end
    
    subgraph "Deployment Options"
        CLOUD["Third-Party APIs<br/>- BigModel<br/>- ModelScope"]
        SELFHOST["Self-Hosted<br/>- vLLM server<br/>- SGLang server"]
    end
    
    subgraph "Request Processing"
        PREP["_prepare_request()<br/>Format messages<br/>Handle images"]
        SEND["chat.completions.create()<br/>POST /v1/chat/completions"]
        PARSE["_parse_response()<br/>Extract thinking + action"]
    end
    
    MC --> MCL
    MCL --> OPENAI
    
    OPENAI --> CLOUD
    OPENAI --> SELFHOST
    
    MCL --> PREP
    PREP --> SEND
    SEND --> PARSE
```

**API Request Format:**
```json
{
  "model": "autoglm-phone-9b",
  "messages": [
    {"role": "system", "content": "..."},
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "Current app: com.example"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
      ]
    }
  ],
  "max_tokens": 3000,
  "temperature": 0.1
}
```

**Sources:** [phone_agent/model/client.py](), [main.py:272-352]()

## Error Handling and Callbacks

The agent provides extension points for custom behavior:

| Callback | Signature | Purpose | Invoked By |
|----------|-----------|---------|------------|
| `confirmation_callback` | `(message: str) -> bool` | User approval for sensitive actions | `ActionHandler` |
| `takeover_callback` | `(message: str) -> None` | Manual intervention request | `ActionHandler` |

**Default Implementations:**
- `confirmation_callback`: CLI prompt with "yes/no" input [phone_agent/agent.py]()
- `takeover_callback`: CLI prompt to wait for user completion [phone_agent/agent.py]()

**Custom Implementation Example:**
```python
def custom_confirm(message: str) -> bool:
    # Custom logic (e.g., GUI dialog, logging)
    return user_approval

agent = PhoneAgent(
    confirmation_callback=custom_confirm,
    takeover_callback=custom_takeover
)
```

**Sources:** [phone_agent/agent.py](), [phone_agent/actions/handler.py](), [examples/basic_usage.py]()

## Threading and Concurrency

Open-AutoGLM follows a synchronous, single-threaded execution model:

- **No Concurrent Operations**: Each task executes sequentially in the main thread
- **Blocking API Calls**: Model requests block until response received
- **Sequential Device Commands**: Device operations execute one at a time
- **Stateful Message History**: Maintains conversation context across steps

This design prioritizes simplicity and predictability over throughput, suitable for interactive automation scenarios.

**Sources:** [phone_agent/agent.py](), [phone_agent/model/client.py]()

---

