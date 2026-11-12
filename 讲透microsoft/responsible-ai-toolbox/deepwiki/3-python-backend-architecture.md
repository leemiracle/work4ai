<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/responsible-ai-toolbox · page 3 Python Backend Architecture · fetched 2026-10-26 -->

# Python Backend Architecture

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [CHANGES.md](CHANGES.md)
- [erroranalysis/requirements-dev.txt](erroranalysis/requirements-dev.txt)
- [erroranalysis/requirements.txt](erroranalysis/requirements.txt)
- [nlp_feature_extractors/requirements.txt](nlp_feature_extractors/requirements.txt)
- [rai_core_flask/requirements.txt](rai_core_flask/requirements.txt)
- [raiwidgets/requirements.txt](raiwidgets/requirements.txt)
- [responsibleai/requirements-dev.txt](responsibleai/requirements-dev.txt)
- [responsibleai/requirements.txt](responsibleai/requirements.txt)
- [responsibleai/responsibleai/_internal/constants.py](responsibleai/responsibleai/_internal/constants.py)
- [responsibleai/responsibleai/rai_insights/rai_base_insights.py](responsibleai/responsibleai/rai_insights/rai_base_insights.py)
- [responsibleai/responsibleai/rai_insights/rai_insights.py](responsibleai/responsibleai/rai_insights/rai_insights.py)
- [responsibleai/tests/common_utils.py](responsibleai/tests/common_utils.py)
- [responsibleai/tests/model_analysis/test_model_analysis.py](responsibleai/tests/model_analysis/test_model_analysis.py)
- [responsibleai/tests/model_analysis/test_model_analysis_validations.py](responsibleai/tests/model_analysis/test_model_analysis_validations.py)
- [responsibleai/tests/rai_insights/test_rai_insights.py](responsibleai/tests/rai_insights/test_rai_insights.py)
- [responsibleai/tests/rai_insights/test_rai_insights_cohort_filter.py](responsibleai/tests/rai_insights/test_rai_insights_cohort_filter.py)
- [responsibleai/tests/rai_insights/test_rai_insights_data_size_scenarios.py](responsibleai/tests/rai_insights/test_rai_insights_data_size_scenarios.py)
- [responsibleai/tests/rai_insights/test_rai_insights_get_feature_ranges.py](responsibleai/tests/rai_insights/test_rai_insights_get_feature_ranges.py)
- [responsibleai/tests/rai_insights/test_rai_insights_save_and_load_scenarios.py](responsibleai/tests/rai_insights/test_rai_insights_save_and_load_scenarios.py)
- [responsibleai/tests/rai_insights/test_rai_insights_validations.py](responsibleai/tests/rai_insights/test_rai_insights_validations.py)
- [responsibleai/tests/test_model_serializer.py](responsibleai/tests/test_model_serializer.py)
- [responsibleai_text/responsibleai_text/version.py](responsibleai_text/responsibleai_text/version.py)
- [responsibleai_vision/responsibleai_vision/version.py](responsibleai_vision/responsibleai_vision/version.py)
- [version.cfg](version.cfg)

</details>



## Purpose and Scope

This document describes the Python backend architecture of the Responsible AI Toolbox, covering the core analysis packages and their interactions. It focuses on the structure of the `responsibleai` package, the `RAIInsights` API, the manager orchestration pattern, and supporting infrastructure packages.

