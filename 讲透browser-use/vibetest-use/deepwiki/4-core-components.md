<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/vibetest-use · page 4 Core Components · fetched 2026-10-30 -->

# Core Components

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [vibetest/agents.py](vibetest/agents.py)
- [vibetest/mcp_server.py](vibetest/mcp_server.py)

</details>



The Vibetest Use system consists of three primary layers that work together to provide AI-powered website testing through browser agents. This page provides an overview of these components and their interactions. For detailed documentation of specific components, see the child pages:

- **Page 4.1** - MCP Server Interface: The FastMCP server that exposes testing tools to IDEs
- **Page 4.2** - Agent Orchestration System: The three-phase agent execution model including scout agent, QA agent pool, and results analysis

This overview focuses on how the components communicate and the key data structures that flow between them.

## Three-Layer Architecture

The system is organized into three distinct layers, each implemented in separate modules:

**Layer 1: MCP Interface** (`vibetest/mcp_server.py`)
- `FastMCP("vibetest")` - The MCP server instance
- `start()` tool - Initiates testing and returns `test_id`
- `results()` tool - Retrieves summarized test results

**Layer 2: Agent Orchestration** (`vibetest/agents.py`)
- `run_pool()` - Orchestrates scout and QA agents
- `scout_page()` - Discovers page elements and generates tasks
- `summarize_bug_reports()` - Analyzes results using LLM
- `_test_results` - In-memory storage dictionary

**Layer 3: Browser Automation** (via `browser_use` library)
- `Agent` - Browser agent with LLM-driven actions
- `BrowserSession` - Playwright session wrapper
- `ChatGoogle` - Google Gemini LLM integration

### Component Interaction Diagram

```mermaid
graph TB
    subgraph Layer1["Layer 1: MCP Server (mcp_server.py)"]
        mcp["mcp = FastMCP('vibetest')"]
        startTool["@mcp.tool() start()"]
        resultsTool["@mcp.tool() results()"]
    end
    
    subgraph Layer2["Layer 2: Agent Orchestration (agents.py)"]
        runPool["run_pool()"]
        scoutPage["scout_page()"]
        summarizeBugs["summarize_bug_reports()"]
        testResults["_test_results = {}"]
    end
    
    subgraph Layer3["Layer 3: Browser Automation (browser_use)"]
        agent["Agent(task, llm, browser_session)"]
        browserSession["BrowserSession(browser_profile)"]
        browserProfile["BrowserProfile(headless, args, ...)"]
        chatGoogle["ChatGoogle(model, api_key)"]
    end
    
    startTool -->|"await"| runPool
    resultsTool -->|"await"| summarizeBugs
    
    runPool -->|"await"| scoutPage
    runPool -->|"stores test_id"| testResults
    summarizeBugs -->|"retrieves by test_id"| testResults
    
    scoutPage -->|"creates"| agent
    runPool -->|"spawns N agents"| agent
    summarizeBugs -->|"uses for analysis"| chatGoogle
    
    agent -->|"requires"| browserSession
    agent -->|"requires"| chatGoogle
    browserSession -->|"configured by"| browserProfile
```

**Sources:** [vibetest/mcp_server.py:13-17](), [vibetest/mcp_server.py:19-38](), [vibetest/mcp_server.py:40-76](), [vibetest/agents.py:1-3](), [vibetest/agents.py:12](), [vibetest/agents.py:23-170](), [vibetest/agents.py:174-361](), [vibetest/agents.py:363-473]()

## Execution Flow

The following sequence diagram shows the complete execution flow from tool invocation to result retrieval, including all function calls and data structures:

