<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/hf-hub · page 6 Advanced Examples · fetched 2026-10-26 -->

# Advanced Examples

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [examples/iced/src/main.rs](examples/iced/src/main.rs)
- [examples/socks/src/main.rs](examples/socks/src/main.rs)

</details>



This page demonstrates complex usage patterns and integration examples that go beyond basic file downloading. It covers custom progress implementations, proxy configuration, stream-based downloads, error handling, and GUI integration patterns.

For basic usage patterns and simple download examples, see [Getting Started](#2). For detailed API reference including progress traits and download methods, see [API Reference](#4).

## Overview of Advanced Patterns

The hf-hub crate supports several advanced integration patterns that extend beyond simple file downloads:

```mermaid
graph TB
    BasicDownload["Basic Download<br/>api.get(filename)"]
    
    subgraph "Advanced Patterns"
        ProxyConfig["Proxy Configuration<br/>HTTPS_PROXY + reqwest"]
        CustomProgress["Custom Progress<br/>Progress trait impl"]
        StreamDownload["Stream-based Downloads<br/>iced::stream::try_channel"]
        ErrorHandling["Error Recovery<br/>ApiError handling"]
        ConcurrentDownloads["Concurrent Downloads<br/>Multiple tokio tasks"]
    end
    
    subgraph "Integration Examples"
        SocksExample["SOCKS Proxy<br/>examples/socks/"]
        IcedGUI["GUI Integration<br/>examples/iced/"]
    end
    
    BasicDownload --> ProxyConfig
    BasicDownload --> CustomProgress
    BasicDownload --> StreamDownload
    
    ProxyConfig --> SocksExample
    CustomProgress --> IcedGUI
    StreamDownload --> IcedGUI
    ErrorHandling --> IcedGUI
    ConcurrentDownloads --> IcedGUI
```

Sources: [examples/socks/src/main.rs:1-16](), [examples/iced/src/main.rs:1-245]()

## SOCKS Proxy Configuration

The crate supports proxy configuration through environment variables when using the reqwest backend with tokio. The HTTPS_PROXY environment variable is automatically recognized by the underlying HTTP client.

```mermaid
graph LR
    EnvVar["HTTPS_PROXY<br/>environment variable"]
    ApiBuilder["ApiBuilder::new()<br/>with_progress(true)"]
    ReqwestClient["reqwest HTTP client<br/>proxy auto-detection"]
    HFHub["Hugging Face Hub<br/>via proxy"]
    
    EnvVar --> ApiBuilder
    ApiBuilder --> ReqwestClient
    ReqwestClient --> HFHub
```

The SOCKS example demonstrates this pattern by expecting the `HTTPS_PROXY` environment variable to be set and using the tokio API with progress tracking enabled. The `ApiBuilder` automatically configures the underlying reqwest client to use the specified proxy.

Sources: [examples/socks/src/main.rs:3-8]()

## Custom Progress Implementation

Advanced applications often require custom progress tracking that integrates with their UI framework or logging system. The `Progress` trait provides hooks for initialization, updates, and completion.

```mermaid
graph TB
    ProgressTrait["hf_hub::api::tokio::Progress"]
    
    subgraph "Required Methods"
        InitMethod["async fn init(size, filename)"]
        UpdateMethod["async fn update(current_size)"]
        FinishMethod["async fn finish()"]
    end
    
    subgraph "Custom Implementation"
        IcedProg["Prog struct<br/>with mpsc::Sender"]
        ChannelSend["Send to GUI thread<br/>via futures channel"]
        UIUpdate["Update progress bar<br/>in GUI framework"]
    end
    
    ProgressTrait --> InitMethod
    ProgressTrait --> UpdateMethod
    ProgressTrait --> FinishMethod
    
    InitMethod --> IcedProg
    UpdateMethod --> IcedProg
    FinishMethod --> IcedProg
    
    IcedProg --> ChannelSend
    ChannelSend --> UIUpdate
```

The Iced example implements a custom `Prog` struct that sends progress updates through an mpsc channel to the GUI thread. This pattern allows progress tracking to work across thread boundaries in async applications.

Sources: [examples/iced/src/main.rs:36-67]()

## Stream-based Downloads

For GUI applications and reactive systems, downloads can be exposed as streams that emit progress events. This pattern integrates well with frameworks like Iced that expect stream-based data flows.

The `try_channel` function creates a stream that emits `Progress` events throughout the download lifecycle:

```mermaid
sequenceDiagram
    participant GUI as "GUI Thread"
    participant Stream as "try_channel Stream"
    participant API as "hf_hub::api::tokio::Api"
    participant Progress as "Custom Progress"
    participant Hub as "Hugging Face Hub"
    
    GUI->>Stream: initiate download stream
    Stream->>API: download_with_progress()
    API->>Progress: init(size, filename)
    Progress->>Stream: Progress::Downloading{0, total}
    Stream->>GUI: emit progress event
    
    loop Download chunks
        Hub->>API: file data
        API->>Progress: update(current_size)
        Progress->>Stream: Progress::Downloading{current, total}
        Stream->>GUI: emit progress event
    end
    
    API->>Progress: finish()
    Progress->>Stream: Progress::Finished
    Stream->>GUI: emit completion event
```

This pattern enables clean separation between download logic and UI updates, making it easier to handle errors and provide responsive user interfaces.

Sources: [examples/iced/src/main.rs:69-81]()

## Error Handling and Recovery

Advanced applications need robust error handling that can recover from network failures, provide user feedback, and retry failed downloads. The crate's error types integrate with application-specific error handling patterns.

```mermaid
graph TB
    ApiError["hf_hub::api::tokio::ApiError"]
    
    subgraph "Error Conversion"
        CustomError["Application Error<br/>enum Error"]
        ErrorImpl["From<ApiError> impl<br/>for Error"]
    end
    
    subgraph "Recovery Strategies"
        RetryLogic["Retry download<br/>on failure"]
        UserFeedback["Display error<br/>to user"]
        StateReset["Reset download<br/>state machine"]
    end
    
    subgraph "Download States"
        IdleState["State::Idle"]
        DownloadingState["State::Downloading"]
        ErroredState["State::Errored"]
        FinishedState["State::Finished"]
    end
    
    ApiError --> ErrorImpl
    ErrorImpl --> CustomError
    CustomError --> RetryLogic
    CustomError --> UserFeedback
    
    RetryLogic --> IdleState
    UserFeedback --> ErroredState
    IdleState --> DownloadingState
    DownloadingState --> FinishedState
    ErroredState --> IdleState
```

The Iced example demonstrates a state machine approach where downloads can transition between idle, downloading, finished, and errored states, with retry capability from any terminal state.

Sources: [examples/iced/src/main.rs:15-24](), [examples/iced/src/main.rs:154-159]()

## Concurrent Download Management

For applications managing multiple simultaneous downloads, the crate supports concurrent operations with individual progress tracking and task management.

Each download operation can be managed as a separate task with abort capabilities:

```mermaid
graph TB
    MultiDownload["Multiple Downloads<br/>Vec<Download>"]
    
    subgraph "Task Management"
        TaskHandle["task::Handle<br/>abort_on_drop()"]
        AbortableTask["Task::stream().abortable()"]
        TaskNone["Task::none()<br/>for idle states"]
    end
    
    subgraph "State Management"
        DownloadId["unique download ID"]
        DownloadState["per-download State"]
        ProgressTracker["individual progress<br/>tracking"]
    end
    
    subgraph "Message Handling"
        AddMessage["Message::Add<br/>new download"]
        DownloadMessage["Message::Download(id)<br/>start download"]
        ProgressMessage["Message::DownloadProgressed<br/>(id, progress)"]
    end
    
    MultiDownload --> DownloadId
    MultiDownload --> DownloadState
    DownloadState --> TaskHandle
    TaskHandle --> AbortableTask
    
    AddMessage --> MultiDownload
    DownloadMessage --> AbortableTask
    ProgressMessage --> ProgressTracker
```

This pattern allows applications to manage multiple downloads with individual progress tracking, error handling, and the ability to cancel operations cleanly.

Sources: [examples/iced/src/main.rs:147-186](), [examples/iced/src/main.rs:98-125]()

## GUI Integration

For complete GUI integration examples including progress bars, user interaction, and visual feedback, see [GUI Integration with Iced](#6.1). The Iced example demonstrates how to combine all the advanced patterns above into a cohesive desktop application.

Sources: [examples/iced/src/main.rs:1-245]()

---

