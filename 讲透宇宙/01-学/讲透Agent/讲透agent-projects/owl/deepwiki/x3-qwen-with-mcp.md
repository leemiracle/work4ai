<!-- source: DeepWiki mcp.deepwiki.com · repo camel-ai/owl · extra page Qwen with MCP · fetched 2026-10-29 -->

# Qwen with MCP

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [community_usecase/qwen3_mcp/mcp_sse_config.json](community_usecase/qwen3_mcp/mcp_sse_config.json)
- [community_usecase/qwen3_mcp/run_mcp_qwen3.py](community_usecase/qwen3_mcp/run_mcp_qwen3.py)

</details>



This page documents the Qwen-MCP integration example located in `community_usecase/qwen3_mcp/`, which demonstrates using Alibaba's Qwen models with the Model Context Protocol (MCP) toolkit for browser automation and web deployment tasks. This example showcases structured conversation logging to markdown files and formatted terminal output.

For general MCP toolkit architecture and configuration, see [MCP Toolkit](#5.2). For other MCP integration examples including Puppeteer and Notion, see [Puppeteer Browser Automation](#8.2.2) and [Notion Workspace Management](#8.2.3). For Qwen model platform configuration, see [Chinese LLM Platforms](#6.4).

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:1-331]()

## Purpose and Capabilities

The Qwen-MCP example demonstrates:

- **Qwen Model Integration**: Using `ModelPlatformType.QWEN` with `ModelType.QWEN_PLUS_LATEST` for both user and assistant agents
- **MCP Server Connection**: Connecting to Playwright and EdgeOne Pages MCP servers for browser automation and deployment
- **Structured Logging**: Automatic export of conversations to timestamped markdown files
- **Terminal Formatting**: Color-coded output using `colorama` for better readability
- **Async Execution**: Full async/await pattern for MCP toolkit operations

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:40-84](), [community_usecase/qwen3_mcp/run_mcp_qwen3.py:264-330]()

## System Architecture

```mermaid
graph TB
    subgraph "User Input"
        CLI["Command Line Args<br/>sys.argv[1]"]
        DefaultTask["Default Task:<br/>GitHub Analysis +<br/>HTML Generation"]
    end
    
    subgraph "Model Configuration"
        ModelFactory["ModelFactory.create()"]
        QwenUser["User Agent Model<br/>QWEN_PLUS_LATEST<br/>temperature=0"]
        QwenAssist["Assistant Agent Model<br/>QWEN_PLUS_LATEST<br/>temperature=0"]
    end
    
    subgraph "MCP Integration"
        MCPConfig["mcp_sse_config.json"]
        MCPToolkit["MCPToolkit<br/>strict=True"]
        Playwright["Playwright MCP<br/>@playwright/mcp"]
        EdgeOne["EdgeOne Pages MCP<br/>edgeone-pages-mcp"]
    end
    
    subgraph "Society Construction"
        ConstructSociety["construct_society()"]
        OwlRP["OwlRolePlaying<br/>user_role_name='user'<br/>assistant_role_name='assistant'"]
        UserAgent["User Agent<br/>with QWEN model"]
        AssistAgent["Assistant Agent<br/>with QWEN model + tools"]
    end
    
    subgraph "Execution & Logging"
        RunSociety["run_society_with_formatted_output()"]
        TerminalOutput["Terminal Output<br/>colorama formatting"]
        MDLogging["Markdown Logging<br/>conversation_logs/"]
        CreateMD["create_md_file()"]
        WriteMD["write_to_md()"]
    end
    
    CLI --> ConstructSociety
    DefaultTask --> ConstructSociety
    
    ModelFactory --> QwenUser
    ModelFactory --> QwenAssist
    
    MCPConfig --> MCPToolkit
    MCPToolkit --> Playwright
    MCPToolkit --> EdgeOne
    
    QwenUser --> ConstructSociety
    QwenAssist --> ConstructSociety
    MCPToolkit --> ConstructSociety
    
    ConstructSociety --> OwlRP
    OwlRP --> UserAgent
    OwlRP --> AssistAgent
    
    OwlRP --> RunSociety
    RunSociety --> TerminalOutput
    RunSociety --> CreateMD
    CreateMD --> MDLogging
    RunSociety --> WriteMD
    WriteMD --> MDLogging
```

