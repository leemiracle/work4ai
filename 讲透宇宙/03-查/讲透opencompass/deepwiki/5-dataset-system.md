<!-- source: DeepWiki mcp.deepwiki.com · repo open-compass/opencompass · page 5 Dataset System · fetched 2026-10-21 -->

# Dataset System

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [dataset-index.yml](dataset-index.yml)
- [opencompass/configs/datasets/IFBench/IFBench_gen.py](opencompass/configs/datasets/IFBench/IFBench_gen.py)
- [opencompass/configs/datasets/MedCalc_Bench/MedCalcBench_official_gen_a5155f.py](opencompass/configs/datasets/MedCalc_Bench/MedCalcBench_official_gen_a5155f.py)
- [opencompass/configs/datasets/srbench/srbench_gen.py](opencompass/configs/datasets/srbench/srbench_gen.py)
- [opencompass/configs/summarizers/groups/biodata.py](opencompass/configs/summarizers/groups/biodata.py)
- [opencompass/datasets/IFBench/evaluation_lib.py](opencompass/datasets/IFBench/evaluation_lib.py)
- [opencompass/datasets/IFBench/ifbench.py](opencompass/datasets/IFBench/ifbench.py)
- [opencompass/datasets/IFBench/instructions.py](opencompass/datasets/IFBench/instructions.py)
- [opencompass/datasets/IFBench/instructions_registry.py](opencompass/datasets/IFBench/instructions_registry.py)
- [opencompass/datasets/IFBench/instructions_util.py](opencompass/datasets/IFBench/instructions_util.py)
- [opencompass/datasets/MedCalc_Bench.py](opencompass/datasets/MedCalc_Bench.py)
- [opencompass/datasets/__init__.py](opencompass/datasets/__init__.py)
- [opencompass/datasets/scicode.py](opencompass/datasets/scicode.py)
- [opencompass/datasets/srbench.py](opencompass/datasets/srbench.py)
- [opencompass/utils/datasets_info.py](opencompass/utils/datasets_info.py)
- [requirements/extra.txt](requirements/extra.txt)

</details>



The Dataset System is OpenCompass's comprehensive framework for managing, loading, and evaluating benchmarks across hundreds of datasets. This system provides a unified interface for handling diverse evaluation tasks ranging from multiple-choice questions to code generation and long-context understanding.

