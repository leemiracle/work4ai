<!-- source: DeepWiki mcp.deepwiki.com · repo NVIDIA/NeMo-text-processing · page 5 Development and Testing · fetched 2026-10-26 -->

# Development and Testing

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [Jenkinsfile](Jenkinsfile)
- [nemo_text_processing/text_normalization/en/data/electronic/domain.tsv](nemo_text_processing/text_normalization/en/data/electronic/domain.tsv)
- [nemo_text_processing/text_normalization/en/taggers/electronic.py](nemo_text_processing/text_normalization/en/taggers/electronic.py)
- [nemo_text_processing/text_normalization/en/taggers/tokenize_and_classify.py](nemo_text_processing/text_normalization/en/taggers/tokenize_and_classify.py)
- [tests/nemo_text_processing/en/data_text_normalization/test_cases_electronic.txt](tests/nemo_text_processing/en/data_text_normalization/test_cases_electronic.txt)
- [tests/nemo_text_processing/en/data_text_normalization/test_cases_punctuation.txt](tests/nemo_text_processing/en/data_text_normalization/test_cases_punctuation.txt)
- [tests/nemo_text_processing/en/data_text_normalization/test_cases_punctuation_match_input.txt](tests/nemo_text_processing/en/data_text_normalization/test_cases_punctuation_match_input.txt)
- [tests/nemo_text_processing/en/data_text_normalization/test_cases_range.txt](tests/nemo_text_processing/en/data_text_normalization/test_cases_range.txt)

</details>



This document covers the development workflow, continuous integration/continuous deployment (CI/CD) pipeline, and testing framework for the NeMo Text Processing system. It focuses on the technical aspects of grammar development, automated testing, and deployment validation processes.

