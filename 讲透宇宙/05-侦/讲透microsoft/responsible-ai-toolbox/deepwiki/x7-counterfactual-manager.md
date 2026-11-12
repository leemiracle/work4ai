<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/responsible-ai-toolbox · extra page Counterfactual Manager · fetched 2026-10-26 -->

# Counterfactual Manager

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [raiwidgets/raiwidgets/interfaces.py](raiwidgets/raiwidgets/interfaces.py)
- [responsibleai/responsibleai/_tools/shared/state_directory_management.py](responsibleai/responsibleai/_tools/shared/state_directory_management.py)
- [responsibleai/responsibleai/exceptions.py](responsibleai/responsibleai/exceptions.py)
- [responsibleai/responsibleai/modelanalysis/model_analysis.py](responsibleai/responsibleai/modelanalysis/model_analysis.py)
- [responsibleai/tests/causal_manager_validator.py](responsibleai/tests/causal_manager_validator.py)
- [responsibleai/tests/counterfactual_manager_validator.py](responsibleai/tests/counterfactual_manager_validator.py)
- [responsibleai/tests/error_analysis_validator.py](responsibleai/tests/error_analysis_validator.py)
- [responsibleai/tests/explainer_manager_validator.py](responsibleai/tests/explainer_manager_validator.py)
- [responsibleai/tests/test_exceptions.py](responsibleai/tests/test_exceptions.py)

</details>



## Purpose and Scope

