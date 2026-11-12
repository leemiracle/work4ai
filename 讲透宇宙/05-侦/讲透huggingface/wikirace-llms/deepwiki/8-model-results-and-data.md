<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/wikirace-llms · page 8 Model Results and Data · fetched 2026-10-26 -->

# Model Results and Data

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [results/popular_nodes.json](results/popular_nodes.json)
- [results/qwen3-30B-A3-results.json](results/qwen3-30B-A3-results.json)
- [results/qwen3.json](results/qwen3.json)
- [src/components/about-tab.tsx](src/components/about-tab.tsx)

</details>



This document describes the structure, format, and analysis of model evaluation results in the WikiRacing LLMs system. It covers how evaluation data is collected, stored, and interpreted to assess model performance in Wikipedia navigation tasks.

For information about the evaluation framework that generates this data, see [Evaluation Framework](#7.2). For details about the game mechanics being evaluated, see [Game Logic](#7.1).

## Results Data Structure

The system stores evaluation results in JSON format with a standardized schema that captures both aggregate statistics and detailed step-by-step traces of model navigation behavior.

### Primary Results Schema

```mermaid
graph TB
    ResultsFile["results/qwen3-30B-A3-results.json"]
    ArticleList["article_list"]
    TrialConfig["Trial Configuration"]
    AgentSettings["agent_settings"]
    RunsArray["runs[]"]
    
    ResultsFile --> ArticleList
    ResultsFile --> TrialConfig
    ResultsFile --> AgentSettings
    ResultsFile --> RunsArray
    
    TrialConfig --> NumTrials["num_trials"]
    TrialConfig --> NumWorkers["num_workers"] 
    TrialConfig --> MaxSteps["max_steps"]
    
    AgentSettings --> ModelName["model"]
    AgentSettings --> ApiBase["api_base"]
    AgentSettings --> MaxLinks["max_links"]
    AgentSettings --> MaxTries["max_tries"]
    
    RunsArray --> IndividualRun["Individual Run"]
    IndividualRun --> RunMetadata["Run Metadata"]
    IndividualRun --> StepsArray["steps[]"]
    
    RunMetadata --> Result["result: win/move/lose"]
    RunMetadata --> StartArticle["start_article"]
    RunMetadata --> DestArticle["destination_article"]
    
    StepsArray --> StepType["type: start/move/win/lose"]
    StepsArray --> StepArticle["article"]
    StepsArray --> StepMetadata["metadata"]
```

**Results File Structure**

Sources: [results/qwen3-30B-A3-results.json:1-50](), [results/qwen3.json:1-50]()

### Run Outcome Classification

The evaluation system classifies each navigation attempt into three categories:

| Result Type | Description | Example |
|-------------|-------------|---------|
| `"win"` | Successfully reached target article | Soviet Union → Frank Lloyd Wright in 3 steps |
| `"move"` | Reached maximum steps without success | Stuck in navigation loops |
| `"lose"` | Failed to find valid links after max retries | Model output parsing failures |

### Step Trace Format

Each navigation step is recorded with detailed metadata:

```mermaid
graph LR
    Step["Navigation Step"]
    Step --> Type["type"]
    Step --> Article["article"]
    Step --> Metadata["metadata"]
    
    Type --> Start["start"]
    Type --> Move["move"] 
    Type --> Win["win"]
    Type --> Lose["lose"]
    
    Metadata --> Tries["tries: int"]
    Metadata --> Message["message: string"]
```

**Step Types and Metadata**

Sources: [results/qwen3-30B-A3-results.json:40-70](), [results/qwen3.json:43-69]()

## Popular Navigation Nodes

The system tracks frequently visited Wikipedia articles to identify common navigation hubs and patterns.

### Node Popularity Data

```mermaid
graph TB
    PopularNodes["results/popular_nodes.json"]
    PopularNodes --> NodeArray["Article Names Array"]
    
    NodeArray --> Geographic["Geographic Entities"]
    NodeArray --> Countries["Countries/Regions"]
    NodeArray --> Cultural["Cultural Topics"]
    NodeArray --> Technical["Technical Subjects"]
    
    Geographic --> Examples1["'United States', 'Europe', 'Asia'"]
    Countries --> Examples2["'France', 'Japan', 'England'"]
    Cultural --> Examples3["'The Beatles', 'Animation', 'Association football'"]
    Technical --> Examples4["'R (programming language)', 'PlayStation 4'"]
```

**Popular Node Categories**

The data reveals several categories of highly-trafficked articles:

- **Geographic hubs**: Major countries, continents, and regions
- **Cultural landmarks**: Famous bands, movies, sports
- **Technical topics**: Programming languages, software platforms
- **Institutional entities**: Universities, organizations, government bodies

Sources: [results/popular_nodes.json:1-10]()

## Performance Metrics Analysis

### Success Rate Patterns

```mermaid
graph LR
    SuccessMetrics["Success Rate Analysis"]
    SuccessMetrics --> WinRate["Win Rate"]
    SuccessMetrics --> PathLength["Average Path Length"]
    SuccessMetrics --> RetryPattern["Retry Patterns"]
    
    WinRate --> DirectPaths["Direct Navigation Success"]
    WinRate --> IndirectPaths["Multi-hop Success"]
    
    PathLength --> OptimalPaths["2-3 Steps"]
    PathLength --> LongPaths["10+ Steps"]
    
    RetryPattern --> FirstTry["tries: 0"]
    RetryPattern --> MultipleRetries["tries: 1-3"]
```

**Key Performance Indicators**

From the evaluation data, several performance patterns emerge:

1. **Navigation Efficiency**: Successful runs typically complete in 2-10 steps
2. **Retry Behavior**: Models often succeed on first attempt (`tries: 0`) for direct paths
3. **Loop Detection**: Failed runs show repeated article transitions
4. **Target Specificity**: Some destinations (e.g., "France") are reached more reliably than others

Sources: [results/qwen3-30B-A3-results.json:36-107](), [results/qwen3.json:40-177]()

## Model Comparison Framework

### Multi-Model Evaluation Structure

```mermaid
graph TB
    ModelResults["Model Results Comparison"]
    ModelResults --> Qwen30B["qwen3-30B-A3-results.json"]
    ModelResults --> Qwen14B["qwen3.json"]
    
    Qwen30B --> Config30B["30B Model Config"]
    Qwen14B --> Config14B["14B Model Config"]
    
    Config30B --> Settings30B["max_links: 200<br/>max_steps: 20<br/>num_workers: 200"]
    Config14B --> Settings14B["max_links: 500<br/>max_steps: 20<br/>num_workers: 200"]
    
    ModelResults --> ComparisonMetrics["Comparison Metrics"]
    ComparisonMetrics --> SuccessRates["Success Rates"]
    ComparisonMetrics --> PathEfficiency["Path Efficiency"] 
    ComparisonMetrics --> NavigationPatterns["Navigation Patterns"]
```

**Configuration Differences**

The evaluation framework tests different model configurations to assess capability variations:

- **Model size impact**: 30B vs 14B parameter models
- **Link limit effects**: 200 vs 500 max links per page
- **Consistency across runs**: Multiple trials per article pair

Sources: [results/qwen3-30B-A3-results.json:21-29](), [results/qwen3.json:28-33]()

## Navigation Pattern Analysis

### Common Path Strategies

The traced navigation data reveals distinct strategic patterns:

| Strategy | Example Path | Characteristics |
|----------|--------------|-----------------|
| Geographic Bridging | Soviet Union → United States → Japan → Nintendo | Uses major countries as intermediate hubs |
| Topical Association | Soviet Union → State atheism → Vietnam → Hindu temple → Hinduism | Follows conceptual relationships |
| Institutional Routing | Soviet Union → University of Pennsylvania → Ivy League → Harvard → Academic degree | Leverages institutional connections |

### Loop Prevention Analysis

```mermaid
graph LR
    LoopDetection["Loop Detection Patterns"]
    LoopDetection --> SuccessfulAvoidance["Successful Avoidance"]
    LoopDetection --> FailedAttempts["Failed Loop Recovery"]
    
    SuccessfulAvoidance --> DiversePath["Path Diversification"]
    SuccessfulAvoidance --> BacktrackStrategy["Strategic Backtracking"]
    
    FailedAttempts --> InfiniteLoops["Infinite Article Cycles"]
    FailedAttempts --> StuckPatterns["Repetitive Patterns"]
    
    InfiniteLoops --> Example1["Borneo ↔ Kalimantan"]
    StuckPatterns --> Example2["Google ↔ List of Google products"]
```

**Loop Mitigation Strategies**

Sources: [results/qwen3-30B-A3-results.json:565-687](), [results/qwen3.json:590-686]()

## Data Storage and Access Patterns

### File Organization Schema

```mermaid
graph TB
    ResultsDir["results/"]
    ResultsDir --> ModelFiles["Model-specific Files"]
    ResultsDir --> AggregateData["Aggregate Data"]
    
    ModelFiles --> QwenResults["qwen3*.json"]
    ModelFiles --> OtherModels["Other Model Results"]
    
    AggregateData --> PopularNodes["popular_nodes.json"]
    AggregateData --> SummaryStats["Summary Statistics"]
    
    QwenResults --> DetailedTraces["Detailed Step Traces"]
    QwenResults --> ConfigMetadata["Configuration Metadata"]
    
    PopularNodes --> FrequencyData["Article Visit Frequencies"]
    PopularNodes --> NavigationHubs["Common Navigation Hubs"]
```

**File Naming Conventions**

- Model results: `{model_name}-{config_suffix}-results.json`
- Aggregate data: `{data_type}_nodes.json`
- Configuration variants indicated by suffixes (e.g., `30B-A3`)

Sources: [results/qwen3-30B-A3-results.json:1](), [results/popular_nodes.json:1](), [results/qwen3.json:1]()

---

