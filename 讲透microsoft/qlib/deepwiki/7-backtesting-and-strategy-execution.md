<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/qlib · page 7 Backtesting and Strategy Execution · fetched 2026-10-26 -->

# Backtesting and Strategy Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [qlib/backtest/__init__.py](qlib/backtest/__init__.py)
- [qlib/backtest/account.py](qlib/backtest/account.py)
- [qlib/backtest/backtest.py](qlib/backtest/backtest.py)
- [qlib/backtest/decision.py](qlib/backtest/decision.py)
- [qlib/backtest/exchange.py](qlib/backtest/exchange.py)
- [qlib/backtest/executor.py](qlib/backtest/executor.py)
- [qlib/backtest/high_performance_ds.py](qlib/backtest/high_performance_ds.py)
- [qlib/backtest/position.py](qlib/backtest/position.py)
- [qlib/backtest/report.py](qlib/backtest/report.py)
- [qlib/backtest/utils.py](qlib/backtest/utils.py)
- [qlib/contrib/strategy/rule_strategy.py](qlib/contrib/strategy/rule_strategy.py)
- [qlib/strategy/base.py](qlib/strategy/base.py)
- [qlib/utils/index_data.py](qlib/utils/index_data.py)
- [qlib/utils/time.py](qlib/utils/time.py)
- [tests/backtest/test_file_strategy.py](tests/backtest/test_file_strategy.py)
- [tests/misc/test_index_data.py](tests/misc/test_index_data.py)

</details>



The Qlib backtesting system provides a realistic simulation environment for evaluating quantitative trading strategies. It handles the complete workflow from model predictions to portfolio execution, including market simulation, transaction costs, trading constraints, and performance analysis.

