<!-- source: DeepWiki mcp.deepwiki.com · repo anthropics/anthropic-sdk-ruby · page 11 Type System · fetched 2026-10-26 -->

# Type System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [lib/anthropic/internal/type/base_model.rb](lib/anthropic/internal/type/base_model.rb)
- [lib/anthropic/internal/type/boolean.rb](lib/anthropic/internal/type/boolean.rb)
- [lib/anthropic/internal/type/converter.rb](lib/anthropic/internal/type/converter.rb)
- [lib/anthropic/internal/type/enum.rb](lib/anthropic/internal/type/enum.rb)
- [lib/anthropic/internal/type/io_like.rb](lib/anthropic/internal/type/io_like.rb)
- [lib/anthropic/internal/type/request_parameters.rb](lib/anthropic/internal/type/request_parameters.rb)
- [lib/anthropic/internal/type/union.rb](lib/anthropic/internal/type/union.rb)
- [rbi/lib/anthropic/internal/type/boolean.rbi](rbi/lib/anthropic/internal/type/boolean.rbi)
- [sig/anthropic/internal/type/boolean.rbs](sig/anthropic/internal/type/boolean.rbs)
- [test/anthropic/internal/type/base_model_test.rb](test/anthropic/internal/type/base_model_test.rb)

</details>



The Anthropic Ruby SDK implements a sophisticated type system that handles conversion, validation, and serialization of data between the Ruby application and Anthropic's APIs. This system ensures type safety, provides helpful error messages, and makes it easier to work with the API's request parameters and response models.

This page documents the internal type system architecture and behavior. For information on using the SDK's public models and parameter types, see [Messages API](#4) and [Completions API](#6).

## Overview of the Type System

The type system serves several critical functions in the SDK:

1. **Type Definition** - Defines structured models for requests and responses
2. **Type Conversion** - Intelligently converts between Ruby and API representations
3. **Type Validation** - Ensures data conforms to expected formats and constraints
4. **Serialization** - Handles conversion to/from JSON for API communication

The type system is designed to operate invisibly to SDK users in most cases, while providing rich debugging information when necessary.

```mermaid
flowchart TD
    subgraph "Type System"
        BM["BaseModel"]
        CONV["Converter"]
        
        subgraph "Type Specializations"
            BOOL["Boolean"]
            ENUM["Enum"]
            UNION["Union"]
            ARR["ArrayOf"]
            HASH["HashOf"]
            IO["IOLike"]
        end
        
        REQ["RequestParameters"]
    end
    
    subgraph "SDK Usage"
        PARAMS["API Request Parameters"]
        RESP["API Response Models"]
        SER["Serialization"]
        VAL["Validation"]
    end
    
    BM --> PARAMS
    BM --> RESP
    CONV --> BM
    CONV --> SER
    BOOL --> BM
    ENUM --> BM
    UNION --> BM
    ARR --> BM
    HASH --> BM
    IO --> BM
    PARAMS --> REQ
    BM --> VAL
```

Sources: [lib/anthropic/internal/type/base_model.rb:1-380](), [lib/anthropic/internal/type/converter.rb:1-247]()

## Core Type System Components

The type system is built around several key components that work together to provide type safety and conversion capabilities.

### BaseModel

The `BaseModel` class serves as the foundation for all structured data models in the SDK, including request parameters and API responses. It provides a way to define fields with specific types and validation rules.

Key features of `BaseModel`:
- Defines required and optional fields with specific types
- Handles validation and conversion of field values
- Supports field mapping between API and SDK representations
- Provides serialization to JSON and other formats
- Supports pattern matching through `deconstruct_keys`

```mermaid
classDiagram
    class BaseModel {
        +known_fields()
        +fields()
        +required(name, type, spec)
        +optional(name, type, spec)
        +request_only(block)
        +response_only(block)
        +coerce(value, state)
        +dump(value, state)
        +[](key)
        +to_h()
        +to_json()
        +initialize(data)
    }
    
    class ModelInstance {
        +field_accessor1
        +field_accessor2
        +[](key)
        +to_h()
        +to_json()
    }
    
    BaseModel <|-- "UserDefinedModel"
    "UserDefinedModel" ..> ModelInstance : instantiates
```

Sources: [lib/anthropic/internal/type/base_model.rb:4-380]()