For information about the TypeScript dashboard that consumes this backend, see [TypeScript Dashboard Architecture](#4). For domain-specific extensions to vision and text models, see [Vision Package](#5.1) and [Text Package](#5.2).

## Package Structure and Dependencies

The Python backend is organized into multiple independently versioned packages that work together to provide responsible AI capabilities.

### Core Package Hierarchy

```mermaid
graph TB
    subgraph "Foundation"
        raiutils["raiutils<br/>v0.4.2<br/>Common utilities,<br/>exceptions, retries"]
    end
    
    subgraph "Analysis Engines"
        erroranalysis["erroranalysis<br/>v0.5.4<br/>Error tree/matrix,<br/>cohort filtering"]
        rai_core_flask["rai-core-flask<br/>v0.7.6<br/>Flask server,<br/>SocketIO endpoints"]
    end
    
    subgraph "Core Integration"
        responsibleai["responsibleai<br/>v0.36.0<br/>RAIInsights API,<br/>Manager orchestration"]
        raiwidgets["raiwidgets<br/>v0.36.0<br/>Dashboard launcher,<br/>Jupyter integration"]
    end
    
    subgraph "External ML Libraries"
        dice["dice-ml<br/>Counterfactuals"]
        econml["EconML<br/>Causal inference"]
        interpret["interpret-community<br/>Model explanations"]
        fairlearn["fairlearn==0.7.0<br/>Fairness metrics"]
        sklearn["scikit-learn"]
        lightgbm["LightGBM<br/>Surrogate models"]
    end
    
    erroranalysis --> raiutils
    erroranalysis --> sklearn
    erroranalysis --> lightgbm
    rai_core_flask --> raiutils
    
    responsibleai --> raiutils
    responsibleai --> erroranalysis
    responsibleai --> dice
    responsibleai --> econml
    responsibleai --> interpret
    responsibleai --> sklearn
    
    raiwidgets --> rai_core_flask
    raiwidgets --> erroranalysis
    raiwidgets --> fairlearn
    raiwidgets --> raiutils
```

**Sources:** [responsibleai/requirements.txt:1-22](), [raiwidgets/requirements.txt:1-10](), [erroranalysis/requirements.txt:1-6](), [rai_core_flask/requirements.txt:1-8]()

### Dependency Version Constraints

| Package | Key Dependencies | Version Constraints |
|---------|-----------------|---------------------|
| `responsibleai` | dice-ml | >=0.11,<0.12 |
| | econml | >=0.14.1 |
| | erroranalysis | >=0.5.4 |
| | interpret-community | >=0.31.0 |
| | scikit-learn | >=0.22.1,!=1.1,<=1.5.1 |
| | raiutils | >=0.4.2 |
| `raiwidgets` | rai-core-flask | >=0.7.6 |
| | erroranalysis | >=0.5.4 |
| | fairlearn | ==0.7.0 (exact) |
| `erroranalysis` | lightgbm | >=2.0.11 |
| | raiutils | >=0.4.2 |

**Sources:** [responsibleai/requirements.txt:1-22](), [raiwidgets/requirements.txt:1-10]()

## RAIInsights Entry Point Architecture

The `RAIInsights` class serves as the primary user-facing API for tabular data analysis. It inherits from `RAIBaseInsights` and orchestrates all analysis components.

### Class Hierarchy and Initialization

```mermaid
graph TB
    subgraph "User Interface"
        User["Data Scientist<br/>Jupyter Notebook"]
    end
    
    subgraph "RAIInsights Class Structure"
        RAIBaseInsights["RAIBaseInsights<br/>responsibleai/rai_insights/rai_base_insights.py:29-347<br/>Abstract base class"]
        RAIInsights["RAIInsights<br/>responsibleai/rai_insights/rai_insights.py:141-1465<br/>Main API for tabular data"]
        RAIVisionInsights["RAIVisionInsights<br/>responsibleai_vision<br/>For image models"]
        RAITextInsights["RAITextInsights<br/>responsibleai_text<br/>For NLP models"]
        
        RAIBaseInsights -."|extends|".-> RAIInsights
        RAIBaseInsights -."|extends|".-> RAIVisionInsights
        RAIBaseInsights -."|extends|".-> RAITextInsights
    end
    
    subgraph "Constructor Parameters"
        ModelParam["model: Any<br/>sklearn-style or callable"]
        TrainParam["train: pd.DataFrame<br/>with target column"]
        TestParam["test: pd.DataFrame<br/>with target column"]
        TaskParam["task_type: str<br/>classification|regression|forecasting"]
        MetadataParam["feature_metadata: FeatureMetadata<br/>categorical, dropped features"]
    end
    
    subgraph "Validation Steps"
        ValidateInputs["_validate_rai_insights_input_parameters()<br/>rai_insights.py:440-639"]
        ValidateModel["_ensure_model_outputs()<br/>Verify predict/predict_proba"]
        ValidateClasses["_validate_classes()<br/>For classification tasks"]
        ValidateMetadata["_validate_feature_metadata()<br/>rai_insights.py:697-834"]
    end
    
    User -->|"RAIInsights(...)"| RAIInsights
    ModelParam --> RAIInsights
    TrainParam --> RAIInsights
    TestParam --> RAIInsights
    TaskParam --> RAIInsights
    MetadataParam --> RAIInsights
    
    RAIInsights --> ValidateInputs
    ValidateInputs --> ValidateModel
    ValidateInputs --> ValidateClasses
    ValidateInputs --> ValidateMetadata
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:141-263](), [responsibleai/rai_insights/rai_base_insights.py:29-77]()

### Model Output Caching Strategy

The `RAIInsights` class caches model predictions to avoid recomputation across different managers. This is handled through a sophisticated output caching system that supports both small and large datasets.

```mermaid
graph LR
    subgraph "Model Methods by Task"
        ClassificationMethods["Classification:<br/>predict() [required]<br/>predict_proba() [required]"]
        RegressionMethods["Regression:<br/>predict() [required]"]
        ForecastingMethods["Forecasting:<br/>forecast() [required]<br/>forecast_quantiles() [optional]"]
    end
    
    subgraph "Cached Outputs"
        PredictOutput["_predict_output<br/>rai_insights.py:211"]
        PredictProbaOutput["_predict_proba_output<br/>rai_insights.py:213"]
        ForecastOutput["_forecast_output<br/>rai_insights.py:212"]
        QuantilesOutput["_forecast_quantiles_output<br/>rai_insights.py:214"]
    end
    
    subgraph "Large Dataset Outputs"
        LargePredictOutput["_large_predict_output<br/>rai_insights.py:215<br/>For test sets > 5000"]
        LargePredictProbaOutput["_large_predict_proba_output<br/>rai_insights.py:217"]
    end
    
    subgraph "Cache Population"
        SetModelOutputs["_set_model_outputs()<br/>rai_insights.py:1227-1267<br/>Called in __init__"]
    end
    
    ClassificationMethods --> SetModelOutputs
    RegressionMethods --> SetModelOutputs
    ForecastingMethods --> SetModelOutputs
    
    SetModelOutputs --> PredictOutput
    SetModelOutputs --> PredictProbaOutput
    SetModelOutputs --> ForecastOutput
    SetModelOutputs --> QuantilesOutput
    SetModelOutputs --> LargePredictOutput
    SetModelOutputs --> LargePredictProbaOutput
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:211-218](), [responsibleai/rai_insights/rai_insights.py:1227-1267](), [responsibleai/rai_insights/rai_insights.py:72-139]()

