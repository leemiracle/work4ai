<!-- source: DeepWiki mcp.deepwiki.com · repo openai/openai-dotnet · page 6 Tool Integration · fetched 2026-10-26 -->

# Tool Integration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGELOG.md](CHANGELOG.md)
- [api/OpenAI.net8.0.cs](api/OpenAI.net8.0.cs)
- [api/OpenAI.netstandard2.0.cs](api/OpenAI.netstandard2.0.cs)
- [scripts/Test-ApiCompatibility.ps1](scripts/Test-ApiCompatibility.ps1)
- [src/Generated/Models/OpenAIContext.cs](src/Generated/Models/OpenAIContext.cs)
- [src/Generated/OpenAIModelFactory.cs](src/Generated/OpenAIModelFactory.cs)
- [src/OpenAI.csproj](src/OpenAI.csproj)
- [tests/Responses/ResponsesTests.cs](tests/Responses/ResponsesTests.cs)
- [tests/SessionRecords/ResponsesTests/WebSearchCallStreaming.json](tests/SessionRecords/ResponsesTests/WebSearchCallStreaming.json)
- [tests/SessionRecords/ResponsesTests/WebSearchCallStreamingAsync.json](tests/SessionRecords/ResponsesTests/WebSearchCallStreamingAsync.json)
- [tspCodeModel.json](tspCodeModel.json)

</details>



This document provides an overview of the tool integration capabilities in the OpenAI .NET SDK. Tools extend model functionality by enabling interaction with external systems, code execution environments, search services, and custom functions.

