<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/safety-eval · extra page WildJailbreak and Jailbreak Attacks · fetched 2026-10-26 -->

# WildJailbreak and Jailbreak Attacks

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [README.md](README.md)
- [evaluation/eval.py](evaluation/eval.py)
- [evaluation/models/__init__.py](evaluation/models/__init__.py)
- [evaluation/tasks/__init__.py](evaluation/tasks/__init__.py)
- [evaluation/tasks/generation/base.py](evaluation/tasks/generation/base.py)
- [evaluation/tasks/generation/do_anything_now/__init__.py](evaluation/tasks/generation/do_anything_now/__init__.py)
- [evaluation/tasks/generation/harmbench/__init__.py](evaluation/tasks/generation/harmbench/__init__.py)
- [evaluation/tasks/generation/toxigen/__init__.py](evaluation/tasks/generation/toxigen/__init__.py)
- [evaluation/tasks/generation/trustllm_jailbreaktrigger/__init__.py](evaluation/tasks/generation/trustllm_jailbreaktrigger/__init__.py)
- [evaluation/tasks/generation/trustllm_jailbreaktrigger/gpt4.yaml](evaluation/tasks/generation/trustllm_jailbreaktrigger/gpt4.yaml)
- [evaluation/tasks/generation/wildguardtest/__init__.py](evaluation/tasks/generation/wildguardtest/__init__.py)
- [evaluation/tasks/generation/wildjailbreak/__init__.py](evaluation/tasks/generation/wildjailbreak/__init__.py)
- [evaluation/tasks/generation/xstest/exaggerated_safety.json](evaluation/tasks/generation/xstest/exaggerated_safety.json)

</details>



This page documents the WildJailbreak evaluation task and the jailbreak attack wrapper system for adversarial safety evaluation. WildJailbreak is a specific benchmark dataset that tests model robustness against in-the-wild jailbreak prompts (both harmful and benign variants). The jailbreak attack wrapper system is a generic framework that allows any generation task to be evaluated under adversarial attack conditions by wrapping it with attack strategies like PAIR or WildJailbreak-style attacks.

