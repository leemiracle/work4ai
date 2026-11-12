<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/acon · extra page AppWorld Setup · fetched 2026-10-26 -->

# AppWorld Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [experiments/appworld/README.md](experiments/appworld/README.md)
- [experiments/appworld/data_copy/datasets/train_history_tiny.txt](experiments/appworld/data_copy/datasets/train_history_tiny.txt)
- [experiments/appworld/data_copy/datasets/train_obs_tiny.txt](experiments/appworld/data_copy/datasets/train_obs_tiny.txt)

</details>



## Purpose and Scope

This page covers the installation and configuration of the AppWorld benchmark environment required to run ACON experiments. It includes installing the upstream AppWorld package, downloading benchmark data, and configuring the local directory structure.

For running AppWorld experiments after setup, see [Running Experiments](#5). For understanding the AppWorld task structure and data formats, see [AppWorld Task Structure](#4.1.2).

## Overview

AppWorld is an external benchmark that must be installed separately before running ACON experiments. The setup process involves three main steps: cloning the upstream repository, downloading benchmark data, and relocating data files to the ACON directory structure.

**Installation Flow**

```mermaid
graph TB
    START["Start Setup"]
    GIT_LFS["git lfs install"]
    CLONE["git clone AppWorld repo"]
    INSTALL["pip install -e ."]
    DOWNLOAD["appworld download data"]
    MOVE["Move data/ to experiments/appworld/"]
    VERIFY["Verify Setup"]
    
    START --> GIT_LFS
    GIT_LFS --> CLONE
    CLONE --> INSTALL
    INSTALL --> DOWNLOAD
    DOWNLOAD --> MOVE
    MOVE --> VERIFY
    
    CLONE -.creates.-> REPO["appworld/<br/>repository"]
    DOWNLOAD -.creates.-> DATA["appworld/data/<br/>benchmark datasets"]
    MOVE -.creates.-> ACON_DATA["experiments/appworld/data/<br/>datasets accessible to ACON"]
    
    INSTALL -.provides.-> CMD["appworld CLI<br/>commands"]
    CMD -.used by.-> DOWNLOAD
```

Sources: [experiments/appworld/README.md:6-23]()

## Prerequisites

Before beginning the AppWorld setup, ensure you have:

- **Git LFS** (Large File Storage) installed on your system
- **Python 3.11+** with pip
- **ACON repository** cloned locally
- Sufficient disk space (AppWorld data is approximately several GB)

## Installation Steps

### Step 1: Install Git LFS

Git LFS is required to download large files from the AppWorld repository.

```bash
git lfs install
```

### Step 2: Clone AppWorld Repository

Clone the upstream AppWorld repository from StonyBrookNLP:

```bash
git clone https://github.com/StonyBrookNLP/appworld
cd appworld
```

This creates an `appworld/` directory containing the benchmark implementation.

### Step 3: Install AppWorld Package

Install the AppWorld package in editable mode:

```bash
pip install -e .
```

This makes the `appworld` CLI command available and installs all required dependencies.

**Key CLI Commands Available After Installation**

| Command | Purpose |
|---------|---------|
| `appworld install --repo` | Installs repository-level dependencies |
| `appworld download data` | Downloads benchmark datasets |
| `appworld evaluate <model> <split>` | Evaluates experiment results |

### Step 4: Download Benchmark Data

Download the AppWorld benchmark datasets:

```bash
appworld install --repo
appworld download data
```

This creates a `data/` directory inside the `appworld/` repository containing:
- Task definitions
- Ground truth annotations
- Test splits (train, dev, test_normal, test_challenge)

### Step 5: Relocate Data to ACON Directory

Move the downloaded `data/` directory into the ACON AppWorld experiments directory:

```bash
mv data /path/to/acon/experiments/appworld/
```

Replace `/path/to/acon` with the actual path to your ACON repository.

**Directory Relocation Diagram**

```mermaid
graph LR
    subgraph "AppWorld Repository"
        AW_ROOT["appworld/"]
        AW_DATA["data/"]
        AW_ROOT --> AW_DATA
    end
    
    subgraph "ACON Repository"
        ACON_ROOT["acon/"]
        ACON_EXP["experiments/"]
        ACON_AW["appworld/"]
        ACON_DATA_TARGET["data/"]
        
        ACON_ROOT --> ACON_EXP
        ACON_EXP --> ACON_AW
        ACON_AW --> ACON_DATA_TARGET
    end
    
    AW_DATA -.mv command.-> ACON_DATA_TARGET
    
    ACON_DATA_TARGET --> DATASETS["datasets/"]
    DATASETS --> TRAIN["train/"]
    DATASETS --> DEV["dev/"]
    DATASETS --> TEST_N["test_normal/"]
    DATASETS --> TEST_C["test_challenge/"]
```

Sources: [experiments/appworld/README.md:19-23]()

## Directory Structure After Setup

After completing the setup, the `experiments/appworld/` directory should have the following structure:

```
experiments/appworld/
├── data/                              # Benchmark data (moved from appworld repo)
│   ├── datasets/
│   │   ├── train/                     # Training split task definitions
│   │   ├── dev/                       # Development split task definitions
│   │   ├── test_normal/               # Normal test split
│   │   └── test_challenge/            # Challenge test split
│   └── ...                            # Other AppWorld data files
├── data_copy/                         # Subset datasets for testing
│   └── datasets/
│       ├── train_history_tiny.txt     # Tiny subset for history compression
│       └── train_obs_tiny.txt         # Tiny subset for observation compression
├── configs/                           # Configuration files
├── prompts/                           # Prompt templates
├── scripts/                           # Execution scripts
├── run.py                             # Single task runner
├── run_all.py                         # Batch experiment runner
└── README.md                          # AppWorld-specific documentation
```

**Data Dependencies**

```mermaid
graph TB
    subgraph "experiments/appworld/data/"
        DATASETS["datasets/"]
        TRAIN_DS["train/<br/>training tasks"]
        DEV_DS["dev/<br/>development tasks"]
        TEST_N_DS["test_normal/<br/>normal difficulty"]
        TEST_C_DS["test_challenge/<br/>challenging tasks"]
        
        DATASETS --> TRAIN_DS
        DATASETS --> DEV_DS
        DATASETS --> TEST_N_DS
        DATASETS --> TEST_C_DS
    end
    
    subgraph "experiments/appworld/data_copy/datasets/"
        HISTORY_TINY["train_history_tiny.txt<br/>39 task IDs"]
        OBS_TINY["train_obs_tiny.txt<br/>18 task IDs"]
    end
    
    subgraph "ACON Scripts"
        RUN_ALL["run_all.py<br/>--split argument"]
        RUN_CTXOPT["scripts/run_ctxopt_history.sh"]
    end
    
    RUN_ALL -.reads.-> TRAIN_DS
    RUN_ALL -.reads.-> DEV_DS
    RUN_ALL -.reads.-> TEST_N_DS
    RUN_ALL -.reads.-> TEST_C_DS
    
    RUN_CTXOPT -.reads.-> HISTORY_TINY
    RUN_CTXOPT -.reads.-> OBS_TINY
```

Sources: [experiments/appworld/README.md:69-84](), [experiments/appworld/data_copy/datasets/train_history_tiny.txt:1-39](), [experiments/appworld/data_copy/datasets/train_obs_tiny.txt:1-18]()

## Test Datasets

ACON includes pre-defined subsets of the training data for rapid testing and validation:

### train_history_tiny.txt

A curated subset of 39 task instances used for testing history compression configurations. Each line contains a task ID in the format `<hash>_<repetition>`.

**Sample Task IDs:**
```
07b42fd_1
07b42fd_2
07b42fd_3
229360a_1
229360a_3
...
```

This dataset is referenced by `scripts/run_ctxopt_history.sh` for validating history compression prompts.

### train_obs_tiny.txt

A curated subset of 18 task instances used for testing observation compression configurations.

**Sample Task IDs:**
```
229360a_1
229360a_3
22cc237_1
22cc237_3
...
```

These subsets enable rapid iteration on context optimization configurations without running full experiments.

Sources: [experiments/appworld/data_copy/datasets/train_history_tiny.txt:1-39](), [experiments/appworld/data_copy/datasets/train_obs_tiny.txt:1-18](), [experiments/appworld/README.md:118-120]()

## Verification

To verify that AppWorld is correctly installed and configured:

### 1. Check AppWorld CLI

Verify the `appworld` command is available:

```bash
appworld --help
```

Expected output should show available commands including `evaluate`, `download`, and `install`.

### 2. Check Data Directory Structure

Verify the data directory exists and contains datasets:

```bash
ls experiments/appworld/data/datasets/
```

Expected output:
```
train  dev  test_normal  test_challenge
```

### 3. Check Dataset Splits

Verify each split contains task files:

```bash
ls experiments/appworld/data/datasets/train/ | head -5
```

This should show task definition files.

### 4. Run Debug Mode (Optional)

Test the setup by running a single task in debug mode:

```bash
cd experiments/appworld
python run_all.py \
    --split train \
    --model_name gpt-4.1 \
    --tag setup_test \
    --debug
```

The `--debug` flag limits execution to verify configuration without consuming API credits.

Sources: [experiments/appworld/README.md:42]()

## Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `appworld: command not found` | Package not installed or not in PATH | Re-run `pip install -e .` in appworld directory |
| `data/` directory not found | Data not downloaded or not moved | Run `appworld download data` and move to `experiments/appworld/` |
| Git LFS files appear as pointers | Git LFS not installed before cloning | Install Git LFS, re-clone repository |
| Permission errors on data files | Insufficient permissions | Check file ownership and permissions on moved data directory |

## Next Steps

After completing the AppWorld setup:

1. **Configure API Keys**: Set up OpenAI API credentials (see [API Configuration](#2.2))
2. **Understand Task Structure**: Learn about AppWorld task formats (see [AppWorld Task Structure](#4.1.2))
3. **Run First Experiment**: Execute a baseline experiment (see [Running Your First Experiment](#2.3))

Sources: [experiments/appworld/README.md:1-24]()

---

