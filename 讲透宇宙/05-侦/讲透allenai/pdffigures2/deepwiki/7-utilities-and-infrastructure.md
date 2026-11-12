<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/pdffigures2 · page 7 Utilities and Infrastructure · fetched 2026-10-26 -->

# Utilities and Infrastructure

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [src/main/java/org/allenai/pdffigures2/RegexWithTimeout.java](src/main/java/org/allenai/pdffigures2/RegexWithTimeout.java)
- [src/main/scala/org/allenai/pdffigures2/Logging.scala](src/main/scala/org/allenai/pdffigures2/Logging.scala)

</details>



This page covers the supporting utilities and infrastructure components that provide essential services across the pdffigures2 system. These include logging facilities, regex processing with timeout protection, and other cross-cutting infrastructure concerns that support the main extraction pipeline.

For information about the core extraction pipeline components, see [Core Processing Pipeline](#3). For build system configuration, see [Build System and Configuration](#6).

## Logging Infrastructure

The pdffigures2 system uses a comprehensive logging framework built around SLF4J and Logback, implemented through the `Logging` trait. This infrastructure provides structured logging capabilities with lazy evaluation for performance optimization.

### Logging Trait Architecture

```mermaid
graph TB
    subgraph "Logging Trait Implementation"
        LoggingTrait["Logging trait"]
        InternalLogger["internalLogger: org.slf4j.Logger"]
        LoggerObject["logger object"]
    end
    
    subgraph "Log Level Methods"
        TraceMethod["trace(message: => String)"]
        DebugMethod["debug(message: => String)"]
        InfoMethod["info(message: => String)"]
        WarnMethod["warn(message: => String)"]
        ErrorMethod["error(message: => String)"]
    end
    
    subgraph "Configuration Utilities"
        LoggerConfig["loggerConfig object"]
        LoggerCase["Logger case class"]
        PatternEncoder["newPatternLayoutEncoder"]
        HtmlEncoder["newHtmlLayoutEncoder"]
        ConsoleAppender["newConsoleAppender"]
        FileAppender["newFileAppender"]
    end
    
    subgraph "External Dependencies"
        SLF4J["SLF4J LoggerFactory"]
        Logback["Logback Classic"]
    end
    
    LoggingTrait --> InternalLogger
    LoggingTrait --> LoggerObject
    LoggingTrait --> LoggerConfig
    
    LoggerObject --> TraceMethod
    LoggerObject --> DebugMethod
    LoggerObject --> InfoMethod
    LoggerObject --> WarnMethod
    LoggerObject --> ErrorMethod
    
    LoggerConfig --> LoggerCase
    LoggerConfig --> PatternEncoder
    LoggerConfig --> HtmlEncoder
    LoggerConfig --> ConsoleAppender
    LoggerConfig --> FileAppender
    
    InternalLogger --> SLF4J
    LoggerCase --> Logback
    
    style LoggingTrait fill:#e1f5fe
    style LoggerObject fill:#f3e5f5
    style LoggerConfig fill:#e8f5e8
```

**Sources:** [src/main/scala/org/allenai/pdffigures2/Logging.scala:1-161]()

### Lazy Message Evaluation

The logging system implements lazy evaluation for log messages using Scala's call-by-name parameters (`message: => String`). This optimization ensures that expensive string construction operations are only performed when the corresponding log level is actually enabled.

| Log Level | Method | Level Check | Exception Support |
|-----------|--------|-------------|-------------------|
| TRACE | `logger.trace()` | `isTraceEnabled` | No |
| DEBUG | `logger.debug()` | `isDebugEnabled` | No |
| INFO | `logger.info()` | `isInfoEnabled` | No |
| WARN | `logger.warn()` | `isWarnEnabled` | Yes |
| ERROR | `logger.error()` | `isErrorEnabled` | Yes |

**Sources:** [src/main/scala/org/allenai/pdffigures2/Logging.scala:24-57]()

### Logback Configuration API

The `loggerConfig` object provides a programmatic configuration API for Logback, allowing runtime configuration of loggers, appenders, and encoders:

```mermaid
graph TD
    subgraph "Logger Configuration Flow"
        LoggerCase["Logger case class"]
        SetLevel["setLevel(Level)"]
        AddAppender["addAppender(encoder, appender)"]
        Reset["reset()"]
    end
    
    subgraph "Encoder Creation"
        PatternCreate["newPatternLayoutEncoder(pattern)"]
        HtmlCreate["newHtmlLayoutEncoder(pattern)"]
    end
    
    subgraph "Appender Creation"
        ConsoleCreate["newConsoleAppender()"]
        FileCreate["newFileAppender(fileName)"]
    end
    
    subgraph "Output Configuration"
        PatternLayoutEncoder["PatternLayoutEncoder"]
        HTMLLayout["HTMLLayout"]
        ConsoleAppender["ConsoleAppender"]
        FileAppender["FileAppender"]
    end
    
    LoggerCase --> SetLevel
    LoggerCase --> AddAppender
    LoggerCase --> Reset
    
    PatternCreate --> PatternLayoutEncoder
    HtmlCreate --> HTMLLayout
    ConsoleCreate --> ConsoleAppender
    FileCreate --> FileAppender
    
    AddAppender --> PatternLayoutEncoder
    AddAppender --> HTMLLayout
    AddAppender --> ConsoleAppender
    AddAppender --> FileAppender
    
    style LoggerCase fill:#e1f5fe
    style PatternLayoutEncoder fill:#f3e5f5
    style ConsoleAppender fill:#e8f5e8
```

**Sources:** [src/main/scala/org/allenai/pdffigures2/Logging.scala:75-160]()

## Regex Timeout Protection

The system includes specialized regex processing utilities that prevent infinite or long-running regular expression operations from blocking the extraction pipeline. This is implemented through the `RegexWithTimeout` Java class.

### Timeout Mechanism Architecture

```mermaid
graph TB
    subgraph "RegexWithTimeout Implementation"
        RegexClass["RegexWithTimeout class"]
        MatcherMethod["matcher(Pattern, CharSequence)"]
        TimeoutException["RegexTimeout exception"]
    end
    
    subgraph "TimeoutCharSequence Wrapper"
        TimeoutWrapper["TimeoutCharSequence"]
        InnerSequence["inner: CharSequence"]
        AbortTime["abortTime: long"]
        CharAtMethod["charAt(index)"]
        LengthMethod["length()"]
        SubSequenceMethod["subSequence(start, end)"]
    end
    
    subgraph "Timeout Logic"
        TimeCheck["System.currentTimeMillis() >= abortTime"]
        ThrowTimeout["throw RegexTimeout()"]
        DelegateCall["inner.charAt(index)"]
    end
    
    RegexClass --> MatcherMethod
    RegexClass --> TimeoutException
    MatcherMethod --> TimeoutWrapper
    
    TimeoutWrapper --> InnerSequence
    TimeoutWrapper --> AbortTime
    TimeoutWrapper --> CharAtMethod
    TimeoutWrapper --> LengthMethod
    TimeoutWrapper --> SubSequenceMethod
    
    CharAtMethod --> TimeCheck
    TimeCheck --> ThrowTimeout
    TimeCheck --> DelegateCall
    
    style RegexClass fill:#e1f5fe
    style TimeoutWrapper fill:#f3e5f5
    style TimeCheck fill:#fff3e0
```

**Sources:** [src/main/java/org/allenai/pdffigures2/RegexWithTimeout.java:1-45]()

### Timeout Implementation Details

The `RegexWithTimeout` class implements timeout protection by wrapping the input `CharSequence` with a proxy that checks the system time on each character access. Key implementation details:

| Component | Value | Purpose |
|-----------|-------|---------|
| Default Timeout | 1500ms | Prevents regex operations from hanging indefinitely |
| Time Check Location | `charAt()` method | Intercepts every character access during regex processing |
| Exception Type | `RegexTimeout` | Custom runtime exception for timeout conditions |
| Abort Time Calculation | `currentTimeMillis() + timeout` | Pre-computed absolute timeout timestamp |

The `TimeoutCharSequence` inner class wraps the original character sequence and delegates all operations while performing time checks:

- `charAt(index)`: Checks timeout before delegating to inner sequence
- `length()`: Direct delegation without timeout check
- `subSequence(start, end)`: Returns new `TimeoutCharSequence` with same abort time
- `toString()`: Direct delegation without timeout check

**Sources:** [src/main/java/org/allenai/pdffigures2/RegexWithTimeout.java:10-44]()

## Integration with Core System

The utilities and infrastructure components integrate with the core pdffigures2 system through trait mixins and direct usage patterns:

```mermaid
graph TB
    subgraph "Core System Components"
        FigureExtractor["FigureExtractor"]
        CaptionDetector["CaptionDetector"] 
        GraphicsExtractor["GraphicsExtractor"]
        FigureDetector["FigureDetector"]
        VisualLogger["VisualLogger"]
    end
    
    subgraph "Infrastructure Utilities"
        LoggingTrait["Logging trait"]
        RegexTimeout["RegexWithTimeout"]
    end
    
    subgraph "Mixed-in Capabilities"
        LoggerMethods["logger.info/debug/warn/error"]
        TimeoutRegex["Pattern matching with timeout"]
    end
    
    FigureExtractor -.-> LoggingTrait
    CaptionDetector -.-> LoggingTrait
    GraphicsExtractor -.-> LoggingTrait
    FigureDetector -.-> LoggingTrait
    VisualLogger -.-> LoggingTrait
    
    CaptionDetector --> RegexTimeout
    FigureDetector --> RegexTimeout
    
    LoggingTrait --> LoggerMethods
    RegexTimeout --> TimeoutRegex
    
    FigureExtractor --> LoggerMethods
    CaptionDetector --> LoggerMethods
    CaptionDetector --> TimeoutRegex
    
    style LoggingTrait fill:#e1f5fe
    style RegexTimeout fill:#f3e5f5
    style LoggerMethods fill:#e8f5e8
```

### Usage Patterns

The infrastructure components follow these integration patterns:

1. **Trait Mixing**: Core classes mix in the `Logging` trait to gain access to the `logger` object and its methods
2. **Defensive Programming**: Regex-intensive operations use `RegexWithTimeout.matcher()` instead of direct `Pattern.matcher()` calls
3. **Performance Optimization**: Lazy evaluation in logging prevents expensive string construction when logs are disabled
4. **Configuration Flexibility**: The `loggerConfig` API allows runtime reconfiguration of logging behavior for debugging

**Sources:** [src/main/scala/org/allenai/pdffigures2/Logging.scala:19-20](), [src/main/java/org/allenai/pdffigures2/RegexWithTimeout.java:10-43]()

---

