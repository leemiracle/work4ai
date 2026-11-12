<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/anthropic-sdk-java · page 5 Data Models · fetched 2026-10-26 -->

# Data Models

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.stats.yml](.stats.yml)
- [anthropic-java-core/src/main/kotlin/com/anthropic/core/Utils.kt](anthropic-java-core/src/main/kotlin/com/anthropic/core/Utils.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/core/Values.kt](anthropic-java-core/src/main/kotlin/com/anthropic/core/Values.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/core/http/HttpRequestBodies.kt](anthropic-java-core/src/main/kotlin/com/anthropic/core/http/HttpRequestBodies.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/BetaRawContentBlockDelta.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/BetaRawContentBlockDelta.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/BetaRawContentBlockDeltaEvent.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/BetaRawContentBlockDeltaEvent.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/MessageCountTokensParams.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/MessageCountTokensParams.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/MessageCreateParams.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/MessageCreateParams.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/batches/BatchCreateParams.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/batches/BatchCreateParams.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/completions/CompletionCreateParams.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/completions/CompletionCreateParams.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCountTokensParams.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCountTokensParams.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCreateParams.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCreateParams.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/RawContentBlockDelta.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/RawContentBlockDelta.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/RawContentBlockDeltaEvent.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/RawContentBlockDeltaEvent.kt)
- [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/batches/BatchCreateParams.kt](anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/batches/BatchCreateParams.kt)
- [anthropic-java-core/src/test/kotlin/com/anthropic/core/UtilsTest.kt](anthropic-java-core/src/test/kotlin/com/anthropic/core/UtilsTest.kt)
- [anthropic-java-core/src/test/kotlin/com/anthropic/core/ValuesTest.kt](anthropic-java-core/src/test/kotlin/com/anthropic/core/ValuesTest.kt)
- [anthropic-java-core/src/test/kotlin/com/anthropic/models/beta/messages/BetaRawContentBlockDeltaEventTest.kt](anthropic-java-core/src/test/kotlin/com/anthropic/models/beta/messages/BetaRawContentBlockDeltaEventTest.kt)
- [anthropic-java-core/src/test/kotlin/com/anthropic/models/beta/messages/BetaRawContentBlockDeltaTest.kt](anthropic-java-core/src/test/kotlin/com/anthropic/models/beta/messages/BetaRawContentBlockDeltaTest.kt)
- [anthropic-java-core/src/test/kotlin/com/anthropic/models/beta/messages/BetaRawMessageStreamEventTest.kt](anthropic-java-core/src/test/kotlin/com/anthropic/models/beta/messages/BetaRawMessageStreamEventTest.kt)
- [anthropic-java-core/src/test/kotlin/com/anthropic/models/messages/RawContentBlockDeltaEventTest.kt](anthropic-java-core/src/test/kotlin/com/anthropic/models/messages/RawContentBlockDeltaEventTest.kt)
- [anthropic-java-core/src/test/kotlin/com/anthropic/models/messages/RawContentBlockDeltaTest.kt](anthropic-java-core/src/test/kotlin/com/anthropic/models/messages/RawContentBlockDeltaTest.kt)

</details>