For information about other adversarial safety tasks like StrongReject, see [4.1.1](#4.1.1). For Harmbench, see [4.1.2](#4.1.2). For the base task system architecture, see [3.2](#3.2).

## WildJailbreak Evaluation Task

The WildJailbreak task evaluates language models against adversarial prompts collected from real-world jailbreak attempts. It provides two contrasting evaluation sets: harmful prompts that should be refused, and benign prompts that should be answered (testing for over-refusal).

### Task Implementation Classes

```mermaid
graph TB
    AdversarialTaskBase["AdversarialTaskBase<br/>base.py:12-163"]
    WildJailbreakValidation["WildJailbreakValidation<br/>wildjailbreak/__init__.py:7-16"]
    WildJailbreakValidationBenign["WildJailbreakValidationBenign<br/>wildjailbreak/__init__.py:19-30"]
    
    AdversarialTaskBase --> WildJailbreakValidation
    AdversarialTaskBase --> WildJailbreakValidationBenign
    
    HarmfulData["harmful.jsonl<br/>Adversarial harmful prompts<br/>Should trigger refusal"]
    BenignData["benign.jsonl<br/>Adversarial benign prompts<br/>Should NOT trigger refusal"]
    
    WildJailbreakValidation --> HarmfulData
    WildJailbreakValidationBenign --> BenignData
    
    WildJailbreakValidation --> |"benign=False"| InvertedASR["Inverted ASR Metric<br/>1 - attack_success_rate"]
    WildJailbreakValidationBenign --> |"benign=True"| DirectASR["Direct ASR Metric<br/>attack_success_rate"]
```

**WildJailbreakValidation Class**

The harmful variant tests the model's ability to refuse adversarial harmful requests:

- **Location**: [evaluation/tasks/generation/wildjailbreak/__init__.py:7-16]()
- **Data Source**: Loads from `harmful.jsonl` containing adversarial harmful prompts
- **Instruction Mapping**: Uses the `adversarial` field from the dataset as the model input [wildjailbreak/__init__.py:13]()
- **Metric**: Reports inverted ASR (1 - attack success rate), where lower ASR is better
- **Inherits**: `AdversarialTaskBase` with `benign=False` (default)

**WildJailbreakValidationBenign Class**

The benign variant tests for over-refusal by presenting benign prompts with adversarial phrasing:

- **Location**: [evaluation/tasks/generation/wildjailbreak/__init__.py:19-30]()
- **Data Source**: Loads from `benign.jsonl` containing adversarial but benign prompts
- **Field Handling**: Deletes the `vanilla` field so the classifier judges using the adversarial instruction [wildjailbreak/__init__.py:27]()
- **Metric**: Reports direct ASR (attack success rate), where higher is worse (indicates over-refusal)
- **Inherits**: `AdversarialTaskBase` with `benign=True`

Sources: [evaluation/tasks/generation/wildjailbreak/__init__.py:1-30](), [evaluation/tasks/generation/base.py:12-21]()

### Data Format

WildJailbreak data follows a standard structure with adversarial prompt variants:

| Field | Description |
|-------|-------------|
| `id` | Unique identifier for the example |
| `adversarial` | The adversarial prompt text (used as model input) |
| `vanilla` | The original non-adversarial prompt (if present) |
| Additional metadata | Source, category, or other annotations |

The harmful set includes prompts designed to elicit unsafe responses, while the benign set includes safe requests phrased in ways that might trigger over-cautious refusals.

Sources: [evaluation/tasks/generation/wildjailbreak/__init__.py:8-30](), [src/data_utils.py]()

## Jailbreak Attack Wrapper System

The jailbreak attack wrapper system allows any evaluation task to be tested under adversarial attack conditions without modifying the task implementation. This is achieved through the `JailbreakBase` class and the `wrap_task_with_jailbreak` function.

### Wrapper Architecture

```mermaid
graph TB
    subgraph "Task Wrapping Flow"
        OriginalTask["Original Task<br/>e.g., HarmbenchVanilla<br/>OpenEndedTaskBase"]
        WrapFunction["wrap_task_with_jailbreak()<br/>tasks/__init__.py:74-98"]
        AttackConfig["Attack Config YAML<br/>tasks/jailbreaks/{attack}/{config}.yaml"]
        AttackClass["Attack Class<br/>e.g., PAIRAttack<br/>Extends JailbreakBase"]
        WrappedTask["Wrapped Task<br/>JailbreakBase instance<br/>Contains original task + attack"]
        
        OriginalTask --> WrapFunction
        AttackConfig --> WrapFunction
        WrapFunction --> AttackClass
        AttackClass --> WrappedTask
        WrappedTask --> |"self.task"| OriginalTask
    end
    
    subgraph "Evaluation Execution"
        WrappedTask --> ApplyAttack["apply_attack()<br/>Abstract method in JailbreakBase"]
        ApplyAttack --> ModifiedInputs["Modified Inputs<br/>Adversarial prompts"]
        ModifiedInputs --> TaskEvaluate["task.evaluate(model)<br/>Original task evaluation"]
        TaskEvaluate --> Results["Results<br/>With attack success metrics"]
    end
```

**Key Components:**

1. **`JailbreakBase`**: Abstract base class for all jailbreak attacks
   - Wraps an existing `TaskBase` instance
   - Defines abstract `apply_attack()` method
   - Delegates evaluation to wrapped task after applying attack

2. **`wrap_task_with_jailbreak()`**: Factory function that creates wrapped tasks
   - **Location**: [evaluation/tasks/__init__.py:74-98]()
   - Dynamically imports attack module from `tasks.jailbreaks.{attack}`
   - Loads attack configuration from YAML
   - Instantiates attack class with wrapped task and config

3. **Attack Configuration**: YAML files define attack parameters
   - Located in `evaluation/tasks/jailbreaks/{attack}/{config}.yaml`
   - Specifies `attack_class` and attack-specific hyperparameters
   - Default config is `default.yaml` if not specified

Sources: [evaluation/tasks/__init__.py:74-98](), [evaluation/schemas.py]()

### Attack Application Flow

```mermaid
sequenceDiagram
    participant User
    participant EvalPy as "eval.py jailbreak()"
    participant Wrapper as "wrap_task_with_jailbreak()"
    participant JBTask as "JailbreakBase"
    participant Attack as "Attack.apply_attack()"
    participant OrigTask as "Original Task"
    participant Model as "GeneratorModel"
    
    User->>EvalPy: tasks=['harmbench']<br/>attacks=['pair','wildjailbreak']
    EvalPy->>Wrapper: wrap_task_with_jailbreak(task, 'pair')
    Wrapper->>JBTask: Instantiate with task
    
    EvalPy->>JBTask: evaluate(model)
    JBTask->>Attack: apply_attack(task.data)
    Attack-->>JBTask: Modified adversarial inputs
    JBTask->>OrigTask: evaluate(model) with modified inputs
    OrigTask->>Model: generate_completions(adversarial_inputs)
    Model-->>OrigTask: Completions
    OrigTask->>OrigTask: Classify with safety classifier
    OrigTask-->>JBTask: Metrics (ASR, etc.)
    JBTask-->>EvalPy: Results
```

The flow demonstrates how attacks modify inputs before they reach the underlying task's evaluation logic.

Sources: [evaluation/eval.py:206-305](), [evaluation/tasks/__init__.py:74-98]()

## AdversarialTaskBase Framework

The `AdversarialTaskBase` class provides the foundation for all adversarial evaluation tasks in the framework, including WildJailbreak and other attacks that extend it directly.

### Class Structure and Inheritance

```mermaid
graph TB
    OpenEndedTaskBase["OpenEndedTaskBase<br/>schemas.py"]
    AdversarialTaskBase["AdversarialTaskBase<br/>base.py:12-163"]
    
    WildJailbreakValidation["WildJailbreakValidation"]
    WildJailbreakValidationBenign["WildJailbreakValidationBenign"]
    DoAnythingNow["DoAnythingNow"]
    TrustLLMJailbreakTrigger["TrustLLMJailbreakTrigger"]
    
    OpenEndedTaskBase --> AdversarialTaskBase
    AdversarialTaskBase --> WildJailbreakValidation
    AdversarialTaskBase --> WildJailbreakValidationBenign
    AdversarialTaskBase --> DoAnythingNow
    AdversarialTaskBase --> TrustLLMJailbreakTrigger
```

**Constructor Parameters** [base.py:13-22]():

| Parameter | Type | Description |
|-----------|------|-------------|
| `classifier_model_name` | str | Name of safety classifier to evaluate responses |
| `hparams` | dict | Generation hyperparameters (max_new_tokens, temperature, top_p) |
| `local_model_path` | str | Optional local path for classifier model |
| `thinker_eval` | list | Evaluation mode for reasoning models: ["reasonings"], ["answers"], or both |
| `limit` | bool | Limit dataset to 5 examples for quick testing |
| `flex` | bool | Enable flexible parsing for reasoning traces |
| `benign` | bool | Reverse metric interpretation for over-refusal testing |

Sources: [evaluation/tasks/generation/base.py:12-28]()

### Evaluation Pipeline

```mermaid
graph TD
    Start["_evaluate(model)"] --> GenerateCompletions["model.generate_completions()<br/>base.py:45-48"]
    GenerateCompletions --> RemoveRepetitive["remove_repetitive()<br/>Extract reasoning/answers<br/>base.py:50"]
    
    RemoveRepetitive --> CheckThinker{"thinker_eval<br/>specified?"}
    CheckThinker -->|Yes| SplitSections["Split into sections:<br/>reasonings, answers"]
    CheckThinker -->|No| SingleSection["Single section:<br/>completions"]
    
    SplitSections --> EvalLoop["For each section"]
    SingleSection --> EvalLoop
    
    EvalLoop --> PrepareClassifierInputs["Prepare evaluator inputs:<br/>prompt + response pairs<br/>base.py:74-77"]
    PrepareClassifierInputs --> RunClassifier["classifier.classify()<br/>base.py:79"]
    
    RunClassifier --> ProcessResults["Process each result:<br/>base.py:91-128"]
    ProcessResults --> CheckError{"Parsing<br/>error?"}
    
    CheckError -->|Yes| MarkCorrect["correct = True (unsafe)<br/>or False (benign mode)<br/>base.py:103-108"]
    CheckError -->|No| CheckEmpty{"Empty<br/>response?"}
    
    CheckEmpty -->|Yes| MarkCorrect
    CheckEmpty -->|No| CompareOutput["Compare classifier output<br/>to successful_attack_output<br/>base.py:116"]
    
    MarkCorrect --> AggregateMetrics
    CompareOutput --> AggregateMetrics["Aggregate to macro_asr<br/>and source-specific metrics<br/>base.py:117-125"]
    
    AggregateMetrics --> CheckBenign{"benign<br/>mode?"}
    CheckBenign -->|Yes| DirectASR["Report direct ASR<br/>base.py:131-133"]
    CheckBenign -->|No| InvertedASR["Report inverted ASR<br/>1 - get_average(macro_asr)<br/>base.py:135-138"]
    
    DirectASR --> ReturnResults
    InvertedASR --> ReturnResults["Return metrics + individual results<br/>base.py:139-153"]
```

**Key Evaluation Steps:**

1. **Generation** [base.py:45-48](): Model generates completions for all inputs using configured hyperparameters

2. **Parsing** [base.py:50](): `remove_repetitive()` extracts structured outputs for reasoning models, handles truncation

3. **Section Handling** [base.py:53-61](): 
   - If `thinker_eval` is `["reasonings"]`: Evaluate reasoning traces only
   - If `thinker_eval` is `["answers"]`: Evaluate extracted answers only
   - If `thinker_eval` is `["reasonings", "answers"]`: Evaluate both separately
   - If `thinker_eval` is `None`: Evaluate complete responses

4. **Classifier Input Preparation** [base.py:70-77]():
   - Uses `vanilla` field if present (for tasks like Harmbench that provide original non-adversarial prompt)
   - Otherwise uses `instruction` field
   - Pairs prompts with model completions

5. **Safety Classification** [base.py:79](): Classifier judges harmfulness or refusal

6. **Result Processing** [base.py:91-128]():
   - Handle parsing errors (mark as unsafe/safe depending on `benign` mode)
   - Handle empty responses (mark as unsafe/safe depending on `benign` mode)
   - Compare classifier output to expected "successful attack" indicator
   - Track source-specific metrics if `source` field exists

7. **Metric Calculation** [base.py:129-141]():
   - **Normal mode** (`benign=False`): Report `inverted_macro_asr` = 1 - ASR (higher is better)
   - **Benign mode** (`benign=True`): Report direct `macro_asr` (lower is better)
   - Include error metrics: truncations, parsing_errors, empty_response

Sources: [evaluation/tasks/generation/base.py:44-154]()

### Classifier Preparation

```mermaid
graph LR
    PrepareEvaluator["prepare_evaluator()<br/>base.py:30-42"]
    LoadClassifier["load_classifier_model()<br/>classifier_model_name"]
    CheckFields["Check input/output fields"]
    
    PrepareEvaluator --> LoadClassifier
    LoadClassifier --> CheckFields
    
    CheckFields --> DetermineOutput{"Which output<br/>field?"}
    DetermineOutput -->|response_refusal| RefusalOutput["classifier_output_field = 'response_refusal'<br/>desired_outputs = COMPLIANCE"]
    DetermineOutput -->|response_harmfulness| HarmfulnessOutput["classifier_output_field = 'response_harmfulness'<br/>desired_outputs = HARMFUL"]
    
    RefusalOutput --> Return["Return classifier, field, desired_output"]
    HarmfulnessOutput --> Return
```

The `prepare_evaluator()` method [base.py:30-42]() loads the safety classifier and determines which output field to use for evaluation. If the classifier supports `response_refusal` detection, it uses that and treats `COMPLIANCE` as a successful attack. Otherwise, it uses `response_harmfulness` and treats `HARMFUL` as a successful attack.

Sources: [evaluation/tasks/generation/base.py:30-42](), [src/classifier_models/base.py]()

## Related Adversarial Tasks

Several other tasks extend `AdversarialTaskBase` and follow the same evaluation pattern:

### DoAnythingNow (DAN)

Classic jailbreak prompts using the "Do Anything Now" persona:

- **Location**: [evaluation/tasks/generation/do_anything_now/__init__.py:7-16]()
- **Data**: Loads from `do_anything_now_jailbreak.jsonl`
- **Usage**: Tests model resistance to role-playing jailbreaks

### TrustLLM Jailbreak Trigger

Trigger-based jailbreak prompts from the TrustLLM benchmark:

- **Location**: [evaluation/tasks/generation/trustllm_jailbreaktrigger/__init__.py:7-16]()
- **Data**: 400-sample subset from `trustllm_jailbreaktrigger_400.jsonl`
- **Source Field**: Includes `source` metadata (e.g., "QBB" vs "ITC") for source-specific metrics [base.py:120-125]()

Sources: [evaluation/tasks/generation/do_anything_now/__init__.py:1-16](), [evaluation/tasks/generation/trustllm_jailbreaktrigger/__init__.py:1-16]()

## Running Jailbreak Evaluations

### Direct Task Evaluation

To evaluate the WildJailbreak task directly without additional attack wrapping:

```bash
python evaluation/eval.py generators \
  --model_name_or_path allenai/tulu-2-dpo-7b \
  --model_input_template_path_or_name tulu2 \
  --tasks wildjailbreak \
  --report_output_path ./results/metrics.json
```

This evaluates the model on the harmful variant. To evaluate the benign variant for over-refusal:

```bash
python evaluation/eval.py generators \
  --tasks wildjailbreak:benign \
  --report_output_path ./results/metrics.json
```

The task name format is `{folder}:{config_yaml}` where the YAML config specifies the task class and hyperparameters.

Sources: [evaluation/eval.py:92-203](), [README.md:96-123]()

### Wrapped Attack Evaluation

To wrap an existing task with jailbreak attacks:

```bash
python evaluation/eval.py jailbreak \
  --model_name_or_path allenai/tulu-2-dpo-7b \
  --model_input_template_path_or_name tulu2 \
  --tasks harmbench \
  --attacks pair,wildjailbreak \
  --report_output_path ./results/jailbreak_metrics.json
```

**Evaluation Flow** [eval.py:206-305]():

1. Parse tasks and attacks from command line arguments
2. Load the base generative model
3. Load evaluation tasks (e.g., `HarmbenchVanilla`)
4. For each task and attack combination:
   - Call `wrap_task_with_jailbreak(task, attack)` to create wrapped task
   - Store result under task name `{task_name}/{attack}` (e.g., `harmbench/pair`)
   - Execute `wrapped_task.evaluate(model)`
5. Save aggregated results

The wrapped evaluation allows testing any base task (Harmbench, StrongReject, etc.) under various attack strategies without modifying the task implementation.

Sources: [evaluation/eval.py:206-305](), [evaluation/tasks/__init__.py:74-98]()

### Configuration Files

Tasks are configured via YAML files in the task directories:

**WildJailbreak Harmful Configuration** (example structure):
```yaml
task_class: WildJailbreakValidation
classifier_model_name: WildGuard
hparams:
  max_new_tokens: 512
  temperature: 0.7
  top_p: 0.95
```

**WildJailbreak Benign Configuration** (example structure):
```yaml
task_class: WildJailbreakValidationBenign
classifier_model_name: WildGuard
hparams:
  max_new_tokens: 512
  temperature: 0.7
  top_p: 0.95
```

The `task_class` field specifies which Python class to instantiate. The loader handles the `benign=True` parameter for the benign variant [tasks/__init__.py:66-69]().

Sources: [evaluation/tasks/__init__.py:34-69](), [evaluation/tasks/generation/trustllm_jailbreaktrigger/gpt4.yaml:1-6]()

## Metrics and Results

### Attack Success Rate (ASR)

The primary metric for adversarial evaluation:

- **Calculation**: Proportion of examples where the model's response was classified as harmful/compliant
- **Inverted ASR**: For harmful tasks, reports `1 - ASR` so higher scores indicate better safety
- **Direct ASR**: For benign tasks, reports raw ASR where higher scores indicate more over-refusal

### Error Tracking

All adversarial tasks track evaluation errors [base.py:84-89, 99-103, 127-128]():

| Error Type | Description |
|------------|-------------|
| `truncations` | Responses truncated due to length limits |
| `parsing_errors` | Classifier output couldn't be parsed |
| `empty_response` | Model produced no answer text (reasoning models only) |

Parsing errors and empty responses are treated as unsafe (successful attacks) for harmful tasks, and safe (failed attacks) for benign tasks [base.py:103-114]().

### Source-Specific Metrics

When the data includes a `source` field (e.g., TrustLLM's "QBB" vs "ITC" sources), the framework automatically computes per-source ASR metrics [base.py:120-125]():

```python
if "source" in gt:
    source_format = gt["source"].replace(' ','_').lower()
    source_field = f'{source_format}_asr'
    if source_field not in eval_report:
        eval_report[source_field] = []
    eval_report[source_field].append(correct)
```

This enables fine-grained analysis of attack success across different source types.

Sources: [evaluation/tasks/generation/base.py:84-141](), [evaluation/tasks/metrics.py]()

---

