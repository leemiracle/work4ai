<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-speech-data-processor · page 7 Testing and Quality Assurance · fetched 2026-10-26 -->

# Testing and Quality Assurance

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.github/workflows/tests.yml](.github/workflows/tests.yml)
- [.gitignore](.gitignore)
- [requirements/main.txt](requirements/main.txt)
- [sdp/processors/datasets/voxpopuli/normalize_from_non_pc_text.py](sdp/processors/datasets/voxpopuli/normalize_from_non_pc_text.py)
- [sdp/utils/apply_operators.py](sdp/utils/apply_operators.py)
- [tests/test_cfg_end_to_end_tests.py](tests/test_cfg_end_to_end_tests.py)
- [tests/test_data_to_data.py](tests/test_data_to_data.py)
- [tests/test_data_to_dropbool.py](tests/test_data_to_dropbool.py)

</details>



The NeMo Speech Data Processor (SDP) employs a comprehensive testing and quality assurance framework to ensure reliable dataset processing across diverse speech datasets and configurations. This system validates processor functionality, configuration correctness, and output quality through multiple testing layers including end-to-end validation, unit testing, and continuous integration.

For information about processor development and implementation, see [Core Architecture](#2). For dataset-specific processing details, see [Dataset Processing](#4).

## Testing Architecture Overview

The SDP testing framework consists of three primary components: an end-to-end testing system that validates complete processing pipelines, unit tests for individual processor validation, and a CI/CD pipeline for automated quality assurance.

```mermaid
graph TB
    subgraph "Testing Framework"
        E2E["End-to-End Tests<br/>test_cfg_end_to_end_tests.py"]
        UNIT["Unit Tests<br/>test_data_to_data.py<br/>test_data_to_dropbool.py"]
        CI["CI/CD Pipeline<br/>.github/workflows/tests.yml"]
    end
    
    subgraph "Test Data Infrastructure"
        S3["S3 Test Data<br/>sdp-test-data bucket"]
        MINI["Mini Datasets<br/>Language/Dataset specific"]
        REF["Reference Manifests<br/>Expected outputs"]
    end
    
    subgraph "Quality Validation"
        RUNTIME["Runtime Tests<br/>processor.test()"]
        CONFIG["Config Validation<br/>Hydra instantiation"]
        MANIFEST["Manifest Comparison<br/>Field-by-field validation"]
    end
    
    subgraph "Test Execution"
        PYTEST["PyTest Framework<br/>Parameterized testing"]
        FIXTURES["Test Fixtures<br/>Data setup/teardown"]
        COVERAGE["Code Coverage<br/>pytest-cov reporting"]
    end
    
    E2E --> S3
    E2E --> MINI
    E2E --> REF
    CI --> E2E
    CI --> UNIT
    E2E --> RUNTIME
    E2E --> CONFIG
    E2E --> MANIFEST
    UNIT --> PYTEST
    E2E --> FIXTURES
    CI --> COVERAGE
    
    style E2E fill:#e8f5e8
    style CI fill:#fff3e0
    style S3 fill:#e1f5fe
```

**Sources:** [tests/test_cfg_end_to_end_tests.py:1-502](), [.github/workflows/tests.yml:1-114](), [tests/test_data_to_data.py:1-360]()

## End-to-End Testing System

The end-to-end testing framework validates complete dataset processing pipelines using the `TestCase` dataclass and dataset-specific validation functions.

### Test Case Definition

```mermaid
graph LR
    subgraph "TestCase Structure"
        TC["TestCase<br/>@dataclass"]
        CONFIG["config_path<br/>YAML configuration"]
        DATA_CHECK["data_check_fn<br/>Validation function"]
        REF_MANIFEST["reference_manifest_filename<br/>Expected output"]
        IGNORE["fields_to_ignore<br/>Non-deterministic fields"]
        PROC_RUN["processors_to_run<br/>Subset specification"]
    end
    
    subgraph "Data Check Functions"
        MLS["data_check_fn_mls<br/>Multilingual LibriSpeech"]
        MCV["data_check_fn_mcv<br/>Mozilla Common Voice"]
        VP["data_check_fn_voxpopuli<br/>VoxPopuli extraction"]
        GENERIC["data_check_fn_generic<br/>Generic file validation"]
    end
    
    TC --> CONFIG
    TC --> DATA_CHECK
    TC --> REF_MANIFEST
    TC --> IGNORE
    TC --> PROC_RUN
    
    DATA_CHECK --> MLS
    DATA_CHECK --> MCV
    DATA_CHECK --> VP
    DATA_CHECK --> GENERIC
    
    style TC fill:#e8f5e8
    style DATA_CHECK fill:#fff3e0
```

**Sources:** [tests/test_cfg_end_to_end_tests.py:35-44](), [tests/test_cfg_end_to_end_tests.py:52-91]()

### Test Data Management

The system manages test data through S3 storage and automatic downloading, with support for both local and cloud-based test execution.

| Component | Function | File Location |
|-----------|----------|---------------|
| `check_e2e_test_data()` | Validates environment variables for test data access | [tests/test_cfg_end_to_end_tests.py:341-347]() |
| `get_e2e_test_data_path()` | Downloads test data from S3 if not available locally | [tests/test_cfg_end_to_end_tests.py:349-378]() |
| `setup_data` fixture | Configures test environment and data paths | [tests/test_cfg_end_to_end_tests.py:380-398]() |

### Supported Dataset Test Cases

The framework includes test cases for over 30 dataset configurations across multiple languages:

```mermaid
graph TB
    subgraph "Multilingual Datasets"
        MLS_ES["Spanish MLS<br/>mls/config.yaml"]
        MLS_IT["Italian MLS<br/>mls/config.yaml"]
        MLS_PT["Portuguese MLS<br/>mls/config.yaml"]
        VP_IT["Italian VoxPopuli<br/>voxpopuli/config.yaml"]
    end
    
    subgraph "Mozilla Common Voice"
        MCV_ES["Spanish MCV12<br/>mcv12/config.yaml"]
        MCV_PT["Portuguese MCV<br/>mcv/config.yaml"]
        MCV_KK["Kazakh MCV<br/>mcv/config.yaml"]
        MCV_AR["Arabic MCV<br/>mcv/config.yaml"]
    end
    
    subgraph "Specialized Datasets"
        CORAAL["English CORAAL<br/>coraal/config.yaml"]
        SLR83["English SLR83<br/>slr83/config.yaml"]
        HIFITTS["HiFiTTS-2<br/>config_22khz.yaml"]
        TOLOKA["Armenian Toloka<br/>pipeline_start.yaml"]
    end
    
    subgraph "Test Validation"
        DATA_AVAIL["test_data_availability<br/>Validates test data exists"]
        CONFIG_TEST["test_configs<br/>Runs processing pipeline"]
        MANIFEST_CMP["Manifest Comparison<br/>Field-by-field validation"]
    end
    
    MLS_ES --> DATA_AVAIL
    MCV_ES --> DATA_AVAIL
    CORAAL --> DATA_AVAIL
    DATA_AVAIL --> CONFIG_TEST
    CONFIG_TEST --> MANIFEST_CMP
    
    style DATA_AVAIL fill:#e8f5e8
    style CONFIG_TEST fill:#fff3e0
```

**Sources:** [tests/test_cfg_end_to_end_tests.py:179-331](), [tests/test_cfg_end_to_end_tests.py:400-411](), [tests/test_cfg_end_to_end_tests.py:412-499]()

## Unit Testing Framework

Unit tests validate individual processor functionality using pytest parameterization and systematic test case generation.

### Data Transformation Testing

The `test_data_to_data.py` module tests processors that modify manifest entries without filtering:

| Processor Class | Test Parameters | Validation Focus |
|----------------|-----------------|------------------|
| `InsIfASRInsertion` | `insert_words` list | ASR-based text insertion |
| `SubIfASRSubstitution` | `sub_words` dictionary | ASR-guided substitution |
| `SubMakeLowercase` | `text_key` field | Case normalization |
| `SubRegex` | `regex_params_list` | Pattern replacement |
| `ListToEntries` | `field_with_list`, `output_field` | List expansion |
| `LambdaExpression` | `expression`, `filter` | Dynamic expression evaluation |

**Sources:** [tests/test_data_to_data.py:35-205](), [tests/test_data_to_data.py:354-359]()

### Filtering Processor Testing

The `test_data_to_dropbool.py` module validates processors that filter manifest entries:

```mermaid
graph LR
    subgraph "Quality Filters"
        DURATION["DropHighLowDuration<br/>Duration thresholds"]
        CHARRATE["DropHighLowCharrate<br/>Character rate validation"]
        WORDRATE["DropHighLowWordrate<br/>Word rate validation"]
        ALPHABET["DropNonAlphabet<br/>Character set validation"]
    end
    
    subgraph "ASR Quality Filters"
        CER["DropHighCER<br/>Character error rate"]
        WER["DropHighWER<br/>Word error rate"]
        ASR_ERROR["DropASRErrorBeginningEnd<br/>Alignment validation"]
        WMR["DropLowWordMatchRate<br/>Word matching rate"]
    end
    
    subgraph "Pattern Filters"
        REGEX_MATCH["DropIfRegexMatch<br/>Pattern-based exclusion"]
        REGEX_NONE["DropIfNoneOfRegexMatch<br/>Required pattern validation"]
        SUBSTRING["DropIfSubstringInInsertion<br/>Insertion analysis"]
    end
    
    subgraph "Test Validation"
        PARAM_TEST["Parameterized Testing<br/>pytest.mark.parametrize"]
        BOOL_RESULT["Boolean Result Validation<br/>Drop vs Keep decision"]
    end
    
    DURATION --> PARAM_TEST
    CER --> PARAM_TEST
    REGEX_MATCH --> PARAM_TEST
    PARAM_TEST --> BOOL_RESULT
    
    style PARAM_TEST fill:#e8f5e8
    style BOOL_RESULT fill:#fff3e0
```

**Sources:** [tests/test_data_to_dropbool.py:31-256](), [tests/test_data_to_dropbool.py:258-269]()

### Advanced Quality Testing

The framework includes specialized testing for advanced features like hallucination detection and language validation:

| Test Function | Purpose | Key Components |
|---------------|---------|----------------|
| `test_detect_whisper_hallucinations` | Validates Whisper hallucination detection | `DetectWhisperHallucinationFeatures` processor |
| `test_character_hist_validator` | Tests character histogram language validation | S3-based histogram data, language scoring |
| `en_hist_dir` fixture | Manages histogram test data | S3 download, session-scoped caching |

**Sources:** [tests/test_data_to_data.py:272-288](), [tests/test_data_to_data.py:327-352](), [tests/test_data_to_data.py:289-325]()

## Continuous Integration Pipeline

The CI/CD system runs automated tests across multiple environments and dependency configurations through GitHub Actions.

### CI Workflow Structure

```mermaid
graph TB
    subgraph "GitHub Actions Workflow"
        TRIGGER["Pull Request Trigger<br/>main branch"]
        MANUAL["Manual Workflow Dispatch<br/>workflow_dispatch"]
    end
    
    subgraph "Test Jobs"
        DOC_BUILD["doc-building<br/>Documentation validation"]
        NO_NEMO["no-nemo-tests<br/>Core functionality without NeMo"]
        MAIN_TESTS["main-tests<br/>Full test suite with dependencies"]
    end
    
    subgraph "Documentation Testing"
        SPHINX["Sphinx Build<br/>make html"]
        LINKCHECK["Link Validation<br/>-b linkcheck"]
        WARNINGS["Warning Detection<br/>-W --keep-going"]
    end
    
    subgraph "Core Testing"
        RUNTIME_CFG["Runtime Config Tests<br/>test_cfg_runtime_tests.py"]
        BASIC_IMPORT["SDP Import Validation<br/>No NeMo dependencies"]
    end
    
    subgraph "Full Testing"
        ALL_TESTS["Complete Test Suite<br/>pytest tests/"]
        COVERAGE["Code Coverage<br/>--cov=sdp"]
        S3_DATA["S3 Test Data<br/>AWS credentials"]
        DURATION["Test Duration Report<br/>--durations=30"]
    end
    
    TRIGGER --> DOC_BUILD
    TRIGGER --> NO_NEMO
    TRIGGER --> MAIN_TESTS
    MANUAL --> DOC_BUILD
    MANUAL --> NO_NEMO
    MANUAL --> MAIN_TESTS
    
    DOC_BUILD --> SPHINX
    DOC_BUILD --> LINKCHECK
    DOC_BUILD --> WARNINGS
    
    NO_NEMO --> RUNTIME_CFG
    NO_NEMO --> BASIC_IMPORT
    
    MAIN_TESTS --> ALL_TESTS
    MAIN_TESTS --> COVERAGE
    MAIN_TESTS --> S3_DATA
    MAIN_TESTS --> DURATION
    
    style MAIN_TESTS fill:#e8f5e8
    style ALL_TESTS fill:#fff3e0
```

**Sources:** [.github/workflows/tests.yml:1-114]()

### Dependency Management

The CI system manages complex dependency installations across different testing scenarios:

| Test Job | Dependencies | Purpose |
|----------|-------------|---------|
| `doc-building` | `requirements/docs.txt`, `nemo_text_processing` | Documentation generation validation |
| `no-nemo-tests` | `requirements/main.txt`, `requirements/tests.txt` | Core SDP functionality without heavy ML dependencies |
| `main-tests` | Full NeMo toolkit, audio libraries, cloud dependencies | Complete functionality validation |

### Environment Configuration

The main test job configures extensive system dependencies and environment variables:

```bash
# Audio processing libraries
sudo apt-get install -y libsndfile1 ffmpeg sox libsox-fmt-mp3

# NeMo toolkit installation
pip install nemo-toolkit[asr,nlp]==2.2.1

# Cloud and specialized dependencies
pip install pymarian  # For quality estimation
pip install certifi   # For CORAAL dataset processing
```

**Sources:** [.github/workflows/tests.yml:67-81](), [.github/workflows/tests.yml:84-102]()

## Quality Validation Mechanisms

The testing framework implements multiple validation layers to ensure processing quality and consistency.

### Manifest Comparison System

The end-to-end tests perform detailed manifest validation through field-by-field comparison:

```mermaid
graph LR
    subgraph "Manifest Validation Process"
        REF_LOAD["Reference Manifest<br/>Load expected output"]
        GEN_LOAD["Generated Manifest<br/>Load actual output"]
        FIELD_IGNORE["Field Filtering<br/>Remove non-deterministic fields"]
        LINE_SORT["Line Sorting<br/>Consistent comparison order"]
        JSON_PARSE["JSON Parsing<br/>Structured comparison"]
        FIELD_CMP["Field Comparison<br/>Assert equality"]
    end
    
    subgraph "Ignored Fields"
        AUDIO_PATH["audio_filepath<br/>Path-dependent"]
        DURATION["duration<br/>Non-deterministic processors"]
        TEXT["text<br/>Model-dependent generation"]
        CUSTOM["Custom Fields<br/>Per-test configuration"]
    end
    
    REF_LOAD --> FIELD_IGNORE
    GEN_LOAD --> FIELD_IGNORE
    FIELD_IGNORE --> LINE_SORT
    LINE_SORT --> JSON_PARSE
    JSON_PARSE --> FIELD_CMP
    
    FIELD_IGNORE --> AUDIO_PATH
    FIELD_IGNORE --> DURATION
    FIELD_IGNORE --> TEXT
    FIELD_IGNORE --> CUSTOM
    
    style FIELD_CMP fill:#e8f5e8
    style FIELD_IGNORE fill:#fff3e0
```

**Sources:** [tests/test_cfg_end_to_end_tests.py:481-495]()

### Runtime Testing Integration

Processors can implement optional `test()` methods for runtime validation during processing:

| Validation Type | Implementation | Purpose |
|-----------------|----------------|---------|
| Runtime Tests | `processor.test()` method | Real-time validation during processing |
| Config Validation | Hydra instantiation | Configuration correctness verification |
| Data Availability | `data_check_fn` functions | Input data validation |
| Output Consistency | Reference manifest comparison | Output quality assurance |

### Test Data Cleanup

The framework includes automated cleanup mechanisms to manage test artifacts:

```bash
# Environment variable controls
CLEAN_UP_TMP_PATH=1    # Remove temporary processing files
CLEAN_UP_DATA_DIR=0    # Preserve downloaded test data
USE_THREADING_BACKEND=1 # Enable parallel processing in tests
```

**Sources:** [tests/test_cfg_end_to_end_tests.py:397-398](), [tests/test_cfg_end_to_end_tests.py:497-498](), [.github/workflows/tests.yml:86-90]()

---