This document provides a comprehensive overview of the data models used in the Anthropic Java SDK. It covers the core JSON field handling system, message parameter models, content blocks, and serialization mechanisms. For information about streaming response handling and message accumulation, see [Streaming Response Handling](#4).

## Core JSON Field Representation

The Anthropic Java SDK uses a sophisticated JSON field representation system designed to handle both strongly-typed data and flexible JSON structures. This approach allows the SDK to work with both known types expected by the API and arbitrary JSON values.

### JsonField and JsonValue Hierarchy

```mermaid
classDiagram
    class JsonField~T~ {
        <<abstract>>
        +isMissing() Boolean
        +isNull() Boolean
        +asKnown() Optional~T~
        +asUnknown() Optional~JsonValue~
        +asBoolean() Optional~Boolean~
        +asNumber() Optional~Number~
        +asString() Optional~String~
        +asArray() Optional~List~
        +asObject() Optional~Map~
        +accept(Visitor) R
    }
    
    class KnownValue~T~ {
        +value T
        +of(value) KnownValue~T~
    }
    
    class JsonValue {
        <<abstract>>
        +from(value) JsonValue
        +fromJsonNode(node) JsonValue
        +convert(type) R
        +accept(Visitor) R
    }
    
    class JsonMissing {
        +of() JsonMissing
    }
    
    class JsonNull {
        +of() JsonNull
    }
    
    class JsonBoolean {
        +value Boolean
        +of(value) JsonBoolean
    }
    
    class JsonNumber {
        +value Number
        +of(value) JsonNumber
    }
    
    class JsonString {
        +value String
        +of(value) JsonString
    }
    
    class JsonArray {
        +values List~JsonValue~
        +of(values) JsonArray
    }
    
    class JsonObject {
        +values Map~String,JsonValue~
        +of(values) JsonObject
    }
    
    JsonField <|-- KnownValue
    JsonField <|-- JsonValue
    JsonValue <|-- JsonMissing
    JsonValue <|-- JsonNull
    JsonValue <|-- JsonBoolean
    JsonValue <|-- JsonNumber
    JsonValue <|-- JsonString
    JsonValue <|-- JsonArray
    JsonValue <|-- JsonObject
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/core/Values.kt:38-262](), [anthropic-java-core/src/main/kotlin/com/anthropic/core/Values.kt:270-394](), [anthropic-java-core/src/main/kotlin/com/anthropic/core/Values.kt:397-424]()

The core structure consists of:

- **JsonField<T>**: An abstract class that represents a field in a JSON structure. It can either be a `KnownValue<T>` (strongly-typed) or a `JsonValue` (flexible).
- **KnownValue<T>**: Contains a value of type `T` that matches what the SDK expects.
- **JsonValue**: Represents arbitrary JSON data that may not match the expected type.
- **Concrete JsonValue classes**: Implementations for different JSON data types (null, boolean, number, string, array, object).

This design allows for both type safety and flexibility when handling JSON data in the SDK.

### Type Handling and Conversion

The `JsonField` class provides methods to safely convert between different representations:

- `asKnown()`: Returns the value as type `T` if it's a `KnownValue<T>`
- `asBoolean()`, `asNumber()`, `asString()`: Type-specific accessors
- `asArray()`, `asObject()`: Methods for accessing complex structures
- `getRequired()`: Used internally to throw appropriate exceptions when required values are missing

```mermaid
flowchart LR
    subgraph "JSON Input"
        JI["API JSON\nData"]
    end
    
    subgraph "JsonField Representation"
        JF["JsonField~T~"]
        KV["KnownValue~T~"]
        JV["JsonValue"]
        JA["JsonArray"]
        JO["JsonObject"]
        JP["JsonPrimitive"]
        
        JF --> KV
        JF --> JV
        JV --> JA
        JV --> JO
        JV --> JP
    end
    
    subgraph "Type Conversion"
        TC["asKnown()\nasString()\nasNumber()\nasBoolean()\nasArray()\nasObject()"]
    end
    
    subgraph "SDK Types"
        ST["String\nNumber\nBoolean\nList\nMap\nCustom Object"]
    end
    
    JI --> JF
    JF --> TC
    TC --> ST
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/core/Values.kt:45-168]()

## Request Parameter Models

The SDK uses a structured approach for building API request parameters with builder patterns. The main parameter classes follow a consistent design:

```mermaid
classDiagram
    class MessageCreateParams {
        -body Body
        +maxTokens() Long
        +messages() List~MessageParam~
        +model() Model
        +metadata() Optional~Metadata~
        +stopSequences() Optional~List~String~~
        +system() Optional~System~
        +temperature() Optional~Double~
        +thinking() Optional~ThinkingConfigParam~
        +toolChoice() Optional~ToolChoice~
        +tools() Optional~List~ToolUnion~~
        +topK() Optional~Long~
        +topP() Optional~Double~
        +builder() Builder
    }
    
    class MessageCreateParams.Builder {
        +body(body) Builder
        +maxTokens(tokens) Builder
        +messages(messages) Builder
        +addMessage(message) Builder
        +addUserMessage(content) Builder
        +addAssistantMessage(content) Builder
        +model(model) Builder
        +system(system) Builder
        +temperature(temp) Builder
        +build() MessageCreateParams
    }
    
    class MessageCountTokensParams {
        -body Body
        +messages() List~MessageParam~
        +model() Model
        +system() Optional~System~
        +thinking() Optional~ThinkingConfigParam~
        +toolChoice() Optional~ToolChoice~
        +tools() Optional~List~MessageCountTokensTool~~
        +builder() Builder
    }
    
    class BatchCreateParams {
        -body Body
        +requests() List~Request~
        +builder() Builder
    }
    
    MessageCreateParams --> MessageCreateParams.Builder
    MessageCreateParams.Builder --> MessageCreateParams : builds
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCreateParams.kt:44-343](), [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCountTokensParams.kt:44-168](), [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/batches/BatchCreateParams.kt:70-104]()

Key features of these parameter models:

1. **Immutable Objects**: All parameter objects are immutable once built
2. **Builder Pattern**: Each parameter class has a builder for constructing instances
3. **Fluent API**: Builders support chaining methods for a clean API
4. **Required vs Optional**: Clear distinction between required and optional parameters
5. **Type Safety**: Strong typing for all parameters

### Parameter Building Process

```mermaid
flowchart TD
    A["Client Code"] -->|"creates"| B["Builder"]
    B -->|"maxTokens(100)"| C["Builder with maxTokens"]
    C -->|"model(Model.CLAUDE_3_HAIKU)"| D["Builder with model"]
    D -->|"addUserMessage(...)"| E["Builder with messages"]
    E -->|"system(...)"| F["Builder with system"]
    F -->|"build()"| G["Immutable MessageCreateParams"]
    G -->|"used by"| H["AnthropicClient"]
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCreateParams.kt:317-443]()

## Message Content Structure

Messages in the Anthropic API can contain various types of content blocks. The SDK provides models to represent these content blocks both for requests and responses:

```mermaid
classDiagram
    class MessageParam {
        +role Role
        +content Content
    }
    
    class Content {
        +ofString(string) Content
        +ofBlockParams(blocks) Content
    }
    
    class ContentBlockParam {
        <<interface>>
    }
    
    class TextBlockParam {
        +text String
        +type "text"
    }
    
    class ImageBlockParam {
        +source ImageSource
        +type "image"
    }
    
    class ToolResultBlockParam {
        +toolUseId String
        +content String
        +type "tool_result"
    }
    
    MessageParam --> Content
    Content --> ContentBlockParam : contains
    ContentBlockParam <|.. TextBlockParam
    ContentBlockParam <|.. ImageBlockParam
    ContentBlockParam <|.. ToolResultBlockParam
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCreateParams.kt:96-141](), [anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/MessageCountTokensParams.kt:97-141]()

### Content Block Deltas (for Streaming)

For streaming responses, the SDK provides models to represent deltas (incremental updates) to content blocks:

```mermaid
classDiagram
    class RawContentBlockDeltaEvent {
        +delta() RawContentBlockDelta
        +index() Long
    }
    
    class RawContentBlockDelta {
        +text() Optional~TextDelta~
        +inputJson() Optional~InputJsonDelta~
        +citations() Optional~CitationsDelta~
        +thinking() Optional~ThinkingDelta~
        +signature() Optional~SignatureDelta~
        +accept(Visitor) R
    }
    
    class TextDelta {
        +text String
    }
    
    class InputJsonDelta {
        +partialJson String
    }
    
    class CitationsDelta {
        +citation Citation
    }
    
    RawContentBlockDeltaEvent --> RawContentBlockDelta
    RawContentBlockDelta --> TextDelta
    RawContentBlockDelta --> InputJsonDelta
    RawContentBlockDelta --> CitationsDelta
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/RawContentBlockDeltaEvent.kt:19-54](), [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/RawContentBlockDelta.kt:23-73]()

## JSON Serialization and Handling

The SDK provides utilities for serializing and deserializing JSON data, including handling multipart form data:

```mermaid
flowchart LR
    subgraph "SDK Objects"
        MCP["MessageCreateParams"]
        MCTP["MessageCountTokensParams"]
        BCP["BatchCreateParams"]
    end
    
    subgraph "Serialization"
        JM["JsonMapper"]
        JF["JsonField Converters"]
        S["Serializers"]
        D["Deserializers"]
    end
    
    subgraph "HTTP Layer"
        RB["Request Bodies"]
        HD["HTTP Clients"]
    end
    
    MCP --> JF
    MCTP --> JF
    BCP --> JF
    
    JF --> S
    JF --> D
    
    S --> JM
    D --> JM
    
    JM --> RB
    RB --> HD
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/core/Values.kt:247-262](), [anthropic-java-core/src/main/kotlin/com/anthropic/core/http/HttpRequestBodies.kt:33-47]()

### MultipartField Handling

For handling file uploads and multipart form data, the SDK provides the `MultipartField` class:

```mermaid
classDiagram
    class MultipartField~T~ {
        -value JsonField~T~
        -contentType String
        -filename String?
        +of(value) MultipartField~T~
        +of(value) MultipartField~T~
        +builder() Builder~T~
    }
    
    class Builder~T~ {
        +value(value) Builder
        +contentType(type) Builder
        +filename(name) Builder
        +build() MultipartField~T~
    }
    
    MultipartField~T~ --> Builder~T~
    Builder~T~ --> MultipartField~T~ : builds
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/core/Values.kt:608-723](), [anthropic-java-core/src/main/kotlin/com/anthropic/core/http/HttpRequestBodies.kt:66-160]()

## Relationship to API Requests

The data models fit into the overall SDK architecture to build and send API requests:

```mermaid
flowchart TD
    A["Client Code"] -->|"creates"| B["MessageCreateParams.Builder"]
    B -->|"build()"| C["MessageCreateParams"]
    
    C -->|"serialized to"| D["JSON Request Body"]
    
    E["AnthropicClient"] -->|"creates"| F["MessageService"]
    F -->|"uses"| G["HttpClient"]
    
    C -->|"passed to"| F
    
    G -->|"sends"| D
    G -->|"receives"| H["JSON Response"]
    
    H -->|"deserialized to"| I["Message or StreamResponse"]
    
    I -->|"returned to"| E
    E -->|"returned to"| A
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCreateParams.kt:44-731]()

## Utility Functions

The SDK provides various utility functions for working with data models:

1. **Field Validation**: Functions to check for required fields and validate data
2. **Type Conversion**: Methods for converting between different representations
3. **Content Handling**: Utilities for working with content hashes and equality
4. **Immutability**: Functions to convert mutable structures to immutable ones

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/core/Utils.kt:10-90]()

## Beta Models

The SDK provides beta versions of models for experimental features. These follow the same patterns as the standard models but have a `Beta` prefix and may contain additional fields or different behavior:

```mermaid
flowchart LR
    subgraph "Standard Models"
        M["Message"]
        MCP["MessageCreateParams"]
        MCTP["MessageCountTokensParams"]
        RMS["RawMessageStreamEvent"]
        RCBD["RawContentBlockDelta"]
    end
    
    subgraph "Beta Models"
        BM["BetaMessage"]
        BMCP["BetaMessageCreateParams"]
        BMCTP["BetaMessageCountTokensParams"]
        BRMS["BetaRawMessageStreamEvent"]
        BRCBD["BetaRawContentBlockDelta"]
    end
    
    M -.-> BM
    MCP -.-> BMCP
    MCTP -.-> BMCTP
    RMS -.-> BRMS
    RCBD -.-> BRCBD
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/MessageCreateParams.kt:46-340](), [anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/MessageCountTokensParams.kt:46-187](), [anthropic-java-core/src/main/kotlin/com/anthropic/models/beta/messages/BetaRawContentBlockDeltaEvent.kt:19-54]()

## Best Practices for Working with Data Models

1. **Use Builders**: Always use builder methods to create parameter objects
2. **Check Required Fields**: Ensure all required fields are set before building
3. **Type Safety**: Use the strongly-typed methods when possible
4. **Error Handling**: Handle potential exceptions from field access methods
5. **Immutability**: Treat all data model objects as immutable

Example usage pattern:

```java
// Create message parameters
MessageCreateParams params = MessageCreateParams.builder()
    .maxTokens(1024)
    .model(Model.CLAUDE_3_HAIKU_LATEST)
    .addUserMessage("Hello, Claude!")
    .system("You are a helpful AI assistant.")
    .temperature(0.7)
    .build();

// Use the parameters to create a message
Message message = client.messages().create(params);
```

Sources: [anthropic-java-core/src/main/kotlin/com/anthropic/models/messages/MessageCreateParams.kt:215-311]()

---

