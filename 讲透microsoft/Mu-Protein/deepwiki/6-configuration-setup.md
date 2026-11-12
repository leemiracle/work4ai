<!-- source: DeepWiki mcp.deepwiki.com · repo microsoft/Mu-Protein · page 6 Configuration & Setup · fetched 2026-10-26 -->

# Configuration & Setup

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.gitattributes](.gitattributes)
- [.gitignore](.gitignore)
- [LICENSE](LICENSE)

</details>



This page covers the essential configuration and setup procedures for the μProtein framework repository. It explains the repository structure, Git configuration for large model files, development environment setup, and how configuration files coordinate the three-stage pipeline. For detailed repository-specific configurations, see [Repository Configuration](#6.1). For protein task and fairseq integration configurations, see [Protein Task Configuration](#6.2).

## Repository Structure and Configuration Overview

The μProtein framework uses a multi-component architecture where configuration spans across three main systems: PMLM pretraining, μFormer training, and μSearch optimization. Each component requires specific configuration for data handling, model parameters, and training procedures.

### Repository Organization

```mermaid
graph TB
    subgraph "μProtein Repository Structure"
        ROOT["/"]
        
        subgraph "Core Components"
            PMLM["pmlm/"]
            MUFORMER["mu-former/"]
            MUSEARCH["mu-search/"]
            PRETRAINED["pretrained/"]
        end
        
        subgraph "Configuration Files"
            GITATTRIBUTES[".gitattributes"]
            GITIGNORE[".gitignore"]
            REQUIREMENTS["requirements.txt"]
            LICENSE["LICENSE"]
        end
        
        subgraph "Documentation"
            README["README.md"]
            CONTRIBUTING["CONTRIBUTING.md"]
            SECURITY["SECURITY.md"]
            CODE_OF_CONDUCT["CODE_OF_CONDUCT.md"]
        end
        
        subgraph "Data Directories"
            PROTEIN_DATA["protein/"]
            SCRIPTS["script/"]
        end
    end
    
    ROOT --> PMLM
    ROOT --> MUFORMER
    ROOT --> MUSEARCH
    ROOT --> PRETRAINED
    ROOT --> GITATTRIBUTES
    ROOT --> GITIGNORE
    ROOT --> REQUIREMENTS
    ROOT --> LICENSE
    ROOT --> README
    ROOT --> CONTRIBUTING
    ROOT --> SECURITY
    ROOT --> CODE_OF_CONDUCT
    ROOT --> PROTEIN_DATA
    ROOT --> SCRIPTS
```

Sources: [.gitattributes:1-2](), [.gitignore:1-175](), [LICENSE:1-22]()

## Git Large File Storage Configuration

The repository uses Git LFS to manage large model files, particularly the pretrained PMLM models which can exceed 2GB in size.

### LFS Configuration

```mermaid
flowchart LR
    subgraph "Git LFS Setup"
        GITATTRIBUTES_FILE[".gitattributes"]
        PT_FILES["*.pt files"]
        LFS_STORAGE["Git LFS Storage"]
        
        GITATTRIBUTES_FILE --> PT_FILES
        PT_FILES --> LFS_STORAGE
        
        FILTER["filter=lfs"]
        DIFF["diff=lfs"] 
        MERGE["merge=lfs"]
        TEXT["-text"]
        
        PT_FILES --> FILTER
        PT_FILES --> DIFF
        PT_FILES --> MERGE
        PT_FILES --> TEXT
    end
    
    subgraph "Model Files"
        PMLM_MODEL["pretrained/pmlm_650m.pt"]
        UFORMER_MODEL["uformer_l_encoder.pt"]
        OTHER_MODELS["Additional .pt files"]
    end
    
    LFS_STORAGE --> PMLM_MODEL
    LFS_STORAGE --> UFORMER_MODEL
    LFS_STORAGE --> OTHER_MODELS
```

The `.gitattributes` file configures all PyTorch model files (`.pt` extension) to use Git LFS with the following settings:

| Attribute | Purpose |
|-----------|---------|
| `filter=lfs` | Routes files through LFS clean/smudge filters |
| `diff=lfs` | Uses LFS-aware diff for large files |
| `merge=lfs` | Handles LFS files during merge operations |
| `-text` | Treats files as binary, preventing line ending conversion |

Sources: [.gitattributes:1-2]()

## Development Environment Configuration

### Dependency Management

The repository follows standard Python project conventions for dependency management and environment configuration.

```mermaid
graph TB
    subgraph "Python Environment Setup"
        PYTHON_VERSION["Python 3.x"]
        VENV["Virtual Environment"]
        REQUIREMENTS_FILE["requirements.txt"]
        
        subgraph "Core Dependencies"
            PYTORCH["PyTorch 1.12.0+"]
            FAIRSEQ["fairseq 0.10.2"]
            BIOPYTHON["biopython ≥1.78"]
            TAPE["tape_proteins ≥0.4"]
        end
        
        subgraph "Scientific Computing"
            NUMPY["numpy"]
            PANDAS["pandas"]
            SKLEARN["scikit-learn ≥0.24.1"]
        end
        
        subgraph "Infrastructure"
            BOTO3["boto3"]
            PROTOBUF["protobuf 4.25.8"]
            SENTENCEPIECE["sentencepiece"]
        end
    end
    
    PYTHON_VERSION --> VENV
    VENV --> REQUIREMENTS_FILE
    REQUIREMENTS_FILE --> PYTORCH
    REQUIREMENTS_FILE --> FAIRSEQ
    REQUIREMENTS_FILE --> BIOPYTHON
    REQUIREMENTS_FILE --> TAPE
    REQUIREMENTS_FILE --> NUMPY
    REQUIREMENTS_FILE --> PANDAS
    REQUIREMENTS_FILE --> SKLEARN
    REQUIREMENTS_FILE --> BOTO3
    REQUIREMENTS_FILE --> PROTOBUF
    REQUIREMENTS_FILE --> SENTENCEPIECE
```

### Ignored Files and Directories

The repository uses comprehensive `.gitignore` patterns to exclude development artifacts:

| Category | Examples | Lines |
|----------|----------|-------|
| Python artifacts | `__pycache__/`, `*.pyc`, `*.egg-info/` | [.gitignore:1-27]() |
| Virtual environments | `.venv`, `venv/`, `ENV/` | [.gitignore:130-137]() |
| Testing artifacts | `.coverage`, `.pytest_cache/`, `htmlcov/` | [.gitignore:39-52]() |
| IDE/Editor files | `.spyderproject`, `.ropeproject` | [.gitignore:139-144]() |
| Documentation builds | `docs/_build/`, `/site` | [.gitignore:71-147]() |

Sources: [.gitignore:1-175]()

## Configuration Flow Between Components

The μProtein framework coordinates configuration across its three-stage architecture through a combination of configuration files, environment variables, and command-line arguments.

### Component Configuration Dependencies

```mermaid
flowchart TD
    subgraph "Stage 1: PMLM Configuration"
        PMLM_CONFIG["pmlm/src/config"]
        FAIRSEQ_CONFIG["Fairseq Configuration"]
        PROTEIN_DICT["protein/dict.txt"]
        PRETRAIN_SCRIPT["script/pretrain.sh"]
    end
    
    subgraph "Stage 2: μFormer Configuration"  
        MF_MAIN["mu-former/main.py"]
        MF_CONFIG["Command-line arguments"]
        PRETRAINED_PATH["Model path configuration"]
        DATA_CONFIG["Data loading configuration"]
    end
    
    subgraph "Stage 3: μSearch Configuration"
        MS_CONFIG["μSearch configuration"]
        FITNESS_ORACLE["Fitness oracle settings"]
        RL_PARAMS["RL parameter configuration"]
    end
    
    subgraph "Shared Configuration"
        ENV_VARS["Environment Variables"]
        MODEL_PATHS["Model file paths"]
        DATA_PATHS["Data directory paths"]
    end
    
    PMLM_CONFIG --> PRETRAINED_PATH
    FAIRSEQ_CONFIG --> MF_CONFIG
    PROTEIN_DICT --> DATA_CONFIG
    PRETRAIN_SCRIPT --> MODEL_PATHS
    
    PRETRAINED_PATH --> FITNESS_ORACLE
    MF_CONFIG --> RL_PARAMS
    
    ENV_VARS --> PMLM_CONFIG
    ENV_VARS --> MF_CONFIG
    ENV_VARS --> MS_CONFIG
    
    MODEL_PATHS --> DATA_PATHS
```

Sources: [.gitattributes:1-2](), [.gitignore:130-137]()

## License and Legal Configuration

The repository operates under the MIT License, providing broad permissions for use, modification, and distribution while requiring attribution.

### License Terms Summary

| Permission | Restriction | Condition |
|------------|-------------|-----------|
| Commercial use | None | Include copyright notice |
| Modification | None | Include license text |
| Distribution | None | Include original license |
| Private use | None | No warranty provided |

The MIT License allows users to:
- Use the software commercially
- Modify and distribute the code
- Sublicense under different terms
- Include in proprietary software

Sources: [LICENSE:1-22]()

## Security and Contribution Configuration

The repository includes structured policies for security reporting and community contributions, establishing clear procedures for:

- **Security vulnerabilities**: Reporting through designated channels
- **Code contributions**: Following contributor license agreement requirements
- **Community standards**: Adherence to code of conduct policies
- **Development workflow**: Contribution guidelines and pull request procedures

For detailed contribution procedures, see [Contributing](#7.1). For security policy details, see [Security](#7.2).

Sources: [.gitignore:1-175](), [LICENSE:1-22]()

---