**Diagram: Qwen-MCP System Component Flow**

This diagram shows how the Qwen-MCP example integrates model configuration, MCP toolkit initialization, society construction, and dual-output logging (terminal + markdown).

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:40-84](), [community_usecase/qwen3_mcp/run_mcp_qwen3.py:264-330]()

## MCP Server Configuration

The MCP servers are defined in `mcp_sse_config.json` with a standard structure:

| Server Name | Command | Arguments | Purpose |
|------------|---------|-----------|---------|
| `edgeone-pages-mcp-server` | `npx` | `["edgeone-pages-mcp"]` | Web deployment and hosting services |
| `playwright` | `npx` | `["@playwright/mcp@latest"]` | Browser automation for web scraping and interaction |

The configuration follows the MCP SSE (Server-Sent Events) protocol structure. Each server is spawned as a subprocess using `npx`, which executes the corresponding Node.js packages.

**Sources:** [community_usecase/qwen3_mcp/mcp_sse_config.json:1-14]()

### Configuration Loading and Connection

```mermaid
sequenceDiagram
    participant Main as main()
    participant Config as mcp_sse_config.json
    participant Toolkit as MCPToolkit
    participant Servers as MCP Servers<br/>(npx processes)
    participant Society as OwlRolePlaying
    
    Main->>Config: Load config_path
    Main->>Toolkit: MCPToolkit(config_path, strict=True)
    Main->>Toolkit: await connect()
    
    Toolkit->>Servers: Spawn edgeone-pages-mcp
    Toolkit->>Servers: Spawn playwright MCP
    Servers-->>Toolkit: Server ready
    
    Main->>Toolkit: get_tools()
    Toolkit-->>Main: List[FunctionTool]
    
    Main->>Society: construct_society(task, tools)
    Society-->>Main: OwlRolePlaying instance
    
    Main->>Society: run_society_with_formatted_output()
    
    Note over Main,Servers: Conversation loop with tool calls
    
    Main->>Toolkit: await disconnect()
    Toolkit->>Servers: Terminate processes
```

**Diagram: MCP Toolkit Lifecycle in Qwen Example**

The `MCPToolkit` is initialized with `strict=True`, which enforces type checking on tool parameters. Connection is asynchronous and must complete before tools can be retrieved.

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:264-330]()

## Society Construction Function

The `construct_society` function creates an `OwlRolePlaying` instance with Qwen models and MCP tools:

```mermaid
graph LR
    subgraph "Function: construct_society"
        Input1["question: str"]
        Input2["tools: List[FunctionTool]"]
        
        ModelDict["models dict"]
        UserModelCfg["user: QWEN_PLUS_LATEST<br/>temperature=0"]
        AssistModelCfg["assistant: QWEN_PLUS_LATEST<br/>temperature=0"]
        
        UserKwargs["user_agent_kwargs<br/>{'model': ...}"]
        AssistKwargs["assistant_agent_kwargs<br/>{'model': ..., 'tools': ...}"]
        
        TaskKwargs["task_kwargs<br/>task_prompt, with_task_specify=False"]
        
        Society["OwlRolePlaying<br/>user_role_name='user'<br/>assistant_role_name='assistant'"]
        
        Input1 --> TaskKwargs
        Input2 --> AssistKwargs
        
        UserModelCfg --> ModelDict
        AssistModelCfg --> ModelDict
        
        ModelDict --> UserKwargs
        ModelDict --> AssistKwargs
        
        UserKwargs --> Society
        AssistKwargs --> Society
        TaskKwargs --> Society
    end
```

**Diagram: construct_society Function Flow**

Key configuration details:

- **User Agent**: Uses Qwen Plus with temperature 0 (deterministic), no tools
- **Assistant Agent**: Uses Qwen Plus with temperature 0 (deterministic), receives all MCP tools
- **Task Configuration**: Sets `with_task_specify=False` to use the raw task prompt without modification

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:40-84]()

### Model Configuration Details

