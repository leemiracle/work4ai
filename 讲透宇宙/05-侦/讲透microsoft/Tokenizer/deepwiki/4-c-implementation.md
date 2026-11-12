<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Tokenizer · page 4 C# Implementation · fetched 2026-10-26 -->

# C# Implementation

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Tokenizer_C#/TokenizerLib/TikTokenizer.cs](Tokenizer_C#/TokenizerLib/TikTokenizer.cs)
- [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs](Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs)
- [Tokenizer_C#/TokenizerLib/TokenizerLib.csproj](Tokenizer_C#/TokenizerLib/TokenizerLib.csproj)

</details>



This document covers the **Microsoft.DeepDev.TokenizerLib** NuGet package, which provides C# implementation of Byte Pair Encoding (BPE) tokenization for OpenAI large language models. The implementation targets .NET Standard 2.0 and offers a complete API for encoding and decoding text using various OpenAI model configurations.

For information about the TypeScript implementation, see [TypeScript Implementation](#3). For details about the underlying BPE algorithm across both implementations, see [BPE Algorithm Deep Dive](#7.1). For build and packaging specifics, see [Build and Distribution](#4.4).

## Package Architecture

The C# implementation follows a factory pattern with clear separation between tokenizer creation, core tokenization logic, and model configuration management.

### Core Class Structure

```mermaid
classDiagram
    class ITokenizer {
        <<interface>>
        +Encode(string, bool) List~int~
        +Encode(string, IReadOnlyCollection~string~) List~int~
        +EncodeTrimSuffix(string, int, bool) (List~int~, string)
        +EncodeTrimPrefix(string, int, bool) (List~int~, string)
        +Decode(int[]) string
    }
    
    class TokenizerBuilder {
        <<static>>
        +CreateByModelNameAsync(string, IReadOnlyDictionary~string,int~) Task~ITokenizer~
        +CreateByEncoderNameAsync(string, IReadOnlyDictionary~string,int~) Task~ITokenizer~
        +CreateTokenizer(Stream, IReadOnlyDictionary~string,int~, string, int) ITokenizer
        -MODEL_TO_ENCODING Dictionary~string,string~
        -MODEL_PREFIX_TO_ENCODING Dictionary~string,string~
    }
    
    class TikTokenizer {
        -SpecialTokensEncoder IReadOnlyDictionary~string,int~
        -Encoder IReadOnlyDictionary~byte[],int~
        -Decoder IReadOnlyDictionary~int,byte[]~
        -Regex Regex
        -Cache LruCache~string,int[]~
        +Encode(string, bool) List~int~
        +Decode(int[]) string
        -LoadTikTokenBpe(Stream) Dictionary~byte[],int~
        -BytePairEncode(byte[], IReadOnlyDictionary~byte[],int~) List~int~
    }
    
    class LruCache~K,V~ {
        +Lookup(K, out V) bool
        +Add(K, V) void
        +Count int
    }
    
    class BytePairEncoder {
        <<static>>
        +BytePairEncode(byte[], IReadOnlyDictionary~byte[],int~) List~int~
    }
    
    ITokenizer <|.. TikTokenizer
    TokenizerBuilder ..> TikTokenizer : creates
    TikTokenizer *-- LruCache~string,int[]~
    TikTokenizer ..> BytePairEncoder : uses
```

Sources: [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:20-605](), [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs:14-214]()

### Component Interaction Flow

```mermaid
sequenceDiagram
    participant Client
    participant TokenizerBuilder
    participant HttpClient
    participant TikTokenizer
    participant BytePairEncoder
    participant LruCache
    
    Client->>TokenizerBuilder: CreateByModelNameAsync("gpt-4")
    TokenizerBuilder->>TokenizerBuilder: MODEL_TO_ENCODING lookup
    TokenizerBuilder->>HttpClient: GetStreamAsync(tiktoken_url)
    HttpClient-->>TokenizerBuilder: BPE file stream
    TokenizerBuilder->>TikTokenizer: new TikTokenizer(stream, specialTokens, pattern)
    TikTokenizer->>TikTokenizer: LoadTikTokenBpe(stream)
    TikTokenizer-->>TokenizerBuilder: ITokenizer instance
    TokenizerBuilder-->>Client: ITokenizer
    
    Client->>TikTokenizer: Encode("Hello world")
    TikTokenizer->>LruCache: Lookup("Hello")
    alt Cache Miss
        TikTokenizer->>BytePairEncoder: BytePairEncode(bytes, encoder)
        BytePairEncoder-->>TikTokenizer: token_ids
        TikTokenizer->>LruCache: Add("Hello", token_ids)
    end
    TikTokenizer-->>Client: List<int> tokens
```

Sources: [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs:82-98](), [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:250-274]()

## TokenizerBuilder Factory

The `TokenizerBuilder` class serves as the primary entry point for creating tokenizer instances. It provides static factory methods that handle model-to-encoder mapping and remote BPE file retrieval.

### Model Configuration Mapping

The builder maintains two key dictionaries for model resolution:

- `MODEL_TO_ENCODING`: Direct model name to encoder mapping
- `MODEL_PREFIX_TO_ENCODING`: Prefix-based matching for model families

```mermaid
graph TD
    subgraph "Model Resolution"
        ModelName["Model Name Input"]
        DirectLookup["MODEL_TO_ENCODING Lookup"]
        PrefixLookup["MODEL_PREFIX_TO_ENCODING Lookup"]
        EncoderName["Encoder Name Result"]
    end
    
    subgraph "Supported Encoders"
        cl100k["cl100k_base<br/>gpt-4, gpt-3.5-turbo"]
        p50k["p50k_base<br/>text-davinci-003, code-davinci-002"]
        p50k_edit["p50k_edit<br/>text-davinci-edit-001"]
        r50k["r50k_base<br/>text-davinci-001, ada"]
        gpt2_enc["gpt2<br/>gpt2 model"]
    end
    
    ModelName --> DirectLookup
    DirectLookup --> EncoderName
    DirectLookup -.->|"Not Found"| PrefixLookup
    PrefixLookup --> EncoderName
    
    EncoderName --> cl100k
    EncoderName --> p50k
    EncoderName --> p50k_edit
    EncoderName --> r50k
    EncoderName --> gpt2_enc
```

Sources: [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs:17-66](), [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs:84-96]()

### Factory Methods

| Method | Purpose | Parameters |
|--------|---------|------------|
| `CreateByModelNameAsync` | Create tokenizer from OpenAI model name | `modelName`, `extraSpecialTokens` |
| `CreateByEncoderNameAsync` | Create tokenizer from encoder name | `encoderName`, `extraSpecialTokens` |
| `CreateTokenizer` | Create tokenizer from embedded stream | `tikTokenBpeFileStream`, `specialTokensEncoder`, `pattern`, `cacheSize` |

The async methods download BPE rank files from remote URLs, while the synchronous method accepts a pre-loaded stream for embedded scenarios.

Sources: [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs:82-98](), [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs:107-184](), [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs:210-213]()

## TikTokenizer Core Implementation

The `TikTokenizer` class implements the `ITokenizer` interface and provides the main tokenization functionality using Byte Pair Encoding.

### Internal Data Structures

The tokenizer maintains several key data structures for efficient encoding and decoding:

```mermaid
graph TB
    subgraph "Core Data Structures"
        Encoder["Encoder<br/>IReadOnlyDictionary&lt;byte[], int&gt;<br/>Maps byte sequences to token IDs"]
        Decoder["Decoder<br/>IReadOnlyDictionary&lt;int, byte[]&gt;<br/>Maps token IDs to byte sequences"]
        SpecialTokensEncoder["SpecialTokensEncoder<br/>IReadOnlyDictionary&lt;string, int&gt;<br/>Maps special tokens to IDs"]
        SpecialTokensDecoder["SpecialTokensDecoder<br/>IReadOnlyDictionary&lt;int, string&gt;<br/>Maps IDs to special tokens"]
    end
    
    subgraph "Processing Components"
        Regex["Regex<br/>Text splitting pattern"]
        SpecialTokensRegex["SpecialTokensRegex<br/>Special token matching"]
        Cache["LruCache&lt;string, int[]&gt;<br/>Performance optimization"]
    end
    
    subgraph "BPE File Input"
        BPEFile["*.tiktoken file<br/>Base64 token rank"]
    end
    
    BPEFile --> Encoder
    Encoder --> Decoder
    SpecialTokensEncoder --> SpecialTokensDecoder
    Cache -.->|"Caches results from"| Encoder
```

Sources: [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:23-29](), [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:74-91]()

### Encoding Process

The encoding process handles both regular text and special tokens through a multi-stage pipeline:

```mermaid
flowchart TD
    Input["Input Text"]
    SpecialCheck{"Contains Special Tokens?"}
    RegexSplit["Regex.Matches()<br/>Split text into pieces"]
    CacheCheck{"Cache Lookup<br/>LruCache.Lookup()"}
    DirectEncode["Direct Encoder Lookup<br/>Encoder.TryGetValue()"]
    BPEEncode["BytePairEncoder.BytePairEncode()<br/>Recursive BPE algorithm"]
    CacheStore["Cache.Add()<br/>Store result"]
    TokenIds["List&lt;int&gt; Token IDs"]
    
    Input --> SpecialCheck
    SpecialCheck -->|Yes| SpecialFlow["EncodeInternal()<br/>Handle special tokens"]
    SpecialCheck -->|No| RegexSplit
    SpecialFlow --> RegexSplit
    RegexSplit --> CacheCheck
    CacheCheck -->|Hit| TokenIds
    CacheCheck -->|Miss| DirectEncode
    DirectEncode -->|Found| TokenIds
    DirectEncode -->|Not Found| BPEEncode
    BPEEncode --> CacheStore
    CacheStore --> TokenIds
```

Sources: [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:250-274](), [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:141-170]()

### Advanced Encoding Features

The `TikTokenizer` provides specialized encoding methods for token count constraints:

- `EncodeTrimSuffix`: Encodes text up to a maximum token count, truncating from the end
- `EncodeTrimPrefix`: Encodes text up to a maximum token count, truncating from the beginning

These methods are essential for applications that need to fit text within model context windows.

Sources: [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:402-435](), [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:546-579]()

## BPE File Loading and Processing

The tokenizer loads BPE rank data from `.tiktoken` files, which contain Base64-encoded byte sequences paired with integer ranks.

### File Format Processing

```mermaid
flowchart LR
    subgraph "BPE File Format"
        Line1["dGhlIDwvZGl2Pg== 0"]
        Line2["Lg== 1"]
        Line3["</s> 2"]
    end
    
    subgraph "Parsing Process"
        Split["line.Split(' ')"]
        Base64Decode["Convert.FromBase64String()"]
        RankParse["int.TryParse()"]
    end
    
    subgraph "Result Dictionary"
        ByteArray1["byte[] {116,104,101...}"]
        ByteArray2["byte[] {46}"]
        Rank0["Rank: 0"]
        Rank1["Rank: 1"]
    end
    
    Line1 --> Split
    Line2 --> Split
    Split --> Base64Decode
    Split --> RankParse
    Base64Decode --> ByteArray1
    Base64Decode --> ByteArray2
    RankParse --> Rank0
    RankParse --> Rank1
```

Sources: [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:99-139]()

## Special Token Handling

Special tokens like `<|endoftext|>`, `<|fim_prefix|>`, `<|fim_middle|>`, `<|fim_suffix|>`, and `<|endofprompt|>` receive dedicated handling with predefined token IDs that vary by encoder type.

### Special Token Configuration by Encoder

| Encoder | `<|endoftext|>` | `<|fim_prefix|>` | `<|fim_middle|>` | `<|fim_suffix|>` | `<|endofprompt|>` |
|---------|-----------------|------------------|------------------|------------------|-------------------|
| `cl100k_base` | 100257 | 100258 | 100259 | 100260 | 100276 |
| `p50k_base` | 50256 | - | - | - | - |
| `p50k_edit` | 50256 | 50281 | 50282 | 50283 | - |
| `r50k_base` | 50256 | - | - | - | - |
| `gpt2` | 50256 | - | - | - | - |

Sources: [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs:68-72](), [Tokenizer_C#/TokenizerLib/TokenizerBuilder.cs:114-177]()

## Performance Optimizations

The implementation includes several performance optimizations:

### LRU Cache

The `LruCache<string, int[]>` caches encoding results for frequently used text pieces, with a default size of 4096 entries. Cache performance can be monitored through the `NumOfCacheEntries` property.

### Regex Compilation

Text-splitting regex patterns are compiled once during initialization with `RegexOptions.Compiled` for better performance during repeated tokenization operations.

### Memory Efficiency

The implementation uses `IReadOnlyDictionary` interfaces and `byte[]` keys with custom `ByteArrayComparer` for efficient memory usage and lookup performance.

Sources: [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:34-38](), [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:77-78](), [Tokenizer_C#/TokenizerLib/TikTokenizer.cs:101]()

## Project Configuration and Distribution

The library targets .NET Standard 2.0 for broad compatibility and is configured for NuGet distribution with strong-name signing and Microsoft code signing through MicroBuild.

### Project Properties

- **Target Framework**: `netstandard2.0`
- **Package ID**: `Microsoft.DeepDev.TokenizerLib`
- **Assembly Version**: Defined in project file
- **Strong Name Signing**: Enabled with public key
- **Code Signing**: Microsoft Authenticode through MicroBuild

Sources: [Tokenizer_C#/TokenizerLib/TokenizerLib.csproj:3-23](), [Tokenizer_C#/TokenizerLib/TokenizerLib.csproj:38-50]()

---

