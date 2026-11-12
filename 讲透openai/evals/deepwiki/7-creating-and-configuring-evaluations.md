<!-- source: DeepWiki mcp.deepwiki.com · repo openai/evals · page 7 Creating and Configuring Evaluations · fetched 2026-10-26 -->

# Creating and Configuring Evaluations

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.github/config.yml](.github/config.yml)
- [Makefile](Makefile)
- [README.md](README.md)
- [docs/build-eval.md](docs/build-eval.md)
- [docs/completion-fn-protocol.md](docs/completion-fn-protocol.md)
- [docs/completion-fns.md](docs/completion-fns.md)
- [docs/custom-eval.md](docs/custom-eval.md)
- [evals/cli/oaievalset.py](evals/cli/oaievalset.py)
- [evals/data.py](evals/data.py)
- [evals/data_test.py](evals/data_test.py)
- [evals/record.py](evals/record.py)
- [evals/record_test.py](evals/record_test.py)
- [evals/registry/data/README.md](evals/registry/data/README.md)
- [evals/registry/data/logic/samples.jsonl](evals/registry/data/logic/samples.jsonl)
- [evals/registry/data/pattern_identification/samples.v0.jsonl](evals/registry/data/pattern_identification/samples.v0.jsonl)
- [evals/registry/evals/pattern_identification.yaml](evals/registry/evals/pattern_identification.yaml)
- [evals/utils/misc.py](evals/utils/misc.py)
- [mypy.ini](mypy.ini)
- [scripts/battle_generator.py](scripts/battle_generator.py)
- [scripts/modelgraded_generator.py](scripts/modelgraded_generator.py)
- [scripts/pattern_identification_generator.py](scripts/pattern_identification_generator.py)

</details>



## Purpose and Scope

This page provides a comprehensive guide to creating and configuring new evaluations in the OpenAI Evals framework. It covers the end-to-end workflow from conceptualizing an evaluation to registering it in the system and making it executable via the CLI.

