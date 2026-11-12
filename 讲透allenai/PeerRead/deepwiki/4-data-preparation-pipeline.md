<!-- source: DeepWiki mcp.deepwiki.com · repo allenai/PeerRead · page 4 Data Preparation Pipeline · fetched 2026-10-26 -->

# Data Preparation Pipeline

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [code/data_prepare/prepare.py](code/data_prepare/prepare.py)
- [code/data_prepare/run_prepare.sh](code/data_prepare/run_prepare.sh)

</details>



## Purpose and Scope

The Data Preparation Pipeline transforms raw conference data (PDFs and review JSONs) into structured train/dev/test splits ready for machine learning experiments. This pipeline handles data validation, PDF parsing via Science Parse, and standardized dataset organization.

This document provides a high-level overview of the complete preparation workflow. For detailed information about specific stages:
- Data collection from conferences and arXiv: see [Data Collection](#4.1)
- The `prepare.py` script and splitting logic: see [Data Processing and Splitting](#4.2)

For information about the downstream ML pipelines that consume the prepared data:
- Acceptance classification: see [Acceptance Classification Pipeline](#5)
- Aspect prediction: see [Aspect Prediction Pipeline](#6)

**Sources:** [code/data_prepare/prepare.py:1-126](), [code/data_prepare/run_prepare.sh:1-15]()

## Pipeline Overview

The data preparation pipeline consists of four stages executed sequentially for each dataset. The pipeline is mandatory before running any ML experiments, as it creates the standardized directory structure and enriches PDFs with metadata from Science Parse.

```mermaid
graph LR
    RawData["Raw Data<br/>(pdfs/, reviews/)"]
    Validation["Data Validation<br/>Paper.from_json()<br/>Counter(decisions)"]
    ScienceParse["PDF Processing<br/>science-parse-cli JAR<br/>scienceparse/"]
    Split["Train/Dev/Test Split<br/>train_test_split()<br/>90%/5%/5%"]
    Output["Structured Dataset<br/>train/, dev/, test/"]
    
    RawData --> Validation
    Validation --> ScienceParse
    ScienceParse --> Split
    Split --> Output
```

**Diagram: High-level pipeline stages executed by prepare.py**

The pipeline operates on multiple datasets in batch mode via the `run_prepare.sh` script, which iterates through conference venues (NIPS, ICLR, ACL, CoNLL, arXiv categories).

**Sources:** [code/data_prepare/prepare.py:10-126](), [code/data_prepare/run_prepare.sh:1-15]()

## Input Requirements

Before running the preparation pipeline, the data directory must contain:

| Directory/File | Description | Required |
|----------------|-------------|----------|
| `pdfs/` | Directory containing PDF files of papers | Yes |
| `reviews/` | Directory containing JSON files with reviews | Yes (or `reviews.json`) |
| `reviews.json` | Alternative: single file with all reviews from SoftConf dump | Alternative to `reviews/` |

The pipeline validates these inputs and reports statistics before processing:

```mermaid
graph TD
    Input["Input Directory<br/>(e.g., data/arxiv/cs.cl)"]
    CheckReviews{"reviews/ exists?"}
    ReviewsJSON["reviews.json"]
    LoadReviews["Paper.from_softconf_dump()"]
    CreateReviews["Create reviews/<br/>Paper.to_json()"]
    CheckDirs{"pdfs/ and<br/>reviews/ exist?"}
    ValidatePDFs["glob.glob(pdfs/*.pdf)"]
    ValidateReviews["glob.glob(reviews/*.json)"]
    Statistics["Counter(decisions)<br/>Counter(recs)<br/>category_dict"]
    
    Input --> CheckReviews
    CheckReviews -->|No| ReviewsJSON
    ReviewsJSON --> LoadReviews
    LoadReviews --> CreateReviews
    CheckReviews -->|Yes| CheckDirs
    CreateReviews --> CheckDirs
    CheckDirs -->|Yes| ValidatePDFs
    ValidatePDFs --> ValidateReviews
    ValidateReviews --> Statistics
```

**Diagram: Input validation and review file handling in prepare.py**

The validation stage [code/data_prepare/prepare.py:17-61]() performs several checks:
- Converts SoftConf dump format to individual review JSONs if needed
- Counts PDFs, papers, and reviews
- Analyzes decision distributions (accept/reject)
- Categorizes papers by arXiv subject area

**Sources:** [code/data_prepare/prepare.py:14-61]()

## Science Parse Integration

The pipeline invokes an external Science Parse JAR file to extract structured information from PDFs. This produces enriched JSON files containing:
- Title, authors, abstract
- References (parsed bibliographic entries)
- Section structure
- Figures and tables

```mermaid
graph TD
    PDFDir["pdfs/<br/>*.pdf files"]
    CheckSci{"scienceparse/<br/>exists?"}
    CreateDir["os.makedirs(scienceparse/)"]
    RunJAR["os.system()<br/>java -Xmx6g -jar<br/>science-parse-cli-assembly"]
    LoadExisting["glob.glob()<br/>scienceparse/*.pdf.json"]
    Count["len(science_files)"]
    
    PDFDir --> CheckSci
    CheckSci -->|No| CreateDir
    CreateDir --> RunJAR
    RunJAR --> Count
    CheckSci -->|Yes| LoadExisting
    LoadExisting --> Count
```

**Diagram: Science Parse execution flow**

The Science Parse invocation [code/data_prepare/prepare.py:69]() uses:
- **Memory allocation:** 6GB heap (`-Xmx6g`)
- **Input:** `pdf_dir` containing all PDFs
- **Output:** `scienceparse/` directory with `*.pdf.json` files
- **JAR path:** `../lib/science-parse-cli-assembly-1.2.9-SNAPSHOT.jar`

If the `scienceparse/` directory already exists, the pipeline skips reprocessing and loads existing parsed files [code/data_prepare/prepare.py:72-74]().

**Sources:** [code/data_prepare/prepare.py:64-75]()

## Data Splitting Strategy

The pipeline splits data into train/dev/test sets with a 90%/5%/5% ratio using `sklearn.model_selection.train_test_split`:

```mermaid
graph TD
    Collect["Collect Paper IDs<br/>pids from pdfs/<br/>rids from reviews/<br/>sids from scienceparse/"]
    Intersect["ID Intersection<br/>if pid in rids and pid in sids"]
    ValidIDs["Valid IDs List"]
    Split1["train_test_split()<br/>test_size=0.1<br/>random_state=42"]
    TrainSet["train (90%)"]
    ValidTest["validtest (10%)"]
    Split2["train_test_split()<br/>test_size=0.5<br/>random_state=42"]
    DevSet["dev (5%)"]
    TestSet["test (5%)"]
    
    Collect --> Intersect
    Intersect --> ValidIDs
    ValidIDs --> Split1
    Split1 --> TrainSet
    Split1 --> ValidTest
    ValidTest --> Split2
    Split2 --> DevSet
    Split2 --> TestSet
```

**Diagram: Two-stage splitting process**

The splitting logic [code/data_prepare/prepare.py:95-103]() ensures:
1. **Completeness:** Only papers with all three components (PDF, review, parsed PDF) are included
2. **Reproducibility:** Fixed random seed (42) ensures consistent splits across runs
3. **Two-stage split:** First separates train (90%) from validation+test (10%), then splits the 10% equally into dev and test

**Sources:** [code/data_prepare/prepare.py:78-103]()

## File Organization

After splitting, the pipeline creates parallel directory structures for each split:

```mermaid
graph TD
    DataDir["data/<venue>"]
    
    subgraph " "
        Train["train/"]
        Dev["dev/"]
        Test["test/"]
    end
    
    subgraph "Each split contains"
        PDFs["pdfs/<br/>*.pdf"]
        Reviews["reviews/<br/>*.json"]
        Parsed["parsed_pdfs/<br/>*.pdf.json"]
    end
    
    DataDir --> Train
    DataDir --> Dev
    DataDir --> Test
    
    Train -.structure.-> PDFs
    Train -.structure.-> Reviews
    Train -.structure.-> Parsed
    
    Dev -.structure.-> PDFs
    Dev -.structure.-> Reviews
    Dev -.structure.-> Parsed
    
    Test -.structure.-> PDFs
    Test -.structure.-> Reviews
    Test -.structure.-> Parsed
```

**Diagram: Output directory structure created by prepare.py**

The file copying operation [code/data_prepare/prepare.py:105-123]() uses:
- `copyfile()` from `shutil` module to copy files
- `rmtree()` to clean existing split directories if re-running
- Consistent naming: Paper ID is preserved across all three file types

| Split | Purpose | Directory Structure |
|-------|---------|---------------------|
| `train/` | Model training | `pdfs/`, `reviews/`, `parsed_pdfs/` |
| `dev/` | Hyperparameter tuning, model selection | `pdfs/`, `reviews/`, `parsed_pdfs/` |
| `test/` | Final evaluation | `pdfs/`, `reviews/`, `parsed_pdfs/` |

**Sources:** [code/data_prepare/prepare.py:105-124]()

## Batch Processing

The `run_prepare.sh` script processes multiple datasets in sequence:

```mermaid
graph LR
    Script["run_prepare.sh"]
    
    subgraph "Dataset Array DATAS[]"
        ArXivCL["arxiv/cs.cl"]
        ArXivLG["arxiv/cs.lg"]
        ArXivAI["arxiv/cs.ai"]
        NIPS13["nips/nips_2013"]
        NIPS14["nips/nips_2014"]
        NIPS15["nips/nips_2015"]
        NIPS16["nips/nips_2016"]
        ICLR["openreview/ICLR.cc_2017"]
        CoNLL["conll16"]
        ACL["acl17"]
    end
    
    Loop["for DATA in DATAS<br/>python prepare.py"]
    
    Script --> ArXivCL
    Script --> ArXivLG
    Script --> ArXivAI
    Script --> NIPS13
    Script --> NIPS14
    Script --> NIPS15
    Script --> NIPS16
    Script --> ICLR
    Script --> CoNLL
    Script --> ACL
    
    ArXivCL --> Loop
    ArXivLG --> Loop
    ArXivAI --> Loop
    NIPS13 --> Loop
    NIPS14 --> Loop
    NIPS15 --> Loop
    NIPS16 --> Loop
    ICLR --> Loop
    CoNLL --> Loop
    ACL --> Loop
```

**Diagram: Batch processing loop in run_prepare.sh**

The script [code/data_prepare/run_prepare.sh:4-12]() defines:
- **DATADIR:** Base path (`../../data/`)
- **DATAS array:** 10 datasets across 4 venues (arXiv, NIPS, ICLR/OpenReview, direct submissions)
- **Execution:** Calls `python prepare.py $DATADIR$DATA` for each dataset

**Sources:** [code/data_prepare/run_prepare.sh:1-15]()

## Dependencies and Imports

The preparation pipeline requires the following Python dependencies:

| Module | Purpose | Usage in prepare.py |
|--------|---------|---------------------|
| `os`, `sys`, `glob` | File system operations | Directory creation, file discovery |
| `collections.Counter` | Statistics collection | Decision and recommendation counts |
| `shutil.copyfile`, `rmtree` | File operations | Copying files to splits, cleaning directories |
| `sklearn.model_selection.train_test_split` | Data splitting | Creating train/dev/test splits |
| `models.Paper` | Data model | Loading and parsing paper/review JSON files |
| `models.Review` | Data model | Review representation |

The pipeline also depends on:
- **Science Parse JAR:** External Java tool for PDF processing (see [External Dependencies](#9))
- **Java Runtime:** Required to execute Science Parse (minimum 6GB heap)

**Sources:** [code/data_prepare/prepare.py:1-9]()

## Execution Flow Summary

The complete execution flow from raw data to structured dataset:

```mermaid
sequenceDiagram
    participant User
    participant Shell as run_prepare.sh
    participant Python as prepare.py
    participant SP as Science Parse JAR
    participant FS as File System
    
    User->>Shell: ./run_prepare.sh
    loop For each dataset in DATAS
        Shell->>Python: python prepare.py <dataset_path>
        Python->>FS: Check pdfs/ and reviews/
        Python->>FS: Load paper/review JSONs
        Python->>Python: Counter(decisions, recs)
        Python->>SP: java -jar science-parse-cli
        SP->>FS: Write scienceparse/*.pdf.json
        Python->>Python: Collect valid IDs (pdf+review+parse)
        Python->>Python: train_test_split() twice
        Python->>FS: rmtree() existing splits
        Python->>FS: makedirs() train/dev/test
        loop For each paper ID in split
            Python->>FS: copyfile() pdf, review, parsed_pdf
        end
    end
    Shell->>User: All datasets prepared
```

**Diagram: Sequence diagram showing prepare.py execution**

The pipeline is idempotent: running it multiple times on the same data produces identical results due to the fixed random seed. However, existing split directories are removed and recreated [code/data_prepare/prepare.py:106-107]() to ensure clean state.

**Sources:** [code/data_prepare/prepare.py:10-126](), [code/data_prepare/run_prepare.sh:8-12]()

## Output Validation

The pipeline prints statistics at each stage:

```
Number of pdfs: <count>
Number of papers: <count>
Paper Decisions: Counter({'true': X, 'false': Y})
Review Recommendations: Counter({...})
Number of reviews: <count>
Categories: {'cs.cl': X, 'cs.lg': Y, ...}
Number of science parses: <count>
Splitting.. train <count>
Splitting.. dev <count>
Splitting.. test <count>
```

These statistics [code/data_prepare/prepare.py:28-74]() help verify:
- All expected PDFs and reviews are present
- Decision distribution (class balance)
- Category breakdown for arXiv papers
- Science Parse completed successfully
- Split sizes match expected ratios

**Sources:** [code/data_prepare/prepare.py:28-111]()

---

