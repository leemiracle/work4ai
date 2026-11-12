<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/SkillOpt · page 1 SkillOpt Overview · fetched 2026-10-26 -->

# SkillOpt Overview

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [docs/contributing.md](docs/contributing.md)
- [docs/guide/dl-analogy.md](docs/guide/dl-analogy.md)
- [docs/guide/first-experiment.md](docs/guide/first-experiment.md)
- [docs/guide/skill-document.md](docs/guide/skill-document.md)
- [docs/guide/training-loop.md](docs/guide/training-loop.md)
- [docs/index.md](docs/index.md)
- [docs/review_guidelines.md](docs/review_guidelines.md)
- [index.html](index.html)
- [mkdocs.yml](mkdocs.yml)
- [skillopt-assets/arxiv-logomark-small.svg](skillopt-assets/arxiv-logomark-small.svg)
- [skillopt.html](skillopt.html)

</details>



SkillOpt is a framework for training natural-language "skills" for frozen Large Language Model (LLM) agents using an optimization paradigm inspired by deep learning. Rather than fine-tuning model weights, SkillOpt treats a Markdown skill document as the trainable parameter state and uses an LLM-based optimizer to perform iterative text-space updates based on task performance [README.md:31-38]().

For installation, initial experiments, configuration parameters, and detailed tutorials, see the child pages:
- **[Getting Started](#1.1)** — Installation, environment variables, SearchQA walkthrough, and WebUI dashboard.
- **[Deep Learning Analogy](#1.2)** — Systematic mapping between deep learning concepts and SkillOpt counterparts.
- **[Documentation Site and Repository Layout](#1.3)** — Structure of `docs/`, `data/`, and `ckpt/` paths.

## Core Concept: Text-Space Optimization

SkillOpt bridges manual prompt engineering and automated fine-tuning by introducing a structured training loop where an optimizer model analyzes agent trajectories and applies textual edit patches to a skill document. This process mirrors neural network training—incorporating epochs, batch sizes, learning rates, and validation gates—entirely within natural language space [README.md:31-38]().

**System Architecture Mapping**
```mermaid
graph TD
    subgraph "NaturalLanguageSpace"
        SkillDoc[""Skill Document (.md)""]
        Trajectories[""Trajectories (conversation.json)""]
        Patch[""Patch (Edit list)""]
    end

    subgraph "CodeEntitySpace"
        direction LR
        TargetModel[""Target Model""] -->|"Rollout"| Trainer[""skillopt.trainer.ReflACTTrainer""]
        Trainer -->|"Analyze"| OptimizerModel[""Optimizer Model""]
        Trainer -->|"skillopt.types.Edit"| Patch
        Trainer -->|"skillopt.types.RolloutResult"| Trajectories
        
        subgraph "Backends"
            AzureBackend[""skillopt.model.azure_openai_backend""]
            CompatibleBackend[""skillopt.model.openai_compatible_backend""]
        end
    end

    SkillDoc -.->|"Input"| TargetModel
    Trajectories -.->|"Feedback"| OptimizerModel
    OptimizerModel -.->|"Generates"| Patch
    Patch -.->|"Updates"| SkillDoc
```
Sources: [skillopt/types.py:126-160](), [skillopt/envs/base.py:51-65](), [docs/guide/skill-document.md:1-20]()

## Repository Organization

The codebase isolates training orchestrators, model backend integrations, environment adapters, and offline evolution pipelines:

*   `skillopt/`: Core library containing the `ReflACT` trainer and loop logic.
*   `skillopt/model/`: Implements the model router and backend adapters (`azure_openai`, `openai_compatible`, `claude`, etc.) [docs/reference/api.md:180-195]().
*   `skillopt/envs/`: Contains `EnvAdapter` implementations and benchmark definitions [docs/reference/api.md:16-25]().
*   `skillopt_webui/`: Gradio interface for training visualization [README.md:84-91]().
*   `skillopt_sleep/`: Nightly offline self-evolution companion engine [README.md:17-18]().
*   `scripts/`: Command-line entry points including `train.py` and `eval_only.py` [docs/index.md:143-168]().
*   `configs/`: YAML configuration hierarchies [docs/guide/configuration.md:7-17]().

Sources: [README.md:62-83](), [docs/index.md:21-30]()

## Supported Benchmarks

SkillOpt includes built-in adapters for six diverse benchmarks covering information retrieval, embodied agents, visual QA, and code generation.

| Benchmark | Type | Description | Config Path |
|---|---|---|---|
| **SearchQA** | Text QA | Information retrieval and question answering | `configs/searchqa/` |
| **ALFWorld** | Embodied | Interactive pick-and-place simulator tasks | `configs/alfworld/` |
| **DocVQA** | Visual QA | Document image understanding and question answering | `configs/docvqa/` |
| **LiveMathematicianBench** | Reasoning | Complex mathematical problem solving | `configs/livemathematicianbench/` |
| **SpreadsheetBench** | Code Gen | Spreadsheet editing and code execution | `configs/spreadsheetbench/` |
| **OfficeQA** | Tool-Use | Tool-augmented enterprise productivity tasks | `configs/officeqa/` |

Sources: [docs/index.md:114-124](), [docs/guide/first-experiment.md:5-18]()

## Training Workflow

Training is managed via `ReflACTTrainer` through a six-stage step execution loop alongside epoch boundary updates [docs/guide/training-loop.md:7-24]().

1.  **Rollout**: Target executes tasks using the active skill document.
2.  **Reflect**: Optimizer analyzes trajectory minibatches to produce `Edit` patches.
3.  **Aggregate**: Semantically similar edit patches are merged.
4.  **Select**: Edits are ranked and clipped by the `learning_rate` budget.
5.  **Update**: Selected patches are applied to the skill document.
6.  **Gate**: The candidate skill is evaluated on a selection split via `GateResult` and accepted only on strict score improvement.

**Optimization Loop to Code Entity Mapping**
```mermaid
graph LR
    subgraph "OptimizationPhase"
        direction TB
        StepNode[""Training Step""]
        GateNode[""Validation Gate""]
        EpochNode[""Epoch Boundary""]
    end

    subgraph "CodeImplementation"
        direction TB
        FnStep[""ReflACTTrainer.step()""]
        FnGate[""skillopt.evaluation.gate.GateResult""]
        FnSlow[""ReflACTTrainer.slow_update()""]
    end

    StepNode --> FnStep
    GateNode --> FnGate
    EpochNode --> FnSlow
    
    FnStep -.->|"Calls"| FnGate
```
Sources: [docs/guide/training-loop.md:26-101](), [docs/reference/api.md:162-167]()

## Related Child Sections

For detailed technical guides and parameters, refer to the corresponding child pages:
- Installation and execution tutorials: **[Getting Started](#1.1)**
- Theoretical mappings: **[Deep Learning Analogy](#1.2)**
- Repository layout and documentation build: **[Documentation Site and Repository Layout](#1.3)**

---

