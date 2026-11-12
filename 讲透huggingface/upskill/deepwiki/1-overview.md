<!-- source: DeepWiki mcp.deepwiki.com · repo huggingface/upskill · page 1 Overview · fetched 2026-10-26 -->

# Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [pyproject.toml](pyproject.toml)
- [src/upskill/cli.py](src/upskill/cli.py)
- [tests/test_smoke.py](tests/test_smoke.py)
- [uv.lock](uv.lock)

</details>



## Purpose and Scope

This document provides a high-level introduction to the **upskill** system, a framework for automatically generating and evaluating agent skills using large language models. The system implements a teacher-student paradigm where powerful "teacher models" (e.g., Claude Opus, GPT-4) generate structured skill documents that less capable "student models" (e.g., Claude Haiku, smaller local models) can use to improve their performance on specific tasks.

Upskill enables:
- **Automated skill generation** from task descriptions, examples, or agent traces
- **Systematic evaluation** with baseline comparison and statistical metrics
- **Iterative refinement** through feedback loops
- **Cross-model testing** to validate skill effectiveness on different models
- **Comprehensive logging** for performance analysis and debugging

For detailed information on specific subsystems, see:
- Installation and configuration: [Getting Started](#2)
- Core concepts and terminology: [Core Concepts](#3)
- CLI command reference: [CLI Reference](#4)
- Skill lifecycle workflows: [Skill Lifecycle](#5)
- Data structures: [Data Models Reference](#7)

**Sources**: [README.md:1-514](), [src/upskill/cli.py:1-43](), Diagram 1 and 2 from context

---

## Teacher-Student Model Paradigm

The upskill system is built around the concept that expensive, high-capability models can teach cheaper, faster models to perform specific tasks more effectively. A **teacher model** analyzes a task and generates a skill document (SKILL.md) containing instructions, examples, and guidance. A **student model** then loads this skill into its context when executing tasks, improving success rates and often reducing token usage.

```mermaid
graph LR
    subgraph "Teacher Phase"
        Task["Task Description"]
        Teacher["Teacher Model<br/>(e.g., opus, gpt-4)"]
        SkillGen["skill_gen agent"]
    end
    
    subgraph "Skill Artifact"
        Skill["SKILL.md<br/>+ references/<br/>+ scripts/"]
    end
    
    subgraph "Student Phase"
        Student["Student Model<br/>(e.g., haiku, llama3.2)"]
        Evaluator["evaluator agent"]
        Result["Improved Performance"]
    end
    
    Task --> Teacher
    Teacher --> SkillGen
    SkillGen --> Skill
    Skill --> Student
    Skill --> Evaluator
    Student --> Evaluator
    Evaluator --> Result
```

The evaluation system measures skill effectiveness using two key metrics:
- **Skill lift**: percentage improvement in success rate (must exceed 5% for acceptance)
- **Token savings**: reduction in token usage (must exceed 20% if success rate doesn't improve significantly)

A skill is considered **beneficial** if `lift > 5%` OR `(lift >= 0 AND token_savings > 20%)`.

**Sources**: [README.md:5-6](), [src/upskill/models.py:270-307](), Diagram 2 from context

---

## System Architecture

### Component Overview

The upskill system has a layered architecture with four main layers:

```mermaid
graph TB
    subgraph "Interface Layer"
        CLI["CLI<br/>cli.py::main"]
        PythonAPI["Python API<br/>generate_skill()<br/>evaluate_skill()"]
    end
    
    subgraph "Core Layer"
        Generate["generate.py<br/>generate_skill()<br/>refine_skill()<br/>improve_skill()"]
        Evaluate["evaluate.py<br/>evaluate_skill()<br/>run_test()"]
        Models["models.py<br/>Skill<br/>TestCase<br/>EvalResults<br/>RunResult"]
    end
    
    subgraph "Agent Layer"
        FastAgent["FastAgent Runtime<br/>_fast_agent_context()"]
        SkillGenCard["agent_cards/skill_gen.md"]
        TestGenCard["agent_cards/test_gen.md"]
        EvaluatorCard["agent_cards/evaluator.md"]
    end
    
    subgraph "Storage Layer"
        Config["config.py<br/>Config.load()"]
        Logging["logging.py<br/>write_run_result()<br/>summarize_runs()"]
        SkillsFS["./skills/<br/>skill-name/SKILL.md"]
        RunsFS["./runs/<br/>batch_*/run_*/"]
    end
    
    CLI --> Generate
    CLI --> Evaluate
    PythonAPI --> Generate
    PythonAPI --> Evaluate
    
    Generate --> Models
    Evaluate --> Models
    Generate --> FastAgent
    Evaluate --> FastAgent
    
    FastAgent --> SkillGenCard
    FastAgent --> TestGenCard
    FastAgent --> EvaluatorCard
    
    Models --> SkillsFS
    Generate --> Config
    Evaluate --> Config
    Evaluate --> Logging
    Logging --> RunsFS
```

**Sources**: [src/upskill/cli.py:49-66](), [src/upskill/generate.py](), [src/upskill/evaluate.py](), [src/upskill/models.py](), Diagram 1 from context

### Key Code Entities

| Layer | Component | Primary Code Entities | Purpose |
|-------|-----------|----------------------|---------|
| **Interface** | CLI | `cli.py::main()`, `cli.py::generate()`, `cli.py::eval_cmd()` | Command-line interface |
| | Python API | `generate.py::generate_skill()`, `evaluate.py::evaluate_skill()` | Programmatic access |
| **Core** | Generation | `generate.py::generate_skill()`, `generate.py::refine_skill()` | Skill creation and improvement |
| | Evaluation | `evaluate.py::evaluate_skill()`, `evaluate.py::run_test()` | Performance testing |
| | Data Models | `models.py::Skill`, `models.py::TestCase`, `models.py::EvalResults` | Data structures |
| **Agent** | FastAgent | `cli.py::_fast_agent_context()`, `fast.run()` | Agent orchestration |
| | Agent Cards | `agent_cards/skill_gen.md`, `agent_cards/test_gen.md`, `agent_cards/evaluator.md` | Agent definitions |
| **Storage** | Configuration | `config.py::Config`, `Config.load()` | System settings |
| | Logging | `logging.py::create_batch_folder()`, `logging.py::write_run_result()` | Run tracking |
| | Persistence | `Skill.save()`, `Skill.load()` | Skill storage |

**Sources**: [src/upskill/cli.py:162-254](), [src/upskill/generate.py](), [src/upskill/evaluate.py](), [src/upskill/models.py](), [src/upskill/config.py](), [src/upskill/logging.py]()

---

## Main Workflows

### Skill Generation and Evaluation Flow

```mermaid
graph TD
    Start["User invokes<br/>upskill generate TASK"]
    
    GenSkill["generate.py::generate_skill()<br/>via agent.skill_gen"]
    GenSkillDraft["Returns SkillDraft"]
    ConvertSkill["Converts to Skill object<br/>models.py::Skill"]
    
    GenTests["generate.py::generate_tests()<br/>via agent.test_gen"]
    TestList["Returns List[TestCase]"]
    
    EvalLoop{"Refinement Loop<br/>attempts < max_refine_attempts"}
    
    RunEval["evaluate.py::evaluate_skill()<br/>via agent.evaluator"]
    
    Baseline["Run baseline tests<br/>(without skill)"]
    WithSkill["Run with-skill tests<br/>(skill in context)"]
    Compare["Compare results<br/>EvalResults.is_beneficial"]
    
    LogRuns["logging.py::write_run_result()<br/>to ./runs/batch_*/"]
    
    Beneficial{"is_beneficial?"}
    SaveSkill["Skill.save()<br/>to ./skills/skill-name/"]
    
    Refine["generate.py::refine_skill()<br/>with failure descriptions"]
    
    Start --> GenSkill
    GenSkill --> GenSkillDraft
    GenSkillDraft --> ConvertSkill
    ConvertSkill --> GenTests
    GenTests --> TestList
    TestList --> EvalLoop
    
    EvalLoop -->|continue| RunEval
    RunEval --> Baseline
    RunEval --> WithSkill
    Baseline --> Compare
    WithSkill --> Compare
    Compare --> LogRuns
    LogRuns --> Beneficial
    
    Beneficial -->|Yes| SaveSkill
    Beneficial -->|No| Refine
    Refine --> EvalLoop
    
    EvalLoop -->|max attempts| SaveSkill
```

**Sources**: [src/upskill/cli.py:256-536](), [src/upskill/generate.py:60-134](), [src/upskill/evaluate.py:140-204](), Diagram 2 from context

### Agent Card System

The system uses declarative YAML-frontmatter markdown files to define specialized agents:

```mermaid
graph TB
    subgraph "Agent Card Files"
        SkillGenMD["agent_cards/skill_gen.md<br/>type: agent<br/>model: opus"]
        TestGenMD["agent_cards/test_gen.md<br/>type: agent<br/>model: opus?reasoning=1024"]
        EvalMD["agent_cards/evaluator.md<br/>type: agent<br/>skills: ./skills"]
    end
    
    subgraph "FastAgent Runtime"
        FastAgentCtx["cli.py::_fast_agent_context()<br/>FastAgent('upskill')"]
        LoadAgents["fast.load_agents(cards_path)"]
        RunCtx["fast.run() as agent"]
    end
    
    subgraph "Agent Instances"
        SkillGenAgent["agent.skill_gen"]
        TestGenAgent["agent.test_gen"]
        EvaluatorAgent["agent.evaluator"]
    end
    
    subgraph "Core Functions"
        GenFunc["generate.py::generate_skill(<br/>generator=agent.skill_gen)"]
        TestFunc["generate.py::generate_tests(<br/>generator=agent.test_gen)"]
        EvalFunc["evaluate.py::evaluate_skill(<br/>evaluator=agent.evaluator)"]
    end
    
    SkillGenMD --> LoadAgents
    TestGenMD --> LoadAgents
    EvalMD --> LoadAgents
    
    FastAgentCtx --> LoadAgents
    LoadAgents --> RunCtx
    
    RunCtx --> SkillGenAgent
    RunCtx --> TestGenAgent
    RunCtx --> EvaluatorAgent
    
    SkillGenAgent --> GenFunc
    TestGenAgent --> TestFunc
    EvaluatorAgent --> EvalFunc
```

**Sources**: [src/upskill/cli.py:49-66](), [src/upskill/generate.py](), [src/upskill/evaluate.py](), Diagram 3 from context

---

## Data Models

### Core Data Structures

The system defines several Pydantic models in `models.py` that represent the data flowing through the system:

```mermaid
graph TB
    subgraph "Generation Phase"
        SkillDraft["SkillDraft<br/>name: str<br/>description: str<br/>body: str"]
        Skill["Skill<br/>name: str<br/>description: str<br/>body: str<br/>metadata: SkillMetadata<br/>references: dict<br/>scripts: dict<br/>tests: list"]
        TestCase["TestCase<br/>input: str<br/>expected: ExpectedSpec<br/>context: TestCaseContext<br/>validator: str"]
    end
    
    subgraph "Evaluation Phase"
        TestResult["TestResult<br/>test_case: TestCase<br/>success: bool<br/>output: str<br/>stats: ConversationStats<br/>validation_result: ValidationResult"]
        
        ConvStats["ConversationStats<br/>conversation_span_ms: float<br/>llm_time_ms: float<br/>tool_time_ms: float<br/>turns: int<br/>input_tokens: int<br/>output_tokens: int<br/>total_tokens: int"]
        
        EvalResults["EvalResults<br/>baseline_results: list<br/>with_skill_results: list<br/>baseline_success_rate: float<br/>with_skill_success_rate: float<br/>skill_lift: float<br/>token_savings: float<br/>is_beneficial: bool"]
    end
    
    subgraph "Logging Phase"
        RunMeta["RunMetadata<br/>model: str<br/>task: str<br/>batch_id: str<br/>run_number: int"]
        
        RunResult["RunResult<br/>metadata: RunMetadata<br/>stats: ConversationStats<br/>passed: bool<br/>assertions_passed: int<br/>assertions_total: int<br/>run_type: str<br/>skill_name: str"]
        
        BatchSummary["BatchSummary<br/>batch_id: str<br/>model: str<br/>task: str<br/>total_runs: int<br/>passed_runs: int<br/>results: List[RunResult]"]
    end
    
    SkillDraft -.->|converted to| Skill
    Skill --> TestCase
    TestCase --> TestResult
    TestResult --> ConvStats
    TestResult --> EvalResults
    ConvStats --> RunResult
    RunMeta --> RunResult
    RunResult --> BatchSummary
```

**Sources**: [src/upskill/models.py:1-307](), Diagram 4 from context

### Key Model Relationships

| Model | Purpose | Key Fields | Created By |
|-------|---------|------------|------------|
| `Skill` | Complete skill artifact | `name`, `body`, `references`, `scripts` | `generate.py::generate_skill()` |
| `TestCase` | Individual test specification | `input`, `expected`, `validator` | `generate.py::generate_tests()` |
| `EvalResults` | Comparison of baseline vs with-skill | `skill_lift`, `token_savings`, `is_beneficial` | `evaluate.py::evaluate_skill()` |
| `ConversationStats` | Detailed execution metrics | `llm_time_ms`, `total_tokens`, `tool_calls` | `logging.py::extract_stats()` |
| `RunResult` | Single evaluation run record | `metadata`, `stats`, `passed` | CLI during evaluation |
| `BatchSummary` | Aggregated batch results | `total_runs`, `passed_runs`, `results` | `logging.py::write_batch_summary()` |

**Sources**: [src/upskill/models.py:31-307](), [src/upskill/logging.py:96-270]()

---

## Evaluation and Metrics System

### Test Execution Pipeline

```mermaid
graph LR
    subgraph "Input"
        TC["TestCase<br/>input<br/>expected<br/>validator"]
    end
    
    subgraph "Execution"
        Agent["LlmAgent<br/>(detached instance)"]
        Workspace["Isolated<br/>temp directory"]
        RunTest["evaluate.py::run_test()"]
    end
    
    subgraph "Metrics Collection"
        MsgHistory["Message History<br/>from agent"]
        ExtractTokens["logging.py::extract_tokens()<br/>from FAST_AGENT_USAGE"]
        ExtractTiming["logging.py::extract_timing()<br/>from FAST_AGENT_TIMING"]
        ConvStats2["ConversationStats"]
    end
    
    subgraph "Validation"
        Validator["Custom validator<br/>or contains check"]
        ValResult["ValidationResult<br/>assertions_passed<br/>assertions_total"]
    end
    
    subgraph "Output"
        TR["TestResult<br/>success<br/>output<br/>stats<br/>validation_result"]
    end
    
    TC --> RunTest
    RunTest --> Agent
    Agent --> Workspace
    Agent --> MsgHistory
    MsgHistory --> ExtractTokens
    MsgHistory --> ExtractTiming
    ExtractTokens --> ConvStats2
    ExtractTiming --> ConvStats2
    Workspace --> Validator
    TC --> Validator
    Validator --> ValResult
    ConvStats2 --> TR
    ValResult --> TR
```

**Sources**: [src/upskill/evaluate.py:50-204](), [src/upskill/logging.py:96-216](), Diagram 6 from context

### Metrics Calculation

The system tracks comprehensive metrics during evaluation:

| Metric | Calculation | Purpose |
|--------|-------------|---------|
| **conversation_span_ms** | Total time from first to last message | Overall execution time |
| **llm_time_ms** | Sum of LLM call durations | Time spent in model inference |
| **tool_time_ms** | Sum of tool execution durations | Time spent in tool/MCP calls |
| **turns** | Count of conversation turns | Interaction complexity |
| **input_tokens** | Sum from FAST_AGENT_USAGE | Input cost estimation |
| **output_tokens** | Sum from FAST_AGENT_USAGE | Output cost estimation |
| **total_tokens** | input_tokens + output_tokens | Total cost estimation |
| **skill_lift** | `(with_skill_rate - baseline_rate) / baseline_rate` | Performance improvement |
| **token_savings** | `(baseline_tokens - with_skill_tokens) / baseline_tokens` | Efficiency gain |

The **is_beneficial** decision logic is implemented in [src/upskill/models.py:297-307]():

```python
@property
def is_beneficial(self) -> bool:
    """Skill is beneficial if it improves success rate by >5% OR maintains/improves 
    success while saving >20% tokens."""
    lift = self.skill_lift
    savings = self.token_savings
    
    # Significant success improvement
    if lift > 0.05:
        return True
    
    # Maintains success with significant token savings
    if lift >= 0 and savings > 0.20:
        return True
    
    return False
```

**Sources**: [src/upskill/models.py:212-307](), [src/upskill/logging.py:96-216](), Diagram 6 from context

---

## Storage and Persistence

### Directory Structure

```mermaid
graph TB
    subgraph "Skills Directory"
        SkillsDir["./skills/"]
        SkillName["skill-name/"]
        SkillMD["SKILL.md"]
        SkillMeta["skill_meta.json"]
        RefsDir["references/"]
        ScriptsDir["scripts/"]
    end
    
    subgraph "Runs Directory"
        RunsDir["./runs/"]
        Batch["batch_YYYYMMDD_HHMMSS/"]
        Run1["run_1/"]
        RunMeta2["run_metadata.json"]
        RunRes["run_result.json"]
        BatchSum["batch_summary.json"]
    end
    
    SkillsDir --> SkillName
    SkillName --> SkillMD
    SkillName --> SkillMeta
    SkillName --> RefsDir
    SkillName --> ScriptsDir
    
    RunsDir --> Batch
    Batch --> Run1
    Run1 --> RunMeta2
    Run1 --> RunRes
    Batch --> BatchSum
```

Skills are saved using `Skill.save()` [src/upskill/models.py:100-139]() and loaded using `Skill.load()` [src/upskill/models.py:141-186]().

Run results are logged using functions in `logging.py`:
- `create_batch_folder()` [src/upskill/logging.py:27-47]() creates timestamped batch directories
- `create_run_folder()` [src/upskill/logging.py:50-60]() creates individual run directories
- `write_run_result()` [src/upskill/logging.py:80-93]() writes JSON result files
- `write_batch_summary()` [src/upskill/logging.py:273-282]() writes aggregate batch statistics

**Sources**: [src/upskill/models.py:100-186](), [src/upskill/logging.py:27-282](), [README.md:356-370](), Diagram 4 from context

---

## Dependencies and External Systems

### Core Dependencies

| Dependency | Purpose | Usage |
|------------|---------|-------|
| **fast-agent-mcp** | Agent orchestration, LLM providers, MCP support | Core runtime for executing agents |
| **pydantic** | Data validation and serialization | All data models in `models.py` |
| **click** | CLI framework | Command definitions in `cli.py` |
| **rich** | Terminal output formatting | Progress display, tables, panels |
| **pyyaml** | Configuration parsing | `config.yaml` and agent card frontmatter |

### Module Dependency Graph

```mermaid
graph TD
    subgraph "External"
        FastAgent["fast_agent"]
        Pydantic["pydantic"]
        Click["click"]
        Rich["rich"]
        YAML["pyyaml"]
    end
    
    subgraph "Core"
        Models["models.py"]
        Config["config.py"]
        ManifestUtils["manifest_utils.py"]
        FAIntegration["fastagent_integration.py"]
        Generate["generate.py"]
        Evaluate["evaluate.py"]
        Logging["logging.py"]
        CLI["cli.py"]
    end
    
    subgraph "Resources"
        AgentCards["agent_cards/"]
        ConfigFiles["config.yaml"]
    end
    
    Pydantic --> Models
    Models --> Config
    Models --> Generate
    Models --> Evaluate
    Models --> Logging
    Models --> CLI
    
    FastAgent --> ManifestUtils
    FastAgent --> Generate
    FastAgent --> Evaluate
    FastAgent --> CLI
    
    ManifestUtils --> Generate
    FAIntegration --> Evaluate
    Config --> CLI
    Logging --> CLI
    Generate --> CLI
    Evaluate --> CLI
    
    Click --> CLI
    Rich --> CLI
    YAML --> Config
    
    AgentCards -.->|loaded by| CLI
    ConfigFiles -.->|read by| Config
```

The system integrates with FastAgent through:
1. **Context manager**: `_fast_agent_context()` [src/upskill/cli.py:49-66]() initializes FastAgent and loads agent cards
2. **Agent instances**: Accessed via `agent.skill_gen`, `agent.test_gen`, `agent.evaluator`
3. **Skill composition**: `compose_instruction()` in `fastagent_integration.py` formats skills for agent consumption
4. **Message channels**: Uses `FAST_AGENT_USAGE` and `FAST_AGENT_TIMING` for metrics extraction

**Sources**: [pyproject.toml:1-38](), [src/upskill/cli.py:49-66](), Diagram 5 from context

---

## Configuration System

The system uses two configuration files:

### upskill Configuration

`~/.config/upskill/config.yaml` or `./upskill.config.yaml`:

```yaml
model: sonnet                    # Default generation model
eval_model: haiku               # Default evaluation model (optional)
skills_dir: ./skills            # Where to save skills
runs_dir: ./runs                # Where to save run logs
max_refine_attempts: 3          # Refinement iterations
```

Loaded via `Config.load()` [src/upskill/config.py:21-58]()

### FastAgent Configuration

`./fastagent.config.yaml`:

```yaml
default_model: sonnet

logger:
  progress_display: true
  show_chat: false
  streaming: markdown

# MCP servers (optional)
mcp:
  servers:
    fetch:
      command: "uvx"
      args: ["mcp-server-fetch"]
```

FastAgent automatically loads this configuration when initialized.

**Sources**: [src/upskill/config.py:1-70](), [README.md:374-423]()

---

## Summary

The upskill system provides a complete framework for automatically generating, evaluating, and refining agent skills. Its architecture separates concerns across four layers (interface, core, agent, storage) while maintaining clear data flow through well-defined Pydantic models. The teacher-student paradigm enables powerful models to create skills that improve the performance of less capable models, with comprehensive evaluation metrics ensuring skills provide measurable benefits.

Key architectural patterns:
- **Agent card declarative configuration** for flexible model substitution
- **Detached agent instances** for isolated test execution
- **Comprehensive metrics extraction** from FastAgent message channels
- **Iterative refinement loops** with plateau detection
- **Structured persistence** with both skill artifacts and evaluation logs

The system's modular design supports both CLI and programmatic usage, making it suitable for interactive development as well as automated pipelines.

**Sources**: All diagrams and sections above

---