Both agents use identical model configurations:

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `model_platform` | `ModelPlatformType.QWEN` | Specifies Alibaba Qwen platform |
| `model_type` | `ModelType.QWEN_PLUS_LATEST` | Uses latest Qwen Plus model version |
| `temperature` | `0` | Deterministic output for reproducibility |

The temperature setting of 0 is important for consistent behavior across multiple runs, which is valuable for debugging and validation.

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:53-64]()

## Markdown Logging System

The example implements a sophisticated logging system that exports conversations to markdown files with timestamps and structured formatting.

### File Creation

The `create_md_file` function generates timestamped markdown files:

| Component | Implementation | Example |
|-----------|---------------|---------|
| **Timestamp Format** | `%Y%m%d_%H%M%S` | `20240315_143022` |
| **Task Shortening** | First 30 chars, replace spaces/slashes | `Visit_the_Qwen3_GitHub_rep` |
| **Directory** | `conversation_logs/` | Auto-created if missing |
| **Filename Pattern** | `conversation_{timestamp}_{task_short}.md` | `conversation_20240315_143022_Visit_the_Qwen3.md` |

The file is initialized with:
- H1 header with full task description
- Generation timestamp
- Task details section
- Empty conversation section

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:87-113]()

### Content Writing

The `write_to_md` function handles different content types:

```mermaid
graph TB
    WriteToMD["write_to_md(filename, content)"]
    
    CheckSystemInfo{"'system_info'<br/>in content?"}
    CheckAssistant{"'assistant'<br/>in content?"}
    CheckUser{"'user'<br/>in content?"}
    CheckSummary{"'summary'<br/>in content?"}
    CheckToolCalls{"'tool_calls'<br/>in content?"}
    
    WriteSystemInfo["Write System Information<br/>with key-value pairs"]
    WriteToolCalls["Write Tool Calls<br/>in code blocks"]
    WriteAssistant["Write Assistant Response<br/>with 🤖 emoji"]
    WriteUser["Write User Response<br/>with 👤 emoji"]
    WriteSummary["Write Summary Section"]
    
    WriteToMD --> CheckSystemInfo
    CheckSystemInfo -->|Yes| WriteSystemInfo
    CheckSystemInfo -->|No| CheckAssistant
    
    WriteSystemInfo --> CheckAssistant
    CheckAssistant -->|Yes| CheckToolCalls
    CheckToolCalls -->|Yes| WriteToolCalls
    CheckToolCalls -->|No| WriteAssistant
    WriteToolCalls --> WriteAssistant
    CheckAssistant -->|No| CheckUser
    
    WriteAssistant --> CheckUser
    CheckUser -->|Yes| WriteUser
    CheckUser -->|No| CheckSummary
    
    WriteUser --> CheckSummary
    CheckSummary -->|Yes| WriteSummary
    CheckSummary -->|No| Done["Done"]
    WriteSummary --> Done
```

**Diagram: Markdown Content Writing Logic**

Content types handled:

1. **System Information**: Configuration and prompts (written once at start)
2. **Tool Calls**: Function calls with parameters in code blocks
3. **Assistant Messages**: AI responses with tool call context
4. **User Messages**: User agent guidance and feedback
5. **Summary**: Task completion or termination information

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:116-144]()

## Execution Flow with Formatted Output

The `run_society_with_formatted_output` function orchestrates the conversation loop with dual output streams.

