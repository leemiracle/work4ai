<!-- source: DeepWiki mcp.deepwiki.com · repo TauricResearch/TradingAgents · page 3 User Interfaces · fetched 2026-10-29 -->

# User Interfaces

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [cli/main.py](cli/main.py)

</details>



## Purpose and Scope

This document provides a high-level overview of the primary methods for interacting with the TradingAgents framework: the interactive Command Line Interface (CLI), the programmatic Python API, the batch backtesting sweep, and the portfolio context management layer. These interfaces bridge natural language user intent and automated batch runs with the core multi-agent execution pipeline.

As a parent page, this section introduces each interface at a macro level. For granular implementation guides, configuration options, and deep technical details, refer to the child pages:
- For CLI workflows, preferences, and real-time display, see [Command Line Interface](#3.1).
- For programmatic graph instantiation and headless automation, see [Python API](#3.2).
- For grid sweeps, evaluation metrics, and decision log persistence, see [Backtesting and Evaluation](#3.3).
- For managing holdings, cash ledgers, and sizing against real portfolios, see [Portfolio Context](#3.4).

Sources: [cli/main.py:68-72](), [tradingagents/backtest.py:1-15](), [tradingagents/portfolio.py:1-15]()

## Interface Comparison and Architecture

The TradingAgents framework supplies multiple access vectors that all funnel through the core orchestration layer (`TradingAgentsGraph`). 

| Interaction Mode | Primary Entry Point | Configuration Mechanism | Execution Context | Output & Persistence |
|------------------|---------------------|-------------------------|-------------------|----------------------|
| **Interactive CLI** | `cli.main:analyze` [cli/main.py:32-67]() | Interactive questionnaire (`questionary`) [cli/utils.py:44-56]() + saved prefs [cli/prefs.py:35-46]() | Single-ticker, single-date run with real-time display | Rich terminal panels + markdown report tree |
| **Python API** | `TradingAgentsGraph` [tradingagents/graph/trading_graph.py:270-275]() | Programmatic configuration dictionary (`DEFAULT_CONFIG`) [tradingagents/default_config.py:1-10]() | Headless or embedded script execution | Python state dicts, return strings, and `save_reports()` [tradingagents/graph/trading_graph.py:270-300]() |
| **Backtest Sweep** | `cli.main:backtest` [cli/main.py:103-119]() | Backtest grid parameters (`--start`, `--end`, `--every`) [cli/main.py:106-108]() | Multi-ticker, multi-date grid iteration | Isolated decision log [tradingagents/backtest.py:145-148]() and aggregate hit-rate scoring |

Sources: [cli/main.py:32-119](), [tradingagents/backtest.py:127-150](), [tradingagents/graph/trading_graph.py:270-300]()

### System Interaction Diagram

```mermaid
graph TB
    subgraph "User_Interfaces"
        CLI[""cli.main:app (Typer App)""]
        API[""TradingAgentsGraph (Python API)""]
        BT[""cli.main:backtest""]
    end
    
    subgraph "Context_and_State"
        Prefs[""cli.prefs:load_last_run()""]
        Port[""tradingagents.portfolio:load_portfolio""]
        Config[""DEFAULT_CONFIG / run_config""]
    end
    
    subgraph "Core_Orchestration"
        Graph[""TradingAgentsGraph.propagate()""]
        Log[""TradingMemoryLog""]
    end
    
    CLI --> Prefs
    CLI --> Config
    API --> Config
    BT --> Config
    
    CLI --> Graph
    API --> Graph
    BT --> Graph
    
    Port -.-> Graph
    Config --> Graph
    Graph --> Log
```

Sources: [cli/main.py:32-153](), [cli/prefs.py:35-46](), [tradingagents/backtest.py:127-150](), [tradingagents/graph/trading_graph.py:270-300]()

## Command Line Interface

The Command Line Interface provides an interactive questionnaire flow for configuring and executing analyses directly from the terminal. Built using `Typer` [cli/main.py:25-29]() and `questionary` [cli/utils.py:44-56](), the CLI prompts users for ticker symbols, analysis dates, asset classifications, and LLM provider parameters via `cli.main:analyze` and `cli.main:backtest` [cli/main.py:32-119](). Previous selections are saved via `cli/prefs.py` to prefill prompts on subsequent runs without skipping validation steps [cli/prefs.py:1-15].

During execution, the CLI renders a live-updating terminal dashboard via `Rich.Live`, tracking agent state transitions (pending, in_progress, completed) through the `MessageBuffer` class [cli/main.py:76-151](). 

For full details on the questionnaire wizard, preference persistence, announcements, and display panels, see [Command Line Interface](#3.1).

Sources: [cli/main.py:25-151](), [cli/utils.py:37-133](), [cli/prefs.py:1-46]()

## Python API

The Python API offers programmatic integration for developers embedding TradingAgents into automated trading bots, notebooks, or continuous integration pipelines. By importing `TradingAgentsGraph` [tradingagents/graph/trading_graph.py:270-275](), scripts can instantiate the graph with customized dictionaries derived from `DEFAULT_CONFIG` [tradingagents/default_config.py:1-10]() and invoke `propagate(ticker, date, portfolio=...)` directly.

Headless executions utilize `save_reports()` to export structured markdown report trees to disk without requiring a terminal console or interactive prompt responses [tradingagents/graph/trading_graph.py:270-300]().

For code examples, instantiation patterns, and configuration overrides, see [Python API](#3.2).

Sources: [tradingagents/graph/trading_graph.py:270-300]()

## Backtesting and Evaluation Sweep

The backtesting subsystem (`tradingagents/backtest.py`) executes the graph over a grid of tickers and dates via `tradingagents.backtest:iter_grid` to evaluate decision quality across historical timeframes [tradingagents/backtest.py:32-49](). To avoid polluting live operational memory, backtests write to an isolated decision log directory configured via `--run-id` [cli/main.py:116-118]().

Cells already recorded in the run's memory log are automatically skipped, enabling robust resumption of interrupted sweeps [tradingagents/backtest.py:136-158](). Aggregate summaries computed via `tradingagents.backtest:summarize` evaluate directional hit rates and mean alpha returns against regional benchmarks [tradingagents/backtest.py:92-124](). Note that backtesting is strictly an evaluation tool for decision quality and explicitly avoids portfolio simulation (e.g., position sizing, cash ledgers, or execution fills) [tradingagents/backtest.py:9-15]().

For detailed coverage of grid generation, settlement passes, and hit-rate scoring, see [Backtesting and Evaluation](#3.3).

Sources: [cli/main.py:103-153](), [tradingagents/backtest.py:1-169]()

## Portfolio Context

Portfolio awareness is managed via `tradingagents/portfolio.py`, which defines the `PortfolioContext` data structure encompassing cash balances, currency types, and active positions [tradingagents/portfolio.py:1-20](). Portfolios can be injected into graph runs via the `--portfolio` CLI flag [cli/main.py:46-51]() or passed explicitly to `propagate(portfolio=...)`. 

Analyst, risk management, and portfolio approval agents inspect real holdings to size recommendations against current portfolio constraints rather than treating the account as a flat cash book [tradingagents/portfolio.py:1-30]().

For complete details on schema definition, position parsing, and integration into agent reasoning prompts, see [Portfolio Context](#3.4).

Sources: [cli/main.py:46-51](), [tradingagents/portfolio.py:1-30]()

### Interface Routing and Execution Flow

```mermaid
graph TB
    subgraph "Interface_Inputs"
        CLI_In[""cli.main:analyze""]
        API_In[""TradingAgentsGraph(config=...)""]
        BT_In[""cli.main:backtest""]
    end
    
    subgraph "Execution_Entities"
        Grid[""tradingagents.backtest:iter_grid()""]
        Prop[""TradingAgentsGraph.propagate()""]
        PortCtx[""tradingagents.portfolio:load_portfolio()""]
    end
    
    subgraph "Storage_and_Reporting"
        MemLog[""tradingagents.agents.utils.memory:TradingMemoryLog""]
        SaveRep[""TradingAgentsGraph.save_reports()""]
    end
    
    CLI_In --> Prop
    API_In --> Prop
    BT_In --> Grid
    Grid --> Prop
    
    PortCtx -.-> Prop
    Prop --> MemLog
    Prop --> SaveRep
```

Sources: [cli/main.py:32-153](), [tradingagents/backtest.py:32-165](), [tradingagents/graph/trading_graph.py:270-300](), [tradingagents/portfolio.py:1-30]()

---

