<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/poml · page 7 Advanced Topics · fetched 2026-10-26 -->

# Advanced Topics

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [packages/poml/base.tsx](packages/poml/base.tsx)
- [packages/poml/index.ts](packages/poml/index.ts)
- [packages/poml/tests/base.test.tsx](packages/poml/tests/base.test.tsx)
- [packages/poml/tests/index.test.tsx](packages/poml/tests/index.test.tsx)
- [packages/poml/tests/trace.test.tsx](packages/poml/tests/trace.test.tsx)
- [packages/poml/tests/writer.test.tsx](packages/poml/tests/writer.test.tsx)
- [packages/poml/util/index.ts](packages/poml/util/index.ts)
- [packages/poml/util/trace.ts](packages/poml/util/trace.ts)
- [packages/poml/writer.ts](packages/poml/writer.ts)

</details>



This page covers advanced POML features including debugging capabilities, optimization strategies, error handling systems, and source mapping. These features enable sophisticated prompt engineering workflows and production deployment scenarios.

The material builds upon [Core Architecture](#3) and [Language Reference](#4). For specific integration patterns, see [Integrations](#5). For development information, see [Development and Contributing](#8).

## Tracing and Debugging

POML provides comprehensive tracing capabilities for debugging prompt processing and tracking execution flow. The tracing system captures input markup, context data, execution results, and source mappings.

### Trace System Architecture

#### Trace System Implementation

```mermaid
graph TD
    subgraph "Trace Configuration"
        setTrace["setTrace(enabled, dir)"]
        clearTrace["clearTrace()"]
        isTracing["isTracing()"]
        POML_TRACE["POML_TRACE env var"]
    end
    
    subgraph "Trace Capture"
        dumpTrace["dumpTrace()"]
        nextIndex["nextIndex()"]
        replaceBuffers["replaceBuffers()"]
        parseJsonWithBuffers["parseJsonWithBuffers()"]
    end
    
    subgraph "Trace Files"
        pomlFile[".poml - markup"]
        contextFile[".context.json - variables"]
        stylesheetFile[".stylesheet.json - styles"]
        resultFile[".result.json - output"]
        envFile[".env - source path"]
        sourceFile[".source.poml - symlink"]
    end
    
    setTrace --> dumpTrace
    isTracing --> dumpTrace
    dumpTrace --> nextIndex
    dumpTrace --> replaceBuffers
    
    dumpTrace --> pomlFile
    dumpTrace --> contextFile
    dumpTrace --> stylesheetFile
    dumpTrace --> resultFile
    dumpTrace --> envFile
    dumpTrace --> sourceFile
```

### Trace File Management

The `nextIndex` function ensures atomic trace file creation:

| File Type | Purpose | Example |
|-----------|---------|---------|
| `0001.main.poml` | Input markup | Original POML content |
| `0001.main.context.json` | Context variables | Template data with base64 buffers |
| `0001.main.stylesheet.json` | Stylesheet config | CSS-like styling rules |
| `0001.main.result.json` | Processing output | Messages, schema, tools, runtime |
| `0001.main.env` | Environment info | `SOURCE_PATH=/path/to/file.poml` |
| `0001.main.source.poml` | Source symlink | Links to original file |

### Buffer Serialization

The tracing system handles binary data through base64 encoding:

```typescript
// Buffer replacement pattern from trace.ts
function replaceBuffers(value: any): any {
  if (Buffer.isBuffer(value)) {
    return { __base64__: value.toString('base64') };
  }
  // ... recursive handling for objects and arrays
}
```

### CLI Integration

The `commandLine` function integrates tracing when `--trace-dir` is specified:

```typescript
// From index.ts commandLine function
if (args.traceDir) {
  setTrace(true, args.traceDir);
}
// ... processing happens
if (isTracing()) {
  dumpTrace(input, context, stylesheet, result, sourcePath, prettyOutput);
}
```

**Sources:** [packages/poml/util/trace.ts:36-144](), [packages/poml/tests/trace.test.tsx:16-109](), [packages/poml/index.ts:157-254]()

## Error Handling and Validation

POML implements a sophisticated error handling system with specialized error types, source position tracking, and graceful degradation strategies.

### ErrorCollection Singleton

#### Error Management System

```mermaid
graph TD
    subgraph "Error Types"
        PomlError["PomlError (base)"]
        ReadError["ReadError"]
        WriteError["WriteError"]
        SystemError["SystemError"]
    end
    
    subgraph "ErrorCollection Methods"
        add["ErrorCollection.add()"]
        first["ErrorCollection.first()"]
        empty["ErrorCollection.empty()"]
        clear["ErrorCollection.clear()"]
        list["ErrorCollection.list()"]
    end
    
    subgraph "Error Context"
        startIndex["startIndex"]
        endIndex["endIndex"]
        sourcePath["sourcePath"]
        irStartIndex["irStartIndex"]
        irEndIndex["irEndIndex"]
        severity["severity: 'error' | 'warning'"]
    end
    
    ReadError --> add
    WriteError --> add
    SystemError --> add
    
    startIndex --> ReadError
    endIndex --> ReadError
    sourcePath --> ReadError
    
    irStartIndex --> WriteError
    irEndIndex --> WriteError
    
    severity --> PomlError
```

### Error Recovery Patterns

#### Component Error Boundaries

The `useWithCatch` hook provides async error handling for React components:

```typescript
// Pattern from base.tsx
export const useWithCatch = <T,>(promise: Promise<T>, props: PropsBase) => {
  const catchedPromise = promise.catch((err: any) => {
    if (err instanceof PomlError) {
      ErrorCollection.add(err);
    } else {
      ErrorCollection.add(
        ReadError.fromProps(
          err && err.message ? err.message : 'Unknown error...',
          props,
          { cause: err }
        )
      );
    }
  });
  return React.use(catchedPromise);
};
```

#### Writer Error Handling

The `Writer.raiseError` method provides contextual error information:

| Error Property | Source | Purpose |
|---------------|---------|---------|
| `originalStartIndex` | Element attribute | Original source position |
| `originalEndIndex` | Element attribute | Original source end |
| `sourcePath` | Element context | File path for debugging |
| `irStartIndex` | Element processing | IR position start |
| `irEndIndex` | Element processing | IR position end |
| `relatedIr` | Writer state | Full IR context |

### Validation Strategies

The component system validates props through multiple stages:

1. **Required Props Check**: `throwIfMissing` validates required properties
2. **Type Validation**: `preprocessProps` converts and validates data types  
3. **Speaker Validation**: Ensures valid speaker values (`human`, `ai`, `system`, `tool`)
4. **Attribute Validation**: Component-specific validation rules

**Sources:** [packages/poml/base.tsx:320-472](), [packages/poml/writer.ts:201-229](), [packages/poml/tests/index.test.tsx:445-520]()

## Token Counting and Optimization

POML provides sophisticated content truncation and token management capabilities through the Writer system. The implementation supports both character-based and token-based limits with priority-driven content removal.

### Writer Truncation System

#### Truncation Implementation

```mermaid
graph TD
    subgraph "TruncateOptions"
        truncateMarker["truncateMarker"]
        truncateDirection["truncateDirection"]
        tokenEncodingModel["tokenEncodingModel"]
    end
    
    subgraph "Writer.truncateText"
        charLimit["charLimit check"]
        tokenLimit["tokenLimit check"]
        tokenizerCache["tokenizerCache[model]"]
        encodingForModel["encodingForModel()"]
    end
    
    subgraph "Optimization Strategy"
        byteCheck["Buffer.byteLength() optimization"]
        tokenEncode["enc.encode(text)"]
        tokenDecode["enc.decode(tokens)"]
    end
    
    charLimit --> tokenLimit
    tokenLimit --> byteCheck
    byteCheck --> tokenizerCache
    tokenizerCache --> encodingForModel
    encodingForModel --> tokenEncode
    tokenEncode --> tokenDecode
    
    truncateDirection --> tokenDecode
    truncateMarker --> tokenDecode
```

### Priority-Based Content Removal

The `MarkdownWriter.reduceBoxesByLimit` method implements sophisticated content prioritization:

| Priority Level | Removal Order | Implementation |
|---------------|---------------|----------------|
| `undefined` | Removed first | Default priority 0 |
| `priority="1"` | Low priority | Removed before higher priorities |
| `priority="2"` | Medium priority | Preserved longer |
| `priority="3"` | High priority | Preserved longest |

#### Priority Removal Algorithm

```mermaid
graph LR
    subgraph "MarkdownBox System"
        makeBox["makeBox()"]
        priority["priority attribute"]
        charLimit["char-limit"]
        tokenLimit["token-limit"]
    end
    
    subgraph "reduceBoxesByLimit"
        totalChars["totalChars()"]
        totalTokens["totalTokens()"]
        currentBoxes["current boxes"]
        minPriority["Math.min priorities"]
    end
    
    subgraph "Size Calculation"
        getTokenLength["getTokenLength()"]
        byteEstimate["BYTES_PER_TOKEN_ESTIMATE"]
        tokenizerCache["Writer.tokenizerCache"]
    end
    
    makeBox --> priority
    priority --> reduceBoxesByLimit
    charLimit --> totalChars
    tokenLimit --> totalTokens
    
    totalTokens --> getTokenLength
    getTokenLength --> byteEstimate
    getTokenLength --> tokenizerCache
    
    currentBoxes --> minPriority
    minPriority --> currentBoxes
```

### Performance Optimizations

The tokenizer system includes several performance optimizations:

1. **Tokenizer Caching**: Reuses `Tiktoken` instances via `tokenizerCache`
2. **Byte Count Estimation**: Skips tokenization when `byteCount <= tokenLimit`
3. **Conservative Estimation**: Uses `BYTES_PER_TOKEN_ESTIMATE = 4` for quick checks

**Sources:** [packages/poml/writer.ts:90-152](), [packages/poml/writer.ts:753-842](), [packages/poml/tests/index.test.tsx:59-160](), [packages/poml/tests/writer.test.tsx:289-368]()

## Source Maps and Position Tracking

POML maintains detailed source position information throughout the processing pipeline, enabling precise error reporting and debugging capabilities.

### Source Mapping Architecture

#### Position Tracking System

```mermaid
graph TD
    subgraph "Input Tracking"
        originalStartIndex["originalStartIndex"]
        originalEndIndex["originalEndIndex"]
        sourcePath["sourcePath"]
        element["cheerio element"]
    end
    
    subgraph "IR Tracking"
        irStartIndex["irStartIndex"]
        irEndIndex["irEndIndex"]
        startIndex["element.startIndex"]
        endIndex["element.endIndex"]
    end
    
    subgraph "Output Mapping"
        outputStart["outputStart"]
        outputEnd["outputEnd"]
        content["RichContent"]
        MappingNode["MappingNode"]
    end
    
    subgraph "Writer Methods"
        createMappingNode["createMappingNode()"]
        buildSourceMap["buildSourceMap()"]
        writeWithSourceMap["writeWithSourceMap()"]
        writeMessagesWithSourceMap["writeMessagesWithSourceMap()"]
    end
    
    originalStartIndex --> createMappingNode
    originalEndIndex --> createMappingNode
    startIndex --> createMappingNode
    endIndex --> createMappingNode
    
    createMappingNode --> MappingNode
    MappingNode --> buildSourceMap
    buildSourceMap --> writeWithSourceMap
    buildSourceMap --> writeMessagesWithSourceMap
    
    outputStart --> content
    outputEnd --> content
```

### Source Map Data Structures

| Interface | Properties | Purpose |
|-----------|-----------|---------|
| `MappingNode` | `originalStart`, `originalEnd`, `inputStart`, `inputEnd`, `outputStart`, `outputEnd` | Maps IR positions to output positions |
| `SourceMapRichContent` | `startIndex`, `endIndex`, `irStartIndex`, `irEndIndex`, `content` | Single content segment with source info |
| `SourceMapMessage` | `speaker`, `content: SourceMapRichContent[]` | Message with detailed source mapping |

### Boundary Detection Algorithm

The `buildSourceMap` method creates precise content segments:

```typescript
// Boundary collection from writer.ts
const boundaries = new Set<number>();
result.mappings.forEach((m) => {
  boundaries.add(m.outputStart);
  boundaries.add(m.outputEnd + 1);
});
result.multimedia.forEach((m) => {
  boundaries.add(m.index);
  boundaries.add(m.index + 1);
});
```

#### Source Segment Creation

```mermaid
graph LR
    subgraph "Boundary Detection"
        mappingBoundaries["mapping boundaries"]
        multimediaBoundaries["multimedia boundaries"]
        sortedPoints["sorted points"]
    end
    
    subgraph "Segment Creation"
        textSlices["text slices"]
        multimediaItems["multimedia items"]
        chosenMapping["most specific mapping"]
    end
    
    subgraph "Segment Categories"
        topSegments["topSegments (position='top')"]
        middleSegments["middleSegments"]
        bottomSegments["bottomSegments (position='bottom')"]
    end
    
    mappingBoundaries --> sortedPoints
    multimediaBoundaries --> sortedPoints
    sortedPoints --> textSlices
    sortedPoints --> multimediaItems
    
    textSlices --> chosenMapping
    multimediaItems --> chosenMapping
    
    chosenMapping --> topSegments
    chosenMapping --> middleSegments
    chosenMapping --> bottomSegments
```

### Speaker Assignment Integration

The source mapping system integrates with speaker assignment through `assignSpeakers`:

1. **Speaker Inheritance**: Child elements inherit parent speaker unless overridden
2. **Default Behavior**: System speaker becomes human when human speaker appears
3. **Segment Mapping**: Speaker boundaries align with source map segments
4. **Range Optimization**: Non-whitespace segments determine message source ranges

**Sources:** [packages/poml/writer.ts:154-167](), [packages/poml/writer.ts:425-533](), [packages/poml/writer.ts:362-417](), [packages/poml/tests/writer.test.tsx:63-287]()

## Error Handling and Debugging

POML implements a comprehensive error handling system with specialized error types, source mapping for debugging, and graceful error recovery mechanisms.

### Error Collection System

The `ErrorCollection` singleton manages all errors during processing:

```mermaid
graph TD
    subgraph "Error Types"
        POML_ERROR["PomlError (base)"]
        READ_ERROR["ReadError"]
        WRITE_ERROR["WriteError"] 
        SYSTEM_ERROR["SystemError"]
    end
    
    subgraph "ErrorCollection Singleton"
        ADD["ErrorCollection.add()"]
        FIRST["ErrorCollection.first()"]
        EMPTY["ErrorCollection.empty()"]
        CLEAR["ErrorCollection.clear()"]
        LIST["ErrorCollection.list()"]
    end
    
    subgraph "Error Context"
        START_INDEX["startIndex"]
        END_INDEX["endIndex"]
        SOURCE_PATH["sourcePath"]
        IR_MAPPING["irStartIndex/irEndIndex"]
    end
    
    READ_ERROR --> ADD
    WRITE_ERROR --> ADD
    SYSTEM_ERROR --> ADD
    
    START_INDEX --> READ_ERROR
    END_INDEX --> READ_ERROR
    SOURCE_PATH --> READ_ERROR
    
    IR_MAPPING --> WRITE_ERROR
    
    ADD --> FIRST
    ADD --> EMPTY
    ADD --> LIST
```

### Error Types and Context

| Error Type | Properties | Use Case |
|-----------|-----------|----------|
| `ReadError` | `startIndex`, `endIndex`, `sourcePath` | Parse-time validation errors |
| `WriteError` | `irStartIndex`, `irEndIndex`, `relatedIr` | Runtime rendering errors |
| `SystemError` | Standard `Error` properties | Internal system failures |

### Source Mapping for Debugging

The `writeWithSourceMap` and `writeMessagesWithSourceMap` methods provide detailed mapping between input and output for debugging:

```mermaid
graph LR
    subgraph "Input Tracking"
        ORIG_START["originalStartIndex"]
        ORIG_END["originalEndIndex"]
        IR_START["irStartIndex"]
        IR_END["irEndIndex"]
    end
    
    subgraph "Output Mapping"
        OUT_START["outputStart"]
        OUT_END["outputEnd"]
        CONTENT["content"]
    end
    
    subgraph "SourceMapMessage"
        SPEAKER["speaker"]
        MSG_CONTENT["SourceMapRichContent[]"]
    end
    
    subgraph "Debugging Workflow"
        BUILD_MAP["buildSourceMap()"]
        CREATE_SEGMENTS["Create SourceSegment[]"]
        ASSIGN_SPEAKERS["assignSpeakers()"]
    end
    
    ORIG_START --> BUILD_MAP
    ORIG_END --> BUILD_MAP
    IR_START --> BUILD_MAP
    IR_END --> BUILD_MAP
    
    BUILD_MAP --> CREATE_SEGMENTS
    CREATE_SEGMENTS --> OUT_START
    CREATE_SEGMENTS --> OUT_END
    
    ASSIGN_SPEAKERS --> SPEAKER
    CREATE_SEGMENTS --> MSG_CONTENT
```

### Error Recovery Patterns

The system implements several error recovery strategies:

#### Component Error Boundaries

The `PomlComponent.render` method wraps component execution with error handling:

```typescript
// From PomlComponent.render
try {
  this.throwIfMissing(props);
  if (this.options.applyStyleSheet) {
    props = this.style(props);
  }
  props = this.preprocessProps(props);
  return this.componentFunc(props);
} catch (e) {
  if (e instanceof PomlError) {
    ErrorCollection.add(e);
  } else {
    ErrorCollection.add(
      ReadError.fromProps(`Error in component render of ${this.officialName}: ${e}`, props)
    );
  }
  return null;
}
```

#### Writer Error Handling

The `Writer.raiseError` method provides contextual error information:

```typescript
// Writer error handling pattern
protected raiseError(message: string, element: cheerio.Cheerio<any>): WriterPartialResult {
  ErrorCollection.add(
    new WriteError(
      message,
      parseAttrAsInt('original-start-index'),
      parseAttrAsInt('original-end-index'),
      element[0].sourcePath,
      element[0].startIndex,
      element[0].endIndex,
      this.ir
    )
  );
  return emptyOutput;
}
```

**Sources:** [packages/poml/base.tsx:328-365](), [packages/poml/base.tsx:842-880](), [packages/poml/writer.ts:214-244](), [packages/poml/tests/index.test.tsx:427-501]()

## Advanced Component Patterns

### Custom Component Development

POML's component system supports sophisticated patterns for building reusable, configurable components.

### Performance-Critical Component Design

When developing components that process large amounts of data or complex structures, consider these patterns:

- **Lazy rendering**: Components that defer expensive operations until actually needed
- **Memoization**: Caching computed results to avoid redundant processing  
- **Stream processing**: Handling large datasets without loading everything into memory
- **Resource cleanup**: Proper disposal of resources like file handles or network connections

### Component Composition Strategies

Advanced component composition involves understanding the component lifecycle and optimization opportunities:

```mermaid
graph LR
    subgraph "Component Lifecycle"
        REGISTRATION["Component<br/>Registration"]
        INSTANTIATION["Component<br/>Instantiation"]
        RENDERING["Render Phase"]
        CLEANUP["Cleanup Phase"]
    end
    
    subgraph "Optimization Points"
        CACHE_STRATEGY["Caching Strategy"]
        MEMORY_POOL["Memory Pooling"]
        ASYNC_RENDERING["Async Rendering"]
    end
    
    REGISTRATION --> INSTANTIATION
    INSTANTIATION --> RENDERING  
    RENDERING --> CLEANUP
    
    CACHE_STRATEGY --> RENDERING
    MEMORY_POOL --> INSTANTIATION
    ASYNC_RENDERING --> RENDERING
```

**Sources:** [packages/poml/util/image.ts:27-45](), [media/style.css:243-385]()

## Debugging and Profiling

### VS Code Extension Debugging

The VS Code extension provides comprehensive debugging capabilities through its preview and testing system:

- **Live preview**: Real-time rendering updates as you edit POML files
- **Interactive toolbar**: Quick access to testing and debugging commands
- **Token counting**: Immediate feedback on token usage and costs
- **Error highlighting**: Syntax and semantic error detection

### Performance Profiling

For performance-critical applications, POML provides several profiling hooks:

```mermaid
graph TD
    subgraph "Profiling Points"
        PARSE_TIME["Parse Time"]
        RENDER_TIME["Render Time"]
        TOKEN_COUNT["Token Count"]
        MEMORY_USAGE["Memory Usage"]
    end
    
    subgraph "Monitoring Tools"
        METRICS_COLLECTION["Metrics Collection"]
        PERFORMANCE_LOGS["Performance Logs"]
        RESOURCE_TRACKING["Resource Tracking"]
    end
    
    subgraph "Optimization Feedback"
        BOTTLENECK_IDENTIFICATION["Bottleneck<br/>Identification"]
        RECOMMENDATION_ENGINE["Optimization<br/>Recommendations"]
        COST_ANALYSIS["Cost Analysis"]
    end
    
    PARSE_TIME --> METRICS_COLLECTION
    RENDER_TIME --> PERFORMANCE_LOGS
    TOKEN_COUNT --> RESOURCE_TRACKING
    MEMORY_USAGE --> RESOURCE_TRACKING
    
    METRICS_COLLECTION --> BOTTLENECK_IDENTIFICATION
    PERFORMANCE_LOGS --> RECOMMENDATION_ENGINE
    RESOURCE_TRACKING --> COST_ANALYSIS
```

**Sources:** [packages/poml-vscode/tests/preview.test.ts:11-24](), [media/style.css:48-385]()

## Production Deployment Considerations

### Scaling Strategies

When deploying POML in production environments, consider:

- **Caching layers**: Component output caching to reduce processing overhead
- **Resource limits**: Memory and CPU constraints for large document processing  
- **Error boundaries**: Isolation of component failures to prevent cascade failures
- **Monitoring integration**: Performance metrics and error tracking

### Security Considerations

- **Input validation**: Strict validation of POML markup and template inputs
- **Resource limits**: Prevention of resource exhaustion attacks
- **Sandboxing**: Isolation of component execution environments

**Sources:** [packages/poml/util/tokenCounterImage.ts:68-77](), [packages/poml-vscode/tests/extension.test.ts:1-11]()

---