### Task-Specific Model Method Validation

```mermaid
graph TB
    subgraph "ModelMethod Class"
        ModelMethod["ModelMethod<br/>rai_insights.py:100-104<br/>name, optional, purpose"]
    end
    
    subgraph "MODEL_METHODS Dictionary"
        ClassTask["ModelTask.CLASSIFICATION:<br/>[predict: required,<br/>predict_proba: required]"]
        RegTask["ModelTask.REGRESSION:<br/>[predict: required]"]
        ForeTask["ModelTask.FORECASTING:<br/>[forecast: required,<br/>forecast_quantiles: optional]"]
    end
    
    subgraph "Validation Logic"
        EnsureOutputs["_ensure_model_outputs()<br/>rai_insights.py:1269-1312<br/>Validates each method"]
        WrapModel["_wrap_model_if_needed()<br/>Wraps forecasting models"]
    end
    
    subgraph "Error Handling"
        UserException["UserConfigValidationException<br/>_MODEL_METHOD_EXCEPTION_MESSAGE<br/>rai_insights.py:56-57"]
    end
    
    ModelMethod --> ClassTask
    ModelMethod --> RegTask
    ModelMethod --> ForeTask
    
    ClassTask --> EnsureOutputs
    RegTask --> EnsureOutputs
    ForeTask --> EnsureOutputs
    
    EnsureOutputs -->|"method fails"| UserException
    EnsureOutputs -->|"forecasting"| WrapModel
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:100-138](), [responsibleai/rai_insights/rai_insights.py:1269-1312]()

## Manager Pattern and Orchestration

The `RAIInsights` class uses a manager pattern where each type of analysis (causal, counterfactual, error analysis, explainer, data balance) is handled by a dedicated manager. This enables modular, independent development of each capability.

### Manager Initialization Flow

```mermaid
graph TB
    subgraph "RAIInsights Constructor"
        Init["__init__()<br/>rai_insights.py:148-263"]
        InitManagers["_initialize_managers()<br/>rai_insights.py:372-414"]
    end
    
    subgraph "Manager Instantiation"
        CausalMgr["CausalManager<br/>responsibleai/managers/causal_manager.py<br/>_causal_manager"]
        CFMgr["CounterfactualManager<br/>responsibleai/managers/counterfactual_manager.py<br/>_counterfactual_manager"]
        DBMgr["DataBalanceManager<br/>responsibleai/managers/data_balance_manager.py<br/>_data_balance_manager"]
        ErrorMgr["ErrorAnalysisManager<br/>responsibleai/managers/error_analysis_manager.py<br/>_error_analysis_manager"]
        ExplainerMgr["ExplainerManager<br/>responsibleai/managers/explainer_manager.py<br/>_explainer_manager"]
    end
    
    subgraph "Manager List"
        ManagersList["_managers = [<br/>_causal_manager,<br/>_counterfactual_manager,<br/>_data_balance_manager,<br/>_error_analysis_manager,<br/>_explainer_manager<br/>]<br/>rai_insights.py:410-414"]
    end
    
    subgraph "Forecasting Special Case"
        ForecastCheck["if task_type == FORECASTING:<br/>_managers = []<br/>return<br/>rai_insights.py:378-380"]
    end
    
    Init --> InitManagers
    InitManagers --> ForecastCheck
    InitManagers --> CausalMgr
    InitManagers --> CFMgr
    InitManagers --> DBMgr
    InitManagers --> ErrorMgr
    InitManagers --> ExplainerMgr
    
    CausalMgr --> ManagersList
    CFMgr --> ManagersList
    DBMgr --> ManagersList
    ErrorMgr --> ManagersList
    ExplainerMgr --> ManagersList
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:372-414](), [responsibleai/rai_insights/rai_insights.py:29-34]()

