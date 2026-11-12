<!-- source: DeepWiki mcp.deepwiki.com · repo camel-ai/owl · page 5 Toolkits · fetched 2026-10-29 -->

# Toolkits

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitignore](.gitignore)
- [README.md](README.md)
- [README_ja.md](README_ja.md)
- [README_zh.md](README_zh.md)
- [examples/run_gemini.py](examples/run_gemini.py)
- [examples/run_groq.py](examples/run_groq.py)
- [examples/run_mistral.py](examples/run_mistral.py)
- [examples/run_novita_ai.py](examples/run_novita_ai.py)
- [examples/run_openai_compatible_model.py](examples/run_openai_compatible_model.py)
- [examples/run_together_ai.py](examples/run_together_ai.py)
- [owl/assets/owl-favicon.ico](owl/assets/owl-favicon.ico)

</details>



The toolkit system extends agent capabilities by providing standardized interfaces to external systems, code execution environments, web browsers, document processors, and specialized services. Each toolkit exposes functionality through `FunctionTool` objects that agents can invoke during task execution.

The toolkit ecosystem comprises both "lightweight" toolkits with minimal dependencies (e.g., `ExcelToolkit`, `FileWriteToolkit`) and "heavyweight" toolkits requiring external services or model capabilities (e.g., `BrowserToolkit`, `DocumentProcessingToolkit`). The `MCPToolkit` serves as a meta-toolkit, exposing external MCP servers as tool collections.

This page provides an overview of the toolkit architecture and details on specific toolkit categories. For toolkit integration with agents, see page 2.2.

Sources: [README.md:101-195](), [README.md:488-584]()

## FunctionTool Abstraction

All toolkits expose their capabilities through the `FunctionTool` interface from the CAMEL framework. A `FunctionTool` wraps a Python function with metadata (name, description, parameters) that enables LLM agents to discover, select, and invoke tools based on natural language task requirements.

```mermaid
graph TD
    A["Toolkit Class"] --> B["get_tools()"]
    B --> C["List[FunctionTool]"]
    
    C --> D["FunctionTool 1"]
    C --> E["FunctionTool 2"]
    C --> F["FunctionTool N"]
    
    D --> G["func: Callable"]
    D --> H["name: str"]
    D --> I["description: str"]
    D --> J["parameters: dict"]
    
    K["Assistant Agent"] --> L["tools parameter"]
    C --> L
    
    K --> M["LLM Model"]
    M --> N["Tool Selection"]
    N --> O["Tool Invocation"]
    O --> G
```

**FunctionTool Interface Structure**

The `get_tools()` method is the standard interface for extracting tool collections. Some toolkits (e.g., `SearchToolkit`) also expose individual methods as standalone tools.

Sources: [examples/run.py:91-106](), [examples/run_groq.py:102-117]()

## Toolkit Configuration Patterns

Toolkits follow three primary configuration patterns based on their requirements:

### Pattern 1: Model-Dependent Toolkits

These toolkits require LLM model instances for processing:

| Toolkit | Required Models | Purpose |
|---------|----------------|---------|
| `BrowserToolkit` | `web_agent_model`, `planning_agent_model` | Web page interpretation, navigation planning |
| `ImageAnalysisToolkit` | `model` (vision-capable) | Image content analysis |
| `VideoAnalysisToolkit` | `model` (vision-capable) | Video frame analysis |
| `DocumentProcessingToolkit` | `model` | Document content extraction, conversion |

```mermaid
graph LR
    A["ModelFactory.create()"] --> B["Vision Model"]
    A --> C["Planning Model"]
    
    B --> D["BrowserToolkit(web_agent_model=B, planning_agent_model=C)"]
    C --> D
    
    D --> E["get_tools()"]
    E --> F["List[FunctionTool]"]
```

**Model-Dependent Toolkit Configuration**

Sources: [examples/run.py:92-96](), [examples/run_groq.py:104-107](), [examples/run_gemini.py:90-94]()

### Pattern 2: Service-Dependent Toolkits

These toolkits require external services or API keys:

| Toolkit | Dependencies | Configuration |
|---------|--------------|---------------|
| `AudioAnalysisToolkit` | OpenAI API | Requires `OPENAI_API_KEY` environment variable |
| `MCPToolkit` | MCP servers, Node.js | Requires `mcp_servers_config.json` configuration |
| `GitHubToolkit` | GitHub API | Requires `GITHUB_API_KEY` |
| `NotionToolkit` | Notion API | Requires `NOTION_API_KEY` |

Sources: [examples/run.py:98](), [examples/run_groq.py:109](), [examples/run_mistral.py:144-148]()

### Pattern 3: Standalone Toolkits

These toolkits have minimal external dependencies:

- `ExcelToolkit`: Operates on local files using `openpyxl`, `pandas`
- `FileWriteToolkit`: Built-in file operations
- `TerminalToolkit`: System command execution
- `MathToolkit`: Pure Python mathematical operations

```mermaid
graph TD
    A["ExcelToolkit()"] --> B["get_tools()"]
    C["FileWriteToolkit(output_dir='./tmp')"] --> D["get_tools()"]
    E["TerminalToolkit()"] --> F["get_tools()"]
    
    B --> G["read_excel"]
    B --> H["write_excel"]
    
    D --> I["write_file"]
    
    F --> J["execute_command"]
    
    G --> K["tools list"]
    H --> K
    I --> K
    J --> K
```

**Standalone Toolkit Pattern**

Sources: [examples/run.py:99-106](), [examples/run_groq.py:115-117]()

## Tool Integration in construct_society()

Toolkits are integrated into the agent society through the `assistant_agent_kwargs` configuration within `construct_society()`:

```mermaid
graph TD
    A["construct_society(question)"] --> B["Instantiate Toolkits"]
    
    B --> C["BrowserToolkit(...)"]
    B --> D["SearchToolkit()"]
    B --> E["CodeExecutionToolkit(...)"]
    B --> F["Other Toolkits"]
    
    C --> G["get_tools()"]
    D --> H["Individual Methods"]
    E --> G
    F --> G
    
    G --> I["tools = [...]"]
    H --> I
    
    I --> J["assistant_agent_kwargs"]
    J --> K["'model': models['assistant']"]
    J --> L["'tools': tools"]
    
    J --> M["RolePlaying or OwlRolePlaying"]
    M --> N["Assistant Agent with Tools"]
```

**Toolkit Integration in Society Construction**

The `tools` list aggregates `FunctionTool` objects from multiple sources. Tools from `get_tools()` are unpacked with the `*` operator, while individual toolkit methods (e.g., `SearchToolkit().search_wiki`) are added directly.

Sources: [examples/run.py:91-111](), [examples/run_groq.py:102-122](), [examples/run_mistral.py:162-167]()

## Core Toolkit Categories

### Web Automation and Search

The web-related toolkits provide comprehensive browser automation and search capabilities:

| Toolkit | Primary Function | Key Dependencies |
|---------|------------------|------------------|
| `BrowserToolkit` | Web automation, page interaction | `web_agent_model`, `planning_agent_model` |
| `SearchToolkit` | Search engine queries | DuckDuckGo, Google API, Wikipedia |

The `BrowserToolkit` requires specialized model configuration for web navigation and planning tasks, while `SearchToolkit` provides both unified and individual search methods.

Sources: [examples/run.py:92-96](), [examples/run_groq.py:104-107](), [examples/run_mini.py:77-81]()

### Code and Data Processing

Processing-oriented toolkits handle code execution, data manipulation, and file operations:

| Toolkit | Capabilities | Configuration Options |
|---------|--------------|----------------------|
| `CodeExecutionToolkit` | Python code execution | `sandbox="subprocess"`, `verbose=True` |
| `ExcelToolkit` | Spreadsheet operations | Default configuration |
| `FileWriteToolkit` | File system operations | `output_dir` specification |

Sources: [examples/run.py:99](), [examples/run_groq.py:110](), [examples/run_ollama.py:95]()

### Media Analysis

Media processing toolkits provide multimodal analysis capabilities:

```mermaid
graph TD
    A["Media Analysis Toolkits"] --> B["ImageAnalysisToolkit"]
    A --> C["VideoAnalysisToolkit"]
    A --> D["AudioAnalysisToolkit"]
    
    B --> E["model Parameter"]
    C --> F["model Parameter"]
    D --> G["OpenAI Key Required"]
    
    E --> H["Image Processing Tools"]
    F --> I["Video Processing Tools"]
    G --> J["Audio Processing Tools"]
```

**Media Analysis Toolkit Architecture**

These toolkits typically require model parameters for processing and analysis tasks, with `AudioAnalysisToolkit` specifically requiring OpenAI API access.

Sources: [examples/run.py:97-98](), [examples/run_groq.py:108-109](), [examples/run_novita_ai.py:90]()

### External System Integration

The `MCPToolkit` provides integration with Model Context Protocol servers for extended functionality:

```mermaid
graph TD
    A["MCPToolkit"] --> B["config_path"]
    B --> C["mcp_servers_config.json"]
    
    A --> D["await connect()"]
    A --> E[".get_tools()"]
    A --> F["await disconnect()"]
    
    D --> G["MCP Server Connections"]
    E --> H["External Service Tools"]
    F --> I["Cleanup"]
    
    C --> J["playwright"]
    C --> K["fetch"]
    C --> L["other servers"]
```

**MCP Toolkit Integration Pattern**

The `MCPToolkit` follows an asynchronous pattern requiring explicit connection management and configuration through external JSON files.

Sources: [examples/run_mistral.py:144-148](), [examples/run_mistral.py:172-176]()

## Toolkit Usage Patterns

### Standard Synchronous Pattern

Most toolkits follow a synchronous instantiation and usage pattern:

```mermaid
graph LR
    A["Toolkit Constructor"] --> B["Configuration Parameters"]
    B --> C["Toolkit Instance"]
    C --> D[".get_tools()"]
    D --> E["FunctionTool List"]
    E --> F["Agent Integration"]
```

**Synchronous Toolkit Usage Flow**

This pattern is used by `BrowserToolkit`, `CodeExecutionToolkit`, `ImageAnalysisToolkit`, and others.

Sources: [examples/run.py:92-106](), [examples/run_groq.py:104-117]()

### Asynchronous MCP Pattern

The `MCPToolkit` requires asynchronous handling:

```mermaid
graph TD
    A["MCPToolkit(config_path)"] --> B["await toolkit.connect()"]
    B --> C["toolkit.get_tools()"]
    C --> D["Society Execution"]
    D --> E["await toolkit.disconnect()"]
    
    F["Exception Handling"] --> E
    G["try/finally Block"] --> F
```

**Asynchronous MCP Toolkit Pattern**

This pattern ensures proper resource management for external MCP server connections.

Sources: [examples/run_mistral.py:144-176]()

### Model-Dependent Configuration

Several toolkits require model parameters for specialized processing:

| Toolkit | Model Requirements | Usage Pattern |
|---------|-------------------|---------------|
| `BrowserToolkit` | `web_agent_model`, `planning_agent_model` | Web automation with AI guidance |
| `ImageAnalysisToolkit` | `model` parameter | Image processing and analysis |
| `VideoAnalysisToolkit` | `model` parameter | Video content analysis |
| `DocumentProcessingToolkit` | `model` parameter | Document extraction and processing |

Sources: [examples/run.py:92-96](), [examples/run_groq.py:104-107](), [examples/run_novita_ai.py:84-92]()

## Tool Integration in Society Construction

The toolkit system integrates into the agent society through the `assistant_agent_kwargs` configuration:

```mermaid
graph TD
    A["Multiple Toolkits"] --> B["Tool Collection"]
    B --> C["tools = [*toolkit1.get_tools(), *toolkit2.get_tools(), ...]"]
    C --> D["assistant_agent_kwargs"]
    D --> E["RolePlaying Society"]
    
    F["Individual Tools"] --> B
    G["SearchToolkit Methods"] --> F
    
    H["search_duckduckgo"] --> F
    I["search_google"] --> F
    J["search_wiki"] --> F
```

**Tool Aggregation in Agent Society**

The framework supports mixing tools from multiple toolkits and individual tool methods within a single agent configuration.

Sources: [examples/run.py:91-111](), [examples/run_groq.py:102-122](), [examples/run_mistral.py:162-167]()

---