```mermaid
sequenceDiagram
    participant Function as run_society_with_formatted_output
    participant Society as OwlRolePlaying
    participant Terminal as Terminal<br/>(colorama)
    participant MD as Markdown File
    participant Agents as User/Assistant Agents
    
    Function->>Terminal: Print system messages (GREEN, BLUE)
    Function->>Terminal: Print task prompts (YELLOW, CYAN, RED)
    Function->>MD: Write system_info dict
    
    Function->>Society: init_chat()
    Society-->>Function: initial input_msg
    
    loop n < round_limit (default 15)
        Function->>Society: await astep(input_msg)
        Society->>Agents: Execute conversation step
        Agents-->>Society: assistant_response, user_response
        Society-->>Function: responses with token usage
        
        Function->>Function: Accumulate token counts
        
        alt assistant_response.terminated
            Function->>Terminal: Print termination (GREEN)
            Function->>MD: Write termination summary
            Function->>Function: break
        end
        
        alt user_response.terminated
            Function->>Terminal: Print termination (GREEN)
            Function->>MD: Write termination summary
            Function->>Function: break
        end
        
        alt tool_calls in assistant_response
            Function->>Terminal: Print tool calls (GREEN)
            Function->>MD: Write tool calls in code blocks
        end
        
        Function->>Terminal: Print assistant content (GREEN)
        Function->>Terminal: Print user content (BLUE)
        
        Function->>MD: Write assistant and user content
        Function->>Function: Append to chat_history
        
        alt "TASK_DONE" in user_response
            Function->>Terminal: Print success (YELLOW)
            Function->>MD: Write success summary
            Function->>Function: break
        end
        
        Function->>Function: input_msg = assistant_response.msg
    end
    
    Function->>MD: Write final token counts
    Function-->>Function: Return (answer, chat_history, token_info)
```

**Diagram: Conversation Loop with Dual Output**

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:146-261]()

### Terminal Color Scheme

The colorama library provides colored output for different message types:

| Color | Message Type | Usage |
|-------|-------------|-------|
| `Fore.GREEN` | Assistant messages, tool calls, success | AI responses and system success |
| `Fore.BLUE` | User messages, system info | User agent responses |
| `Fore.YELLOW` | Task prompts, warnings, completion | Important information |
| `Fore.CYAN` | Specified prompts, metadata | Secondary information |
| `Fore.RED` | Final task prompt, errors | Critical information |

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:157-162](), [community_usecase/qwen3_mcp/run_mcp_qwen3.py:222-232]()

### Token Tracking

Token usage is accumulated across all conversation rounds:

```python
# Tracked metrics
overall_completion_token_count += (
    assistant_response.info["usage"].get("completion_tokens", 0) +
    user_response.info["usage"].get("completion_tokens", 0)
)
overall_prompt_token_count += (
    assistant_response.info["usage"].get("prompt_tokens", 0) +
    user_response.info["usage"].get("prompt_tokens", 0)
)
```

The final token information includes:
- `completion_token_count`: Total tokens generated
- `prompt_token_count`: Total tokens in prompts

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:185-195]()

## Main Execution and Error Handling

The `main` function demonstrates robust async execution with proper cleanup:

```mermaid
graph TB
    Main["main() async"]
    LoadConfig["Load mcp_sse_config.json"]
    SetTask["Set task from sys.argv<br/>or use default"]
    CreateToolkit["MCPToolkit(config_path, strict=True)"]
    
    CreateMDFile["create_md_file(task)"]
    Connect["await mcp_toolkit.connect()"]
    GetTools["tools = mcp_toolkit.get_tools()"]
    BuildSociety["await construct_society(task, tools)"]
    RunSociety["await run_society_with_formatted_output()"]
    
    PrintResults["Print final answer and tokens"]
    
    Disconnect["await mcp_toolkit.disconnect()"]
    Sleep["await asyncio.sleep(0.5)"]
    
    Main --> LoadConfig
    LoadConfig --> SetTask
    SetTask --> CreateToolkit
    CreateToolkit --> CreateMDFile
    
    CreateMDFile --> TryBlock
    
    subgraph TryBlock ["Try Block"]
        Connect --> GetTools
        GetTools --> BuildSociety
        BuildSociety --> RunSociety
        RunSociety --> PrintResults
    end
    
    TryBlock --> ExceptBlock
    
    subgraph ExceptBlock ["Exception Handling"]
        KeyboardInt["KeyboardInterrupt:<br/>Exit gracefully"]
        GeneralExc["Exception:<br/>Print error"]
    end
    
    ExceptBlock --> FinallyBlock
    
    subgraph FinallyBlock ["Finally Block"]
        Disconnect
        DisconnectTimeout["Timeout after 3s"]
        DisconnectCancel["Handle cancellation"]
        Sleep
    end
    
    FinallyBlock --> End["Program Exit"]
```

**Diagram: Main Function Error Handling Flow**

### Exception Handling Strategy

The example implements three-tier exception handling:

1. **KeyboardInterrupt**: Graceful shutdown on Ctrl+C
2. **General Exceptions**: Error logging with traceback
3. **Finally Block**: Guaranteed cleanup with timeout protection

The disconnect operation includes:
- `asyncio.wait_for` with 3-second timeout
- `asyncio.shield` to prevent cancellation during cleanup
- Fallback handling for `TimeoutError` and `CancelledError`
- 0.5-second sleep to allow async tasks to complete

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:304-327]()

## Default Task Example

The default task demonstrates complex multi-step automation:

```
Visit the Qwen3 GitHub repository, summarize the introduction of the repository.
Write a comprehensive HTML documentation site with the following features:
- A clear introduction to Qwen3
- Well-organized sections of the technical documentation
- Practical code examples
- A visually appealing purple technology theme (e.g. modern, clean, purple-accented design)
Finally, deploy the HTML site and open it in the browser.
```

This task exercises:
- **Playwright MCP**: GitHub repository access and browser control
- **EdgeOne Pages MCP**: HTML deployment and hosting
- **Multi-step reasoning**: Repository analysis → HTML generation → deployment → browser opening
- **Creative output**: Custom styling and design requirements

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:269-277]()

## Usage Examples

### Running with Default Task

```bash
python community_usecase/qwen3_mcp/run_mcp_qwen3.py
```

This executes the GitHub documentation generation task.

### Running with Custom Task

```bash
python community_usecase/qwen3_mcp/run_mcp_qwen3.py "Search for recent AI papers on arXiv and create a summary webpage"
```

The command-line argument overrides the default task.

### Environment Requirements

Required environment variables (loaded from `.env`):

| Variable | Purpose | Required For |
|----------|---------|--------------|
| `QWEN_API_KEY` | Qwen API authentication | Model calls |

Required system dependencies:

| Dependency | Purpose | Installation |
|-----------|---------|--------------|
| Node.js + npm | npx command for MCP servers | System package manager |
| Playwright browsers | Browser automation | `npx playwright install` |

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:35-37](), [community_usecase/qwen3_mcp/run_mcp_qwen3.py:280-281]()

## Output Structure

### Terminal Output Format

The terminal displays color-coded information in this order:

1. **System Messages** (Green/Blue): Agent system prompts
2. **Task Prompts** (Yellow/Cyan/Red): Original, specified, and final task descriptions
3. **Markdown Path** (Cyan): Location of conversation log file
4. **Connection Status** (Green): MCP server connection confirmation
5. **Conversation Loop**:
   - Assistant messages (Green) with tool calls
   - User messages (Blue) with guidance
6. **Final Results** (Green): Answer and token counts
7. **Log Location** (Cyan): Confirmation of saved conversation

### Markdown Output Structure

Generated markdown files follow this structure:

```markdown
# Agent Conversation: {task}

*Generated on: {timestamp}*

## Task Details

**Task:** {full task description}

## Conversation

### System Information

**AI Assistant System Message:** {system_msg}
**AI User System Message:** {system_msg}
...

### 🤖 Assistant

**Tool Calls:**

```
{tool_call_record}
```

{assistant_content}

### 👤 User

{user_content}

...

## Summary

{completion_message}

**completion_token_count:** {count}
**prompt_token_count:** {count}
```

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:87-144]()

## Key Differences from Other MCP Examples

This Qwen-MCP example differs from other MCP integration examples in several ways:

| Feature | Qwen Example | Puppeteer Example | Notion Example |
|---------|-------------|-------------------|----------------|
| **Model Platform** | Qwen (Chinese LLM) | Various | Various |
| **Conversation Logging** | Markdown files with timestamps | Varies | Varies |
| **Terminal Formatting** | colorama with color coding | Standard output | Standard output |
| **MCP Servers** | EdgeOne Pages + Playwright | Puppeteer | Notion API |
| **Use Case Focus** | Web dev + deployment | Browser automation | Workspace management |
| **Model Temperature** | 0 (deterministic) | Varies | Varies |

The emphasis on structured logging and formatted output makes this example particularly useful for debugging and documentation purposes.

**Sources:** [community_usecase/qwen3_mcp/run_mcp_qwen3.py:1-331]()

---