### Manager Configuration and Computation Phase

Each manager follows a two-phase pattern: configuration (via `add()` methods) and computation (via `compute()` method).

```mermaid
graph LR
    subgraph "User Configuration Phase"
        UserAddCausal["rai.causal.add(<br/>treatment_features=[...]<br/>)"]
        UserAddExplainer["rai.explainer.add(<br/>method='shap'<br/>)"]
        UserAddError["rai.error_analysis.add(<br/>max_depth=3<br/>)"]
        UserAddCF["rai.counterfactual.add(<br/>total_CFs=10<br/>)"]
    end
    
    subgraph "Manager State"
        ConfigStored["Configuration stored<br/>in manager instance<br/>Not yet computed"]
    end
    
    subgraph "Compute Synchronization"
        ComputeCall["rai.compute()<br/>rai_base_insights.py:84-87"]
        ManagerCompute["for manager in _managers:<br/>manager.compute()"]
    end
    
    subgraph "Manager Computation"
        CausalCompute["CausalManager.compute()<br/>Calls EconML"]
        ExplainerCompute["ExplainerManager.compute()<br/>Calls InterpretML"]
        ErrorCompute["ErrorAnalysisManager.compute()<br/>Builds surrogate tree"]
        CFCompute["CounterfactualManager.compute()<br/>Calls DiCE"]
    end
    
    UserAddCausal --> ConfigStored
    UserAddExplainer --> ConfigStored
    UserAddError --> ConfigStored
    UserAddCF --> ConfigStored
    
    ConfigStored --> ComputeCall
    ComputeCall --> ManagerCompute
    
    ManagerCompute --> CausalCompute
    ManagerCompute --> ExplainerCompute
    ManagerCompute --> ErrorCompute
    ManagerCompute --> CFCompute
```

**Sources:** [responsibleai/rai_insights/rai_base_insights.py:84-87]()

### Manager Names and Constants

```mermaid
graph TB
    subgraph "ManagerNames Constants"
        Constants["class ManagerNames:<br/>responsibleai/_internal/constants.py:7-14"]
        Causal["CAUSAL = 'causal'"]
        CF["COUNTERFACTUAL = 'counterfactual'"]
        DB["DATA_BALANCE = 'data_balance'"]
        EA["ERROR_ANALYSIS = 'error_analysis'"]
        Exp["EXPLAINER = 'explainer'"]
    end
    
    subgraph "Used For"
        Serialization["Directory names<br/>in save/load"]
        AccessProps["Public properties:<br/>rai.causal<br/>rai.counterfactual<br/>rai.error_analysis<br/>rai.explainer"]
        ManagerMap["Manager class mapping<br/>in load() methods"]
    end
    
    Constants --> Causal
    Constants --> CF
    Constants --> DB
    Constants --> EA
    Constants --> Exp
    
    Causal --> Serialization
    Causal --> AccessProps
    Causal --> ManagerMap
```

**Sources:** [responsibleai/_internal/constants.py:7-14]()

## Data Handling and Feature Processing

### Feature Metadata and Dropped Features

The `FeatureMetadata` class allows users to specify which features should be dropped, which are categorical, and other metadata. The `RAIInsights` class provides accessor methods that handle dropped features transparently.

