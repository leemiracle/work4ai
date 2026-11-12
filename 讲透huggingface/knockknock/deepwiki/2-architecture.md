<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/knockknock · page 2 Architecture · fetched 2026-10-26 -->

# Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [knockknock/__init__.py](knockknock/__init__.py)
- [knockknock/__main__.py](knockknock/__main__.py)

</details>



This document provides a technical overview of the design and architecture of the knockknock library. It explains the core components, their relationships, and the underlying patterns that enable the notification functionality. For information about installation and usage, see [Overview](#1) and [Quick Start](#1.2).

## Overview

KnockKnock is a Python library that provides notification capabilities for long-running processes, particularly machine learning training jobs. The library implements a decorator-based approach that allows users to receive notifications when their processes start, complete successfully, or crash.

The architecture follows a simple yet effective design centered around the decorator pattern. This enables users to add notification capabilities to their existing code with minimal modifications.

### High-Level Architecture

```mermaid
graph TD
    A["User Code"] --> B["KnockKnock Decorators"]
    B --> C["Notification Channels"]
    
    C --> D["Email Sender"]
    C --> E["Slack Sender"]
    C --> F["Discord Sender"]
    C --> G["Telegram Sender"]
    C --> H["Desktop Sender"]
    C --> I["SMS/Twilio Sender"]
    C --> J["Teams Sender"]
    C --> K["Matrix Sender"]
    C --> L["Chime Sender"]
    C --> M["DingTalk Sender"]
    C --> N["RocketChat Sender"]
    C --> O["WeChat Sender"]
    
    P["CLI Interface"] --> B
    Q["Distributed Training Support"] --> B
```

Sources: [README.md:1-406](), [knockknock/__init__.py:1-13](), [knockknock/__main__.py:1-212]()

## Core Components

KnockKnock consists of several key components that work together to provide the notification functionality:

1. **Decorators**: Python function decorators that wrap user-defined functions to add notification capabilities.
2. **Notification Senders**: Specialized modules that handle sending notifications to different platforms.
3. **CLI Interface**: Command-line interface for using KnockKnock without modifying code.
4. **Distributed Training Support**: Logic to handle notifications in distributed environments.

### Component Relationships

```mermaid
classDiagram
    class SenderDecorator {
        <<conceptual>>
        +send_start_notification()
        +send_end_notification()
        +send_error_notification()
        +__call__(func)
    }
    
    class NotificationChannel {
        <<conceptual>>
        +send_message()
        +format_notification()
    }
    
    class CLIInterface {
        +parse_arguments()
        +execute_command()
    }
    
    class DistributedTrainingHandler {
        +is_master_process()
        +should_send_notification()
    }
    
    SenderDecorator --> NotificationChannel : uses
    SenderDecorator --> DistributedTrainingHandler : uses
    CLIInterface --> SenderDecorator : creates and uses
```

Sources: [README.md:19-69](), [knockknock/__main__.py:17-207]()

## Decorator Pattern Implementation

The decorator pattern is central to KnockKnock's design. It allows the library to intercept function calls, send notifications at appropriate times, and handle errors, all while being transparent to the wrapped function.

### Execution Flow

```mermaid
sequenceDiagram
    participant User as "User Code"
    participant Decorator as "KnockKnock Decorator"
    participant Function as "User Function"
    participant Platform as "Notification Platform"
    
    User->>Decorator: Apply decorator
    User->>Function: Call function
    Decorator->>Decorator: Check if should send notification
    Decorator->>Platform: Send "Started" notification
    Decorator->>Function: Execute original function
    
    alt Function succeeds
        Function-->>Decorator: Return result
        Decorator->>Platform: Send "Completed" notification
        Decorator-->>User: Return original result
    else Function fails
        Function-->>Decorator: Raise exception
        Decorator->>Platform: Send "Crashed" notification with traceback
        Decorator-->>User: Re-raise exception
    end
```

Sources: [README.md:46-55](), [README.md:77-86](), [README.md:112-119]()

## Notification Channels

KnockKnock supports multiple notification channels, each implemented as a separate module. Despite their different implementations, all channels follow a common pattern.

### Channel Structure

```mermaid
classDiagram
    class BaseSender {
        <<conceptual>>
        +send_start_notification()
        +send_success_notification()
        +send_failure_notification()
        +handle_distributed_training()
    }
    
    class email_sender {
        +configure_email_settings()
        +send_via_yagmail()
    }
    
    class slack_sender {
        +configure_webhook()
        +send_via_webhook()
    }
    
    class discord_sender {
        +configure_webhook()
        +send_via_webhook()
    }
    
    class telegram_sender {
        +configure_bot()
        +send_via_bot_api()
    }
    
    class teams_sender {
        +configure_webhook()
        +send_via_webhook()
    }
    
    class sms_sender {
        +configure_twilio()
        +send_via_twilio()
    }
    
    class desktop_sender {
        +detect_platform()
        +send_os_notification()
    }
    
    class matrix_sender {
        +configure_client()
        +send_via_matrix_api()
    }
    
    class chime_sender {
        +configure_webhook()
        +send_via_webhook()
    }
    
    class dingtalk_sender {
        +configure_webhook()
        +send_via_webhook()
    }
    
    class rocketchat_sender {
        +configure_client()
        +send_via_api()
    }
    
    class wechat_sender {
        +configure_webhook()
        +send_via_webhook()
    }
    
    BaseSender <|-- email_sender
    BaseSender <|-- slack_sender
    BaseSender <|-- discord_sender
    BaseSender <|-- telegram_sender
    BaseSender <|-- teams_sender
    BaseSender <|-- sms_sender
    BaseSender <|-- desktop_sender
    BaseSender <|-- matrix_sender
    BaseSender <|-- chime_sender
    BaseSender <|-- dingtalk_sender
    BaseSender <|-- rocketchat_sender
    BaseSender <|-- wechat_sender
```

Sources: [knockknock/__init__.py:1-13](), [README.md:41-399]()

## Command-Line Interface

KnockKnock provides a command-line interface that allows users to utilize its notification capabilities without modifying their code. The CLI is implemented in [knockknock/__main__.py]() and supports all the notification channels available in the library.

### CLI Flow

```mermaid
flowchart TD
    A["User invokes knockknock CLI"] --> B["Parse command-line arguments"]
    B --> C["Select notification channel"]
    C --> D["Configure sender with arguments"]
    D --> E["Execute target command"]
    E --> F1["Send start notification"]
    F1 --> G["Wait for command completion"]
    
    G --> H{Command succeeds?}
    H -->|Yes| I["Send success notification"]
    H -->|No| J["Send error notification"]
```

Sources: [knockknock/__main__.py:17-207]()

### CLI Structure

The CLI implementation defines a separate subparser for each notification channel, with specific arguments required for that channel.

```mermaid
graph TD
    A["ArgumentParser"] --> B["Subparsers"]
    
    B --> C["email"]
    B --> D["slack"]
    B --> E["discord"]
    B --> F["telegram"]
    B --> G["desktop"]
    B --> H["sms"]
    B --> I["teams"]
    B --> J["matrix"]
    B --> K["chime"]
    B --> L["dingtalk"]
    B --> M["rocketchat"]
    B --> N["wechat"]
    
    C --> O["sender_func=email_sender"]
    D --> P["sender_func=slack_sender"]
    E --> Q["sender_func=discord_sender"]
    F --> R["sender_func=telegram_sender"]
    G --> S["sender_func=desktop_sender"]
    H --> T["sender_func=sms_sender"]
    I --> U["sender_func=teams_sender"]
    J --> V["sender_func=matrix_sender"]
    K --> W["sender_func=chime_sender"]
    L --> X["sender_func=dingtalk_sender"]
    M --> Y["sender_func=rocketchat_sender"]
    N --> Z["sender_func=wechat_sender"]
```

Sources: [knockknock/__main__.py:17-192]()

## Distributed Training Support

KnockKnock includes support for distributed training environments, particularly for PyTorch distributed training. This prevents multiple notification messages from being sent when using multiple processes.

### Distributed Training Logic

```mermaid
flowchart TD
    A["Start Notification Process"] --> B{"RANK environment variable exists?"}
    B -->|Yes| C{"RANK == 0?"}
    B -->|No| D["Set as master process"]
    C -->|Yes| D
    C -->|No| E["Set as worker process"]
    
    D --> F{"Is master process?"}
    E --> F
    
    F -->|Yes| G["Send notification"]
    F -->|No| H["Skip notification"]
    
    G --> I["Continue processing"]
    H --> I
    
    J["Error notification?"] -->|Yes| G
    J -->|No| F
```

Sources: [README.md:401-405]()

## Integration Methods

KnockKnock provides two main integration methods: Python decorators and the command-line interface.

### Integration Comparison

| Feature | Python Decorator | CLI |
|---------|------------------|-----|
| Code Modification | Requires adding decorators to functions | No code changes required |
| Configuration | Done in code | Done via command-line arguments |
| Flexibility | Can wrap any Python function | Wraps command-line commands |
| Function Return Value | Preserved and included in notification | Command exit code only |
| Integration Ease | Simple for Python code | Works with any executable |

Sources: [README.md:19-399]()

## Extensibility

KnockKnock's architecture is designed to be extensible, making it easy to add support for new notification channels. Each notification channel is implemented as a separate module with a similar interface.

### Adding a New Channel

To add a new notification channel, one would need to:

1. Create a new module in the knockknock package
2. Implement a decorator function that configures the notification channel
3. Add the notification sending logic
4. Update `__init__.py` to expose the new sender
5. Add CLI support in `__main__.py`

```mermaid
flowchart TD
    A["Create new_channel_sender.py"] --> B["Implement decorator function"]
    B --> C["Add notification sending logic"]
    C --> D["Update __init__.py"]
    D --> E["Add CLI support in __main__.py"]
```

Sources: [knockknock/__init__.py:1-13](), [knockknock/__main__.py:17-192]()

## Summary

KnockKnock employs a simple yet effective architecture centered around the decorator pattern. This allows it to provide notification capabilities with minimal code changes. The library supports multiple notification channels and offers both programmatic and command-line interfaces for integration.

The system's distributed training support ensures that notifications work correctly in multi-process environments, preventing duplicate notifications while ensuring that error notifications are always sent.

Sources: [README.md:1-406](), [knockknock/__init__.py:1-13](), [knockknock/__main__.py:1-212]()

---

