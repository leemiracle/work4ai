<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/asta-bench · page 4 Tool System · fetched 2026-10-26 -->

# Tool System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [astabench/evals/paper_finder/eval.py](astabench/evals/paper_finder/eval.py)
- [astabench/tools/__init__.py](astabench/tools/__init__.py)
- [tests/test_registry_evals.py](tests/test_registry_evals.py)

</details>



The Tool System provides a standardized framework for configuring and managing AI agent tools within asta-bench evaluations. It enables flexible composition of capabilities including search, code execution, document editing, and external API integration through a unified configuration interface. The system handles tool registration, parameter validation, date filtering for reproducible evaluations, and integration with external services like Semantic Scholar.

For information about task-specific tool usage patterns, see [Task System](#3.3). For details on external API configurations, see [External API Integration](#4.3).

## ToolsetConfig

The `ToolsetConfig` class serves as the central configuration interface for standardized tool creation in asta-bench. It uses boolean flags to enable/disable different tool categories and provides validation to ensure compatible configurations.

```mermaid
graph TD
    subgraph "ToolsetConfig"
        TC[ToolsetConfig]
        FLAGS["Boolean Configuration Flags"]
        VALIDATION["model_post_init Validation"]
        CREATE["create_tools() Method"]
        
        FLAGS --> TC
        VALIDATION --> TC
        TC --> CREATE
    end
    
    subgraph "Configuration Flags"
        SEARCH["with_search_tools"]
        S2["with_s2_corpus_tools"]
        PYTHON["with_stateful_python"]
        REPORT["with_report_editor"]
        TABLE["with_table_editor"]
        THINKING["with_thinking_tool"]
        SUBMIT["with_editor_submit"]
        
        SEARCH --> FLAGS
        S2 --> FLAGS
        PYTHON --> FLAGS
        REPORT --> FLAGS
        TABLE --> FLAGS
        THINKING --> FLAGS
        SUBMIT --> FLAGS
    end
    
    subgraph "Tool Creation"
        TOOLS_LIST["list[Tool]"]
        MERGE["merge_tools_with_state()"]
        SOLVER["Solver Integration"]
        
        CREATE --> TOOLS_LIST
        TOOLS_LIST --> MERGE
        MERGE --> SOLVER
    end
```

Sources: [astabench/tools/__init__.py:28-117]()

The configuration system enforces dependencies between tools. For example, `with_editor_submit=True` requires at least one editor tool to be enabled:

```mermaid
graph LR
    subgraph "Validation Rules"
        EDITOR_SUBMIT["with_editor_submit=True"]
        REPORT_CHECK{"with_report_editor?"}
        TABLE_CHECK{"with_table_editor?"}
        ERROR["ValueError"]
        VALID["Valid Configuration"]
        
        EDITOR_SUBMIT --> REPORT_CHECK
        EDITOR_SUBMIT --> TABLE_CHECK
        REPORT_CHECK -->|No| TABLE_CHECK
        TABLE_CHECK -->|No| ERROR
        REPORT_CHECK -->|Yes| VALID
        TABLE_CHECK -->|Yes| VALID
    end
```

Sources: [astabench/tools/__init__.py:77-83]()

## Tool Categories and Registration

The tool system organizes tools into distinct categories, each serving specific agent capabilities:

| Category | Tools | Purpose |
|----------|--------|---------|
| Search | `paper_search`, `snippet_search` | Literature discovery and information retrieval |
| External APIs | S2 corpus tools, native search tools | Integration with Semantic Scholar and other APIs |
| Code Execution | `python_session`, `continue_wait`, `interrupt_kernel` | Stateful Python code execution |
| Document Editing | `report_editor`, `table_editor` | Document creation and modification |
| Utility | `calculator`, `think()` | Mathematical computation and reasoning |
| Submission | `submit_tool` | Result submission functionality |

```mermaid
graph TD
    subgraph "Tool Registration System"
        REGISTRY["TOOL_REGISTRY dict"]
        REGISTER_FUNC["register_tool() function"]
        FACTORY_PATTERN["Factory Pattern"]
        TOOL_DEF["ToolDef wrapper"]
        
        REGISTER_FUNC --> REGISTRY
        FACTORY_PATTERN --> REGISTER_FUNC
        TOOL_DEF --> FACTORY_PATTERN
    end
    
    subgraph "Registered Tools"
        PAPER_SEARCH["paper_search()"]
        SNIPPET_SEARCH["snippet_search()"]
        CALCULATOR["calculator()"]
        TABLE_EDITOR["table_editor()"]
        REPORT_EDITOR["report_editor()"]
        
        PAPER_SEARCH --> REGISTRY
        SNIPPET_SEARCH --> REGISTRY
        CALCULATOR --> REGISTRY
        TABLE_EDITOR --> REGISTRY
        REPORT_EDITOR --> REGISTRY
    end
```

Sources: [astabench/tools/__init__.py:120-149]()

The registration system uses a factory pattern where tools are wrapped in lambda functions to ensure proper initialization:

```mermaid
graph LR
    subgraph "Tool Factory Pattern"
        FUNC["Tool Function"]
        REGISTER["register_tool(func)"]
        LAMBDA["lambda: ToolDef(func).as_tool()"]
        REGISTRY_ENTRY["TOOL_REGISTRY entry"]
        
        FUNC --> REGISTER
        REGISTER --> LAMBDA
        LAMBDA --> REGISTRY_ENTRY
    end
```

Sources: [astabench/tools/__init__.py:124-135]()

## Semantic Scholar API Integration

The S2 API tools provide comprehensive integration with Semantic Scholar's research corpus through MCP (Model Context Protocol) connections. The system includes sophisticated date filtering for reproducible evaluations.

```mermaid
graph TD
    subgraph "S2 API Architecture"
        TOOLSOURCE["make_s2api_toolsource()"]
        MCP_CLIENT["MCPServerImpl"]
        HTTP_CLIENT["streamablehttp_client"]
        S2_API["Semantic Scholar API"]
        
        TOOLSOURCE --> MCP_CLIENT
        MCP_CLIENT --> HTTP_CLIENT
        HTTP_CLIENT --> S2_API
    end
    
    subgraph "Available S2 Tools"
        GET_PAPER["get_paper"]
        GET_BATCH["get_paper_batch"]
        GET_CITATIONS["get_citations"]
        SEARCH_AUTHORS["search_authors_by_name"]
        GET_AUTHOR_PAPERS["get_author_papers"]
        SEARCH_RELEVANCE["search_papers_by_relevance"]
        SEARCH_TITLE["search_paper_by_title"]
        SNIPPET_SEARCH_S2["snippet_search"]
        
        TOOLSOURCE --> GET_PAPER
        TOOLSOURCE --> GET_BATCH
        TOOLSOURCE --> GET_CITATIONS
        TOOLSOURCE --> SEARCH_AUTHORS
        TOOLSOURCE --> GET_AUTHOR_PAPERS
        TOOLSOURCE --> SEARCH_RELEVANCE
        TOOLSOURCE --> SEARCH_TITLE
        TOOLSOURCE --> SNIPPET_SEARCH_S2
    end
```

Sources: [astabench/tools/s2_api_tools.py:56-64](), [astabench/tools/s2_api_tools.py:604-632]()

### Date Filtering System

The S2 API tools implement comprehensive date filtering to ensure reproducible evaluations by limiting results to papers published before a specified insertion date:

```mermaid
graph TD
    subgraph "Date Filtering Pipeline"
        INSERTION_DATE["insertion_date parameter"]
        FIELD_INJECTION["_adjust_fields_arg_for_subfield_filter()"]
        API_CALL["Original S2 API Call"]
        RESPONSE_FILTER["_filter_response_subfield()"]
        FILTERED_RESPONSE["Filtered Response"]
        
        INSERTION_DATE --> FIELD_INJECTION
        FIELD_INJECTION --> API_CALL
        API_CALL --> RESPONSE_FILTER
        RESPONSE_FILTER --> FILTERED_RESPONSE
    end
    
    subgraph "Filtering Mechanisms"
        SUBFIELD_FILTER["_wrap_subfield_date_filter()"]
        TOPLEVEL_FILTER["_wrap_toplevel_date_filter()"]
        ERROR_CHECK["_error_if_recent_papers_toplevel()"]
        
        SUBFIELD_FILTER --> RESPONSE_FILTER
        TOPLEVEL_FILTER --> ERROR_CHECK
    end
```

Sources: [astabench/tools/s2_api_tools.py:255-321](), [astabench/tools/s2_api_tools.py:323-365]()

The date filtering system automatically injects required date fields and removes them from responses to maintain clean tool interfaces:

```mermaid
graph LR
    subgraph "Field Injection Process"
        ORIGINAL_FIELDS["Original fields param"]
        CHECK_YEAR["Check for year field"]
        CHECK_DATE["Check for publicationDate field"]
        INJECT_FIELDS["Inject missing date fields"]
        API_REQUEST["Modified API request"]
        FILTER_RESPONSE["Filter & remove injected fields"]
        CLEAN_RESPONSE["Clean response"]
        
        ORIGINAL_FIELDS --> CHECK_YEAR
        CHECK_YEAR --> CHECK_DATE
        CHECK_DATE --> INJECT_FIELDS
        INJECT_FIELDS --> API_REQUEST
        API_REQUEST --> FILTER_RESPONSE
        FILTER_RESPONSE --> CLEAN_RESPONSE
    end
```

Sources: [astabench/tools/s2_api_tools.py:227-252]()

### Retry and Error Handling

The S2 API tools include sophisticated retry mechanisms for handling rate limiting and transient failures:

```mermaid
graph TD
    subgraph "Retry System"
        TOOL_CALL["Tool Execution"]
        ERROR_CHECK{"Is Error Retryable?"}
        RETRY_CODES["429, 529, 504 HTTP codes"]
        BROKEN_RESOURCE["BrokenResourceError"]
        EXPONENTIAL_BACKOFF["Exponential Backoff"]
        MAX_RETRIES{"Max Retries Reached?"}
        TOOL_ERROR["ToolError"]
        SUCCESS["Successful Response"]
        
        TOOL_CALL --> ERROR_CHECK
        ERROR_CHECK -->|Yes| RETRY_CODES
        ERROR_CHECK -->|Yes| BROKEN_RESOURCE
        RETRY_CODES --> EXPONENTIAL_BACKOFF
        BROKEN_RESOURCE --> EXPONENTIAL_BACKOFF
        EXPONENTIAL_BACKOFF --> MAX_RETRIES
        MAX_RETRIES -->|No| TOOL_CALL
        MAX_RETRIES -->|Yes| TOOL_ERROR
        TOOL_CALL --> SUCCESS
    end
```

Sources: [astabench/tools/s2_api_tools.py:544-602](), [astabench/tools/s2_api_tools.py:454-485]()

## Tool Configuration Workflows

The tool system integrates with asta-bench evaluation workflows through standardized configuration patterns:

```mermaid
graph TD
    subgraph "Solver Integration Pattern"
        CLI_FLAGS["CLI Tool Flags"]
        TOOL_OPTIONS["**tool_options"]
        CONFIG_VALIDATE["ToolsetConfig.model_validate()"]
        CREATE_TOOLS["config.create_tools()"]
        MERGE_STATE["merge_tools_with_state()"]
        SOLVER_CHAIN["Solver Chain"]
        
        CLI_FLAGS --> TOOL_OPTIONS
        TOOL_OPTIONS --> CONFIG_VALIDATE
        CONFIG_VALIDATE --> CREATE_TOOLS
        CREATE_TOOLS --> MERGE_STATE
        MERGE_STATE --> SOLVER_CHAIN
    end
    
    subgraph "CLI Example"
        INSPECT_EVAL["inspect eval"]
        SOLVER_FLAG["--solver my_agent"]
        S_FLAGS["-S with_report_editor=1 -S with_s2_corpus_tools=1"]
        
        INSPECT_EVAL --> SOLVER_FLAG
        SOLVER_FLAG --> S_FLAGS
        S_FLAGS --> CLI_FLAGS
    end
```

Sources: [astabench/tools/__init__.py:37-56]()

### Tool Override and Merging

The system supports tool merging where task-provided tools can override solver-provided tools, maintaining task-specific constraints like date restrictions:

```mermaid
graph LR
    subgraph "Tool Merging Process"
        SOLVER_TOOLS["Solver Tools"]
        TASK_TOOLS["Task Tools"]
        MERGE_FUNC["merge_tools_with_state()"]
        FINAL_TOOLS["Final Tool Set"]
        
        SOLVER_TOOLS --> MERGE_FUNC
        TASK_TOOLS --> MERGE_FUNC
        MERGE_FUNC --> FINAL_TOOLS
    end
    
    subgraph "Override Logic"
        EQUIVALENT_CHECK{"Equivalent Tool Names?"}
        USE_TASK["Use Task Version"]
        USE_SOLVER["Use Solver Version"]
        
        MERGE_FUNC --> EQUIVALENT_CHECK
        EQUIVALENT_CHECK -->|Yes| USE_TASK
        EQUIVALENT_CHECK -->|No| USE_SOLVER
    end
```

Sources: [astabench/tools/__init__.py:32-36]()

## Advanced Tool Customization

The tool system supports extensive customization through wrapper functions and parameter overrides:

```mermaid
graph TD
    subgraph "Tool Customization System"
        ORIGINAL_TOOL["Original Tool"]
        OVERRIDE_WRAPPER["make_override_wrapper()"]
        RETRY_WRAPPER["make_retry_wrapper()"]
        DATE_FILTER_WRAPPER["Date Filter Wrappers"]
        FINAL_TOOL["Customized Tool"]
        
        ORIGINAL_TOOL --> OVERRIDE_WRAPPER
        OVERRIDE_WRAPPER --> RETRY_WRAPPER
        RETRY_WRAPPER --> DATE_FILTER_WRAPPER
        DATE_FILTER_WRAPPER --> FINAL_TOOL
    end
    
    subgraph "Override Types"
        ARG_DEFAULTS["Argument Defaults"]
        ARG_OVERRIDES["Forced Overrides"]
        PARAM_REMOVAL["Parameter Removal"]
        DESC_MODIFICATION["Description Updates"]
        
        ARG_DEFAULTS --> OVERRIDE_WRAPPER
        ARG_OVERRIDES --> OVERRIDE_WRAPPER
        PARAM_REMOVAL --> OVERRIDE_WRAPPER
        DESC_MODIFICATION --> OVERRIDE_WRAPPER
    end
```

Sources: [astabench/tools/s2_api_tools.py:487-542]()

The customization system allows for:
- Setting default values for tool parameters
- Forcing specific parameter values that cannot be overridden
- Removing parameters from the tool interface
- Updating tool descriptions to reflect changes

Sources: [astabench/tools/s2_api_tools.py:487-542](), [astabench/tools/s2_api_tools.py:367-434]()

---

