<!-- source: DeepWiki mcp.deepwiki.com · repo google-deepmind/alphafold · page 2 Deployment and Execution · fetched 2026-10-26 -->

# Deployment and Execution

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [.dockerignore](.dockerignore)
- [docker/Dockerfile](docker/Dockerfile)
- [docker/run_docker.py](docker/run_docker.py)
- [pyproject.toml](pyproject.toml)
- [requirements.txt](requirements.txt)
- [run_alphafold.py](run_alphafold.py)
- [run_alphafold_test.py](run_alphafold_test.py)

</details>



## Purpose and Scope

This document provides an overview of AlphaFold's deployment architecture and execution pipeline. It covers how the system is containerized, launched, and orchestrated from initial deployment through structure prediction completion.

For specific topics:
- Docker image construction and dependencies: see [Docker Environment](#2.1)
- Database download and configuration: see [Database Setup](#2.2)  
- Detailed prediction workflow: see [Running AlphaFold](#2.3)
- Command-line flags and configuration: see [Command-Line Interface](#2.4)

## Deployment Architecture Overview

AlphaFold is primarily deployed via Docker containerization to ensure reproducibility and consistent dependency management. The deployment consists of three main components: the Docker container image, genetic databases, and pre-trained model parameters.

```mermaid
graph TB
    subgraph "Host System"
        HostFS["Host Filesystem"]
        Docker["Docker Engine<br/>+ NVIDIA Container Toolkit"]
        RunDockerScript["docker/run_docker.py"]
    end
    
    subgraph "Data Dependencies"
        DBDir["Database Directory<br/>600GB-2.6TB<br/>BFD/UniRef/MGnify/PDB"]
        ParamsDir["Model Parameters<br/>~5GB<br/>params/"]
    end
    
    subgraph "Docker Container"
        EntryScript["run_alphafold.sh"]
        MainScript["run_alphafold.py"]
        AlphaFoldPkg["alphafold/ package"]
        
        subgraph "Dependencies"
            CUDA["CUDA 12.2.2"]
            JAX["JAX 0.4.26"]
            OpenMM["OpenMM 8.2.0"]
            HHsuite["HHsuite 3.3.0"]
            HMMER["HMMER Suite"]
        end
    end
    
    subgraph "Execution Environment"
        GPU["NVIDIA GPU"]
        CPUs["CPU Cores"]
    end
    
    HostFS --> RunDockerScript
    DBDir --> RunDockerScript
    ParamsDir --> RunDockerScript
    
    RunDockerScript -->|"mounts volumes"| Docker
    Docker -->|"launches"| EntryScript
    
    EntryScript -->|"ldconfig"| GPU
    EntryScript -->|"executes"| MainScript
    
    MainScript --> AlphaFoldPkg
    AlphaFoldPkg --> CUDA
    AlphaFoldPkg --> JAX
    AlphaFoldPkg --> OpenMM
    AlphaFoldPkg --> HHsuite
    AlphaFoldPkg --> HMMER
    
    GPU -.->|"used by"| JAX
    GPU -.->|"used by"| OpenMM
    CPUs -.->|"used by"| HHsuite
    CPUs -.->|"used by"| HMMER
```

**Docker Image Construction**

The Docker image is built from `docker/Dockerfile` [docker/Dockerfile:1-92]() which:
1. Uses `nvidia/cuda:12.2.2-cudnn8-runtime-ubuntu20.04` as base image [docker/Dockerfile:15-16]().
2. Installs system dependencies: `build-essential`, `cmake`, `git`, `hmmer`, `kalign` [docker/Dockerfile:25-37]().
3. Compiles `HHsuite 3.3.0` from source [docker/Dockerfile:39-47]().
4. Installs `Miniconda` and `Python 3.11` [docker/Dockerfile:49-59]().
5. Installs Python packages including `JAX 0.4.26` with CUDA support [docker/Dockerfile:68-74]() and `OpenMM 8.2.0` [requirements.txt:9-9]().
6. Copies the AlphaFold codebase and creates the entry point script `run_alphafold.sh` [docker/Dockerfile:63-91]().

Sources: [docker/Dockerfile:1-92](), [requirements.txt:1-14]()

## Execution Flow

The execution flow involves three script layers that orchestrate container launching, GPU configuration, and the prediction pipeline.

```mermaid
sequenceDiagram
    participant User
    participant run_docker.py
    participant Docker
    participant run_alphafold.sh
    participant run_alphafold.py
    participant DataPipeline
    participant RunModel
    participant AmberRelaxation
    
    User->>run_docker.py: python3 docker/run_docker.py --fasta_paths=... --data_dir=...
    
    run_docker.py->>run_docker.py: Parse flags.FLAGS
    run_docker.py->>run_docker.py: _create_mount() for volumes
    run_docker.py->>Docker: docker.from_env().containers.run(...)
    
    Docker->>run_alphafold.sh: ENTRYPOINT execution
    run_alphafold.sh->>run_alphafold.sh: ldconfig (configure GPU libraries)
    run_alphafold.sh->>run_alphafold.py: python run_alphafold.py "$@"
    
    run_alphafold.py->>run_alphafold.py: main() - Parse flags
    run_alphafold.py->>run_alphafold.py: Initialize DataPipeline
    run_alphafold.py->>run_alphafold.py: Initialize RunModel instances
    
    loop For each FASTA in fasta_paths
        run_alphafold.py->>run_alphafold.py: predict_structure()
        run_alphafold.py->>DataPipeline: process(fasta_path)
        DataPipeline-->>run_alphafold.py: feature_dict
        
        loop For each model in model_runners
            run_alphafold.py->>RunModel: process_features()
            run_alphafold.py->>RunModel: predict()
            RunModel-->>run_alphafold.py: prediction_result
        end
        
        run_alphafold.py->>run_alphafold.py: Rank models by ranking_confidence
        run_alphafold.py->>AmberRelaxation: process(unrelaxed_protein)
        AmberRelaxation-->>run_alphafold.py: relaxed_pdb_str
        
        run_alphafold.py->>run_alphafold.py: Save outputs (PDB, mmCIF, JSON)
    end
    
    run_alphafold.py-->>User: Exit
```

Sources: [docker/run_docker.py:159-250](), [docker/Dockerfile:87-91](), [run_alphafold.py:345-556](), [run_alphafold_test.py:35-92]()

## Entry Points and Scripts

### docker/run_docker.py

Container orchestration script that launches the Docker container with appropriate volume mounts and GPU configuration.
- Uses `absl.flags` to define execution parameters like `fasta_paths`, `data_dir`, and `model_preset` [docker/run_docker.py:29-126]().
- Implements `_create_mount()` to map host paths to container paths under `/mnt/` [docker/run_docker.py:133-156]().
- Uses the `docker` Python library to manage container lifecycle [docker/run_docker.py:25-26]().

### run_alphafold.sh

Shell script created during Docker image build [docker/Dockerfile:87-91]() that serves as the container's `ENTRYPOINT`. It performs two critical operations:
1. **GPU Library Configuration**: Executes `ldconfig` to ensure GPU libraries are visible to applications [docker/Dockerfile:88-88]().
2. **Main Script Invocation**: Forwards all command-line arguments to `run_alphafold.py` [docker/Dockerfile:89-89]().

### run_alphafold.py

The main Python entry point containing the complete prediction pipeline [run_alphafold.py:15-25](). Key functions:

**`main()` Function**
- Initializes data pipelines and model runners based on `FLAGS.model_preset` [run_alphafold.py:168-175]().
- Validates database paths against the chosen `db_preset` [run_alphafold.py:160-167]().

**`predict_structure()` Function** [run_alphafold.py:345-556]()
- Orchestrates the transition from raw FASTA to final 3D structure.
- Calls `data_pipeline.process` to generate features [run_alphafold.py:375-377]().
- Calls `model_runner.predict` to perform inference [run_alphafold.py:438-440]().
- Handles structure relaxation using the `amber_relaxer` [run_alphafold.py:494-515]().

Sources: [run_alphafold.py:1-733](), [docker/Dockerfile:87-91]()

## Configuration and Presets

AlphaFold uses a configuration system with model and database presets defined via `absl` flags.

### Model Presets

The `--model_preset` flag [run_alphafold.py:168-175]() determines the architecture:
- `monomer`: Original model for single chains.
- `monomer_casp14`: Monomer model with CASP14 configuration (extra ensembling).
- `monomer_ptm`: Monomer model with pTM head for confidence scoring.
- `multimer`: Model for protein complexes.

### Database Presets

The `--db_preset` flag [run_alphafold.py:160-167]() controls the MSA search depth:
- `full_dbs`: Uses the complete set of genetic databases (BFD, UniRef90, etc.).
- `reduced_dbs`: Uses a smaller version of BFD for faster execution [run_alphafold.py:115-118]().

Sources: [run_alphafold.py:160-175](), [docker/run_docker.py:80-93]()

## Execution Modes

The system branches logic based on whether it is predicting a single chain or a multimer.

**Monomer Mode**
- Uses `pipeline.DataPipeline` [run_alphafold.py:33]().
- Typically uses `hhsearch.HHSearch` for template finding [run_alphafold.py:36]().

**Multimer Mode**
- Uses `pipeline_multimer.DataPipeline` [run_alphafold.py:34]().
- Uses `hmmsearch.Hmmsearch` for template finding [run_alphafold.py:37]().
- Allows multiple predictions per model via `--num_multimer_predictions_per_model` [run_alphafold.py:193-201]().

Sources: [run_alphafold.py:33-40](), [run_alphafold.py:193-201]()

## Output Directory Structure

For every input FASTA, AlphaFold creates a subdirectory in `output_dir` [run_alphafold.py:68-70]() containing:
- `features.pkl`: Pickled input features [run_alphafold_test.py:101-101]().
- `unrelaxed_model_*.pdb`: Predicted structures before relaxation [run_alphafold_test.py:110-110]().
- `relaxed_model_*.pdb`: Structures after Amber relaxation [run_alphafold_test.py:114-114]().
- `ranked_*.pdb`: Final structures ranked by confidence [run_alphafold_test.py:105-105]().
- `ranking_debug.json`: Confidence scores used for ranking [run_alphafold_test.py:106-106]().

Sources: [run_alphafold_test.py:98-128](), [run_alphafold.py:61-70]()

---

