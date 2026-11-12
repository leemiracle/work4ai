<!-- source: DeepWiki mcp.deepwiki.com · repo browser-use/rl-env-use · page 6 RL Env Interface and Integrations · fetched 2026-10-30 -->

# RL Env Interface and Integrations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)

</details>



This page provides an overview of the programmatic surface, environment interfaces, and external integration components of `rl-env-use`. It covers how downstream RL trainers and evaluators interact with constructed environments, how model failure modes are judged, how baseline comparisons are performed, and how the test suite ensures correctness.

For deep technical details, see the child pages:
- [The Env API and Dataset Export](#6.1)
- [Judges, Checks and Vanilla Comparison](#6.2)
- [Testing](#6.3)

---

## 6.1 The Env API and Dataset Export

The programmatic interface for interacting with generated environments is centered around the `Env` class located in `rl_env_use/env.py` [README.md:28](). It manages environment initialization via directory structures (`env_dir`), dataset splits (`split`), and verified task filters (`verified`). 

The interface supports standard environment operations including `reset()`, reward computation, and full model rollouts while automatically handling public observation isolation and gold answer hiding to prevent data leakage during training. Additionally, environments support direct serialization to JSONL formats optimized for consumption by external reinforcement learning trainers.

For full details on API methods, state management, and export schemas, see [The Env API and Dataset Export](#6.1).

**Sources:**
- `README.md:28-28`

---

## 6.2 Judges, Checks and Vanilla Comparison

To evaluate model outputs reliably and detect reasoning or execution failures, `rl-env-use` provides calibrated failure-mode judges and structural checks. 

- **Judges (`rl_env_use/judges.py`)**: Implement automated evaluation logic to catch qualitative failures, formatting errors, and ungrounded claims.
- **Checks (`rl_env_use/checks.py`)**: Validate task consistency, numerical tolerances, and expected data schemas.
- **Vanilla Comparison (`rl_env_use/vanilla.py`)**: Provides A/B evaluation against unassisted or vanilla agent setups (such as standard Claude Code browsing sessions) via the `compare` command workflow.

For implementation specifics on prompt rubrics, check rules, and baseline comparison harnesses, see [Judges, Checks and Vanilla Comparison](#6.2).

**Sources:**
- `README.md:10-12`

---

## 6.3 Testing

The testing infrastructure under the `tests/` directory ensures robustness across all core modules, including task graders, scout parsers, hillclimbing loops, audit validators, and UI report generators. 

The test suite uses `conftest.py` and dedicated ground-truth fixtures to run offline unit tests (executing in seconds) alongside selective live integration tests for external API interactions.

For detailed test layouts, fixture definitions, and execution commands, see [Testing](#6.3).

**Sources:**
- `README.md:72-73`

---

## Architecture Diagrams

### Diagram 1: Environment Interface and Dataset Export Flow
Bridging natural language requests and environment configurations to programmatic Python classes and RL trainer datasets.

```mermaid
graph TD
    NL["NaturalLanguageEnvironmentSpec"] -->|scout/synth| CodeFiles["EnvironmentDirectoryFiles"]
    CodeFiles -->|loads spec and tasks| EnvClass["EnvClassInEnvPy"]
    EnvClass -->|exposes methods| ResetMethod["resetMethod"]
    EnvClass -->|exposes methods| RolloutMethod["rolloutMethod"]
    EnvClass -->|hides answers| PublicObs["PublicObservations"]
    EnvClass -->|serializes| JSONLExport["JSONLDatasetExport"]

    sub-graph Code Entity Space
        EnvClass
        ResetMethod
        RolloutMethod
        PublicObs
        JSONLExport
    end
```
Sources: `README.md:28-28`

### Diagram 2: Evaluation, Judges, and Vanilla Comparison Pipeline
Mapping evaluation workflows from model generation to calibrated judges and baseline comparisons.

```mermaid
graph TD
    TaskInput["NaturalLanguageTaskPrompt"] -->|executes policy| RolloutRunner["rolloutPyAndRunnerPy"]
    RolloutRunner -->|produces results| ResultsJSONL["resultsJsonlRecord"]
    ResultsJSONL -->|evaluated by| JudgeModule["judgesPyCalibratedJudges"]
    ResultsJSONL -->|validated by| CheckModule["checksPyStructuralChecks"]
    ResultsJSONL -->|compared via| VanillaCompare["vanillaPyCompareCommand"]

    sub-graph Code Entity Space
        RolloutRunner
        ResultsJSONL
        JudgeModule
        CheckModule
        VanillaCompare
    end
```
Sources: `README.md:10-12`, `README.md:28-28`

---