```mermaid
sequenceDiagram
    participant IDE as "IDE Client"
    participant start as "start() tool"
    participant runPool as "run_pool()"
    participant scout as "scout_page()"
    participant agent as "Agent.run()"
    participant testResults as "_test_results dict"
    participant results as "results() tool"
    participant summarize as "summarize_bug_reports()"
    participant llm as "ChatGoogle"
    
    IDE->>start: "start(url, num_agents, headless)"
    start->>runPool: "await run_pool(base_url, num_agents, headless)"
    
    runPool->>scout: "await scout_page(base_url)"
    scout->>agent: "Agent(scout_task, llm, browser_session)"
    agent->>llm: "Catalog interactive elements"
    llm-->>agent: "Element inventory"
    agent-->>scout: "history.final_result()"
    scout->>llm: "Partition into qa_tasks[]"
    llm-->>scout: "JSON array of tasks"
    scout-->>runPool: "return qa_tasks[]"
    
    loop "For each agent (parallel)"
        runPool->>agent: "Agent(qa_tasks[i % len], llm, browser_session)"
        agent->>llm: "Execute assigned task"
        llm-->>agent: "Test results"
        agent-->>runPool: "result dict {agent_id, task, result, status}"
    end
    
    runPool->>runPool: "test_id = uuid.uuid4()"
    runPool->>testResults: "_test_results[test_id] = test_data"
    runPool-->>start: "return test_id"
    start-->>IDE: "return str(test_id)"
    
    Note over IDE,summarize: "User requests results..."
    
    IDE->>results: "results(test_id)"
    results->>summarize: "await summarize_bug_reports(test_id)"
    summarize->>testResults: "test_data = _test_results[test_id]"
    testResults-->>summarize: "test_data dict"
    summarize->>llm: "Analyze bug_reports_text"
    llm-->>summarize: "severity_analysis JSON"
    summarize->>summarize: "Calculate overall_status, status_emoji"
    summarize-->>results: "summary dict"
    results->>testResults: "Get duration"
    results->>results: "Format duration_formatted"
    results-->>IDE: "return summary with duration"
```

**Sources:** [vibetest/mcp_server.py:20-38](), [vibetest/mcp_server.py:41-76](), [vibetest/agents.py:23-170](), [vibetest/agents.py:363-473](), [vibetest/agents.py:174-361]()

## Component Function Mapping

| Layer | Module | Key Functions | Returns | Storage |
|-------|--------|---------------|---------|---------|
| **MCP Interface** | `mcp_server.py` | `start()`, `results()` | `str` (test_id), `dict` (summary) | None (delegates to agents) |
| **Orchestration** | `agents.py` | `run_pool()`, `scout_page()`, `summarize_bug_reports()` | `str` (test_id), `list` (tasks), `dict` (summary) | `_test_results` dict |
| **Automation** | `browser_use` | `Agent.run()`, `BrowserSession.aclose()` | `history` object | Browser state |
| **LLM** | `browser_use.llm` | `ChatGoogle.ainvoke()` | Response object | API state |

### Key Imports and Dependencies

```
vibetest/mcp_server.py:
    from mcp.server.fastmcp import FastMCP
    from .agents import run_pool, summarize_bug_reports

vibetest/agents.py:
    from browser_use import Agent, BrowserSession, BrowserProfile
    from browser_use.llm import ChatGoogle
    from browser_use.llm.messages import UserMessage
```

**Sources:** [vibetest/mcp_server.py:13-14](), [vibetest/agents.py:1-3](), [vibetest/agents.py:29-32](), [vibetest/agents.py:265-266]()

## Data Structures

The `_test_results` dictionary stores all test execution data using `test_id` as the key. The data structures flow through the system in three stages:

### Storage Schema

```mermaid
erDiagram
    _test_results {
        string test_id PK
    }
    
    test_data {
        string test_id
        string url
        int agents
        float start_time
        float end_time
        float duration
        string status
    }
    
    results_array {
        int agent_id
        string task
        string result
        float timestamp
        string status
        string error
    }
    
    severity_breakdown {
        array high_severity
        array medium_severity
        array low_severity
    }
    
    summary_dict {
        string test_id
        int total_agents
        int successful_agents
        int failed_agents
        string overall_status
        string status_emoji
        string status_description
        int total_issues
        float duration_seconds
        string duration_formatted
    }
    
    _test_results ||--|| test_data : "indexed by test_id"
    test_data ||--o{ results_array : "contains"
    results_array ||--|| severity_breakdown : "LLM analyzes into"
    severity_breakdown ||--|| summary_dict : "merged into"
```