This page focuses on the **overall process and system architecture** for creating evaluations. For detailed information on specific aspects:
- For data format specifications and data management, see [Data Preparation](#7.1)
- For detailed YAML configuration schemas and registry organization, see [Registry Configuration](#7.2)
- For automated eval generation tools and scripts, see [Generator Scripts](#7.3)
- For implementing custom evaluation logic beyond templates, see [Custom Evaluation Implementation](#6.4)
- For running evaluations once configured, see [Using oaieval CLI](#5.1)

**Note:** The framework currently does not accept contributions with custom code [README.md:75-75](). However, you can still create and submit model-graded evaluations with custom YAML configurations [docs/build-eval.md:3-4]().

## Overview: The Three-Component System

Every evaluation in the framework consists of three components:

1. **Data Files** - JSONL files containing evaluation samples [docs/build-eval.md:23-24]().
2. **YAML Configuration** - Registry entries defining evaluation parameters [docs/build-eval.md:42-43]().
3. **Evaluation Class** (optional) - Python implementation if using custom logic [docs/custom-eval.md:28-30]().

```mermaid
graph TB
    subgraph "Component 1: Data Files"
        DataFile["samples.jsonl<br/>evals/registry/data/{eval_name}/"]
        DataFormat["Format: One JSON object per line<br/>Keys: input, ideal, etc."]
    end
    
    subgraph "Component 2: YAML Registry"
        EvalYAML["evals/registry/evals/{eval_name}.yaml"]
        EvalEntry1["{eval_name}<br/>id, metrics, description"]
        EvalEntry2["{eval_name}.{split}.{version}<br/>class, args"]
    end
    
    subgraph "Component 3: Evaluation Class (Optional)"
        TemplateClass["Built-in Templates<br/>Match, ModelBasedClassify, etc."]
        CustomClass["Custom Implementation<br/>evals.elsuite.{module}:{Class}"]
    end
    
    subgraph "CLI Execution"
        CLI["oaieval gpt-4 {eval_name}"]
    end
    
    DataFile --> DataFormat
    EvalYAML --> EvalEntry1
    EvalEntry1 --> EvalEntry2
    
    EvalEntry2 -.references.-> DataFile
    EvalEntry2 -.instantiates.-> TemplateClass
    EvalEntry2 -.instantiates.-> CustomClass
    
    CLI --> EvalEntry1
    CLI --> TemplateClass
    CLI --> CustomClass
    
    TemplateClass --> DataFile
    CustomClass --> DataFile
```

Sources: [docs/build-eval.md:1-98](), [README.md:66-98]()

## Evaluation Creation Workflow

The following diagram shows the complete workflow for creating and registering a new evaluation:

```mermaid
flowchart TD
    Start["Start: Define Evaluation Goal"]
    
    ChooseType{"Choose<br/>Evaluation Type"}
    
    UseTemplate["Use Existing Template<br/>Match, Includes, ModelBasedClassify"]
    CustomCode["Implement Custom Logic<br/>Inherit from evals.Eval"]
    
    PrepareData["Prepare Data<br/>Convert to JSONL format<br/>Define keys: input, ideal, etc."]
    
    PlaceData["Place Data File<br/>evals/registry/data/{eval_name}/samples.jsonl"]
    
    CreateYAML["Create YAML Configuration<br/>evals/registry/evals/{eval_name}.yaml"]
    
    DefineBase["Define Base Eval Entry<br/>{eval_name}:<br/>  id: {eval_name}.dev.v0<br/>  metrics: [accuracy]"]
    
    DefineVersion["Define Version Entry<br/>{eval_name}.dev.v0:<br/>  class: path.to:Class<br/>  args:<br/>    samples_jsonl: {eval_name}/samples.jsonl"]
    
    TestLocal["Test Locally<br/>oaieval gpt-3.5-turbo {eval_name}"]
    
    CheckResults{"Results<br/>Acceptable?"}
    
    Iterate["Iterate:<br/>- Adjust prompt engineering<br/>- Modify data<br/>- Tune parameters"]
    
    MetaEval["(Optional) Create Meta-Eval<br/>For model-graded evals"]
    
    Done["Ready for Use/Contribution"]
    
    Start --> ChooseType
    
    ChooseType -->|"Basic/Model-Graded"| UseTemplate
    ChooseType -->|"Complex Logic"| CustomCode
    
    UseTemplate --> PrepareData
    CustomCode --> PrepareData
    
    PrepareData --> PlaceData
    PlaceData --> CreateYAML
    
    CreateYAML --> DefineBase
    DefineBase --> DefineVersion
    
    DefineVersion --> TestLocal
    TestLocal --> CheckResults
    
    CheckResults -->|"No"| Iterate
    Iterate --> PrepareData
    
    CheckResults -->|"Yes"| MetaEval
    MetaEval --> Done
```

Sources: [docs/build-eval.md:6-93](), [docs/custom-eval.md:1-156]()

## Naming Conventions and Registry Structure

The registry follows a strict hierarchical naming convention that enables version management and organization:

### Naming Pattern

The naming convention for evals is in the form `<eval_name>.<split>.<version>` [docs/build-eval.md:57-57]().

| Component | Description | Examples |
|-----------|-------------|----------|
| `<eval_name>` | Base evaluation name, groups comparable evals | `coqa-match`, `joke-fruits`, `arithmetic` |
| `<split>` | Data split identifier (e.g., "val", "test", or "dev") | `dev`, `val`, `test`, `train` |
| `<version>` | Version identifier (avoid `.` in version) | `v0`, `v1`, `match-v1` |

### Registry File Organization

The `Registry` class [evals/cli/oaievalset.py:11-11]() resolves paths within `evals/registry/`.

```mermaid
graph TB
    subgraph "evals/registry/"
        EvalDir["evals/"]
        DataDir["data/"]
        CompFnDir["completion_fns/"]
        SolverDir["solvers/"]
        MGDir["modelgraded/"]
        EvalSetDir["eval_sets/"]
    end
    
    subgraph "evals/ (Evaluation Definitions)"
        EvalFile1["{eval_name}.yaml"]
        EvalFile2["test-modelgraded.yaml"]
        EvalFile3["coqa-ex.yaml"]
    end
    
    subgraph "data/ (Sample Data)"
        DataSubdir["{eval_name}/"]
        SamplesFile["samples.jsonl"]
        VariantFile["samples.v1.jsonl"]
    end
    
    subgraph "modelgraded/ (Grading Specs)"
        MGFile1["fact.yaml"]
        MGFile2["closedqa.yaml"]
        MGFile3["humor.yaml"]
    end
    
    subgraph "eval_sets/ (Eval Collections)"
        SetFile["test-all.yaml"]
    end
    
    EvalDir --> EvalFile1
    EvalDir --> EvalFile2
    EvalDir --> EvalFile3
    
    DataDir --> DataSubdir
    DataSubdir --> SamplesFile
    DataSubdir --> VariantFile
    
    MGDir --> MGFile1
    MGDir --> MGFile2
    MGDir --> MGFile3
    
    EvalSetDir --> SetFile
    
    EvalFile1 -.references.-> SamplesFile
    EvalFile2 -.references.-> MGFile1
```

Sources: [docs/build-eval.md:40-63](), [evals/registry/data/README.md:1-34](), [scripts/modelgraded_generator.py:6-6]()

## YAML Configuration Structure

### Basic Evaluation Example

The YAML configuration has two levels: a base entry (alias) and a version entry [docs/custom-eval.md:109-128]().

```yaml
# Base eval entry (alias)
coqa-match:
  id: coqa-match.dev.v0
  metrics: [accuracy]
  description: CoQA dataset with exact matching

# Version entry (concrete implementation)
coqa-match.dev.v0:
  class: evals.elsuite.basic.match:Match
  args:
    samples_jsonl: coqa/match.jsonl
```

| Field | Level | Required | Description |
|-------|-------|----------|-------------|
| `id` | Base | Yes | Points to the concrete version to use |
| `metrics` | Base | Yes | List of metrics to compute (first is primary) |
| `description` | Base | No | Human-readable description |
| `class` | Version | Yes | Python class path `module.path:ClassName` |
| `args` | Version | Yes | Arguments passed to class constructor |

Sources: [docs/build-eval.md:40-53](), [docs/custom-eval.md:102-128]()

### Model-Graded Evaluation Example

Model-graded evaluations reference a `modelgraded_spec` and specify an `eval_type` [docs/build-eval.md:76-80]().

```yaml
mg-humor-fruits:
  id: mg-humor-fruits.dev.v0
  metrics: [accuracy]

mg-humor-fruits.dev.v0:
  class: evals.elsuite.modelgraded.classify:ModelBasedClassify
  args:
    samples_jsonl: test_modelgraded/humor_fruits.jsonl
    eval_type: cot_classify_jp
    modelgraded_spec: humor_jp
```

Sources: [scripts/modelgraded_generator.py:18-28](), [docs/build-eval.md:76-80]()

## Class Path Resolution

The `class` field in YAML uses Python's dotted import notation to resolve to an implementation of `evals.Eval` [docs/custom-eval.md:28-28]().

```mermaid
graph LR
    YAML["class: evals.elsuite.basic.match:Match"]
    
    Module["Module Path:<br/>evals.elsuite.basic.match"]
    Class["Class Name:<br/>Match"]
    
    File["Resolves to File:<br/>evals/elsuite/basic/match.py"]
    ClassDef["class Match(evals.Eval):<br/>    ..."]
    
    YAML --> Module
    YAML --> Class
    
    Module --> File
    Class --> ClassDef
    
    File --> ClassDef
```

Common class paths:

| Template Type | Class Path |
|---------------|------------|
| Match | `evals.elsuite.basic.match:Match` |
| ModelBasedClassify | `evals.elsuite.modelgraded.classify:ModelBasedClassify` [scripts/modelgraded_generator.py:23-23]() |
| Custom | `evals.elsuite.{your_module}:{YourClass}` |

Sources: [docs/build-eval.md:40-53](), [docs/custom-eval.md:102-128]()

## Data File Format and Requirements

### Required JSONL Structure

Data files must be in JSONL format, with one JSON object per line [docs/build-eval.md:23-24](). The `evals.data` module provides utilities like `get_jsonl` [evals/data.py:120-120]() and `iter_jsonls` [evals/data.py:146-146]() to process these files.

### Common Keys by Evaluation Type

| Eval Type | Required Keys | Optional Keys | Example |
|-----------|---------------|---------------|---------|
| Match/FuzzyMatch | `input`, `ideal` | | `{"input": "Q?", "ideal": "A"}` [evals/registry/data/README.md:9-9]() |
| ModelBasedClassify (single) | `input` | `ideal` (for meta-eval) | `{"input": "..."}` [scripts/modelgraded_generator.py:190-190]() |
| ModelBasedClassify (battle) | `input1`, `input2` | | `{"input1": "...", "input2": "..."}` [scripts/battle_generator.py:56-57]() |

### Chat Format for Input

The `input` field should use chat format (list of role/content dictionaries) for best compatibility [docs/build-eval.md:32-32]().

```json
{
  "input": [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
  ],
  "ideal": "Paris"
}
```

Sources: [docs/build-eval.md:21-38](), [evals/registry/data/README.md:8-34]()

## Mapping: YAML Args to Class Constructor

The `args` dictionary in YAML is unpacked and passed to the evaluation class constructor [docs/custom-eval.md:39-44]().

```mermaid
graph TB
    subgraph "YAML Configuration"
        YAMLArgs["args:<br/>  train_jsonl: arithmetic/train.jsonl<br/>  test_jsonl: arithmetic/test.jsonl<br/>  train_samples_per_prompt: 2"]
    end
    
    subgraph "Python Class"
        Constructor["def __init__(self,<br/>    train_jsonl,<br/>    test_jsonl,<br/>    train_samples_per_prompt=2,<br/>    **kwargs):<br/>    super().__init__(**kwargs)<br/>    self.train_jsonl = train_jsonl<br/>    ..."]
    end
    
    subgraph "Base Class (evals.Eval)"
        BaseInit["def __init__(self,<br/>    **kwargs):<br/>    ..."]
    end
    
    YAMLArgs -->|"Unpacked as kwargs"| Constructor
    Constructor -->|"Remaining **kwargs"| BaseInit
```

Sources: [docs/custom-eval.md:39-44](), [docs/build-eval.md:40-53]()

## Testing Your Evaluation

### Local Testing Process

1. **Install in editable mode**:
   ```bash
   pip install -e .
   ```
   Changes to your eval will be reflected immediately without reinstalling [README.md:39-42]().

2. **Run the evaluation**:
   ```bash
   oaieval gpt-3.5-turbo <eval_name>
   ```

3. **Review output**:
   The `RecorderBase` logs events [evals/record.py:54-54](). You can find results in local JSON files or Snowflake if configured [README.md:64-64]().

### Resume Mode

Use `oaievalset` to run multiple evaluations and resume from checkpoints if interrupted [evals/cli/oaievalset.py:59-63]().

Sources: [README.md:39-42](), [evals/cli/oaievalset.py:111-129](), [docs/custom-eval.md:133-156]()

## Generator Scripts for Scale

For creating large numbers of similar evaluations, generator scripts automate YAML and data file creation.

- **`modelgraded_generator.py`**: Generates `ModelBasedClassify` evals based on subjects and prompts [scripts/modelgraded_generator.py:188-214]().
- **`battle_generator.py`**: Creates pairwise "battle" evaluations between different subjects [scripts/battle_generator.py:52-70]().
- **`pattern_identification_generator.py`**: Generates synthetic pattern-matching tasks with system/user chat prompts [scripts/pattern_identification_generator.py:54-70]().

Sources: [scripts/modelgraded_generator.py:1-219](), [scripts/battle_generator.py:1-76](), [scripts/pattern_identification_generator.py:1-71]()

## Quality Criteria Checklist

Before submitting an evaluation, verify these criteria [docs/build-eval.md:83-93]():

- [ ] **Data Format**: Samples are valid JSONL and use chat format where possible.
- [ ] **Registry**: YAML is correctly placed in `evals/registry/evals/`.
- [ ] **Versioning**: Follows `<eval_name>.<split>.<version>` convention.
- [ ] **Metrics**: Primary metric is defined in the base eval entry.
- [ ] **Meta-Eval**: Model-graded evals include human-provided labels (choice keys) for verification [docs/build-eval.md:79-80]().
- [ ] **LFS**: Data files are tracked via Git LFS [README.md:19-24]().

Sources: [docs/build-eval.md:57-93](), [README.md:19-24]()

---

