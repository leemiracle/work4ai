<!-- source: DeepWiki mcp.deepwiki.com · repo TauricResearch/TradingAgents · page 6 Core Orchestration · fetched 2026-10-29 -->

# Core Orchestration

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [tests/test_memory_log.py](tests/test_memory_log.py)
- [tradingagents/graph/trading_graph.py](tradingagents/graph/trading_graph.py)

</details>



## Purpose and Scope

This document covers the core orchestration system of TradingAgents, focusing on how the `TradingAgentsGraph` class coordinates the entire multi-agent trading analysis framework [tradingagents/graph/trading_graph.py:51-52](). The orchestration system manages the execution flow from initial data gathering through multi-agent analysis, debate, and final trading decisions.

The orchestration layer sits between the user interfaces ([User Interfaces](#3)) and the individual agent implementations ([Agent System](#5)), providing a unified execution pipeline that coordinates data flow, agent interactions, and decision synthesis using LangGraph.

For detailed information about the `TradingAgentsGraph` class architecture, see [TradingAgentsGraph Architecture](#6.1). For details on how the state transitions through the pipeline, see [State Management and Propagation](#6.2). For the learning and feedback loop, see [Reflection and Memory Updates](#6.3). For checkpointing capabilities, see [Checkpointing and Resume](#6.4). For signal extraction and report outputs, see [Signal Processing and Reporting Output](#6.5).

Sources: `[tradingagents/graph/trading_graph.py:51-52]()`

---

## Main Orchestration Flow

The core orchestration follows a structured pipeline that coordinates multiple agent teams through distinct phases of analysis, research, and decision-making [tradingagents/graph/trading_graph.py:51-116](). The graph construction initializes LangGraph workflows, binding tier-specific LLM clients and tool nodes.

### High-Level Execution Pipeline

```mermaid
flowchart TD
    UserRequest["User Request<br/>ticker, date"] --> Initialize["TradingAgentsGraph.propagate()"]
    
    Initialize --> InitState["Propagator.create_initial_state()<br/>AgentState initialization"]
    
    InitState --> AnalystPhase["Analyst Team Phase"]
    
    subgraph AnalystPhase["Sequential Analyst Execution"]
        MarketAnalyst["market_analyst_node"]
        FundamentalsAnalyst["fundamentals_analyst_node"]
        SocialAnalyst["social_media_analyst_node"]
        NewsAnalyst["news_analyst_node"]
    end
    
    AnalystPhase --> ResearchPhase["Research Team Phase"]
    
    subgraph ResearchPhase["Investment Research Debate"]
        BullResearcher["Bull Researcher"]
        BearResearcher["Bear Researcher"]
        ResearchManager["Research Manager"]
    end
    
    ResearchPhase --> TradingPhase["Trading Decision Phase"]
    
    subgraph TradingPhase["Trading Agent"]
        TraderAgent["Trader"]
    end
    
    TradingPhase --> RiskPhase["Risk Management Phase"]
    
    subgraph RiskPhase["Risk Assessment Team"]
        AggressiveAnalyst["Aggressive Analyst"]
        ConservativeAnalyst["Conservative Analyst"]
        NeutralAnalyst["Neutral Analyst"]
        PortfolioManager["Portfolio Manager"]
    end
    
    RiskPhase --> FinalDecision["final_trade_decision"]
    FinalDecision --> ProcessSignal["SignalProcessor.process_signal()"]
    ProcessSignal --> Output["Processed trading signal"]
    
    FinalDecision --> StateLogging["_log_state()<br/>JSON persistence"]
```

For details on the underlying setup, see [TradingAgentsGraph Architecture](#6.1).

Sources: `[tradingagents/graph/trading_graph.py:51-116]()`

---

## State Management and Data Flow

The orchestration system manages complex state transitions through the multi-agent pipeline, ensuring data consistency and proper information flow between agent teams. The graph maintains run state, debate states (`InvestDebateState`, `RiskDebateState`), and checkpoint signatures [tradingagents/graph/trading_graph.py:140-154]().

### State Flow Architecture

```mermaid
graph TB
    subgraph "Input Layer"
        UserInput["ticker: str<br/>trade_date: str"]
        Config["config: Dict<br/>DEFAULT_CONFIG"]
    end
    
    subgraph "State Initialization"
        InitState["Propagator.create_initial_state()<br/>AgentState object"]
    end
    
    subgraph "Agent State Management"
        AnalystReports["market_report<br/>sentiment_report<br/>news_report<br/>fundamentals_report"]
        DebateStates["investment_debate_state<br/>InvestDebateState"]
        TradingDecision["trader_investment_plan"]
        RiskStates["risk_debate_state<br/>RiskDebateState"]
        FinalState["final_trade_decision"]
    end
    
    subgraph "Persistence Layer"
        CurrentState["self.curr_state<br/>reflection context"]
        MemoryLog["TradingMemoryLog<br/>markdown log file"]
    end
    
    UserInput --> InitState
    Config --> InitState
    
    InitState --> AnalystReports
    AnalystReports --> DebateStates
    DebateStates --> TradingDecision
    TradingDecision --> RiskStates
    RiskStates --> FinalState
    
    FinalState --> CurrentState
    FinalState --> MemoryLog
```

For details on state propagation, data structures, and streaming vs. invocation modes, see [State Management and Propagation](#6.2).

Sources: `[tradingagents/graph/trading_graph.py:51-154]()`

---

## Execution Modes and Checkpointing

The orchestration system supports standard batch execution via `.invoke()` and streaming execution for debug modes, alongside durable per-ticker SQLite checkpointers to resume interrupted or cached runs [tradingagents/graph/trading_graph.py:22-26]() [tradingagents/graph/trading_graph.py:112-116]().

### Execution Mode Selection

```mermaid
flowchart TD
    PropagateCall["TradingAgentsGraph.propagate(ticker, trade_date)"] --> DebugCheck{"self.debug?"}
    
    DebugCheck -->|True| DebugMode["Debug Mode<br/>Streaming Execution"]
    DebugCheck -->|False| StandardMode["Standard Mode<br/>Batch Execution"]
    
    subgraph DebugMode["Debug Mode Implementation"]
        StreamCall["self.workflow.stream(init_state, config)"]
        DebugResult["final_state = trace[-1]"]
    end
    
    subgraph StandardMode["Standard Mode Implementation"]
        InvokeCall["self.graph.invoke(init_state, config)"]
        StandardResult["final_state = result"]
    end
    
    DebugResult --> PostProcess["Post-processing & Checkpoint"]
    StandardResult --> PostProcess
    
    PostProcess --> SignalProcess["SignalProcessor.process_signal()"]
```

For details on SQLite checkpointers, run signatures, and resumption logic, see [Checkpointing and Resume](#6.4).

Sources: `[tradingagents/graph/trading_graph.py:22-26](), [tradingagents/graph/trading_graph.py:112-116]()`

---

## Learning, Signal Processing, and Reporting

After graph execution completes, the orchestration layer invokes signal processing, outcome settlement, and report tree generation. The `Reflector` evaluates final outcomes against historical benchmarks (`benchmark_map`), appending structured lessons to `TradingMemoryLog` [tradingagents/graph/trading_graph.py:18-20]() [tradingagents/graph/trading_graph.py:106-106]().

### Reflection and Memory Update Flow

```mermaid
sequenceDiagram
    participant User
    participant TradingAgentsGraph
    participant Reflector
    participant TradingMemoryLog
    
    User->>TradingAgentsGraph: "reflect_on_final_decision(ticker, trade_date)"
    TradingAgentsGraph->>TradingAgentsGraph: "_fetch_returns(ticker, trade_date)"
    Note over TradingAgentsGraph: "Calculates raw_return and alpha_return"
    
    TradingAgentsGraph->>Reflector: "reflect_on_final_decision(state, returns)"
    Reflector->>TradingAgentsGraph: "Returns reflection text"
    
    TradingAgentsGraph->>TradingMemoryLog: "update_with_outcome(ticker, trade_date, outcome_data)"
    Note over TradingMemoryLog: "Appends outcome and reflection to markdown log"
```

For details on outcome settlement and reflection resilience, see [Reflection and Memory Updates](#6.3). For signal extraction, review flagging, and HTML report generation, see [Signal Processing and Reporting Output](#6.5).

Sources: `[tradingagents/graph/trading_graph.py:18-20](), [tradingagents/graph/trading_graph.py:106-106]()`

---

## Child Pages
- [TradingAgentsGraph Architecture](#6.1) — Explain the TradingAgentsGraph class, initialization parameters, component setup (LLMs, memories, tool nodes), GraphSetup, ConditionalLogic, Propagator, Reflector, SignalProcessor, _log_state, and save_reports()
- [State Management and Propagation](#6.2) — Detail AgentState, InvestDebateState, RiskDebateState, create_run_state/create_initial_state, instrument identity resolution, propagate(), and graph streaming vs invocation
- [Reflection and Memory Updates](#6.3) — Explain the Reflector, reflect_on_final_decision, outcome settlement (raw_return, alpha_return, holding_period_days window), configurable benchmark_map alpha baselines, and resilience when reflection fails
- [Checkpointing and Resume](#6.4) — Document graph/checkpointer.py, per-ticker SQLite checkpointers, begin_checkpoint/end_checkpoint, run signature graph-shape identity, clear_checkpoint_on_success, and the --checkpoint / checkpoint_enabled options
- [Signal Processing and Reporting Output](#6.5) — Explain signal_processing.py extraction of the final rating, labelled-rating precedence and review flagging, tradingagents/reporting.py write_report_tree / missing-report handling, and report_html.py self-contained HTML report generation with embedded logo assets

---