### Data Flow Through Functions

| Function | Input | Output | Side Effects |
|----------|-------|--------|--------------|
| `run_pool()` | `base_url`, `num_agents`, `headless` | `test_id` (str) | Stores in `_test_results[test_id]` |
| `scout_page()` | `base_url` | `qa_tasks` (list of str) | Creates temporary browser |
| `summarize_bug_reports()` | `test_id` | `summary` (dict) | Reads from `_test_results[test_id]` |
| `start()` tool | `url`, `num_agents`, `headless` | `test_id` (str) | Calls `run_pool()` |
| `results()` tool | `test_id` | `summary` (dict) | Calls `summarize_bug_reports()`, adds duration |

**Sources:** [vibetest/agents.py:12](), [vibetest/agents.py:157-169](), [vibetest/agents.py:116-122](), [vibetest/agents.py:203-210](), [vibetest/agents.py:303-331](), [vibetest/mcp_server.py:57-72]()

## Browser Configuration

The `run_pool()` function contains an internal `run_single_agent()` async function that configures each browser instance with optimized settings:

### Browser Configuration Flow

```mermaid
flowchart TD
    Start["run_single_agent(i)"] --> GetTask["task = qa_tasks[i % len(qa_tasks)]"]
    GetTask --> BrowserArgs["browser_args = ['--disable-gpu', '--no-sandbox', ...]"]
    
    BrowserArgs --> CheckHeadless{"headless?"}
    CheckHeadless -->|true| AddHeadless["browser_args.append('--headless=new')"]
    CheckHeadless -->|false| GetScreen["screen_width, screen_height = get_screen_dimensions()"]
    
    GetScreen --> CalcPos["Calculate x_offset, y_offset based on agent index i"]
    CalcPos --> WindowConfig["window_config = {window_size, viewport}"]
    
    AddHeadless --> CreateProfile["BrowserProfile(headless, args, **window_config)"]
    WindowConfig --> CreateProfile
    
    CreateProfile --> CreateSession["BrowserSession(browser_profile)"]
    CreateSession --> CreateAgent["Agent(task, llm, browser_session)"]
    CreateAgent --> RunAgent["history = await agent.run()"]
    RunAgent --> CloseSession["await browser_session.aclose()"]
    CloseSession --> ReturnResult["return {agent_id, task, result, status}"]
```

### Concurrency Control

The agents execute in parallel with a semaphore limit:

```python
# Line 140-149 in agents.py
semaphore = asyncio.Semaphore(min(num_agents, 10))

async def run_agent_with_semaphore(i: int):
    async with semaphore:
        return await run_single_agent(i)

results = await asyncio.gather(
    *[run_agent_with_semaphore(i) for i in range(num_agents)],
    return_exceptions=True
)
```

The system limits concurrent browser instances to a maximum of 10, regardless of the requested `num_agents` value.

**Sources:** [vibetest/agents.py:35-149](), [vibetest/agents.py:14-21](), [vibetest/agents.py:40-99](), [vibetest/agents.py:140-149]()

## AI Integration Points

The system integrates with Google's Gemini models at three critical points:

| Integration Point | Model | Temperature | Purpose |
|------------------|--------|-------------|---------|
| **scout_page()** | `gemini-1.5-flash` | 0.1 | Element discovery and task generation |
| **run_single_agent()** | `gemini-2.0-flash` | 0.9 | QA task execution with high creativity |
| **summarize_bug_reports()** | `gemini-1.5-flash` | 0.1 | Structured analysis and severity classification |

Each integration point uses `ChatGoogleGenerativeAI` with specific configurations optimized for its role in the testing pipeline.

**Sources:** [vibetest/agents.py:27-31](), [vibetest/agents.py:373-377](), [vibetest/agents.py:233-238]()

---

