<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/CommaQA · page 5 Execution Engine · fetched 2026-10-26 -->

# Execution Engine

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [commaqa/execution/model_executer.py](commaqa/execution/model_executer.py)
- [commaqa/execution/operation_executer.py](commaqa/execution/operation_executer.py)
- [commaqa/execution/utils.py](commaqa/execution/utils.py)

</details>



The Execution Engine is the core operational component that executes structured operations against knowledge bases and model libraries. It processes questions through a series of operations (`select`, `project`, `filter`) and manages variable assignments throughout the execution process. This system bridges natural language questions to structured knowledge base queries through predicate matching and operation chaining.

For information about higher-level inference orchestration, see [Inference System](#4). For details about specific models used in execution, see [Model Library](#5.2).

## Core Architecture

The execution engine is built around two primary classes: `OperationExecuter` which handles the core operation logic, and `ModelExecutor` which manages predicate-to-question mapping and model selection.

### Execution Engine Components

```mermaid
graph TD
    subgraph "Execution Engine Core"
        OE["OperationExecuter"] --> ML["model_library"]
        OE --> EXEC_SEL["execute_select()"]
        OE --> EXEC_PROJ["execute_project()"]
        OE --> EXEC_FILT["execute_filter()"]
        OE --> EXEC_SUB["execute_sub_operations()"]
    end
    
    subgraph "Model Integration"
        ME["ModelExecutor"] --> PL["predicate_language"]
        ME --> KB["kblookup"]
        ME --> ASK_Q["ask_question()"]
        ME --> ASK_PRED["ask_question_predicate()"]
    end
    
    subgraph "Model Library"
        ML --> MATH["MathModel"]
        ML --> KBLOOKUP["KBLookup"]
        ML --> TEXT["ModelExecutor instances"]
    end
    
    subgraph "Operations Flow"
        QUESTION["Natural Language Question"] --> ASK_Q
        ASK_Q --> PRED_MATCH["find_qpred_assignments()"]
        PRED_MATCH --> ASK_PRED
        ASK_PRED --> OE
        OE --> ANSWERS["answers, facts_used"]
    end
    
    EXEC_SEL --> ML
    EXEC_PROJ --> ML
    EXEC_FILT --> ML
```

Sources: [commaqa/execution/operation_executer.py:10-16](), [commaqa/execution/model_executer.py:13-20](), [commaqa/execution/utils.py:11-26]()

### Operation Execution Flow

The execution process follows a systematic pattern where questions are parsed, matched to predicates, and executed through the appropriate operation type:

```mermaid
graph TD
    subgraph "Question Processing"
        INPUT["Input Question"] --> PARSE["get_predicate_args()"]
        PARSE --> CHECK{"Predicate Format?"}
        CHECK -->|Yes| DIRECT["ask_question_predicate()"]
        CHECK -->|No| MATCH["find_qpred_assignments()"]
    end
    
    subgraph "Assignment Processing"
        MATCH --> ASSIGN["Variable Assignments"]
        ASSIGN --> SUBST["Variable Substitution"]
        DIRECT --> PRED_EXEC["Predicate Execution"]
        SUBST --> PRED_EXEC
    end
    
    subgraph "Operation Execution"
        PRED_EXEC --> OP_TYPE{"Operation Type"}
        OP_TYPE -->|select| SELECT["execute_select()"]
        OP_TYPE -->|project| PROJECT["execute_project()"]
        OP_TYPE -->|filter| FILTER["execute_filter()"]
    end
    
    subgraph "Result Processing"
        SELECT --> SUB_OPS["execute_sub_operations()"]
        PROJECT --> SUB_OPS
        FILTER --> SUB_OPS
        SUB_OPS --> RESULT["answers, facts_used"]
    end
```

Sources: [commaqa/execution/model_executer.py:38-69](), [commaqa/execution/operation_executer.py:190-218]()

## Operation Types

The execution engine supports three primary operation types, each designed for specific query patterns:

### Select Operations

Select operations retrieve data directly from the knowledge base using the model library. They replace answer indices with assigned values and query the specified model.

**Key Implementation Details:**
- Processes answer indices (`#1`, `#2`, etc.) from questions
- Substitutes indices with values from `assignments` dictionary
- Calls `model_library[model].ask_question()` for execution
- Applies sub-operations to results

```mermaid
graph LR
    subgraph "Select Operation Flow"
        Q["Question with #1, #2"] --> IDX["get_answer_indices()"]
        IDX --> REPLACE["Replace indices with assignments"]
        REPLACE --> MODEL["model_library[model].ask_question()"]
        MODEL --> SUBOP["execute_sub_operations()"]
        SUBOP --> RESULT["Final Answer"]
    end
```

Sources: [commaqa/execution/operation_executer.py:43-55]()

### Project Operations

Project operations iterate over list assignments and apply questions to each item, creating new associations between keys and values.

**Supported Project Types:**
- `project`: Creates `(item, answer)` tuples
- `projectValues`: Creates `(key, answer)` tuples from `(key, value)` inputs  
- `projectKeys`: Creates `(answer, value)` tuples from `(key, value)` inputs

| Operation Type | Input Format | Output Format |
|---------------|--------------|---------------|
| `project` | `[item1, item2, ...]` | `[(item1, answer1), (item2, answer2), ...]` |
| `projectValues` | `[(key1, val1), (key2, val2), ...]` | `[(key1, answer1), (key2, answer2), ...]` |
| `projectKeys` | `[(key1, val1), (key2, val2), ...]` | `[(answer1, val1), (answer2, val2), ...]` |

Sources: [commaqa/execution/operation_executer.py:57-112]()

### Filter Operations

Filter operations evaluate boolean conditions on list items and return only those items that satisfy the condition.

**Filter Types:**
- `filter`: Evaluates condition on string items
- `filterValues`: Evaluates condition on tuple values
- `filterKeys`: Evaluates condition on tuple keys

The filter expects boolean responses (`"yes"`, `"1"`, `"true"`) to determine item inclusion.

Sources: [commaqa/execution/operation_executer.py:114-188]()

## Sub-Operations

Sub-operations are chained modifiers applied after the primary operation execution. They are specified using underscore notation (e.g., `select_flat_unique`).

### Available Sub-Operations

| Sub-Operation | Purpose | Input Type | Behavior |
|--------------|---------|------------|----------|
| `flat` | Flatten nested lists | `list` | Calls `flatten_list()` |
| `unique` | Remove duplicates | `list` | JSON-based deduplication |
| `keys` | Extract keys from tuples | `list of tuples` | Returns `[x[0] for x in list]` |
| `values` | Extract values from tuples | `list of tuples` | Returns `[x[1] for x in list]` |

```mermaid
graph LR
    subgraph "Sub-Operation Chain"
        INPUT["Operation Result"] --> CHECK1{"flat?"}
        CHECK1 -->|Yes| FLAT["flatten_list()"]
        CHECK1 -->|No| CHECK2{"unique?"}
        FLAT --> CHECK2
        CHECK2 -->|Yes| UNIQUE["JSON-based deduplication"]
        CHECK2 -->|No| CHECK3{"keys?"}
        UNIQUE --> CHECK3
        CHECK3 -->|Yes| KEYS["Extract x[0]"]
        CHECK3 -->|No| CHECK4{"values?"}
        KEYS --> CHECK4
        CHECK4 -->|Yes| VALUES["Extract x[1]"]
        CHECK4 -->|No| OUTPUT["Final Result"]
        VALUES --> OUTPUT
    end
```

Sources: [commaqa/execution/operation_executer.py:17-42]()

## Model Integration and Predicate Matching

The `ModelExecutor` class handles the translation from natural language questions to structured predicates through pattern matching and variable assignment.

### Predicate Language Processing

```mermaid
graph TD
    subgraph "Question-to-Predicate Mapping"
        NL_Q["Natural Language Question"] --> REGEX["find_qpred_assignments()"]
        REGEX --> PATTERN["Regex Pattern Matching"]
        PATTERN --> VARS["Variable Extraction"]
        VARS --> ASSIGN["Assignment Dictionary"]
    end
    
    subgraph "Predicate Language Structure"
        PL["predicate_language"] --> QUESTIONS["questions[]"]
        PL --> PREDICATE["predicate"]
        PL --> STEPS["steps[]"]
        QUESTIONS --> Q_DEF["Question Definitions with $1, $2"]
        PREDICATE --> P_DEF["Predicate with Variables"]
        STEPS --> EXEC_STEPS["Execution Steps"]
    end
    
    subgraph "Execution Path"
        ASSIGN --> SUBST["Variable Substitution"]
        SUBST --> P_DEF
        P_DEF --> EXEC_STEPS
        EXEC_STEPS --> KB_EXEC["KBLookup Execution"]
        KB_EXEC --> FINAL["Final Answer"]
    end
```

The system uses regular expressions to match question patterns, extracting variables through named capture groups. For example, a question pattern `"What is the age of $1?"` becomes the regex `"What is the age of (?P<G1>.+)?"`.

Sources: [commaqa/execution/model_executer.py:21-36](), [commaqa/execution/model_executer.py:70-108]()

## Error Handling and Robustness

The execution engine includes comprehensive error handling with configurable behavior through the `ignore_input_mismatch` parameter.

### Error Handling Strategy

| Error Condition | `ignore_input_mismatch=False` | `ignore_input_mismatch=True` |
|----------------|-------------------------------|------------------------------|
| Model not found | Raises `ValueError` | Returns `NOANSWER`, logs debug |
| No matching predicate | Raises `ValueError` | Returns `NOANSWER`, logs debug |
| Invalid assignments | Raises `ValueError` | Returns `NOANSWER`, logs debug |
| Operation execution failure | Raises `ValueError` | Returns `NOANSWER`, logs debug |

The system tracks execution statistics through `num_calls` counters in both `OperationExecuter` and `ModelExecutor` classes.

Sources: [commaqa/execution/operation_executer.py:190-218](), [commaqa/execution/model_executer.py:62-68](), [commaqa/execution/model_executer.py:103-108]()

## Model Library Construction

The execution engine is initialized with a model library built through the `build_models()` function, which creates specialized model instances based on configuration.

```mermaid
graph LR
    subgraph "Model Library Building"
        CONFIG["pred_lang_config"] --> BUILD["build_models()"]
        KB["complete_kb"] --> BUILD
        BUILD --> KBLOOKUP["KBLookup(kb)"]
        BUILD --> CHECK{"model_name == MATH_MODEL?"}
        CHECK -->|Yes| MATH_MODEL["MathModel()"]
        CHECK -->|No| MODEL_EXEC["ModelExecutor()"]
        MATH_MODEL --> LIB["model_library{}"]
        MODEL_EXEC --> LIB
        KBLOOKUP --> MATH_MODEL
        KBLOOKUP --> MODEL_EXEC
    end
```

Each model in the library is instantiated with the same `KBLookup` instance, ensuring consistent knowledge base access across all execution paths.

Sources: [commaqa/execution/utils.py:11-26]()

---