### Converter

The `Converter` module provides the core type conversion functionality in the SDK. It's responsible for converting Ruby values to and from their API representations:

- **coerce**: Converts API data to appropriate Ruby types
- **dump**: Converts Ruby objects to API-compatible representations

The converter handles both simple primitive types and complex nested structures.

```mermaid
flowchart TD
    subgraph "Converter"
        COERCE["coerce(target, value, state)"]
        DUMP["dump(target, value, state)"]
        TYPE_INFO["type_info(spec)"]
    end
    
    subgraph "Input/Output"
        API_DATA["API Data"]
        RUBY_OBJ["Ruby Objects"]
    end
    
    API_DATA --> COERCE --> RUBY_OBJ
    RUBY_OBJ --> DUMP --> API_DATA
    TYPE_INFO --> COERCE
    TYPE_INFO --> DUMP
```

Sources: [lib/anthropic/internal/type/converter.rb:7-246]()

### Type Specializations

The type system includes several specialized type handlers for different data types:

- **Boolean**: Handles boolean values (true/false)
- **Enum**: Handles enumerated values with predefined sets of options
- **Union**: Handles values that can be one of several different types
- **ArrayOf**: Handles arrays of values with specific item types
- **HashOf**: Handles hashes with specific key and value types
- **IOLike**: Handles IO-like objects (Pathname, StringIO, etc.)

These specializations provide type-specific conversion and validation logic.

```mermaid
classDiagram
    class Converter {
        +coerce(value, state)
        +dump(value, state)
    }
    
    class Boolean {
        +coerce(value, state)
        +dump(value, state)
        +===(other)
        +==(other)
    }
    
    class Enum {
        +values()
        +coerce(value, state)
        +dump(value, state)
        +===(other)
        +==(other)
    }
    
    class Union {
        +variants()
        +discriminator(property)
        +variant(key, spec)
        +coerce(value, state)
        +dump(value, state)
        +===(other)
        +==(other)
    }
    
    Converter <|-- Boolean
    Converter <|-- Enum
    Converter <|-- Union
```

Sources: [lib/anthropic/internal/type/boolean.rb:1-59](), [lib/anthropic/internal/type/enum.rb:1-114](), [lib/anthropic/internal/type/union.rb:1-217]()

## Type Conversion Process

The type system performs two main conversion operations:

1. **Coercion** - Converting from API data to Ruby objects
2. **Dumping** - Converting from Ruby objects to API data

### Coercion Process

The coercion process converts values from API representations to Ruby objects, applying type-specific conversion rules and validation.

```mermaid
flowchart TD
    START["Start Coercion"] --> CHECK_TYPE["Check Value Type"]
    
    CHECK_TYPE --> IS_TARGET{"Is already\ntarget type?"}
    IS_TARGET -->|Yes| RETURN_VALUE["Return Value"]
    IS_TARGET -->|No| HANDLE_TYPE{"Handle by\ntype"}
    
    HANDLE_TYPE -->|Primitive| CONVERT_PRIMITIVE["Convert Primitive\n(String, Integer, etc.)"]
    HANDLE_TYPE -->|BaseModel| CONVERT_MODEL["Convert to Model\n(coerce fields)"]
    HANDLE_TYPE -->|Enum| CONVERT_ENUM["Convert to Enum Value"]
    HANDLE_TYPE -->|Union| TRY_VARIANTS["Try Each Variant\nFind Best Match"]
    HANDLE_TYPE -->|Array| CONVERT_ARRAY["Convert Array Items"]
    HANDLE_TYPE -->|Hash| CONVERT_HASH["Convert Hash Keys/Values"]
    
    CONVERT_PRIMITIVE --> RETURN_VALUE
    CONVERT_MODEL --> RETURN_VALUE
    CONVERT_ENUM --> RETURN_VALUE
    TRY_VARIANTS --> RETURN_VALUE
    CONVERT_ARRAY --> RETURN_VALUE
    CONVERT_HASH --> RETURN_VALUE
```

Sources: [lib/anthropic/internal/type/converter.rb:12-222](), [lib/anthropic/internal/type/base_model.rb:186-253]()

### Dumping Process

The dumping process converts Ruby objects to API-compatible representations, preparing them for transmission to the API.