For information about model integration with datasets, see [Model Support](#4). For details on evaluation methodologies, see [Evaluation Methods](#6).

## Dataset Registry Architecture

The dataset system uses a registry-based architecture where all datasets are registered as modules and can be dynamically loaded based on configuration.

```mermaid
graph TB
    subgraph "Dataset Registration System"
        LOAD_DATASET["@LOAD_DATASET.register_module()"]
        BaseDataset["BaseDataset"]
        DatasetClasses["SciCodeDataset<br/>SeedBenchDataset<br/>MMluDataset<br/>..."]
    end
    
    subgraph "Dataset Index Registry"
        DatasetIndex["dataset-index.yml<br/>600+ datasets"]
        ConfigPaths["configpath mappings<br/>Category classifications<br/>Paper references"]
    end
    
    subgraph "Storage Management"
        DATASETS_MAPPING["DATASETS_MAPPING<br/>Storage locations"]
        HF["HuggingFace Hub"]
        MS["ModelScope"]
        Local["Local Files"]
        URLs["DATASETS_URL<br/>Download links"]
    end
    
    subgraph "Data Loading Pipeline"
        get_data_path["get_data_path()"]
        DatasetLoader["Dataset.load()"]
        HFLoader["datasets.load_dataset()"]
        MSLoader["MsDataset.load()"]
    end
    
    LOAD_DATASET --> DatasetClasses
    DatasetClasses --> BaseDataset
    DatasetIndex --> ConfigPaths
    DATASETS_MAPPING --> HF
    DATASETS_MAPPING --> MS  
    DATASETS_MAPPING --> Local
    DATASETS_MAPPING --> URLs
    
    get_data_path --> DATASETS_MAPPING
    DatasetLoader --> get_data_path
    DatasetLoader --> HFLoader
    DatasetLoader --> MSLoader
```

**Dataset Registry Flow**
```mermaid
sequenceDiagram
    participant Config as "Dataset Config"
    participant Registry as "LOAD_DATASET Registry"
    participant DatasetClass as "Dataset Class"
    participant Storage as "Storage Backend"
    participant Loader as "Data Loader"
    
    Config->>Registry: Load dataset by type
    Registry->>DatasetClass: Instantiate registered class
    DatasetClass->>Storage: Resolve data path via get_data_path()
    Storage->>Storage: Check DATASETS_MAPPING
    Storage->>Loader: Load from HF/ModelScope/Local
    Loader->>DatasetClass: Return Dataset object
    DatasetClass->>Config: Ready for evaluation
```

Sources: [opencompass/datasets/__init__.py:1-182](), [opencompass/utils/datasets_info.py:1-507](), [dataset-index.yml:1-50]()

## Dataset Implementation Patterns

All datasets in OpenCompass follow a consistent implementation pattern using the `BaseDataset` class and registration decorators.

### Core Dataset Structure

```mermaid
classDiagram
    class BaseDataset {
        +load()
        +return_dataset()
    }
    
    class SciCodeDataset {
        +load(path, with_bg, **kwargs)
        +return_dataset()
    }
    
    class SeedBenchDataset {
        +load(data_files, path, split, **kwargs)  
    }
    
    class LOAD_DATASET {
        +register_module()
    }
    
    BaseDataset <|-- SciCodeDataset
    BaseDataset <|-- SeedBenchDataset
    LOAD_DATASET ..> SciCodeDataset : registers
    LOAD_DATASET ..> SeedBenchDataset : registers
    
    note for SciCodeDataset "Handles HDF5 data processing<br/>Scientific computing tasks"
    note for SeedBenchDataset "Agricultural domain benchmark<br/>Multi-task evaluation"
```

### Dataset Registration Pattern

All datasets use the `@LOAD_DATASET.register_module()` decorator pattern:

```python
@LOAD_DATASET.register_module()
class SciCodeDataset(BaseDataset):
    @staticmethod
    def load(path, with_bg, **kwargs):
        # Implementation specific loading logic
```

**Dataset Categories and Distribution**
```mermaid
pie title "Dataset Categories (600+ datasets)"
    "Language Understanding" : 25
    "Reasoning" : 20
    "Code Generation" : 15
    "Mathematics" : 12
    "Knowledge QA" : 10
    "Long Context" : 8
    "Safety & Bias" : 5
    "Multimodal" : 3
    "Other" : 2
```

Sources: [opencompass/datasets/base.py](), [opencompass/datasets/scicode.py:23-43](), [opencompass/datasets/SeedBench.py:19-48]()

## Storage and Data Distribution System

The system supports multiple storage backends and automatic dataset downloading through a comprehensive mapping system.

```mermaid
graph TB
    subgraph "Dataset Resolution Pipeline"
        DatasetID["Dataset Identifier<br/>'opencompass/mmlu'"]
        DATASETS_MAPPING_LOOKUP["DATASETS_MAPPING lookup"]
        StorageOptions["Storage Options"]
    end
    
    subgraph "Storage Backends"
        HF_ID["hf_id: HuggingFace Hub"]
        MS_ID["ms_id: ModelScope Hub"] 
        LOCAL["local: File path"]
    end
    
    subgraph "Download System"
        DATASETS_URL_LOOKUP["DATASETS_URL lookup"]
        HTTP_DOWNLOAD["HTTP Download"]
        MD5_VERIFY["MD5 Verification"]
    end
    
    subgraph "Path Resolution"
        get_data_path_func["get_data_path()"]
        ENV_CHECK["Environment Variable Check<br/>DATASET_SOURCE"]
        FINAL_PATH["Resolved Dataset Path"]
    end
    
    DatasetID --> DATASETS_MAPPING_LOOKUP
    DATASETS_MAPPING_LOOKUP --> StorageOptions
    StorageOptions --> HF_ID
    StorageOptions --> MS_ID
    StorageOptions --> LOCAL
    
    LOCAL --> DATASETS_URL_LOOKUP
    DATASETS_URL_LOOKUP --> HTTP_DOWNLOAD
    HTTP_DOWNLOAD --> MD5_VERIFY
    
    HF_ID --> get_data_path_func
    MS_ID --> get_data_path_func
    LOCAL --> get_data_path_func
    get_data_path_func --> ENV_CHECK
    ENV_CHECK --> FINAL_PATH
```

### Storage Mapping Examples

| Dataset ID | HuggingFace ID | ModelScope ID | Local Path | Download URL |
|------------|----------------|---------------|------------|--------------|
| `opencompass/mmlu` | `opencompass/mmlu` | `opencompass/mmlu` | `./data/mmlu/` | Auto-download |
| `opencompass/scicode` | - | - | `./data/scicode` | OSS URL with MD5 |
| `opencompass/seedbench` | `yj12869741/SeedBench` | `y12869741/SeedBench` | `./data/SeedBench` | - |

Sources: [opencompass/utils/datasets_info.py:1-507](), [opencompass/utils/datasets_info.py:509-886]()

## Evaluation Framework Integration

The dataset system integrates tightly with OpenCompass's evaluation framework through registered evaluators and standardized interfaces.

```mermaid
graph TB
    subgraph "Dataset Loading"
        DatasetClass["Dataset Class"]
        reader_cfg["reader_cfg<br/>Input/Output columns"]
        infer_cfg["infer_cfg<br/>Prompt templates"]
        eval_cfg["eval_cfg<br/>Evaluator config"]
    end
    
    subgraph "Evaluation Pipeline"
        ICL_EVALUATORS["ICL_EVALUATORS Registry"]
        EvaluatorTypes["AccEvaluator<br/>RougeEvaluator<br/>F1ScoreEvaluator<br/>Custom Evaluators"]
        PostProcessors["TEXT_POSTPROCESSORS<br/>first_option_postprocess<br/>my_multiple_select_postprocess"]
    end
    
    subgraph "Task Execution"
        OpenICLInferTask["OpenICLInferTask"]
        OpenICLEvalTask["OpenICLEvalTask"]  
        Predictions["Model Predictions"]
        Results["Evaluation Results"]
    end
    
    DatasetClass --> reader_cfg
    DatasetClass --> infer_cfg  
    DatasetClass --> eval_cfg
    
    eval_cfg --> ICL_EVALUATORS
    ICL_EVALUATORS --> EvaluatorTypes
    eval_cfg --> PostProcessors
    
    infer_cfg --> OpenICLInferTask
    eval_cfg --> OpenICLEvalTask
    OpenICLInferTask --> Predictions
    Predictions --> PostProcessors
    PostProcessors --> EvaluatorTypes
    EvaluatorTypes --> Results
```

### Evaluator Registration Pattern

```python
@ICL_EVALUATORS.register_module()
class SciCodeEvaluator(BaseEvaluator):
    def score(self, predictions, references):
        # Custom evaluation logic
        return result
```

**Common Evaluation Patterns**
```mermaid
flowchart LR
    subgraph "Multiple Choice"
        MC_Input["ABCD options"]
        first_option["first_option_postprocess"]
        AccEvaluator["AccEvaluator"]
        MC_Input --> first_option --> AccEvaluator
    end
    
    subgraph "Multi-Select"
        MS_Input["ABC selection"]  
        multi_select["my_multiple_select_postprocess"]
        F1ScoreEvaluator["F1ScoreEvaluator"]
        MS_Input --> multi_select --> F1ScoreEvaluator
    end
    
    subgraph "Generation Tasks"
        Gen_Input["Text generation"]
        RougeEvaluator["RougeEvaluator"]
        Gen_Input --> RougeEvaluator
    end
    
    subgraph "Code Execution"
        Code_Input["Python code"]
        CodeExecution["Code execution & testing"]
        SciCodeEvaluator["SciCodeEvaluator"]
        Code_Input --> CodeExecution --> SciCodeEvaluator
    end
```

Sources: [opencompass/datasets/scicode.py:219-364](), [opencompass/datasets/SeedBench.py:135-309](), [opencompass/configs/datasets/SeedBench/seedbench_gen_5d5ea1.py:1-75]()

## Dataset Configuration Management

Dataset configurations are managed through a hierarchical system of YAML metadata and Python configuration files.

```mermaid
graph TB
    subgraph "Configuration Hierarchy"
        DatasetIndexYML["dataset-index.yml<br/>Master registry"]
        CategoryMeta["Category metadata<br/>Paper references<br/>Config paths"]
        ConfigFiles["Python config files<br/>Reader/Infer/Eval configs"]
    end
    
    subgraph "Configuration Components" 
        reader_cfg_detail["reader_cfg:<br/>input_columns: ['question']<br/>output_column: 'answer'"]
        infer_cfg_detail["infer_cfg:<br/>prompt_template<br/>retriever: ZeroRetriever<br/>inferencer: GenInferencer"]
        eval_cfg_detail["eval_cfg:<br/>evaluator: AccEvaluator<br/>pred_postprocessor"]
    end
    
    subgraph "Runtime Assembly"
        ConfigLoader["Configuration Loader"]
        DatasetInstance["Dataset Instance"]
        TaskCreation["Task Creation"]
    end
    
    DatasetIndexYML --> CategoryMeta
    CategoryMeta --> ConfigFiles
    ConfigFiles --> reader_cfg_detail
    ConfigFiles --> infer_cfg_detail  
    ConfigFiles --> eval_cfg_detail
    
    reader_cfg_detail --> ConfigLoader
    infer_cfg_detail --> ConfigLoader
    eval_cfg_detail --> ConfigLoader
    ConfigLoader --> DatasetInstance
    DatasetInstance --> TaskCreation
```

### Configuration Example Structure

| Component | Purpose | Example |
|-----------|---------|---------|
| `reader_cfg` | Define input/output columns | `{'input_columns': ['question'], 'output_column': 'answer'}` |
| `infer_cfg` | Prompt template and inference | `{'prompt_template': PromptTemplate, 'retriever': ZeroRetriever}` |
| `eval_cfg` | Evaluation method | `{'evaluator': AccEvaluator, 'pred_postprocessor': first_option_postprocess}` |

**Dataset Metadata Structure**
```mermaid
graph LR
    subgraph "dataset-index.yml Entry"
        DatasetName["Dataset Name"]
        Category["category: 'Reasoning'"]
        Paper["paper: 'arxiv.org/...'"] 
        ConfigPath["configpath: 'configs/.../gen.py'"]
        LLMJudgePath["configpath_llmjudge: '...'"]
    end
    
    DatasetName --> Category
    DatasetName --> Paper
    DatasetName --> ConfigPath
    DatasetName --> LLMJudgePath
```

Sources: [dataset-index.yml:1-886](), [opencompass/configs/datasets/SeedBench/seedbench_gen_5d5ea1.py:9-29]()

## Specialized Dataset Examples

The system supports highly specialized datasets with custom evaluation logic and data processing requirements.

### SciCode: Scientific Computing Evaluation

```mermaid
graph TB
    subgraph "SciCode Pipeline"
        SciCodeData["SciCode JSON data<br/>with_bg parameter"]
        HDF5Data["HDF5 test data<br/>Scientific computing results"]
        PythonExtraction["extract_python_script()<br/>Code extraction from responses"]
    end
    
    subgraph "Code Execution Environment"
        ScriptGeneration["Generate test scripts<br/>Import statements + user code + tests"]
        ConcurrentExecution["ThreadPoolExecutor<br/>Concurrent script execution"]
        ResultCollection["Collect execution results<br/>0=success, 1=error, 2=timeout"]
    end
    
    subgraph "Scientific Data Processing"
        HDF5Processing["process_hdf5_to_tuple()<br/>Handle sparse matrices, arrays"]
        NumericComparison["are_dicts_close()<br/>numpy.allclose() with tolerances"]
        ScientificEval["Scientific result validation"]
    end
    
    SciCodeData --> PythonExtraction
    HDF5Data --> HDF5Processing
    PythonExtraction --> ScriptGeneration
    ScriptGeneration --> ConcurrentExecution
    ConcurrentExecution --> ResultCollection
    HDF5Processing --> NumericComparison
    NumericComparison --> ScientificEval
```

### SeedBench: Agricultural Domain Multi-task Evaluation  

```mermaid
graph TB
    subgraph "SeedBench Task Types"
        QA_Tasks["QA Tasks:<br/>QA-1: Multiple Choice<br/>QA-2: Multiple Answer<br/>QA-3: Fill-in-blank<br/>QA-4: Generation"]
        SUM_Tasks["Summarization:<br/>SUM-1: Simple Summary<br/>SUM-2: Key Info Extraction"]
        RC_Tasks["Reading Comprehension:<br/>RC-1 to RC-5<br/>Various formats"]
    end
    
    subgraph "Specialized Evaluators"
        F1ScoreEvaluator_SB["F1ScoreEvaluator<br/>Multiple answer validation"]
        AverageRougeScoreEvaluator_SB["AverageRougeScoreEvaluator<br/>Chinese text with jieba"]
        AccScoreStr_Evaluator_SB["AccScoreStr_Evaluator<br/>String matching"]
    end
    
    subgraph "Text Processing"
        ChineseProcessing["Chinese text processing<br/>jieba tokenization<br/>Rouge-Chinese scoring"]
        MultiSelectProcessing["my_multiple_select_postprocess<br/>ABC -> A,B,C format"]
    end
    
    QA_Tasks --> F1ScoreEvaluator_SB
    QA_Tasks --> AccScoreStr_Evaluator_SB
    SUM_Tasks --> AverageRougeScoreEvaluator_SB
    RC_Tasks --> ChineseProcessing
    
    F1ScoreEvaluator_SB --> MultiSelectProcessing
    AverageRougeScoreEvaluator_SB --> ChineseProcessing
```

Sources: [opencompass/datasets/scicode.py:45-364](), [opencompass/datasets/SeedBench.py:51-309](), [opencompass/configs/datasets/SeedBench/README.md:1-80]()

---