```mermaid
graph TB
    subgraph "FeatureMetadata Class"
        FM["FeatureMetadata<br/>responsibleai/feature_metadata.py"]
        CatFeats["categorical_features: List[str]"]
        DroppedFeats["dropped_features: List[str]"]
        IdentityFeat["identity_feature_name: str"]
        DatetimeFeats["datetime_features: List[str]"]
        TSIDFeats["time_series_id_features: List[str]"]
    end
    
    subgraph "RAIInsights Data Accessors"
        GetTrainData["get_train_data()<br/>rai_insights.py:273-289<br/>Returns train with dropped features removed"]
        GetTestData["get_test_data()<br/>rai_insights.py:291-312<br/>Returns test with dropped features removed"]
        GetCatAfterDrop["get_categorical_features_after_drop()<br/>rai_insights.py:265-271<br/>Removes dropped from categorical list"]
    end
    
    subgraph "Manager Usage"
        MgrUseData["Managers call:<br/>get_train_data()<br/>get_test_data()<br/>get_categorical_features_after_drop()"]
    end
    
    FM --> CatFeats
    FM --> DroppedFeats
    FM --> IdentityFeat
    FM --> DatetimeFeats
    FM --> TSIDFeats
    
    DroppedFeats --> GetTrainData
    DroppedFeats --> GetTestData
    DroppedFeats --> GetCatAfterDrop
    
    GetTrainData --> MgrUseData
    GetTestData --> MgrUseData
    GetCatAfterDrop --> MgrUseData
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:265-312](), [responsibleai/rai_insights/rai_insights.py:382-408]()

### Categorical Feature Processing

```mermaid
graph LR
    subgraph "Input"
        RawData["test: pd.DataFrame<br/>categorical_features: List[str]"]
    end
    
    subgraph "Processing Pipeline"
        ProcessCat["process_categoricals()<br/>erroranalysis/_internal/process_categoricals.py<br/>Called in __init__"]
    end
    
    subgraph "Stored Artifacts"
        Categories["_categories: List<br/>Unique values per cat feature<br/>rai_insights.py:245"]
        CatIndexes["_categorical_indexes: List[int]<br/>Column indices<br/>rai_insights.py:245"]
        CatDict["_category_dictionary: Dict<br/>Feature->values mapping<br/>rai_insights.py:246"]
        StringIndData["_string_ind_data: List<br/>Indexed categorical data<br/>rai_insights.py:246"]
    end
    
    RawData --> ProcessCat
    ProcessCat --> Categories
    ProcessCat --> CatIndexes
    ProcessCat --> CatDict
    ProcessCat --> StringIndData
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:245-250]()

### Feature Ranges Calculation

```mermaid
graph TB
    subgraph "Input Data"
        TestData["test DataFrame<br/>or _large_test if exists"]
        CategoricalList["categorical_features"]
        DatetimeList["datetime_features"]
    end
    
    subgraph "Calculation Method"
        GetRanges["_get_feature_ranges()<br/>rai_insights.py:835-990<br/>Static method"]
    end
    
    subgraph "Range Types"
        NumericRange["Numeric features:<br/>{'column_name': str,<br/>'range_type': 'numeric',<br/>'min_value': float,<br/>'max_value': float}"]
        CategoricalRange["Categorical features:<br/>{'column_name': str,<br/>'range_type': 'categorical',<br/>'unique_values': List}"]
        DatetimeRange["Datetime features:<br/>{'column_name': str,<br/>'range_type': 'datetime',<br/>'min_value': timestamp,<br/>'max_value': timestamp}"]
    end
    
    subgraph "Storage"
        FeatureRanges["_feature_ranges: List[Dict]<br/>rai_insights.py:240-244"]
    end
    
    TestData --> GetRanges
    CategoricalList --> GetRanges
    DatetimeList --> GetRanges
    
    GetRanges --> NumericRange
    GetRanges --> CategoricalRange
    GetRanges --> DatetimeRange
    
    NumericRange --> FeatureRanges
    CategoricalRange --> FeatureRanges
    DatetimeRange --> FeatureRanges
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:240-244](), [responsibleai/rai_insights/rai_insights.py:835-990]()

## Serialization and Persistence

The `RAIInsights` class supports saving and loading its complete state, including the model, data, managers, and computed results. This uses a directory-based structure with JSON and pickle files.

### Save Architecture

```mermaid
graph TB
    subgraph "Save Entry Point"
        SaveMethod["save(path)<br/>rai_base_insights.py:219-229"]
    end
    
    subgraph "Save Components"
        SaveManagers["_save_managers(path)<br/>rai_base_insights.py:208-217<br/>Calls manager._save()"]
        SaveData["_save_data(path)<br/>rai_base_insights.py:138-167<br/>Saves train/test DataFrames"]
        SaveMetadata["_save_metadata(path)<br/>rai_insights.py:991-1055<br/>Saves meta.json"]
        SaveModel["_save_model(path)<br/>rai_base_insights.py:179-206<br/>Pickle or custom serializer"]
        SavePredictions["_save_predictions(path)<br/>rai_insights.py:1057-1119<br/>Saves cached predictions"]
    end
    
    subgraph "File Structure"
        MetaJSON["meta.json<br/>Task type, target, features, classes"]
        ModelPKL["model.pkl<br/>or custom serializer output"]
        TrainJSON["data/train.json<br/>data/traindtypes.json"]
        TestJSON["data/test.json<br/>data/testdtypes.json"]
        PredictJSON["predictions/predict.json<br/>predictions/predict_proba.json"]
        ManagerDirs["causal/<UUID>/<br/>error_analysis/<UUID>/<br/>explainer/<UUID>/"]
    end
    
    SaveMethod --> SaveManagers
    SaveMethod --> SaveData
    SaveMethod --> SaveMetadata
    SaveMethod --> SaveModel
    SaveMethod --> SavePredictions
    
    SaveMetadata --> MetaJSON
    SaveModel --> ModelPKL
    SaveData --> TrainJSON
    SaveData --> TestJSON
    SavePredictions --> PredictJSON
    SaveManagers --> ManagerDirs