```mermaid
flowchart TD
    START["Start Dump"] --> CHECK_TYPE["Check Value Type"]
    
    CHECK_TYPE --> HANDLE_TYPE{"Handle by\ntype"}
    
    HANDLE_TYPE -->|BaseModel| DUMP_MODEL["Dump Model to Hash"]
    HANDLE_TYPE -->|Array| DUMP_ARRAY["Dump Array Items"]
    HANDLE_TYPE -->|Hash| DUMP_HASH["Dump Hash Values"]
    HANDLE_TYPE -->|IO/Pathname| SERIALIZE_IO["Create Serialization Adapter"]
    HANDLE_TYPE -->|Other| RETURN_AS_IS["Return Value As Is"]
    
    DUMP_MODEL --> APPLY_FIELD_RULES["Apply Field Rules\n(omit response_only)"]
    APPLY_FIELD_RULES --> RETURN_HASH["Return Serialized Hash"]
    
    DUMP_ARRAY --> RETURN_ARRAY["Return Serialized Array"]
    DUMP_HASH --> RETURN_HASH
    SERIALIZE_IO --> SET_NO_RETRY["Set can_retry=false"]
    SET_NO_RETRY --> RETURN_ADAPTER["Return Serialization Adapter"]
    RETURN_AS_IS --> FINAL["Final Result"]
    
    RETURN_HASH --> FINAL
    RETURN_ARRAY --> FINAL
    RETURN_ADAPTER --> FINAL
```

Sources: [lib/anthropic/internal/type/converter.rb:33-50](), [lib/anthropic/internal/type/base_model.rb:255-295]()

## Model Definition

The type system provides a declarative way to define structured models with field types and validation rules.

### Field Definition

Models define fields using `required` and `optional` methods, specifying the field name, type, and additional options.

```mermaid
flowchart TD
    MODEL["Define Model Class"] --> REQ["Define Required Fields\nrequired :field, Type"]
    MODEL --> OPT["Define Optional Fields\noptional :field, Type"]
    
    REQ --> TYPE_OPTIONS{"Type Options"}
    OPT --> TYPE_OPTIONS
    
    TYPE_OPTIONS -->|"nil?: true"| ALLOW_NIL["Allow Nil Values"]
    TYPE_OPTIONS -->|"api_name: 'fieldName'"| API_NAME["Custom API Field Name"]
    TYPE_OPTIONS -->|"const: :value"| CONST_VAL["Constant Value"]
    
    ALLOW_NIL --> REGISTER["Register Field in known_fields"]
    API_NAME --> REGISTER
    CONST_VAL --> REGISTER
    
    REGISTER --> ACCESSORS["Generate Accessors"]
```

Sources: [lib/anthropic/internal/type/base_model.rb:43-145]()

### Request vs Response Fields

The type system allows designating fields specifically for requests or responses using the `request_only` and `response_only` blocks:

- `request_only`: Fields included when sending requests but not expected in responses
- `response_only`: Fields expected in responses but not included in requests

```mermaid
classDiagram
    class BaseModel {
        +request_only(block)
        +response_only(block)
    }
    
    class RequestModel {
        +required fields
        +optional fields
        +request_only fields
    }
    
    class ResponseModel {
        +required fields
        +optional fields
        +response_only fields
    }
    
    BaseModel <|-- RequestModel
    BaseModel <|-- ResponseModel
    
    note for RequestModel "Fields in request_only block\nare sent to API but not expected\nin responses"
    note for ResponseModel "Fields in response_only block\nare expected from API but\nnot sent in requests"
```

Sources: [lib/anthropic/internal/type/base_model.rb:147-170]()

## Advanced Type Features

The type system includes several advanced features for handling complex data structures and constraints.

### Union Types

Union types allow a field to accept values of different types, with automatic type detection and conversion. The system can use a discriminator field to determine the appropriate type.

```mermaid
flowchart TD
    UNION["Define Union Module"] --> DISCRIMINATOR["Set discriminator field\ndiscriminator :type"]
    UNION --> VARIANTS["Define variants\nvariant :key, Type\nvariant Type"]
    
    DISCRIMINATOR --> COERCE["Coercion Process"]
    VARIANTS --> COERCE
    
    COERCE --> CHECK_DISCRIMINATOR{"Check discriminator\nin value"}
    CHECK_DISCRIMINATOR -->|"Match found"| USE_VARIANT["Use matching variant type"]
    CHECK_DISCRIMINATOR -->|"No match"| TRY_ALL["Try all variants\nfind best match"]
    
    USE_VARIANT --> RETURN["Return converted value"]
    TRY_ALL --> RETURN
```