The SDK supports three distinct tool systems:
- **Chat Tools** - Function calling for `ChatClient` (see [#4.2](#4.2))
- **Assistant Tools** - Server-side tools for `AssistantClient` including file search and code execution (see [#4.4](#4.4))
- **Response Tools** - Advanced tool suite for `ResponsesClient` including web search, computer use, and MCP integration (see [#4.3](#4.3))

For detailed implementation patterns of specific tools, see sections [#6.1](#6.1) through [#6.6](#6.6).

Sources: [api/OpenAI.net8.0.cs:1-15000](), [tspCodeModel.json:1-1000](), [tests/Responses/ResponsesTests.cs:1-500]()

## Tool System Architecture

The SDK implements three independent tool systems, each tailored to different API surfaces and use cases:

**Tool System Comparison**

| System | Client | Base Class | Execution Model | Primary Use Cases |
|--------|--------|------------|-----------------|-------------------|
| Chat Tools | `ChatClient` | `ChatTool` | Client-side function execution | Synchronous function calling, structured outputs |
| Assistant Tools | `AssistantClient` | `ToolDefinition` | Server-side execution with runs | RAG workflows, code execution, persistent sessions |
| Response Tools | `ResponsesClient` | `ResponseTool` | Hybrid (client + server) | Web search, computer use, MCP integration, multi-turn workflows |

**Tool System Architecture Diagram**

```mermaid
graph TB
    subgraph ChatSystem["Chat Tool System"]
        CCO["ChatCompletionOptions.Tools<br/>(IList&lt;ChatTool&gt;)"]
        CCO --> CFTD["ChatFunctionToolDefinition"]
        CFTD --> CTC["ChatToolCall"]
        CTC --> ClientExec["Client executes function<br/>Returns result in next message"]
    end
    
    subgraph AssistantSystem["Assistant Tool System"]
        ACO["AssistantCreationOptions.Tools<br/>(IList&lt;ToolDefinition&gt;)"]
        ACO --> CITD["CodeInterpreterToolDefinition"]
        ACO --> FSTD["FileSearchToolDefinition"]
        ACO --> FTD["FunctionToolDefinition"]
        CITD --> ServerExec1["Server executes Python<br/>Returns outputs in RunStep"]
        FSTD --> ServerExec2["Server searches vectors<br/>Returns ranked results"]
        FTD --> ServerExec3["Server requests execution<br/>Client submits ToolOutput"]
    end
    
    subgraph ResponseSystem["Response Tool System"]
        RCO["CreateResponseOptions.Tools<br/>(IList&lt;ResponseTool&gt;)"]
        RCO --> RFT["FunctionTool"]
        RCO --> RFST["FileSearchTool"]
        RCO --> WST["WebSearchTool"]
        RCO --> CT["ComputerTool"]
        RCO --> MCPT["McpTool"]
        RCO --> IGT["ImageGenerationTool"]
        RCO --> RCIT["CodeInterpreterTool"]
        
        RFT --> HybridExec1["Client provides function output"]
        RFST --> HybridExec2["Server searches vectors"]
        WST --> HybridExec3["Server searches internet"]
        CT --> HybridExec4["Client provides screenshots"]
        MCPT --> HybridExec5["Remote MCP server executes"]
        IGT --> HybridExec6["Server generates images"]
        RCIT --> HybridExec7["Server executes in container"]
    end
    
    User["Application Code"] --> ChatSystem
    User --> AssistantSystem
    User --> ResponseSystem
```

Sources: [api/OpenAI.net8.0.cs:2050-2150](), [api/OpenAI.net8.0.cs:214-340](), [api/OpenAI.net8.0.cs:7100-7300]()

## Tool Execution Patterns

Tools follow different execution patterns based on where and how the work is performed:

**Execution Pattern Categories**

```mermaid
graph LR
    subgraph ClientSide["Client-Side Execution"]
        CS1["Model requests tool call"]
        CS2["Client executes function"]
        CS3["Client returns result"]
        CS1 --> CS2 --> CS3
    end
    
    subgraph ServerSide["Server-Side Execution"]
        SS1["Model initiates tool"]
        SS2["Server executes automatically"]
        SS3["Server returns output"]
        SS1 --> SS2 --> SS3
    end
    
    subgraph Interactive["Interactive Execution"]
        IS1["Model requests action"]
        IS2["Client provides input<br/>(e.g., screenshot)"]
        IS3["Model analyzes input"]
        IS4["Repeat or complete"]
        IS1 --> IS2 --> IS3 --> IS4
    end
    
    subgraph Remote["Remote Execution"]
        RS1["Model calls MCP tool"]
        RS2["Request to MCP server"]
        RS3["Server executes"]
        RS4["Result returned"]
        RS1 --> RS2 --> RS3 --> RS4
    end
```

**Pattern Mapping by Tool Type**

| Tool Type | Pattern | Client Responsibility | Server Responsibility |
|-----------|---------|----------------------|----------------------|
| `ChatFunctionToolDefinition` | Client-Side | Execute function, format response | Generate tool call request |
| `FunctionToolDefinition` (Assistant) | Client-Side | Submit `ToolOutput` via `SubmitToolOutputsToRun` | Request function execution in run |
| `FunctionTool` (Response) | Client-Side | Provide output in `FunctionCallOutputResponseItem` | Generate function call |
| `CodeInterpreterToolDefinition` | Server-Side | None (automatic) | Execute Python code, return outputs |
| `CodeInterpreterTool` | Server-Side | None (automatic) | Execute in container, stream logs |
| `FileSearchToolDefinition` | Server-Side | None (automatic) | Search vectors, rank results |
| `FileSearchTool` | Server-Side | None (automatic) | Search vectors, return citations |
| `WebSearchTool` | Server-Side | None (automatic) | Search internet, return results |
| `ComputerTool` | Interactive | Provide screenshots via `ComputerCallOutput` | Generate UI actions |
| `McpTool` | Remote | Configure auth/approval | Route to MCP server |
| `ImageGenerationTool` | Server-Side | None (automatic) | Generate images with DALL-E |

Sources: [src/Custom/Chat/ChatToolCall.cs:1-50](), [src/Custom/Assistants/ToolOutput.cs:1-50](), [src/Custom/Responses/ResponseItem.Serialization.cs:1-100]()

## Chat Tools

Chat tools enable synchronous function calling during chat completions. The model determines when to call functions based on the conversation context.

**Chat Tool Class Hierarchy**

```mermaid
graph TB
    ChatTool["ChatTool<br/>(abstract base)"]
    ChatTool --> CFTD["ChatFunctionToolDefinition"]
    
    CFTD --> Props["Properties:<br/>FunctionName: string<br/>Description: string<br/>Parameters: BinaryData<br/>StrictSchemaEnabled: bool"]
    
    CCO["ChatCompletionOptions"] --> Tools["Tools<br/>(IList&lt;ChatTool&gt;)"]
    CCO --> ToolChoice["ToolChoice<br/>(ChatToolChoice)"]
    
    Tools --> CFTD
    ToolChoice --> Auto["Auto (default)"]
    ToolChoice --> Required["Required"]
    ToolChoice --> None["None"]
    ToolChoice --> Specific["Specific function"]
```

**Usage Example**

[examples/Chat/Example04_FunctionCalling.cs:1-100]() demonstrates creating a function tool:

```csharp
ChatTool tool = ChatTool.CreateFunctionTool(
    functionName: "get_weather",
    functionDescription: "Get weather for a location",
    functionParameters: BinaryData.FromString("""
        {
            "type": "object",
            "properties": {
                "location": { "type": "string" }
            }
        }
        """)
);

ChatCompletionOptions options = new()
{
    Tools = { tool }
};
```

When the model calls a tool, the response includes `ChatToolCall` objects in the assistant message's `ToolCalls` property. The client must execute the function and provide the result in a `ToolChatMessage` in the next request.

Sources: [api/OpenAI.net8.0.cs:2050-2150](), [src/Custom/Chat/ChatFunctionToolDefinition.cs:1-100](), [src/Custom/Chat/ChatToolCall.cs:1-100]()

## Assistant Tools

Assistant tools operate within the context of persistent threads and runs, with server-side execution for most operations.

**Assistant Tool Class Hierarchy**

```mermaid
graph TB
    ToolDef["ToolDefinition<br/>(abstract base)"]
    ToolDef --> CITD["CodeInterpreterToolDefinition"]
    ToolDef --> FSTD["FileSearchToolDefinition"]
    ToolDef --> FTD["FunctionToolDefinition"]
    
    CITD --> CIProps["No configuration<br/>Executes Python automatically"]
    
    FSTD --> FSProps["Properties:<br/>MaxResults: int?<br/>RankingOptions: FileSearchRankingOptions"]
    FSProps --> FSRank["RankingOptions:<br/>Ranker: FileSearchRanker<br/>ScoreThreshold: float"]
    
    FTD --> FProps["Properties:<br/>FunctionName: string<br/>Description: string<br/>Parameters: BinaryData<br/>StrictParameterSchemaEnabled: bool"]
    
    ACO["AssistantCreationOptions<br/>ThreadCreationOptions<br/>RunCreationOptions"] --> Tools["Tools<br/>(IList&lt;ToolDefinition&gt;)"]
    ACO --> ToolRes["ToolResources"]
    
    ToolRes --> CIRes["CodeInterpreter.FileIds"]
    ToolRes --> FSRes["FileSearch.VectorStoreIds"]
```

**Tool Resources Configuration**

Tools that operate on files require resource configuration:

```csharp
AssistantCreationOptions options = new()
{
    Tools = 
    { 
        new CodeInterpreterToolDefinition(),
        new FileSearchToolDefinition 
        { 
            MaxResults = 20,
            RankingOptions = new FileSearchRankingOptions(0.7f)
            {
                Ranker = FileSearchRanker.Auto
            }
        }
    },
    ToolResources = new()
    {
        CodeInterpreter = new() { FileIds = { "file-abc123" } },
        FileSearch = new() { VectorStoreIds = { "vs-xyz789" } }
    }
};
```

For function tools, use `SubmitToolOutputsToRun` when the run status becomes `RequiresAction`:

[src/Custom/Assistants/AssistantClient.cs:300-400]() shows the workflow:
1. Monitor run status via polling or streaming
2. Check `RequiredAction.Type` for `SubmitToolOutputs`
3. Call `SubmitToolOutputsToRun` with `ToolOutput` collection
4. Continue monitoring until run completes

Sources: [api/OpenAI.net8.0.cs:298-340](), [src/Custom/Assistants/ToolDefinition.cs:1-100](), [src/Custom/Assistants/ToolResources.cs:1-100]()

## Response Tools

Response tools provide the most comprehensive tool suite, supporting advanced scenarios like web search, computer use, and Model Context Protocol integration.

**Response Tool Type System**

```mermaid
graph TB
    ResponseTool["ResponseTool<br/>(abstract base)"]
    
    ResponseTool --> FT["FunctionTool"]
    ResponseTool --> FST["FileSearchTool"]
    ResponseTool --> WST["WebSearchTool"]
    ResponseTool --> WSPT["WebSearchPreviewTool"]
    ResponseTool --> CT["ComputerTool"]
    ResponseTool --> MCPT["McpTool"]
    ResponseTool --> IGT["ImageGenerationTool"]
    ResponseTool --> CIT["CodeInterpreterTool"]
    
    FT --> FTProps["functionName<br/>functionDescription<br/>functionParameters<br/>strictSchemaEnabled"]
    
    FST --> FSTProps["maxResults<br/>rankingOptions"]
    
    WST --> WSTProps["searchContextSize<br/>userLocation<br/>filters"]
    WSTProps --> WSTLoc["Location:<br/>city, region, country, timezone"]
    WSTProps --> WSTFilt["Filters:<br/>dateRange, includeDomains, excludeDomains"]
    
    WSPT --> WSPTNote["Preview features<br/>same as WebSearchTool"]
    
    CT --> CTProps["environment<br/>displayWidth<br/>displayHeight"]
    CTProps --> CTEnv["Environment:<br/>Windows, MacOS, Linux"]
    
    MCPT --> MCPProps["serverLabel<br/>serverUri<br/>allowedTools<br/>toolCallApprovalPolicy<br/>authorizationToken<br/>connectorId<br/>serviceDescription"]
    
    IGT --> IGTProps["size<br/>quality<br/>style<br/>background<br/>inputImages"]
    
    CIT --> CITProps["container"]
    CITProps --> CIContainer["Container:<br/>fileIds, configuration"]
```

**Factory Methods for Response Tools**

Response tools use factory methods on `ResponseTool` for instantiation:

| Factory Method | Purpose | Key Parameters |
|----------------|---------|----------------|
| `CreateFunctionTool` | External function calling | `functionName`, `functionDescription`, `functionParameters` |
| `CreateFileSearchTool` | Vector store search | `maxResults`, `rankingOptions` |
| `CreateWebSearchTool` | Internet search (stable) | `searchContextSize`, `userLocation`, `filters` |
| `CreateWebSearchPreviewTool` | Internet search (preview) | Same as `WebSearchTool` |
| `CreateComputerTool` | UI automation | `environment`, `displayWidth`, `displayHeight` |
| `CreateMcpTool` | MCP integration | `serverLabel`, `serverUri`, `allowedTools` |
| `CreateImageGenerationTool` | Image generation | `size`, `quality`, `style` |
| `CreateCodeInterpreterTool` | Python execution | `container` |

**Response Tool Integration Flow**

```mermaid
sequenceDiagram
    participant App as "Application"
    participant RC as "ResponsesClient"
    participant Model as "Model"
    participant Tool as "Tool System"
    
    App->>RC: CreateResponseAsync(options)
    Note over App,RC: options.Tools contains tool definitions
    
    RC->>Model: Send request with tools
    Model->>Tool: Determine tool to call
    
    alt Server-Side Tool (WebSearch, FileSearch, ImageGen, CodeInterpreter)
        Tool->>Tool: Execute automatically
        Tool->>Model: Return results
        Model->>RC: Response with tool results
        RC->>App: ResponseResult
    else Client-Side Tool (Function, Computer)
        Tool->>Model: Generate tool call request
        Model->>RC: Response with tool call item
        RC->>App: ResponseResult with item
        App->>App: Execute function or provide screenshot
        App->>RC: CreateResponseAsync with output item
        RC->>Model: Continue with tool output
        Model->>RC: Final response
        RC->>App: ResponseResult
    else MCP Tool
        Tool->>Tool: Route to MCP server
        Tool->>Tool: Apply approval policy if configured
        Tool->>Model: Return MCP result
        Model->>RC: Response with results
        RC->>App: ResponseResult
    end
```

**Web Search Tool Example**

[tests/Responses/ResponsesTests.cs:140-164]() demonstrates web search:

```csharp
ResponseResult response = await client.CreateResponseAsync(
    new CreateResponseOptions([
        ResponseItem.CreateUserMessageItem("What's the weather like in Seattle?")
    ])
    {
        Tools = { ResponseTool.CreateWebSearchTool() },
        ToolChoice = ResponseToolChoice.CreateWebSearchChoice()
    });

// Response contains WebSearchCallResponseItem and MessageResponseItem
WebSearchCallResponseItem searchItem = response.OutputItems[0] as WebSearchCallResponseItem;
MessageResponseItem messageItem = response.OutputItems[1] as MessageResponseItem;

// Message content includes annotations with URL citations
foreach (var part in messageItem.Content)
{
    Console.WriteLine(part.Text);
    foreach (var annotation in part.OutputTextAnnotations)
    {
        // Annotations contain source URLs
    }
}
```

**Computer Tool Example**

[tests/Responses/ResponsesTests.cs:76-137]() demonstrates interactive computer use:

```csharp
ResponseTool computerTool = ResponseTool.CreateComputerTool(
    ComputerToolEnvironment.Windows, 1024, 768);

CreateResponseOptions options = new([
    ResponseItem.CreateDeveloperMessageItem("Call tools for computer tasks."),
    ResponseItem.CreateUserMessageItem("Click on the Save button.")
])
{
    Tools = { computerTool }
};

ResponseResult response = await client.CreateResponseAsync(options);

// Handle screenshot requests
while (true)
{
    ComputerCallResponseItem computerCall = 
        response.OutputItems.OfType<ComputerCallResponseItem>().LastOrDefault();
    
    if (computerCall?.Action.Kind == ComputerCallActionKind.Screenshot)
    {
        BinaryData screenshot = GetScreenshot(); // Client captures screen
        
        ResponseItem screenshotReply = ResponseItem.CreateComputerCallOutputItem(
            computerCall.CallId,
            ComputerCallOutput.CreateScreenshotOutput(screenshot, "image/png"));
        
        options.PreviousResponseId = response.Id;
        options.InputItems.Clear();
        options.InputItems.Add(screenshotReply);
        
        response = await client.CreateResponseAsync(options);
    }
    else if (computerCall?.Action.Kind == ComputerCallActionKind.Click)
    {
        break; // Model has determined the action
    }
}
```

Sources: [api/OpenAI.net8.0.cs:7100-7300](), [src/Custom/Responses/ResponseTool.cs:1-200](), [tests/Responses/ResponsesTests.cs:76-260]()

## Tool Selection and Control

Each tool system provides mechanisms to control which tools the model uses.

**Tool Choice Mechanisms**

```mermaid
graph TB
    subgraph ChatChoice["Chat: ChatToolChoice"]
        CC1["ChatToolChoice.Auto<br/>(model decides)"]
        CC2["ChatToolChoice.Required<br/>(must use a tool)"]
        CC3["ChatToolChoice.None<br/>(no tools)"]
        CC4["ChatToolChoice.CreateFunctionChoice<br/>(specific function)"]
    end
    
    subgraph AssistantChoice["Assistant: (via ToolResources)"]
        AC1["Tools enabled by ToolResources"]
        AC2["Functions always optional"]
        AC3["No explicit choice mechanism"]
    end
    
    subgraph ResponseChoice["Response: ResponseToolChoice"]
        RC1["ResponseToolChoice.Auto<br/>(model decides)"]
        RC2["ResponseToolChoice.Required<br/>(must use a tool)"]
        RC3["ResponseToolChoice.None<br/>(no tools)"]
        RC4["CreateFunctionChoice<br/>(specific function)"]
        RC5["CreateWebSearchChoice<br/>(web search)"]
        RC6["CreateFileSearchChoice<br/>(file search)"]
        RC7["CreateComputerChoice<br/>(computer use)"]
    end
```

**Tool Choice Configuration Examples**

For `ChatClient`:
```csharp
ChatCompletionOptions options = new()
{
    Tools = { functionTool },
    ToolChoice = ChatToolChoice.CreateFunctionChoice("get_weather")
};
```

For `AssistantClient`:
```csharp
// Tool availability determined by ToolResources
// Functions are always optional; model decides when to call
RunCreationOptions runOptions = new()
{
    ToolResources = new()
    {
        FileSearch = new() { VectorStoreIds = { vectorStoreId } }
    }
};
```

For `ResponsesClient`:
```csharp
CreateResponseOptions options = new(inputItems)
{
    Tools = 
    { 
        ResponseTool.CreateWebSearchTool(),
        ResponseTool.CreateFunctionTool("calculator", "Do math", parameters)
    },
    ToolChoice = ResponseToolChoice.CreateWebSearchChoice() // Force web search
};
```

**Parallel Tool Execution**

Chat and Response APIs support parallel tool calls:

| Property | Client | Default | Description |
|----------|--------|---------|-------------|
| `AllowParallelToolCalls` | `ChatClient` | `true` | Chat can call multiple functions in one response |
| `ParallelToolCallsEnabled` | `ResponsesClient` | `true` | Response can execute multiple tools concurrently |

Example:
```csharp
ChatCompletionOptions options = new()
{
    Tools = { weatherTool, timeTool, calculatorTool },
    AllowParallelToolCalls = false // Force sequential execution
};
```

Parallel execution reduces round trips but requires handling multiple tool calls in a single response.

Sources: [api/OpenAI.net8.0.cs:2200-2250](), [api/OpenAI.net8.0.cs:7350-7400](), [src/Custom/Chat/ChatToolChoice.cs:1-100](), [src/Custom/Responses/ResponseToolChoice.cs:1-100]()

## Tool Response Items

Response tools produce various output item types depending on the tool used:

**Response Item Type Mapping**

```mermaid
graph TB
    ResponseItem["ResponseItem<br/>(abstract base)"]
    
    ResponseItem --> MRI["MessageResponseItem<br/>(assistant text output)"]
    ResponseItem --> FCRI["FunctionCallResponseItem<br/>(function call request)"]
    ResponseItem --> FCORI["FunctionCallOutputResponseItem<br/>(client function result)"]
    ResponseItem --> FSCRI["FileSearchCallResponseItem<br/>(vector search results)"]
    ResponseItem --> WSCRI["WebSearchCallResponseItem<br/>(internet search results)"]
    ResponseItem --> CCRI["ComputerCallResponseItem<br/>(UI action request)"]
    ResponseItem --> CCORI["ComputerCallOutputResponseItem<br/>(screenshot/action result)"]
    ResponseItem --> IGCRI["ImageGenerationCallResponseItem<br/>(generated image)"]
    ResponseItem --> CICRI["CodeInterpreterCallResponseItem<br/>(code execution)"]
    
    FCRI --> FCProps["CallId<br/>FunctionName<br/>FunctionArguments<br/>Status"]
    FCORI --> FCOProps["CallId<br/>Output"]
    FSCRI --> FSCProps["Status<br/>Results[]<br/>Each result: content, score, fileId"]
    WSCRI --> WSCProps["Status<br/>Action.Query"]
    CCRI --> CCProps["CallId<br/>Action (Click, Type, Screenshot, etc)<br/>Status"]
    CCORI --> CCOProps["CallId<br/>Output (Screenshot or Error)"]
    IGCRI --> IGCProps["Status<br/>Images[]"]
    CICRI --> CICProps["Status<br/>Outputs[]<br/>(Logs, Images)"]
```

**Tool Status Lifecycle**

Many tool response items include a `Status` property tracking execution:

| Status | Meaning | Applicable Tools |
|--------|---------|------------------|
| `InProgress` | Tool call initiated | All tools |
| `Completed` | Tool execution finished successfully | All tools |
| `Failed` | Tool execution encountered an error | All tools |
| `RequiresAction` | Client must provide input | `FunctionCallResponseItem`, `ComputerCallResponseItem` |

**Handling Tool Outputs in Multi-Turn**

For client-side tools, provide outputs using factory methods on `ResponseItem`:

```csharp
// Function tool output
ResponseItem functionOutput = ResponseItem.CreateFunctionCallOutputItem(
    callId: functionCall.CallId,
    output: JsonSerializer.Serialize(result));

// Computer tool output (screenshot)
ResponseItem screenshotOutput = ResponseItem.CreateComputerCallOutputItem(
    callId: computerCall.CallId,
    output: ComputerCallOutput.CreateScreenshotOutput(screenshotBytes, "image/png"));

// Continue conversation
CreateResponseOptions nextOptions = new([functionOutput])
{
    PreviousResponseId = previousResponse.Id
};
```

Sources: [api/OpenAI.net8.0.cs:7500-7800](), [src/Custom/Responses/ResponseItem.cs:1-200](), [tests/Responses/ResponsesTests.cs:76-137]()

---