For information about grammar compilation and production deployment, see [Grammar Compilation](#6.1) and [Sparrowhawk Runtime](#6.2). For details on the core text processing algorithms, see [Core Text Processing Systems](#3).

## CI/CD Pipeline Architecture

The development and testing infrastructure is built around a comprehensive Jenkins-based CI/CD pipeline that orchestrates grammar building, testing, and validation across multiple languages and deployment targets.

### Pipeline Stages Overview

```mermaid
graph TB
    subgraph "L0_Stage"["L0: Grammar Creation"]
        L0_EN["EN_TN_ITN_Creation"]
        L0_HI["HI_TN_ITN_Creation"]
        L0_DE_ES["DE_ES_TN_ITN_Creation"]
        L0_AR["AR_TN_ITN_Creation"]
        L0_FR_VI_HU_IT["FR_VI_HU_IT_Creation"]
        L0_RU_SV_PT["RU_SV_PT_Creation"]
        L0_HY_MR["HY_MR_Creation"]
        L0_ZH["ZH_TN_ITN_Creation"]
        L0_JA["JA_ITN_Creation"]
        L0_Utils["Test_Utils"]
    end
    
    subgraph "L1_Stage"["L1: TN/ITN CPU Tests"]
        L1_EN["pytest_EN_tests"]
        L1_HI["pytest_HI_tests"]
        L1_DE["pytest_DE_tests"]
        L1_ES["pytest_ES_tests"]
        L1_AR["pytest_AR_tests"]
        L1_FR["pytest_FR_tests"]
        L1_Others["pytest_Other_Languages"]
    end
    
    subgraph "L2_Stage"["L2: Integration Tests"]
        L2_Sparrowhawk["Sparrowhawk_Tests"]
        L2_NeMo["NeMo_Text_Processing"]
        L2_Alignment["FST_Alignment_Tests"]
        L2_Export["Grammar_Export_Tests"]
    end
    
    subgraph "Cache_Management"["Cache System"]
        EN_TN_CACHE["EN_TN_CACHE"]
        HI_TN_CACHE["HI_TN_CACHE"]
        DE_TN_CACHE["DE_TN_CACHE"]
        DEFAULT_TN_CACHE["DEFAULT_TN_CACHE"]
    end
    
    L0_EN --> L1_EN
    L0_HI --> L1_HI
    L0_DE_ES --> L1_DE
    L0_DE_ES --> L1_ES
    L0_AR --> L1_AR
    L0_FR_VI_HU_IT --> L1_FR
    
    L1_EN --> L2_Sparrowhawk
    L1_EN --> L2_NeMo
    L1_HI --> L2_NeMo
    
    EN_TN_CACHE --> L0_EN
    HI_TN_CACHE --> L0_HI
    DE_TN_CACHE --> L0_DE_ES
    DEFAULT_TN_CACHE --> L0_RU_SV_PT
    
    L2_Sparrowhawk --> L2_Alignment
    L2_NeMo --> L2_Export
```

The pipeline consists of three main stages that execute sequentially, with parallel execution within each stage to optimize build times.

**Sources:** [Jenkinsfile:33-498]()

### Grammar Creation Commands

The L0 stage executes grammar creation commands for each supported language, using cached grammar files when available:

```mermaid
graph LR
    subgraph "Grammar_Creation_Commands"["Grammar Creation Commands"]
        normalize_py["normalize.py"]
        normalize_with_audio_py["normalize_with_audio.py"]
        inverse_normalize_py["inverse_normalize.py"]
    end
    
    subgraph "Language_Specific_Execution"["Language-Specific Execution"]
        EN_TN["python normalize.py --text=1 --cache_dir ${EN_TN_CACHE}"]
        EN_TN_NonDet["python normalize_with_audio.py --text=1 --cache_dir ${EN_TN_CACHE}"]
        EN_ITN["python inverse_normalize.py --language en --text=twenty --cache_dir ${EN_TN_CACHE}"]
        HI_TN["python normalize.py --lang=hi --text=१ --cache_dir ${HI_TN_CACHE}"]
        HI_ITN["python inverse_normalize.py --lang=hi --text=एक --cache_dir ${HI_TN_CACHE}"]
    end
    
    subgraph "Cache_Directories"["Cache Directories"]
        EN_Cache["/home/jenkinsci/TestData/text_norm/ci/grammars/09-04-24-0"]
        HI_Cache["/home/jenkinsci/TestData/text_norm/ci/grammars/04-22-25-0"]
        DE_Cache["/home/jenkinsci/TestData/text_norm/ci/grammars/10-23-24-0"]
    end
    
    normalize_py --> EN_TN
    normalize_with_audio_py --> EN_TN_NonDet
    inverse_normalize_py --> EN_ITN
    normalize_py --> HI_TN
    inverse_normalize_py --> HI_ITN
    
    EN_TN --> EN_Cache
    EN_TN_NonDet --> EN_Cache
    EN_ITN --> EN_Cache
    HI_TN --> HI_Cache
    HI_ITN --> HI_Cache
```

**Sources:** [Jenkinsfile:64-320]()

## Testing Framework

The testing framework combines pytest-based unit tests with shell-based integration tests, covering both Python API functionality and Sparrowhawk compatibility.

### Test Execution Strategy

```mermaid
graph TB
    subgraph "Test_Types"["Test Types"]
        PyTest["pytest_tests"]
        ShellTest["shell_tests"]
        SparrowhawkTest["sparrowhawk_tests"]
    end
    
    subgraph "Test_Execution"["Test Execution Pattern"]
        L1_Pattern["pytest tests/nemo_text_processing/{lang}/ -m 'not pleasefixme' --cpu --tn_cache_dir ${CACHE}"]
        L2_SH_Pattern["bash sh_test.sh --MODE=test_itn_grammars --OVERWRITE_CACHE=False"]
        L2_Export_Pattern["python pynini_export.py --output=$OUTPUT_DIR --grammars=tn_grammars"]
    end
    
    subgraph "Test_Data_Format"["Test Data Format"]
        TestCase["input~expected_output"]
        TestFiles["test_cases_electronic.txt"]
        TestFiles_Punct["test_cases_punctuation.txt"]
        TestFiles_Range["test_cases_range.txt"]
    end
    
    PyTest --> L1_Pattern
    ShellTest --> L2_SH_Pattern
    SparrowhawkTest --> L2_Export_Pattern
    
    L1_Pattern --> TestCase
    TestCase --> TestFiles
    TestCase --> TestFiles_Punct
    TestCase --> TestFiles_Range
```

**Sources:** [Jenkinsfile:325-497](), [tests/nemo_text_processing/en/data_text_normalization/test_cases_electronic.txt:1-44]()

### Test Data Structure

Test cases follow a standardized format with input and expected output separated by `~`:

| Component | Example Input | Expected Output |
|-----------|---------------|-----------------|
| Electronic | `cdf@abc.edu` | `cdf at abc dot edu` |
| Punctuation | `$150-$200` | `one hundred and fifty dollars to two hundred dollars` |
| Range | `1980-1986` | `nineteen eighty to nineteen eighty six` |

**Sources:** [tests/nemo_text_processing/en/data_text_normalization/test_cases_electronic.txt:7](), [tests/nemo_text_processing/en/data_text_normalization/test_cases_range.txt:19]()

## Grammar Development Workflow

The grammar development process involves creating FST-based classifiers and verbalizers that are integrated into the main tokenization pipeline.

### FST Component Integration

```mermaid
graph TB
    subgraph "ClassifyFst_Construction"["ClassifyFst Construction"]
        CardinalFst["CardinalFst"]
        OrdinalFst["OrdinalFst"]
        DecimalFst["DecimalFst"]
        ElectronicFst["ElectronicFst"]
        MoneyFst["MoneyFst"]
        TimeFst["TimeFst"]
        DateFst["DateFst"]
        MeasureFst["MeasureFst"]
    end
    
    subgraph "Weight_Assignment"["Weight Assignment"]
        Weight_Whitelist["whitelist_graph: 1.01"]
        Weight_Time["time_graph: 1.1"]
        Weight_Date["date_graph: 1.09"]
        Weight_Electronic["electronic_graph: 1.11"]
        Weight_Serial["serial_graph: 1.12"]
        Weight_Word["word_graph: 100"]
    end
    
    subgraph "Final_Graph"["Final Graph Assembly"]
        TokenizeAndClassify["tokenize_and_classify.fst"]
        FARFile["en_tn_True_deterministic_cased__tokenize.far"]
    end
    
    CardinalFst --> Weight_Time
    ElectronicFst --> Weight_Electronic
    Weight_Whitelist --> TokenizeAndClassify
    Weight_Time --> TokenizeAndClassify
    Weight_Electronic --> TokenizeAndClassify
    Weight_Serial --> TokenizeAndClassify
    Weight_Word --> TokenizeAndClassify
    
    TokenizeAndClassify --> FARFile
```

**Sources:** [nemo_text_processing/text_normalization/en/taggers/tokenize_and_classify.py:189-241]()

### Electronic FST Development Example

The `ElectronicFst` class demonstrates the grammar development pattern:

```mermaid
graph TB
    subgraph "ElectronicFst_Components"["ElectronicFst Components"]
        DataFiles["data/electronic/*.tsv"]
        CCCues["cc_cues.tsv"]
        DomainFile["domain.tsv"]
        SymbolFile["symbol.tsv"]
        WordsFile["words.tsv"]
    end
    
    subgraph "FST_Construction"["FST Construction"]
        Username["username_fst"]
        Domain["domain_fst"]
        Protocol["protocol_fst"]
        EmailPattern["email_pattern"]
        URLPattern["url_pattern"]
    end
    
    subgraph "Output_Format"["Output Format"]
        ClassTags["tokens { electronic { username: 'value' domain: 'value' } }"]
    end
    
    DataFiles --> Username
    DomainFile --> Domain
    SymbolFile --> Protocol
    
    Username --> EmailPattern
    Domain --> EmailPattern
    Protocol --> URLPattern
    
    EmailPattern --> ClassTags
    URLPattern --> ClassTags
```

**Sources:** [nemo_text_processing/text_normalization/en/taggers/electronic.py:44-178](), [nemo_text_processing/text_normalization/en/data/electronic/domain.tsv:1-13]()

## Cache Management System

The CI/CD pipeline uses a sophisticated cache management system to optimize build times by reusing compiled grammar files across builds.

### Cache Directory Structure

```mermaid
graph TB
    subgraph "Cache_Environment_Variables"["Cache Environment Variables"]
        AR_TN_CACHE["AR_TN_CACHE: /home/jenkinsci/TestData/text_norm/ci/grammars/04-24-24-0"]
        DE_TN_CACHE["DE_TN_CACHE: /home/jenkinsci/TestData/text_norm/ci/grammars/10-23-24-0"]
        EN_TN_CACHE["EN_TN_CACHE: /home/jenkinsci/TestData/text_norm/ci/grammars/09-04-24-0"]
        HI_TN_CACHE["HI_TN_CACHE: /home/jenkinsci/TestData/text_norm/ci/grammars/04-22-25-0"]
        DEFAULT_TN_CACHE["DEFAULT_TN_CACHE: /home/jenkinsci/TestData/text_norm/ci/grammars/06-08-23-0"]
    end
    
    subgraph "Cache_Usage_Pattern"["Cache Usage Pattern"]
        CacheCheck["Check if .far files exist"]
        CacheRestore["Restore from cache"]
        CacheRebuild["Rebuild grammars"]
        CacheStore["Store compiled .far files"]
    end
    
    subgraph "FAR_Files"["FAR Files"]
        TNGrammar["en_tn_True_deterministic_cased__tokenize.far"]
        ITNGrammar["en_itn_lower_cased.far"]
        SHGrammar["SH_ITN/classify.far"]
    end
    
    EN_TN_CACHE --> CacheCheck
    CacheCheck --> CacheRestore
    CacheCheck --> CacheRebuild
    CacheRebuild --> CacheStore
    CacheStore --> TNGrammar
    CacheStore --> ITNGrammar
    CacheStore --> SHGrammar
```

**Sources:** [Jenkinsfile:14-31]()

## Sparrowhawk Integration Testing

The L2 stage includes comprehensive Sparrowhawk integration testing to validate grammar compatibility with the C++ runtime environment.

### Sparrowhawk Test Flow

```mermaid
graph TB
    subgraph "Sparrowhawk_Test_Stages"["Sparrowhawk Test Stages"]
        SHTestScript["sh_test.sh"]
        GrammarCopy["cp grammars to test directory"]
        TestExecution["bash test_sparrowhawk_*.sh"]
    end
    
    subgraph "Test_Modes"["Test Modes"]
        ITNLowerCase["test_itn_grammars (lower_cased)"]
        ITNCased["test_itn_grammars (cased)"]
        TNGrammars["test_tn_grammars"]
    end
    
    subgraph "Test_Parameters"["Test Parameters"]
        MODE["--MODE=test_itn_grammars"]
        OVERWRITE_CACHE["--OVERWRITE_CACHE=False"]
        FAR_PATH["--FAR_PATH=${EN_TN_CACHE}/SH_ITN"]
        LANGUAGE["--LANGUAGE=en"]
        INPUT_CASE["--INPUT_CASE=cased"]
    end
    
    SHTestScript --> ITNLowerCase
    SHTestScript --> ITNCased
    SHTestScript --> TNGrammars
    
    MODE --> SHTestScript
    OVERWRITE_CACHE --> SHTestScript
    FAR_PATH --> SHTestScript
    LANGUAGE --> SHTestScript
    INPUT_CASE --> SHTestScript
    
    GrammarCopy --> TestExecution
```

**Sources:** [Jenkinsfile:421-442]()

## Deployment Validation

The L2 stage includes comprehensive deployment validation through grammar export testing and alignment verification.

### Export and Alignment Testing

```mermaid
graph TB
    subgraph "Export_Testing"["Export Testing"]
        PyniniExport["pynini_export.py"]
        FARGeneration["Generate .far files"]
        OutputValidation["Validate output against gold standard"]
    end
    
    subgraph "Alignment_Testing"["Alignment Testing"]
        AlignmentPy["alignment.py"]
        TNAlignment["TN alignment test"]
        ITNAlignment["ITN alignment test"]
    end
    
    subgraph "Test_Commands"["Test Commands"]
        ExportCmd["python pynini_export.py --output=$OUTPUT_DIR --grammars=tn_grammars --cache_dir ${EN_TN_CACHE}"]
        AlignTNCmd["python alignment.py --text='2615 Forest Av' --grammar=tn --rule=tokenize_and_classify"]
        AlignITNCmd["python alignment.py --text='one million' --grammar=itn --rule=tokenize_and_classify"]
    end
    
    subgraph "Validation_Files"["Validation Files"]
        TestGoalPy["test_goal_py.txt"]
        AlignmentGold["alignment_gold.txt"]
    end
    
    PyniniExport --> ExportCmd
    AlignmentPy --> AlignTNCmd
    AlignmentPy --> AlignITNCmd
    
    ExportCmd --> TestGoalPy
    AlignTNCmd --> AlignmentGold
    AlignITNCmd --> AlignmentGold
```

**Sources:** [Jenkinsfile:454-494]()

---