Sources: [lib/anthropic/internal/type/union.rb:32-216]()

### Enum Types

Enum types provide a way to define a constrained set of valid values for a field, mapping between different representations.

```mermaid
flowchart TD
    ENUM["Define Enum Module"] --> CONSTANTS["Define Constants\nVALUE = :value"]
    CONSTANTS --> VALUES["Generate values list"]
    
    VALUES --> COERCE["Coercion Process"]
    
    COERCE --> CHECK_VALUE{"Is value in\nenum values?"}
    CHECK_VALUE -->|Yes| RETURN_VALUE["Return value"]
    CHECK_VALUE -->|No| RETURN_ORIGINAL["Return original\n(may fail validation)"]
```

Sources: [lib/anthropic/internal/type/enum.rb:6-113]()

### Collection Types (ArrayOf and HashOf)

The type system provides special handlers for collections with type constraints on their elements:

- `ArrayOf`: Arrays where all elements must be of a specific type
- `HashOf`: Hashes with constraints on keys and/or values

These types recursively apply type conversion and validation to collection elements.

Sources: Test usages in [test/anthropic/internal/type/base_model_test.rb:248-292]()

## Integration with SDK Request Flow

The type system is integrated into the SDK's request flow through the `RequestParameters` module, which ensures proper serialization and handling of request options.

```mermaid
sequenceDiagram
    participant Client as Client
    participant Resource as API Resource
    participant Request as RequestParameters
    participant Type as Type System
    participant API as Anthropic API
    
    Client->>Resource: Create request
    Resource->>Request: Prepare parameters
    Request->>Type: dump_request(params)
    Type->>Type: dump(params, state)
    Type->>Type: Extract request_options
    Type->>Request: Return [body, options]
    Request->>API: Send request with body
    API->>Request: Response data
    Request->>Type: coerce(target, data)
    Type->>Client: Return model instance
```

Sources: [lib/anthropic/internal/type/request_parameters.rb:4-49]()

## Error Handling

The type system provides robust error handling with meaningful error messages when type conversion fails.

When a conversion error occurs during model field access, the SDK throws a `Anthropic::Errors::ConversionError` with details about what went wrong. Users can still access the raw value using the `[]` accessor if needed.

```ruby
begin
  model_instance.field  # Parsed and validated field
rescue Anthropic::Errors::ConversionError => e
  raw_value = model_instance[:field]  # Raw, unparsed value
end
```

Sources: [lib/anthropic/internal/type/base_model.rb:89-106]()

## Practical Example

Let's walk through a practical example of how the type system processes a request and response for a message creation:

```mermaid
flowchart TD
    subgraph "Application Code"
        CODE["client.messages.create(\n  model: 'claude-3-opus-20240229',\n  max_tokens: 1024,\n  messages: [{role: 'user', content: 'Hello'}]\n)"]
    end
    
    subgraph "Type System Processing"
        CODE --> PARAMS["MessageCreateParams instance"]
        PARAMS --> VALIDATE["Validate & convert parameters"]
        VALIDATE --> DUMP["Dump to API format"]
        
        DUMP --> API_REQUEST["API Request"]
        API_REQUEST --> API_RESPONSE["API Response"]
        
        API_RESPONSE --> COERCE["Coerce to Message model"]
        COERCE --> MODEL["Message instance"]
    end
    
    MODEL --> APP_RESULT["Return to application"]
```

Sources: Understanding derived from all examined files

## Summary

The Anthropic Ruby SDK's type system provides a robust foundation for working with the Anthropic API, offering:

1. **Type Safety** - Ensures values conform to expected types and formats
2. **Seamless Conversion** - Handles conversion between API and Ruby representations
3. **Helpful Errors** - Provides clear error messages when issues occur
4. **Request/Response Handling** - Manages the serialization and deserialization process
5. **Rich Models** - Creates structured models with validation and accessors

This system operates largely behind the scenes, making the SDK easy to use while providing robust guarantees about data integrity.

Sources: All examined files

---