The system supports both single-frequency execution (e.g., daily rebalancing) and nested multi-frequency execution (e.g., daily portfolio decisions executed at minute-level granularity). This page provides an overview of the backtesting architecture, while detailed information about specific components can be found in:
- **[Trading Strategies](#7.1)**: Signal-based and rule-based strategy implementations.
- **[Executors and Nested Execution](#7.2)**: Order execution engines and nested execution patterns.
- **[Exchange and Market Simulation](#7.3)**: Market data, trading limits, and transaction cost models.
- **[Account and Position Management](#7.4)**: Portfolio tracking and position updates.
- **[Performance Metrics and Reporting](#7.5)**: Risk metrics, trade indicators, and reporting.
- **[High-Performance Data Structures](#7.6)**: Fast quote data and indicator computation structures.

## Architecture Overview

### Backtesting Pipeline

The backtesting system transforms model predictions into executed trades through a multi-stage pipeline. The flow proceeds from high-level portfolio decisions through order generation, market simulation, and position updates.

**System Component Association**

The following diagram associates natural language concepts with specific code entities in the Qlib backtesting system.

```mermaid
graph TB
    subgraph "Strategy Layer"
        ["BaseStrategy"] --> ["TWAPStrategy"]
        ["BaseStrategy"] --> ["SBBStrategyBase"]
    end
    
    subgraph "Decision & Execution"
        ["BaseTradeDecision"] --- ["Order"]
        ["BaseExecutor"] --- ["SimulatorExecutor"]
        ["BaseExecutor"] --- ["NestedExecutor"]
    end
    
    subgraph "Market & State"
        ["Exchange"] --- ["Account"]
        ["Account"] --- ["BasePosition"]
        ["BasePosition"] --- ["Position"]
    end

    subgraph "Code Entities"
        ["BaseStrategy"]:::code
        ["TWAPStrategy"]:::code
        ["SBBStrategyBase"]:::code
        ["BaseTradeDecision"]:::code
        ["Order"]:::code
        ["BaseExecutor"]:::code
        ["SimulatorExecutor"]:::code
        ["NestedExecutor"]:::code
        ["Exchange"]:::code
        ["Account"]:::code
        ["BasePosition"]:::code
        ["Position"]:::code
    end

    classDef code font-family:monospace, font-weight:bold;
```

**Key Flow**:
1. **Strategy Layer**: `BaseStrategy` implementations like `TWAPStrategy` convert goals into decisions [qlib/strategy/base.py:23-147]().
2. **Decision Layer**: `BaseTradeDecision` encapsulates `Order` objects which contain `stock_id`, `amount`, and `direction` [qlib/backtest/decision.py:11-50]().
3. **Execution Layer**: `BaseExecutor` (e.g., `SimulatorExecutor`) manages the timing of execution and infrastructure [qlib/backtest/executor.py:22-125]().
4. **Market Simulation**: `Exchange` validates orders, applies costs via `open_cost`/`close_cost`, and calculates execution prices [qlib/backtest/exchange.py:28-121]().
5. **Portfolio State**: `Account` tracks `current_position` and `accum_info` (returns, costs, turnover) [qlib/backtest/account.py:71-125]().
6. **Analysis**: `PortfolioMetrics` and `Indicator` compute performance reports [qlib/backtest/report.py:22-247]().

Sources: [qlib/strategy/base.py:23-147](), [qlib/backtest/executor.py:22-125](), [qlib/backtest/exchange.py:28-121](), [qlib/backtest/account.py:71-125](), [qlib/backtest/report.py:22-247]()

### Execution Loop

The main backtesting loop iterates through trading periods, generating decisions and executing orders.

**Backtest Execution Flow**

```mermaid
graph TD
    [Start: backtest_loop] --> [collect_data_loop]
    [collect_data_loop] --> [trade_strategy.generate_trade_decision]
    [trade_strategy.generate_trade_decision] --> [trade_executor.collect_data]
    
    subgraph "Execution Step"
        [trade_executor.collect_data] --> ["exchange.deal_order"]
        ["exchange.deal_order"] --> ["account.update_order"]
        ["account.update_order"] --> ["account.update_bar_end"]
    end
    
    ["account.update_bar_end"] --> [trade_calendar.step]
    [trade_calendar.step] --> [Check: executor.finished]
    [Check: executor.finished] -- "No" --> [trade_strategy.generate_trade_decision]
    [Check: executor.finished] -- "Yes" --> [End: Collect Metrics]
```

**Core Loop Logic**:
The `backtest_loop` initiates the process by calling `collect_data_loop` [qlib/backtest/backtest.py:25-49](). The loop iterates until the `trade_executor` calendar is finished [qlib/backtest/backtest.py:87-91](). In each step:
- `generate_trade_decision` is called on the strategy to produce a `BaseTradeDecision` [qlib/backtest/backtest.py:88]().
- `collect_data` on the executor processes the decision, yielding results from the simulation [qlib/backtest/backtest.py:89]().
- The account state is updated via `_update_state_from_order` during execution [qlib/backtest/account.py:183-200]().
- Final metrics are aggregated from all executors in the hierarchy [qlib/backtest/backtest.py:95-109]().

Sources: [qlib/backtest/backtest.py:25-110](), [qlib/backtest/executor.py:110-125](), [qlib/backtest/account.py:183-200]()

## Key Components

### 1. Trading Strategies
Strategies convert model predictions into trading decisions. Qlib provides signal-based strategies and rule-based strategies like `TWAPStrategy` [qlib/contrib/strategy/rule_strategy.py:22-123]() and `SBBStrategyBase` [qlib/contrib/strategy/rule_strategy.py:125-153](). For details, see **[Trading Strategies](#7.1)**.

Sources: [qlib/strategy/base.py:23-147](), [qlib/contrib/strategy/rule_strategy.py:22-153]()

### 2. Executors and Order Execution
Executors manage the timing and hierarchy of trading. `BaseExecutor` provides the interface for resetting infrastructure and tracking dealt amounts [qlib/backtest/executor.py:22-125](). For details, see **[Executors and Nested Execution](#7.2)**.

Sources: [qlib/backtest/executor.py:22-155]()

### 3. Exchange and Market Simulation
The `Exchange` class simulates realistic market conditions, handling `deal_price`, `limit_threshold`, and volume constraints [qlib/backtest/exchange.py:28-121](). It can be initialized via `get_exchange` helper [qlib/backtest/__init__.py:33-110](). For details, see **[Exchange and Market Simulation](#7.3)**.

Sources: [qlib/backtest/exchange.py:28-121](), [qlib/backtest/__init__.py:33-110]()

### 4. Account and Position Management
The `Account` class tracks portfolio state, including cash and positions [qlib/backtest/account.py:71-125](). It manages `AccumulatedInfo` for returns and costs [qlib/backtest/account.py:35-70](). For details, see **[Account and Position Management](#7.4)**.

Sources: [qlib/backtest/account.py:35-136](), [qlib/backtest/position.py:16-200]()

### 5. Performance Metrics and Reporting
`PortfolioMetrics` tracks daily returns, benchmark comparisons, and turnover [qlib/backtest/report.py:22-166](). It supports benchmark configurations like CSI300 [qlib/backtest/report.py:97-122](). For details, see **[Performance Metrics and Reporting](#7.5)**.

Sources: [qlib/backtest/report.py:22-247]()

### 6. High-Performance Data Structures
Qlib uses specialized structures like `NumpyQuote` [qlib/backtest/high_performance_ds.py:128-151]() and `IndexData` [qlib/utils/index_data.py:87-120]() for fast data retrieval during simulation. For details, see **[High-Performance Data Structures](#7.6)**.

Sources: [qlib/backtest/high_performance_ds.py:128-182](), [qlib/utils/index_data.py:87-120]()

## Infrastructure and Coordination

Backtesting components are coordinated via `CommonInfrastructure` and `LevelInfrastructure` [qlib/backtest/utils.py:17-19](). 

- **CommonInfrastructure**: Shares the `trade_account` and `trade_exchange` across all execution levels [qlib/backtest/__init__.py:208]().
- **LevelInfrastructure**: Manages level-specific data like the `trade_calendar` and the current `executor` [qlib/backtest/executor.py:116-117]().
- **TradeCalendarManager**: Handles time stepping and frequency-specific calendars [qlib/backtest/utils.py:23-102]().

Sources: [qlib/backtest/utils.py:23-102](), [qlib/backtest/executor.py:110-125](), [qlib/strategy/base.py:63-78]()

---

