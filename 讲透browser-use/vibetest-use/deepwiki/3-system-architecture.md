<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/vibetest-use · page 3 System Architecture · fetched 2026-10-30 -->

# System Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [vibetest/agents.py](vibetest/agents.py)
- [vibetest/mcp_server.py](vibetest/mcp_server.py)

</details>



This document provides a detailed explanation of how vibetest-use works internally, covering the MCP server implementation, agent orchestration system, and browser automation components. It focuses on the technical architecture and interactions between core system components.

For setup and installation instructions, see [Getting Started](#2). For detailed API documentation of individual components, see [Core Components](#4).

## Overview

vibetest-use implements a distributed website testing system built around three main architectural layers: an MCP (Model Context Protocol) server interface, an agent orchestration system, and a browser automation engine. The system coordinates multiple parallel browser agents to perform comprehensive QA testing of web applications.

### High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        Claude["Claude IDE"]
        Cursor["Cursor IDE"] 
        CLI["Command Line"]
    end
    
    subgraph "MCP Protocol Layer"
        FastMCP["FastMCP Server<br/>mcp_server.py"]
        StartTool["start() tool"]
        ResultsTool["results() tool"]
    end
    
    subgraph "Agent Orchestration Layer"
        RunPool["run_pool()"]
        Scout["scout_page()"]
        Summarize["summarize_bug_reports()"]
        TestResults["_test_results dict"]
    end
    
    subgraph "Browser Automation Layer" 
        BrowserUse["Browser-Use Agent"]
        BrowserSession["BrowserSession"]
        BrowserProfile["BrowserProfile"]
        Playwright["Playwright"]
    end
    
    subgraph "AI/LLM Layer"
        Gemini["ChatGoogleGenerativeAI<br/>gemini-2.0-flash"]
        LangChain["langchain_core"]
    end
    
    Claude --> FastMCP
    Cursor --> FastMCP
    CLI --> FastMCP
    
    FastMCP --> StartTool
    FastMCP --> ResultsTool
    
    StartTool --> RunPool
    ResultsTool --> Summarize
    
    RunPool --> Scout
    RunPool --> TestResults
    Summarize --> TestResults
    
    RunPool --> BrowserUse
    Scout --> BrowserUse
    BrowserUse --> BrowserSession
    BrowserSession --> BrowserProfile
    BrowserProfile --> Playwright
    
    RunPool --> Gemini
    Scout --> Gemini
    Summarize --> Gemini
    Gemini --> LangChain
```

Sources: [vibetest/mcp_server.py:1-87](), [vibetest/agents.py:1-453](), [README.md:1-89]()

## MCP Server Interface

The system's entry point is a FastMCP server that exposes two primary tools for test orchestration. The server handles JSON-RPC communication and provides a clean interface for external clients.

### Server Implementation

```mermaid
graph LR
    subgraph "mcp_server.py"
        MCPInstance["mcp = FastMCP('vibetest')"]
        StartTool["@mcp.tool()<br/>start(url, num_agents, headless)"]
        ResultsTool["@mcp.tool()<br/>results(test_id)"]
        RunEntry["run()"]
    end
    
    subgraph "External Interface"
        JSONRpc["JSON-RPC Calls"]
        ClientIDEs["IDE Clients"]
    end
    
    subgraph "Agent Layer Integration"
        RunPoolFunc["run_pool()"]
        SummarizeFunc["summarize_bug_reports()"]
    end
    
    ClientIDEs --> JSONRpc
    JSONRpc --> MCPInstance
    MCPInstance --> StartTool
    MCPInstance --> ResultsTool
    
    StartTool --> RunPoolFunc
    ResultsTool --> SummarizeFunc
    
    RunEntry --> MCPInstance
```

The `start()` tool accepts a URL and configuration parameters, then delegates to `run_pool()` for agent coordination. The `results()` tool retrieves test outcomes via `summarize_bug_reports()` and enriches them with timing data from the `_test_results` global store.

Sources: [vibetest/mcp_server.py:19-84]()

## Agent Orchestration System

The core orchestration logic resides in the `agents.py` module, implementing a multi-phase testing workflow: reconnaissance, task generation, parallel execution, and result analysis.

### Agent Workflow

```mermaid
sequenceDiagram
    participant Client
    participant StartTool as "start() tool"
    participant RunPool as "run_pool()"
    participant Scout as "scout_page()"
    participant LLM as "ChatGoogleGenerativeAI"
    participant AgentPool as "Agent Pool"
    participant Results as "_test_results"
    
    Client->>StartTool: "start(url, num_agents, headless)"
    StartTool->>RunPool: "run_pool(base_url, num_agents, headless)"
    
    RunPool->>Scout: "scout_page(base_url)"
    Scout->>LLM: "Inventory interactive elements"
    LLM-->>Scout: "Element discovery results"
    Scout->>LLM: "Partition elements into tasks"
    LLM-->>Scout: "qa_tasks[]"
    Scout-->>RunPool: "qa_tasks[]"
    
    RunPool->>AgentPool: "asyncio.gather(run_single_agent())"
    
    par Agent 1
        AgentPool->>LLM: "Task execution"
    and Agent 2  
        AgentPool->>LLM: "Task execution"
    and Agent N
        AgentPool->>LLM: "Task execution"  
    end
    
    AgentPool-->>RunPool: "agent_results[]"
    RunPool->>Results: "_test_results[test_id] = test_data"
    RunPool-->>StartTool: "test_id"
    StartTool-->>Client: "test_id"
```

Sources: [vibetest/agents.py:21-187](), [vibetest/agents.py:370-453]()

### Agent Pool Management

The `run_pool()` function implements sophisticated agent lifecycle management with parallel execution controls:

| Component | Implementation | Purpose |
|-----------|----------------|---------|
| **Semaphore Control** | `asyncio.Semaphore(min(num_agents, 10))` | Limits concurrent browser instances |
| **Window Positioning** | Screen dimension calculation + offset logic | Arranges non-headless browser windows |
| **Browser Configuration** | `BrowserProfile` with security disabled | Optimizes automation performance |
| **Error Handling** | Per-agent exception isolation | Ensures partial test completion |
| **Process Cleanup** | `pkill -f chromium` on macOS | Prevents resource leaks |

The system creates unique `BrowserSession` instances for each agent, with custom `BrowserProfile` configurations that handle both headless and visual modes.

Sources: [vibetest/agents.py:33-187](), [vibetest/agents.py:76-86]()

## Browser Automation Engine

Each agent operates through the Browser-Use library, which provides high-level automation capabilities built on Playwright. The system configures browser instances with specific profiles optimized for QA testing.

### Browser Instance Configuration

```mermaid
graph TB
    subgraph "Agent Configuration"
        AgentClass["Agent(task, llm, browser_session, use_vision=True)"]
        TaskDesc["task_description from qa_tasks"]
        LLMInstance["ChatGoogleGenerativeAI(gemini-2.0-flash)"]
    end
    
    subgraph "Browser Session Setup"
        BrowserSession["BrowserSession(browser_profile, headless)"]
        BrowserProfile["BrowserProfile"]
        WindowConfig["window_size, window_position, viewport"]
        SecurityConfig["disable_security=True"]
        Args["args=['--disable-gpu', '--no-sandbox']"]
    end
    
    subgraph "Runtime Features"
        Vision["use_vision=True"]
        ZoomLogic["document.body.style.zoom = '0.25'"]
        NetworkWait["wait_for_network_idle_page_load_time=2.0"]
        ActionDelay["wait_between_actions=0.5"]
    end
    
    AgentClass --> BrowserSession
    BrowserSession --> BrowserProfile
    BrowserProfile --> WindowConfig
    BrowserProfile --> SecurityConfig  
    BrowserProfile --> Args
    
    AgentClass --> Vision
    BrowserSession --> ZoomLogic
    BrowserProfile --> NetworkWait
    BrowserProfile --> ActionDelay
```

Non-headless mode implements sophisticated window positioning logic that calculates screen dimensions and arranges browser windows in a grid pattern to enable visual monitoring of multiple agents.

Sources: [vibetest/agents.py:76-112](), [vibetest/agents.py:44-74]()

## Task Generation and Execution

The system uses a two-phase approach for test case generation: initial reconnaissance via `scout_page()` followed by LLM-driven task partitioning.

### Scout-Based Task Generation

```mermaid
flowchart TD
    ScoutPage["scout_page(base_url)"]
    HeadlessBrowser["BrowserSession(headless=True)"]
    ScoutTask["Visit page + catalog interactive elements"]
    AgentRun["agent.run()"]
    ScoutResult["scout_result string"]
    
    PartitionPrompt["LLM Partition Prompt:<br/>Create 6-8 specific testing tasks"]
    LLMInvoke["llm.invoke(partition_prompt)"]
    JSONParse["JSON array parsing with regex"]
    ElementTasks["element_tasks[]"]
    FallbackTasks["Fallback generic tasks"]
    
    ScoutPage --> HeadlessBrowser
    HeadlessBrowser --> ScoutTask
    ScoutTask --> AgentRun
    AgentRun --> ScoutResult
    
    ScoutResult --> PartitionPrompt
    PartitionPrompt --> LLMInvoke
    LLMInvoke --> JSONParse
    JSONParse --> ElementTasks
    JSONParse --> FallbackTasks
    
    ElementTasks --> Return["return element_tasks"]
    FallbackTasks --> Return
```

The scout agent operates in headless mode to minimize resource usage and performs comprehensive element discovery. The LLM then partitions discovered elements into specific, non-overlapping test scenarios.

Sources: [vibetest/agents.py:370-453](), [vibetest/agents.py:406-441]()

## Result Processing and Analysis

Test results undergo structured analysis through the `summarize_bug_reports()` function, which applies LLM-based severity classification and generates standardized reports.

### Analysis Pipeline

```mermaid
graph TB
    subgraph "Data Collection"
        TestResults["_test_results[test_id]"]
        AgentResults["agent_results[]"]
        BugReports["bug_reports[]"]
        Errors["errors[]"]
    end
    
    subgraph "LLM Analysis"
        AnalysisPrompt["Severity classification prompt"]
        GeminiFlash["ChatGoogleGenerativeAI(gemini-1.5-flash)"]
        JSONRegex["re.search(r'\\{.*\\}', response)"]
        SeverityBreakdown["high_severity[], medium_severity[], low_severity[]"]
    end
    
    subgraph "Report Generation"
        OverallStatus["overall_status calculation"]
        StatusEmoji["status_emoji assignment"]
        DurationCalc["duration_formatted calculation"]
        FinalSummary["Complete summary dict"]
    end
    
    TestResults --> AgentResults
    TestResults --> BugReports  
    TestResults --> Errors
    
    BugReports --> AnalysisPrompt
    AnalysisPrompt --> GeminiFlash
    GeminiFlash --> JSONRegex
    JSONRegex --> SeverityBreakdown
    
    SeverityBreakdown --> OverallStatus
    OverallStatus --> StatusEmoji
    TestResults --> DurationCalc
    
    OverallStatus --> FinalSummary
    StatusEmoji --> FinalSummary
    DurationCalc --> FinalSummary
    SeverityBreakdown --> FinalSummary
```

The analysis pipeline implements strict criteria for issue classification, requiring specific technical problems rather than subjective design opinions. Results include detailed severity breakdowns with actionable descriptions.

Sources: [vibetest/agents.py:191-368](), [vibetest/agents.py:240-281]()

## Data Storage and State Management

The system maintains test state through a global `_test_results` dictionary that persists throughout the server's lifecycle. Each test receives a UUID identifier and comprehensive metadata.

### Test Data Structure

| Field | Type | Description |
|-------|------|-------------|
| `test_id` | `str` | UUID identifier from `uuid.uuid4()` |
| `url` | `str` | Target URL being tested |
| `agents` | `int` | Number of agents spawned |
| `start_time` | `float` | Unix timestamp from `time.time()` |
| `end_time` | `float` | Completion timestamp |
| `duration` | `float` | Calculated execution time |
| `results` | `list` | Array of agent result dictionaries |
| `status` | `str` | Overall test status |

Individual agent results contain task descriptions, execution outcomes, timestamps, and error details when applicable.

Sources: [vibetest/agents.py:10](), [vibetest/agents.py:174-186]()

---