```

**Sources:** [responsibleai/rai_insights/rai_base_insights.py:219-229](), [responsibleai/rai_insights/rai_insights.py:991-1119]()

### Directory Structure on Disk

```
<save_path>/
├── meta.json                          # Metadata
├── rai_version.json                   # Package version
├── model.pkl                          # Serialized model
├── data/
│   ├── train.json                     # Training data
│   ├── traindtypes.json              # Column dtypes
│   ├── test.json                      # Test data
│   └── testdtypes.json               # Column dtypes
├── predictions/
│   ├── predict.json                   # Cached predictions
│   ├── predict_proba.json            # Cached probabilities
│   ├── large_predict.json            # Large dataset predictions
│   └── large_predict_proba.json      # Large dataset probabilities
├── causal/
│   └── <uuid>/                        # Per-config directories
│       ├── data/                      # Computed results
│       └── generators/                # (not used)
├── counterfactual/
│   └── <uuid>/
│       ├── config/                    # Configuration
│       ├── data/                      # Computed results
│       └── generators/                # DiCE generators
├── error_analysis/
│   └── <uuid>/
│       ├── config/                    # Configuration
│       └── data/                      # Error reports
├── explainer/
│   └── <uuid>/
│       └── data/                      # Explanation results
└── data_balance/
    └── <uuid>/
        └── data/                      # Data balance measures
```

**Sources:** [responsibleai/_internal/constants.py:87-143](), [responsibleai/rai_insights/test_rai_insights.py:300-362]()

### Load Architecture

```mermaid
graph TB
    subgraph "Load Entry Point"
        LoadMethod["load(path)<br/>rai_insights.py:1121-1191<br/>@staticmethod"]
    end
    
    subgraph "Load Components"
        LoadData["_load_data(inst, path)<br/>rai_base_insights.py:232-258<br/>Loads DataFrames"]
        LoadMetadata["_load_metadata(inst, path)<br/>rai_insights.py:1193-1225<br/>Loads meta.json"]
        LoadModel["_load_model(inst, path)<br/>rai_base_insights.py:260-300<br/>Unpickle or custom"]
        LoadManagers["_load_managers(inst, path, manager_map)<br/>rai_base_insights.py:302-323<br/>Reconstructs managers"]
        LoadPredictions["Predictions loaded on-demand<br/>via _get_<method>_output()"]
    end
    
    subgraph "Manager Map"
        MgrMap["manager_map = {<br/>ManagerNames.CAUSAL: CausalManager,<br/>ManagerNames.COUNTERFACTUAL: CounterfactualManager,<br/>ManagerNames.ERROR_ANALYSIS: ErrorAnalysisManager,<br/>ManagerNames.EXPLAINER: ExplainerManager,<br/>ManagerNames.DATA_BALANCE: DataBalanceManager<br/>}<br/>rai_insights.py:1165-1171"]
    end
    
    subgraph "Instance Creation"
        EmptyInit["inst = object.__new__(RAIInsights)<br/>rai_insights.py:1151"]
        BaseLoad["RAIBaseInsights._load(<br/>path, inst, manager_map, load_metadata_func<br/>)<br/>rai_base_insights.py:326-346"]
    end
    
    LoadMethod --> EmptyInit
    EmptyInit --> MgrMap
    MgrMap --> BaseLoad
    
    BaseLoad --> LoadData
    BaseLoad --> LoadMetadata
    BaseLoad --> LoadModel
    BaseLoad --> LoadManagers
    
    LoadManagers --> LoadPredictions
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:1121-1191](), [responsibleai/rai_insights/rai_base_insights.py:326-346]()

### Metadata JSON Schema

The `meta.json` file contains essential information for reconstruction:

```json
{
  "task_type": "classification|regression|forecasting",
  "target_column": "string",
  "classes": ["class1", "class2", ...],  // for classification
  "feature_columns": ["feature1", "feature2", ...],
  "feature_ranges": [
    {
      "column_name": "feature1",
      "range_type": "numeric|categorical|datetime",
      "min_value": 0.0,
      "max_value": 100.0
    }
  ],
  "categorical_features": ["cat1", "cat2", ...],
  "categories": [["val1", "val2"], ...],
  "category_dictionary": {"cat1": ["val1", "val2"]},
  "categorical_indexes": [0, 1, ...],
  "string_ind_data": [...],
  "number_large_test_samples": 10000,  // if large dataset
  "feature_metadata": {
    "categorical_features": [...],
    "dropped_features": [...],
    "identity_feature_name": "string",
    "datetime_features": [...],
    "time_series_id_features": [...]
  }
}
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:991-1055](), [responsibleai/_internal/constants.py:17-35]()

## Model Wrapping and Validation

### Model Interface Validation

The `RAIInsights` class validates that the provided model implements the required methods for the specified task type.

```mermaid
graph TB
    subgraph "Validation Entry"
        ValidateParams["_validate_rai_insights_input_parameters()<br/>rai_insights.py:440-639"]
    end
    
    subgraph "Model Checks"
        HasModel["if model is not None"]
        WrapIfNeeded["_wrap_model_if_needed(model)<br/>rai_insights.py:621"]
        EnsureOutputs["_ensure_model_outputs(input_data)<br/>rai_insights.py:626-627<br/>Called on train and test"]
    end
    
    subgraph "Output Validation"
        TryMethod["Try calling model method<br/>with input_data"]
        CheckOutput["Verify output shape/type<br/>Ensure input unchanged"]
        RaiseError["UserConfigValidationException<br/>_MODEL_METHOD_EXCEPTION_MESSAGE"]
    end
    
    subgraph "Special Cases"
        NoModel["model is None:<br/>warn INVALID-MODEL-WARNING<br/>rai_insights.py:493-497"]
        Regression["Regression task:<br/>Verify no predict_proba<br/>rai_insights.py:629-634"]
        Forecasting["Forecasting task:<br/>Wrap model with adapter<br/>_forecasting_wrappers.py"]
    end
    
    ValidateParams --> HasModel
    HasModel -->|Yes| WrapIfNeeded
    HasModel -->|No| NoModel
    WrapIfNeeded --> EnsureOutputs
    EnsureOutputs --> TryMethod
    TryMethod -->|Success| CheckOutput
    TryMethod -->|Failure| RaiseError
    
    WrapIfNeeded --> Forecasting
    EnsureOutputs --> Regression
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:440-639](), [responsibleai/rai_insights/rai_insights.py:1269-1312]()

### Forecasting Model Wrapper

For forecasting tasks, models are wrapped to provide a consistent interface:

```mermaid
graph LR
    subgraph "Original Model"
        UserModel["User's forecasting model<br/>with forecast() method"]
    end
    
    subgraph "Wrapper Function"
        WrapModel["_wrap_model(model, task_type)<br/>responsibleai/_internal/_forecasting_wrappers.py"]
    end
    
    subgraph "Wrapped Interface"
        WrappedModel["Wrapped model<br/>Compatible with RAI pipeline"]
        ForecastMethod["forecast(X) -> predictions"]
        QuantilesMethod["forecast_quantiles(X, quantiles) -> quantiles<br/>(if supported)"]
    end
    
    UserModel --> WrapModel
    WrapModel --> WrappedModel
    WrappedModel --> ForecastMethod
    WrappedModel --> QuantilesMethod
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:621](), [responsibleai/_internal/_forecasting_wrappers.py:24]()

## Supporting Infrastructure

### Exception Hierarchy

The backend uses structured exceptions from `raiutils` to provide clear error messages:

```mermaid
graph TB
    subgraph "Exception Classes"
        UserConfigException["UserConfigValidationException<br/>raiutils.exceptions<br/>User input errors"]
        SystemException["SystemErrorException<br/>raiutils.exceptions<br/>Internal errors"]
    end
    
    subgraph "Usage Examples"
        BadTaskType["Unsupported task_type<br/>rai_insights.py:489-491"]
        BadTarget["Target column not in data<br/>rai_insights.py:536-539"]
        BadCategorical["Categorical feature not in data<br/>rai_insights.py:549-555"]
        ModelFail["Model method failure<br/>rai_insights.py:1298-1302"]
        FeatureConvert["Unable to convert feature range<br/>rai_insights.py:976-980"]
    end
    
    UserConfigException --> BadTaskType
    UserConfigException --> BadTarget
    UserConfigException --> BadCategorical
    UserConfigException --> ModelFail
    SystemException --> FeatureConvert
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:19-20](), [responsibleai/rai_insights/rai_insights.py:489-639]()

### Constants and File Formats