The **CounterfactualManager** is one of the core analysis managers in the Responsible AI Toolbox, responsible for generating counterfactual explanations for machine learning models. Counterfactual explanations answer the question: "What minimal changes to input features would result in a different prediction?" This manager integrates the [DiCE (Diverse Counterfactual Explanations)](https://github.com/interpretml/DiCE) library to generate diverse, actionable counterfactual examples.

The CounterfactualManager is accessed as a property of the `RAIInsights` object and follows the standard manager pattern used throughout the toolkit. For information about the broader manager orchestration system, see [Manager Orchestration](#3.2.2). For other analysis types, see [Causal Manager](#3.3.3), [Explainer Manager](#3.3.2), and [Error Analysis Manager](#3.3.1).

**Sources:** [responsibleai/responsibleai/modelanalysis/model_analysis.py:98-104](), [responsibleai/tests/counterfactual_manager_validator.py:1-128]()

## Architecture Overview

The CounterfactualManager integrates into the RAI ecosystem as a specialized analysis component that wraps the DiCE library. The following diagram shows how it fits within the overall system:

```mermaid
graph TB
    subgraph "RAIInsights API"
        RAIInsights["RAIInsights<br/>Main Entry Point"]
        CFProperty["counterfactual property<br/>Returns CounterfactualManager"]
    end
    
    subgraph "CounterfactualManager"
        CFManager["CounterfactualManager"]
        AddMethod["add()<br/>Configure counterfactual generation"]
        ComputeMethod["compute()<br/>Generate counterfactuals"]
        GetMethod["get()<br/>Retrieve results"]
        ListMethod["list()<br/>Get metadata"]
        
        CFManager --> AddMethod
        CFManager --> ComputeMethod
        CFManager --> GetMethod
        CFManager --> ListMethod
    end
    
    subgraph "External Library"
        DiCE["dice-ml<br/>Counterfactual Generation Engine"]
        DiCEMethods["Methods:<br/>- random<br/>- genetic<br/>- kdtree"]
    end
    
    subgraph "Storage"
        ConfigDir["Configuration Directory<br/>JSON config files"]
        DataDir["Data Directory<br/>Serialized results"]
        GenDir["Generators Directory<br/>DiCE objects"]
    end
    
    subgraph "Results"
        CFData["CounterfactualData"]
        CFExamples["cf_examples_list<br/>List of counterfactual instances"]
        LocalImportance["local_importance<br/>Feature importance per CF"]
        SummaryImportance["summary_importance<br/>Aggregated importance"]
        
        CFData --> CFExamples
        CFData --> LocalImportance
        CFData --> SummaryImportance
    end
    
    RAIInsights --> CFProperty
    CFProperty --> CFManager
    AddMethod --> ConfigDir
    ComputeMethod --> DiCE
    DiCE --> DiCEMethods
    ComputeMethod --> CFData
    GetMethod --> CFData
    CFData --> DataDir
    DiCE --> GenDir
    
    style CFManager fill:#f9f9f9,stroke:#333,stroke-width:2px
    style DiCE fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [responsibleai/responsibleai/modelanalysis/model_analysis.py:14,99-104](), [responsibleai/tests/counterfactual_manager_validator.py:33-128]()

## Manager Lifecycle and API

### Standard Manager Pattern

The CounterfactualManager follows the standard three-phase lifecycle used by all RAI managers:

| Phase | Method | Purpose |
|-------|--------|---------|
| **Configuration** | `add()` | Specify parameters for counterfactual generation |
| **Computation** | `compute()` | Execute DiCE to generate counterfactuals |
| **Retrieval** | `get()`, `list()` | Access computed results and metadata |

```mermaid
graph LR
    Init["RAIInsights<br/>Initialization"] --> Add["counterfactual.add()<br/>Configure parameters"]
    Add --> Add2["counterfactual.add()<br/>Additional configs<br/>(optional)"]
    Add2 --> Compute["rai_insights.compute()<br/>or<br/>counterfactual.compute()"]
    Compute --> Get["counterfactual.get()<br/>Retrieve results"]
    Compute --> List["counterfactual.list()<br/>Retrieve metadata"]
    
    style Compute fill:#f9f9f9,stroke:#333,stroke-width:2px
```

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:33-96]()

### Configuration Phase: `add()` Method

The `add()` method configures a counterfactual generation task. Users can call this method multiple times to create different configurations with varying parameters.

**Key Parameters:**

| Parameter | Type | Description | Constraints |
|-----------|------|-------------|-------------|
| `total_CFs` | int | Number of counterfactual examples to generate per instance | Must be positive; if `feature_importance=True`, must be ≥ 10 |
| `method` | str | DiCE method to use | Options: `'random'`, `'genetic'`, `'kdtree'` |
| `desired_class` | int/str | Target class for classification (optional) | Used for classification tasks |
| `desired_range` | tuple | Target range for regression (optional) | Used for regression tasks |
| `feature_importance` | bool | Whether to compute feature importance | Default: `False`; requires `total_CFs ≥ 10` |

**Example Usage Pattern:**

```python
# Classification: Generate counterfactuals for desired class
rai_insights.counterfactual.add(
    total_CFs=10,
    method='random',
    desired_class=1,
    feature_importance=True
)

# Regression: Generate counterfactuals within desired range
rai_insights.counterfactual.add(
    total_CFs=5,
    method='genetic',
    desired_range=[50, 100]
)
```

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:33-85]()

### Validation Logic

The CounterfactualManager performs several validation checks during configuration:

```mermaid
graph TD
    AddCall["counterfactual.add()"] --> CheckModel{"Model<br/>available?"}
    CheckModel -->|No| ErrorModel["Raise UserConfigValidationException:<br/>'Model is required for counterfactual<br/>example generation and feature importances'"]
    CheckModel -->|Yes| CheckDuplicate{"Configuration<br/>already exists?"}
    CheckDuplicate -->|Yes| ErrorDuplicate["Raise DuplicateManagerConfigException"]
    CheckDuplicate -->|No| CheckFeatureImportance{"feature_importance<br/>== True?"}
    CheckFeatureImportance -->|Yes| CheckTotalCFs{"total_CFs<br/>>= 10?"}
    CheckTotalCFs -->|No| ErrorTotalCFs["Raise UserConfigValidationException:<br/>'Insufficient counterfactuals for<br/>feature importance'"]
    CheckTotalCFs -->|Yes| ValidConfig["Store Configuration"]
    CheckFeatureImportance -->|No| CheckPositive{"total_CFs<br/>> 0?"}
    CheckPositive -->|No| ErrorNegative["Raise UserConfigValidationException:<br/>'total_CFs must be positive'"]
    CheckPositive -->|Yes| ValidConfig
    
    style ErrorModel fill:#ffeeee,stroke:#333,stroke-width:1px
    style ErrorDuplicate fill:#ffeeee,stroke:#333,stroke-width:1px
    style ErrorTotalCFs fill:#ffeeee,stroke:#333,stroke-width:1px
    style ErrorNegative fill:#ffeeee,stroke:#333,stroke-width:1px
```

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:43-128](), [raiutils/raiutils/exceptions.py](), [responsibleai/responsibleai/exceptions.py:25-33]()

### Computation Phase: `compute()` Method

The `compute()` method triggers the actual counterfactual generation using DiCE. This can be called either directly on the manager or on the parent `RAIInsights` object (which will call compute on all configured managers).

**Computation Flow:**

```mermaid
graph TB
    Start["compute()"] --> Iterate["For each configuration"]
    Iterate --> InitDiCE["Initialize DiCE<br/>with model and data"]
    InitDiCE --> Generate["DiCE.generate_counterfactuals()<br/>with configured parameters"]
    Generate --> CheckFI{"feature_importance<br/>enabled?"}
    CheckFI -->|Yes| ComputeFI["Compute feature importance<br/>from counterfactual variations"]
    CheckFI -->|No| StoreBasic["Store cf_examples_list only"]
    ComputeFI --> StoreComplete["Store cf_examples_list,<br/>local_importance,<br/>summary_importance"]
    StoreBasic --> Next["Next configuration"]
    StoreComplete --> Next
    Next --> Iterate
    Next --> Done["Mark as computed"]
```

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:61-95]()

### Retrieval Phase: `get()` and `list()` Methods

#### `get()` Method

Returns a list of counterfactual result objects, one for each configured counterfactual generation task.

**Return Structure:**

Each result object contains:
- `cf_examples_list`: List of generated counterfactual examples
- `local_importance`: Feature importance for each counterfactual (if `feature_importance=True`)
- `summary_importance`: Aggregated feature importance across all counterfactuals (if `feature_importance=True`)

**Filtering Failed Computations:**

```python
# Get successful results only (default)
results = rai_insights.counterfactual.get()

# Get failed computations
failed = rai_insights.counterfactual.get(failed_to_compute=True)
```

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:62-95,121-127]()

#### `list()` Method

Returns metadata about all counterfactual configurations without the full result data.

**Return Structure:**

```python
{
    'manager_type': 'counterfactual',  # ManagerNames.COUNTERFACTUAL
    'counterfactuals': [
        # List of configuration summaries
        # Length equals number of add() calls
    ]
}
```

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:22-30,67-69]()

## Result Data Structures

### Counterfactual Object Structure

```mermaid
graph TB
    subgraph "CounterfactualData Object"
        CFObj["Counterfactual Result"]
        CFExamples["cf_examples_list<br/>Type: List"]
        LocalImp["local_importance<br/>Type: Array or None"]
        SummaryImp["summary_importance<br/>Type: Array or None"]
        
        CFObj --> CFExamples
        CFObj --> LocalImp
        CFObj --> SummaryImp
    end
    
    subgraph "When feature_importance=False"
        Basic["cf_examples_list: populated<br/>local_importance: None<br/>summary_importance: None"]
    end
    
    subgraph "When feature_importance=True"
        Full["cf_examples_list: populated<br/>local_importance: populated<br/>summary_importance: populated"]
    end
    
    CFObj -.feature_importance=False.-> Basic
    CFObj -.feature_importance=True.-> Full
```

**Validation Assertions:**

The test suite validates the following invariants:

| Condition | Assertion |
|-----------|-----------|
| Always | `cf_examples_list is not None` |
| `feature_importance=True` | `local_importance is not None` |
| `feature_importance=True` | `summary_importance is not None` |
| `feature_importance=False` | `local_importance is None` |
| `feature_importance=False` | `summary_importance is None` |

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:12-20]()

## Multiple Configurations

The CounterfactualManager supports multiple configurations, allowing users to experiment with different generation strategies.

### Configuration Multiplicity Example

```mermaid
graph LR
    subgraph "Configuration 1"
        Config1["total_CFs=1<br/>method='random'<br/>feature_importance=False"]
    end
    
    subgraph "Configuration 2"
        Config2["total_CFs=2<br/>method='random'<br/>feature_importance=False"]
    end
    
    subgraph "Configuration 3"
        Config3["total_CFs=10<br/>method='random'<br/>feature_importance=True"]
    end
    
    Config1 --> Result1["Result 1:<br/>cf_examples_list"]
    Config2 --> Result2["Result 2:<br/>cf_examples_list"]
    Config3 --> Result3["Result 3:<br/>cf_examples_list<br/>local_importance<br/>summary_importance"]
```

### Duplicate Detection

The manager prevents duplicate configurations:

- Configurations are compared based on all parameters: `total_CFs`, `method`, `desired_class`, `desired_range`, `feature_importance`
- If a duplicate is detected, `DuplicateManagerConfigException` is raised
- This ensures efficient resource usage and prevents redundant computations

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:71-77](), [responsibleai/responsibleai/exceptions.py:25-33]()

## Persistence and Serialization

The CounterfactualManager integrates with the broader RAI persistence system using the `DirectoryManager` pattern.

### Storage Structure

```mermaid
graph TB
    subgraph "RAIInsights Directory"
        ParentDir["parent_directory_path/<br/>sub_directory_name/"]
        
        subgraph "Subdirectories"
            ConfigDir["configuration/<br/>Counterfactual configs"]
            DataDir["data/<br/>Counterfactual results"]
            GenDir["generators/<br/>DiCE generators"]
        end
        
        ParentDir --> ConfigDir
        ParentDir --> DataDir
        ParentDir --> GenDir
    end
    
    subgraph "File Contents"
        ConfigJSON["Configuration JSON:<br/>- total_CFs<br/>- method<br/>- desired_class/range<br/>- feature_importance"]
        DataJSON["Results JSON:<br/>- cf_examples_list<br/>- local_importance<br/>- summary_importance"]
        DiCEPickle["DiCE generator objects<br/>(pickled)"]
    end
    
    ConfigDir --> ConfigJSON
    DataDir --> DataJSON
    GenDir --> DiCEPickle
```

The manager uses the `DirectoryManager` class to create and access these directories:
- `create_config_directory()`: Store configuration parameters
- `create_data_directory()`: Store computed results  
- `create_generators_directory()`: Store DiCE generator objects for potential reuse

**Sources:** [responsibleai/responsibleai/_tools/shared/state_directory_management.py:11-132]()

## Error Handling and Edge Cases

### Required Model Validation

The CounterfactualManager requires a model to function, unlike some other managers that can operate with cached predictions:

```mermaid
graph TD
    Check["CounterfactualManager<br/>Configuration"] --> ModelCheck{"Model<br/>provided?"}
    ModelCheck -->|No| Error["Raise UserConfigValidationException:<br/>'Model is required for counterfactual<br/>example generation and feature importances'"]
    ModelCheck -->|Yes| Proceed["Proceed with<br/>configuration"]
    
    style Error fill:#ffeeee,stroke:#333,stroke-width:1px
```

This is because DiCE needs to evaluate the model repeatedly to search for counterfactual examples.

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:43-53]()

### Failed Computation Tracking

The manager tracks configurations that fail during computation:

| Scenario | Behavior |
|----------|----------|
| Successful computation | Result added to main results list |
| Failed computation | Configuration stored separately, accessible via `get(failed_to_compute=True)` |
| Invalid pre-compute configuration | Exception raised during `add()`, configuration not stored |
| Invalid runtime configuration | Exception raised during `compute()`, marked as failed |

**Example: Tracking Failures**

```python
# Add invalid configuration (negative total_CFs)
try:
    rai_insights.counterfactual.add(total_CFs=-2, method='random')
    rai_insights.counterfactual.compute()
except UserConfigValidationException:
    pass

# Check failed computations
successful = rai_insights.counterfactual.get()  # Excludes failed
failed = rai_insights.counterfactual.get(failed_to_compute=True)  # Only failed
```

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:113-127]()

## Integration with RAIInsights

### Manager Property Access

The CounterfactualManager is accessed as a property of `RAIInsights`:

```python
# Via RAIInsights
rai_insights = RAIInsights(model, train, test, target_column, task_type)
cf_manager = rai_insights.counterfactual  # Returns CounterfactualManager instance
```

The deprecated `ModelAnalysis` class provides the same interface:

```python
# Via ModelAnalysis (deprecated)
model_analysis = ModelAnalysis(model, train, test, target_column, task_type)
cf_manager = model_analysis.counterfactual  # Returns CounterfactualManager instance
```

**Sources:** [responsibleai/responsibleai/modelanalysis/model_analysis.py:98-104]()

### Orchestration with Other Managers

The CounterfactualManager operates independently but can be computed alongside other managers:

```mermaid
graph TB
    subgraph "RAIInsights Configuration"
        EA["error_analysis.add()"]
        EX["explainer.add()"]
        CA["causal.add()"]
        CF["counterfactual.add()"]
    end
    
    subgraph "Unified Compute"
        Compute["rai_insights.compute()"]
    end
    
    subgraph "Manager Execution"
        EAComp["ErrorAnalysisManager.compute()"]
        EXComp["ExplainerManager.compute()"]
        CAComp["CausalManager.compute()"]
        CFComp["CounterfactualManager.compute()"]
    end
    
    EA --> Compute
    EX --> Compute
    CA --> Compute
    CF --> Compute
    
    Compute --> EAComp
    Compute --> EXComp
    Compute --> CAComp
    Compute --> CFComp
```

All managers are computed when `rai_insights.compute()` is called, or individual managers can be computed separately.

**Sources:** [responsibleai/responsibleai/modelanalysis/model_analysis.py:122-124]()

## Constants and Configuration Keys

The CounterfactualManager uses standardized keys defined in the `_internal.constants` module:

| Constant | Usage |
|----------|-------|
| `CounterfactualManagerKeys.COUNTERFACTUALS` | Key for counterfactual results in `list()` output |
| `ManagerNames.COUNTERFACTUAL` | Identifier for manager type |
| `ListProperties.MANAGER_TYPE` | Key for manager type in `list()` output |

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:7-8,24-30]()

## Summary

The CounterfactualManager provides a streamlined interface for generating counterfactual explanations using the DiCE library. Key features include:

- **Flexible Configuration**: Support for multiple generation strategies and parameters
- **Feature Importance**: Optional computation of feature importance from counterfactual variations
- **Validation**: Comprehensive input validation and duplicate detection
- **Persistence**: Integration with RAI's standard serialization system
- **Error Tracking**: Graceful handling of failed computations

The manager follows the standard RAI manager pattern (add → compute → get/list) and integrates seamlessly with other analysis components in the Responsible AI Toolbox.

**Sources:** [responsibleai/tests/counterfactual_manager_validator.py:1-128](), [responsibleai/responsibleai/modelanalysis/model_analysis.py:1-176]()

---