```mermaid
graph TB
    subgraph "Metadata Constants"
        MetadataClass["class Metadata<br/>responsibleai/_internal/constants.py:17-35"]
        META_JSON["META_JSON = 'meta.json'"]
        TRAIN["TRAIN = 'train'"]
        TEST["TEST = 'test'"]
        TASK_TYPE["TASK_TYPE = 'task_type'"]
        TARGET_COLUMN["TARGET_COLUMN = 'target_column'"]
        CLASSES["CLASSES = 'classes'"]
        FEATURE_COLUMNS["FEATURE_COLUMNS = 'feature_columns'"]
        CATEGORICAL_FEATURES["CATEGORICAL_FEATURES = 'categorical_features'"]
    end
    
    subgraph "File Format Constants"
        FileFormats["class FileFormats<br/>constants.py:134-138"]
        JSON[".JSON = '.json'"]
        PKL[".PKL = '.pkl'"]
        TXT[".TXT = '.txt'"]
    end
    
    subgraph "Serialization Attributes"
        SerializationAttr["class SerializationAttributes<br/>constants.py:95-132"]
        RESULTS_DIR["RESULTS_DIRECTORY = 'results'"]
        PREDICTIONS_DIR["PREDICTIONS_DIRECTORY = 'predictions'"]
        DATA_DIR["DATA_DIRECTORY = 'data'"]
        MODEL_PKL["MODEL_PKL = 'model.pkl'"]
        PREDICT_JSON["PREDICT_JSON = 'predict.json'"]
        PREDICT_PROBA_JSON["PREDICT_PROBA_JSON = 'predict_proba.json'"]
    end
    
    MetadataClass --> META_JSON
    MetadataClass --> TRAIN
    MetadataClass --> TEST
    MetadataClass --> TASK_TYPE
    
    FileFormats --> JSON
    FileFormats --> PKL
    
    SerializationAttr --> RESULTS_DIR
    SerializationAttr --> PREDICTIONS_DIR
    SerializationAttr --> DATA_DIR
    SerializationAttr --> MODEL_PKL
    SerializationAttr --> PREDICT_JSON
```

**Sources:** [responsibleai/_internal/constants.py:17-143]()

### Model Serving Integration

The `RAIBaseInsights` class supports loading models from a locally served endpoint instead of a pickled file, enabling deployment scenarios:

```mermaid
graph LR
    subgraph "Environment Detection"
        EnvVar["RAI_MODEL_SERVING_PORT<br/>environment variable"]
    end
    
    subgraph "Load Logic"
        CheckEnv["_load_model(inst, path)<br/>rai_base_insights.py:260-300"]
        CheckPort["model_serving_port = os.getenv(<br/>RAI_MODEL_SERVING_PORT_ENV_VAR<br/>)"]
    end
    
    subgraph "Model Source"
        ServedModel["ServedModelWrapper(port)<br/>responsibleai/_internal/_served_model_wrapper.py<br/>Makes HTTP calls to localhost"]
        PickledModel["Unpickle from model.pkl<br/>or custom serializer"]
    end
    
    EnvVar --> CheckPort
    CheckPort -->|"port is set"| ServedModel
    CheckPort -->|"port is None"| PickledModel
    CheckEnv --> CheckPort
```

**Sources:** [responsibleai/rai_insights/rai_base_insights.py:260-300](), [responsibleai/_internal/constants.py:141-143]()

### Large Dataset Handling

When test datasets exceed the `maximum_rows_for_test` threshold (default 5000), RAIInsights stores the full dataset separately and uses a subset for interactive operations:

```mermaid
graph TB
    subgraph "Initialization Check"
        CheckSize["len(test) > maximum_rows_for_test<br/>rai_insights.py:199-206"]
    end
    
    subgraph "Data Split"
        Warning["warnings.warn(<br/>size exceeds limit<br/>)"]
        StoreLarge["_large_test = test.copy()<br/>rai_insights.py:205"]
        TruncateTest["test = test[0:maximum_rows_for_test]<br/>rai_insights.py:206"]
    end
    
    subgraph "Cached Outputs"
        SmallOutputs["_predict_output<br/>_predict_proba_output<br/>for test subset"]
        LargeOutputs["_large_predict_output<br/>_large_predict_proba_output<br/>for full test set"]
    end
    
    subgraph "Feature Ranges"
        UseFullData["Feature ranges computed<br/>on _large_test if exists<br/>rai_insights.py:241"]
    end
    
    CheckSize -->|Yes| Warning
    Warning --> StoreLarge
    StoreLarge --> TruncateTest
    
    TruncateTest --> SmallOutputs
    StoreLarge --> LargeOutputs
    StoreLarge --> UseFullData
```

**Sources:** [responsibleai/rai_insights/rai_insights.py:199-206](), [responsibleai/rai_insights/rai_insights.py:215-218](), [responsibleai/rai_insights/rai_insights.py:240-244]()

---

